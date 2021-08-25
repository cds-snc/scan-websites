from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database.db import db_session
from logger import log

from models.Organisation import Organisation
from schemas.Organization import OrganizationCreate

app = FastAPI()

templates = Jinja2Templates(directory="front_end/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = {"page": "Home page"}
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

# TODO Require auth and redirect to home
# TODO Push errors to cloudwatch metric and response when debug enabled
@app.post("/organization", response_class=RedirectResponse)
async def create_organization(organization: OrganizationCreate):
    session = db_session()
    try:
        new_organization = Organisation(name=organization.name)
        session.add(new_organization)
        session.commit()
        return RedirectResponse('/')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# TODO Require auth & limit to users current organization
# TODO Push errors to cloudwatch metric and response when debug enabled
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
