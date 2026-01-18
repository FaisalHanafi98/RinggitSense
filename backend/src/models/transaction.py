"""
RinggitSense - Transaction model
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Text, Date, Boolean, Numeric, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin


class Transaction(Base, UUIDMixin, TimestampMixin):
    """Financial transactions imported from banks and e-wallets."""

    __tablename__ = "transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="SET NULL"),
        nullable=True
    )

    # Core transaction data
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    original_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Categorization (from AG-01 Categorizer)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    category_confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    merchant_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Debt detection (from AG-02 Debt Detector)
    is_debt_related: Mapped[bool] = mapped_column(Boolean, default=False)
    debt_tier: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    debt_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("debts.id", ondelete="SET NULL"),
        nullable=True
    )

    # Metadata
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    user_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="transactions")
    source = relationship("DataSource", back_populates="transactions")
    debt = relationship("Debt", back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_date} RM{self.amount}>"
