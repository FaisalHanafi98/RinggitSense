"""
RinggitSense - AG-06 Advisor data contracts.

Input/output schemas for the financial advice agent.
Model: claude-sonnet-4 | Temperature: 0.6
"""
from pydantic import BaseModel, Field

from src.schemas.agents.base import BaseAgentInput
from src.schemas.agents.enums import AdviceCategory, Difficulty


class UserProfile(BaseModel):
    """Summarized user financial profile for the advisor."""
    income: float = Field(description="Monthly income in RM")
    fixed_expenses: float = Field(description="Fixed monthly expenses in RM")
    debt_total: float = Field(description="Total monthly debt obligation in RM")


class AdvisorInput(BaseAgentInput):
    """Input for AG-06."""
    user_profile: UserProfile
    patterns: dict = Field(description="AG-03 output (hidden_costs, bundles, trends)")
    debt_summary: dict = Field(description="AG-02 aggregation output")
    goals: list[str] | None = Field(
        default=None, description="User-defined financial goals"
    )


class Recommendation(BaseModel):
    """A single financial recommendation."""
    priority: int = Field(ge=1, le=5, description="1 = highest, 5 = lowest")
    category: AdviceCategory
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    potential_impact: float = Field(
        ge=0.0, description="Estimated RM impact per month"
    )
    difficulty: Difficulty
    action_steps: list[str] = Field(
        min_length=1, description="Specific action strings"
    )


class AdviceResponse(BaseModel):
    """Full output from AG-06."""
    recommendations: list[Recommendation]
    disclaimer: str = Field(
        min_length=1,
        description="MANDATORY disclaimer — blocking defect if absent"
    )
    overall_assessment: str = Field(
        min_length=1, description="Summary of financial health"
    )
