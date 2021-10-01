"""setup template scan triggers

Revision ID: 9cceeaa52f49
Revises: 85d881a256c0
Create Date: 2021-10-01 14:17:01.414218

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision = "9cceeaa52f49"
down_revision = "85d881a256c0"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("template_scan_triggers", "template_scan_id")
    op.add_column("template_scan_triggers", sa.Column("name", sa.String()))
    op.add_column("scan_types", sa.Column("callback", postgresql.JSONB()))

    meta = sa.MetaData(bind=op.get_bind())
    meta.reflect(only=("template_scan_triggers", "scan_types"))
    template_scan_triggers = sa.Table("template_scan_triggers", meta)

    op.execute(
        """
        UPDATE scan_types SET callback='{"event":"sns","topic_env":"AXE_CORE_URLS_TOPIC"}' where name = 'axe-core';
        UPDATE scan_types SET callback='{"event":"sns","topic_env":"OWASP_ZAP_URLS_TOPIC"}' where name = 'OWASP Zap';
        """
    )
    op.bulk_insert(
        template_scan_triggers,
        [
            {
                "id": str(uuid.uuid4()),
                "name": "daily",
                "callback": {"event": "cron", "expression": "0 3 * * *"},
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": str(uuid.uuid4()),
                "name": "weekly",
                "callback": {"event": "cron", "expression": "0 3 * * 0"},
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ],
    )


def downgrade():
    op.execute(
        """
        DELETE FROM template_scan_triggers;
        """
    )
    op.drop_column("template_scan_triggers", "name")
    op.drop_column("scan_types", "callback")
    op.add_column(
        "template_scan_triggers",
        sa.Column("template_scan_id", postgresql.UUID(as_uuid=True)),
    )
