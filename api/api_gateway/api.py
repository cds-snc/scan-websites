from os import environ
from fastapi import Depends, FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.sessions import SessionMiddleware


from front_end import view, scan_view
from .routers import auth, dev, ops, organisations, scans
from .middleware.security_headers import SecurityHeadersMiddleware

import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

FASTAPI_SECRET_KEY = environ.get("FASTAPI_SECRET_KEY") or None
if FASTAPI_SECRET_KEY is None:
    raise HTTPException(status_code=500, detail="Missing FASTAPI_SECRET_KEY")

app.add_middleware(SecurityHeadersMiddleware)
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

# Log more details when invalid requests received
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    logging.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
