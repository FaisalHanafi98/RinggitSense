"""
Test authentication endpoints and dependencies
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.main import app


client = TestClient(app)


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
        get_clerk_user,
        get_current_user,
        get_optional_user,
        ClerkJWTVerifier,
        ClerkUser,
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
    from src.database import engine, async_session_maker, get_db
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
