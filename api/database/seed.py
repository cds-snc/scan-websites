import os
import random
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
from pub_sub import pub_sub  # noqa: E402

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

    session.query(A11yViolation).delete()
    session.query(A11yReport).delete()
    session.query(SecurityViolation).delete()
    session.query(SecurityReport).delete()
    session.query(ScanIgnore).delete()
    session.query(Scan).delete()
    session.query(TemplateScanTrigger).delete()
    session.query(TemplateScan).delete()
    session.query(Template).delete()

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

    owasp_zap_template_scan = TemplateScan(
        data={"url": "https://www.example.com"},
        scan_type=owasp_zap_scan_type,
        template=owasp_zap_template,
    )
    session.add(owasp_zap_template_scan)

    axe_core_template_scan = TemplateScan(
        data={"url": "https://www.alpha.canada.ca"},
        scan_type=axe_core_scan_type,
        template=axe_core_template,
    )
    session.add(axe_core_template_scan)

    owasp_zap_scan = Scan(
        organisation=cds_org,
        scan_type=owasp_zap_scan_type,
        template=owasp_zap_template,
    )
    session.add(owasp_zap_scan)

    axe_core_scan = Scan(
        organisation=cds_org,
        scan_type=axe_core_scan_type,
        template=axe_core_template,
    )
    session.add(axe_core_scan)

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

        for _ in range(10):
            a11y_violation = A11yViolation(
                violation="".join(random.choice(letters) for i in range(10)),
                impact="impact",
                target="target",
                html="html",
                data={"jsonb": "data"},
                tags={"jsonb": "tags"},
                message="message",
                url="url",
                a11y_report=a11y_report,
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

        for _ in range(10):
            security_violation = SecurityViolation(
                violation="".join(random.choice(letters) for i in range(10)),
                risk="Low (Medium)",
                message="message",
                confidence=str(random.randint(1, 3)),
                solution="<p>Phase: Architecture and Design</p><p>Use a vetted library or framework that does not allow this weakness to occur or provides constructs that make this weakness easier to avoid.</p><p>For example, use anti-CSRF packages such as the OWASP CSRFGuard.</p><p></p><p>Phase: Implementation</p><p>Ensure that your application is free of cross-site scripting issues, because most CSRF defenses can be bypassed using attacker-controlled script.</p><p></p><p>Phase: Architecture and Design</p><p>Generate a unique nonce for each form, place the nonce into the form, and verify the nonce upon receipt of the form. Be sure that the nonce is not predictable (CWE-330).</p><p>Note that this can be bypassed using XSS.</p><p></p><p>Identify especially dangerous operations. When the user performs a dangerous operation, send a separate confirmation request to ensure that the user intended to perform that operation.</p><p>Note that this can be bypassed using XSS.</p><p></p><p>Use the ESAPI Session Management control.</p><p>This control includes a component for CSRF.</p><p></p><p>Do not use the GET method for any request that triggers a state change.</p><p></p><p>Phase: Implementation</p><p>Check the HTTP Referer header to see if the request originated from an expected page. This could break legitimate functionality, because users or proxies may have disabled sending the Referer for privacy reasons.</p>",
                reference="<p>http://projects.webappsec.org/Cross-Site-Request-Forgery</p><p>http://cwe.mitre.org/data/definitions/352.html</p>",
                data=[
                    {
                        "uri": "https://example.com/",
                        "method": "GET",
                        "param": "Cache-Control",
                        "evidence": "s-maxage=31536000, stale-while-revalidate",
                    },
                    {
                        "uri": "https://example.com",
                        "method": "GET",
                        "param": "Cache-Control",
                        "evidence": "s-maxage=31536000, stale-while-revalidate",
                    },
                    {
                        "uri": "https://example.com/fr/privacy-confidentialite",
                        "method": "GET",
                        "param": "Cache-Control",
                        "evidence": "s-maxage=31536000, stale-while-revalidate",
                    },
                    {
                        "uri": "https://example.com/en/privacy-confidentialite",
                        "method": "GET",
                        "param": "Cache-Control",
                        "evidence": "s-maxage=31536000, stale-while-revalidate",
                    },
                ],
                tags={
                    "alertRef": "".join(random.choice(letters) for i in range(5)),
                    "riskcode": str(random.randint(1, 3)),
                    "cweid": "".join(random.choice(letters) for i in range(3)),
                    "otherinfo": '<p>No known Anti-CSRF token [anticsrf, CSRFToken, __RequestVerificationToken, csrfmiddlewaretoken, authenticity_token, OWASP_CSRFTOKEN, anoncsrf, csrf_token, _csrf, _csrfSecret, __csrf_magic, CSRF] was found in the following HTML form: [Form 1: "2" "3" "4" "5" ].</p>',
                },
                url="https://www.example.com",
                security_report=security_report,
            )
            session.add(security_violation)

    session.commit()
