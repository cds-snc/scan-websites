import os
import pytest
from unittest.mock import MagicMock

from alembic.config import Config
from alembic import command

from api_gateway import api

from fastapi.testclient import TestClient

from factories import (
    A11yReportFactory,
    A11yViolationFactory,
    OrganisationFactory,
    ScanFactory,
    ScanIgnoreFactory,
    ScanTypeFactory,
    SecurityReportFactory,
    SecurityViolationFactory,
    TemplateFactory,
    TemplateScanFactory,
    UserFactory,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def client():
    client = TestClient(api.app)
    yield client


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
def session():
    db_engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_TEST_URI"))
    Session = sessionmaker(bind=db_engine)
    session = Session()
    A11yReportFactory._meta.sqlalchemy_session = session
    A11yViolationFactory._meta.sqlalchemy_session = session
    UserFactory._meta.sqlalchemy_session = session
    OrganisationFactory._meta.sqlalchemy_session = session
    SecurityReportFactory._meta.sqlalchemy_session = session
    SecurityViolationFactory._meta.sqlalchemy_session = session
    ScanFactory._meta.sqlalchemy_session = session
    ScanIgnoreFactory._meta.sqlalchemy_session = session
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


@pytest.fixture(scope="function")
def authorized_request(session, client):
    organisation = OrganisationFactory()
    user = UserFactory(organisation=organisation)
    session.commit()
    client.post(f"/login/ci/{user.email_address}")
    yield client, user, organisation
