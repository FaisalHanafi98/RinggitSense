"""
RinggitSense - Transaction schemas for API request/response
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.base import PaginationMeta


class TransactionResponse(BaseModel):
    """Single transaction in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    source_id: UUID | None = None
    transaction_date: date
    amount: Decimal
    description: str
    original_description: str | None = None
    category: str | None = None
    category_confidence: Decimal | None = None
    subcategory: str | None = None
    merchant_name: str | None = None
    is_debt_related: bool = False
    debt_tier: str | None = None
    debt_id: UUID | None = None
    is_recurring: bool = False
    user_comment: str | None = None
    created_at: datetime


class TransactionListResponse(BaseModel):
    """Paginated list of transactions."""
    transactions: list[TransactionResponse]
    pagination: PaginationMeta


class UploadValidationDetail(BaseModel):
    """Validation detail for a single transaction in the upload."""
    row: int
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DuplicateDetail(BaseModel):
    """Detail about a detected duplicate."""
    row: int
    description: str
    amount: Decimal
    transaction_date: date
    status: str  # DUPLICATE or SUSPICIOUS
    matching_description: str | None = None


class UploadResponse(BaseModel):
    """Response from the transaction upload endpoint."""
    source_id: UUID
    bank_name: str
    total_parsed: int
    total_valid: int
    total_invalid: int
    total_stored: int
    duplicates_skipped: int
    suspicious_duplicates: int
    job_id: UUID | None = None
    validation_errors: list[UploadValidationDetail] = Field(default_factory=list)
    duplicate_details: list[DuplicateDetail] = Field(default_factory=list)
    batch_warnings: list[str] = Field(default_factory=list)
    parser_warnings: list[str] = Field(default_factory=list)
