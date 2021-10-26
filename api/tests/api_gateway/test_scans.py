from fastapi.testclient import TestClient
from unittest.mock import ANY, MagicMock, patch

from api_gateway import api
from factories import (
    OrganisationFactory,
    ScanFactory,
    ScanTypeFactory,
    SecurityReportFactory,
    SecurityViolationFactory,
    TemplateFactory,
    TemplateScanFactory,
)

from models.Scan import Scan
from models.SecurityReport import SecurityReport
from models.SecurityViolation import SecurityViolation
from pub_sub.pub_sub import AvailableScans


import os
import uuid

client = TestClient(api.app)


def test_create_template_valid(authorized_request):
    logged_in_client, _, _ = authorized_request
    response = logged_in_client.post("/scans/template", json={"name": "foo"})
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_create_template_scan_valid(session, authorized_request):
    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory()
    session.commit()

    response = logged_in_client.post(
        f"/scans/template/{str(template.id)}/scan",
        json={
            "data": {"url": "https://www.example.com"},
            "scan_types": [{"scanType": scan_type.name}],
        },
    )
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_create_template_scan_when_already_exist(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory()

    TemplateScanFactory(template=template, scan_type=scan_type)
    session.commit()

    response = logged_in_client.post(
        f"/scans/template/{str(template.id)}/scan",
        json={
            "data": {"url": "https://www.example.com"},
            "scan_types": [{"scanType": scan_type.name}],
        },
    )
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_create_template_scan_not_my_org(
    session,
    authorized_request,
):
    logged_in_client, _, _ = authorized_request

    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory()
    session.commit()

    response = logged_in_client.post(
        f"/scans/template/{str(template.id)}/scan",
        json={
            "data": {"url": "https://www.example.com"},
            "scan_types": [{"scanType": scan_type.name}],
        },
    )
    assert response.status_code == 401


def test_create_template_scan_unknown_scan_type(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    session.commit()

    response = logged_in_client.post(
        f"/scans/template/{str(template.id)}/scan",
        json={
            "data": {"url": "https://www.example.com"},
            "scan_types": [{"scanType": "foo"}],
        },
    )
    assert response.json() == {
        "error": "error creating template: No row was found when one was required"
    }
    assert response.status_code == 500


def test_create_template_scan_invalid_url(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory()
    session.commit()

    response = logged_in_client.post(
        f"/scans/template/{str(template.id)}/scan",
        json={
            "data": {"url": "ftp://www.example.com"},
            "scan_types": [{"scanType": scan_type.name}],
        },
    )

    assert "URL scheme not permitted" in str(response.text)
    assert response.status_code == 422


def test_create_template_scan_url_missing(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    session.commit()

    response = logged_in_client.post(
        f"/scans/template/{str(template.id)}/scan",
        json={"data": {"foo": "bar"}, "scan_types": [{"scanType": "axe-core"}]},
    )

    assert "value_error.missing" in str(response.text)
    assert response.status_code == 422


def test_update_template_scan_valid(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory()
    template_scan = TemplateScanFactory(template=template, scan_type=scan_type)
    session.commit()

    response = logged_in_client.put(
        f"/scans/template/{str(template.id)}/scan/{str(template_scan.id)}",
        json={
            "data": {"url": "https://other.example.com"},
            "scan_types": [{"scanType": scan_type.name}],
        },
    )
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_update_template_scan_not_my_template(
    session,
    authorized_request,
):
    logged_in_client, _, _ = authorized_request

    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory()
    template_scan = TemplateScanFactory(template=template, scan_type=scan_type)
    session.commit()

    response = logged_in_client.put(
        f"/scans/template/{str(template.id)}/scan/{str(template_scan.id)}",
        json={
            "data": {"url": "https://other.example.com"},
            "scan_types": [{"scanType": scan_type.name}],
        },
    )
    assert response.status_code == 401


def test_update_template_scan_invalid_template(
    session,
    authorized_request,
):
    logged_in_client, _, _ = authorized_request

    scan_type = ScanTypeFactory()
    session.commit()

    response = logged_in_client.put(
        "/scans/template/foo/scan/bar",
        json={
            "data": {"url": "https://other.example.com"},
            "scan_types": [{"scanType": scan_type.name}],
        },
    )
    assert response.status_code == 401


@patch("pub_sub.pub_sub.get_session")
def test_start_scan_valid_api_keys(
    mock_aws_session,
    session,
    authorized_request,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    _, user, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    template_scan = TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": str(user.access_token),
            "X-TEMPLATE-TOKEN": str(template.token),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Scan start details: {template.name}, successful: ['{template_scan.scan_type.name}'], failed: []"
    }


@patch("pub_sub.pub_sub.dispatch")
def test_start_scan_valid_api_keys_with_unknown_error(
    mock_dispatch,
    session,
    authorized_request,
):
    mock_dispatch.side_effect = Exception()

    _, user, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    template_scan = TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": str(user.access_token),
            "X-TEMPLATE-TOKEN": str(template.token),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Scan start details: {template.name}, successful: [], failed: ['{template_scan.scan_type.name}']"
    }


@patch("pub_sub.pub_sub.send")
@patch("database.db.get_session")
@patch.dict(os.environ, {"OWASP_ZAP_URLS_TOPIC": "topic"}, clear=True)
def test_start_scan_valid_api_keys_with_gitsha(
    mock_aws_session,
    mock_send,
    session,
    authorized_request,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    _, user, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    template_scan = TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = client.get(
        "scans/start/revision/123456789",
        headers={
            "X-API-KEY": str(user.access_token),
            "X-TEMPLATE-TOKEN": str(template.token),
        },
    )

    assert response.status_code == 200

    mock_send.assert_called_once_with(
        "topic",
        {
            "type": AvailableScans.OWASP_ZAP.value,
            "product": template.name,
            "revision": "123456789",
            "template_id": str(template.id),
            "scan_id": ANY,
            "url": template_scan.data["url"],
            "crawl": False,
            "event": "sns",
            "queue": "topic",
            "id": ANY,
        },
    )


@patch("fastapi.BackgroundTasks.add_task")
@patch.dict(os.environ, {"OWASP_ZAP_URLS_TOPIC": "topic"}, clear=True)
def test_start_scan_valid_api_keys_with_crawling(
    mock_add_task,
    session,
    authorized_request,
):
    _, user, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    template_scan = TemplateScanFactory(
        template=template,
        scan_type=scan_type,
        data={"url": "http://www.example.com", "crawl": "true"},
    )
    session.commit()

    response = client.get(
        "scans/start/revision/123456789",
        headers={
            "X-API-KEY": str(user.access_token),
            "X-TEMPLATE-TOKEN": str(template.token),
        },
    )

    assert response.status_code == 200

    mock_add_task.assert_called_once_with(
        ANY,
        {
            "type": AvailableScans.OWASP_ZAP.value,
            "product": template.name,
            "revision": "123456789",
            "template_id": str(template.id),
            "scan_id": ANY,
            "url": template_scan.data["url"],
            "crawl": "true",
            "event": "sns",
            "queue": "topic",
        },
    )


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_valid_keys_wrong_org(
    mock_aws_session,
    session,
    authorized_request,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    _, user, _ = authorized_request

    organisation = OrganisationFactory()
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": str(user.access_token),
            "X-TEMPLATE-TOKEN": str(template.token),
        },
    )

    assert response.status_code == 401


@patch("database.db.get_session")
def test_start_scan_no_api_keys(
    mock_aws_session,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    response = client.get("scans/start")
    assert response.status_code == 401


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_invalid_user_api_key(
    mock_aws_session,
    session,
    authorized_request,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    _, _, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": "foo",
            "X-TEMPLATE-TOKEN": str(template.token),
        },
    )
    assert response.status_code == 401


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_invalid_template_token(
    mock_aws_session,
    session,
    authorized_request,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    _, user, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": str(user.access_token),
            "X-TEMPLATE-TOKEN": "bar",
        },
    )
    assert response.status_code == 401


def test_delete_security_report_with_bad_id(
    session,
    authorized_request,
):

    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    template_scan = TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = logged_in_client.delete(
        f"/scans/template/{str(template.id)}/scan/{str(template_scan.id)}/security/foo"
    )

    assert response.json() == {"error": "error deleting report"}
    assert response.status_code == 500


def test_delete_security_report_with_id_not_found(
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

    response = logged_in_client.delete(
        f"/scans/template/{str(template.id)}/scan/{str(scan.id)}/security/{str(uuid.uuid4())}"
    )

    assert response.json() == {"error": "error deleting report"}
    assert response.status_code == 500


def test_delete_security_report_with_correct_id(
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

    deleted_security_report = security_report.id
    deleted_security_violation = security_violation.id
    response = logged_in_client.delete(
        f"/scans/template/{str(template.id)}/scan/{str(scan.id)}/security/{str(security_report.id)}"
    )

    security_report = (
        session.query(SecurityReport)
        .filter(SecurityReport.id == deleted_security_report)
        .one_or_none()
    )
    security_violations = (
        session.query(SecurityViolation)
        .filter(SecurityViolation.id == deleted_security_violation)
        .all()
    )

    assert response.json() == {"status": "OK"}
    assert response.status_code == 200
    assert security_report is None
    assert len(security_violations) == 0


def test_delete_template_scan_with_bad_id(session, authorized_request):
    logged_in_client, _, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    session.commit()

    response = logged_in_client.delete(f"/scans/template/{str(template.id)}/scan/foo")
    assert response.json() == {"error": "error deleting template"}
    assert response.status_code == 500


def test_delete_template_scan_with_id_not_found(session, authorized_request):
    client, _, organisation = authorized_request

    template = TemplateFactory(organisation=organisation)
    session.commit()

    response = client.delete(
        f"/scans/template/{str(template.id)}/scan/{str(uuid.uuid4())}"
    )
    assert response.json() == {"error": "error deleting template"}
    assert response.status_code == 500


def test_delete_template_scan_with_correct_id(
    session,
    authorized_request,
):
    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    template_scan = TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    session.commit()

    response = logged_in_client.delete(
        f"/scans/template/{str(template.id)}/scan/{str(template_scan.id)}"
    )

    assert response.json() == {"status": "OK"}
    assert response.status_code == 200


def test_delete_template_scan_with_correct_id_has_reports(
    session,
    authorized_request,
):

    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    template_scan = TemplateScanFactory(
        template=template, scan_type=scan_type, data={"url": "http://www.example.com"}
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    security_report = SecurityReportFactory(scan=scan)
    security_violation = SecurityViolationFactory(security_report=security_report)
    session.commit()

    deleted_scan_id = scan.id
    deleted_security_report = security_report.id
    deleted_security_violation = security_violation.id

    response = logged_in_client.delete(
        f"/scans/template/{str(template.id)}/scan/{str(template_scan.id)}"
    )

    scan = session.query(Scan).filter(Scan.id == deleted_scan_id).one_or_none()
    security_report = (
        session.query(SecurityReport)
        .filter(SecurityReport.id == deleted_security_report)
        .one_or_none()
    )
    security_violations = (
        session.query(SecurityViolation)
        .filter(SecurityViolation.id == deleted_security_violation)
        .all()
    )

    assert response.json() == {"status": "OK"}
    assert response.status_code == 200
    assert scan is None
    assert security_report is None
    assert len(security_violations) == 0


def test_ignore_security_violation(
    session,
    authorized_request,
):

    logged_in_client, _, organisation = authorized_request
    template = TemplateFactory(organisation=organisation)
    scan_type = ScanTypeFactory(
        name=AvailableScans.OWASP_ZAP.value,
        callback={"event": "sns", "topic_env": "OWASP_ZAP_URLS_TOPIC"},
    )
    scan = ScanFactory(
        organisation=organisation, template=template, scan_type=scan_type
    )
    security_report = SecurityReportFactory(scan=scan)

    violation_data = [
        {
            "uri": "https://example.com/fr/id/19",
            "method": "GET",
            "param": "",
            "attack": "",
            "evidence": '<form id="form" data-testid="form" method="POST" encType="multipart/form-data" novalidate="">',
        },
        {
            "uri": "https://example.com/fr/id/21",
            "method": "GET",
            "param": "",
            "attack": "",
            "evidence": '<form id="form" data-testid="form" method="POST" encType="multipart/form-data" novalidate="">',
        },
    ]
    security_violation = SecurityViolationFactory(
        security_report=security_report, data=violation_data
    )
    session.commit()

    response = logged_in_client.post(
        f"/scans/template/{str(template.id)}/scan/{str(scan.id)}/type/{str(scan_type.id)}",
        json={
            "violation": security_violation.violation,
            "location": "evidence",
            "condition": '<form id="form" data-testid="form" method="POST" encType="multipart/form-data" novalidate="">',
        },
    )

    assert response.json() == {"id": ANY}
    assert response.status_code == 200
