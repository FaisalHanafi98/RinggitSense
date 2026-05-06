"""
RinggitSense - Base schemas for API responses
"""
import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Meta(BaseModel):
    """Response metadata."""
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool = True
    data: T
    meta: Meta = Field(default_factory=Meta)


class ErrorDetail(BaseModel):
    """Error details."""
    code: str
    message: str
    details: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: ErrorDetail
    meta: Meta = Field(default_factory=Meta)


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total_items: int
    total_pages: int

    @classmethod
    def from_query(cls, page: int, limit: int, total: int) -> "PaginationMeta":
        """Create pagination metadata from query parameters."""
        total_pages = (total + limit - 1) // limit if limit > 0 else 0
        return cls(
            page=page,
            limit=limit,
            total_items=total,
            total_pages=total_pages,
        )
