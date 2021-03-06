from fastapi import (
    APIRouter,
    Depends,
    BackgroundTasks,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)


from logger import log
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
from models.ScanIgnore import ScanIgnore
from models.ScanType import ScanType
from models.A11yReport import A11yReport
from models.SecurityReport import SecurityReport
from schemas.Template import TemplateCreate, TemplateScanData
from schemas.ScanIgnore import ScanIgnoreCreate
from pub_sub import pub_sub


router = APIRouter()


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


def build_base_report(scan_type, scan, payload, session):
    if (
        scan_type == pub_sub.AvailableScans.OWASP_ZAP.value
        or scan_type == pub_sub.AvailableScans.NUCLEI.value
    ):
        security_report = SecurityReport(
            product=payload["product"],
            revision=payload["revision"],
            url=payload["url"],
            summary={"status": "scanning"},
            scan=scan,
        )
        session.add(security_report)
        session.commit()
        return str(security_report.id)
    elif scan_type == pub_sub.AvailableScans.AXE_CORE.value:
        a11y_report = A11yReport(
            product=payload["product"],
            revision=payload["revision"],
            url=payload["url"],
            summary={"status": "scanning"},
            scan=scan,
        )
        session.add(a11y_report)
        session.commit()
        return str(a11y_report.id)
    else:
        log.error(f"Unsupported scan type: {scan_type}")
        raise ValueError("Unsupported scan type", scan_type)


def build_scan_payload(template, template_scan, scan, git_sha=None):
    item = {}
    item["event"] = template_scan.scan_type.callback["event"]
    item["revision"] = "latest"

    if template_scan.scan_type.callback["event"] == "sns":
        item["queue"] = os.getenv(
            template_scan.scan_type.callback["topic_env"], "NOT_FOUND"
        )
    elif template_scan.scan_type.callback["event"] == "stepfunctions":
        item["queue"] = template_scan.scan_type.callback["state_machine_name"]

    item["scan_id"] = str(scan.id)
    item["type"] = template_scan.scan_type.name
    item["product"] = template.name
    item["template_id"] = str(template.id)

    if "url" in template_scan.data:
        item["url"] = template_scan.data["url"]
    if "revision" in template_scan.data:
        item["revision"] = template_scan.data["revision"]

    if "crawl" in template_scan.data:
        item["crawl"] = template_scan.data["crawl"]
    else:
        item["crawl"] = False

    if "url" not in item:
        return {"message": "Scan error: URL not configured in template"}

    if "event" not in item:
        return {"message": "Scan error: Scan type callback event not defined"}

    if git_sha:
        item["revision"] = git_sha

    return item


@router.get("/start")
@router.get("/start/revision/{git_sha}")
async def start_scan(
    request: Request,
    background_tasks: BackgroundTasks,
    git_sha: Optional[str] = None,
    dynamic: Optional[bool] = Query(False),
    session: Session = Depends(get_session),
    template: Template = Depends(verify_scan_tokens),
):

    success_list = []
    fail_list = []
    payload_list = []
    skipped_list = []
    for template_scan in template.template_scans:
        if template_scan.scan_type.dynamic != dynamic:
            skipped_list.append(template_scan.scan_type.name)
            continue

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

        item = build_scan_payload(template, template_scan, scan, git_sha)
        base_report_id = build_base_report(
            template_scan.scan_type.name, scan, item, session
        )
        item["id"] = base_report_id

        try:
            if item["crawl"] == "true":
                background_tasks.add_task(crawl, item)
                success_list.append(template_scan.scan_type.name)
            else:
                payload_list.append(item)
        except Exception as error:
            log.error(error)
            fail_list.append(template_scan.scan_type.name)
            pass

    try:
        pub_sub.dispatch(payload_list)
        for payload in payload_list:
            success_list.append(payload["type"])
    except Exception as error:
        log.error(error)
        for payload in payload_list:
            fail_list.append(payload["type"])
        pass

    return {
        "message": f"Scan start details: {template.name}, successful: {success_list}, failed: {fail_list}, skipped: {skipped_list}"
    }


