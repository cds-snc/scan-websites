from os import environ
from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from database.db import db_session
from logger import log

router = APIRouter()

# Dependency
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


@router.get("/version")
def version():
    return {"version": environ.get("GIT_SHA", "unknown")}


def get_db_version(session):

    query = "SELECT version_num FROM alembic_version"
    full_name = session.execute(query).fetchone()[0]
    return full_name


@router.get("/healthcheck")
def healthcheck(session: Session = Depends(get_db)):
    try:
        full_name = get_db_version(session)
        db_status = {"able_to_connect": True, "db_version": full_name}
    except SQLAlchemyError as err:
        log.error(err)
        db_status = {"able_to_connect": False}

    return {"database": db_status}
