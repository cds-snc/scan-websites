from copy import copy
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from database.db import db_session
from logger import log
from sqlalchemy.orm import Session

from .view import languages, default_fallback, templates
from api_gateway.routers.auth import is_authenticated
from api_gateway.routers.scans import template_belongs_to_org
from models.A11yReport import A11yReport
from models.Scan import Scan
from models.ScanIgnore import ScanIgnore
from models.SecurityReport import SecurityReport
from models.SecurityViolation import SecurityViolation
from pub_sub import pub_sub
from storage import storage

import base64
import os
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
    "/{locale}/results/{template_id}/a11y/{scan_id}/{report_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
    response_class=HTMLResponse,
)
async def get_a11y_report(
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
            session.query(A11yReport)
            .outerjoin(Scan.a11y_reports)
            .filter(
                A11yReport.id == report_id,
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
    if report.scan.scan_type.name == pub_sub.AvailableScans.AXE_CORE.value:
        return templates.TemplateResponse("scan_results_a11y_summary.html", result)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Scan type {report.scan.scan_type.name} has no associated layout",
        )


@router.get(
    "/{locale}/results/{template_id}/a11y/{scan_id}/{report_id}/screenshot",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
)
async def get_a11y_report_screenshot(
    request: Request,
    locale: str,
    template_id: uuid.UUID,
    scan_id: uuid.UUID,
    report_id: uuid.UUID,
    session: Session = Depends(get_db),
    response_class=HTMLResponse,
):
    try:
        if locale not in languages:
            locale = default_fallback

        report = (
            session.query(A11yReport)
            .outerjoin(Scan.a11y_reports)
            .filter(
                A11yReport.id == report_id,
                Scan.id == scan_id,
                Scan.template_id == template_id,
            )
            .one()
        )

        record = {
            "s3": {
                "bucket": {"name": os.environ.get("AXE_CORE_SCREENSHOT_BUCKET", False)},
                "object": {"key": f"{str(report_id)}.png"},
            }
        }

        data = base64.b64encode(storage.get_object(record)).decode("utf-8")
        result = {"request": request}
        result.update(languages[locale])
        result.update({"report": report, "data": data})

    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    if report.scan.scan_type.name == pub_sub.AvailableScans.AXE_CORE.value:
        return templates.TemplateResponse("scan_results_screenshot.html", result)
    else:
        raise HTTPException(
            status_code=500,
            detail="Could not download image from bucket",
        )


@router.get(
    "/{locale}/results/{template_id}/security/{scan_id}/{report_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
    response_class=HTMLResponse,
)
async def get_security_report(
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
        return templates.TemplateResponse("scan_results_security_summary.html", result)
    elif report.scan.scan_type.name == pub_sub.AvailableScans.NUCLEI.value:
        return templates.TemplateResponse("scan_results_nuclei_summary.html", result)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Scan type {report.scan.scan_type.name} has no associated layout",
        )


@router.get(
    "/{locale}/results/{template_id}/security/{scan_id}/{report_id}/{violation_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
    response_class=HTMLResponse,
)
async def get_security_violation(
    request: Request,
    locale: str,
    template_id: uuid.UUID,
    scan_id: uuid.UUID,
    report_id: uuid.UUID,
    violation_id: uuid.UUID,
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

        violation = (
            session.query(SecurityViolation)
            .filter(
                SecurityViolation.id == violation_id,
                SecurityViolation.security_report_id == report_id,
            )
            .one()
        )

        scan_ignores = (
            session.query(ScanIgnore)
            .filter(ScanIgnore.violation == violation.violation)
            .all()
        )

        if scan_ignores:
            included_data = copy(violation.data)
            excluded_data = copy(violation.data)

            try:
                included_data[:] = (
                    itm
                    for itm in included_data
                    if storage.filter_ignored_results(
                        False, itm, violation.violation, scan_ignores
                    )
                )

                excluded_data[:] = (
                    itm
                    for itm in excluded_data
                    if storage.filter_ignored_results(
                        True, itm, violation.violation, scan_ignores
                    )
                )
            except ValueError as err:
                log.error(f"Error filtering results: {err}")
                included_data = violation.data
                excluded_data = []

        else:
            included_data = violation.data
            excluded_data = []

        result = {"request": request}
        result.update(languages[locale])
        result.update({"report": report})
        result.update({"security_violation": violation})
        result.update({"included_data": included_data})
        result.update({"excluded_data": excluded_data})
        result.update({"scan_ignores": scan_ignores})

    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    if report.scan.scan_type.name == pub_sub.AvailableScans.OWASP_ZAP.value:
        return templates.TemplateResponse(
            "scan_results_security_details_zap.html", result
        )
    elif report.scan.scan_type.name == pub_sub.AvailableScans.NUCLEI.value:
        return templates.TemplateResponse(
            "scan_results_security_details_nuclei.html", result
        )
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
        return templates.TemplateResponse("scan_results_owasp_zap.html", result)
    elif scan.scan_type.name == pub_sub.AvailableScans.NUCLEI.value:
        return templates.TemplateResponse("scan_results_nuclei.html", result)
    elif scan.scan_type.name == pub_sub.AvailableScans.AXE_CORE.value:
        return templates.TemplateResponse("scan_results_a11y.html", result)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Scan type {scan.scan_type.name} has no associated layout",
        )


@router.get(
    "/{locale}/ignored/{template_id}/scan/{scan_id}",
    dependencies=[Depends(is_authenticated), Depends(template_belongs_to_org)],
    response_class=HTMLResponse,
)
async def get_scan_ignores(
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

        scan_ignores = (
            session.query(ScanIgnore).filter(ScanIgnore.scan_id == str(scan.id)).all()
        )

        result = {"request": request}
        result.update(languages[locale])
        result.update({"scan": scan})
        result.update({"scan_ignores": scan_ignores})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))

    return templates.TemplateResponse("scan_ignore_list.html", result)
