from fastapi import APIRouter
from logger import log
from pydantic import BaseModel
from crawler.crawler import crawl
import uuid

router = APIRouter()


class CrawlUrl(BaseModel):
    url: str


@router.post("/crawl")
def crawl_endpoint(crawl_url: CrawlUrl):
    log.info(f"Crawling {crawl_url}")
    crawl(uuid.uuid4(), crawl_url.url)
