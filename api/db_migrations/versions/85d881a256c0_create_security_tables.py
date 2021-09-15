"""Create security tables

Revision ID: 85d881a256c0
Revises: 5818f4679595
Create Date: 2021-09-15 19:13:38.286350

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "85d881a256c0"
down_revision = "5818f4679595"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "security_reports",
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

    op.create_table(
        "security_violations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("security_report_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("violation", sa.String(), nullable=False),
        sa.Column("risk", sa.String(), nullable=False),
        sa.Column("confidence", sa.String(), nullable=False),
        sa.Column("solution", sa.Text()),
        sa.Column("reference", sa.Text()),
        sa.Column("target", sa.Text()),
        sa.Column("data", postgresql.JSONB(), nullable=False),
        sa.Column("tags", postgresql.JSONB(), nullable=False),
        sa.Column("message", sa.Text()),
        sa.Column("url", sa.String()),
        sa.Column("created_at", sa.DateTime, default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
        sa.ForeignKeyConstraint(
            ["security_report_id"],
            ["security_reports.id"],
        ),
    )


def downgrade():
    op.drop_table("security_violations")
    op.drop_table("security_reports")
