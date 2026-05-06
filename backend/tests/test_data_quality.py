"""
RinggitSense - Tests for data quality validators.

Tests transaction validation (L2-L4) and agent output validation.
"""
from datetime import date, timedelta
from decimal import Decimal

from src.data_quality.agent_output_validator import AgentOutputValidator
from src.data_quality.transaction_validator import (
    DuplicateStatus,
    TransactionValidator,
)
from src.parsers.base import ParsedTransaction, ParserResult, TransactionType
from src.schemas.agents.advisor import AdviceResponse, Recommendation
from src.schemas.agents.categorizer import CategorizerOutput
from src.schemas.agents.debt_detector import DebtDetectorOutput
from src.schemas.agents.enums import (
    AdviceCategory,
    DebtTier,
    Difficulty,
    TransactionCategory,
)

# ─── Helpers ─────────────────────────────────────────────────────────


def _make_txn(
    description: str = "GRAB CAR",
    amount: Decimal = Decimal("15.50"),
    txn_date: date | None = None,
    txn_type: TransactionType = TransactionType.DEBIT,
) -> ParsedTransaction:
    return ParsedTransaction(
        transaction_date=txn_date or date(2026, 1, 15),
        description=description,
        amount=amount,
        transaction_type=txn_type,
    )


# ─── L2: Parse Validation ───────────────────────────────────────────


class TestTransactionValidatorL2:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_valid_transaction(self):
        txn = _make_txn()
        result = self.validator.validate_parsed_transaction(txn)
        assert result.is_valid
        assert result.errors == []

    def test_zero_amount_rejected(self):
        txn = _make_txn(amount=Decimal("0"))
        result = self.validator.validate_parsed_transaction(txn)
        assert not result.is_valid
        assert any("zero" in e.lower() for e in result.errors)

    def test_future_date_rejected(self):
        future = date.today() + timedelta(days=30)
        txn = _make_txn(txn_date=future)
        result = self.validator.validate_parsed_transaction(txn)
        assert not result.is_valid
        assert any("future" in e.lower() for e in result.errors)

    def test_ancient_date_rejected(self):
        txn = _make_txn(txn_date=date(1999, 12, 31))
        result = self.validator.validate_parsed_transaction(txn)
        assert not result.is_valid
        assert any("before" in e.lower() for e in result.errors)

    def test_empty_description_rejected(self):
        txn = _make_txn(description="")
        result = self.validator.validate_parsed_transaction(txn)
        assert not result.is_valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_whitespace_description_rejected(self):
        txn = _make_txn(description="   ")
        result = self.validator.validate_parsed_transaction(txn)
        assert not result.is_valid

    def test_large_amount_warns(self):
        txn = _make_txn(amount=Decimal("200000"))
        result = self.validator.validate_parsed_transaction(txn)
        assert result.is_valid  # Warning, not error
        assert len(result.warnings) > 0

    def test_boundary_date_today_valid(self):
        txn = _make_txn(txn_date=date.today())
        result = self.validator.validate_parsed_transaction(txn)
        assert result.is_valid

    def test_boundary_date_min_valid(self):
        txn = _make_txn(txn_date=date(2000, 1, 1))
        result = self.validator.validate_parsed_transaction(txn)
        assert result.is_valid


# ─── L3: Business Validation ────────────────────────────────────────


class TestTransactionValidatorL3:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_batch_all_valid(self):
        txns = [
            _make_txn(txn_date=date(2026, 1, i + 1))
            for i in range(5)
        ]
        result = self.validator.validate_batch(
            ParserResult(transactions=txns, bank_name="Maybank")
        )
        assert result.all_valid
        assert result.total == 5
        assert result.valid == 5
        assert result.invalid == 0

    def test_batch_with_invalid(self):
        txns = [
            _make_txn(),
            _make_txn(amount=Decimal("0")),  # Invalid
        ]
        result = self.validator.validate_batch(
            ParserResult(transactions=txns, bank_name="Maybank")
        )
        assert not result.all_valid
        assert result.invalid == 1

    def test_out_of_order_warns(self):
        txns = [
            _make_txn(txn_date=date(2026, 1, 15)),
            _make_txn(txn_date=date(2026, 1, 10)),
            _make_txn(txn_date=date(2026, 1, 20)),
        ]
        result = self.validator.validate_batch(
            ParserResult(transactions=txns, bank_name="Maybank")
        )
        assert any("chronological" in w.lower() for w in result.batch_warnings)

    def test_chronological_order_no_warning(self):
        txns = [
            _make_txn(txn_date=date(2026, 1, 1)),
            _make_txn(txn_date=date(2026, 1, 5)),
            _make_txn(txn_date=date(2026, 1, 10)),
        ]
        result = self.validator.validate_batch(
            ParserResult(transactions=txns, bank_name="Maybank")
        )
        assert not any("chronological" in w.lower() for w in result.batch_warnings)

    def test_balance_mismatch_warns(self):
        txns = [
            _make_txn(amount=Decimal("100"), txn_type=TransactionType.DEBIT),
        ]
        result = self.validator.validate_batch(
            ParserResult(
                transactions=txns,
                bank_name="Maybank",
                opening_balance=Decimal("1000"),
                closing_balance=Decimal("999"),  # Should be 900
            )
        )
        assert any("balance" in w.lower() for w in result.batch_warnings)

    def test_balance_match_no_warning(self):
        txns = [
            _make_txn(amount=Decimal("100"), txn_type=TransactionType.DEBIT),
        ]
        result = self.validator.validate_batch(
            ParserResult(
                transactions=txns,
                bank_name="Maybank",
                opening_balance=Decimal("1000"),
                closing_balance=Decimal("900"),
            )
        )
        assert not any("balance" in w.lower() for w in result.batch_warnings)


