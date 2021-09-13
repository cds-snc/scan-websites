import os
import pytest
from unittest.mock import MagicMock

from alembic.config import Config
from alembic import command

from models.A11yReport import A11yReport
from models.Organisation import Organisation
from models.Scan import Scan
from models.ScanType import ScanType
from models.Template import Template
from models.TemplateScan import TemplateScan
from models.User import User


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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
    return organisation


@pytest.fixture(scope="session")
def session():
    db_engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_TEST_URI"))
    Session = sessionmaker(bind=db_engine)
    return Session()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
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
    return scan


@pytest.fixture(scope="session")
def scan_type_fixture(session):
    scan_type = ScanType(name="fixture_name")
    session.add(scan_type)
    return scan_type


@pytest.fixture(scope="session")
def template_fixture(session, organisation_fixture):
    template = Template(name="fixture_name", organisation=organisation_fixture)
    session.add(template)
    return template


@pytest.fixture(scope="session")
def template_scan_fixture(scan_type_fixture, template_fixture, session):
    template_scan = TemplateScan(
        data={"jsonb": "data"},
        scan_type=scan_type_fixture,
        template=template_fixture,
    )
    session.add(template_scan)
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
