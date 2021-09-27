from starlette.middleware.base import BaseHTTPMiddleware


class HSTSHeaderMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, header_value="max-age=300; includeSubDomains; preload"):
        super().__init__(app)
        self.header_value = header_value

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = self.header_value
        return response
