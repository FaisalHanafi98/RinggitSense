"""
RinggitSense - Pattern model
Detected spending patterns and lifestyle bundles
"""
import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, Date, Boolean, Numeric, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class Pattern(Base, UUIDMixin, TimestampMixin):
    """Detected spending patterns and lifestyle bundles."""

    __tablename__ = "patterns"
    __table_args__ = (
        CheckConstraint(
            "pattern_type IN ('BUNDLE', 'TREND', 'ANOMALY', 'HIDDEN_COST', 'TEMPORAL', 'RECURRING')",
            name="valid_pattern_type"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Pattern definition
    pattern_type: Mapped[str] = mapped_column(String(50), nullable=False)
    pattern_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Analysis results
    data_points: Mapped[dict] = mapped_column(JSON, nullable=False)
    frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    monthly_impact: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    annual_impact: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 2), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    first_detected: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_seen: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # User interaction
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="patterns")

    def __repr__(self) -> str:
        return f"<Pattern [{self.pattern_type}] {self.pattern_name}>"
