"""Added scan ignore table

Revision ID: 09b1dec8eb5d
Revises: ee2ca4ffaee4
Create Date: 2021-10-19 17:26:20.431031

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "09b1dec8eb5d"
down_revision = "ee2ca4ffaee4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "scan_ignores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("violation", sa.String(), nullable=False),
        sa.Column("ignore_condition", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["scan_id"],
            ["scans.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_scan_ignores_scan_id"), "scan_ignores", ["scan_id"], unique=False
    )
    op.alter_column(
        "a11y_reports",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.create_index(
        op.f("ix_a11y_reports_scan_id"), "a11y_reports", ["scan_id"], unique=False
    )
    op.alter_column(
        "a11y_violations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.create_index(
        op.f("ix_a11y_violations_a11y_report_id"),
        "a11y_violations",
        ["a11y_report_id"],
        unique=False,
    )
    op.alter_column(
        "organisations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.alter_column(
        "scan_types",
        "callback",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        nullable=False,
    )
    op.alter_column(
        "scan_types", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.alter_column(
        "scans", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.create_index(
        op.f("ix_scans_organisation_id"), "scans", ["organisation_id"], unique=False
    )
    op.create_index(
        op.f("ix_scans_scan_type_id"), "scans", ["scan_type_id"], unique=False
    )
    op.create_index(
        op.f("ix_scans_template_id"), "scans", ["template_id"], unique=False
    )
    op.alter_column(
        "security_reports",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.create_index(
        op.f("ix_security_reports_scan_id"),
        "security_reports",
        ["scan_id"],
        unique=False,
    )
    op.alter_column(
        "security_violations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.create_index(
        op.f("ix_security_violations_security_report_id"),
        "security_violations",
        ["security_report_id"],
        unique=False,
    )
    op.alter_column(
        "template_scan_triggers", "name", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "template_scan_triggers",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.create_unique_constraint(None, "template_scan_triggers", ["name"])
    op.alter_column(
        "template_scans",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
    )
    op.create_index(
        op.f("ix_template_scans_scan_type_id"),
        "template_scans",
        ["scan_type_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_template_scans_template_id"),
        "template_scans",
        ["template_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_template_scans_template_scan_trigger_id"),
        "template_scans",
        ["template_scan_trigger_id"],
        unique=False,
    )
    op.create_foreign_key(
        None,
        "template_scans",
        "template_scan_triggers",
        ["template_scan_trigger_id"],
        ["id"],
    )
    op.alter_column(
        "templates", "token", existing_type=postgresql.UUID(), nullable=True
    )
    op.alter_column(
        "templates", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.drop_constraint("templates_token_key", "templates", type_="unique")
    op.create_index(
        op.f("ix_templates_organisation_id"),
        "templates",
        ["organisation_id"],
        unique=False,
    )
    op.alter_column(
        "users", "access_token", existing_type=postgresql.UUID(), nullable=True
    )
    op.alter_column(
        "users", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.drop_constraint("users_access_token_key", "users", type_="unique")
    op.create_index(
        op.f("ix_users_organisation_id"), "users", ["organisation_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_organisation_id"), table_name="users")
    op.create_unique_constraint("users_access_token_key", "users", ["access_token"])
    op.alter_column(
        "users", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "users", "access_token", existing_type=postgresql.UUID(), nullable=False
    )
    op.drop_index(op.f("ix_templates_organisation_id"), table_name="templates")
    op.create_unique_constraint("templates_token_key", "templates", ["token"])
    op.alter_column(
        "templates", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "templates", "token", existing_type=postgresql.UUID(), nullable=False
    )
    op.drop_constraint(
        "template_scans_template_scan_trigger_id_fkey",
        "template_scans",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_template_scans_template_scan_trigger_id"), table_name="template_scans"
    )
    op.drop_index(op.f("ix_template_scans_template_id"), table_name="template_scans")
    op.drop_index(op.f("ix_template_scans_scan_type_id"), table_name="template_scans")
    op.alter_column(
        "template_scans",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.drop_constraint(
        "template_scan_triggers_name_key", "template_scan_triggers", type_="unique"
    )
    op.alter_column(
        "template_scan_triggers",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.alter_column(
        "template_scan_triggers", "name", existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_index(
        op.f("ix_security_violations_security_report_id"),
        table_name="security_violations",
    )
    op.alter_column(
        "security_violations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.drop_index(op.f("ix_security_reports_scan_id"), table_name="security_reports")
    op.alter_column(
        "security_reports",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.drop_index(op.f("ix_scans_template_id"), table_name="scans")
    op.drop_index(op.f("ix_scans_scan_type_id"), table_name="scans")
    op.drop_index(op.f("ix_scans_organisation_id"), table_name="scans")
    op.alter_column(
        "scans", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "scan_types", "created_at", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "scan_types",
        "callback",
        existing_type=postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    )
    op.alter_column(
        "organisations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.drop_index(
        op.f("ix_a11y_violations_a11y_report_id"), table_name="a11y_violations"
    )
    op.alter_column(
        "a11y_violations",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.drop_index(op.f("ix_a11y_reports_scan_id"), table_name="a11y_reports")
    op.alter_column(
        "a11y_reports",
        "created_at",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
    )
    op.drop_index(op.f("ix_scan_ignores_scan_id"), table_name="scan_ignores")
    op.drop_table("scan_ignores")
    # ### end Alembic commands ###
