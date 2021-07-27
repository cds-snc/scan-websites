"""create_organisations_table

Revision ID: 06b310a6251e
Revises: 
Create Date: 2021-07-27 00:24:48.480009

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "06b310a6251e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "organisations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Unicode(255), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
    )


def downgrade():
    op.drop_table("organisations")
