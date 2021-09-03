import json
import os
import uuid
from boto3wrapper.wrapper import get_session


from logger import log


def dispatch(payload):
    # Add some logic to figure out what queues to dispatch to
    # Currently only dispatches to axe-core
    AXE_CORE_URLS_TOPIC = os.environ.get("AXE_CORE_URLS_TOPIC", False)

    # Add a ID that can be linked back to the parent ID of the payload
    payload["id"] = str(uuid.uuid4())

    send(AXE_CORE_URLS_TOPIC, payload)


def send(topic_arn, payload):
    if topic_arn:
        use_localstack = os.environ.get("AWS_LOCALSTACK", False)
        if use_localstack:
          client = get_session().client("sns", endpoint_url="http://localstack:4566")
        else:
          client = get_session().client("sns")
        
        client.publish(
            TargetArn=topic_arn,
            Message=json.dumps({"default": json.dumps(payload)}),
            MessageStructure="json",
        )
    else:
        log.error("Topic ARN is not defined")
