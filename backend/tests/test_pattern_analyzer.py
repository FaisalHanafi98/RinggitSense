"""
RinggitSense - Unit tests for AG-03 Pattern Analyzer Agent.

TDD: Tests written FIRST, then implementation.
Tests pattern detection across 5 types:
  TEMPORAL    (weekend surges, payday effects, day-of-month clustering)
  BUNDLE      (co-occurring expenses — commute, night-out bundles)
  HIDDEN_COST (toll aggregation, subscription creep, delivery fees)
  TREND       (rising/falling category spend over time)
  ANOMALY     (large one-off expenses, merchant concentration)
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.schemas.agents.enums import PatternType

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def _mock_api_response(text: str):
    """Create a mock Anthropic message response."""
    mock_content = MagicMock()
    mock_content.text = text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.usage = MagicMock(input_tokens=200, output_tokens=300)
    return mock_message


def _sample_transactions() -> list[dict]:
    """Return a minimal set of categorized transactions for testing."""
    return [
        {"id": "t1", "date": "2026-01-04", "category": "TRANSPORT", "subcategory": "toll", "amount": 3.20, "description": "PLUS TOLL"},
        {"id": "t2", "date": "2026-01-04", "category": "FOOD", "amount": 12.00, "description": "STARBUCKS"},
        {"id": "t3", "date": "2026-01-05", "category": "TRANSPORT", "subcategory": "toll", "amount": 3.20, "description": "PLUS TOLL"},
        {"id": "t4", "date": "2026-01-05", "category": "FOOD", "amount": 11.50, "description": "ZUS COFFEE"},
        {"id": "t5", "date": "2026-01-06", "category": "BILLS", "amount": 54.90, "description": "NETFLIX MALAYSIA"},
        {"id": "t6", "date": "2026-01-26", "category": "SHOPPING", "amount": 350.00, "description": "SHOPEE MALAYSIA"},
        {"id": "t7", "date": "2026-02-26", "category": "SHOPPING", "amount": 410.00, "description": "SHOPEE MALAYSIA"},
        {"id": "t8", "date": "2026-03-26", "category": "SHOPPING", "amount": 490.00, "description": "SHOPEE MALAYSIA"},
    ]


# ─── Agent Properties ─────────────────────────────────────────────────


class TestPatternAnalyzerProperties:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_agent_id(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        assert agent.AGENT_ID == "AG-03"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_agent_name(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        assert agent.AGENT_NAME == "Pattern Analyzer"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_temperature(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        assert agent.TEMPERATURE == 0.5

    @patch("src.agents.base.anthropic.Anthropic")
    def test_system_prompt_contains_all_pattern_types(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        prompt = agent.get_system_prompt()
        for pattern_type in ["TEMPORAL", "BUNDLE", "HIDDEN_COST", "TREND", "ANOMALY"]:
            assert pattern_type in prompt, f"{pattern_type} missing from system prompt"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_system_prompt_contains_malaysian_context(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        prompt = agent.get_system_prompt()
        assert "PLUS" in prompt or "toll" in prompt.lower()
        assert "Grab" in prompt or "GrabFood" in prompt
        assert "Netflix" in prompt or "subscription" in prompt.lower()

    @patch("src.agents.base.anthropic.Anthropic")
    def test_system_prompt_forbids_advice_and_prediction(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        prompt = agent.get_system_prompt()
        # Spec: MUST NOT provide financial advice or predictions
        assert "MUST NOT" in prompt or "must not" in prompt.lower()


# ─── HIDDEN_COST Pattern Detection ───────────────────────────────────


class TestHiddenCostDetection:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_subscription_hidden_cost(self, mock_cls):
        """Monthly subscriptions (Netflix, Spotify) flagged as HIDDEN_COST."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "HIDDEN_COST",
                    "name": "Subscription Creep",
                    "description": "You have 3 recurring digital subscriptions totalling RM183.80/month",
                    "evidence": ["NETFLIX MALAYSIA RM54.90", "SPOTIFY RM17.90", "CELCOM POSTPAID RM79.00"],
                    "impact": 183.80,
                    "confidence": 0.92,
                }
            ],
            "summary": "Subscription services account for RM183.80/month of hidden recurring costs.",
            "hidden_cost_total": 183.80,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
            focus_areas=["hidden_costs"],
        )

        assert len(result.patterns) == 1
        assert result.patterns[0].type == PatternType.HIDDEN_COST
        assert result.patterns[0].impact > 0
        assert result.patterns[0].confidence >= 0.70
        assert result.hidden_cost_total > 0

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_toll_hidden_cost(self, mock_cls):
        """Daily toll charges aggregated as HIDDEN_COST."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "HIDDEN_COST",
                    "name": "Daily Toll Underestimation",
                    "description": "Toll expenses total RM192/month across PLUS and LDP highways",
                    "evidence": ["60 toll transactions", "RM3.20 avg per trip", "Weekday commute pattern"],
                    "impact": 192.00,
                    "confidence": 0.95,
                }
            ],
            "summary": "Daily commute toll costs RM192/month — likely higher than your estimate.",
            "hidden_cost_total": 192.00,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
        )

        assert result.patterns[0].type == PatternType.HIDDEN_COST
        assert result.patterns[0].impact >= 50.0
        assert result.hidden_cost_total >= 50.0

    @patch("src.agents.base.anthropic.Anthropic")
    def test_recurring_monthly_detected_as_hidden_cost(self, mock_cls):
        """Identical monthly transaction is classified as recurring HIDDEN_COST pattern."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "HIDDEN_COST",
                    "name": "Recurring Monthly Subscription",
                    "description": "NETFLIX MALAYSIA charged RM54.90 every month for 3 months",
                    "evidence": ["2026-01-06 RM54.90", "2026-02-06 RM54.90", "2026-03-06 RM54.90"],
                    "impact": 54.90,
                    "confidence": 0.97,
                }
            ],
            "summary": "1 recurring monthly subscription detected.",
            "hidden_cost_total": 54.90,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=[
                {"id": "t1", "date": "2026-01-06", "category": "BILLS", "amount": 54.90, "description": "NETFLIX MALAYSIA"},
                {"id": "t2", "date": "2026-02-06", "category": "BILLS", "amount": 54.90, "description": "NETFLIX MALAYSIA"},
                {"id": "t3", "date": "2026-03-06", "category": "BILLS", "amount": 54.90, "description": "NETFLIX MALAYSIA"},
            ],
            period="3_months",
        )

        assert len(result.patterns) >= 1
        hidden = [p for p in result.patterns if p.type == PatternType.HIDDEN_COST]
        assert len(hidden) >= 1
        assert hidden[0].confidence >= 0.80


