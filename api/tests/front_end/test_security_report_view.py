from fastapi.testclient import TestClient

from api_gateway import api

client = TestClient(api.app)


def test_loading_scan_results_not_logged_in(scan_fixture, template_fixture):
    response = client.get(f"/en/results/{template_fixture.id}/scan/{scan_fixture.id}")
    assert response.status_code == 401


def test_landing_page_error_logged_in_not_my_template(
    scan_fixture, template_fixture, logged_in_client
):
    response = logged_in_client.get(
        f"/en/results/{template_fixture.id}/scan/{scan_fixture.id}"
    )
    assert response.status_code == 401


def test_security_report_findings(
    home_org_owasp_scan_fixture, home_org_owasp_zap_template_fixture, logged_in_client
):
    response = logged_in_client.get(
        f"/en/results/{home_org_owasp_zap_template_fixture.id}/scan/{home_org_owasp_scan_fixture.id}"
    )
    assert response.status_code == 200
    assert response.template.name == "scan_results_security.html"


# TODO: Figure out why error mocks don't work with logged_in_client
# @patch("api_gateway.routers.ops.get_db_version")
# def test_security_report_findings_unknown_error(mock_get_db_version, home_org_owasp_scan_fixture, home_org_owasp_zap_template_fixture, logged_in_client):
#     mock_get_db_version.side_effect = SQLAlchemyError()
#     response = logged_in_client.get(f"/en/results/{home_org_owasp_zap_template_fixture.id}/scan/{home_org_owasp_scan_fixture.id}")
#     assert response.status_code == 500


def test_security_report_violations_not_authorized(
    home_org_owasp_scan_fixture,
    home_org_owasp_zap_template_fixture,
    owasp_security_report_fixture,
):
    response = client.get(
        f"/en/results/{home_org_owasp_zap_template_fixture.id}/security/{home_org_owasp_scan_fixture.id}/{owasp_security_report_fixture.id}"
    )
    assert response.status_code == 401


def test_security_report_violations(
    home_org_owasp_scan_fixture,
    home_org_owasp_zap_template_fixture,
    owasp_security_report_fixture,
    logged_in_client,
):
    response = logged_in_client.get(
        f"/en/results/{home_org_owasp_zap_template_fixture.id}/security/{home_org_owasp_scan_fixture.id}/{owasp_security_report_fixture.id}"
    )
    assert response.status_code == 200
    assert response.template.name == "scan_results_security_details.html"
