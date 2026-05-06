"""
RinggitSense - Pipeline run model for async agent processing.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin


class PipelineRun(Base, UUIDMixin, TimestampMixin):
    """Tracks async agent pipeline executions triggered by statement uploads."""

    __tablename__ = "pipeline_runs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_sources.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Pipeline state
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    stages_completed: Mapped[int] = mapped_column(Integer, default=0)
    total_stages: Mapped[int] = mapped_column(Integer, default=6)

    # Results and errors
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    stage_results: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user = relationship("User")
    source = relationship("DataSource")