# ─── TEMPORAL Pattern Detection ──────────────────────────────────────


class TestTemporalPatternDetection:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_payday_spending_surge(self, mock_cls):
        """Spending spike after salary credit on 25th-28th flagged as TEMPORAL."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "TEMPORAL",
                    "name": "Payday Spending Surge",
                    "description": "Spending jumps 3x on days 26-28 of each month after salary credit",
                    "evidence": [
                        "Jan 26-28: RM850 spent vs RM280 avg other days",
                        "Feb 26-28: RM920 spent",
                        "Mar 26-28: RM790 spent",
                    ],
                    "impact": 1830.00,
                    "confidence": 0.88,
                }
            ],
            "summary": "Payday surge: spending spikes 3x on days 26-28 each month.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
        )

        temporal = [p for p in result.patterns if p.type == PatternType.TEMPORAL]
        assert len(temporal) >= 1
        assert temporal[0].confidence >= 0.70

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_weekend_spending_surge(self, mock_cls):
        """Higher weekend spend compared to weekday flagged as TEMPORAL."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "TEMPORAL",
                    "name": "Weekend Spending Surge",
                    "description": "You spend 2.3x more on weekends (Fri-Sun) vs weekdays",
                    "evidence": ["Weekday avg: RM45", "Weekend avg: RM104", "Entertainment + dining driven"],
                    "impact": 472.00,
                    "confidence": 0.91,
                }
            ],
            "summary": "Weekend spending is 2.3x higher than weekday average.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
        )

        temporal = [p for p in result.patterns if p.type == PatternType.TEMPORAL]
        assert len(temporal) >= 1
        assert temporal[0].impact > 0


# ─── BUNDLE Pattern Detection ─────────────────────────────────────────


class TestBundleDetection:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_morning_commute_bundle(self, mock_cls):
        """Toll + coffee co-occurring on weekday mornings flagged as BUNDLE."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "BUNDLE",
                    "name": "Morning Commute Bundle",
                    "description": "Toll + coffee co-occur on 85% of weekdays within 30-minute windows",
                    "evidence": ["Toll at 7:30-8:30 AM", "Coffee within 30 min", "22 occurrences/month"],
                    "impact": 428.00,
                    "confidence": 0.88,
                }
            ],
            "summary": "Morning commute bundle costs RM428/month when toll + coffee are combined.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
        )

        bundles = [p for p in result.patterns if p.type == PatternType.BUNDLE]
        assert len(bundles) >= 1
        assert bundles[0].confidence >= 0.70
        assert len(bundles[0].evidence) >= 1


# ─── TREND Pattern Detection ──────────────────────────────────────────


class TestTrendDetection:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_rising_shopping_trend(self, mock_cls):
        """Month-over-month increase in shopping spend flagged as TREND."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "TREND",
                    "name": "Rising Shopping Spend",
                    "description": "Shopee spending increased 40% over 3 months",
                    "evidence": ["Jan: RM350", "Feb: RM410", "Mar: RM490"],
                    "impact": 140.00,
                    "confidence": 0.85,
                }
            ],
            "summary": "Shopping spend trending up 40% — driven by Shopee purchases.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
        )

        trends = [p for p in result.patterns if p.type == PatternType.TREND]
        assert len(trends) >= 1
        assert trends[0].confidence >= 0.70


