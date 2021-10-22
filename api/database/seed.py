import json
import os
import string
import sys
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path = ["", ".."] + sys.path[1:]

# noqa for all the below since they're below the sys and will trigger E402
from models.A11yReport import A11yReport  # noqa: E402
from models.A11yViolation import A11yViolation  # noqa: E402
from models.SecurityReport import SecurityReport  # noqa: E402
from models.SecurityViolation import SecurityViolation  # noqa: E402
from models.Organisation import Organisation  # noqa: E402
from models.Scan import Scan  # noqa: E402
from models.ScanIgnore import ScanIgnore  # noqa: E402
from models.ScanType import ScanType  # noqa: E402
from models.Template import Template  # noqa: E402
from models.TemplateScan import TemplateScan  # noqa: E402
from models.TemplateScanTrigger import TemplateScanTrigger  # noqa: E402
from models.User import User  # noqa: E402
from pub_sub import pub_sub  # noqa: E402
from storage import storage  # noqa: E402

if __name__ == "__main__":
    db_engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URI"))
    Session = sessionmaker(bind=db_engine)
    session = Session()
    letters = string.ascii_lowercase

    cds_org = (
        session.query(Organisation)
        .filter(
            Organisation.name == "Canadian Digital Service - Service Numérique Canadien"
        )
        .scalar()
    )

    owasp_zap_scan_type = (
        session.query(ScanType)
        .filter(ScanType.name == pub_sub.AvailableScans.OWASP_ZAP.value)
        .scalar()
    )

    axe_core_scan_type = (
        session.query(ScanType)
        .filter(ScanType.name == pub_sub.AvailableScans.AXE_CORE.value)
        .scalar()
    )

    print("Deleting all previous data ...")

    session.query(A11yViolation).delete()
    session.query(A11yReport).delete()
    session.query(SecurityViolation).delete()
    session.query(SecurityReport).delete()
    session.query(ScanIgnore).delete()
    session.query(Scan).delete()
    session.query(TemplateScanTrigger).delete()
    session.query(TemplateScan).delete()
    session.query(Template).delete()
    session.query(User).delete()

    print("Adding new data ...")

    user = User(
        name="Seed User",
        email_address="scan-websites+seed@cds-sns.ca",
        organisation=cds_org,
    )

    owasp_zap_template = Template(
        name="OWASP Zap template",
        organisation=cds_org,
    )
    session.add(owasp_zap_template)

    axe_core_template = Template(
        name="Axe core template",
        organisation=cds_org,
    )
    session.add(axe_core_template)

    combined_template = Template(
        name="Combined template",
        organisation=cds_org,
    )
    session.add(combined_template)

    owasp_zap_template_scan = TemplateScan(
        data={"url": "https://www.example.com"},
        scan_type=owasp_zap_scan_type,
        template=combined_template,
    )
    session.add(owasp_zap_template_scan)

    axe_core_template_scan = TemplateScan(
        data={"url": "https://www.alpha.canada.ca"},
        scan_type=axe_core_scan_type,
        template=combined_template,
    )
    session.add(axe_core_template_scan)

    owasp_zap_scan = Scan(
        organisation=cds_org,
        scan_type=owasp_zap_scan_type,
        template=combined_template,
    )
    session.add(owasp_zap_scan)

    axe_core_scan = Scan(
        organisation=cds_org,
        scan_type=axe_core_scan_type,
        template=combined_template,
    )
    session.add(axe_core_scan)

    owasp_zap_report_f = open(
        "./tests/storage/fixtures/owasp_zap_report.json",
    )
    axe_core_report_f = open(
        "./tests/storage/fixtures/axe_core_report.json",
    )

    owasp_zap_data = json.load(owasp_zap_report_f)
    axe_core_data = json.load(axe_core_report_f)

    # Create 5 reports with 10 violations each
    for _ in range(5):
        a11y_report = A11yReport(
            product="product",
            revision=str(uuid.uuid4()),
            url="https://www.alpha.canada.ca",
            summary={
                "status": "completed",
                "inapplicable": 1,
                "incomplete": 1,
                "violations": 1,
                "passes": 1,
            },
            scan=axe_core_scan,
        )
        session.add(a11y_report)

        security_report = SecurityReport(
            product="product",
            revision=str(uuid.uuid4()),
            url="https://www.example.com",
            summary={
                "status": "completed",
            },
            scan=owasp_zap_scan,
        )
        session.add(security_report)

        session.commit()

        axe_core_data["id"] = str(a11y_report.id)
        storage.store_axe_core_record(session, axe_core_data)

        owasp_zap_data["id"] = str(security_report.id)
        storage.store_owasp_zap_record(session, owasp_zap_data)

    print("Seed completed!")
