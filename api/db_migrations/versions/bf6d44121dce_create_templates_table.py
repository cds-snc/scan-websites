"""create templates table

Revision ID: bf6d44121dce
Revises: da6527f6cd76
Create Date: 2021-08-24 13:14:26.089149

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "bf6d44121dce"
down_revision = "da6527f6cd76"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisations.id"],
        ),
    )


def downgrade():
    op.drop_table("templates")
