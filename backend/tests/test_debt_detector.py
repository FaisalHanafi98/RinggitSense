"""
RinggitSense - Unit tests for AG-02 Debt Detector Agent.

TDD: Tests written FIRST, then implementation.
Tests the agent's debt classification across three tiers:
  FORMAL (bank loans, PTPTN, hire purchase)
  BNPL (SPayLater, GrabPayLater, Atome)
  HUTANG (informal borrowing — pinjam, hutang, bayar balik)
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.schemas.agents.enums import DebtTier

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


def _mock_api_response(text: str):
    """Create a mock Anthropic message response."""
    mock_content = MagicMock()
    mock_content.text = text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.usage = MagicMock(input_tokens=150, output_tokens=80)
    return mock_message


# ─── Agent Properties ─────────────────────────────────────────────────


class TestDebtDetectorProperties:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_agent_id(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        assert agent.AGENT_ID == "AG-02"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_agent_name(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        assert agent.AGENT_NAME == "Debt Detector"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_temperature(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        assert agent.TEMPERATURE == 0.1

    @patch("src.agents.base.anthropic.Anthropic")
    def test_system_prompt_contains_three_tiers(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        prompt = agent.get_system_prompt()
        assert "FORMAL" in prompt
        assert "BNPL" in prompt
        assert "HUTANG" in prompt

    @patch("src.agents.base.anthropic.Anthropic")
    def test_system_prompt_contains_malaysian_context(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        prompt = agent.get_system_prompt()
        assert "PTPTN" in prompt
        assert "SPayLater" in prompt
        assert "hutang" in prompt.lower()


# ─── FORMAL Tier Detection ───────────────────────────────────────────


class TestDetectFormalDebt:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_formal_debt_ptptn(self, mock_cls):
        """PTPTN loan payment -> FORMAL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "FORMAL",
            "debt_type": "education_loan",
            "provider": "PTPTN",
            "confidence": 0.98,
            "indicators": ["PTPTN", "REPAYMENT"],
            "estimated_monthly": 250.00,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="PTPTN REPAYMENT",
            amount=250.00,
            source="Maybank",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.FORMAL
        assert result.debt_type == "education_loan"
        assert result.provider == "PTPTN"
        assert result.confidence >= 0.90

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_formal_debt_car_loan(self, mock_cls):
        """Car loan installment -> FORMAL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "FORMAL",
            "debt_type": "hire_purchase",
            "provider": "Maybank",
            "confidence": 0.97,
            "indicators": ["HIRE PURCHASE"],
            "estimated_monthly": 850.00,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="MAYBANK HIRE PURCHASE",
            amount=850.00,
            source="Maybank",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.FORMAL
        assert result.debt_type == "hire_purchase"
        assert result.confidence >= 0.90

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_formal_debt_housing_loan(self, mock_cls):
        """Housing loan -> FORMAL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "FORMAL",
            "debt_type": "housing_loan",
            "provider": "CIMB",
            "confidence": 0.98,
            "indicators": ["HOUSING LOAN"],
            "estimated_monthly": 1200.00,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="CIMB HOUSING LOAN",
            amount=1200.00,
            source="CIMB",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.FORMAL
        assert result.provider == "CIMB"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_formal_debt_asb_financing(self, mock_cls):
        """ASB financing -> FORMAL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "FORMAL",
            "debt_type": "investment_loan",
            "provider": "ASB",
            "confidence": 0.95,
            "indicators": ["ASB FINANCING", "PAYMENT"],
            "estimated_monthly": 200.00,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="ASB FINANCING PAYMENT",
            amount=200.00,
            source="Maybank",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.FORMAL


# ─── BNPL Tier Detection ─────────────────────────────────────────────


class TestDetectBNPL:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_bnpl_atome(self, mock_cls):
        """Atome payment -> BNPL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "BNPL",
            "debt_type": "installment",
            "provider": "Atome",
            "confidence": 0.94,
            "indicators": ["ATOME", "PAYMENT", "2/3"],
            "estimated_monthly": 66.33,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="ATOME PAYMENT 2/3",
            amount=66.33,
            source="Maybank",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.BNPL
        assert result.provider == "Atome"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_bnpl_spaylater(self, mock_cls):
        """SPayLater -> BNPL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "BNPL",
            "debt_type": "installment",
            "provider": "SPayLater",
            "confidence": 0.95,
            "indicators": ["SPAYLATER", "INSTALLMENT"],
            "estimated_monthly": 89.90,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="SPAYLATER INSTALLMENT",
            amount=89.90,
            source="Maybank",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.BNPL
        assert result.provider == "SPayLater"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_bnpl_grabpaylater(self, mock_cls):
        """GrabPayLater -> BNPL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "BNPL",
            "debt_type": "installment",
            "provider": "GrabPayLater",
            "confidence": 0.94,
            "indicators": ["GRABPAYLATER", "1/3"],
            "estimated_monthly": 33.33,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="GRABPAYLATER 1/3",
            amount=33.33,
            source="CIMB",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.BNPL

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_bnpl_hoolah(self, mock_cls):
        """Hoolah -> BNPL tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "BNPL",
            "debt_type": "installment",
            "provider": "Hoolah",
            "confidence": 0.93,
            "indicators": ["HOOLAH", "INSTALLMENT"],
            "estimated_monthly": 75.00,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="HOOLAH INSTALLMENT 1/4",
            amount=75.00,
            source="Maybank",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.BNPL
        assert result.provider == "Hoolah"


# ─── HUTANG (Informal) Tier Detection ────────────────────────────────


class TestDetectHutang:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_hutang_informal(self, mock_cls):
        """'bayar hutang Kamal' -> HUTANG tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "HUTANG",
            "debt_type": "informal_repayment",
            "provider": None,
            "confidence": 0.85,
            "indicators": ["BAYAR", "HUTANG"],
            "estimated_monthly": None,
            "person_name": "Kamal",
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="BAYAR HUTANG KAMAL",
            amount=80.00,
            source="CIMB",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.HUTANG
        assert result.person_name == "Kamal"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_detect_hutang_pinjam(self, mock_cls):
        """'pinjam duit Ahmad' -> HUTANG tier."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "HUTANG",
            "debt_type": "informal_loan",
            "provider": None,
            "confidence": 0.82,
            "indicators": ["PINJAM", "DUIT"],
            "estimated_monthly": None,
            "person_name": "Ahmad",
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="PINJAM DUIT AHMAD",
            amount=300.00,
            source="Maybank",
        )

        assert result.is_debt_related is True
        assert result.debt_tier == DebtTier.HUTANG
        assert result.person_name == "Ahmad"


# ─── Non-Debt (Negative Cases) ───────────────────────────────────────


class TestNonDebt:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_no_debt_regular_expense(self, mock_cls):
        """Regular grocery -> not debt."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": False,
            "debt_tier": None,
            "debt_type": None,
            "provider": None,
            "confidence": 0.95,
            "indicators": [],
            "estimated_monthly": None,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="JAYA GROCER MID VALLEY",
            amount=156.80,
            source="Maybank",
        )

        assert result.is_debt_related is False
        assert result.debt_tier is None

    @patch("src.agents.base.anthropic.Anthropic")
    def test_no_debt_salary(self, mock_cls):
        """Salary deposit -> not debt."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": False,
            "debt_tier": None,
            "debt_type": None,
            "provider": None,
            "confidence": 0.98,
            "indicators": [],
            "estimated_monthly": None,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="SALARY JAN 2026",
            amount=5500.00,
            source="Maybank",
        )

        assert result.is_debt_related is False
        assert result.debt_tier is None

    @patch("src.agents.base.anthropic.Anthropic")
    def test_no_debt_toll(self, mock_cls):
        """Toll payment -> not debt."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": False,
            "debt_tier": None,
            "debt_type": None,
            "provider": None,
            "confidence": 0.97,
            "indicators": [],
            "estimated_monthly": None,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="PLUS TOLL PLZ SUBANG",
            amount=3.20,
            source="TnG",
        )

        assert result.is_debt_related is False


