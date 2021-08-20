from boto3 import Session
import os


def get_session():

    options = {"region_name": "ca_central_1"}

    use_localstack = os.environ.get("AWS_LOCALSTACK", False)
    if use_localstack:
        options["aws_access_key_id"] = "foo"
        options["aws_secret_access_key"] = "bar"
        options["endpoint_url"] = "http://localstack:4566"

    return Session(**options)
