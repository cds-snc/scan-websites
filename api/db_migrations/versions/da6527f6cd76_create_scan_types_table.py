"""create scan types table

Revision ID: da6527f6cd76
Revises: b9ab107cd56a
Create Date: 2021-08-23 20:09:57.730128

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "da6527f6cd76"
down_revision = "b9ab107cd56a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "scan_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Unicode(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
    )


def downgrade():
    op.drop_table("scan_types")
