from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from babel.plural import PluralRule
from database.db import db_session
from logger import log

from models.Organisation import Organisation
from schemas.Organization import OrganizationCreate

import glob
import json
import os

app = FastAPI()

templates = Jinja2Templates(directory="front_end/templates")

default_fallback = "en"
languages = {}
plural_rule = PluralRule({"one": "n in 0..1"})

language_list = glob.glob("i18n/*.json")
for lang in language_list:
    filename = lang.split(os.path.sep)
    lang_code = filename[1].split(".")[0]

    with open(lang, "r", encoding="utf8") as file:
        languages[lang_code] = json.load(file)

# custom filters for Jinja2
def plural_formatting(key_value, input, locale):
    key = ""
    for i in languages[locale]:
        if key_value == languages[locale][i]:
            key = i
            break

    if not key:
        return key_value

    plural_key = f"{key}_plural"

    if plural_rule(input) != "one" and plural_key in languages[locale]:
        key = plural_key

    return languages[locale][key]


# assign filter to Jinja2
templates.env.filters["plural_formatting"] = plural_formatting


@app.get("/", response_class=HTMLResponse)
async def force_lang():
    return RedirectResponse("/en")


@app.get("/{locale}", response_class=HTMLResponse)
async def home(request: Request, locale: str):
    try:
        if locale not in languages:
            locale = default_fallback

        result = {"request": request}
        result.update(languages[locale])
        return templates.TemplateResponse("index.html", result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TODO Require auth and redirect to home
# TODO Push errors to cloudwatch metric and response when debug enabled
@app.post("/organization", response_class=RedirectResponse)
async def create_organization(organization: OrganizationCreate):
    session = db_session()
    try:
        new_organization = Organisation(name=organization.name)
        session.add(new_organization)
        session.commit()
        return RedirectResponse("/dashboard")
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
