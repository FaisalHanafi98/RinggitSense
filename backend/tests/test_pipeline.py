"""
RinggitSense - Tests for async pipeline infrastructure.

Tests the pipeline service, job endpoints, and semaphore behavior.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.models.pipeline_run import PipelineRun
from src.models.user import User
from src.services.pipeline import PIPELINE_STAGES, get_claude_semaphore

# ─── Fixtures ────────────────────────────────────────────────────────


def _make_mock_user() -> User:
    user = MagicMock(spec=User)
    user.id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    user.clerk_id = "user_test_pipeline"
    user.email = "pipeline@ringgitsense.com"
    return user


def _make_mock_pipeline_run(**overrides) -> MagicMock:
    defaults = {
        "id": uuid.uuid4(),
        "user_id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
        "source_id": uuid.uuid4(),
        "status": "pending",
        "current_stage": None,
        "stages_completed": 0,
        "total_stages": 6,
        "error_message": None,
        "error_stage": None,
        "stage_results": {},
        "started_at": None,
        "completed_at": None,
        "created_at": datetime(2026, 1, 15, 10, 0, 0),
        "updated_at": datetime(2026, 1, 15, 10, 0, 0),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for k, v in defaults.items():
        setattr(mock, k, v)
    return mock


def _make_mock_data_source(user_id=None, source_id=None):
    mock = MagicMock()
    mock.id = source_id or uuid.uuid4()
    mock.user_id = user_id or uuid.UUID("00000000-0000-0000-0000-000000000001")
    return mock


def _override_auth():
    return _make_mock_user()


# ─── Pipeline model tests ────────────────────────────────────────────


class TestPipelineRunModel:
    def test_import(self):
        from src.models import PipelineRun
        assert PipelineRun is not None
        assert PipelineRun.__tablename__ == "pipeline_runs"

    def test_default_status_is_pending(self):
        from src.models.pipeline_run import PipelineRun
        columns = {c.name: c for c in PipelineRun.__table__.columns}
        assert columns["status"].default.arg == "pending"

    def test_default_stages_is_6(self):
        from src.models.pipeline_run import PipelineRun
        columns = {c.name: c for c in PipelineRun.__table__.columns}
        assert columns["total_stages"].default.arg == 6


class TestPipelineStages:
    def test_six_stages_defined(self):
        assert len(PIPELINE_STAGES) == 6

    def test_stages_start_with_ag01(self):
        assert PIPELINE_STAGES[0] == ("AG-01", "categorizer")

    def test_stages_end_with_ag06(self):
        assert PIPELINE_STAGES[-1] == ("AG-06", "advisor")

    def test_all_agent_ids_unique(self):
        ids = [s[0] for s in PIPELINE_STAGES]
        assert len(ids) == len(set(ids))


class TestClaudioSemaphore:
    def test_semaphore_limit_is_3(self):
        sem = get_claude_semaphore()
        # asyncio.Semaphore._value is the internal counter
        assert sem._value == 3


# ─── Pipeline schema tests ───────────────────────────────────────────


class TestPipelineSchemas:
    def test_pipeline_run_response_from_mock(self):
        from src.schemas.pipeline import PipelineRunResponse
        mock_run = _make_mock_pipeline_run()
        resp = PipelineRunResponse.model_validate(mock_run)
        assert resp.status == "pending"
        assert resp.total_stages == 6
        assert resp.stages_completed == 0

    def test_pipeline_run_create_schema(self):
        from src.schemas.pipeline import PipelineRunCreate
        source_id = uuid.uuid4()
        create = PipelineRunCreate(source_id=source_id)
        assert create.source_id == source_id


# ─── Jobs endpoint tests ─────────────────────────────────────────────


def _make_jobs_client(execute_side_effects: list):
    """Create a TestClient with mocked DB for jobs endpoints.

    execute_side_effects: list of return values for sequential db.execute() calls.
    Each entry is a dict describing what the mock result should return:
      {"scalar_one_or_none": value} or {"scalar_one": value} or {"scalars_all": list}
    """
    from src.auth import get_current_user
    from src.database import get_db

    call_count = 0

    async def mock_execute(query, *args, **kwargs):
        nonlocal call_count
        idx = min(call_count, len(execute_side_effects) - 1)
        call_count += 1
        effect = execute_side_effects[idx]

        mock_result = MagicMock()
        if "scalar_one_or_none" in effect:
            mock_result.scalar_one_or_none.return_value = effect["scalar_one_or_none"]
        if "scalar_one" in effect:
            mock_result.scalar_one.return_value = effect["scalar_one"]
        if "scalars_all" in effect:
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = effect["scalars_all"]
            mock_result.scalars.return_value = mock_scalars
        return mock_result

    mock_session = AsyncMock()
    mock_session.execute = mock_execute
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    async def mock_get_db():
        yield mock_session

    app.dependency_overrides[get_current_user] = _override_auth
    app.dependency_overrides[get_db] = mock_get_db

    return TestClient(app)


class TestJobsEndpointAuth:
    def test_post_jobs_requires_auth(self):
        app.dependency_overrides.clear()
        with TestClient(app) as c:
            response = c.post("/api/v1/jobs", json={"source_id": str(uuid.uuid4())})
            assert response.status_code == 401

    def test_get_job_requires_auth(self):
        app.dependency_overrides.clear()
        with TestClient(app) as c:
            response = c.get(f"/api/v1/jobs/{uuid.uuid4()}")
            assert response.status_code == 401

    def test_list_jobs_requires_auth(self):
        app.dependency_overrides.clear()
        with TestClient(app) as c:
            response = c.get("/api/v1/jobs")
            assert response.status_code == 401


class TestPostJobs:
    def test_returns_404_for_unknown_source(self):
        # DataSource query returns None
        c = _make_jobs_client([{"scalar_one_or_none": None}])
        try:
            response = c.post(
                "/api/v1/jobs", json={"source_id": str(uuid.uuid4())}
            )
            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    def test_returns_409_for_active_pipeline(self):
        source = _make_mock_data_source()
        active_run = _make_mock_pipeline_run(status="running")
        # 1st call: DataSource found, 2nd call: active run found
        c = _make_jobs_client([
            {"scalar_one_or_none": source},
            {"scalar_one_or_none": active_run},
        ])
        try:
            response = c.post(
                "/api/v1/jobs", json={"source_id": str(source.id)}
            )
            assert response.status_code == 409
            assert "already running" in response.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    @patch("src.routers.jobs.run_pipeline")
    @patch("src.routers.jobs.create_pipeline_run")
    def test_creates_and_returns_202(self, mock_create, mock_run):
        source = _make_mock_data_source()
        new_run = _make_mock_pipeline_run(source_id=source.id)
        mock_create.return_value = new_run

        # 1st call: DataSource found, 2nd call: no active run
        c = _make_jobs_client([
            {"scalar_one_or_none": source},
            {"scalar_one_or_none": None},
        ])
        try:
            response = c.post(
                "/api/v1/jobs", json={"source_id": str(source.id)}
            )
            assert response.status_code == 202
            body = response.json()
            assert body["success"] is True
            assert body["data"]["status"] == "pending"
            assert body["data"]["total_stages"] == 6
        finally:
            app.dependency_overrides.clear()


class TestGetJobStatus:
    def test_returns_404_for_unknown_job(self):
        c = _make_jobs_client([{"scalar_one_or_none": None}])
        try:
            response = c.get(f"/api/v1/jobs/{uuid.uuid4()}")
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_returns_running_job_status(self):
        run = _make_mock_pipeline_run(
            status="running",
            current_stage="categorizer",
            stages_completed=0,
        )
        c = _make_jobs_client([{"scalar_one_or_none": run}])
        try:
            response = c.get(f"/api/v1/jobs/{run.id}")
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["status"] == "running"
            assert data["current_stage"] == "categorizer"
        finally:
            app.dependency_overrides.clear()

    def test_returns_failed_job_with_error(self):
        run = _make_mock_pipeline_run(
            status="failed",
            error_message="Claude API rate limit exceeded",
            error_stage="categorizer",
            stages_completed=0,
        )
        c = _make_jobs_client([{"scalar_one_or_none": run}])
        try:
            response = c.get(f"/api/v1/jobs/{run.id}")
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["status"] == "failed"
            assert data["error_message"] == "Claude API rate limit exceeded"
            assert data["error_stage"] == "categorizer"
        finally:
            app.dependency_overrides.clear()

    def test_returns_completed_job(self):
        run = _make_mock_pipeline_run(
            status="completed",
            stages_completed=6,
            stage_results={"categorizer": {"status": "completed", "categorized": 10}},
        )
        c = _make_jobs_client([{"scalar_one_or_none": run}])
        try:
            response = c.get(f"/api/v1/jobs/{run.id}")
            assert response.status_code == 200
            data = response.json()["data"]
            assert data["status"] == "completed"
            assert data["stages_completed"] == 6
        finally:
            app.dependency_overrides.clear()


# ─── Pipeline service unit tests ──────────────────────────────────────


class TestPipelineService:
    @pytest.mark.asyncio
    async def test_create_pipeline_run(self):
        from src.services.pipeline import create_pipeline_run

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()

        user_id = uuid.uuid4()
        source_id = uuid.uuid4()

        run = await create_pipeline_run(mock_db, user_id, source_id)

        assert run.user_id == user_id
        assert run.source_id == source_id
        assert run.status == "pending"
        assert run.total_stages == 6
        mock_db.add.assert_called_once()
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_stage_unimplemented_returns_skipped(self):
        from src.services.pipeline import _execute_stage

        # AG-04 through AG-06 are not yet implemented — use AG-04 as the stub
        result = await _execute_stage(
            "AG-04", "predictor", [], {}, AsyncMock()
        )
        assert result["status"] == "skipped"
        assert "not yet implemented" in result["reason"]

    @pytest.mark.asyncio
    async def test_execute_stage_debt_detector_no_transactions(self):
        from src.services.pipeline import _execute_stage

        result = await _execute_stage(
            "AG-02", "debt_detector", [], {}, AsyncMock()
        )
        assert result["status"] == "skipped"
        assert "no transactions" in result["reason"]

    @pytest.mark.asyncio
    async def test_execute_stage_pattern_analyzer_no_transactions(self):
        from src.services.pipeline import _execute_stage

        result = await _execute_stage(
            "AG-03", "pattern_analyzer", [], {}, AsyncMock()
        )
        assert result["status"] == "skipped"
        assert "no transactions" in result["reason"]

    @pytest.mark.asyncio
    @patch("src.agents.pattern_analyzer.PatternAnalyzerAgent")
    async def test_execute_stage_pattern_analyzer_returns_patterns(self, mock_agent_cls):
        from src.services.pipeline import _execute_stage

        mock_pattern = MagicMock()
        mock_pattern.type.value = "HIDDEN_COST"
        mock_pattern.name = "Subscription Creep"
        mock_pattern.impact = 183.80
        mock_pattern.confidence = 0.92

        mock_result = MagicMock()
        mock_result.patterns = [mock_pattern]
        mock_result.hidden_cost_total = 183.80
        mock_result.summary = "Subscription services cost RM183.80/month."

        mock_agent = MagicMock()
        mock_agent.analyze.return_value = mock_result
        mock_agent_cls.return_value = mock_agent

        txn = MagicMock()
        txn.id = uuid.uuid4()
        txn.description = "NETFLIX MALAYSIA"
        txn.amount = Decimal("54.90")
        txn.transaction_date = date(2026, 1, 6)
        txn.category = "BILLS"
        txn.subcategory = None

        result = await _execute_stage("AG-03", "pattern_analyzer", [txn], {}, AsyncMock())

        assert result["status"] == "completed"
        assert result["pattern_count"] == 1
        assert result["hidden_cost_total"] == 183.80
        assert result["patterns"][0]["type"] == "HIDDEN_COST"

    @pytest.mark.asyncio
    @patch("src.agents.debt_detector.DebtDetectorAgent")
    async def test_execute_stage_debt_detector_detects_debt(self, mock_agent_cls):
        from src.services.pipeline import _execute_stage

        mock_result = MagicMock()
        mock_result.is_debt_related = True
        mock_result.debt_tier.value = "FORMAL"
        mock_result.confidence = 0.98

        mock_agent = MagicMock()
        mock_agent.detect.return_value = mock_result
        mock_agent_cls.return_value = mock_agent

        txn = MagicMock()
        txn.id = uuid.uuid4()
        txn.description = "PTPTN REPAYMENT"
        txn.amount = Decimal("250.00")

        mock_db = AsyncMock()
        result = await _execute_stage("AG-02", "debt_detector", [txn], {}, mock_db)

        assert result["status"] == "completed"
        assert result["detected"] == 1
        assert txn.is_debt_related is True
        assert txn.debt_tier == "FORMAL"
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.agents.debt_detector.DebtDetectorAgent")
    async def test_execute_stage_debt_detector_non_debt(self, mock_agent_cls):
        from src.services.pipeline import _execute_stage

        mock_result = MagicMock()
        mock_result.is_debt_related = False

        mock_agent = MagicMock()
        mock_agent.detect.return_value = mock_result
        mock_agent_cls.return_value = mock_agent

        txn = MagicMock()
        txn.id = uuid.uuid4()
        txn.description = "MCDONALD'S"
        txn.amount = Decimal("25.90")

        mock_db = AsyncMock()
        result = await _execute_stage("AG-02", "debt_detector", [txn], {}, mock_db)

        assert result["status"] == "completed"
        assert result["detected"] == 0

    @pytest.mark.asyncio
    @patch("src.agents.debt_detector.DebtDetectorAgent")
    async def test_execute_stage_debt_detector_handles_error(self, mock_agent_cls):
        from src.services.pipeline import _execute_stage

        mock_agent = MagicMock()
        mock_agent.detect.side_effect = ValueError("API error")
        mock_agent_cls.return_value = mock_agent

        txn = MagicMock()
        txn.id = uuid.uuid4()
        txn.description = "WEIRD TXN"
        txn.amount = Decimal("100.00")

        mock_db = AsyncMock()
        result = await _execute_stage("AG-02", "debt_detector", [txn], {}, mock_db)

        assert result["status"] == "completed"
        assert result["detected"] == 0
        assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_execute_stage_categorizer_skips_when_all_categorized(self):
        from src.services.pipeline import _execute_stage

        # Mock transaction that already has a category
        txn = MagicMock()
        txn.category = "FOOD"

        result = await _execute_stage(
            "AG-01", "categorizer", [txn], {}, AsyncMock()
        )
        assert result["status"] == "skipped"
        assert "already categorized" in result["reason"]

    @pytest.mark.asyncio
    @patch("src.agents.categorizer.CategorizerAgent")
    async def test_execute_stage_categorizer_processes_uncategorized(self, mock_agent_cls):
        from src.services.pipeline import _execute_stage

        mock_result = MagicMock()
        mock_result.category.value = "FOOD"
        mock_result.confidence = 0.95
        mock_result.subcategory = "restaurant"
        mock_result.merchant_name = "Nasi Kandar Pelita"

        mock_agent = MagicMock()
        mock_agent.categorize.return_value = mock_result
        mock_agent_cls.return_value = mock_agent

        txn = MagicMock()
        txn.id = uuid.uuid4()
        txn.category = None
        txn.description = "NASI KANDAR PELITA"
        txn.amount = Decimal("12.50")
        txn.transaction_date = date(2026, 1, 15)

        mock_db = AsyncMock()
        result = await _execute_stage("AG-01", "categorizer", [txn], {}, mock_db)

        assert result["status"] == "completed"
        assert result["categorized"] == 1
        assert txn.category == "FOOD"
        assert txn.category_confidence == 0.95
        mock_db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.agents.categorizer.CategorizerAgent")
    async def test_execute_stage_categorizer_handles_agent_error(self, mock_agent_cls):
        from src.services.pipeline import _execute_stage

        mock_agent = MagicMock()
        mock_agent.categorize.side_effect = ValueError("Could not parse JSON")
        mock_agent_cls.return_value = mock_agent

        txn = MagicMock()
        txn.id = uuid.uuid4()
        txn.category = None
        txn.description = "UNKNOWN TXN"
        txn.amount = Decimal("999.99")
        txn.transaction_date = date(2026, 1, 15)

        mock_db = AsyncMock()
        result = await _execute_stage("AG-01", "categorizer", [txn], {}, mock_db)

        assert result["status"] == "completed"
        assert result["categorized"] == 0
        assert len(result["errors"]) == 1
        assert "Could not parse JSON" in result["errors"][0]["error"]

    @pytest.mark.asyncio
    @patch("src.services.pipeline._run_pattern_analyzer")
    async def test_run_pipeline_marks_running_then_completed(self, mock_pa):
        """Full pipeline run with all stages stubbed.

        AG-01 is skipped naturally (transaction already categorized).
        AG-02 swallows per-transaction errors internally.
        AG-03 is patched because it makes a batch Anthropic call with no key in CI.
        AG-04..06 are stubbed by the pipeline itself (not yet implemented).
        """
        mock_pa.return_value = {
            "status": "completed",
            "pattern_count": 0,
            "hidden_cost_total": 0.0,
            "summary": "No patterns detected.",
            "patterns": [],
        }

        from src.services.pipeline import run_pipeline

        run_id = uuid.uuid4()
        mock_run = PipelineRun(
            id=run_id,
            user_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            status="pending",
            total_stages=6,
            stages_completed=0,
            stage_results={},
        )

        # Mock a transaction with category already set (so categorizer skips)
        mock_txn = MagicMock()
        mock_txn.category = "FOOD"
        mock_txn.user_id = mock_run.user_id
        mock_txn.source_id = mock_run.source_id

        call_count = 0

        async def mock_execute(query, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_result = MagicMock()
            if call_count == 1:
                # Load pipeline run
                mock_result.scalar_one_or_none.return_value = mock_run
            elif call_count == 2:
                # Load transactions
                mock_scalars = MagicMock()
                mock_scalars.all.return_value = [mock_txn]
                mock_result.scalars.return_value = mock_scalars
            return mock_result

        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        mock_session.commit = AsyncMock()

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=False)

        with patch("src.services.pipeline.async_session_maker", return_value=mock_context):
            await run_pipeline(run_id)

        assert mock_run.status == "completed"
        assert mock_run.stages_completed == 6
        assert mock_run.completed_at is not None
        assert mock_run.current_stage is None

    @pytest.mark.asyncio
    async def test_run_pipeline_stops_on_failure(self):
        """Pipeline stops at failed stage and records the error."""
        from src.services.pipeline import run_pipeline

        run_id = uuid.uuid4()
        mock_run = PipelineRun(
            id=run_id,
            user_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            status="pending",
            total_stages=6,
            stages_completed=0,
            stage_results={},
        )

        mock_txn = MagicMock()
        mock_txn.category = None
        mock_txn.description = "TEST"
        mock_txn.amount = Decimal("10.00")
        mock_txn.transaction_date = date(2026, 1, 15)
        mock_txn.id = uuid.uuid4()

        call_count = 0

        async def mock_execute(query, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_result = MagicMock()
            if call_count == 1:
                mock_result.scalar_one_or_none.return_value = mock_run
            elif call_count == 2:
                mock_scalars = MagicMock()
                mock_scalars.all.return_value = [mock_txn]
                mock_result.scalars.return_value = mock_scalars
            return mock_result

        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        mock_session.commit = AsyncMock()

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=False)

        with patch("src.services.pipeline.async_session_maker", return_value=mock_context):
            with patch("src.services.pipeline._execute_stage", side_effect=RuntimeError("API down")):
                await run_pipeline(run_id)

        assert mock_run.status == "failed"
        assert mock_run.error_message == "API down"
        assert mock_run.error_stage == "categorizer"
        assert mock_run.completed_at is not None

    @pytest.mark.asyncio
    async def test_run_pipeline_no_transactions_completes_immediately(self):
        """Pipeline with no transactions completes without running stages."""
        from src.services.pipeline import run_pipeline

        run_id = uuid.uuid4()
        mock_run = PipelineRun(
            id=run_id,
            user_id=uuid.uuid4(),
            source_id=uuid.uuid4(),
            status="pending",
            total_stages=6,
            stages_completed=0,
            stage_results={},
        )

        call_count = 0

        async def mock_execute(query, *args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_result = MagicMock()
            if call_count == 1:
                mock_result.scalar_one_or_none.return_value = mock_run
            elif call_count == 2:
                mock_scalars = MagicMock()
                mock_scalars.all.return_value = []
                mock_result.scalars.return_value = mock_scalars
            return mock_result

        mock_session = AsyncMock()
        mock_session.execute = mock_execute
        mock_session.commit = AsyncMock()

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_context.__aexit__ = AsyncMock(return_value=False)

        with patch("src.services.pipeline.async_session_maker", return_value=mock_context):
            await run_pipeline(run_id)

        assert mock_run.status == "completed"
        assert "No transactions" in mock_run.error_message
