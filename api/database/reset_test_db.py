import os
import sys

from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine

# Add parent to PYTHONPATH. This is needed since models is not in the PYTHONPATH when db migrations are generated
sys.path = ["", ".."] + sys.path[1:]

from models import (  # noqa
    Base,
    A11yReport,
    A11yViolation,
    Organisation,
    Scan,
    ScanIgnore,
    ScanType,
    SecurityReport,
    SecurityViolation,
    Template,
    TemplateScan,
    TemplateScanTrigger,
    User,
)

# This code will reset the test database in-case it gets into a unstable state
if __name__ == "__main__":
    os.environ["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "SQLALCHEMY_DATABASE_TEST_URI"
    )

    engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_TEST_URI"))
    Base.metadata.drop_all(bind=engine)

    alembic_cfg = Config("../db_migrations/alembic.ini")
    alembic_cfg.set_main_option("script_location", "../db_migrations")

    command.stamp(alembic_cfg, "base")
    command.upgrade(alembic_cfg, "head")
