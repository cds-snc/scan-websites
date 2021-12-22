from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.datastructures import MutableHeaders

# Custom class required to add headers in-order to not block background tasks
# https://github.com/encode/starlette/issues/919


class SecurityHeadersMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers[
                    "Strict-Transport-Security"
                ] = "max-age=63072000; includeSubDomains; preload"
            await send(message)

        await self.app(scope, receive, send_wrapper)
