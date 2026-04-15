from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Force HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Restrict referrer info
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content security policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        # Remove server fingerprint
        response.headers.pop("server", None)

        return response
