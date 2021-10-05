from fastapi.testclient import TestClient
from unittest.mock import ANY, MagicMock, patch

from api_gateway import api
from pub_sub import pub_sub

import os

client = TestClient(api.app)


def test_create_template_valid(logged_in_client):
    response = logged_in_client.post("/scans/template", data={"name": "foo"})
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_create_template_scan_valid(
    home_org_template_fixture_2, scan_type_fixture, logged_in_client
):
    response = logged_in_client.post(
        f"/scans/template/{str(home_org_template_fixture_2.id)}/scan",
        json={
            "data": [{"url": "https://www.example.com"}],
            "scan_types": [{"scanType": scan_type_fixture.name}],
        },
    )
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_create_template_scan_when_already_exist(
    home_org_template_fixture,
    home_org_template_scan_fixture,
    scan_type_fixture,
    logged_in_client,
):
    response = logged_in_client.post(
        f"/scans/template/{str(home_org_template_fixture.id)}/scan",
        json={
            "data": [{"url": "https://www.example.com"}],
            "scan_types": [{"scanType": scan_type_fixture.name}],
        },
    )
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_create_template_scan_not_my_org(
    template_fixture, scan_type_fixture, logged_in_client
):
    response = logged_in_client.post(
        f"/scans/template/{str(template_fixture.id)}/scan",
        json={
            "data": [{"url": "https://www.example.com"}],
            "scan_types": [{"scanType": scan_type_fixture.name}],
        },
    )
    assert response.status_code == 401


def test_create_template_scan_unknown_scan_type(
    home_org_template_fixture, logged_in_client
):
    response = logged_in_client.post(
        f"/scans/template/{str(home_org_template_fixture.id)}/scan",
        json={
            "data": [{"url": "https://www.example.com"}],
            "scan_types": [{"scanType": "foo"}],
        },
    )
    assert response.json() == {
        "error": "error creating template: No row was found when one was required"
    }
    assert response.status_code == 500


def test_create_template_scan_invalid_url(
    home_org_template_fixture, scan_type_fixture, logged_in_client
):
    response = logged_in_client.post(
        f"/scans/template/{str(home_org_template_fixture.id)}/scan",
        json={
            "data": [{"url": "ftp://www.example.com"}],
            "scan_types": [{"scanType": scan_type_fixture.name}],
        },
    )

    assert "URL scheme not permitted" in str(response.text)
    assert response.status_code == 422


def test_create_template_scan_url_missing(home_org_template_fixture, logged_in_client):
    response = logged_in_client.post(
        f"/scans/template/{str(home_org_template_fixture.id)}/scan",
        json={"data": [{"foo": "bar"}], "scan_types": [{"scanType": "axe-core"}]},
    )

    assert "value_error.missing" in str(response.text)
    assert response.status_code == 422


def test_update_template_scan_valid(
    home_org_template_fixture,
    home_org_template_scan_fixture,
    scan_type_fixture,
    logged_in_client,
):
    response = logged_in_client.put(
        f"/scans/template/{str(home_org_template_fixture.id)}/scan",
        json={
            "data": [{"url": "https://other.example.com"}],
            "scan_types": [{"scanType": scan_type_fixture.name}],
        },
    )
    assert response.json() == {"id": ANY}
    assert response.status_code == 200


def test_update_template_scan_not_my_template(
    template_fixture,
    home_org_template_scan_fixture,
    scan_type_fixture,
    logged_in_client,
):
    response = logged_in_client.put(
        f"/scans/template/{str(template_fixture.id)}/scan",
        json={
            "data": [{"url": "https://other.example.com"}],
            "scan_types": [{"scanType": scan_type_fixture.name}],
        },
    )
    assert response.status_code == 401


def test_update_template_scan_invalid_template(
    template_fixture,
    home_org_template_scan_fixture,
    scan_type_fixture,
    logged_in_client,
):
    response = logged_in_client.put(
        "/scans/template/cheese/scan",
        json={
            "data": [{"url": "https://other.example.com"}],
            "scan_types": [{"scanType": scan_type_fixture.name}],
        },
    )
    assert response.status_code == 401


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_valid_api_keys(
    mock_aws_session,
    mock_db_session,
    loggedin_user_fixture,
    owasp_zap_fixture,
    home_org_owasp_zap_template_fixture,
    home_org_owasp_zap_template_scan_fixture,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": str(loggedin_user_fixture.access_token),
            "X-TEMPLATE-TOKEN": str(home_org_owasp_zap_template_fixture.token),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Scan started: {home_org_owasp_zap_template_fixture.name}"
    }


@patch("pub_sub.pub_sub.send")
@patch("database.db.get_session")
@patch.dict(os.environ, {"OWASP_ZAP_URLS_TOPIC": "topic"}, clear=True)
def test_start_scan_valid_api_keys_with_gitsha(
    mock_db_session,
    mock_send,
    loggedin_user_fixture,
    owasp_zap_fixture,
    home_org_owasp_zap_template_fixture,
    home_org_owasp_zap_template_scan_fixture,
):
    response = client.get(
        "scans/start/revision/123456789",
        headers={
            "X-API-KEY": str(loggedin_user_fixture.access_token),
            "X-TEMPLATE-TOKEN": str(home_org_owasp_zap_template_fixture.token),
        },
    )

    assert response.status_code == 200

    mock_send.assert_called_once_with(
        "topic",
        {
            "type": pub_sub.AvailableScans.OWASP_ZAP.value,
            "product": home_org_owasp_zap_template_fixture.name,
            "revision": "123456789",
            "template_id": str(home_org_owasp_zap_template_fixture.id),
            "scan_id": ANY,
            "url": "https://www.alpha.canada.ca",
            "event": "sns",
            "queue": "topic",
            "id": ANY,
        },
    )


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_valid_keys_wrong_org(
    mock_aws_session,
    mock_db_session,
    loggedin_user_fixture,
    home_org_template_fixture,
    template_fixture,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": str(loggedin_user_fixture.access_token),
            "X-TEMPLATE-TOKEN": str(template_fixture.token),
        },
    )

    assert response.status_code == 401


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_no_api_keys(
    mock_aws_session,
    mock_db_session,
    loggedin_user_fixture,
    home_org_template_fixture,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    response = client.get("scans/start")
    assert response.status_code == 401


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_invalid_user_api_key(
    mock_aws_session,
    mock_db_session,
    loggedin_user_fixture,
    home_org_template_fixture,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": "foo",
            "X-TEMPLATE-TOKEN": str(home_org_template_fixture.token),
        },
    )
    assert response.status_code == 401


@patch("database.db.get_session")
@patch("pub_sub.pub_sub.get_session")
def test_start_scan_invalid_template_token(
    mock_aws_session,
    mock_db_session,
    loggedin_user_fixture,
    home_org_template_fixture,
):
    mock_client = MagicMock()
    mock_aws_session.return_value.client.return_value = mock_client

    response = client.get(
        "scans/start",
        headers={
            "X-API-KEY": str(loggedin_user_fixture.access_token),
            "X-TEMPLATE-TOKEN": "bar",
        },
    )
    assert response.status_code == 401
