import json

from fastapi import APIRouter, Body

from storage import storage

router = APIRouter()


@router.post("/handle_s3_event")
def handle(Records: str = Body(...)):
    record = json.loads(Records)
    original_event = json.loads(record["Message"])
    for record in original_event["Records"]:
        storage.retrieve_and_route(record)
    return {}
