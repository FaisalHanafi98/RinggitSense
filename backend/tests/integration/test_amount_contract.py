"""
M0.3 — Amount-sign contract tests.

Verifies the sign convention documented in docs/CONVENTIONS.md:
  - Debits (expenses) are stored POSITIVE.
  - Credits (income) are stored NEGATIVE.
  - The API serializes the stored value unchanged.

These tests are integration-tier (require a real Postgres) because they
verify the full path: parser -> storage -> API response. Constraint C1:
auto-skipped locally when TEST_DATABASE_URL is unset.

B2-related assertions are marked ``xfail`` referencing the defect register
(docs/plans/refactor-baseline.md section 2). They document the EXPECTED
(correct) behavior — re-uploads must not duplicate credits — and will flip
to passing when M1.2 lands. Never write a test that asserts the broken
behavior.
"""
import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import select

from src.models.transaction import Transaction
from src.parsers.base import ParsedTransaction, TransactionType
from src.parsers.maybank import MaybankParser

pytestmark = pytest.mark.integration

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
GOLDEN_CSV = FIXTURES_DIR / "golden" / "maybank_golden.csv"


class TestParserSignConvention:
    """The parser's signed_amount is the canonical source of the sign convention."""

    def test_debit_signed_amount_is_positive(self):
        """A debit (expense) must produce a positive signed_amount."""
        txn = ParsedTransaction(
            transaction_date=date(2026, 1, 1),
            description="TEST EXPENSE",
            amount=Decimal("50.00"),
            transaction_type=TransactionType.DEBIT,
        )
        assert txn.signed_amount > 0
        assert txn.signed_amount == Decimal("50.00")

    def test_credit_signed_amount_is_negative(self):
        """A credit (income) must produce a negative signed_amount."""
        txn = ParsedTransaction(
            transaction_date=date(2026, 1, 1),
            description="TEST INCOME",
            amount=Decimal("5000.00"),
            transaction_type=TransactionType.CREDIT,
        )
        assert txn.signed_amount < 0
        assert txn.signed_amount == Decimal("-5000.00")

    def test_maybank_golden_csv_produces_signed_amounts(self):
        """The golden CSV parser must produce signed amounts: credits negative, debits positive."""
        content = GOLDEN_CSV.read_text()
        parser = MaybankParser()
        result = parser.parse(content, filename="maybank_golden.csv")

        assert result.success, f"Parser failed: {result.errors}"
        assert len(result.transactions) > 0, "No transactions parsed from golden CSV"

        credits = [t for t in result.transactions if t.transaction_type == TransactionType.CREDIT]
        debits = [t for t in result.transactions if t.transaction_type == TransactionType.DEBIT]

        assert len(credits) > 0, "No credit transactions in golden CSV"
        assert len(debits) > 0, "No debit transactions in golden CSV"

        for t in credits:
            assert t.signed_amount < 0, (
                f"Credit '{t.description}' signed_amount must be negative, "
                f"got {t.signed_amount}"
            )

        for t in debits:
            assert t.signed_amount > 0, (
                f"Debit '{t.description}' signed_amount must be positive, "
                f"got {t.signed_amount}"
            )


class TestStorageSignConvention:
    """The DB must store amounts with the sign from signed_amount."""

    async def test_debit_stored_positive(
        self,
        client,
        integration_db,
        test_user,
    ):
        """A debit (expense) must be stored as a positive amount in the DB."""
        txn = Transaction(
            id=uuid.uuid4(),
            user_id=test_user.id,
            source_id=None,
            transaction_date=date(2026, 7, 1),
            amount=Decimal("75.00"),
            description="TEST DEBIT STORAGE",
        )
        integration_db.add(txn)
        await integration_db.flush()

        result = await integration_db.execute(
            select(Transaction).where(
                Transaction.user_id == test_user.id,
                Transaction.description == "TEST DEBIT STORAGE",
            )
        )
        stored = result.scalar_one()
        assert stored.amount > 0
        assert stored.amount == Decimal("75.00")

    async def test_credit_stored_negative(
        self,
        client,
        integration_db,
        test_user,
    ):
        """A credit (income) must be stored as a negative amount in the DB."""
        txn = Transaction(
            id=uuid.uuid4(),
            user_id=test_user.id,
            source_id=None,
            transaction_date=date(2026, 7, 1),
            amount=Decimal("-3000.00"),
            description="TEST CREDIT STORAGE",
        )
        integration_db.add(txn)
        await integration_db.flush()

        result = await integration_db.execute(
            select(Transaction).where(
                Transaction.user_id == test_user.id,
                Transaction.description == "TEST CREDIT STORAGE",
            )
        )
        stored = result.scalar_one()
        assert stored.amount < 0
        assert stored.amount == Decimal("-3000.00")


