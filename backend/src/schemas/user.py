"""
RinggitSense - User schemas
"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str | None = None
    monthly_income: Decimal | None = None
    currency: str = "MYR"
    created_at: datetime


class UserUpdate(BaseModel):
    """User update schema."""
    name: str | None = None
    monthly_income: Decimal | None = None
    currency: str | None = None
    settings: dict | None = None
