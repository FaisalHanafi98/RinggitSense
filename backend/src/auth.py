"""
RinggitSense - Clerk JWT authentication
"""
import httpx
import jwt
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.user import User

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


class ClerkUser(BaseModel):
    """Clerk user info extracted from JWT."""
    clerk_id: str
    email: Optional[str] = None
    name: Optional[str] = None


class ClerkJWTVerifier:
    """Verifies Clerk JWT tokens using JWKS."""

    def __init__(self):
        self._jwks: Optional[dict] = None
        self._jwks_url = f"https://{settings.CLERK_DOMAIN}/.well-known/jwks.json"

    async def _fetch_jwks(self) -> dict:
        """Fetch JWKS from Clerk."""
        if self._jwks is None:
            async with httpx.AsyncClient() as client:
                response = await client.get(self._jwks_url)
                response.raise_for_status()
                self._jwks = response.json()
        return self._jwks

    async def verify_token(self, token: str) -> ClerkUser:
        """Verify Clerk JWT and extract user info."""
        try:
            # Get JWKS for signature verification
            jwks = await self._fetch_jwks()

            # Decode header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            # Find matching key
            rsa_key = None
            for key in jwks.get("keys", []):
                if key.get("kid") == kid:
                    rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                    break

            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )

            # Verify and decode token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=settings.CLERK_JWT_AUDIENCE or None,
                options={
                    "verify_aud": bool(settings.CLERK_JWT_AUDIENCE),
                    "verify_exp": True,
                    "verify_iat": True,
                }
            )

            # Extract user info
            return ClerkUser(
                clerk_id=payload.get("sub"),
                email=payload.get("email"),
                name=payload.get("name"),
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except httpx.HTTPError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to verify token"
            )


# Global verifier instance
clerk_verifier = ClerkJWTVerifier()


async def get_clerk_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> ClerkUser:
    """Dependency that extracts and validates Clerk user from JWT."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await clerk_verifier.verify_token(credentials.credentials)


async def get_current_user(
    clerk_user: ClerkUser = Depends(get_clerk_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that returns the current authenticated user.
    Creates user if not exists (first-time login).
    """
    # Try to find existing user
    result = await db.execute(
        select(User).where(User.clerk_id == clerk_user.clerk_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        # Create new user on first login
        user = User(
            clerk_id=clerk_user.clerk_id,
            email=clerk_user.email or f"{clerk_user.clerk_id}@placeholder.local",
            name=clerk_user.name,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Dependency that returns the current user if authenticated, None otherwise.
    Useful for endpoints that work both with and without auth.
    """
    if credentials is None:
        return None

    try:
        clerk_user = await clerk_verifier.verify_token(credentials.credentials)
        result = await db.execute(
            select(User).where(User.clerk_id == clerk_user.clerk_id)
        )
        return result.scalar_one_or_none()
    except HTTPException:
        return None
