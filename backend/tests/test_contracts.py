"""
RinggitSense - Tests for agent data contracts.

Tests that Pydantic models accept valid data, reject invalid data,
and that the AgentPipeline validates handoffs correctly.
"""
import pytest
from pydantic import ValidationError

from src.schemas.agents.enums import (
    AdviceCategory,
    DebtTier,
    Difficulty,
    PatternType,
    TransactionCategory,
    Trend,
)
from src.schemas.agents.categorizer import (
    CategorizerInput,
    CategorizerOutput,
    CategorizerBatchInput,
    CategorizerBatchOutput,
)
from src.schemas.agents.debt_detector import (
    DebtDetectorInput,
    DebtDetectorOutput,
    DebtSummary,
    DebtTierSummary,
)
from src.schemas.agents.pattern_analyzer import PatternItem, PatternResult
from src.schemas.agents.predictor import (
    CategoryPrediction,
    ConfidenceInterval,
    PredictionResult,
    PredictorInput,
)
from src.schemas.agents.query import QueryContext, QueryInput, QueryResponse
from src.schemas.agents.advisor import (
    AdvisorInput,
    AdviceResponse,
    Recommendation,
    UserProfile,
)
from src.schemas.agents.base import AgentContractViolation
from src.schemas.agents.pipeline import AgentPipeline


# ─── AG-01 Categorizer ──────────────────────────────────────────────


class TestCategorizerContracts:
    def test_valid_input(self):
        inp = CategorizerInput(
            description="GRAB CAR",
            amount=15.50,
            source="maybank",
            date="2026-01-15",
        )
        assert inp.description == "GRAB CAR"
        assert inp.comment is None

    def test_valid_output(self):
        out = CategorizerOutput(
            category=TransactionCategory.TRANSPORT,
            confidence=0.95,
            subcategory="ride_hailing",
            merchant_name="Grab",
            reasoning="Grab is a ride-hailing service",
        )
        assert out.category == TransactionCategory.TRANSPORT

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            CategorizerOutput(
                category="INVALID_CATEGORY",
                confidence=0.9,
                reasoning="test",
            )

    def test_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            CategorizerOutput(
                category=TransactionCategory.FOOD,
                confidence=1.5,
                reasoning="test",
            )

    def test_confidence_negative(self):
        with pytest.raises(ValidationError):
            CategorizerOutput(
                category=TransactionCategory.FOOD,
                confidence=-0.1,
                reasoning="test",
            )

    def test_empty_description_rejected(self):
        with pytest.raises(ValidationError):
            CategorizerInput(
                description="",
                amount=10.0,
                source="cimb",
                date="2026-01-01",
            )

    def test_empty_reasoning_rejected(self):
        with pytest.raises(ValidationError):
            CategorizerOutput(
                category=TransactionCategory.FOOD,
                confidence=0.9,
                reasoning="",
            )

    def test_batch_input_max_50(self):
        items = [
            {"id": f"txn_{i}", "description": "test", "amount": 10.0,
             "source": "maybank", "date": "2026-01-01"}
            for i in range(51)
        ]
        with pytest.raises(ValidationError):
            CategorizerBatchInput(transactions=items)

    def test_batch_output(self):
        out = CategorizerBatchOutput(
            results=[],
            processing_time_ms=500,
            success_count=0,
            error_count=0,
        )
        assert out.processing_time_ms == 500


# ─── AG-02 Debt Detector ────────────────────────────────────────────


class TestDebtDetectorContracts:
    def test_valid_debt_output(self):
        out = DebtDetectorOutput(
            is_debt_related=True,
            debt_tier=DebtTier.FORMAL,
            debt_type="education_loan",
            provider="PTPTN",
            confidence=0.92,
            indicators=["Monthly fixed amount", "PTPTN keyword"],
        )
        assert out.debt_tier == DebtTier.FORMAL

    def test_non_debt_output(self):
        out = DebtDetectorOutput(
            is_debt_related=False,
            confidence=0.85,
        )
        assert out.debt_tier is None
        assert out.indicators == []

    def test_invalid_debt_tier(self):
        with pytest.raises(ValidationError):
            DebtDetectorOutput(
                is_debt_related=True,
                debt_tier="UNKNOWN_TIER",
                confidence=0.8,
            )

    def test_debt_summary(self):
        summary = DebtSummary(
            formal=DebtTierSummary(
                count=2, providers=["PTPTN", "CIMB"],
                estimated_monthly_total=800.0, estimated_total=50000.0,
            ),
            bnpl=DebtTierSummary(
                count=1, providers=["SPayLater"],
                estimated_monthly_total=166.66, estimated_total=500.0,
            ),
            hutang=DebtTierSummary(
                count=0, estimated_monthly_total=0.0, estimated_total=0.0,
            ),
            total_monthly_debt_obligation=966.66,
        )
        assert summary.formal.count == 2


# ─── AG-03 Pattern Analyzer ─────────────────────────────────────────


