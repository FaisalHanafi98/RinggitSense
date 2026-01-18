"""
RinggitSense - Data Source model (banks and e-wallets)
"""
import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, Date, JSON, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, UUIDMixin, TimestampMixin


# Valid source types for Malaysian banks and e-wallets
SOURCE_TYPES = [
    "maybank", "cimb", "rhb", "public_bank", "hong_leong",
    "aeon_bank", "touch_n_go", "grabpay", "shopeepay", "boost",
    "bigpay", "manual"
]


class DataSource(Base, UUIDMixin, TimestampMixin):
    """Connected banks and e-wallets for transaction import."""

    __tablename__ = "data_sources"
    __table_args__ = (
        CheckConstraint(
            f"source_type IN ({', '.join(repr(s) for s in SOURCE_TYPES)})",
            name="valid_source_type"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_synced: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    total_transactions: Mapped[int] = mapped_column(Integer, default=0)
    date_range_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_range_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="data_sources")
    transactions = relationship("Transaction", back_populates="source")

    def __repr__(self) -> str:
        return f"<DataSource {self.source_name} ({self.source_type})>"
