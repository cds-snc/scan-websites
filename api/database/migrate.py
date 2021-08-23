from alembic.config import Config
from alembic import command


def migrate_head():
    alembic_cfg = Config("./db_migrations/alembic.ini")
    alembic_cfg.set_main_option("script_location", "./db_migrations")
    command.upgrade(alembic_cfg, "head")
