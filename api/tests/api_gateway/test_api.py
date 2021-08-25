import os

from fastapi.testclient import TestClient
from unittest.mock import patch

from api_gateway.v1 import api
from sqlalchemy.exc import SQLAlchemyError

client = TestClient(api.app)


def test_version_with_no_GIT_SHA():
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {"version": "unknown"}


@patch.dict(os.environ, {"GIT_SHA": "foo"}, clear=True)
def test_version_with_GIT_SHA():
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {"version": "foo"}


@patch("api_gateway.v1.api.get_db_version")
def test_healthcheck_success(mock_get_db_version):
    mock_get_db_version.return_value = "foo"
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    expected_val = {"database": {"able_to_connect": True, "db_version": "foo"}}
    assert response.json() == expected_val


@patch("api_gateway.v1.api.get_db_version")
@patch("api_gateway.v1.api.log")
def test_healthcheck_failure(mock_log, mock_get_db_version):
    mock_get_db_version.side_effect = SQLAlchemyError()
    response = client.get("/api/v1/healthcheck")
    assert response.status_code == 200
    expected_val = {"database": {"able_to_connect": False}}
    assert response.json() == expected_val
    # assert mock_log.error.assert_called_once_with(SQLAlchemyError())


# @patch("api_gateway.api.crawl")
# @patch("api_gateway.api.log")
# @patch("api_gateway.api.uuid")
# def test_crawl(mock_uuid, mock_log, mock_crawl):
#    fake_url = "bar"
#    fake_uuid = "foo"
#    mock_log.return_value = None
#    mock_uuid.uuid4.return_value = fake_uuid
#
#    response = client.post(url="/crawl", json={"url": fake_url})
#
#    assert response.status_code == 200
#    mock_crawl.assert_called_once_with(fake_uuid, fake_url)
#    mock_log.info.assert_called_once_with("Crawling url='bar'")
