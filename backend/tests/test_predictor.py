"""
RinggitSense - Unit tests for AG-04 Predictor Agent.

TDD: Tests written FIRST, then implementation.
"""
import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from src.schemas.agents.enums import Trend


def _mock_api_response(text: str) -> MagicMock:
    """Create a mock Anthropic message response."""
    mock_content = MagicMock()
    mock_content.text = text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.usage = MagicMock(input_tokens=220, output_tokens=320)
    return mock_message


def _sample_history() -> list[dict]:
    """Synthetic category-month spending summaries for AG-04 tests."""
    return [
        {"month": "2025-10", "category": "FOOD", "total": 850.00},
        {"month": "2025-11", "category": "FOOD", "total": 920.00},
        {"month": "2025-12", "category": "FOOD", "total": 1100.00},
        {"month": "2025-10", "category": "TRANSPORT", "total": 420.00},
        {"month": "2025-11", "category": "TRANSPORT", "total": 450.00},
        {"month": "2025-12", "category": "TRANSPORT", "total": 380.00},
    ]


def _sample_patterns() -> dict:
    """Synthetic AG-03 output passed as context into AG-04."""
    return {
        "status": "completed",
        "pattern_count": 1,
        "hidden_cost_total": 54.90,
        "summary": "Food spending is rising and subscriptions are stable.",
        "patterns": [
            {
                "type": "TREND",
                "name": "Rising Food Spend",
                "impact": 250.00,
                "confidence": 0.84,
            }
        ],
    }


def _valid_prediction_payload() -> dict:
    return {
        "total_predicted": 1850.00,
        "confidence_interval": {"low": 1600.00, "high": 2100.00},
        "by_category": [
            {"category": "FOOD", "predicted": 1080.00, "trend": "RISING"},
            {"category": "TRANSPORT", "predicted": 420.00, "trend": "STABLE"},
            {"category": "BILLS", "predicted": 350.00, "trend": "STABLE"},
        ],
        "assumptions": [
            "Based on synthetic 3-month spending summaries.",
            "Pattern Analyzer context included the rising FOOD trend.",
        ],
        "risks": [
            "Past patterns do not guarantee future results.",
            "Festival timing may change monthly spend.",
        ],
    }


class TestPredictorProperties:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_agent_initialisation_follows_base_agent_pattern(self, mock_cls: MagicMock) -> None:
        mock_cls.return_value = MagicMock()

        from src.agents.predictor import PredictorAgent

        agent = PredictorAgent()

        assert agent.AGENT_ID == "AG-04"
        assert agent.AGENT_NAME == "Predictor"
        assert agent.TEMPERATURE == 0.3
        assert agent.MAX_TOKENS == 4096
        mock_cls.assert_called_once()

    @patch("src.agents.base.anthropic.Anthropic")
    def test_system_prompt_has_scope_boundaries_and_non_advisory_language(
        self,
        mock_cls: MagicMock,
    ) -> None:
        mock_cls.return_value = MagicMock()

        from src.agents.predictor import PredictorAgent

        prompt = PredictorAgent().get_system_prompt()

        assert "YOUR SINGLE RESPONSIBILITY" in prompt
        assert "Forecast next-month spending" in prompt
        assert "MUST NOT" in prompt
        assert "financial advice" in prompt
        assert "Past patterns do not guarantee future results" in prompt


class TestPredictorInvocation:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_valid_mocked_claude_response_parses_to_schema(self, mock_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            json.dumps(_valid_prediction_payload())
        )

        from src.agents.predictor import PredictorAgent

        result = PredictorAgent().predict(
            historical_transactions=_sample_history(),
            prediction_month="2026-01",
            pattern_context=_sample_patterns(),
        )

        assert result.total_predicted == 1850.00
        assert result.confidence_interval.low == 1600.00
        assert result.by_category[0].trend == Trend.RISING
        assert "Past patterns do not guarantee future results." in result.risks

    @patch("src.agents.base.anthropic.Anthropic")
    def test_malformed_claude_response_raises_value_error(self, mock_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            "I need more data before I can forecast."
        )

        from src.agents.predictor import PredictorAgent

        with pytest.raises(ValueError, match="Could not parse JSON"):
            PredictorAgent().predict(
                historical_transactions=_sample_history(),
                prediction_month="2026-01",
            )

    @patch("src.agents.base.anthropic.Anthropic")
    def test_empty_history_is_rejected_before_api_call(self, mock_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client

        from src.agents.predictor import PredictorAgent

        with pytest.raises(ValueError, match="historical_transactions"):
            PredictorAgent().predict(
                historical_transactions=[],
                prediction_month="2026-01",
            )

        mock_client.messages.create.assert_not_called()

    @patch("src.agents.base.anthropic.Anthropic")
    def test_schema_rejects_invalid_confidence_interval(self, mock_cls: MagicMock) -> None:
        payload = _valid_prediction_payload()
        payload["confidence_interval"] = {"low": 2200.00, "high": 1600.00}

        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps(payload))

        from src.agents.predictor import PredictorAgent

        with pytest.raises(ValidationError):
            PredictorAgent().predict(
                historical_transactions=_sample_history(),
                prediction_month="2026-01",
            )

    @patch("src.agents.base.anthropic.Anthropic")
    def test_pattern_context_is_included_in_claude_payload(self, mock_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            json.dumps(_valid_prediction_payload())
        )

        from src.agents.predictor import PredictorAgent

        PredictorAgent().predict(
            historical_transactions=_sample_history(),
            prediction_month="2026-01",
            pattern_context=_sample_patterns(),
        )

        call_args = mock_client.messages.create.call_args
        user_message_content = call_args.kwargs["messages"][0]["content"]
        assert "pattern_context" in user_message_content
        assert "Rising Food Spend" in user_message_content

    @patch("src.agents.base.anthropic.Anthropic")
    def test_no_real_anthropic_call_is_made(self, mock_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            json.dumps(_valid_prediction_payload())
        )

        from src.agents.predictor import PredictorAgent

        PredictorAgent().predict(
            historical_transactions=_sample_history(),
            prediction_month="2026-01",
        )

        mock_client.messages.create.assert_called_once()
