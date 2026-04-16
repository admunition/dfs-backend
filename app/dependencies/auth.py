import httpx
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validates Supabase JWT token using JWKS (supports both HS256 and ES256).
    """
    token = credentials.credentials

    # Log token info for debugging
    logger.info(f"[auth] SUPABASE_URL: {settings.SUPABASE_URL}")
    logger.info(f"[auth] ANON_KEY preview: {settings.SUPABASE_ANON_KEY[:30]}")
    logger.info(f"[auth] Token preview: {token[:30]}")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": settings.SUPABASE_ANON_KEY,
            },
            timeout=10,
        )

    # Log full Supabase response for debugging
    logger.info(f"[auth] Supabase status: {response.status_code}")
    logger.info(f"[auth] Supabase response: {response.text[:300]}")

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Supabase rejected token: {response.text[:200]}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = response.json()
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "role": user.get("role"),
    }
