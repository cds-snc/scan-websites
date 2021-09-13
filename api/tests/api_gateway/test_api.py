import os

from fastapi.testclient import TestClient
from unittest.mock import patch

from api_gateway import api
from sqlalchemy.exc import SQLAlchemyError
from authlib.oidc.core import UserInfo

client = TestClient(api.app)


def test_version_with_no_GIT_SHA():
    response = client.get("/ops/version")
    assert response.status_code == 200
    assert response.json() == {"version": "unknown"}


@patch.dict(os.environ, {"GIT_SHA": "foo"}, clear=True)
def test_version_with_GIT_SHA():
    response = client.get("/ops/version")
    assert response.status_code == 200
    assert response.json() == {"version": "foo"}


@patch("api_gateway.routers.ops.get_db_version")
def test_healthcheck_success(mock_get_db_version):
    mock_get_db_version.return_value = "foo"
    response = client.get("/ops/healthcheck")
    assert response.status_code == 200
    expected_val = {"database": {"able_to_connect": True, "db_version": "foo"}}
    assert response.json() == expected_val


@patch("api_gateway.routers.ops.get_db_version")
@patch("api_gateway.routers.ops.log")
def test_healthcheck_failure(mock_log, mock_get_db_version):
    mock_get_db_version.side_effect = SQLAlchemyError()
    response = client.get("/ops/healthcheck")
    assert response.status_code == 200
    expected_val = {"database": {"able_to_connect": False}}
    assert response.json() == expected_val
    # assert mock_log.error.assert_called_once_with(SQLAlchemyError())


@patch("api_gateway.routers.scans.crawl")
@patch("api_gateway.routers.scans.log")
@patch("api_gateway.routers.scans.uuid")
def test_crawl(mock_uuid, mock_log, mock_crawl):
    fake_url = "bar"
    fake_uuid = "foo"
    mock_log.return_value = None
    mock_uuid.uuid4.return_value = fake_uuid

    response = client.post(url="/scans/crawl", json={"url": fake_url})

    assert response.status_code == 200
    mock_crawl.assert_called_once_with(fake_uuid, fake_url)
    mock_log.info.assert_called_once_with("Crawling url='bar'")


@patch("api_gateway.routers.scans.crawl")
@patch("api_gateway.routers.scans.log")
@patch("api_gateway.routers.scans.uuid")
def test_crawl_ratelimit(mock_uuid, mock_log, mock_crawl):
    fake_url = "bar"
    fake_uuid = "foo"
    mock_log.return_value = None
    mock_uuid.uuid4.return_value = fake_uuid

    for i in range(0, 10):
        response = client.post(url="/scans/crawl", json={"url": fake_url})
        if i < 4:
            assert response.status_code == 200
        else:
            assert response.status_code == 429


def test_accessing_protected_route_not_logged_in():
    fresh_client = TestClient(api.app)
    response = fresh_client.get("/me")
    assert response.status_code == 401


@patch("api_gateway.routers.auth.oauth.google.authorize_access_token")
@patch("api_gateway.routers.auth.oauth.google.parse_id_token")
@patch("database.db.get_session")
def test_google_oauth_callback(
    mock_get_session,
    mock_parse_id_token,
    mock_authorize_access_token,
    regular_user_fixture,
):
    fresh_client = TestClient(api.app)
    mock_authorize_access_token.return_value = {"access_token": "TOKEN"}
    mock_parse_id_token.return_value = UserInfo(regular_user_fixture)
    response = fresh_client.get("/auth/google")

    assert response.cookies["session"] is not None
    assert response.status_code == 200

    response = fresh_client.get("/me")
    assert response.status_code == 200


@patch("api_gateway.routers.auth.oauth.google.authorize_access_token")
@patch("api_gateway.routers.auth.oauth.google.parse_id_token")
@patch("database.db.get_session")
def test_accessing_protected_route_logged_in(
    mock_get_session,
    mock_parse_id_token,
    mock_authorize_access_token,
    regular_user_fixture,
):
    fresh_client = TestClient(api.app)
    mock_authorize_access_token.return_value = {"access_token": "TOKEN"}
    mock_parse_id_token.return_value = UserInfo(regular_user_fixture)
    response = fresh_client.get("/auth/google", cookies=None)

    response = fresh_client.get("/me")
    assert response.status_code == 200


@patch("api_gateway.routers.auth.oauth.google.authorize_access_token")
@patch("api_gateway.routers.auth.oauth.google.parse_id_token")
@patch("database.db.get_session")
def test_logout(
    mock_get_session,
    mock_parse_id_token,
    mock_authorize_access_token,
    regular_user_fixture,
):
    fresh_client = TestClient(api.app)
    mock_authorize_access_token.return_value = {"access_token": "TOKEN"}
    mock_parse_id_token.return_value = UserInfo(regular_user_fixture)
    response = fresh_client.get("/auth/google", cookies=None)

    response = fresh_client.get("/logout", allow_redirects=False)
    assert "session=null" in response.headers["set-cookie"]
    assert response.is_redirect
