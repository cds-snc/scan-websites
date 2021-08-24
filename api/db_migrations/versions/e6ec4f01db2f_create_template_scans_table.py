"""create template scans table

Revision ID: e6ec4f01db2f
Revises: bf6d44121dce
Create Date: 2021-08-24 13:59:34.800116

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e6ec4f01db2f"
down_revision = "bf6d44121dce"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "template_scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scan_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
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
    op.drop_table("template_scans")
