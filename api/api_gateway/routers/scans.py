from fastapi import APIRouter, BackgroundTasks, Depends, Request
from logger import log
from pydantic import BaseModel, Json
from crawler.crawler import crawl
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
import uuid

from .auth import verify_private_api_token
from database.db import get_session

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
