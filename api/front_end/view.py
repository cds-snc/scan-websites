from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from babel.plural import PluralRule
from babel.dates import format_datetime
from database.db import db_session
from logger import log
from sqlalchemy.orm import Session


from models.Organisation import Organisation
from models.Template import Template
from models.User import User
from models.ScanType import ScanType
from schemas.Template import TemplateScanConfigData
from api_gateway.routers.auth import is_authenticated

import glob
import json
import os
import uuid

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


# assign filter to Jinja2
templates.env.filters["plural_formatting"] = plural_formatting
templates.env.filters["date"] = format_date


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def force_lang():
    return RedirectResponse("/en")


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

        scan_configs = []
        return_template_scan = None

        # Currently only allows one template scan per template
        for template_scan in template.template_scans:
            if template_scan.id == template_scan_id:
                return_template_scan = template_scan
                for key, value in template_scan.data.items():
                    scan_configs.append(
                        TemplateScanConfigData(
                            id=str(uuid.uuid4()), key=key, value=value
                        )
                    )

        result = {"request": request}
        result.update(languages[locale])
        result.update({"template": template})
        result.update({"scan_types": scan_types})
        result.update({"scan_config": scan_configs})
        result.update({"template_scan": return_template_scan})
    except Exception as e:
        log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("template_scan.html", result)


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
