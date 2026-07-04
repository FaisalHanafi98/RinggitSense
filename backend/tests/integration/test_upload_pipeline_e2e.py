"""
M0.3 — E2E pipeline test: upload -> pipeline -> DB -> API.

The highest-leverage artifact in the refactor program: one executable spec
of the full upload-to-API flow. Claude agents are mocked so no real API
key is needed. Constraint C1: auto-skipped locally when
TEST_DATABASE_URL is unset.

This test uses a **committing session** (not savepoint-isolated) because
the pipeline creates its own session via ``async_session_maker()`` — a
separate connection that cannot see uncommitted savepoint data. The
upload commits to the test DB for real; the pipeline reads and updates
those committed rows. Per-test isolation is maintained by user-scoping
(each test creates a unique user) and the session-scoped table drop.
"""
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth import get_current_user
from src.database import get_db
from src.main import app
from src.models.pipeline_run import PipelineRun
from src.models.transaction import Transaction
from src.models.user import User
from src.services.pipeline import run_pipeline

pytestmark = pytest.mark.integration

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
GOLDEN_CSV = FIXTURES_DIR / "golden" / "maybank_golden.csv"


# ── Mock agent results ──────────────────────────────────────────────


def _mock_categorize_result(description: str, amount: float):
    """Return a mock CategorizerOutput for a given transaction."""
    mock = MagicMock()
    mock.category.value = "FOOD"
    mock.confidence = 0.9
    mock.subcategory = "test_subcategory"
    mock.merchant_name = "Test Merchant"
    return mock


def _mock_detect_result():
    """Return a mock DebtDetectorOutput."""
    mock = MagicMock()
    mock.is_debt_related = False
    mock.debt_tier = None
    return mock


def _mock_analyze_result():
    """Return a mock PatternResult."""
    mock = MagicMock()
    mock.patterns = []
    mock.hidden_cost_total = 0.0
    mock.summary = "No patterns found (mocked)"
    return mock


def _mock_predict_result():
    """Return a mock PredictionResult."""
    mock = MagicMock()
    mock.total_predicted = 2500.0
    mock.confidence_interval.low = 2000.0
    mock.confidence_interval.high = 3000.0
    mock.by_category = []
    mock.assumptions = ["Based on mocked data"]
    mock.risks = []
    return mock


