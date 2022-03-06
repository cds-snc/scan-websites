from fastapi import APIRouter, Depends, Header, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from babel.plural import PluralRule
from babel.dates import format_datetime
from database.db import db_session
from logger import log
from sqlalchemy.orm import Session
from typing import Optional

from models.Organisation import Organisation
from models.Template import Template
from models.User import User
from models.ScanType import ScanType
from schemas.Template import TemplateScanConfigData
from api_gateway.routers.auth import is_authenticated
from .utils import is_safe_redirect_url

import glob
import json
import os
import uuid
import scan_websites_constants

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


def generate_languages(locale_files):
    languages = {}
    language_list = glob.glob(locale_files)
    for lang in language_list:
        filename = lang.split(os.path.sep)
        lang_code = filename[1].split(".")[0]

        with open(lang, "r", encoding="utf8") as file:
            languages[lang_code] = json.load(file)
    return languages


languages = generate_languages("i18n/*.json")


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


def format_date(value, format="medium"):
    if format == "full":
        format = "EEEE, d. MMMM y 'at' HH:mm"
    elif format == "medium":
        format = "EE dd.MM.y HH:mm"
    return format_datetime(value, format)


def get_risk_colour(riskcode):
    if riskcode == "0" or riskcode == "info":  # Informational
        return "bg-blue-500"
    elif riskcode == "1" or riskcode == "low":  # Low
        print("return green")
        return "bg-green-500"
    elif riskcode == "2" or riskcode == "medium":  # Medium
        return "bg-yellow-300"
    elif riskcode == "3":  # High
        return "bg-red-500"
    elif riskcode == "high":  # High
        return "bg-yellow-600"
    elif riskcode == "3" or riskcode == "critical":  # High
        return "bg-red-500"
    else:  # default
        return "bg-gray-500"


def extract_risk_text(summary):
    reduced_summary = {}
    for key in summary:
        if " (" in key:
            risk = str(key.split(" (")[0]).lower()
            reduced_summary[risk] = summary[key]
        else:
            reduced_summary[key] = summary[key]
    return reduced_summary


def prettier_array(data):
    if scan_websites_constants.UNIQUE_SEPARATOR in data:
        return data.replace(scan_websites_constants.UNIQUE_SEPARATOR, ", ")
    else:
        return data


def get_seperator():
    return scan_websites_constants.UNIQUE_SEPARATOR


# assign filter to Jinja2
templates.env.filters["plural_formatting"] = plural_formatting
templates.env.filters["date"] = format_date
templates.env.filters["risk_colour"] = get_risk_colour
templates.env.filters["prettier_array"] = prettier_array
templates.env.filters["extract_risk_text"] = extract_risk_text
templates.env.globals["get_seperator"] = get_seperator


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def force_lang():
    return RedirectResponse("/en")


@router.get("/lang/{locale}", response_class=HTMLResponse)
async def change_lang(
    request: Request, locale: str, referer: Optional[str] = Header(None)
):
    try:
        if locale not in languages:
            locale = default_fallback

        paths = referer.split("/")
        if referer and len(paths) >= 3 and is_safe_redirect_url(referer):
            paths[3] = locale
            redirect_url = "/".join(paths[3:])
            return RedirectResponse(f"/{redirect_url}")
        else:
            return RedirectResponse("/en")

    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{locale}", response_class=HTMLResponse)
async def home(request: Request, locale: str, session: Session = Depends(get_db)):
    try:
        if locale not in languages:
            locale = default_fallback

        template_list = session.query(Template).all()

        result = {"request": request}
        result.update(languages[locale])
        result.update({"template_list": template_list})
        return templates.TemplateResponse("index.html", result)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{locale}/user",
    dependencies=[Depends(is_authenticated)],
    response_class=HTMLResponse,
)
async def user(request: Request, locale: str, session: Session = Depends(get_db)):
    try:
        if locale not in languages:
            locale = default_fallback

        user = (
            session.query(User)
            .filter(User.email_address == request.user.email_address)
            .scalar()
        )

        result = {"request": request}
        result.update(languages[locale])
        result.update({"token": user.access_token})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("user.html", result)


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


@router.get(
    "/{locale}/template",
    dependencies=[Depends(is_authenticated)],
    response_class=HTMLResponse,
)
async def template(request: Request, locale: str, session: Session = Depends(get_db)):
    try:
        if locale not in languages:
            locale = default_fallback

        template_list = (
            session.query(Template)
            .filter(
                Template.organisation_id == request.user.organisation_id,
            )
            .all()
        )

        result = {"request": request}
        result.update(languages[locale])
        result.update({"templates": template_list})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("template.html", result)


@router.get(
    "/{locale}/template/{template_id}/scan",
    dependencies=[Depends(is_authenticated)],
    response_class=HTMLResponse,
)
async def template_scan_list(
    request: Request,
    locale: str,
    template_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    try:
        if locale not in languages:
            locale = default_fallback

        template = (
            session.query(Template)
            .filter(
                Template.id == template_id,
                Template.organisation_id == request.user.organisation_id,
            )
            .one()
        )

        scan_types = session.query(ScanType).all()
        result = {"request": request}
        result.update(languages[locale])
        result.update({"template": template})
        result.update({"scan_types": scan_types})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("template_scan_list.html", result)


@router.get(
    "/{locale}/template/{template_id}/scan/new",
    dependencies=[Depends(is_authenticated)],
    response_class=HTMLResponse,
)
async def create_template_scan(
    request: Request,
    locale: str,
    template_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    try:
        if locale not in languages:
            locale = default_fallback

        template = (
            session.query(Template)
            .filter(
                Template.id == template_id,
                Template.organisation_id == request.user.organisation_id,
            )
            .one()
        )

        scan_types = session.query(ScanType).all()

        result = {"request": request}
        result.update(languages[locale])
        result.update({"template": template})
        result.update({"scan_types": scan_types})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("template_scan.html", result)


@router.get(
    "/{locale}/template/{template_id}/scan/{template_scan_id}",
    dependencies=[Depends(is_authenticated)],
    response_class=HTMLResponse,
)
async def template_scan(
    request: Request,
    locale: str,
    template_id: uuid.UUID,
    template_scan_id: uuid.UUID,
    session: Session = Depends(get_db),
):
    try:
        if locale not in languages:
            locale = default_fallback

        # Query on template to ensure users only access their org's templates
        template = (
            session.query(Template)
            .filter(
                Template.id == template_id,
                Template.template_scans.any(id=template_scan_id),
                Template.organisation_id == request.user.organisation_id,
            )
            .one()
        )
        scan_types = session.query(ScanType).all()

        return_template_scan = None
        scan_configs = {}
        selected_scans = []

        # Currently only allows one template scan per template
        for template_scan in template.template_scans:
            if template_scan.id == template_scan_id:
                selected_scans.append(template_scan.scan_type.name)
                return_template_scan = template_scan
                for key, value in template_scan.data.items():
                    if value is not None:
                        scan_configs[key] = value

        result = {"request": request}
        result.update(languages[locale])
        result.update({"template": template})
        result.update({"scan_types": scan_types})
        result.update({"template_scan": return_template_scan})
        result.update({"selected_scans": selected_scans})
        result.update({"scan_configs": scan_configs})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("template_scan.html", result)


@router.get("/{locale}/login", response_class=HTMLResponse)
async def login(request: Request, locale: str):
    try:
        if locale not in languages:
            locale = default_fallback

        result = {
            "request": request,
            "heroku": os.environ.get("HEROKU_PR_NUMBER", False),
        }
        result.update(languages[locale])
        return templates.TemplateResponse("login.html", result)
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
