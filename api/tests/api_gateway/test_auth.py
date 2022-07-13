from authlib.oidc.core import UserInfo
from fastapi.testclient import TestClient
from unittest.mock import patch

from api_gateway import api
from factories import OrganisationFactory, UserFactory

import os

client = TestClient(api.app)


@patch("api_gateway.routers.auth.oauth.google.authorize_access_token")
@patch("api_gateway.routers.auth.oauth.google.parse_id_token")
@patch("database.db.get_session")
def test_google_oauth_callback(
    mock_get_session,
    mock_parse_id_token,
    mock_authorize_access_token,
):
    fresh_client = TestClient(api.app)
    mock_authorize_access_token.return_value = {"access_token": "TOKEN"}
    mock_parse_id_token.return_value = UserInfo(
        {
            "email": "user@cds-snc.ca",
            "name": "User McUser",
        }
    )
    response = fresh_client.get("/auth/google")

    assert response.cookies["session"] is not None
    assert response.status_code == 200

    response = fresh_client.get("/me")
    assert response.status_code == 200


def test_preview_login_401_if_PREVIEW_APP_ENV_missing():
    response = client.get("/login/preview")
    assert response.status_code == 401


@patch.dict(os.environ, {"PREVIEW_APP": "foo"}, clear=True)
def test_preview_login_401_if_user_missing():
    response = client.get("/login/preview")
    assert response.status_code == 401


@patch.dict(os.environ, {"PREVIEW_APP": "foo"}, clear=True)
def test_preview_login_redirect_if_seed_user_exists(session):
    organisation = OrganisationFactory()
    user = UserFactory(
        email_address="scan-websites+seed@cds-sns.ca", organisation=organisation
    )
    session.add(user)
    session.commit()
    response = client.get("/login/preview", allow_redirects=False)
    assert response.status_code == 307
