from os import environ
from fastapi import Depends, FastAPI, HTTPException
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware

from front_end import view
from .routers import auth, ops, organisations, scans

app = FastAPI()

FASTAPI_SECRET_KEY = environ.get("FASTAPI_SECRET_KEY") or None
if FASTAPI_SECRET_KEY is None:
    raise HTTPException(status_code=500, detail="Missing FASTAPI_SECRET_KEY")

app.add_middleware(AuthenticationMiddleware, backend=auth.SessionAuthBackend())
app.add_middleware(SessionMiddleware, secret_key=FASTAPI_SECRET_KEY)

app.include_router(auth.router)
app.include_router(ops.router, prefix="/ops", tags=["ops"])
app.include_router(
    organisations.router,
    prefix="/organisations",
    tags=["organisations"],
    dependencies=[Depends(auth.is_authenticated)],
)
app.include_router(scans.router, prefix="/scans", tags=["scans"])
app.include_router(view.router)
