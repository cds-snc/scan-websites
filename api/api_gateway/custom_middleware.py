from fastapi import Request


async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=604800 ; includeSubDomains"
    return response
