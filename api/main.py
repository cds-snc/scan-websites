from mangum import Mangum
from api_gateway import api
from logger import log
from database.migrate import migrate_head
from storage import storage
import os

# Import so that the application is aware of these Models
from models.Organisation import Organisation
from models.Template import Template
from models.User import User

app = api.app


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
