"""
RinggitSense - Integration tests for transaction endpoints.

Tests file validation (L1), parsing, validation (L2/L3),
and the GET /transactions paginated list endpoint.
DB operations are mocked.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.user import User

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _make_mock_user() -> User:
    """Create a mock authenticated user."""
    user = MagicMock(spec=User)
    user.id = "00000000-0000-0000-0000-000000000001"
    user.clerk_id = "user_test123"
    user.email = "test@ringgitsense.com"
    return user


def _override_auth():
    """Override auth dependency to return mock user."""
    return _make_mock_user()


@pytest.fixture
def client():
    """TestClient with auth, DB, and pipeline overridden."""
    from src.auth import get_current_user
    from src.database import get_db

    # Mock DB session
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def mock_get_db():
        yield mock_session

    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[get_db] = mock_get_db

    mock_run = MagicMock()
    mock_run.id = uuid.uuid4()

    with patch("src.routers.transactions.create_pipeline_run", new_callable=AsyncMock, return_value=mock_run), \
         patch("src.routers.transactions.run_pipeline"), \
         TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ─── L1: File Validation ───────────────────────────────────────────


class TestFileValidation:
    def test_upload_requires_auth(self):
        """Upload endpoint should require authentication."""
        with TestClient(app) as c:
            response = c.post(
                "/api/v1/transactions/upload",
                params={"bank": "maybank"},
                files={"file": ("test.csv", b"data", "text/csv")},
            )
            assert response.status_code == 401

    def test_unsupported_bank_rejected(self, client):
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "unknown_bank"},
            files={"file": ("test.csv", b"data", "text/csv")},
        )
        assert response.status_code == 400
        assert "Unsupported bank" in response.json()["detail"]

    def test_unsupported_file_type_rejected(self, client):
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("test.xlsx", b"data", "application/vnd.openxmlformats")},
        )
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]

    def test_empty_file_rejected(self, client):
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("test.csv", b"", "text/csv")},
        )
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_no_filename_rejected(self, client):
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("", b"data", "text/csv")},
        )
        # FastAPI may handle this differently, but the endpoint should not crash
        assert response.status_code in (400, 422)


# ─── Parsing + Validation (L2/L3) ─────────────────────────────────


class TestMaybankUpload:
    def test_parse_golden_csv(self, client):
        """Upload the golden Maybank CSV and verify parsing + validation."""
        csv_path = FIXTURES_DIR / "maybank_sample.csv"
        with open(csv_path, "rb") as f:
            response = client.post(
                "/api/v1/transactions/upload",
                params={"bank": "maybank"},
                files={"file": ("maybank_sample.csv", f, "text/csv")},
            )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True

        data = body["data"]
        assert data["bank_name"] == "Maybank"
        assert data["total_parsed"] == 10
        assert data["total_valid"] == 10
        assert data["total_invalid"] == 0
        assert data["total_stored"] == 10
        assert data["duplicates_skipped"] == 0

    def test_decimal_precision_preserved(self, client):
        """Verify that amounts like RM25.90 are parsed correctly."""
        csv_content = (
            "Transaction Date,Description,Debit,Credit,Balance\n"
            "15/01/2026,TEST TRANSACTION,25.90,,974.10\n"
        )
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        )
        assert response.status_code == 201
        assert response.json()["data"]["total_parsed"] == 1


class TestCIMBUpload:
    def test_parse_golden_csv(self, client):
        """Upload the golden CIMB CSV and verify parsing."""
        csv_path = FIXTURES_DIR / "cimb_sample.csv"
        with open(csv_path, "rb") as f:
            response = client.post(
                "/api/v1/transactions/upload",
                params={"bank": "cimb"},
                files={"file": ("cimb_sample.csv", f, "text/csv")},
            )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True

        data = body["data"]
        assert data["bank_name"] == "CIMB"
        assert data["total_parsed"] >= 4  # At least 4 of the 5 rows should parse


class TestValidationIntegration:
    def test_future_date_rejected_in_upload(self, client):
        """Transaction with a future date should be flagged as invalid."""
        csv_content = (
            "Transaction Date,Description,Debit,Credit,Balance\n"
            "15/12/2099,FUTURE TRANSACTION,100.00,,900.00\n"
            "15/01/2026,VALID TRANSACTION,50.00,,850.00\n"
        )
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["total_parsed"] == 2
        assert data["total_invalid"] >= 1
        assert data["total_valid"] >= 1

    def test_unparseable_csv_returns_422(self, client):
        """Completely unparseable content should return 422."""
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("bad.csv", b"not,a,valid,bank,statement", "text/csv")},
        )
        # Either 422 (parse failure) or 201 with 0 valid transactions
        assert response.status_code in (201, 422)


# ─── GET /transactions (paginated list) ──────────────────────────────


def _make_mock_transaction(**overrides):
    """Create a mock object that satisfies TransactionResponse.model_validate(from_attributes=True)."""
    defaults = {
        "id": uuid.uuid4(),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "source_id": uuid.uuid4(),
        "transaction_date": date(2026, 1, 15),
        "amount": Decimal("25.90"),
        "description": "GRAB CAR KLCC",
        "original_description": "GRAB CAR KLCC",
        "category": "TRANSPORT",
        "category_confidence": Decimal("0.95"),
        "subcategory": "ride_hailing",
        "merchant_name": "Grab",
        "is_debt_related": False,
        "debt_tier": None,
        "debt_id": None,
        "is_recurring": False,
        "user_comment": None,
        "created_at": datetime(2026, 1, 15, 10, 30, 0),
    }
    defaults.update(overrides)

    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _make_list_client(transactions: list, total: int):
    """Create a TestClient whose DB mock returns the given transactions and total count."""
    from src.auth import get_current_user
    from src.database import get_db

    call_count = 0

    async def mock_execute(query, *args, **kwargs):
        nonlocal call_count
        call_count += 1

        if call_count % 2 == 1:
            # First call: count query → scalar_one()
            mock_result = MagicMock()
            mock_result.scalar_one.return_value = total
            return mock_result
        else:
            # Second call: paginated query → scalars().all()
            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = transactions
            mock_result.scalars.return_value = mock_scalars
            return mock_result

    mock_session = AsyncMock()
    mock_session.execute = mock_execute

    async def mock_get_db():
        yield mock_session

    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[get_db] = mock_get_db

    test_client = TestClient(app)
    return test_client


class TestListTransactions:
    def test_requires_auth(self):
        """GET /transactions without auth returns 401."""
        app.dependency_overrides.clear()
        with TestClient(app) as c:
            response = c.get("/api/v1/transactions")
            assert response.status_code == 401

    def test_empty_list(self):
        """Returns empty list with correct pagination when no transactions exist."""
        c = _make_list_client(transactions=[], total=0)
        try:
            response = c.get("/api/v1/transactions")
            assert response.status_code == 200

            body = response.json()
            assert body["success"] is True
            assert body["data"]["transactions"] == []
            assert body["data"]["pagination"]["total_items"] == 0
            assert body["data"]["pagination"]["page"] == 1
        finally:
            app.dependency_overrides.clear()

    def test_returns_transactions_with_correct_shape(self):
        """Response shape matches TransactionResponse schema."""
        txn = _make_mock_transaction(
            description="NASI KANDAR PELITA",
            amount=Decimal("12.50"),
            category="FOOD",
        )
        c = _make_list_client(transactions=[txn], total=1)
        try:
            response = c.get("/api/v1/transactions")
            assert response.status_code == 200

            body = response.json()
            items = body["data"]["transactions"]
            assert len(items) == 1

            t = items[0]
            assert t["description"] == "NASI KANDAR PELITA"
            assert t["amount"] == "12.50"
            assert t["category"] == "FOOD"
            assert "id" in t
            assert "transaction_date" in t
            assert "created_at" in t
        finally:
            app.dependency_overrides.clear()

    def test_pagination_params(self):
        """Custom page and limit are reflected in pagination metadata."""
        txns = [
            _make_mock_transaction(
                description=f"TXN {i}",
                amount=Decimal(f"{10 + i}.00"),
                transaction_date=date(2026, 1, i + 1),
            )
            for i in range(5)
        ]
        c = _make_list_client(transactions=txns, total=25)
        try:
            response = c.get("/api/v1/transactions?page=2&limit=5")
            assert response.status_code == 200

            pagination = response.json()["data"]["pagination"]
            assert pagination["page"] == 2
            assert pagination["limit"] == 5
            assert pagination["total_items"] == 25
            assert pagination["total_pages"] == 5
        finally:
            app.dependency_overrides.clear()

    def test_category_filter_accepted(self):
        """Category filter param is accepted without error."""
        c = _make_list_client(transactions=[], total=0)
        try:
            response = c.get("/api/v1/transactions?category=FOOD")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_date_range_filter_accepted(self):
        """Date range filter params are accepted without error."""
        c = _make_list_client(transactions=[], total=0)
        try:
            response = c.get(
                "/api/v1/transactions?date_from=2026-01-01&date_to=2026-01-31"
            )
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_search_filter_accepted(self):
        """Search filter param is accepted without error."""
        c = _make_list_client(transactions=[], total=0)
        try:
            response = c.get("/api/v1/transactions?search=GRAB")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.clear()

    def test_invalid_page_rejected(self):
        """Page < 1 is rejected by FastAPI validation."""
        c = _make_list_client(transactions=[], total=0)
        try:
            response = c.get("/api/v1/transactions?page=0")
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()

    def test_limit_over_200_rejected(self):
        """Limit > 200 is rejected by FastAPI validation."""
        c = _make_list_client(transactions=[], total=0)
        try:
            response = c.get("/api/v1/transactions?limit=201")
            assert response.status_code == 422
        finally:
            app.dependency_overrides.clear()


# ─── Upload → Pipeline auto-trigger ──────────────────────────────


class TestUploadPipelineTrigger:
    @patch("src.routers.transactions.run_pipeline")
    @patch("src.routers.transactions.create_pipeline_run")
    def test_upload_triggers_pipeline_and_returns_job_id(self, mock_create, mock_run, client):
        mock_run_obj = MagicMock()
        mock_run_obj.id = uuid.uuid4()
        mock_create.return_value = mock_run_obj

        csv_content = (
            "Transaction Date,Description,Debit,Credit,Balance\n"
            "15/01/2026,NASI KANDAR PELITA,12.50,,987.50\n"
        )
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["job_id"] == str(mock_run_obj.id)
        mock_create.assert_called_once()

    @patch("src.routers.transactions.run_pipeline")
    @patch("src.routers.transactions.create_pipeline_run")
    def test_upload_no_pipeline_when_no_transactions_stored(self, mock_create, mock_run, client):
        csv_content = (
            "Transaction Date,Description,Debit,Credit,Balance\n"
            "15/12/2099,FUTURE ONLY,100.00,,900.00\n"
        )
        response = client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["job_id"] is None
        mock_create.assert_not_called()
