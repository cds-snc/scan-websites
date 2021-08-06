from alembic.config import Config
from alembic import command


def migrate_head():
    alembic_cfg = Config("./db_migrations/alembic.ini")
    command.upgrade(alembic_cfg, "head")
