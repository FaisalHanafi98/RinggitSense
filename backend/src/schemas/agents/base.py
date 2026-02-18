"""
RinggitSense - Base contracts for agent pipeline.

Defines the shared base classes and exceptions used across all 6 agents.
"""
from datetime import datetime

from pydantic import BaseModel, Field


class AgentContractViolation(Exception):
    """Raised when agent output does not match the expected contract schema."""

    def __init__(self, from_agent: str, to_agent: str, message: str) -> None:
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message = message
        super().__init__(
            f"Contract violation [{from_agent} -> {to_agent}]: {message}"
        )


class BaseAgentInput(BaseModel):
    """Shared fields for all agent inputs."""
    pass


class BaseAgentOutput(BaseModel):
    """Shared fields for all agent outputs that include confidence scoring."""
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")


class HandoffRecord(BaseModel):
    """Records a single handoff between agents for audit trail."""
    from_agent: str
    to_agent: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool
    error_message: str | None = None