# ─── ANOMALY Pattern Detection ────────────────────────────────────────


class TestAnomalyDetection:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_large_one_off_expense(self, mock_cls):
        """Unusually large single transaction flagged as ANOMALY."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "ANOMALY",
                    "name": "Unusual Healthcare Expense",
                    "description": "KPJ SPECIALIST HOSPITAL charge of RM280 is 6x your typical healthcare spend",
                    "evidence": ["RM280 on 2026-01-15", "Healthcare avg: RM45/month"],
                    "impact": 280.00,
                    "confidence": 0.87,
                }
            ],
            "summary": "One unusual healthcare expense detected — 6x above your typical monthly healthcare cost.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=[
                {"id": "t1", "date": "2026-01-15", "category": "HEALTHCARE", "amount": 280.00, "description": "KPJ SPECIALIST HOSPITAL"},
                {"id": "t2", "date": "2026-01-20", "category": "FOOD", "amount": 25.00, "description": "MCDONALD'S"},
            ],
            period="3_months",
        )

        anomalies = [p for p in result.patterns if p.type == PatternType.ANOMALY]
        assert len(anomalies) >= 1
        assert anomalies[0].impact > 0

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detects_merchant_concentration(self, mock_cls):
        """Single category dominating 40%+ of spend flagged as ANOMALY."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "ANOMALY",
                    "name": "High Category Concentration",
                    "description": "SHOPPING accounts for 62% of total spend — unusually high single-category dominance",
                    "evidence": ["SHOPPING: RM1250 of RM2010 total", "Mainly Shopee purchases"],
                    "impact": 1250.00,
                    "confidence": 0.89,
                }
            ],
            "summary": "Your spending is heavily concentrated in SHOPPING (62%) — consider reviewing.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
        )

        assert len(result.patterns) >= 1
        anomalies = [p for p in result.patterns if p.type == PatternType.ANOMALY]
        assert len(anomalies) >= 1


# ─── Edge Cases ────────────────────────────────────────────────────────


