"""nuclei scan type

Revision ID: 4ca6527d0034
Revises: b77929e07997
Create Date: 2021-10-28 15:43:00.841879

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision = "4ca6527d0034"
down_revision = "b77929e07997"
branch_labels = None
depends_on = None


def upgrade():
    meta = sa.MetaData(bind=op.get_bind())
    meta.reflect(only=("scan_types",))
    scan_types = sa.Table("scan_types", meta)

    op.bulk_insert(
        scan_types,
        [
            {
                "id": str(uuid.uuid4()),
                "name": "Nuclei",
                "callback": {"event": "sns", "topic_env": "NUCLEI_URLS_TOPIC"},
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ],
    )


def downgrade():
    op.execute("""DELETE FROM "scan_types" WHERE name = 'Nuclei'; """)
