"""cleanup orphaned scans

Revision ID: ee2ca4ffaee4
Revises: 9cceeaa52f49
Create Date: 2021-10-14 13:44:27.460893

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ee2ca4ffaee4"
down_revision = "9cceeaa52f49"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DELETE FROM a11y_violations;
        DELETE FROM a11y_reports;
        DELETE FROM security_violations;
        DELETE FROM security_reports;
        DELETE FROM scans;
        """
    )


def downgrade():
    pass
