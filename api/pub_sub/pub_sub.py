import json
import os
from boto3wrapper.wrapper import get_session
from database.db import db_session


from logger import log
from models.A11yReport import A11yReport
from models.SecurityReport import SecurityReport
from models.Scan import Scan


def dispatch(payload):
    session = db_session()
    scan = session.query(Scan).get(payload["scan_id"])

    if payload["type"] == "OWASP Zap":
        security_report = SecurityReport(
            product=payload["product"],
            revision=payload["revision"],
            url=payload["url"],
            summary={"status": "scanning"},
            scan=scan,
        )
        session.add(security_report)
        session.commit()
        payload["id"] = str(
            security_report.id
        )  # Add a ID that can be linked back to the parent ID of the payload
        session.close()

    elif payload["type"] == "axe-core":
        a11y_report = A11yReport(
            product="product",  # TODO how is this populated?
            revision="revision",  # TODO how is this populated?
            url=payload["url"],
            summary={"status": "scanning"},
            scan=scan,
        )
        session.add(a11y_report)
        session.commit()
        payload["id"] = str(
            a11y_report.id
        )  # Add a ID that can be linked back to the parent ID of the payload
        session.close()
    else:
        log.error("Unsupported scan type")
        raise ValueError("Unsupported scan type")

    send(payload["queue"], payload)


def send(topic_arn, payload):
    if topic_arn:
        if os.environ.get("AWS_LOCALSTACK", False):
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
