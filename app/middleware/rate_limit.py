import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._requests: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW
        limit = settings.RATE_LIMIT_REQUESTS

        # Remove timestamps outside the current window
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if now - t < window
        ]

        if len(self._requests[client_ip]) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": f"Too many requests. Max {limit} per {window}s."},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
