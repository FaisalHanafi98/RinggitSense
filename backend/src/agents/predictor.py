"""
RinggitSense - AG-04 Predictor Agent.

Forecasts next-month spending from historical categorized transactions,
known upcoming events, and AG-03 pattern context.

Scope (IN):
  Total spending prediction
  Category-level forecasts
  Confidence intervals
  Trend and seasonal context from prior stages

Scope (OUT):
  Financial advice - handled by AG-06 Advisor
  Pattern discovery - handled by AG-03 Pattern Analyzer
  Transaction categorization - handled by AG-01 Categorizer
  Debt detection - handled by AG-02 Debt Detector

Model: claude-sonnet-4-20250514 | Temperature: 0.3
"""
import logging
from typing import Any

from src.agents.base import BaseAgent
from src.schemas.agents.predictor import PredictionResult, UpcomingItem

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Predictor Agent for RinggitSense, a Malaysian personal finance app.

YOUR SINGLE RESPONSIBILITY: Forecast next-month spending.

You MUST:
1. Use historical categorized spending summaries as the prediction baseline
2. Use AG-03 Pattern Analyzer context only as evidence for trend adjustments
3. Account for Malaysian seasonal factors when present in the input
4. Incorporate known upcoming bills or income when provided
5. Provide a 90% confidence interval
6. Break predictions down by category
7. Include "Past patterns do not guarantee future results" in risks

You MUST NOT:
- Provide financial advice
- Discover new spending patterns
- Categorize individual transactions
- Detect or comment on debt
- Invent Malaysian regulations, bank formats, or unsupported events

PREDICTION FACTORS:

HISTORICAL BASELINE:
- Primary: weighted average of recent months, weighted toward newer data
- Fallback: simple average when history is sparse
- By category: calculate per spending category

TREND ADJUSTMENT:
- RISING: if prior evidence shows a rising category trend
- FALLING: if prior evidence shows a falling category trend
- STABLE: when no reliable trend evidence exists

MALAYSIAN CONTEXT:
- Currency is RM (Malaysian Ringgit)
- Consider known seasonal context only when present in input
- Mention uncertainty using risks instead of inventing facts

OUTPUT FORMAT (JSON only, no markdown):
{
  "total_predicted": 0.0,
  "confidence_interval": {"low": 0.0, "high": 0.0},
  "by_category": [
    {"category": "FOOD", "predicted": 0.0, "trend": "RISING|STABLE|FALLING"}
  ],
  "assumptions": ["list of assumptions"],
  "risks": ["Past patterns do not guarantee future results"]
}"""


class PredictorAgent(BaseAgent):
    """AG-04: Spending forecast agent for Malaysian financial data."""

    AGENT_ID = "AG-04"
    AGENT_NAME = "Predictor"
    TEMPERATURE = 0.3
    MAX_TOKENS = 4096

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def predict(
        self,
        historical_transactions: list[dict[str, Any]],
        prediction_month: str,
        known_upcoming: list[dict[str, Any]] | None = None,
        pattern_context: dict[str, Any] | None = None,
    ) -> PredictionResult:
        """Forecast next-month spending.

        Args:
            historical_transactions: Categorized historical transactions or
                category-month summaries.
            prediction_month: Month to forecast in YYYY-MM format.
            known_upcoming: Optional known bills/income.
            pattern_context: Optional AG-03 Pattern Analyzer output.

        Returns:
            Validated PredictionResult.

        Raises:
            ValueError: If no historical data is available or Claude returns
                unparseable JSON.
            pydantic.ValidationError: If the parsed JSON fails schema validation.
        """
        if not historical_transactions:
            raise ValueError("historical_transactions are required for AG-04 prediction")

        payload: dict[str, Any] = {
            "historical_transactions": historical_transactions,
            "prediction_month": prediction_month,
        }

        if known_upcoming:
            payload["known_upcoming"] = [UpcomingItem(**item).model_dump() for item in known_upcoming]

        if pattern_context:
            payload["pattern_context"] = pattern_context

        raw = self.invoke(payload)

        if "by_category" in raw and isinstance(raw["by_category"], list):
            for item in raw["by_category"]:
                if "trend" in item and isinstance(item["trend"], str):
                    item["trend"] = item["trend"].upper()

        logger.info(
            "%s predicted RM%.2f for %s",
            self.AGENT_ID,
            raw.get("total_predicted", 0.0),
            prediction_month,
        )

        return PredictionResult(**raw)
