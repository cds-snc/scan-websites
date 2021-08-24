"""create scans table

Revision ID: eb58f2b364a3
Revises: db98eafe1333
Create Date: 2021-08-24 18:35:42.224567

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "eb58f2b364a3"
down_revision = "db98eafe1333"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scan_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["templates.id"],
        ),
        sa.ForeignKeyConstraint(
            ["scan_type_id"],
            ["scan_types.id"],
        ),
    )


def downgrade():
    op.drop_table("scans")
