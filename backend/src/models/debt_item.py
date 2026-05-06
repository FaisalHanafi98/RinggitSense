"""
RinggitSense - DebtItem model
Individual items within a debt (especially for HUTANG tracking)
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from src.models.debt import Debt
    from src.models.transaction import Transaction


class DebtItem(Base, UUIDMixin, TimestampMixin):
    """Individual items within a debt (especially for HUTANG tracking)."""

    __tablename__ = "debt_items"

    debt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("debts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Item details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    item_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Payment tracking
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    paid_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    linked_transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True
    )

    # Metadata
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    debt: Mapped["Debt"] = relationship("Debt", back_populates="items")
    linked_transaction: Mapped[Optional["Transaction"]] = relationship(
        "Transaction", foreign_keys=[linked_transaction_id]
    )

    def __repr__(self) -> str:
        return f"<DebtItem {self.item_date} RM{self.amount}>"
