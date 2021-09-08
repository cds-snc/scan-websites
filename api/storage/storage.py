import json

from database.db import db_session
from logger import log
from boto3wrapper.wrapper import get_session
from sqlalchemy.orm import joinedload

from models.Scan import Scan


def get_object(record):
    client = get_session().resource("s3")
    obj = client.Object(record.s3.bucket.name, record.s3.object.key)
    try:
        body = obj.get()["Body"].read()
        log.info(
            f"Downloaded {record.s3.object.key} from {record.s3.bucket.name} with length {len(body)}"
        )
        return body
    except Exception:
        log.error(
            f"Error downloading {record.s3.object.key} from {record.s3.bucket.name}"
        )
        return False


def store(record):
    session = db_session()
    body = get_object(record)
    if not body:
        return False

    try:
        payload = json.loads(body)
        scan = (
            session.query(Scan).options(joinedload(Scan.scan_type)).get(payload["id"])
        )
        if scan is None:
            log.error(f"Scan ID: {payload['id']} could not be found")
            return False

        if scan.scan_type.name == "axe_core":
            return store_axe_core_record(payload)
        else:
            log.error(f"Error storing {scan.id} with type {scan.scan_type.name}")
            return False

    except Exception:
        log.error(f"Error decoding {record.s3.object.key} from {record.s3.bucket.name}")
        return False


def store_axe_core_record(payload):
    return True
