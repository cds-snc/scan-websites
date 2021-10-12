from enum import Enum
import json
import os
from boto3wrapper.wrapper import get_session
from database.db import db_session


from logger import log
from models.A11yReport import A11yReport
from models.SecurityReport import SecurityReport
from models.Scan import Scan


class AvailableScans(Enum):
    OWASP_ZAP = "OWASP Zap"
    AXE_CORE = "axe-core"


validator_list = {}
common_validations = ["url", "type", "queue", "product", "revision", "template_id"]
# Append to common_validations if additional validations are required for only one template
validator_list[AvailableScans.OWASP_ZAP.value] = common_validations
validator_list[AvailableScans.AXE_CORE.value] = common_validations


def validate_mandatory(payload, scan_type):
    if scan_type not in validator_list:
        raise ValueError("Mandatory validator not defined")

    for mandatory_key in validator_list[scan_type]:
        if mandatory_key not in payload:
            raise ValueError(f"{mandatory_key} not defined")


def dispatch(payload):
    session = db_session()
    scan = session.query(Scan).get(payload["scan_id"])

    if "type" not in payload:
        raise ValueError("type is not defined")

    validate_mandatory(payload, payload["type"])
    if payload["type"] == AvailableScans.OWASP_ZAP.value:
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

    elif payload["type"] == AvailableScans.AXE_CORE.value:
        a11y_report = A11yReport(
            product=payload["product"],
            revision=payload["revision"],
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

    if payload["event"] == "sns":
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
