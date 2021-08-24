from os import environ
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import SQLAlchemyError
from database.db import db_session
from logger import log

# from crawler.crawler import crawl
# import uuid
from pydantic import BaseModel


from models.Organisation import Organisation
from schemas.Organization import OrganizationBase

app = FastAPI()

templates = Jinja2Templates(directory="api_gateway/templates")


@app.get("/version")
async def version():
    return {"version": environ.get("GIT_SHA", "unknown")}


def get_db_version(sessionmaker):
    session = sessionmaker()

    query = "SELECT version_num FROM alembic_version"
    full_name = session.execute(query).fetchone()[0]
    return full_name


@app.get("/healthcheck")
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
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {"page": "Home page"}
    return templates.TemplateResponse("page.html", {"request": request, "data": data})


@app.post("/organization", response_class=HTMLResponse)
async def create_organization(organization: OrganizationBase):
    session = db_session()
    try:
        new_organization = Organisation(name=organization.name)
        session.add(new_organization)
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    session = db_session()
    try:
        result = session.query(Organisation).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "organisations": result}
    )
