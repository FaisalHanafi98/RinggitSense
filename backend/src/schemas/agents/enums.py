"""
RinggitSense - Shared enums for agent data contracts.

Canonical source of truth for all categorical values used across
the 6-agent pipeline (AG-01 through AG-06).
"""
from enum import Enum


class TransactionCategory(str, Enum):
    """Transaction categories assigned by AG-01 Categorizer."""
    FOOD = "FOOD"
    TRANSPORT = "TRANSPORT"
    BILLS = "BILLS"
    ENTERTAINMENT = "ENTERTAINMENT"
    SHOPPING = "SHOPPING"
    TRANSFER = "TRANSFER"
    DEBT_PAYMENT = "DEBT_PAYMENT"
    INCOME = "INCOME"
    HEALTHCARE = "HEALTHCARE"
    OTHER = "OTHER"


class DebtTier(str, Enum):
    """Malaysian three-tier debt classification by AG-02 Debt Detector."""
    FORMAL = "FORMAL"      # PTPTN, bank loans, hire purchase, mortgages, credit cards
    BNPL = "BNPL"          # SPayLater, GrabPayLater, Atome, Split
    HUTANG = "HUTANG"      # Informal borrowing between family/friends


class PatternType(str, Enum):
    """Spending pattern types identified by AG-03 Pattern Analyzer."""
    TEMPORAL = "TEMPORAL"        # Weekend surges, payday effects, month-end
    BUNDLE = "BUNDLE"            # Co-occurring expenses
    HIDDEN_COST = "HIDDEN_COST"  # Toll aggregation, delivery fees, subscriptions
    TREND = "TREND"              # Rising/falling categories over time
    ANOMALY = "ANOMALY"          # Spending spikes, new merchants


class Trend(str, Enum):
    """Trend direction for category-level predictions by AG-04."""
    RISING = "RISING"
    STABLE = "STABLE"
    FALLING = "FALLING"


class AdviceCategory(str, Enum):
    """Advice categories from AG-06 Advisor."""
    SPENDING = "SPENDING"
    SAVING = "SAVING"
    DEBT = "DEBT"
    BUDGETING = "BUDGETING"
    BEHAVIOR = "BEHAVIOR"


class Difficulty(str, Enum):
    """Difficulty level for financial recommendations."""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class ConfidenceLevel(str, Enum):
    """Qualitative confidence level for predictions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DebtDirection(str, Enum):
    """Direction of informal debt (HUTANG)."""
    OWE = "OWE"      # User owes someone
    OWED = "OWED"    # Someone owes user
