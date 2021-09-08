"""seed databases and allow nullable password_hash

Revision ID: 5818f4679595
Revises: 4b61e9319ad9
Create Date: 2021-09-08 14:27:33.384835

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision = "5818f4679595"
down_revision = "4b61e9319ad9"
branch_labels = None
depends_on = None


def upgrade():
    meta = sa.MetaData(bind=op.get_bind())
    meta.reflect(only=("organisations", "scan_types", "users"))
    organisations = sa.Table("organisations", meta)
    scan_types = sa.Table("scan_types", meta)

    op.alter_column("users", "password_hash", nullable=True)

    op.bulk_insert(
        organisations,
        [
            {
                "id": str(uuid.uuid4()),
                "name": "Canadian Digital Service - Service Numérique Canadien",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        ],
    )

    op.bulk_insert(
        scan_types,
        [
            {
                "id": str(uuid.uuid4()),
                "name": "Accessibility - Accessibilité",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Security - Sécurité",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ],
    )


def downgrade():
    op.execute("UPDATE users SET password_hash = '' WHERE password_hash IS NULL")
    op.alter_column("users", "password_hash", nullable=False)

    op.execute(
        """DELETE FROM "organisations" WHERE name = 'Canadian Digital Service - Service Numérique Canadien'; """
    )
    op.execute(
        """DELETE FROM "scan_types" WHERE name = 'Accessibility - Accessibilité'; """
    )
    op.execute("""DELETE FROM "scan_types" WHERE name = 'Security - Sécurité'; """)
