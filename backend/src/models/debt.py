"""
RinggitSense - Debt model
Tracks all debt obligations across three tiers: FORMAL, BNPL, HUTANG
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import String, Text, Date, Integer, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User
    from src.models.transaction import Transaction
    from src.models.debt_item import DebtItem


class Debt(Base, UUIDMixin, TimestampMixin):
    """Debt obligations across three tiers: FORMAL, BNPL, HUTANG."""

    __tablename__ = "debts"
    __table_args__ = (
        CheckConstraint(
            "debt_tier IN ('FORMAL', 'BNPL', 'HUTANG')",
            name="valid_debt_tier"
        ),
        CheckConstraint(
            "direction IN ('OWE', 'OWED') OR direction IS NULL",
            name="valid_direction"
        ),
        CheckConstraint(
            "status IN ('active', 'paid_off', 'defaulted', 'paused')",
            name="valid_status"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Classification
    debt_tier: Mapped[str] = mapped_column(String(20), nullable=False)
    debt_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # For FORMAL and BNPL
    provider: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    original_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    current_balance: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    interest_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    monthly_payment: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expected_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    remaining_installments: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # For HUTANG (informal debts)
    person_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    person_relationship: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # OWE or OWED

    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="debts")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="debt"
    )
    items: Mapped[List["DebtItem"]] = relationship(
        "DebtItem", back_populates="debt", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Debt {self.debt_tier}: {self.debt_name}>"
