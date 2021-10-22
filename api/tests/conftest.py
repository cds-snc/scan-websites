import os
import pytest
from unittest.mock import MagicMock, patch

from alembic.config import Config
from alembic import command

from api_gateway import api
from authlib.oidc.core import UserInfo

from fastapi import FastAPI
from fastapi.testclient import TestClient

from factories import (
    OrganisationFactory,
    ScanFactory,
    ScanTypeFactory,
    SecurityReportFactory,
    SecurityViolationFactory,
    TemplateFactory,
    TemplateScanFactory,
    UserFactory,
)

from models.A11yReport import A11yReport
from models.Organisation import Organisation
from models.Scan import Scan
from models.ScanType import ScanType
from models.SecurityReport import SecurityReport
from models.SecurityViolation import SecurityViolation
from models.Template import Template
from models.TemplateScan import TemplateScan
from models.User import User
from pub_sub import pub_sub

from api_gateway.custom_middleware import add_security_headers
from api_gateway.routers import ops

from starlette.middleware.base import BaseHTTPMiddleware

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def client():
    client = TestClient(api.app)
    yield client


@pytest.fixture(scope="session")
def a11y_report_fixture(session, scan_fixture):
    a11y_report = A11yReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(a11y_report)
    session.commit()
    return a11y_report


@pytest.fixture(scope="session")
def security_report_fixture(session, scan_fixture):
    security_report = SecurityReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=scan_fixture,
    )
    session.add(security_report)
    session.commit()
    return security_report


@pytest.fixture(scope="session")
def security_violation_fixture(session, security_report_fixture):
    security_violation = SecurityViolation(
        violation="violation",
        risk="risk",
        confidence="confidence",
        solution="solution",
        reference="reference",
        data=[{"uri": "https://example.com/", "method": "POST", "evidence": "foo"}],
        tags="tags",
        url="url",
        security_report=security_report_fixture,
    )
    session.add(security_violation)
    session.commit()
    return security_violation


@pytest.fixture(scope="session")
def owasp_security_report_fixture(session, home_org_owasp_scan_fixture):
    security_report = SecurityReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=home_org_owasp_scan_fixture,
    )
    session.add(security_report)
    session.commit()
    return security_report


@pytest.fixture(scope="session")
def owasp_security_violation_fixture(session, owasp_security_report_fixture):
    security_violation = SecurityViolation(
        violation="violation",
        risk="risk",
        confidence="confidence",
        solution="solution",
        reference="reference",
        data=[{"uri": "https://example.com/", "method": "POST", "evidence": "foo"}],
        tags="tags",
        url="url",
        security_report=owasp_security_report_fixture,
    )
    session.add(security_violation)
    session.commit()
    return security_violation


@pytest.fixture(scope="session")
def home_org_security_report_fixture(session, home_org_scan_fixture):
    security_report = SecurityReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=home_org_scan_fixture,
    )
    session.add(security_report)
    session.commit()
    return security_report


@pytest.fixture(scope="session")
def home_org_security_violation_fixture(session, home_org_security_report_fixture):
    security_violation = SecurityViolation(
        violation="violation",
        risk="risk",
        confidence="confidence",
        solution="solution",
        reference="reference",
        data=[{"uri": "https://example.com/", "method": "POST", "evidence": "foo"}],
        tags="tags",
        url="url",
        security_report=home_org_security_report_fixture,
    )
    session.add(security_violation)
    session.commit()
    return security_violation


@pytest.fixture(scope="session")
def home_org_security_report_fixture_2(session, home_org_scan_fixture):
    security_report = SecurityReport(
        product="product",
        revision="revision",
        url="url",
        summary={"jsonb": "data"},
        scan=home_org_scan_fixture,
    )
    session.add(security_report)
    session.commit()
    return security_report


@pytest.fixture(scope="session")
def home_org_security_violation_fixture_2(session, home_org_security_report_fixture_2):
    security_violation = SecurityViolation(
        violation="violation",
        risk="risk",
        confidence="confidence",
        solution="solution",
        reference="reference",
        data=[{"uri": "https://example.com/", "method": "POST", "evidence": "foo"}],
        tags="tags",
        url="url",
        security_report=home_org_security_report_fixture_2,
    )
    session.add(security_violation)
    session.commit()
    return security_violation


@pytest.fixture
def assert_new_model_saved():
    def f(model):
        assert model.id is not None
        assert model.created_at is not None
        assert model.updated_at is None

    return f


@pytest.fixture
def context_fixture():
    context = MagicMock()
    context.function_name = "api"
    return context


@pytest.fixture(scope="session")
def organisation_fixture(session):
    organisation = Organisation(name="fixture_name")
    session.add(organisation)
    session.commit()
    return organisation


