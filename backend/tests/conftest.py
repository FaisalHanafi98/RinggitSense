"""
Pytest configuration and fixtures for RinggitSense tests.

Root conftest: shared fixtures + integration-tier gating (M0.2).

Constraint C1 (Docker off-limits locally): the integration tier is
CI-first. Tests marked ``integration`` auto-skip when
``TEST_DATABASE_URL`` is unset, so a local run without a Postgres
instance never fails on infrastructure. CI sets the variable and runs
the marker against the GitHub Actions Postgres service.
"""
import os
import uuid
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def pytest_configure(config: pytest.Config) -> None:
    """Register the integration marker (M0.2)."""
    config.addinivalue_line(
        "markers",
        "integration: tests requiring a real PostgreSQL instance via "
        "TEST_DATABASE_URL (CI-first; auto-skipped locally when unset).",
    )


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Use asyncio as the async backend."""
    return "asyncio"


# ── Integration-tier fixtures (M0.2, constraint C1) ─────────────────


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Return TEST_DATABASE_URL or skip the session if unset (C1).

    Session-scoped so the value is resolved once per pytest session. The
    actual skip is emitted per-test via the autouse fixture in
    ``tests/integration/conftest.py``; this fixture is the gate for
    session-scoped dependents (``integration_engine``).
    """
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip(
            "TEST_DATABASE_URL not set — integration tier is CI-first (C1).",
        )
    return url


@pytest.fixture(scope="session")
async def integration_engine(test_database_url: str):
    """Session-scoped async engine bound to the test database.

    Creates all tables from ``Base.metadata`` at session start and drops
    them at session end. If the DB is unreachable, skips rather than
    erroring (C1: a misconfigured local run should not show red).
    """
    from src.models import Base  # noqa: PLC0415 — lazy import keeps unit runs clean

    engine = create_async_engine(test_database_url, echo=False, pool_pre_ping=True)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        await engine.dispose()
        pytest.skip(
            f"TEST_DATABASE_URL is set but unreachable: {exc} — integration "
            "tier is CI-first (C1).",
        )
        return  # pragma: no cover — pytest.skip raises

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def integration_db(integration_engine) -> AsyncGenerator[AsyncSession, None]:
    """Function-scoped async session with per-test isolation (M0.2).

    Uses a connection-level outer transaction with
    ``join_transaction_mode="create_savepoint"`` so commits inside the
    application code (e.g. ``get_current_user``, upload endpoint) release
    a SAVEPOINT but the outer transaction is rolled back at teardown —
    tests are fully isolated without per-test schema rebuilds.
    """
    async with integration_engine.connect() as conn:
        await conn.begin()  # outer transaction, always rolled back
        factory = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
            join_transaction_mode="create_savepoint",
        )
        session = factory()
        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()


@pytest.fixture
def test_user_id() -> uuid.UUID:
    """Stable UUID for the injected test user within a single test."""
    return uuid.uuid4()
