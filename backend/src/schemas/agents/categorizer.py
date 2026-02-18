"""
RinggitSense - AG-01 Categorizer data contracts.

Input/output schemas for the transaction categorization agent.
Model: claude-sonnet-4 | Temperature: 0.2
"""
from pydantic import BaseModel, Field

from src.schemas.agents.base import BaseAgentInput, BaseAgentOutput
from src.schemas.agents.enums import TransactionCategory


class CategorizerInput(BaseAgentInput):
    """Single transaction input for AG-01."""
    description: str = Field(min_length=1, description="Transaction description from bank/e-wallet")
    amount: float = Field(description="Transaction amount in RM")
    source: str = Field(min_length=1, description="Bank or e-wallet name")
    date: str = Field(description="Transaction date in ISO format")
    comment: str | None = Field(default=None, description="Optional user comment")


class CategorizerOutput(BaseAgentOutput):
    """Single transaction output from AG-01."""
    category: TransactionCategory
    subcategory: str | None = Field(default=None, description="e.g. toll, restaurant, fast_food")
    merchant_name: str | None = Field(default=None, description="Extracted merchant or null")
    reasoning: str = Field(min_length=1, description="Brief explanation for debugging")


class CategorizerBatchItem(BaseModel):
    """A single item within a batch request."""
    id: str = Field(description="Transaction identifier for matching")
    description: str = Field(min_length=1)
    amount: float
    source: str = Field(min_length=1)
    date: str
    comment: str | None = None


class CategorizerBatchInput(BaseModel):
    """Batch input for AG-01 (max 50 transactions per batch)."""
    transactions: list[CategorizerBatchItem] = Field(max_length=50)


class CategorizerBatchResultItem(BaseModel):
    """A single result within a batch response."""
    id: str
    category: TransactionCategory
    confidence: float = Field(ge=0.0, le=1.0)
    subcategory: str | None = None
    merchant_name: str | None = None
    reasoning: str


class CategorizerBatchOutput(BaseModel):
    """Batch output from AG-01."""
    results: list[CategorizerBatchResultItem]
    processing_time_ms: int = Field(ge=0)
    success_count: int = Field(ge=0)
    error_count: int = Field(ge=0)