@router.post("/template", dependencies=[Depends(is_authenticated)])
async def save_template(
    response: Response,
    request: Request,
    template: TemplateCreate,
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
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def save_template_scan(
    request: Request,
    response: Response,
    template_id: uuid.UUID,
    config: TemplateScanData,
    session: Session = Depends(get_session),
):
    try:
        scan_type = (
            session.query(ScanType).filter(ScanType.name == config.scanType).one()
        )

        config_dict = json.loads(config.json())
        new_template_scan = TemplateScan(
            data=config_dict, template_id=template_id, scan_type=scan_type
        )
        session.add(new_template_scan)
        session.commit()
        return {"id": new_template_scan.id}
    except SQLAlchemyError as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": f"error creating template: {err}"}


@router.put(
    "/template/{template_id}/scan/{template_scan_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def update_template_scan(
    request: Request,
    response: Response,
    template_id: uuid.UUID,
    template_scan_id: uuid.UUID,
    config: TemplateScanData,
    session: Session = Depends(get_session),
):
    try:
        template_scan = (
            session.query(TemplateScan)
            .filter(
                TemplateScan.id == template_scan_id,
                TemplateScan.template_id == template_id,
            )
            .one()
        )

        scan_type = (
            session.query(ScanType).filter(ScanType.name == config.scanType).one()
        )
        config_dict = json.loads(config.json())
        if template_scan is None:
            new_template_scan = TemplateScan(
                data=config_dict, template_id=template_id, scan_type=scan_type
            )
            session.add(new_template_scan)
            session.commit()
            return {"id": new_template_scan.id}
        else:
            template_scan.data = config_dict
            template_scan.scan_type = scan_type
            session.add(template_scan)
            session.commit()
            return {"id": template_scan.id}

    except SQLAlchemyError as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": f"error creating template: {err}"}


@router.delete(
    "/template/{template_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def delete_template(
    request: Request,
    response: Response,
    template_id,
    session: Session = Depends(get_session),
):
    try:

        template = session.query(Template).filter(Template.id == template_id).first()
        session.delete(template)
        session.commit()
        return {"status": "OK"}

    except Exception as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error deleting template"}


@router.delete(
    "/template/{template_id}/scan/{template_scan_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def delete_template_scan(
    request: Request,
    response: Response,
    template_id,
    template_scan_id,
    session: Session = Depends(get_session),
):
    try:
        template_scan = (
            session.query(TemplateScan)
            .filter(
                TemplateScan.id == template_scan_id,
                TemplateScan.template_id == template_id,
            )
            .one()
        )

        scan = (
            session.query(Scan)
            .filter(
                Scan.scan_type_id == template_scan.scan_type_id,
                Scan.template_id == template_scan.template_id,
            )
            .one_or_none()
        )
        session.delete(template_scan)
        if scan is not None:
            session.delete(scan)
        session.commit()
        return {"status": "OK"}

    except Exception as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error deleting template"}


@router.delete(
    "/template/{template_id}/scan/{scan_id}/security/{report_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def delete_security_report(
    request: Request,
    response: Response,
    template_id,
    scan_id,
    report_id,
    session: Session = Depends(get_session),
):
    try:
        security_report = (
            session.query(SecurityReport)
            .outerjoin(Scan.security_reports)
            .filter(
                SecurityReport.id == report_id,
                Scan.id == scan_id,
                Scan.template_id == template_id,
            )
            .one_or_none()
        )

        if security_report is not None:
            session.delete(security_report)
            session.commit()
            return {"status": "OK"}
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": "error deleting security report"}

    except Exception as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error deleting security report"}


@router.delete(
    "/template/{template_id}/scan/{scan_id}/a11y/{report_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def delete_a11y_report(
    request: Request,
    response: Response,
    template_id,
    scan_id,
    report_id,
    session: Session = Depends(get_session),
):
    try:
        a11y_report = (
            session.query(A11yReport)
            .outerjoin(Scan.a11y_reports)
            .filter(
                A11yReport.id == report_id,
                Scan.id == scan_id,
                Scan.template_id == template_id,
            )
            .one_or_none()
        )

        if a11y_report is not None:
            session.delete(a11y_report)
            session.commit()
            return {"status": "OK"}
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": "error deleting a11y report"}

    except Exception as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error deleting a11y report"}


@router.post(
    "/template/{template_id}/scan/{scan_id}/type/{scan_type}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def save_scan_ignore(
    request: Request,
    response: Response,
    template_id: uuid.UUID,
    scan_id: uuid.UUID,
    scan_type: uuid.UUID,
    scan_ignore: ScanIgnoreCreate,
    session: Session = Depends(get_session),
):
    try:
        scan = (
            session.query(Scan)
            .filter(
                Scan.id == scan_id,
                Scan.template_id == template_id,
                Scan.scan_type_id == scan_type,
            )
            .one_or_none()
        )

        existing_ignore = (
            session.query(ScanIgnore)
            .filter(
                ScanIgnore.violation == scan_ignore.violation,
                ScanIgnore.location == scan_ignore.location,
                ScanIgnore.condition == scan_ignore.condition,
            )
            .one_or_none()
        )

        if existing_ignore is None:
            new_ignore = ScanIgnore(
                scan_id=scan.id,
                violation=scan_ignore.violation,
                location=scan_ignore.location,
                condition=scan_ignore.condition,
            )

            session.add(new_ignore)
            session.commit()
            return {"id": new_ignore.id}

        return {"id": existing_ignore.id}
    except Exception as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error creating scan ignore"}


@router.delete(
    "/template/{template_id}/scan/{scan_id}/type/{scan_type}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def delete_scan_ignore(
    request: Request,
    response: Response,
    template_id: uuid.UUID,
    scan_id: uuid.UUID,
    scan_type: uuid.UUID,
    scan_ignore: ScanIgnoreCreate,
    session: Session = Depends(get_session),
):
    try:
        scan = (
            session.query(Scan)
            .filter(
                Scan.id == scan_id,
                Scan.template_id == template_id,
                Scan.scan_type_id == scan_type,
            )
            .one_or_none()
        )

        existing_ignore = (
            session.query(ScanIgnore)
            .filter(
                ScanIgnore.scan_id == str(scan.id),
                ScanIgnore.violation == scan_ignore.violation,
                ScanIgnore.location == scan_ignore.location,
                ScanIgnore.condition == scan_ignore.condition,
            )
            .one_or_none()
        )

        if existing_ignore:
            session.delete(existing_ignore)
            session.commit()
            return {"status": "OK"}
        else:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": "error deleting ignore"}
    except Exception as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "error deleting scan ignore"}