# ─── L4: Deduplication ──────────────────────────────────────────────


class TestDuplicateDetection:
    def setup_method(self):
        self.validator = TransactionValidator()

    def test_unique_transaction(self):
        txn = _make_txn()
        existing = [_make_txn(description="DIFFERENT", amount=Decimal("99.99"))]
        result = self.validator.check_duplicates(txn, existing)
        assert result.status == DuplicateStatus.UNIQUE

    def test_exact_duplicate(self):
        txn = _make_txn()
        existing = [_make_txn()]
        result = self.validator.check_duplicates(txn, existing)
        assert result.status == DuplicateStatus.DUPLICATE

    def test_suspicious_near_duplicate(self):
        txn = _make_txn(description="GRAB CAR KLCC")
        existing = [_make_txn(description="GRAB CAR BUKIT BINTANG")]
        result = self.validator.check_duplicates(txn, existing)
        assert result.status == DuplicateStatus.SUSPICIOUS

    def test_case_insensitive_duplicate(self):
        txn = _make_txn(description="grab car")
        existing = [_make_txn(description="GRAB CAR")]
        result = self.validator.check_duplicates(txn, existing)
        assert result.status == DuplicateStatus.DUPLICATE

    def test_empty_existing_is_unique(self):
        txn = _make_txn()
        result = self.validator.check_duplicates(txn, [])
        assert result.status == DuplicateStatus.UNIQUE


# ─── Agent Output Validation ────────────────────────────────────────


class TestAgentOutputValidator:
    def setup_method(self):
        self.validator = AgentOutputValidator()

    # AG-01 Categorizer
    def test_valid_categorizer_output(self):
        output = CategorizerOutput(
            category=TransactionCategory.FOOD,
            confidence=0.95,
            reasoning="Nasi Kandar is a Malaysian food establishment",
        )
        errors = self.validator.validate_categorizer_output(output)
        assert errors == []

    def test_low_confidence_short_reasoning(self):
        output = CategorizerOutput(
            category=TransactionCategory.OTHER,
            confidence=0.3,
            reasoning="unsure",
        )
        errors = self.validator.validate_categorizer_output(output)
        assert len(errors) > 0

    # AG-02 Debt Detector
    def test_valid_debt_output(self):
        output = DebtDetectorOutput(
            is_debt_related=True,
            debt_tier=DebtTier.FORMAL,
            provider="PTPTN",
            confidence=0.92,
        )
        errors = self.validator.validate_debt_detector_output(output)
        assert errors == []

    def test_debt_related_without_tier(self):
        output = DebtDetectorOutput(
            is_debt_related=True,
            debt_tier=None,
            confidence=0.8,
        )
        errors = self.validator.validate_debt_detector_output(output)
        assert any("must have a debt_tier" in e for e in errors)

    def test_non_debt_with_tier(self):
        output = DebtDetectorOutput(
            is_debt_related=False,
            debt_tier=DebtTier.BNPL,
            confidence=0.7,
        )
        errors = self.validator.validate_debt_detector_output(output)
        assert any("should not have" in e for e in errors)

    def test_formal_without_provider(self):
        output = DebtDetectorOutput(
            is_debt_related=True,
            debt_tier=DebtTier.FORMAL,
            confidence=0.9,
        )
        errors = self.validator.validate_debt_detector_output(output)
        assert any("provider" in e for e in errors)

    def test_hutang_without_person(self):
        output = DebtDetectorOutput(
            is_debt_related=True,
            debt_tier=DebtTier.HUTANG,
            confidence=0.85,
        )
        errors = self.validator.validate_debt_detector_output(output)
        assert any("person_name" in e for e in errors)

    # AG-06 Advisor
    def test_valid_advisor_output(self):
        output = AdviceResponse(
            recommendations=[
                Recommendation(
                    priority=1,
                    category=AdviceCategory.DEBT,
                    title="Pay BNPL first",
                    description="High effective interest",
                    potential_impact=50.0,
                    difficulty=Difficulty.EASY,
                    action_steps=["Open app", "Pay balance"],
                )
            ],
            disclaimer="This is not professional financial advice. Consult a licensed financial advisor.",
            overall_assessment="Good financial health overall.",
        )
        errors = self.validator.validate_advisor_output(output)
        assert errors == []

    def test_missing_disclaimer(self):
        output = AdviceResponse(
            recommendations=[],
            disclaimer="ok",
            overall_assessment="Fine.",
        )
        errors = self.validator.validate_advisor_output(output)
        assert any("disclaimer" in e.lower() for e in errors)

    def test_unordered_priorities(self):
        output = AdviceResponse(
            recommendations=[
                Recommendation(
                    priority=3, category=AdviceCategory.SPENDING,
                    title="A", description="a", potential_impact=10.0,
                    difficulty=Difficulty.EASY, action_steps=["x"],
                ),
                Recommendation(
                    priority=1, category=AdviceCategory.DEBT,
                    title="B", description="b", potential_impact=50.0,
                    difficulty=Difficulty.MEDIUM, action_steps=["y"],
                ),
            ],
            disclaimer="This is not professional financial advice. Consult a licensed advisor.",
            overall_assessment="Needs work.",
        )
        errors = self.validator.validate_advisor_output(output)
        assert any("ordered" in e.lower() for e in errors)