class TestEdgeCases:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_empty_transaction_list_returns_empty_patterns(self, mock_cls):
        """Zero-transaction input returns empty patterns list without crashing."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [],
            "summary": "No transactions provided — no patterns detected.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(transactions=[], period="available")

        assert result.patterns == []
        assert result.hidden_cost_total == 0.0
        assert len(result.summary) > 0

    @patch("src.agents.base.anthropic.Anthropic")
    def test_invalid_json_from_api_raises_value_error(self, mock_cls):
        """Unparseable API response raises ValueError from BaseAgent."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            "Sorry, I cannot analyze these transactions right now."
        )

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        with pytest.raises(ValueError, match="Could not parse JSON"):
            agent.analyze(transactions=_sample_transactions(), period="3_months")

    @patch("src.agents.base.anthropic.Anthropic")
    def test_single_transaction_does_not_crash(self, mock_cls):
        """Sparse data (1 transaction) handled gracefully."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [],
            "summary": "Insufficient data for pattern detection — only 1 transaction provided.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=[
                {"id": "t1", "date": "2026-01-04", "category": "FOOD", "amount": 15.00, "description": "WATSONS"},
            ],
            period="available",
        )

        assert isinstance(result.patterns, list)
        assert result.hidden_cost_total >= 0.0


# ─── Debt-Coupled Pattern (AG-02 context passthrough) ────────────────


class TestDebtCoupledPattern:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_accepts_debt_signals_as_input(self, mock_cls):
        """analyze() accepts optional debt_signals from AG-02 without error."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "ANOMALY",
                    "name": "BNPL Purchase Spike",
                    "description": "Shopee purchases on payday correlate with SPayLater activations",
                    "evidence": ["RM350 Shopee on Jan 26", "SPayLater activation same day"],
                    "impact": 350.00,
                    "confidence": 0.82,
                }
            ],
            "summary": "BNPL usage correlates with payday shopping spikes.",
            "hidden_cost_total": 0.0,
        }))

        mock_debt_signals = {
            "status": "completed",
            "detected": 2,
            "total": 8,
            "results": [
                {"id": "t6", "is_debt_related": True, "debt_tier": "BNPL", "provider": "SPayLater"},
                {"id": "t7", "is_debt_related": True, "debt_tier": "BNPL", "provider": "SPayLater"},
            ],
        }

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
            debt_signals=mock_debt_signals,
        )

        assert len(result.patterns) >= 1

    @patch("src.agents.base.anthropic.Anthropic")
    def test_debt_signals_included_in_api_call(self, mock_cls):
        """debt_signals are passed to the Claude API call when provided."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [],
            "summary": "No additional patterns beyond debt signals.",
            "hidden_cost_total": 0.0,
        }))

        debt_signals = {"detected": 1, "results": [{"id": "t1", "debt_tier": "BNPL"}]}

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        agent.analyze(
            transactions=_sample_transactions(),
            period="3_months",
            debt_signals=debt_signals,
        )

        call_args = mock_client.messages.create.call_args
        user_message_content = call_args.kwargs["messages"][0]["content"]
        assert "debt_context" in user_message_content


# ─── Output Schema Validation ─────────────────────────────────────────


class TestOutputSchemaValidation:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_confidence_within_valid_range(self, mock_cls):
        """Every pattern in the result has confidence in [0.0, 1.0]."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "TEMPORAL",
                    "name": "Weekend Surge",
                    "description": "Weekend spending is higher",
                    "evidence": ["Higher Fri-Sun spend"],
                    "impact": 100.0,
                    "confidence": 0.85,
                }
            ],
            "summary": "Weekend spending surge detected.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(transactions=_sample_transactions(), period="3_months")

        for pattern in result.patterns:
            assert 0.0 <= pattern.confidence <= 1.0

    @patch("src.agents.base.anthropic.Anthropic")
    def test_hidden_cost_total_is_non_negative(self, mock_cls):
        """hidden_cost_total must be >= 0."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [],
            "summary": "No patterns.",
            "hidden_cost_total": 0.0,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(transactions=[], period="available")

        assert result.hidden_cost_total >= 0.0

    @patch("src.agents.base.anthropic.Anthropic")
    def test_pattern_type_normalization(self, mock_cls):
        """Lowercase pattern types from API are normalized to PatternType enum."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "patterns": [
                {
                    "type": "hidden_cost",  # lowercase — agent must normalize
                    "name": "Subscription Costs",
                    "description": "Subscription spend detected",
                    "evidence": ["Netflix RM54.90"],
                    "impact": 54.90,
                    "confidence": 0.90,
                }
            ],
            "summary": "Hidden subscription cost detected.",
            "hidden_cost_total": 54.90,
        }))

        from src.agents.pattern_analyzer import PatternAnalyzerAgent
        agent = PatternAnalyzerAgent()
        result = agent.analyze(transactions=_sample_transactions(), period="3_months")

        assert result.patterns[0].type == PatternType.HIDDEN_COST


# ─── Golden Dataset Integration ──────────────────────────────────────


class TestGoldenDatasetPatterns:
    """Validate expected_patterns.json structure and coverage."""

    def setup_method(self):
        with open(GOLDEN_DIR / "expected_patterns.json") as f:
            self.expected = json.load(f)

    def test_golden_dataset_has_recurring_expenses(self):
        assert len(self.expected["recurring_expenses"]) >= 3

    def test_golden_dataset_has_spending_trends(self):
        assert len(self.expected["spending_trends"]) >= 1

    def test_golden_dataset_has_anomalies(self):
        assert len(self.expected["anomalies"]) >= 1

    def test_recurring_expenses_have_required_fields(self):
        for expense in self.expected["recurring_expenses"]:
            assert "description" in expense
            assert "frequency" in expense
            assert "source" in expense

    def test_anomalies_have_amounts(self):
        for anomaly in self.expected["anomalies"]:
            assert "amount" in anomaly
            assert anomaly["amount"] > 0

    def test_spending_trends_have_direction(self):
        """Each trend entry has a direction: RISING, STABLE, or FALLING."""
        valid_trends = {"RISING", "STABLE", "FALLING"}
        for trend in self.expected["spending_trends"]:
            assert trend["trend"] in valid_trends

    def test_golden_dataset_covers_malaysian_merchants(self):
        """Golden dataset includes recognizable Malaysian merchants."""
        all_descriptions = [r["description"] for r in self.expected["recurring_expenses"]]
        malaysian_keywords = ["TNB", "UNIFI", "CELCOM", "MAXIS", "ASTRO", "SYABAS", "NETFLIX"]
        found = any(
            any(kw in desc.upper() for kw in malaysian_keywords)
            for desc in all_descriptions
        )
        assert found, "No Malaysian merchant found in recurring_expenses"
