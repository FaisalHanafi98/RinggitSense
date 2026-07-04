"""
M0.2 — Integration round-trip: create user, insert transaction, list via API.

This is the acceptance test for the integration harness: a trivial
round-trip exercising the real DB + the FastAPI app with auth overridden.
Claude agents are NOT invoked (no upload, no pipeline) — that is M0.3.
"""
import uuid
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.models.transaction import Transaction

pytestmark = pytest.mark.integration


class TestRoundTrip:
    """Trivial round-trip: DB write → API read, all against real Postgres."""

    async def test_create_user_insert_transaction_list_via_api(
        self,
        client,
        integration_db,
        test_user,
    ):
        """Create a user, insert one transaction directly, list via the API."""
        # 1. Insert one transaction directly via the session
        txn = Transaction(
            id=uuid.uuid4(),
            user_id=test_user.id,
            source_id=None,
            transaction_date=date(2026, 7, 1),
            amount=Decimal("50.00"),
            description="TEST TNB BILL PAYMENT",
        )
        integration_db.add(txn)
        await integration_db.flush()

        # 2. List transactions via the API (auth overridden to test_user)
        response = await client.get("/api/v1/transactions")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert data["pagination"]["total_items"] >= 1
        txns = data["transactions"]
        assert any(t["description"] == "TEST TNB BILL PAYMENT" for t in txns)
        assert any(Decimal(t["amount"]) == Decimal("50.00") for t in txns)

    async def test_list_empty_for_fresh_user(
        self,
        client,
        test_user,
    ):
        """A fresh user with no transactions sees an empty list."""
        response = await client.get("/api/v1/transactions")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["pagination"]["total_items"] == 0
        assert body["data"]["transactions"] == []

    async def test_transaction_is_user_scoped(
        self,
        client,
        integration_db,
        test_user,
    ):
        """Transactions belonging to other users are not visible (multi-tenancy)."""
        from src.models.user import User

        # Create a second user
        other_user = User(
            clerk_id=f"other_{uuid.uuid4().hex[:8]}",
            email=f"other_{uuid.uuid4().hex[:8]}@ringgitsense.test",
            name="Other User",
        )
        integration_db.add(other_user)
        await integration_db.flush()

        # Insert a transaction owned by the other user
        other_txn = Transaction(
            id=uuid.uuid4(),
            user_id=other_user.id,
            source_id=None,
            transaction_date=date(2026, 7, 2),
            amount=Decimal("999.00"),
            description="OTHER USER TXN",
        )
        integration_db.add(other_txn)
        await integration_db.flush()

        # List as test_user — must not see other_user's transaction
        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        txns = response.json()["data"]["transactions"]
        assert all(t["description"] != "OTHER USER TXN" for t in txns), (
            "User-scoping violated: other user's transaction visible"
        )

    async def test_transaction_persists_within_test(
        self,
        client,
        integration_db,
        test_user,
    ):
        """A transaction inserted via the session is readable via a fresh select."""
        txn = Transaction(
            id=uuid.uuid4(),
            user_id=test_user.id,
            source_id=None,
            transaction_date=date(2026, 7, 3),
            amount=Decimal("12.34"),
            description="PERSISTENCE CHECK",
        )
        integration_db.add(txn)
        await integration_db.flush()

        result = await integration_db.execute(
            select(Transaction).where(
                Transaction.user_id == test_user.id,
                Transaction.description == "PERSISTENCE CHECK",
            )
        )
        found = result.scalar_one_or_none()
        assert found is not None
        assert found.amount == Decimal("12.34")
