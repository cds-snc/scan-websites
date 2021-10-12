from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from database.db import db_session
from logger import log
from sqlalchemy.orm import Session

from .view import languages, default_fallback, templates
from api_gateway.routers.auth import is_authenticated
from api_gateway.routers.scans import template_belongs_to_org
from models.Scan import Scan
from models.SecurityReport import SecurityReport
from pub_sub import pub_sub


import uuid

router = APIRouter()


# Dependency
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/{locale}/results/{template_id}/security/{scan_id}/{report_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
    response_class=HTMLResponse,
)
async def get__security_report(
    request: Request,
    locale: str,
    template_id: uuid.UUID,
    scan_id: uuid.UUID,
    report_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    try:
        if locale not in languages:
            locale = default_fallback

        report = (
            session.query(SecurityReport)
            .outerjoin(Scan.security_reports)
            .filter(
                SecurityReport.id == report_id,
                Scan.id == scan_id,
                Scan.template_id == template_id,
            )
            .one()
        )

        result = {"request": request}
        result.update(languages[locale])
        result.update({"report": report})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    if report.scan.scan_type.name == pub_sub.AvailableScans.OWASP_ZAP.value:
        return templates.TemplateResponse("scan_results_security_details.html", result)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Scan type {report.scan.scan_type.name} has no associated layout",
        )


@router.get(
    "/{locale}/results/{template_id}/scan/{scan_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
    response_class=HTMLResponse,
)
async def get_scan(
    request: Request,
    locale: str,
    template_id: uuid.UUID,
    scan_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    try:
        if locale not in languages:
            locale = default_fallback

        scan = (
            session.query(Scan)
            .filter(Scan.id == scan_id, Scan.template_id == template_id)
            .one()
        )

        result = {"request": request}
        result.update(languages[locale])
        result.update({"scan": scan})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    if scan.scan_type.name == pub_sub.AvailableScans.OWASP_ZAP.value:
        return templates.TemplateResponse("scan_results_security.html", result)
    elif scan.scan_type.name == pub_sub.AvailableScans.AXE_CORE.value:
        return templates.TemplateResponse("scan_results_a11y.html", result)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Scan type {scan.scan_type.name} has no associated layout",
        )
