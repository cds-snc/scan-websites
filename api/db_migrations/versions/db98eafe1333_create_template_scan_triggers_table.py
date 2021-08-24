"""create template scan triggers table

Revision ID: db98eafe1333
Revises: e6ec4f01db2f
Create Date: 2021-08-24 17:21:59.537651

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "db98eafe1333"
down_revision = "e6ec4f01db2f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "template_scan_triggers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("template_scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("callback", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
        sa.ForeignKeyConstraint(
            ["template_scan_id"],
            ["template_scans.id"],
        ),
    )


def downgrade():
    op.drop_table("template_scan_triggers")
