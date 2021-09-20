from fastapi import (
    APIRouter,
    Depends,
    BackgroundTasks,
    Request,
    Response,
    status,
)
from logger import log
from pydantic import BaseModel
from crawler.crawler import crawl
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import uuid
import json

from .auth import is_authenticated
from database.db import get_session
from models.Template import Template
from models.TemplateScan import TemplateScan
from models.ScanType import ScanType
from schemas.Template import TemplateCreate, TemplateScanCreateList

limiter = Limiter(key_func=get_remote_address, enabled=True)
router = APIRouter()


class CrawlUrl(BaseModel):
    url: str


@router.post("/crawl")
@limiter.limit("5/minute")
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


@router.post(
    "/template/{template_id}/scan",
    dependencies=[Depends(is_authenticated)],
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
