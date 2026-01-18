"""
RinggitSense - User schemas
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    currency: str = "MYR"
    created_at: datetime


class UserUpdate(BaseModel):
    """User update schema."""
    name: Optional[str] = None
    monthly_income: Optional[Decimal] = None
    currency: Optional[str] = None
    settings: Optional[dict] = None
