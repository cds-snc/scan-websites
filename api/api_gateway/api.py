from os import environ
from fastapi import FastAPI

from front_end import view
from .routers import ops, organisations, scans

if "DEV_ENVIRONMENT" in environ:
    app = FastAPI()
else:
    # This is only needed until a dedicated domain name is live
    app = FastAPI(root_path="/v1")

app.include_router(ops.router, prefix="/ops", tags=["ops"])
app.include_router(
    organisations.router,
    prefix="/organisations",
    tags=["organisations"],
)
app.include_router(scans.router, prefix="/scans", tags=["scans"])
app.include_router(view.router)
