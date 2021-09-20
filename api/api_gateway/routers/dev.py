import json

from fastapi import APIRouter, Body

from storage import storage

router = APIRouter()

# What is this? We are using localstack to emulate
# an AWS environment, however, we are not putting this API
# code into a Lambda in that environment. As a results we 
# can't connect the s3 upload event inside the dev environment
# to this code. Instead we are proxying the S3 event through a
# SNS topic that publishes to this endpoint. We then unpack the
# original event and pass it on to the same function that would
# through main.handler

@router.post("/handle_s3_event")
def handle(Records: str = Body(...)):
    record = json.loads(Records)
    original_event = json.loads(record["Message"])
    for record in original_event["Records"]:
        storage.retrieve_and_route(record)
    return {}
