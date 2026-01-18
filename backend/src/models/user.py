"""
RinggitSense - User model
"""
import uuid
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User accounts linked to Clerk authentication."""

    __tablename__ = "users"

    clerk_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    monthly_income: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="MYR")
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    data_sources = relationship("DataSource", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    debts = relationship("Debt", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    advice_items = relationship("Advice", back_populates="user", cascade="all, delete-orphan")
    patterns = relationship("Pattern", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
