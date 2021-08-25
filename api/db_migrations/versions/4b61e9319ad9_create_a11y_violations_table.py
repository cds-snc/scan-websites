"""create a11y_violations table

Revision ID: 4b61e9319ad9
Revises: e251ec3b0f77
Create Date: 2021-08-24 21:30:09.916966

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4b61e9319ad9"
down_revision = "e251ec3b0f77"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "a11y_violations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("a11y_report_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("violation", sa.String(), nullable=False),
        sa.Column("impact", sa.String(), nullable=False),
        sa.Column("target", sa.Text()),
        sa.Column("html", sa.Text()),
        sa.Column("data", postgresql.JSONB(), nullable=False),
        sa.Column("tags", postgresql.JSONB(), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("url", sa.String()),
        sa.Column("created_at", sa.DateTime, default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
        sa.ForeignKeyConstraint(
            ["a11y_report_id"],
            ["a11y_reports.id"],
        ),
    )


def downgrade():
    op.drop_table("a11y_violations")
