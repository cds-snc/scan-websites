"""create a11y_reports table

Revision ID: e251ec3b0f77
Revises: eb58f2b364a3
Create Date: 2021-08-24 19:49:08.946361

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e251ec3b0f77"
down_revision = "eb58f2b364a3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "a11y_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product", sa.String(), nullable=False),
        sa.Column("revision", sa.String(), nullable=False),
        sa.Column("url", sa.String()),
        sa.Column("ci", sa.Boolean, unique=False, default=False),
        sa.Column("summary", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
        sa.ForeignKeyConstraint(
            ["scan_id"],
            ["scans.id"],
        ),
    )


def downgrade():
    op.drop_table("a11y_reports")
