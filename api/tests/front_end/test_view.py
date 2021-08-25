from fastapi.testclient import TestClient

from front_end import view

client = TestClient(view.app)

def test_langing_page_redirect_to_en():
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == '/en'