# ─── Batch Detection ─────────────────────────────────────────────────


class TestBatchDetection:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_batch_detection_mixed(self, mock_cls):
        """Multiple transactions, mixed debt/non-debt."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "results": [
                {
                    "id": "txn_1",
                    "is_debt_related": True,
                    "debt_tier": "FORMAL",
                    "debt_type": "education_loan",
                    "provider": "PTPTN",
                    "confidence": 0.98,
                    "indicators": ["PTPTN"],
                    "estimated_monthly": 250.00,
                    "person_name": None,
                },
                {
                    "id": "txn_2",
                    "is_debt_related": False,
                    "debt_tier": None,
                    "debt_type": None,
                    "provider": None,
                    "confidence": 0.95,
                    "indicators": [],
                    "estimated_monthly": None,
                    "person_name": None,
                },
                {
                    "id": "txn_3",
                    "is_debt_related": True,
                    "debt_tier": "BNPL",
                    "debt_type": "installment",
                    "provider": "Atome",
                    "confidence": 0.93,
                    "indicators": ["ATOME"],
                    "estimated_monthly": 66.33,
                    "person_name": None,
                },
            ]
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect_batch([
            {"id": "txn_1", "description": "PTPTN REPAYMENT", "amount": 250.00, "source": "Maybank"},
            {"id": "txn_2", "description": "MCDONALD'S", "amount": 25.90, "source": "Maybank"},
            {"id": "txn_3", "description": "ATOME PAYMENT 2/3", "amount": 66.33, "source": "Maybank"},
        ])

        assert result.success_count == 3
        assert result.error_count == 0
        # First result: debt
        assert result.results[0].is_debt_related is True
        assert result.results[0].debt_tier == DebtTier.FORMAL
        # Second result: not debt
        assert result.results[1].is_debt_related is False
        # Third result: BNPL
        assert result.results[2].is_debt_related is True
        assert result.results[2].debt_tier == DebtTier.BNPL

    @patch("src.agents.base.anthropic.Anthropic")
    def test_batch_exceeds_50_raises(self, mock_cls):
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        with pytest.raises(ValueError, match="50"):
            agent.detect_batch([{"id": f"txn_{i}"} for i in range(51)])


# ─── Confidence Scoring ──────────────────────────────────────────────


class TestConfidenceScoring:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_confidence_above_threshold_for_clear_debt(self, mock_cls):
        """Clear debt cases should have confidence > 0.70."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": True,
            "debt_tier": "FORMAL",
            "debt_type": "education_loan",
            "provider": "PTPTN",
            "confidence": 0.98,
            "indicators": ["PTPTN", "REPAYMENT"],
            "estimated_monthly": 250.00,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="PTPTN REPAYMENT",
            amount=250.00,
            source="Maybank",
        )

        assert result.confidence > 0.70

    @patch("src.agents.base.anthropic.Anthropic")
    def test_confidence_valid_range(self, mock_cls):
        """Confidence must be 0.0 to 1.0."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "is_debt_related": False,
            "debt_tier": None,
            "debt_type": None,
            "provider": None,
            "confidence": 0.95,
            "indicators": [],
            "estimated_monthly": None,
            "person_name": None,
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect(
            description="MCDONALD'S SUNWAY PYRAMID",
            amount=25.90,
            source="Maybank",
        )

        assert 0.0 <= result.confidence <= 1.0


# ─── Debt Grouping ───────────────────────────────────────────────────


class TestDebtGrouping:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_debt_grouping_same_provider(self, mock_cls):
        """Multiple PTPTN payments should be recognized as same debt group."""
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(json.dumps({
            "results": [
                {
                    "id": "txn_1",
                    "is_debt_related": True,
                    "debt_tier": "FORMAL",
                    "debt_type": "education_loan",
                    "provider": "PTPTN",
                    "confidence": 0.98,
                    "indicators": ["PTPTN"],
                    "estimated_monthly": 250.00,
                    "person_name": None,
                },
                {
                    "id": "txn_2",
                    "is_debt_related": True,
                    "debt_tier": "FORMAL",
                    "debt_type": "education_loan",
                    "provider": "PTPTN",
                    "confidence": 0.98,
                    "indicators": ["PTPTN"],
                    "estimated_monthly": 250.00,
                    "person_name": None,
                },
            ]
        }))

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        result = agent.detect_batch([
            {"id": "txn_1", "description": "PTPTN REPAYMENT", "amount": 250.00, "source": "Maybank"},
            {"id": "txn_2", "description": "PTPTN REPAYMENT", "amount": 250.00, "source": "Maybank"},
        ])

        # Both should be same provider and tier — groupable
        assert result.results[0].provider == result.results[1].provider
        assert result.results[0].debt_tier == result.results[1].debt_tier


# ─── Malaysian Context ───────────────────────────────────────────────


class TestMalaysianContext:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_malaysian_bnpl_providers_recognized(self, mock_cls):
        """Malaysian BNPL providers in system prompt."""
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        prompt = agent.get_system_prompt()
        for provider in ["SPayLater", "GrabPayLater", "Atome", "Hoolah"]:
            assert provider in prompt, f"{provider} missing from system prompt"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_malaysian_formal_debt_types_in_prompt(self, mock_cls):
        """Malaysian formal debt types in system prompt."""
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        prompt = agent.get_system_prompt()
        for keyword in ["PTPTN", "ASB", "hire purchase", "housing loan"]:
            assert keyword.lower() in prompt.lower(), f"{keyword} missing from system prompt"

    @patch("src.agents.base.anthropic.Anthropic")
    def test_hutang_keywords_in_prompt(self, mock_cls):
        """Malay informal debt keywords in system prompt."""
        mock_cls.return_value = MagicMock()
        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        prompt = agent.get_system_prompt().lower()
        for keyword in ["pinjam", "hutang", "bayar balik"]:
            assert keyword in prompt, f"'{keyword}' missing from system prompt"


# ─── Error Handling ───────────────────────────────────────────────────


class TestErrorHandling:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_invalid_json_raises_value_error(self, mock_cls):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            "This is not valid JSON"
        )

        from src.agents.debt_detector import DebtDetectorAgent
        agent = DebtDetectorAgent()
        with pytest.raises(ValueError, match="Could not parse JSON"):
            agent.detect(
                description="PTPTN REPAYMENT",
                amount=250.00,
                source="Maybank",
            )


# ─── Golden Dataset Integration ──────────────────────────────────────


class TestGoldenDatasetDebtDetection:
    """Validate expected_debts.json structure and coverage."""

    def setup_method(self):
        with open(GOLDEN_DIR / "expected_debts.json") as f:
            self.expected = json.load(f)

    def test_all_three_tiers_covered(self):
        assert set(self.expected["tiers_covered"]) == {"FORMAL", "BNPL", "HUTANG"}

    def test_debt_transaction_count(self):
        assert self.expected["total_debt_transactions"] >= 30

    def test_non_debt_sample_exists(self):
        assert len(self.expected["non_debt_sample"]) >= 5

    def test_debt_groups_have_required_fields(self):
        for group in self.expected["debt_groups"]:
            assert "group_key" in group
            assert "tier" in group
            assert "transaction_count" in group
            assert group["transaction_count"] >= 1

    def test_formal_tier_has_providers(self):
        summary = self.expected["tier_summary"]["FORMAL"]
        assert summary["count"] >= 3
        assert "PTPTN" in summary["providers"]

    def test_bnpl_tier_has_providers(self):
        summary = self.expected["tier_summary"]["BNPL"]
        assert summary["count"] >= 2
        assert "SPayLater" in summary["providers"]

    def test_hutang_tier_has_people(self):
        summary = self.expected["tier_summary"]["HUTANG"]
        assert summary["count"] >= 1
        assert len(summary["people"]) >= 1

    def test_each_debt_txn_has_indicators(self):
        for txn in self.expected["debt_transactions"]:
            assert len(txn["expected_indicators"]) >= 1
            assert txn["min_confidence"] >= 0.60
