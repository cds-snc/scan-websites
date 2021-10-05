from fastapi import (
    APIRouter,
    Depends,
    BackgroundTasks,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from logger import log
from pydantic import BaseModel
from crawler.crawler import crawl
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import json
import os
import uuid
from typing import Optional

from .auth import is_authenticated
from database.db import get_session
from models.Template import Template
from models.TemplateScan import TemplateScan
from models.User import User
from models.Scan import Scan
from models.ScanType import ScanType
from schemas.Template import TemplateCreate, TemplateScanCreateList
from pub_sub import pub_sub


router = APIRouter()


class CrawlUrl(BaseModel):
    url: str


def template_belongs_to_org(
    request: Request, template_id: str, session: Session = Depends(get_session)
):
    if template_id:
        try:
            template = (
                session.query(Template)
                .filter(
                    Template.id == template_id,
                    Template.organisation_id == request.user.organisation_id,
                )
                .first()
            )
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if template is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def verify_scan_tokens(
    x_api_key: str = Header(None),
    x_template_token: str = Header(None),
    session: Session = Depends(get_session),
):
    if x_api_key is None or x_template_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        user = session.query(User).filter(User.access_token == x_api_key).one()
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        template = (
            session.query(Template).filter(Template.token == x_template_token).one()
        )
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if user.organisation_id != template.organisation_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return template


@router.get("/start")
@router.get("/start/revision/{git_sha}")
def start_scan(
    request: Request,
    git_sha: Optional[str] = None,
    session: Session = Depends(get_session),
    template: Template = Depends(verify_scan_tokens),
):

    for template_scan in template.template_scans:
        scan = (
            session.query(Scan)
            .filter(
                Scan.template_id == template.id,
                Scan.scan_type == template_scan.scan_type,
            )
            .one_or_none()
        )

        if scan is None:
            scan = Scan(
                organisation_id=template.organisation_id,
                template_id=template.id,
                scan_type=template_scan.scan_type,
            )
            session.add(scan)
            session.commit()

        item = {}
        item["event"] = template_scan.scan_type.callback["event"]
        item["revision"] = "latest"

        if template_scan.scan_type.callback["event"] == "sns":
            item["scan_id"] = str(scan.id)
            item["type"] = template_scan.scan_type.name
            item["product"] = template.name
            item["template_id"] = str(template.id)

            for entry in template_scan.data:
                if "url" in entry:
                    item["url"] = entry["url"]
                if "revision" in entry:
                    item["revision"] = entry["revision"]
            item["queue"] = os.getenv(
                template_scan.scan_type.callback["topic_env"], "NOT_FOUND"
            )

        if "url" not in item:
            return {"message": "Scan error: URL not configured in template"}

        if "event" not in item:
            return {"message": "Scan error: Scan type callback event not defined"}

        if git_sha:
            item["revision"] = git_sha

        try:
            pub_sub.dispatch(item)
        except Exception as error:
            return {"message": f"Scan error: {error}"}

    return {"message": f"Scan started: {template.name}"}


@router.post("/crawl")
def crawl_endpoint(
    crawl_url: CrawlUrl, background_tasks: BackgroundTasks, request: Request
):
    log.info(f"Crawling {crawl_url}")
    background_tasks.add_task(crawl, str(uuid.uuid4()), crawl_url.url)
    return {"message": "Crawler initiated"}


@router.post("/template", dependencies=[Depends(is_authenticated)])
async def save_template(
    response: Response,
    request: Request,
    template: TemplateCreate = Depends(TemplateCreate.as_form),
    session: Session = Depends(get_session),
):
    try:
        new_template = Template(
            name=template.name, organisation_id=request.user.organisation_id
        )
        session.add(new_template)
        session.commit()
        return {"id": new_template.id}
    except SQLAlchemyError as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error creating template"}


@router.put(
    "/template/{template_id}/scan",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
@router.post(
    "/template/{template_id}/scan",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def save_template_scan(
    request: Request,
    response: Response,
    template_id: str,
    config: TemplateScanCreateList,
    session: Session = Depends(get_session),
):
    try:
        template_scan = (
            session.query(TemplateScan)
            .filter(TemplateScan.template_id == template_id)
            .one_or_none()
        )

        scan_type = (
            session.query(ScanType)
            .filter(ScanType.name == config.scan_types[0].scanType)
            .one()
        )

        config_dict = json.loads(config.json())
        if template_scan is None:
            new_template_scan = TemplateScan(
                data=config_dict["data"], template_id=template_id, scan_type=scan_type
            )
            session.add(new_template_scan)
            session.commit()
            return {"id": new_template_scan.id}
        else:
            template_scan.data = config_dict["data"]
            template_scan.scan_type = scan_type
            session.add(template_scan)
            session.commit()
            return {"id": template_scan.id}

    except SQLAlchemyError as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": f"error creating template: {err}"}
