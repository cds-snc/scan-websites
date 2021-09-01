from os import environ
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from database.db import db_session
from logger import log

from models.Organisation import Organisation
from schemas.Organization import OrganizationCreate

# from crawler.crawler import crawl
# import uuid
from pydantic import BaseModel

app = FastAPI()


# Dependency
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/v1/version")
def version():
    return {"version": environ.get("GIT_SHA", "unknown")}


def get_db_version(session):

    query = "SELECT version_num FROM alembic_version"
    full_name = session.execute(query).fetchone()[0]
    return full_name


@app.get("/api/v1/healthcheck")
def healthcheck(session: Session = Depends(get_db)):
    try:
        full_name = get_db_version(session)
        db_status = {"able_to_connect": True, "db_version": full_name}
    except SQLAlchemyError as err:
        log.error(err)
        db_status = {"able_to_connect": False}

    return {"database": db_status}


# TODO Require auth and redirect to home
# TODO Push errors to cloudwatch metric and response when debug enabled
@app.post("/api/v1/organisation", response_class=RedirectResponse)
def create_organisation(
    organisation: OrganizationCreate, session: Session = Depends(get_db)
):

    try:
        new_organisation = Organisation(name=organisation.name)
        session.add(new_organisation)
        session.commit()
        return RedirectResponse("/dashboard")
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


class CrawlUrl(BaseModel):
    url: str


# @app.post("/crawl")
# def crawl_endpoint(crawl_url: CrawlUrl):
#   log.info(f"Crawling {crawl_url}")
#    crawl(uuid.uuid4(), crawl_url.url)
