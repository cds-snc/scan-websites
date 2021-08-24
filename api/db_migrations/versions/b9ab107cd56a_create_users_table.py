"""create_users_table

Revision ID: b9ab107cd56a
Revises: 06b310a6251e
Create Date: 2021-08-13 16:10:56.221141

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "b9ab107cd56a"
down_revision = "06b310a6251e"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email_address", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "access_token", postgresql.UUID(as_uuid=True), nullable=False, unique=True
        ),
        sa.Column("created_at", sa.DateTime, default=sa.func.utc_timestamp()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.utc_timestamp()),
        sa.ForeignKeyConstraint(
            ["organisation_id"],
            ["organisations.id"],
        ),
    )


def downgrade():
    op.drop_table("users")
