from os import environ
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from database.db import db_session
from logger import log

# from crawler.crawler import crawl
# import uuid
from pydantic import BaseModel

app = FastAPI()


@app.get("/api/v1/version")
async def version():
    return {"version": environ.get("GIT_SHA", "unknown")}


def get_db_version(sessionmaker):
    session = sessionmaker()

    query = "SELECT version_num FROM alembic_version"
    full_name = session.execute(query).fetchone()[0]
    return full_name


@app.get("/api/v1/healthcheck")
async def healthcheck():
    try:
        full_name = get_db_version(db_session)
        db_status = {"able_to_connect": True, "db_version": full_name}
    except SQLAlchemyError as err:
        log.error(err)
        db_status = {"able_to_connect": False}

    return {"database": db_status}


class CrawlUrl(BaseModel):
    url: str


# @app.post("/crawl")
# async def crawl_endpoint(crawl_url: CrawlUrl):
#   log.info(f"Crawling {crawl_url}")
#    crawl(uuid.uuid4(), crawl_url.url)
