import logzero
from mangum import Mangum

from api_gateway import api

logzero.json()
logger = logzero.logger

app = api.app


def handler(event, context):
    # TODO: handle different events other than https

    if "httpMethod" in event:
        # Assume it is an API Gateway event

        asgi_handler = Mangum(app)
        response = asgi_handler(event, context)
        return response

    else:
        logger.warning("Handler recieved unrecognised event")

    return False
