from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from api_gateway import api
from front_end.view import get_risk_colour
from factories import (
    OrganisationFactory,
    ScanFactory,
    ScanTypeFactory,
    SecurityReportFactory,
    SecurityViolationFactory,
    TemplateFactory,
    TemplateScanFactory,
)
from pub_sub.pub_sub import AvailableScans

client = TestClient(api.app)


def test_loading_scan_results_not_logged_in(session):
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    response = client.get(f"/en/results/{template.id}/scan/{scan.id}")
    assert response.status_code == 401


def test_landing_page_error_logged_in_not_my_template(
    session,
    authorized_request,
):
    logged_in_client, _, _ = authorized_request
    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    response = logged_in_client.get(f"/en/results/{template.id}/scan/{scan.id}")
    assert response.status_code == 401


def test_security_report_findings(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    session.commit()

    response = logged_in_client.get(f"/en/results/{template.id}/scan/{scan.id}")
    assert response.status_code == 200
    assert response.template.name == "scan_results_security.html"


@patch("front_end.scan_view.db_session")
def test_security_report_findings_unknown_error(
    mock_db_session, session, authorized_request
):
    mock_session = MagicMock()
    mock_session.query().side_effect = SQLAlchemyError()
    mock_db_session.return_value = mock_session

    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    SecurityReportFactory(scan=scan)
    session.commit()

    response = logged_in_client.get(f"/en/results/{template.id}/scan/{scan.id}")
    assert response.status_code == 500


def test_security_report_violations_not_authorized(
    session,
    authorized_request,
):
    _, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    security_report = SecurityReportFactory(scan=scan)
    session.commit()

    response = client.get(
        f"/en/results/{template.id}/security/{scan.id}/{security_report.id}"
    )
    assert response.status_code == 401


def test_security_report_violations(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    security_report = SecurityReportFactory(scan=scan)
    session.commit()

    response = logged_in_client.get(
        f"/en/results/{template.id}/security/{scan.id}/{security_report.id}"
    )
    assert response.status_code == 200
    assert response.template.name == "scan_results_security_summary.html"


def test_security_report_violation_details(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    security_report = SecurityReportFactory(scan=scan)
    security_violation = SecurityViolationFactory(security_report=security_report)
    session.commit()

    response = logged_in_client.get(
        f"/en/results/{template.id}/security/{scan.id}/{security_report.id}/{security_violation.id}"
    )
    assert response.status_code == 200
    assert response.template.name == "scan_results_security_details.html"


def risk_colour_assignment_valid():
    assert get_risk_colour("0") == "bg-blue-500"
    assert get_risk_colour("1") == "bg-green-500"
    assert get_risk_colour("2") == "bg-yellow-600"
    assert get_risk_colour("3") == "bg-red-500"


def risk_colour_assignment_invalid_defaults_gray():
    assert get_risk_colour("foo") == "bg-gray-500"
