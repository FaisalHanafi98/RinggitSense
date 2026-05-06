"""
RinggitSense - Unit tests for AG-01 Categorizer Agent.

Tests the agent's input/output handling, JSON parsing, and error cases.
The actual Claude API is mocked — these test the agent code, not the model.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.agents.categorizer import CategorizerAgent
from src.schemas.agents.enums import TransactionCategory


def _mock_api_response(text: str):
    """Create a mock Anthropic message response."""
    mock_content = MagicMock()
    mock_content.text = text
    mock_message = MagicMock()
    mock_message.content = [mock_content]
    mock_message.usage = MagicMock(input_tokens=100, output_tokens=50)
    return mock_message


class TestCategorizerAgent:
    @patch("src.agents.base.anthropic.Anthropic")
    def test_categorize_food_transaction(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            '{"category": "FOOD", "confidence": 0.98, "subcategory": "fast_food", '
            '"merchant_name": "McDonald\'s", "reasoning": "MCDONALD\'S is a fast food chain"}'
        )

        agent = CategorizerAgent()
        result = agent.categorize(
            description="MCDONALD'S SUNWAY PYRAMID",
            amount=25.90,
            source="Maybank",
            date="2026-01-15",
        )

        assert result.category == TransactionCategory.FOOD
        assert result.confidence == 0.98
        assert result.subcategory == "fast_food"
        assert result.merchant_name == "McDonald's"
        assert len(result.reasoning) > 0

    @patch("src.agents.base.anthropic.Anthropic")
    def test_categorize_transport_toll(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            '{"category": "TRANSPORT", "confidence": 0.99, "subcategory": "toll", '
            '"merchant_name": "PLUS Highway", "reasoning": "PLUS TOLL PLZ indicates highway toll"}'
        )

        agent = CategorizerAgent()
        result = agent.categorize(
            description="PLUS TOLL PLZ SUBANG",
            amount=3.20,
            source="Touch n Go",
            date="2026-01-15",
        )

        assert result.category == TransactionCategory.TRANSPORT
        assert result.confidence >= 0.95

    @patch("src.agents.base.anthropic.Anthropic")
    def test_categorize_income(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            '{"category": "INCOME", "confidence": 0.95, "subcategory": "salary", '
            '"merchant_name": null, "reasoning": "SALARY keyword indicates income"}'
        )

        agent = CategorizerAgent()
        result = agent.categorize(
            description="SALARY JAN 2026",
            amount=5000.00,
            source="Maybank",
            date="2026-01-18",
        )

        assert result.category == TransactionCategory.INCOME

    @patch("src.agents.base.anthropic.Anthropic")
    def test_categorize_lowercase_category_normalized(self, mock_anthropic_cls):
        """Agent should normalize lowercase category from model to enum."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            '{"category": "food", "confidence": 0.90, "subcategory": null, '
            '"merchant_name": null, "reasoning": "food related"}'
        )

        agent = CategorizerAgent()
        result = agent.categorize(
            description="RESTORAN MAMAK",
            amount=12.00,
            source="CIMB",
            date="2026-01-20",
        )

        assert result.category == TransactionCategory.FOOD

    @patch("src.agents.base.anthropic.Anthropic")
    def test_categorize_markdown_json_parsed(self, mock_anthropic_cls):
        """Agent should extract JSON from markdown code blocks."""
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            '```json\n{"category": "SHOPPING", "confidence": 0.85, "subcategory": "online", '
            '"merchant_name": "Shopee", "reasoning": "Shopee is an e-commerce platform"}\n```'
        )

        agent = CategorizerAgent()
        result = agent.categorize(
            description="SHOPEE MALAYSIA",
            amount=89.90,
            source="Maybank",
            date="2026-01-17",
        )

        assert result.category == TransactionCategory.SHOPPING

    @patch("src.agents.base.anthropic.Anthropic")
    def test_categorize_batch(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            '{"results": ['
            '{"id": "txn_1", "category": "FOOD", "confidence": 0.98, "subcategory": "fast_food", '
            '"merchant_name": "McDonald\'s", "reasoning": "fast food chain"},'
            '{"id": "txn_2", "category": "TRANSPORT", "confidence": 0.99, "subcategory": "toll", '
            '"merchant_name": "PLUS", "reasoning": "toll payment"}'
            ']}'
        )

        agent = CategorizerAgent()
        result = agent.categorize_batch([
            {"id": "txn_1", "description": "MCDONALD'S", "amount": 25.90, "source": "Maybank", "date": "2026-01-15"},
            {"id": "txn_2", "description": "PLUS TOLL", "amount": 3.20, "source": "TnG", "date": "2026-01-15"},
        ])

        assert result.success_count == 2
        assert result.error_count == 0
        assert result.processing_time_ms >= 0
        assert result.results[0].category == TransactionCategory.FOOD
        assert result.results[1].category == TransactionCategory.TRANSPORT

    @patch("src.agents.base.anthropic.Anthropic")
    def test_batch_exceeds_50_raises(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        agent = CategorizerAgent()
        with pytest.raises(ValueError, match="50"):
            agent.categorize_batch([{"id": f"txn_{i}"} for i in range(51)])

    @patch("src.agents.base.anthropic.Anthropic")
    def test_invalid_json_raises_value_error(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _mock_api_response(
            "This is not valid JSON at all"
        )

        agent = CategorizerAgent()
        with pytest.raises(ValueError, match="Could not parse JSON"):
            agent.categorize(
                description="TEST", amount=10.0, source="Maybank", date="2026-01-01"
            )

    @patch("src.agents.base.anthropic.Anthropic")
    def test_agent_properties(self, mock_anthropic_cls):
        mock_anthropic_cls.return_value = MagicMock()
        agent = CategorizerAgent()
        assert agent.AGENT_ID == "AG-01"
        assert agent.AGENT_NAME == "Categorizer"
        assert agent.TEMPERATURE == 0.2
        assert "Categorizer Agent" in agent.get_system_prompt()
