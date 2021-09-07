from os import environ
from fastapi import FastAPI, HTTPException
from starlette.middleware.sessions import SessionMiddleware

from front_end import view
from .routers import auth, ops, organisations, scans

if "DEV_ENVIRONMENT" in environ:
    app = FastAPI()
else:
    # This is only needed until a dedicated domain name is live
    app = FastAPI(root_path="/v1")

FASTAPI_SECRET_KEY = environ.get('FASTAPI_SECRET_KEY') or None
if FASTAPI_SECRET_KEY is None:
    raise HTTPException(status_code=500, detail='Missing FASTAPI_SECRET_KEY')

app.add_middleware(SessionMiddleware, secret_key=FASTAPI_SECRET_KEY)

app.include_router(auth.router)
app.include_router(ops.router, prefix="/ops", tags=["ops"])
app.include_router(
    organisations.router,
    prefix="/organisations",
    tags=["organisations"],
)
app.include_router(scans.router, prefix="/scans", tags=["scans"])
app.include_router(view.router)
