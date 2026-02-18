"""
RinggitSense - AG-03 Pattern Analyzer data contracts.

Input/output schemas for the spending pattern detection agent.
Model: claude-sonnet-4 | Temperature: 0.5
"""
from pydantic import BaseModel, Field

from src.schemas.agents.base import BaseAgentInput, BaseAgentOutput
from src.schemas.agents.enums import PatternType


class PatternAnalyzerInput(BaseAgentInput):
    """Input for AG-03."""
    transactions: list[dict] = Field(
        description="All categorized transactions in the analysis period"
    )
    period: str = Field(
        description="Analysis period: 3_months, 6_months, or available"
    )
    focus_areas: list[str] | None = Field(
        default=None,
        description="Optional focus: hidden_costs, bundles, temporal"
    )


class PatternItem(BaseAgentOutput):
    """A single detected pattern."""
    type: PatternType
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    evidence: list[str] = Field(
        description="Transaction IDs or summary strings"
    )
    impact: float = Field(description="Estimated RM impact")


class PatternResult(BaseModel):
    """Full output from AG-03."""
    patterns: list[PatternItem]
    summary: str = Field(min_length=1, description="Overall pattern summary")
    hidden_cost_total: float = Field(
        ge=0.0, description="Total hidden costs in RM"
    )