class TestApiSerialization:
    """The API must serialize the stored amount unchanged (no sign flipping)."""

    async def test_api_returns_negative_for_credit(
        self,
        client,
        integration_db,
        test_user,
    ):
        """API response must show a negative amount for a credit (income) row."""
        txn = Transaction(
            id=uuid.uuid4(),
            user_id=test_user.id,
            source_id=None,
            transaction_date=date(2026, 7, 1),
            amount=Decimal("-2500.00"),
            description="API CREDIT CHECK",
        )
        integration_db.add(txn)
        await integration_db.flush()

        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        txns = response.json()["data"]["transactions"]
        matching = [t for t in txns if t["description"] == "API CREDIT CHECK"]
        assert len(matching) == 1
        assert Decimal(matching[0]["amount"]) == Decimal("-2500.00"), (
            "API must return the stored (negative) value for credits unchanged"
        )

    async def test_api_returns_positive_for_debit(
        self,
        client,
        integration_db,
        test_user,
    ):
        """API response must show a positive amount for a debit (expense) row."""
        txn = Transaction(
            id=uuid.uuid4(),
            user_id=test_user.id,
            source_id=None,
            transaction_date=date(2026, 7, 1),
            amount=Decimal("42.50"),
            description="API DEBIT CHECK",
        )
        integration_db.add(txn)
        await integration_db.flush()

        response = await client.get("/api/v1/transactions")
        assert response.status_code == 200
        txns = response.json()["data"]["transactions"]
        matching = [t for t in txns if t["description"] == "API DEBIT CHECK"]
        assert len(matching) == 1
        assert Decimal(matching[0]["amount"]) == Decimal("42.50"), (
            "API must return the stored (positive) value for debits unchanged"
        )


class TestDedupSignContract:
    """B2-related: re-uploads must not duplicate income (credit) rows.

    These assertions are marked ``xfail`` because defect B2
    (docs/plans/refactor-baseline.md section 2, defect B2) causes credits
    to be re-stored on re-upload. The xfail documents the EXPECTED correct
    behavior. M1.2 flips these to passing. Never write a test that asserts
    the broken behavior.
    """

    @pytest.mark.xfail(
        reason="B2: dedup compares signed DB amount vs unsigned parser amount "
        "for credits — re-upload duplicates income rows. Fix: M1.2. "
        "See docs/plans/refactor-baseline.md section 2, defect register B2.",
        strict=True,
    )
    async def test_reupload_does_not_duplicate_credits(
        self,
        client,
        integration_db,
        test_user,
    ):
        """Re-uploading the same CSV must store 0 new rows (all duplicates).

        This includes credit (income) rows. Currently fails because B2
        compares the DB's signed (negative) amount against the parser's
        unsigned amount with transaction_type hardcoded to DEBIT.
        """
        content = GOLDEN_CSV.read_text()

        # First upload
        response1 = await client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("maybank_golden.csv", content.encode(), "text/csv")},
        )
        assert response1.status_code == 201
        data1 = response1.json()["data"]
        assert data1["total_stored"] > 0, "First upload must store transactions"

        # Count credits in the DB after first upload
        result1 = await integration_db.execute(
            select(Transaction).where(
                Transaction.user_id == test_user.id,
                Transaction.amount < 0,
            )
        )
        credits_after_first = len(result1.scalars().all())

        # Second upload of the SAME file
        response2 = await client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("maybank_golden.csv", content.encode(), "text/csv")},
        )
        assert response2.status_code == 201
        data2 = response2.json()["data"]

        # EXPECTED (correct) behavior: second upload stores 0 new rows
        assert data2["total_stored"] == 0, (
            "Re-upload must store 0 rows — all transactions including "
            "credits must be detected as duplicates"
        )

        # Credit count must not increase
        result2 = await integration_db.execute(
            select(Transaction).where(
                Transaction.user_id == test_user.id,
                Transaction.amount < 0,
            )
        )
        credits_after_second = len(result2.scalars().all())
        assert credits_after_second == credits_after_first, (
            "Credit (income) rows must not be duplicated on re-upload"
        )
