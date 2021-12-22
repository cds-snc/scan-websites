import os

from fastapi.testclient import TestClient
from unittest.mock import patch

from api_gateway import api


client = TestClient(api.app)


def test_landing_page_redirect_to_en():
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/en"


def test_landing_page_displays_templates_not_logged_in():
    response = client.get("/en")
    assert response.status_code == 200
    assert response.template.name == "index.html"


def test_landing_page_displays_templates_logged_in(authorized_request):
    logged_in_client, _, _ = authorized_request
    response = logged_in_client.get("/en")
    assert response.status_code == 200
    assert response.template.name == "index.html"


def test_language_change():
    response = client.get(
        "/lang/en",
        headers={"referer": "http://localhost:8000/fr/foo"},
        allow_redirects=False,
    )
    assert response.status_code == 307
    assert response.headers["location"] == "/en/foo"


def test_language_change_base():
    response = client.get(
        "/lang/en",
        headers={"referer": "http://localhost:8000/fr"},
        allow_redirects=False,
    )
    assert response.status_code == 307
    assert response.headers["location"] == "/en"


@patch.dict(os.environ, {"DOMAIN_NAME": "foo.com"}, clear=True)
def test_language_change_same_domain():
    response = client.get(
        "/lang/en",
        headers={"referer": "http://foo.com/fr/bar/baz"},
        allow_redirects=False,
    )
    assert response.status_code == 307
    assert response.headers["location"] == "/en/bar/baz"


@patch.dict(os.environ, {"DOMAIN_NAME": "foo.com"}, clear=True)
def test_language_change_different_domain():
    response = client.get(
        "/lang/en", headers={"referer": "http://bar.com/fr/bar"}, allow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"] == "/en"


@patch.dict(os.environ, {"DOMAIN_NAME": "foo.com"}, clear=True)
def test_language_change_invalid_domain():
    response = client.get(
        "/lang/en", headers={"referer": "ftp://127.0.0.1"}, allow_redirects=False
    )
    assert response.status_code == 307
    assert response.headers["location"] == "/en"
