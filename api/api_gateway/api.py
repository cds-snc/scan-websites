from os import environ
from fastapi import FastAPI
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from database.db import db_session
from logger import log

app = FastAPI()


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
