from fastapi import APIRouter, BackgroundTasks, Request
from logger import log
from pydantic import BaseModel
from crawler.crawler import crawl
from slowapi import Limiter
from slowapi.util import get_remote_address
import uuid

limiter = Limiter(key_func=get_remote_address, enabled=True)
router = APIRouter()

class CrawlUrl(BaseModel):
    url: str


@router.post("/crawl")
@limiter.limit("5/minute")
def crawl_endpoint(crawl_url: CrawlUrl, background_tasks: BackgroundTasks, request: Request):
    log.info(f"Crawling {crawl_url}")
    background_tasks.add_task(crawl, str(uuid.uuid4()), crawl_url.url)
    return {"message": "Crawler initiated"}
