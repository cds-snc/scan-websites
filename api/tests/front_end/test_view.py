from fastapi.testclient import TestClient

# from unittest.mock import patch

from front_end import view

client = TestClient(view.app)


def test_langing_page_redirect_to_en():
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/en"


# @patch("schemas.Organization.OrganizationCreate")
# def test_create_organization(mock_organization):
#     mock_organization.name = "foobar"
#     response = client.post(
#         "/organization", json={"name": mock_organization.name}, allow_redirects=False
#     )
#     print(response)
#     assert response.status_code == 307

#     assert response.headers["location"] == "/dashboard"
