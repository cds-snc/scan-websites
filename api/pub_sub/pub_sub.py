import json
import os
from boto3wrapper.wrapper import get_session
from database.db import db_session


from logger import log
from models.A11yReport import A11yReport
from models.Scan import Scan


def dispatch(payload):
    session = db_session()
    scan = session.query(Scan).get(payload["scan_id"])

    # Add some logic to figure out what queues to dispatch to
    # Currently only dispatches to axe-core
    AXE_CORE_URLS_TOPIC = os.environ.get("AXE_CORE_URLS_TOPIC", False)

    a11y_report = A11yReport(
        product="product",  # TODO how is this populated?
        revision="revision",  # TODO how is this populated?
        url=payload["url"],
        summary={"state": "scanning"},
        scan=scan,
    )
    session.add(a11y_report)
    session.commit()
    session.close()

    # Add a ID that can be linked back to the parent ID of the payload
    payload["id"] = a11y_report.id
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
