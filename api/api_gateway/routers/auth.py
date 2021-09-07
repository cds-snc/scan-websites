from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Depends, Request, HTTPException
from os import environ
from starlette.requests import Request
from starlette.config import Config
from starlette import status
from sqlalchemy.orm import Session

from models.User import User, AuthenticatedUser
from database.db import get_session

router = APIRouter()

config_data = {'GOOGLE_CLIENT_ID': environ.get("GOOGLE_CLIENT_ID"),
 'GOOGLE_CLIENT_SECRET': environ.get("GOOGLE_CLIENT_SECRET")
 }
config = Config(environ=config_data)
oauth = OAuth(config)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email'
    }
)

def is_authenticated(request: Request):
    if not request.user.is_authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@router.get('/login/google')
async def login_google(request: Request):
    redirect_uri = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth/google', include_in_schema=False)
async def auth_google(request: Request, session: Session = Depends(get_session),):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')
    user = await oauth.google.parse_id_token(request, token)
    email = user['email']

    db_user = session.query(User).filter(User.email_address == email).scalar()
    if db_user is None:
        db_user = User(email_address=email)
        session.add(db_user)

    authenticated_user = AuthenticatedUser(**db_user.__dict__).dict()
    session.commit()
    request.session["user"] = authenticated_user

    return RedirectResponse(url='/en/dashboard')


@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@router.get(
    "/me",
    dependencies=[Depends(is_authenticated)],
    response_model=AuthenticatedUser,
)
async def get_current_user(request: Request):
    return request.user