@pytest.fixture
async def e2e_setup(integration_engine, test_database_url):
    """Set up the E2E test with a committing session and patched pipeline.

    Yields a tuple of (client, session, user) where:
    - client: async httpx client with auth + DB overridden
    - session: a committing AsyncSession (not savepoint-isolated)
    - user: a real User row created in the test DB

    The pipeline's ``async_session_maker`` is patched to use the test
    engine so the pipeline can read and update the uploaded transactions.
    """
    factory = async_sessionmaker(
        integration_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    session = factory()

    # Create a real user
    clerk_id = f"e2e_{uuid.uuid4().hex[:12]}"
    user = User(
        clerk_id=clerk_id,
        email=f"{clerk_id}@ringgitsense.test",
        name="E2E Test User",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    async def _override_get_current_user() -> User:
        result = await session.execute(
            select(User).where(User.id == user.id)
        )
        return result.scalar_one()

    async def _override_get_db():
        yield session

    app.dependency_overrides[get_current_user] = _override_get_current_user
    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch("src.services.pipeline.async_session_maker", new=factory), \
             patch("src.routers.transactions.run_pipeline"), \
             patch("src.agents.categorizer.CategorizerAgent") as mock_cat_cls, \
             patch("src.agents.debt_detector.DebtDetectorAgent") as mock_debt_cls, \
             patch("src.agents.pattern_analyzer.PatternAnalyzerAgent") as mock_pat_cls, \
             patch("src.agents.predictor.PredictorAgent") as mock_pred_cls:

            mock_cat_instance = MagicMock()
            mock_cat_instance.categorize = MagicMock(side_effect=_mock_categorize_result)
            mock_cat_cls.return_value = mock_cat_instance

            mock_debt_instance = MagicMock()
            mock_debt_instance.detect = MagicMock(side_effect=_mock_detect_result)
            mock_debt_cls.return_value = mock_debt_instance

            mock_pat_instance = MagicMock()
            mock_pat_instance.analyze = MagicMock(return_value=_mock_analyze_result())
            mock_pat_cls.return_value = mock_pat_instance

            mock_pred_instance = MagicMock()
            mock_pred_instance.predict = MagicMock(return_value=_mock_predict_result())
            mock_pred_cls.return_value = mock_pred_instance

            yield client, session, user

    app.dependency_overrides.clear()
    await session.close()


class TestUploadPipelineE2E:
    """Full upload -> pipeline -> DB -> API round-trip with mocked Claude."""

    async def test_upload_stores_transactions(self, e2e_setup):
        """Upload of the golden CSV must store transactions with correct signs."""
        client, session, user = e2e_setup
        content = GOLDEN_CSV.read_text()

        response = await client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("maybank_golden.csv", content.encode(), "text/csv")},
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["total_parsed"] > 0, "Parser must extract transactions"
        assert data["total_stored"] > 0, "Upload must store transactions"
        assert data["bank_name"] == "Maybank"
        assert data["job_id"] is not None, "Upload must create a pipeline run"

        # Verify stored rows have correct signs (credits negative, debits positive)
        result = await session.execute(
            select(Transaction).where(Transaction.user_id == user.id)
        )
        txns = result.scalars().all()
        assert len(txns) == data["total_stored"]

        credits = [t for t in txns if t.amount < 0]
        debits = [t for t in txns if t.amount > 0]
        assert len(credits) > 0, "Must have at least one credit (income) row"
        assert len(debits) > 0, "Must have at least one debit (expense) row"

    async def test_pipeline_run_created_and_transitioned(self, e2e_setup):
        """Upload must create a pipeline_run; running the pipeline must complete it."""
        client, session, user = e2e_setup
        content = GOLDEN_CSV.read_text()

        # Upload
        response = await client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("maybank_golden.csv", content.encode(), "text/csv")},
        )
        assert response.status_code == 201
        job_id = response.json()["data"]["job_id"]
        assert job_id is not None

        # Verify pipeline_run was created with status "pending"
        result = await session.execute(
            select(PipelineRun).where(PipelineRun.id == uuid.UUID(job_id))
        )
        run = result.scalar_one()
        assert run.status == "pending"
        assert run.total_stages == 6
        assert run.stages_completed == 0

        # Run the pipeline directly (background task was patched to no-op)
        await run_pipeline(uuid.UUID(job_id))

        # Refresh and verify completed status
        await session.expire_all()
        result = await session.execute(
            select(PipelineRun).where(PipelineRun.id == uuid.UUID(job_id))
        )
        run = result.scalar_one()
        assert run.status == "completed", (
            f"Pipeline must complete, got status={run.status}, "
            f"error={run.error_message}, stage={run.error_stage}"
        )
        assert run.stages_completed == 6
        assert run.completed_at is not None
        assert run.error_message is None

    async def test_pipeline_writes_categories(self, e2e_setup):
        """After the pipeline runs, transactions must have categories assigned."""
        client, session, user = e2e_setup
        content = GOLDEN_CSV.read_text()

        # Upload
        response = await client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("maybank_golden.csv", content.encode(), "text/csv")},
        )
        assert response.status_code == 201
        job_id = response.json()["data"]["job_id"]

        # Before pipeline: no categories
        result = await session.execute(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.category.is_(None),
            )
        )
        uncategorized_before = result.scalars().all()
        assert len(uncategorized_before) > 0, "Transactions must be uncategorized before pipeline"

        # Run pipeline
        await run_pipeline(uuid.UUID(job_id))

        # After pipeline: all transactions should have categories (mocked AG-01)
        await session.expire_all()
        result = await session.execute(
            select(Transaction).where(Transaction.user_id == user.id)
        )
        txns = result.scalars().all()
        categorized = [t for t in txns if t.category is not None]
        assert len(categorized) == len(txns), (
            f"All transactions must be categorized after pipeline, "
            f"got {len(categorized)}/{len(txns)}"
        )

    async def test_api_list_after_pipeline(self, e2e_setup):
        """After upload + pipeline, GET /transactions must return stored rows."""
        client, session, user = e2e_setup
        content = GOLDEN_CSV.read_text()

        # Upload + run pipeline
        response = await client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("maybank_golden.csv", content.encode(), "text/csv")},
        )
        assert response.status_code == 201
        job_id = response.json()["data"]["job_id"]
        stored_count = response.json()["data"]["total_stored"]

        await run_pipeline(uuid.UUID(job_id))

        # List via API
        list_response = await client.get(
            "/api/v1/transactions",
            params={"limit": 200},
        )
        assert list_response.status_code == 200
        body = list_response.json()["data"]
        assert body["pagination"]["total_items"] == stored_count, (
            f"API must return all stored transactions: "
            f"expected {stored_count}, got {body['pagination']['total_items']}"
        )
        assert len(body["transactions"]) == stored_count

        # Verify each transaction has a category (assigned by mocked AG-01)
        for txn in body["transactions"]:
            assert txn["category"] is not None, (
                f"Transaction '{txn['description']}' must have a category after pipeline"
            )

    async def test_pipeline_stage_results_populated(self, e2e_setup):
        """After the pipeline runs, stage_results must contain all 6 stages."""
        client, session, user = e2e_setup
        content = GOLDEN_CSV.read_text()

        # Upload + run pipeline
        response = await client.post(
            "/api/v1/transactions/upload",
            params={"bank": "maybank"},
            files={"file": ("maybank_golden.csv", content.encode(), "text/csv")},
        )
        assert response.status_code == 201
        job_id = response.json()["data"]["job_id"]

        await run_pipeline(uuid.UUID(job_id))

        # Check stage_results
        await session.expire_all()
        result = await session.execute(
            select(PipelineRun).where(PipelineRun.id == uuid.UUID(job_id))
        )
        run = result.scalar_one()
        stage_results = run.stage_results or {}

        assert "categorizer" in stage_results, "AG-01 stage must be in stage_results"
        assert stage_results["categorizer"]["status"] == "completed"
        assert "debt_detector" in stage_results, "AG-02 stage must be in stage_results"
        assert "pattern_analyzer" in stage_results, "AG-03 stage must be in stage_results"
        assert "predictor" in stage_results, "AG-04 stage must be in stage_results"

        # AG-05 and AG-06 are stubs — they should record "skipped"
        assert "query" in stage_results, "AG-05 stub must be in stage_results"
        assert stage_results["query"]["status"] == "skipped"
        assert "advisor" in stage_results, "AG-06 stub must be in stage_results"
        assert stage_results["advisor"]["status"] == "skipped"
