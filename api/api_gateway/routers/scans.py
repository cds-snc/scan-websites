from fastapi import APIRouter, Depends, BackgroundTasks, Request, Response, status
from fastapi.responses import RedirectResponse
from logger import log
from pydantic import BaseModel
from crawler.crawler import crawl
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

import uuid

from .auth import is_authenticated
from database.db import get_session
from models.Template import Template
from schemas.Template import TemplateCreate

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
        print(template)
        new_template = Template(
            name=template.name, organisation_id=request.user.organisation_id
        )
        session.add(new_template)
        session.commit()
        return RedirectResponse(
            f"/en/template/{new_template.id}/scan",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except SQLAlchemyError as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": f"error creating template: {err}"}


@router.post("/template/{template_id}/scan", dependencies=[Depends(is_authenticated)])
async def save_template_scan(
    response: Response,
    request: Request,
    template: TemplateCreate = Depends(TemplateCreate.as_form),
    session: Session = Depends(get_session),
):
    try:
        print(template)
        new_template = Template(
            name=template.name, organisation_id=request.user.organisation_id
        )
        session.add(new_template)
        session.commit()
        return RedirectResponse("/en/dashboard")
    except SQLAlchemyError as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": f"error creating template: {err}"}
