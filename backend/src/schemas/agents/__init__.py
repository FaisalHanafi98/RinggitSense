"""
RinggitSense - Agent data contracts.

Pydantic models defining the input/output schemas for the 6-agent pipeline.
"""
from src.schemas.agents.enums import (
    AdviceCategory,
    ConfidenceLevel,
    DebtDirection,
    DebtTier,
    Difficulty,
    PatternType,
    TransactionCategory,
    Trend,
)
from src.schemas.agents.base import (
    AgentContractViolation,
    BaseAgentInput,
    BaseAgentOutput,
    HandoffRecord,
)
from src.schemas.agents.categorizer import (
    CategorizerBatchInput,
    CategorizerBatchOutput,
    CategorizerInput,
    CategorizerOutput,
)
from src.schemas.agents.debt_detector import (
    DebtDetectorInput,
    DebtDetectorOutput,
    DebtSummary,
)
from src.schemas.agents.pattern_analyzer import (
    PatternAnalyzerInput,
    PatternItem,
    PatternResult,
)
from src.schemas.agents.predictor import (
    PredictionResult,
    PredictorInput,
)
from src.schemas.agents.query import (
    QueryInput,
    QueryResponse,
)
from src.schemas.agents.advisor import (
    AdvisorInput,
    AdviceResponse,
    Recommendation,
)
from src.schemas.agents.pipeline import AgentPipeline

__all__ = [
    # Enums
    "AdviceCategory",
    "ConfidenceLevel",
    "DebtDirection",
    "DebtTier",
    "Difficulty",
    "PatternType",
    "TransactionCategory",
    "Trend",
    # Base
    "AgentContractViolation",
    "BaseAgentInput",
    "BaseAgentOutput",
    "HandoffRecord",
    # AG-01 Categorizer
    "CategorizerBatchInput",
    "CategorizerBatchOutput",
    "CategorizerInput",
    "CategorizerOutput",
    # AG-02 Debt Detector
    "DebtDetectorInput",
    "DebtDetectorOutput",
    "DebtSummary",
    # AG-03 Pattern Analyzer
    "PatternAnalyzerInput",
    "PatternItem",
    "PatternResult",
    # AG-04 Predictor
    "PredictorInput",
    "PredictionResult",
    # AG-05 Query
    "QueryInput",
    "QueryResponse",
    # AG-06 Advisor
    "AdvisorInput",
    "AdviceResponse",
    "Recommendation",
    # Pipeline
    "AgentPipeline",
]
