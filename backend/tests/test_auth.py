"""
Test authentication endpoints and dependencies
"""
import time
from unittest.mock import AsyncMock, MagicMock, patch

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.auth import ClerkJWTVerifier, ClerkUser
from src.main import app

client = TestClient(app)


# ─── RSA key pair for test JWTs ──────────────────────────────────────

_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_public_key = _private_key.public_key()
_public_numbers = _public_key.public_numbers()


def _int_to_base64url(n: int) -> str:
    """Convert an integer to base64url-encoded string (for JWK)."""
    import base64
    byte_length = (n.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(n.to_bytes(byte_length, "big")).rstrip(b"=").decode()


_TEST_KID = "test-key-1"
_TEST_JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "kid": _TEST_KID,
            "use": "sig",
            "alg": "RS256",
            "n": _int_to_base64url(_public_numbers.n),
            "e": _int_to_base64url(_public_numbers.e),
        }
    ]
}


def _make_token(
    sub: str = "user_test123",
    email: str = "test@ringgitsense.com",
    name: str = "Test User",
    kid: str = _TEST_KID,
    exp_offset: int = 3600,
    iat_offset: int = 0,
) -> str:
    """Create a signed RS256 JWT for testing."""
    now = int(time.time())
    payload = {
        "sub": sub,
        "email": email,
        "name": name,
        "iat": now - iat_offset,
        "exp": now + exp_offset,
    }
    headers = {"kid": kid}
    return pyjwt.encode(payload, _private_key, algorithm="RS256", headers=headers)


# ─── ClerkJWTVerifier unit tests ─────────────────────────────────────


class TestClerkJWTVerifier:
    """Tests for the JWT verification logic (auth.py lines 45-102)."""

    @pytest.mark.asyncio
    async def test_valid_token_returns_clerk_user(self):
        """A properly signed token with matching kid decodes to ClerkUser."""
        verifier = ClerkJWTVerifier()
        verifier._jwks = _TEST_JWKS

        token = _make_token(sub="user_abc", email="abc@test.com", name="ABC")
        result = await verifier.verify_token(token)

        assert isinstance(result, ClerkUser)
        assert result.clerk_id == "user_abc"
        assert result.email == "abc@test.com"
        assert result.name == "ABC"

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self):
        """An expired token raises 401 with 'Token has expired'."""
        verifier = ClerkJWTVerifier()
        verifier._jwks = _TEST_JWKS

        token = _make_token(exp_offset=-100)

        with pytest.raises(HTTPException) as exc_info:
            await verifier.verify_token(token)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_malformed_token_raises_401(self):
        """A non-JWT string raises 401."""
        verifier = ClerkJWTVerifier()
        verifier._jwks = _TEST_JWKS

        with pytest.raises(HTTPException) as exc_info:
            await verifier.verify_token("not.a.jwt")
        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_wrong_kid_raises_401(self):
        """A token signed with an unknown kid raises 401."""
        verifier = ClerkJWTVerifier()
        verifier._jwks = _TEST_JWKS

        token = _make_token(kid="unknown-key-id")

        with pytest.raises(HTTPException) as exc_info:
            await verifier.verify_token(token)
        assert exc_info.value.status_code == 401
        assert "Unable to find appropriate key" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_jwks_fetch_failure_raises_503(self):
        """If JWKS fetch fails, raises 503."""
        import httpx
        verifier = ClerkJWTVerifier()

        with patch.object(verifier, "_fetch_jwks", side_effect=httpx.HTTPError("connection refused")):
            with pytest.raises(HTTPException) as exc_info:
                await verifier.verify_token(_make_token())
            assert exc_info.value.status_code == 503
            assert "Unable to verify token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_token_with_no_kid_header_raises_401(self):
        """A token without kid in header can't match any JWKS key."""
        verifier = ClerkJWTVerifier()
        verifier._jwks = _TEST_JWKS

        # Manually encode without kid
        now = int(time.time())
        token = pyjwt.encode(
            {"sub": "user_x", "iat": now, "exp": now + 3600},
            _private_key,
            algorithm="RS256",
        )

        with pytest.raises(HTTPException) as exc_info:
            await verifier.verify_token(token)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_jwks_cached_after_first_fetch(self):
        """JWKS is fetched once and cached for subsequent calls."""
        verifier = ClerkJWTVerifier()
        assert verifier._jwks is None

        mock_response = MagicMock()
        mock_response.json.return_value = _TEST_JWKS
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.auth.httpx.AsyncClient", return_value=mock_client):
            result = await verifier._fetch_jwks()
            assert result == _TEST_JWKS

            # Second call should use cache, not fetch again
            result2 = await verifier._fetch_jwks()
            assert result2 == _TEST_JWKS
            assert mock_client.get.call_count == 1


def test_user_endpoint_requires_auth():
    """Test that /api/v1/users/me requires authentication."""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
    assert "Authentication required" in response.json().get("detail", "")


def test_user_endpoint_rejects_invalid_token():
    """Test that invalid tokens are rejected.

    Note: Returns 503 if Clerk JWKS is unreachable, 401 if token is invalid.
    Both indicate proper rejection of invalid tokens.
    """
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    # Either 401 (invalid token) or 503 (can't reach Clerk to verify)
    assert response.status_code in [401, 503]


def test_auth_module_imports():
    """Test that auth module can be imported."""
    from src.auth import (
        ClerkJWTVerifier,
        ClerkUser,
        get_clerk_user,
        get_current_user,
        get_optional_user,
    )
    assert get_clerk_user is not None
    assert get_current_user is not None
    assert get_optional_user is not None
    assert ClerkJWTVerifier is not None
    assert ClerkUser is not None


def test_clerk_user_model():
    """Test ClerkUser pydantic model."""
    from src.auth import ClerkUser

    user = ClerkUser(
        clerk_id="user_123",
        email="test@example.com",
        name="Test User"
    )
    assert user.clerk_id == "user_123"
    assert user.email == "test@example.com"
    assert user.name == "Test User"


def test_clerk_user_optional_fields():
    """Test ClerkUser with optional fields."""
    from src.auth import ClerkUser

    user = ClerkUser(clerk_id="user_456")
    assert user.clerk_id == "user_456"
    assert user.email is None
    assert user.name is None


def test_database_module_imports():
    """Test that database module can be imported."""
    from src.database import async_session_maker, engine, get_db
    assert engine is not None
    assert async_session_maker is not None
    assert get_db is not None


def test_schemas_import():
    """Test that schemas can be imported."""
    from src.schemas import (
        APIResponse,
        ErrorResponse,
        PaginationMeta,
        UserResponse,
        UserUpdate,
    )
    assert APIResponse is not None
    assert ErrorResponse is not None
    assert PaginationMeta is not None
    assert UserResponse is not None
    assert UserUpdate is not None


def test_api_response_schema():
    """Test APIResponse schema."""
    from src.schemas.base import APIResponse

    response = APIResponse[dict](
        success=True,
        data={"key": "value"}
    )
    assert response.success is True
    assert response.data == {"key": "value"}
    assert response.meta is not None
    assert response.meta.timestamp is not None
    assert response.meta.request_id is not None


def test_pagination_meta():
    """Test PaginationMeta calculation."""
    from src.schemas.base import PaginationMeta

    meta = PaginationMeta.from_query(page=2, limit=20, total=95)
    assert meta.page == 2
    assert meta.limit == 20
    assert meta.total_items == 95
    assert meta.total_pages == 5  # ceil(95/20) = 5
