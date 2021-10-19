from mangum import Mangum
from api_gateway import api
from aws_lambda_powertools import Metrics
from logger import log
from database.migrate import migrate_head
from storage import storage
import os


# Import so that the application is aware of these Models
# Required so that models are initialized before they're referenced
from models.A11yReport import A11yReport  # noqa: F401
from models.A11yViolation import A11yViolation  # noqa: F401
from models.SecurityReport import SecurityReport  # noqa: F401
from models.SecurityViolation import SecurityViolation  # noqa: F401
from models.Organisation import Organisation  # noqa: F401
from models.Scan import Scan  # noqa: F401
from models.ScanIgnore import ScanIgnore  # noqa: F401
from models.Template import Template  # noqa: F401
from models.TemplateScan import TemplateScan  # noqa: F401
from models.TemplateScanTrigger import TemplateScanTrigger  # noqa: F401
from models.User import User  # noqa: F401

app = api.app
metrics = Metrics(namespace="ScanWebsites", service="api")


def print_env_variables():
    rapi = os.getenv("AWS_LAMBDA_RUNTIME_API", "NOT_FOUND")
    log.info(f"AWS_LAMBDA_RUNTIME_API: {rapi}")


@metrics.log_metrics(capture_cold_start_metric=True)
def handler(event, context):
    print_env_variables()
    log.debug(event)
    # TODO: handle different events other than https
    if "httpMethod" in event:
        # Assume it is an API Gateway event
        asgi_handler = Mangum(app)
        response = asgi_handler(event, context)
        return response

    elif "Records" in event:
        for record in event.get("Records", []):
            if "s3" in record:
                storage.retrieve_and_route(record)
            else:
                log.warning(f"Handler received unrecognised record: {record}")
        return "Success"

    elif event.get("task", "") == "migrate":
        try:
            migrate_head()
            return "Success"
        except Exception as err:
            log.error(err)
            return f"Error: {err}"

    else:
        log.warning("Handler received unrecognised event")

    return False
