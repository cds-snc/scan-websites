from mangum import Mangum
from api_gateway.v1 import api
from front_end import view
from logger import log
from database.migrate import migrate_head
from storage import storage
import os


# Import so that the application is aware of these Models
# Required so that models are initialized before they're referenced
from models.A11yReport import A11yReport  # noqa: F401
from models.A11yViolation import A11yViolation  # noqa: F401
from models.Organisation import Organisation  # noqa: F401
from models.Scan import Scan  # noqa: F401
from models.Template import Template  # noqa: F401
from models.TemplateScan import TemplateScan  # noqa: F401
from models.TemplateScanTrigger import TemplateScanTrigger  # noqa: F401
from models.User import User  # noqa: F401


api_v1 = api.app
app = view.app


def print_env_variables():
    rapi = os.getenv("AWS_LAMBDA_RUNTIME_API", "NOT_FOUND")
    log.info(f"AWS_LAMBDA_RUNTIME_API: {rapi}")


def handler(event, context):
    print_env_variables()
    log.debug(event)
    # TODO: handle different events other than https
    if "httpMethod" in event:
        # Assume it is an API Gateway event
        asgi_handler = Mangum(app)

        if "path" in event:
            if event["path"].lower().startswith("/api/v1"):
                asgi_handler = Mangum(api_v1)

        response = asgi_handler(event, context)

        return response

    elif "Records" in event:
        for record in event.get("Records", []):
            if "s3" in record:
                storage.get_object(record)
            else:
                log.warning(f"Handler received unrecognised record: {record}")
        return "Success"

    elif event.get("task", "") == "migrate":
        try:
            migrate_head()
            return "Success"
        except Exception as err:
            log.error(err)
            return "Error"

    else:
        log.warning("Handler received unrecognised event")

    return False
