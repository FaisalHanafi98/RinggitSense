"""
RinggitSense - Agent Pipeline with contract validation.

Validates data at each agent handoff point in the sequential pipeline:
AG-01 (Categorizer) → AG-02 (Debt Detector) → AG-03 (Pattern Analyzer)
→ AG-04 (Predictor) → AG-06 (Advisor)
"""
from datetime import datetime

from pydantic import BaseModel, ValidationError

from src.schemas.agents.base import AgentContractViolation, HandoffRecord
from src.schemas.agents.categorizer import CategorizerOutput, CategorizerBatchOutput
from src.schemas.agents.debt_detector import DebtDetectorOutput, DebtSummary
from src.schemas.agents.pattern_analyzer import PatternResult
from src.schemas.agents.predictor import PredictionResult
from src.schemas.agents.query import QueryResponse
from src.schemas.agents.advisor import AdviceResponse

# Maps (from_agent, to_agent) -> expected output type from from_agent
HANDOFF_CONTRACTS: dict[tuple[str, str], type[BaseModel]] = {
    ("AG-01", "AG-02"): CategorizerOutput,
    ("AG-01", "AG-02-batch"): CategorizerBatchOutput,
    ("AG-02", "AG-03"): DebtDetectorOutput,
    ("AG-02-summary", "AG-03"): DebtSummary,
    ("AG-03", "AG-04"): PatternResult,
    ("AG-04", "AG-06"): PredictionResult,
    ("AG-05", "response"): QueryResponse,
    ("AG-06", "response"): AdviceResponse,
}


class AgentPipeline:
    """Validates contracts between agents and maintains audit trail."""

    def __init__(self) -> None:
        self.handoff_history: list[HandoffRecord] = []

    def validate_handoff(
        self,
        from_agent: str,
        to_agent: str,
        data: dict,
    ) -> BaseModel:
        """Validate that data matches the expected contract for this handoff.

        Args:
            from_agent: Source agent ID (e.g. "AG-01")
            to_agent: Target agent ID (e.g. "AG-02")
            data: Raw dict output from the source agent

        Returns:
            Validated Pydantic model instance

        Raises:
            AgentContractViolation: If data doesn't match expected schema
        """
        key = (from_agent, to_agent)
        contract_type = HANDOFF_CONTRACTS.get(key)

        if contract_type is None:
            raise AgentContractViolation(
                from_agent, to_agent,
                f"No contract defined for handoff {from_agent} -> {to_agent}"
            )

        try:
            validated = contract_type.model_validate(data)
        except ValidationError as e:
            self._record_handoff(from_agent, to_agent, success=False, error=str(e))
            raise AgentContractViolation(
                from_agent, to_agent,
                f"Schema validation failed: {e}"
            ) from e

        self._record_handoff(from_agent, to_agent, success=True)
        return validated

    def _record_handoff(
        self,
        from_agent: str,
        to_agent: str,
        success: bool,
        error: str | None = None,
    ) -> None:
        self.handoff_history.append(
            HandoffRecord(
                from_agent=from_agent,
                to_agent=to_agent,
                timestamp=datetime.now(tz=None),
                success=success,
                error_message=error,
            )
        )

    def get_history(self) -> list[HandoffRecord]:
        """Return the full handoff audit trail."""
        return self.handoff_history

    def reset(self) -> None:
        """Clear handoff history for a new pipeline run."""
        self.handoff_history.clear()
