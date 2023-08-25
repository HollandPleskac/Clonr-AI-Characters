import time

from limits import parse
from limits.aio.storage import RedisStorage
from limits.aio.strategies import FixedWindowElasticExpiryRateLimiter
from starlette.datastructures import MutableHeaders
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.settings import settings

STORAGE_URI = f"async+redis://default:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}"


def extract_ip_addr(request: Request) -> str:
    ip_addr = "127.0.0.1"
    if request.client and request.client.host:
        ip_addr = request.client.host
    return ip_addr


def make_redis_key(ip_addr: str) -> str:
    return f"ratelimitip:{ip_addr}"


class IpAddrRateLimitMiddleware:
    def __init__(self, app: ASGIApp, rate_limit: str) -> None:
        self.app = app
        self.rate_limit_item = parse(rate_limit)
        self.storage = RedisStorage(STORAGE_URI)
        self.limiter = FixedWindowElasticExpiryRateLimiter(storage=self.storage)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive, send)

        ip_addr = extract_ip_addr(request=request)
        identifier = make_redis_key(ip_addr=ip_addr)

        ok = await self.limiter.hit(self.rate_limit_item, identifier, cost=1)

        if not ok:
            stats = await self.limiter.get_window_stats(
                self.rate_limit_item, identifier
            )
            wait_time = stats.reset_time - time.time()

            async def send_with_extra_headers(message: Message) -> None:
                if message["type"] == "http.response.start":
                    headers = MutableHeaders(scope=message)
                    headers.append("retry-after", str(round(wait_time)))
                await send(message)

            response = JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

            return await response(scope, receive, send_with_extra_headers)

        return await self.app(scope, receive, send)
