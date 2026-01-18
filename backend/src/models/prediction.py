"""
RinggitSense - Prediction model
Monthly spending predictions and actual outcomes
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Date, Numeric, JSON, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class Prediction(Base, UUIDMixin, TimestampMixin):
    """Monthly spending predictions and actual outcomes."""

    __tablename__ = "predictions"
    __table_args__ = (
        CheckConstraint(
            "confidence_level IN ('high', 'medium', 'low') OR confidence_level IS NULL",
            name="valid_confidence_level"
        ),
        UniqueConstraint(
            "user_id", "prediction_month", "category",
            name="uq_predictions_user_month_category"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Prediction target
    prediction_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # NULL for total

    # Prediction values
    predicted_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    confidence_low: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    confidence_high: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    confidence_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Actual (filled after month ends)
    actual_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    accuracy_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)

    # Metadata
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    factors: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="predictions")

    def __repr__(self) -> str:
        cat = self.category or "TOTAL"
        return f"<Prediction {self.prediction_month} {cat}: RM{self.predicted_amount}>"
