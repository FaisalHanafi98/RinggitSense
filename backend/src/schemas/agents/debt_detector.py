"""
RinggitSense - AG-02 Debt Detector data contracts.

Input/output schemas for the three-tier debt detection agent.
Model: claude-sonnet-4 | Temperature: 0.1
"""
from pydantic import BaseModel, Field

from src.schemas.agents.base import BaseAgentInput, BaseAgentOutput
from src.schemas.agents.enums import DebtTier


class DebtDetectorInput(BaseAgentInput):
    """Single transaction input for AG-02."""
    description: str = Field(min_length=1)
    amount: float
    source: str = Field(min_length=1)
    is_recurring: bool = False
    comment: str | None = None
    similar_transactions: list[dict] | None = Field(
        default=None,
        description="Other transactions to same recipient for pattern detection"
    )


class DebtDetectorOutput(BaseAgentOutput):
    """Single transaction output from AG-02."""
    is_debt_related: bool
    debt_tier: DebtTier | None = Field(
        default=None, description="Null if not debt-related"
    )
    debt_type: str | None = Field(
        default=None, description="e.g. education_loan, installment, personal_loan"
    )
    provider: str | None = Field(
        default=None, description="e.g. PTPTN, Shopee SPayLater"
    )
    indicators: list[str] = Field(
        default_factory=list, description="List of detection reasons"
    )
    estimated_monthly: float | None = Field(
        default=None, description="Estimated monthly RM payment"
    )
    person_name: str | None = Field(
        default=None, description="For HUTANG tier only"
    )


class DebtTierSummary(BaseModel):
    """Summary for a single debt tier."""
    count: int = Field(ge=0)
    providers: list[str] = Field(default_factory=list)
    people: list[str] = Field(default_factory=list)
    estimated_monthly_total: float = Field(ge=0.0)
    estimated_total: float = Field(ge=0.0)


class DebtSummary(BaseModel):
    """Aggregated debt summary across all three tiers from AG-02."""
    formal: DebtTierSummary
    bnpl: DebtTierSummary
    hutang: DebtTierSummary
    total_monthly_debt_obligation: float = Field(ge=0.0)
