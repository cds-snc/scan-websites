import os
import pytest

from alembic.config import Config
from alembic import command

from models.Organisation import Organisation
from models.ScanType import ScanType
from models.Template import Template
from models.TemplateScan import TemplateScan


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def assert_new_model_saved():
    def f(model):
        assert model.id is not None
        assert model.created_at is not None
        assert model.updated_at is None

    return f


@pytest.fixture(scope="session")
def organisation_fixture(session):
    organisation = Organisation(name="name")
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
def scan_type_fixture(session):
    scan_type = ScanType(name="name")
    session.add(scan_type)
    return scan_type


@pytest.fixture(scope="session")
def template_fixture(session, organisation_fixture):
    template = Template(name="name", organisation=organisation_fixture)
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
