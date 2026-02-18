"""
RinggitSense - AG-04 Predictor data contracts.

Input/output schemas for the financial prediction agent.
Model: claude-sonnet-4 | Temperature: 0.3
"""
from pydantic import BaseModel, Field

from src.schemas.agents.base import BaseAgentInput
from src.schemas.agents.enums import Trend


class UpcomingItem(BaseModel):
    """A known upcoming expense or income."""
    type: str = Field(description="bill or income")
    name: str
    amount: float
    date: str


class PredictorInput(BaseAgentInput):
    """Input for AG-04."""
    historical_transactions: list[dict] = Field(
        description="Past 3-6 months of categorized transactions or category-month summaries"
    )
    known_upcoming: list[UpcomingItem] | None = Field(
        default=None, description="Known upcoming bills or income"
    )
    prediction_month: str = Field(
        description="Month to predict in ISO format, e.g. 2026-03"
    )


class ConfidenceInterval(BaseModel):
    """90% confidence interval bounds."""
    low: float = Field(description="Lower bound (90% confidence)")
    high: float = Field(description="Upper bound (90% confidence)")


class CategoryPrediction(BaseModel):
    """Prediction for a single spending category."""
    category: str
    predicted: float
    trend: Trend


class PredictionResult(BaseModel):
    """Full output from AG-04."""
    total_predicted: float = Field(description="Total predicted spending in RM")
    confidence_interval: ConfidenceInterval
    by_category: list[CategoryPrediction]
    assumptions: list[str] = Field(description="Key assumptions as strings")
    risks: list[str] = Field(description="Risk factor strings")
