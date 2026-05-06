"""
RinggitSense - Base agent class for Claude API integration.

All 6 agents (AG-01 through AG-06) inherit from this base.
"""
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

import anthropic

from src.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for RinggitSense AI agents."""

    AGENT_ID: str = "AG-00"
    AGENT_NAME: str = "BaseAgent"
    MODEL: str = settings.CLAUDE_MODEL
    TEMPERATURE: float = 0.2
    MAX_TOKENS: int = 1024

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the agent's system prompt."""

    def _build_user_message(self, data: dict[str, Any]) -> str:
        """Convert input data to a user message string."""
        return json.dumps(data, default=str)

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """Extract JSON from the model's text response."""
        # Try direct parse first
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        if "```" in text:
            start = text.find("```")
            # Skip the language identifier line (e.g., ```json)
            content_start = text.find("\n", start) + 1
            end = text.find("```", content_start)
            if end > content_start:
                return json.loads(text[content_start:end].strip())

        raise ValueError(f"Could not parse JSON from agent response: {text[:200]}")

    def invoke(self, data: dict[str, Any]) -> dict[str, Any]:
        """Call the Claude API and return parsed JSON output.

        Args:
            data: Input data matching the agent's input schema.

        Returns:
            Parsed JSON response matching the agent's output schema.

        Raises:
            anthropic.APIError: On API-level failures.
            ValueError: If the response can't be parsed as JSON.
        """
        message = self._client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": self._build_user_message(data)},
            ],
        )

        response_text = message.content[0].text
        logger.debug(
            "%s response (tokens: %d in / %d out): %s",
            self.AGENT_ID,
            message.usage.input_tokens,
            message.usage.output_tokens,
            response_text[:200],
        )

        return self._parse_json_response(response_text)

    def invoke_batch(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        """Call the Claude API with a batch of items.

        Override in subclasses for agent-specific batch prompts.
        Default implementation sends all items as a single message.
        """
        return self.invoke({"transactions": items})
