from os import environ
from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware


from front_end import view, scan_view
from .routers import auth, dev, ops, organisations, scans
from .custom_middleware import add_security_headers

app = FastAPI()

FASTAPI_SECRET_KEY = environ.get("FASTAPI_SECRET_KEY") or None
if FASTAPI_SECRET_KEY is None:
    raise HTTPException(status_code=500, detail="Missing FASTAPI_SECRET_KEY")

# https://github.com/tiangolo/fastapi/issues/1472; can't include custom middlware when running tests
if environ.get("CI") is None:
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_security_headers)


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
app.include_router(scan_view.router)

if environ.get("AWS_LOCALSTACK", False):
    app.include_router(dev.router, prefix="/dev", tags=["dev"])

app.mount("/static", StaticFiles(directory="front_end/static"), name="static")
FastAPIInstrumentor.instrument_app(app)
