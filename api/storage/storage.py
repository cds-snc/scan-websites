import json
import os

from database.db import db_session
from logger import log
from boto3wrapper.wrapper import get_session

from models.A11yReport import A11yReport
from models.A11yViolation import A11yViolation


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


def retrieve_and_store(record):
    name = record.s3.bucket.name
    body = get_object(record)

    if not body:
        return False

    try:
        payload = json.loads(body)

        if name == os.environ.get("AXE_CORE_REPORT_DATA_BUCKET", None):
            return store_axe_core_record(payload)
        else:
            log.error(f"Unknown bucket {name}")
            return False

    except Exception:
        log.error(f"Error decoding {record.s3.object.key} from {name}")
        return False


def store_axe_core_record(payload):
    session = db_session()
    a11y_report = session.query(A11yReport).get(payload["id"])

    if a11y_report is None:
        return False

    report = payload["report"]
    summary = {
        "status": "completed",
        "inapplicable": len(report["inapplicable"]),
        "incomplete": len(report["incomplete"]),
        "violations": sum_impact(report["violations"]),
        "passes": len(report["passes"]),
    }
    summary["violations"]["total"] = sum(list(summary["violations"].values()))
    a11y_report.summary = summary
    session.commit()

    for violation in report["violations"]:
        for node in violation["nodes"]:
            for type in ["any", "all", "none"]:
                for item in node[type]:
                    a11y_violation = A11yViolation(
                        violation=violation["id"],
                        impact=node["impact"],
                        target=node["target"],
                        html=node["html"],
                        data=item["data"],
                        tags=violation["tags"],
                        message=item["message"],
                        url=payload["url"],
                        a11y_report=a11y_report,
                    )
                    session.add(a11y_violation)
    session.commit()
    return True


def sum_impact(violations):
    d = {}
    for v in violations:
        if "impact" in v:
            if v["impact"] in d:
                d[v["impact"]] = d[v["impact"]] + 1
            else:
                d[v["impact"]] = 1
    return d
