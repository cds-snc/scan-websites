import boto3
from logger import log


def get_object(record):
    client = boto3.resource("s3")
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
