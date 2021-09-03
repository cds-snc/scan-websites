from fastapi import APIRouter, BackgroundTasks
from logger import log
from pydantic import BaseModel
from crawler.crawler import crawl
import uuid

router = APIRouter()


class CrawlUrl(BaseModel):
    url: str


@router.post("/crawl")
def crawl_endpoint(crawl_url: CrawlUrl, background_tasks: BackgroundTasks):
    log.info(f"Crawling {crawl_url}")
    background_tasks.add_task(str(uuid.uuid4()), crawl_url.url)
    return {"message": "Crawler background task initiated"}

