"""
RinggitSense - AG-05 Query Agent data contracts.

Input/output schemas for the natural language query agent.
Model: claude-sonnet-4 | Temperature: 0.7
"""
from pydantic import BaseModel, Field

from src.schemas.agents.base import BaseAgentInput


class QueryContext(BaseModel):
    """Context provided to the query agent."""
    transactions: list[dict] = Field(description="Relevant transactions")
    patterns: dict | None = Field(default=None, description="Pre-computed patterns")
    date_range: dict = Field(description="start and end dates as YYYY-MM-DD")
    user_locale: str = Field(
        default="en-MY", description="en-MY or ms-MY"
    )


class QueryInput(BaseAgentInput):
    """Input for AG-05."""
    question: str = Field(
        min_length=1, description="Natural language question (English or Malay)"
    )
    context: QueryContext


class QueryResponse(BaseModel):
    """Full output from AG-05."""
    answer: str = Field(min_length=1, description="Natural language answer")
    data: dict | None = Field(
        default=None, description="Structured supporting data"
    )
    visualization_hint: str | None = Field(
        default=None, description="Suggested chart type, e.g. bar_chart_by_week"
    )
    follow_up_questions: list[str] | None = Field(
        default=None, description="2-3 related questions"
    )
    routed_to: str | None = Field(
        default=None, description="Agent ID if routing needed, e.g. AG-04"
    )
