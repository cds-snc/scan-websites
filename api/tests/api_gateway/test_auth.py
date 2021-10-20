from fastapi.testclient import TestClient
from unittest.mock import patch

from api_gateway import api
from models.User import User

import os

client = TestClient(api.app)


def test_heroku_login_401_if_HEROKU_PR_NUMBER_ENV_missing():
    response = client.get("/login/heroku")
    assert response.status_code == 401


@patch.dict(os.environ, {"HEROKU_PR_NUMBER": "foo"}, clear=True)
def test_heroku_login_401_if_user_missing():
    response = client.get("/login/heroku")
    assert response.status_code == 401


@patch.dict(os.environ, {"HEROKU_PR_NUMBER": "foo"}, clear=True)
def test_heroku_login_redirect_if_seed_user_exists(session, home_organisation_fixture):
    user = User(
        name="Seed User",
        email_address="scan-websites+seed@cds-sns.ca",
        organisation=home_organisation_fixture,
    )
    session.add(user)
    session.commit()
    response = client.get("/login/heroku", allow_redirects=False)
    assert response.status_code == 307
