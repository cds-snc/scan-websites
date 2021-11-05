"""Migrate zap & nuclei to step function

Revision ID: ff660f256a86
Revises: 4ca6527d0034
Create Date: 2021-11-05 14:24:35.495027

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ff660f256a86"
down_revision = "4ca6527d0034"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE scan_types SET callback='{"event":"stepfunctions","state_machine_name":"dynamic-security-scans"}' where name = 'Nuclei';
        UPDATE scan_types SET callback='{"event":"stepfunctions","state_machine_name":"dynamic-security-scans"}' where name = 'OWASP Zap';
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE scan_types SET callback='{"event":"sns","topic_env":"NUCLEI_URLS_TOPIC"}' where name = 'Nuclei';
        UPDATE scan_types SET callback='{"event":"sns","topic_env":"OWASP_ZAP_URLS_TOPIC"}' where name = 'OWASP Zap';
        """
    )
