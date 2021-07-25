from os import environ
from fastapi import FastAPI

app = FastAPI()


@app.get("/version")
async def version():
    return {"version": environ.get("GIT_SHA", "unknown")}
