"""initial schema - all 9 tables

Revision ID: e343df7105ef
Revises:
Create Date: 2026-02-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "e343df7105ef"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("clerk_id", sa.String(255), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("monthly_income", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), server_default="MYR"),
        sa.Column("settings", postgresql.JSON(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --- data_sources ---
    op.create_table(
        "data_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_name", sa.String(255), nullable=False),
        sa.Column("last_synced", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_transactions", sa.Integer, server_default="0"),
        sa.Column("date_range_start", sa.Date, nullable=True),
        sa.Column("date_range_end", sa.Date, nullable=True),
        sa.Column("config", postgresql.JSON(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "source_type IN ('maybank', 'cimb', 'rhb', 'public_bank', 'hong_leong', "
            "'aeon_bank', 'touch_n_go', 'grabpay', 'shopeepay', 'boost', 'bigpay', 'manual')",
            name="valid_source_type",
        ),
    )

    # --- debts ---
    op.create_table(
        "debts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("debt_tier", sa.String(20), nullable=False),
        sa.Column("debt_name", sa.String(255), nullable=False),
        sa.Column("provider", sa.String(100), nullable=True),
        sa.Column("original_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("current_balance", sa.Numeric(12, 2), nullable=True),
        sa.Column("interest_rate", sa.Numeric(5, 2), nullable=True),
        sa.Column("monthly_payment", sa.Numeric(12, 2), nullable=True),
        sa.Column("start_date", sa.Date, nullable=True),
        sa.Column("expected_end_date", sa.Date, nullable=True),
        sa.Column("remaining_installments", sa.Integer, nullable=True),
        sa.Column("person_name", sa.String(255), nullable=True),
        sa.Column("person_relationship", sa.String(50), nullable=True),
        sa.Column("direction", sa.String(10), nullable=True),
        sa.Column("status", sa.String(20), server_default="active"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("debt_tier IN ('FORMAL', 'BNPL', 'HUTANG')", name="valid_debt_tier"),
        sa.CheckConstraint("direction IN ('OWE', 'OWED') OR direction IS NULL", name="valid_direction"),
        sa.CheckConstraint("status IN ('active', 'paid_off', 'defaulted', 'paused')", name="valid_status"),
    )

    # --- transactions ---
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("data_sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("transaction_date", sa.Date, nullable=False, index=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("original_description", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=True, index=True),
        sa.Column("category_confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("merchant_name", sa.String(255), nullable=True),
        sa.Column("is_debt_related", sa.Boolean, server_default="false"),
        sa.Column("debt_tier", sa.String(20), nullable=True),
        sa.Column("debt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("raw_data", postgresql.JSON(), nullable=True),
        sa.Column("user_comment", sa.Text, nullable=True),
        sa.Column("is_recurring", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --- debt_items ---
    op.create_table(
        "debt_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("debt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("debts.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("item_date", sa.Date, nullable=False),
        sa.Column("is_paid", sa.Boolean, server_default="false"),
        sa.Column("paid_date", sa.Date, nullable=True),
        sa.Column("paid_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("linked_transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --- predictions ---
    op.create_table(
        "predictions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("prediction_month", sa.Date, nullable=False, index=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("predicted_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("confidence_low", sa.Numeric(12, 2), nullable=True),
        sa.Column("confidence_high", sa.Numeric(12, 2), nullable=True),
        sa.Column("confidence_level", sa.String(20), nullable=True),
        sa.Column("actual_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("accuracy_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("factors", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("confidence_level IN ('high', 'medium', 'low') OR confidence_level IS NULL", name="valid_confidence_level"),
        sa.UniqueConstraint("user_id", "prediction_month", "category", name="uq_predictions_user_month_category"),
    )

    # --- advice ---
    op.create_table(
        "advice",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("advice_type", sa.String(50), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("trigger_metric", sa.String(100), nullable=True),
        sa.Column("trigger_value", postgresql.JSON(), nullable=True),
        sa.Column("is_read", sa.Boolean, server_default="false"),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_helpful", sa.Boolean, nullable=True),
        sa.Column("feedback_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_snoozed", sa.Boolean, server_default="false"),
        sa.Column("snoozed_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("priority IN ('URGENT', 'IMPORTANT', 'GROWTH')", name="valid_priority"),
        sa.CheckConstraint(
            "advice_type IN ('debt_warning', 'bnpl_alert', 'spending_spike', 'savings_tip', "
            "'hidden_cost', 'positive_reinforcement', 'goal_progress', 'seasonal_reminder', 'general_tip')",
            name="valid_advice_type",
        ),
    )

    # --- patterns ---
    op.create_table(
        "patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("pattern_type", sa.String(50), nullable=False),
        sa.Column("pattern_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("data_points", postgresql.JSON(), nullable=False),
        sa.Column("frequency", sa.String(50), nullable=True),
        sa.Column("monthly_impact", sa.Numeric(12, 2), nullable=True),
        sa.Column("annual_impact", sa.Numeric(12, 2), nullable=True),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("first_detected", sa.Date, nullable=True),
        sa.Column("last_seen", sa.Date, nullable=True),
        sa.Column("is_acknowledged", sa.Boolean, server_default="false"),
        sa.Column("user_notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "pattern_type IN ('BUNDLE', 'TREND', 'ANOMALY', 'HIDDEN_COST', 'TEMPORAL', 'RECURRING')",
            name="valid_pattern_type",
        ),
    )

    # --- audit_log ---
    op.create_table(
        "audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False, index=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("old_values", postgresql.JSON(), nullable=True),
        sa.Column("new_values", postgresql.JSON(), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("patterns")
    op.drop_table("advice")
    op.drop_table("predictions")
    op.drop_table("debt_items")
    op.drop_table("transactions")
    op.drop_table("debts")
    op.drop_table("data_sources")
    op.drop_table("users")