class TestPatternContracts:
    def test_valid_pattern_result(self):
        result = PatternResult(
            patterns=[
                PatternItem(
                    type=PatternType.HIDDEN_COST,
                    name="Delivery Fees",
                    description="Recurring delivery charges from food apps",
                    evidence=["txn_001", "txn_042"],
                    impact=45.0,
                    confidence=0.88,
                )
            ],
            summary="Found 1 hidden cost pattern",
            hidden_cost_total=45.0,
        )
        assert len(result.patterns) == 1

    def test_invalid_pattern_type(self):
        with pytest.raises(ValidationError):
            PatternItem(
                type="NOT_A_PATTERN",
                name="test",
                description="test",
                evidence=[],
                impact=0.0,
                confidence=0.5,
            )


# ─── AG-04 Predictor ────────────────────────────────────────────────


class TestPredictorContracts:
    def test_valid_prediction(self):
        result = PredictionResult(
            total_predicted=2500.0,
            confidence_interval=ConfidenceInterval(low=2100.0, high=2900.0),
            by_category=[
                CategoryPrediction(
                    category="FOOD", predicted=800.0, trend=Trend.STABLE
                ),
            ],
            assumptions=["Based on 3 months history"],
            risks=["Hari Raya spending spike possible"],
        )
        assert result.total_predicted == 2500.0

    def test_valid_input(self):
        inp = PredictorInput(
            historical_transactions=[{"month": "2026-01", "total": 2000}],
            prediction_month="2026-03",
        )
        assert inp.known_upcoming is None


# ─── AG-05 Query ─────────────────────────────────────────────────────


class TestQueryContracts:
    def test_valid_query(self):
        inp = QueryInput(
            question="Berapa saya belanja makan bulan lepas?",
            context=QueryContext(
                transactions=[],
                date_range={"start": "2026-01-01", "end": "2026-01-31"},
            ),
        )
        assert inp.context.user_locale == "en-MY"

    def test_empty_question_rejected(self):
        with pytest.raises(ValidationError):
            QueryInput(
                question="",
                context=QueryContext(
                    transactions=[],
                    date_range={"start": "2026-01-01", "end": "2026-01-31"},
                ),
            )

    def test_valid_response(self):
        resp = QueryResponse(
            answer="Anda belanja RM800 untuk makanan bulan lepas.",
            follow_up_questions=["What about transport?"],
        )
        assert resp.routed_to is None


# ─── AG-06 Advisor ───────────────────────────────────────────────────


class TestAdvisorContracts:
    def test_valid_advice(self):
        resp = AdviceResponse(
            recommendations=[
                Recommendation(
                    priority=1,
                    category=AdviceCategory.DEBT,
                    title="Pay off BNPL first",
                    description="Your BNPL has the highest effective interest",
                    potential_impact=50.0,
                    difficulty=Difficulty.EASY,
                    action_steps=["Open SPayLater app", "Pay remaining balance"],
                )
            ],
            disclaimer="This is not professional financial advice.",
            overall_assessment="Your spending is within budget.",
        )
        assert len(resp.recommendations) == 1

    def test_missing_disclaimer_rejected(self):
        with pytest.raises(ValidationError):
            AdviceResponse(
                recommendations=[],
                disclaimer="",
                overall_assessment="Good",
            )

    def test_priority_out_of_range(self):
        with pytest.raises(ValidationError):
            Recommendation(
                priority=6,
                category=AdviceCategory.SPENDING,
                title="test",
                description="test",
                potential_impact=10.0,
                difficulty=Difficulty.EASY,
                action_steps=["do something"],
            )


# ─── Pipeline ────────────────────────────────────────────────────────


class TestAgentPipeline:
    def test_valid_handoff(self):
        pipeline = AgentPipeline()
        data = {
            "category": "FOOD",
            "confidence": 0.95,
            "subcategory": "restaurant",
            "merchant_name": "Nasi Kandar Pelita",
            "reasoning": "Malaysian restaurant chain",
        }
        result = pipeline.validate_handoff("AG-01", "AG-02", data)
        assert result.category == TransactionCategory.FOOD
        assert len(pipeline.get_history()) == 1
        assert pipeline.get_history()[0].success is True

    def test_invalid_handoff_raises(self):
        pipeline = AgentPipeline()
        data = {"category": "INVALID", "confidence": 2.0}
        with pytest.raises(AgentContractViolation):
            pipeline.validate_handoff("AG-01", "AG-02", data)
        assert len(pipeline.get_history()) == 1
        assert pipeline.get_history()[0].success is False

    def test_unknown_handoff_raises(self):
        pipeline = AgentPipeline()
        with pytest.raises(AgentContractViolation, match="No contract defined"):
            pipeline.validate_handoff("AG-99", "AG-100", {})

    def test_reset_clears_history(self):
        pipeline = AgentPipeline()
        data = {
            "category": "FOOD",
            "confidence": 0.9,
            "reasoning": "test",
        }
        pipeline.validate_handoff("AG-01", "AG-02", data)
        assert len(pipeline.get_history()) == 1
        pipeline.reset()
        assert len(pipeline.get_history()) == 0

    def test_contract_violation_attributes(self):
        exc = AgentContractViolation("AG-01", "AG-02", "bad data")
        assert exc.from_agent == "AG-01"
        assert exc.to_agent == "AG-02"
        assert "bad data" in str(exc)
