"""
RinggitSense - Advice model
Generated financial advice and user interactions
"""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Text, Boolean, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from src.models.user import User


class Advice(Base, UUIDMixin, TimestampMixin):
    """Generated financial advice and user interactions."""

    __tablename__ = "advice"
    __table_args__ = (
        CheckConstraint(
            "priority IN ('URGENT', 'IMPORTANT', 'GROWTH')",
            name="valid_priority"
        ),
        CheckConstraint(
            """advice_type IN (
                'debt_warning', 'bnpl_alert', 'spending_spike', 'savings_tip',
                'hidden_cost', 'positive_reinforcement', 'goal_progress',
                'seasonal_reminder', 'general_tip'
            )""",
            name="valid_advice_type"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Advice content
    advice_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Trigger data
    trigger_metric: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    trigger_value: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # User interaction
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_helpful: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_snoozed: Mapped[bool] = mapped_column(Boolean, default=False)
    snoozed_until: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Lifecycle
    expires_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="advice_items")

    def __repr__(self) -> str:
        return f"<Advice [{self.priority}] {self.title[:30]}>"
