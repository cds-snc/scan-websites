import os
import pytest

from alembic.config import Config
from alembic import command

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def session():
    db_engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_TEST_URI"))
    Session = sessionmaker(bind=db_engine)
    return Session()


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    os.chdir("./db_migrations")
    os.environ["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_TEST_URI"
    )
    alembic_cfg = Config("./alembic.ini")
    command.downgrade(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")

    yield
