import json
import os

from database.db import db_session
from logger import log
from boto3wrapper.wrapper import get_session

from models.A11yReport import A11yReport
from models.A11yViolation import A11yViolation
from models.SecurityReport import SecurityReport
from models.SecurityViolation import SecurityViolation


def get_object(record):

    if os.environ.get("AWS_LOCALSTACK", False):
        client = get_session().resource("s3", endpoint_url="http://localstack:4566")
    else:
        client = get_session().resource("s3")

    obj = client.Object(record["s3"]["bucket"]["name"], record["s3"]["object"]["key"])
    try:
        body = obj.get()["Body"].read()
        log.info(
            f"Downloaded {record['s3']['object']['key']} from {record['s3']['bucket']['name']} with length {len(body)}"
        )
        return body
    except Exception as err:
        log.error(
            f"Error downloading {record['s3']['object']['key']} from {record['s3']['bucket']['name']}"
        )
        log.error(err)
        return False


def retrieve_and_route(record):
    name = record["s3"]["bucket"]["name"]
    body = get_object(record)

    if not body:
        return False

    try:
        payload = json.loads(body)
        session = db_session()

        if name == os.environ.get("AXE_CORE_REPORT_DATA_BUCKET", None):
            return store_axe_core_record(session, payload)
        elif name == os.environ.get("OWASP_ZAP_REPORT_DATA_BUCKET", None):
            return store_owasp_zap_record(session, payload)
        else:
            log.error(f"Unknown bucket {name}")
            return False

    except Exception as e:
        log.error(f"Error decoding {record['s3']['object']['key']} from {name}: {e}")
        return False


def store_axe_core_record(session, payload):
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


def store_owasp_zap_record(session, payload):
    security_report = session.query(SecurityReport).get(payload["id"])

    if security_report is None:
        return False

    for report in payload["report"]["site"]:
        summary = {}
        summary["status"] = "completed"
        summary["total"] = 0
        session.query(SecurityViolation).filter(
            SecurityViolation.security_report_id == security_report.id
        ).delete()
        session.commit()
        for alert in report["alerts"]:
            if "riskdesc" in alert:
                if alert["riskdesc"] in summary:
                    summary[alert["riskdesc"]] += int(alert["count"])
                else:
                    summary[alert["riskdesc"]] = int(alert["count"])

                if "solution" in alert:
                    solution = alert["solution"]
                else:
                    solution = ""

                if "reference" in alert:
                    reference = alert["reference"]
                    if reference == "<p></p>":
                        reference = ""
                else:
                    reference = ""

                if "otherinfo" in alert:
                    otherinfo = alert["otherinfo"]
                else:
                    otherinfo = ""

                summary["total"] += int(alert["count"])
                security_violation = SecurityViolation(
                    violation=alert["alert"],
                    risk=alert["riskdesc"],
                    message=alert["desc"],
                    confidence=alert["confidence"],
                    solution=solution,
                    reference=reference,
                    data=alert["instances"],
                    tags={
                        "alertRef": alert["alertRef"],
                        "riskcode": alert["riskcode"],
                        "cweid": alert["cweid"],
                        "otherinfo": otherinfo,
                    },
                    url=report["@name"],
                    security_report=security_report,
                )
                session.add(security_violation)

        security_report.summary = summary
    session.commit()
    return True
