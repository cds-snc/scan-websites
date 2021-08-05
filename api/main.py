from mangum import Mangum
from api_gateway import api
from logger import log
from database.migrate import migrate_head


app = api.app


def handler(event, context):
    # TODO: handle different events other than https
    if "httpMethod" in event:
        # Assume it is an API Gateway event

        asgi_handler = Mangum(app)
        response = asgi_handler(event, context)
        return response

    elif "migrate" in event:
        try:
            migrate_head()
            return "Success"
        except Exception as err:
            log.error(err)
            return "Error: check cloudwatch logs for error."

    else:
        log.warning("Handler recieved unrecognised event")

    return False
