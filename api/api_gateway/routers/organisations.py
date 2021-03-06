from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from database.db import get_session
from logger import log

from models.Organisation import Organisation
from schemas.Organization import OrganizationCreate

router = APIRouter()


# TODO Require auth and redirect to home
# TODO Push errors to cloudwatch metric and response when debug enabled
@router.post("/create", response_class=RedirectResponse)
def create_organisation(
    organisation: OrganizationCreate,
    response: Response,
    session: Session = Depends(get_session),
):

    try:
        new_organisation = Organisation(name=organisation.name)
        session.add(new_organisation)
        session.commit()
        return RedirectResponse("/dashboard")
    except SQLAlchemyError as err:
        log.error(err)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": f"error creating organisation: {err}"}
