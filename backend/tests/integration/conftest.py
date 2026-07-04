"""
Integration-tier pytest configuration (M0.2).

Provides the async ``httpx`` client bound to the FastAPI app with
``get_current_user`` overridden to inject a real ``User`` row created in
the test database. DB access goes through ``integration_db`` (per-test
rollback) defined in the root conftest.

Constraint C1: an autouse fixture skips every test in this directory when
``TEST_DATABASE_URL`` is unset, so local runs without Postgres are clean.
"""
import os
import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from src.auth import get_current_user
from src.database import get_db
from src.main import app
from src.models.user import User


@pytest.fixture(autouse=True)
def _skip_if_no_test_db():
    """Auto-skip every integration test when TEST_DATABASE_URL is unset (C1)."""
    if not os.environ.get("TEST_DATABASE_URL"):
        pytest.skip(
            "TEST_DATABASE_URL not set — integration tier is CI-first (C1).",
        )


@pytest.fixture
async def test_user(integration_db) -> User:
    """Create and persist a real User row in the test database.

    The row is rolled back at teardown by ``integration_db``. Returned to
    tests and to the auth-override dependency below.
    """
    clerk_id = f"test_{uuid.uuid4().hex[:12]}"
    user = User(
        clerk_id=clerk_id,
        email=f"{clerk_id}@ringgitsense.test",
        name="Integration Test User",
    )
    integration_db.add(user)
    await integration_db.commit()
    await integration_db.refresh(user)
    return user


@pytest.fixture
async def client(integration_db, test_user) -> AsyncGenerator[AsyncClient, None]:
    """Async httpx client bound to the app with auth + DB overridden.

    - ``get_current_user`` → returns the real ``test_user`` row (no Clerk
      JWT verification, no network call to Clerk's JWKS).
    - ``get_db`` → yields the per-test ``integration_db`` session so the
      API reads/writes the same test transaction as the test body.
    """
    async def _override_get_current_user() -> User:
        result = await integration_db.execute(
            select(User).where(User.id == test_user.id)
        )
        return result.scalar_one()

    async def _override_get_db() -> AsyncGenerator:
        yield integration_db

    app.dependency_overrides[get_current_user] = _override_get_current_user
    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
