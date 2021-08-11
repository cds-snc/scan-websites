import boto3
import json
import os
import uuid


from logger import log


def dispatch(payload):
    # Add some logic to figure out what queues to dispatch to
    # Currently only dispatches to axe-core
    AXE_CORE_URLS_TOPIC = os.environ.get("AXE_CORE_URLS_TOPIC", False)

    # Add a key that can be linked back to the ID of the payload
    payload["key"] = str(uuid.uuid4())

    send(AXE_CORE_URLS_TOPIC, payload)


def send(topic_arn, payload):
    if topic_arn:
        client = boto3.client("sns", region_name="ca-central-1")
        client.publish(
            TargetArn=topic_arn,
            Message=json.dumps({"default": json.dumps(payload)}),
            MessageStructure="json",
        )
    else:
        log.error("Topic ARN is not defined")
