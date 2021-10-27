from fastapi.testclient import TestClient
from api_gateway import api
from factories import (
    OrganisationFactory,
    ScanFactory,
    ScanIgnoreFactory,
    ScanTypeFactory,
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


def test_loading_scan_ignore_not_logged_in(session):
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

    response = client.get(f"/en/ignored/{template.id}/scan/{scan.id}")
    assert response.status_code == 401


def test_loading_scan_ignore_logged_in(session, authorized_request):
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
    ScanIgnoreFactory(
        scan=scan,
        violation="violation",
        location="evidence",
        condition="condition",
    )
    session.commit()

    response = logged_in_client.get(f"/en/ignored/{template.id}/scan/{scan.id}")
    assert response.status_code == 200
    assert response.template.name == "scan_ignore_list.html"
