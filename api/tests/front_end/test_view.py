from fastapi.testclient import TestClient

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