@pytest.fixture(scope="session")
def home_organisation_fixture(session):
    home_org = (
        session.query(Organisation)
        .filter(
            Organisation.name == "Canadian Digital Service - Service Numérique Canadien"
        )
        .scalar()
    )
    return home_org


@pytest.fixture(scope="session")
def session():
    db_engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_TEST_URI"))
    Session = sessionmaker(bind=db_engine)
    session = Session()
    UserFactory._meta.sqlalchemy_session = session
    OrganisationFactory._meta.sqlalchemy_session = session
    SecurityReportFactory._meta.sqlalchemy_session = session
    SecurityViolationFactory._meta.sqlalchemy_session = session
    ScanFactory._meta.sqlalchemy_session = session
    ScanTypeFactory._meta.sqlalchemy_session = session
    TemplateFactory._meta.sqlalchemy_session = session
    TemplateScanFactory._meta.sqlalchemy_session = session
    return session


@pytest.fixture(scope="session", autouse=True)
def setup_db(session):
    os.environ["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_TEST_URI"
    )
    alembic_cfg = Config("./db_migrations/alembic.ini")
    alembic_cfg.set_main_option("script_location", "./db_migrations")

    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")
    yield


@pytest.fixture(scope="session")
def scan_fixture(scan_type_fixture, template_fixture, organisation_fixture, session):
    scan = Scan(
        organisation=organisation_fixture,
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(scan)
    session.commit()
    return scan


@pytest.fixture(scope="session")
def home_org_scan_fixture(
    owasp_zap_fixture,
    home_org_template_fixture,
    home_organisation_fixture,
    session,
):
    scan = Scan(
        organisation=home_organisation_fixture,
        scan_type=owasp_zap_fixture,
        template=home_org_template_fixture,
    )
    session.add(scan)
    session.commit()
    return scan


@pytest.fixture(scope="session")
def home_org_owasp_scan_fixture(
    owasp_zap_fixture,
    home_org_owasp_zap_template_fixture,
    home_organisation_fixture,
    session,
):
    scan = Scan(
        organisation=home_organisation_fixture,
        scan_type=owasp_zap_fixture,
        template=home_org_owasp_zap_template_fixture,
    )
    session.add(scan)
    session.commit()
    return scan


@pytest.fixture(scope="session")
def scan_type_fixture(session):
    scan_type = ScanType(
        name="fixture_name", callback={"event": "sns", "topic_env": "topic"}
    )
    session.add(scan_type)
    session.commit()
    return scan_type


@pytest.fixture(scope="session")
def template_fixture(session, organisation_fixture):
    template = Template(name="fixture_name", organisation=organisation_fixture)
    session.add(template)
    session.commit()
    return template


@pytest.fixture(scope="session")
def owasp_zap_fixture(session):
    owasp_zap_scan_type = (
        session.query(ScanType)
        .filter(ScanType.name == pub_sub.AvailableScans.OWASP_ZAP.value)
        .scalar()
    )
    return owasp_zap_scan_type


@pytest.fixture(scope="session")
def home_org_owasp_zap_template_fixture(session, home_organisation_fixture):
    template = Template(name="Scan OWASP", organisation=home_organisation_fixture)
    session.add(template)
    session.commit()
    return template


@pytest.fixture(scope="session")
def template_scan_fixture(scan_type_fixture, template_fixture, session):
    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(template_scan)
    session.commit()
    return template_scan


@pytest.fixture(scope="session")
def user_fixture(session):
    user = User(name="fixture_name")
    session.add(user)
    return user


@pytest.fixture(scope="session")
def regular_user_fixture():
    user_info = {
        "email": "user@cds-snc.ca",
        "name": "User McUser",
    }
    return user_info


@pytest.fixture(scope="session")
def logged_in_client(regular_user_fixture):
    with patch(
        "api_gateway.routers.auth.oauth.google.authorize_access_token",
        return_value={"access_token": "TOKEN"},
    ), patch(
        "api_gateway.routers.auth.oauth.google.parse_id_token",
        return_value=UserInfo(regular_user_fixture),
    ):
        client = TestClient(api.app)
        client.get("/auth/google")
        yield client


@pytest.fixture(scope="function")
def authorized_request(session, client):
    organisation = OrganisationFactory()
    user = UserFactory(organisation=organisation)
    session.commit()
    client.post(f"/login/ci/{user.email_address}")
    yield client, user, organisation


@pytest.fixture(scope="session")
def loggedin_user_fixture(logged_in_client, regular_user_fixture, session):
    user = (
        session.query(User)
        .filter(User.email_address == regular_user_fixture["email"])
        .scalar()
    )
    return user


# https://github.com/tiangolo/fastapi/issues/1472; has to be tested seperate from Jinja2 routes
@pytest.fixture
def hsts_middleware_client():
    app = FastAPI()
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_security_headers)
    app.include_router(ops.router, prefix="/ops", tags=["ops"])
    client = TestClient(app)
    yield client
