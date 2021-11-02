import os
import re

from fastapi.testclient import TestClient
from unittest.mock import patch

from api_gateway import api
from sqlalchemy.exc import SQLAlchemyError

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


def test_hsts_in_response(hsts_middleware_client):
    response = hsts_middleware_client.get("/ops/version")
    assert response.status_code == 200
    assert (
        response.headers["Strict-Transport-Security"]
        == "max-age=63072000; includeSubDomains; preload"
    )


def test_accessing_protected_route_not_logged_in():
    response = client.get("/me")
    assert response.status_code == 401


def test_accessing_protected_route_logged_in(
    authorized_request,
):
    logged_in_client, _, _ = authorized_request
    response = logged_in_client.get("/me")
    assert response.status_code == 200


def test_logout(
    authorized_request,
):
    logged_in_client, _, _ = authorized_request
    response = logged_in_client.get("/logout", allow_redirects=False)
    assert "session=null" in response.headers["set-cookie"]
    assert response.is_redirect
