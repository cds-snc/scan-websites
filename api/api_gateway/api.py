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


def healthcheck_session(sessionmaker):
    session = sessionmaker()
    return session.query(text("1")).from_statement(text("SELECT 1")).all()


@app.get("/healthcheck")
async def healthcheck():
    try:
        healthcheck_session(db_session)
        db_status = {"able_to_connect": True}
    except SQLAlchemyError as err:
        log.error(err)
        db_status = {"able_to_connect": False}

    return {"database": db_status}
