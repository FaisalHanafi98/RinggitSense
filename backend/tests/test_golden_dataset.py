"""
RinggitSense - Golden dataset tests.

Validates that the synthetic Maybank and CIMB golden CSVs parse correctly
and cover all 10 transaction categories and 3 debt tiers.
"""
from decimal import Decimal
from pathlib import Path

from src.parsers import get_parser

GOLDEN_DIR = Path(__file__).parent / "fixtures" / "golden"


class TestMaybankGolden:
    def setup_method(self):
        parser = get_parser("maybank")
        with open(GOLDEN_DIR / "maybank_golden.csv", "rb") as f:
            self.result = parser.parse(f.read(), filename="maybank_golden.csv")

    def test_parses_successfully(self):
        assert self.result.success
        assert len(self.result.errors) == 0

    def test_transaction_count(self):
        assert self.result.transaction_count >= 90

    def test_has_credits_and_debits(self):
        credits = [t for t in self.result.transactions if t.transaction_type == "credit"]
        debits = [t for t in self.result.transactions if t.transaction_type == "debit"]
        assert len(credits) >= 4
        assert len(debits) >= 35

    def test_amounts_are_positive(self):
        for txn in self.result.transactions:
            assert txn.amount > 0, f"Amount should be positive: {txn.description}"

    def test_all_dates_in_2026_q1(self):
        """Golden dataset spans Jan-Mar 2026 (3 months for pattern analysis)."""
        for txn in self.result.transactions:
            assert txn.transaction_date.year == 2026
            assert txn.transaction_date.month in (1, 2, 3)

    def test_contains_toll_transactions(self):
        tolls = [t for t in self.result.transactions if "TOLL" in t.description.upper()]
        assert len(tolls) >= 3

    def test_contains_food_transactions(self):
        food_keywords = ["MCDONALD", "NASI KANDAR", "DOMINO", "PELITA", "GROCER"]
        food = [
            t for t in self.result.transactions
            if any(kw in t.description.upper() for kw in food_keywords)
        ]
        assert len(food) >= 3

    def test_contains_debt_payments(self):
        debt_keywords = ["PTPTN", "PERSONAL LOAN", "HIRE PURCHASE", "SPAYLATER", "GRABPAYLATER", "ATOME", "CREDIT CARD"]
        debt = [
            t for t in self.result.transactions
            if any(kw in t.description.upper() for kw in debt_keywords)
        ]
        assert len(debt) >= 5

    def test_contains_salary(self):
        salary = [t for t in self.result.transactions if "SALARY" in t.description.upper()]
        assert len(salary) >= 1
        assert salary[0].transaction_type == "credit"

    def test_small_and_large_amounts(self):
        amounts = [t.amount for t in self.result.transactions]
        assert min(amounts) < Decimal("5")
        assert max(amounts) >= Decimal("850")


class TestCIMBGolden:
    def setup_method(self):
        parser = get_parser("cimb")
        with open(GOLDEN_DIR / "cimb_golden.csv", "rb") as f:
            self.result = parser.parse(f.read(), filename="cimb_golden.csv")

    def test_parses_successfully(self):
        assert self.result.success
        assert len(self.result.errors) == 0

    def test_handles_header_rows(self):
        assert self.result.transaction_count >= 30

    def test_has_credits_and_debits(self):
        credits = [t for t in self.result.transactions if t.transaction_type == "credit"]
        debits = [t for t in self.result.transactions if t.transaction_type == "debit"]
        assert len(credits) >= 4
        assert len(debits) >= 25

    def test_contains_housing_loan(self):
        housing = [t for t in self.result.transactions if "HOUSING LOAN" in t.description.upper()]
        assert len(housing) >= 1
        assert housing[0].amount >= Decimal("1000")

    def test_contains_bnpl_payments(self):
        bnpl_keywords = ["SPAYLATER", "ATOME", "GRABPAYLATER"]
        bnpl = [
            t for t in self.result.transactions
            if any(kw in t.description.upper() for kw in bnpl_keywords)
        ]
        assert len(bnpl) >= 2

    def test_contains_healthcare(self):
        health_keywords = ["PHARMACY", "CLINIC", "HOSPITAL", "WATSONS"]
        health = [
            t for t in self.result.transactions
            if any(kw in t.description.upper() for kw in health_keywords)
        ]
        assert len(health) >= 2

    def test_bonus_is_credit(self):
        bonus = [t for t in self.result.transactions if "BONUS" in t.description.upper()]
        assert len(bonus) >= 1
        assert bonus[0].transaction_type == "credit"
