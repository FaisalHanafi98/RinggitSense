"""
Test SQLAlchemy model imports and basic structure
"""
import pytest


def test_all_models_import():
    """Test that all models can be imported."""
    from src.models import (
        Base, User, DataSource, Transaction,
        Debt, DebtItem, Prediction, Advice, Pattern, AuditLog
    )
    assert Base is not None
    assert User is not None
    assert DataSource is not None
    assert Transaction is not None
    assert Debt is not None
    assert DebtItem is not None
    assert Prediction is not None
    assert Advice is not None
    assert Pattern is not None
    assert AuditLog is not None


def test_model_tablenames():
    """Test that models have correct table names."""
    from src.models import (
        User, DataSource, Transaction,
        Debt, DebtItem, Prediction, Advice, Pattern, AuditLog
    )

    expected = {
        User: "users",
        DataSource: "data_sources",
        Transaction: "transactions",
        Debt: "debts",
        DebtItem: "debt_items",
        Prediction: "predictions",
        Advice: "advice",
        Pattern: "patterns",
        AuditLog: "audit_log",
    }

    for model, tablename in expected.items():
        assert model.__tablename__ == tablename, f"{model.__name__} should have tablename '{tablename}'"


def test_user_relationships():
    """Test that User model has all expected relationships."""
    from src.models import User

    mapper = User.__mapper__
    relationship_names = [r.key for r in mapper.relationships]

    expected_relationships = [
        "data_sources", "transactions", "debts",
        "predictions", "advice_items", "patterns"
    ]

    for rel in expected_relationships:
        assert rel in relationship_names, f"User should have relationship '{rel}'"


def test_debt_tiers():
    """Test debt tier constraint values."""
    from src.models import Debt

    # Check that the model has the constraint
    constraints = [c.name for c in Debt.__table__.constraints if hasattr(c, 'name') and c.name]
    assert "valid_debt_tier" in constraints, "Debt should have valid_debt_tier constraint"


def test_advice_priorities():
    """Test advice priority constraint values."""
    from src.models import Advice

    constraints = [c.name for c in Advice.__table__.constraints if hasattr(c, 'name') and c.name]
    assert "valid_priority" in constraints, "Advice should have valid_priority constraint"


def test_pattern_types():
    """Test pattern type constraint values."""
    from src.models import Pattern

    constraints = [c.name for c in Pattern.__table__.constraints if hasattr(c, 'name') and c.name]
    assert "valid_pattern_type" in constraints, "Pattern should have valid_pattern_type constraint"
