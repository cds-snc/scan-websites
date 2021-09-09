from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from babel.plural import PluralRule
from database.db import db_session
from logger import log
from sqlalchemy.orm import Session

from models.Organisation import Organisation
from api_gateway.routers.auth import is_authenticated

import glob
import json
import os

router = APIRouter()


# Dependency
def get_db():
    db = db_session()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="front_end/templates")
default_fallback = "en"
languages = {}


def generate_languages(locale_files):
    language_list = glob.glob(locale_files)
    for lang in language_list:
        filename = lang.split(os.path.sep)
        lang_code = filename[1].split(".")[0]

        with open(lang, "r", encoding="utf8") as file:
            languages[lang_code] = json.load(file)


generate_languages("i18n/*.json")


# custom filters for Jinja2
def plural_formatting(key_value, input, locale):
    plural_rule = PluralRule({"one": "n in 0..1"})
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


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def force_lang():
    return RedirectResponse("/en")


@router.get("/{locale}", response_class=HTMLResponse)
async def home(request: Request, locale: str):
    try:
        if locale not in languages:
            locale = default_fallback

        result = {"request": request}
        result.update(languages[locale])
        return templates.TemplateResponse("index.html", result)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


# TODO Push errors to cloudwatch metric and response when debug enabled
# TODO Enable detailed error messages via debug flag
@router.get(
    "/{locale}/dashboard",
    dependencies=[Depends(is_authenticated)],
    response_class=HTMLResponse,
)
async def dashboard(request: Request, locale: str, session: Session = Depends(get_db)):
    try:
        if locale not in languages:
            locale = default_fallback

        organisation_list = session.query(Organisation).all()
        result = {"request": request}
        result.update(languages[locale])
        result.update({"organisations": organisation_list})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("dashboard.html", result)


@router.get("/{locale}/login", response_class=HTMLResponse)
async def login(request: Request, locale: str):
    try:
        if locale not in languages:
            locale = default_fallback

        result = {"request": request}
        result.update(languages[locale])
        return templates.TemplateResponse("login.html", result)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
