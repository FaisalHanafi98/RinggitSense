"""
RinggitSense - AG-03 Pattern Analyzer Agent.

Discovers hidden patterns, trends, and anomalies in Malaysian spending data
that users wouldn't notice themselves. Reveals lifestyle bundles, temporal
patterns, and hidden costs unique to Malaysian spending habits.

Scope (IN):
  Temporal pattern detection (weekend surges, payday effects, month-end)
  Lifestyle bundle identification (commute, night-out, shopping-day)
  Hidden cost aggregation (toll, delivery fees, subscriptions)
  Anomaly detection (spending spikes, merchant concentration)
  Trend analysis (rising/falling category spend over time)

Scope (OUT):
  Financial advice — handled by AG-06 Advisor
  Spending predictions — handled by AG-04 Predictor
  Individual transaction categorization — handled by AG-01 Categorizer
  Debt tracking — handled by AG-02 Debt Detector

Model: claude-sonnet-4-20250514 | Temperature: 0.5
"""
import logging
from typing import Any

from src.agents.base import BaseAgent
from src.schemas.agents.pattern_analyzer import PatternResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Pattern Analyzer Agent for RinggitSense, a Malaysian personal finance app.

YOUR SINGLE RESPONSIBILITY: Discover hidden patterns in spending data.

You MUST:
1. Analyze transaction history for non-obvious patterns
2. Identify lifestyle bundles (expenses that occur together)
3. Calculate hidden costs (toll, delivery fees, subscriptions)
4. Detect temporal patterns (weekend, payday, month-end)
5. Flag anomalies and unusual spending (including category concentration)

You MUST NOT:
- Provide financial advice
- Make predictions about future spending
- Categorize individual transactions
- Track or analyze debt

PATTERN CATEGORIES:

TEMPORAL — Time-based spending variations:
  - Weekend effect: Higher spending Fri-Sun
  - Payday surge: Spike after salary credit (25th-28th most common)
  - Month-end squeeze: Reduced spending last week
  - Festival spikes: Raya, CNY, Deepavali periods

BUNDLE — Co-occurring expenses (same day, within 2-hour window, repeat >5x):
  - Morning commute: Toll + Petrol + Coffee
  - Night out: Entertainment + F&B + Transport (Grab)
  - Shopping day: Mall parking + Shopping + F&B
  - Weekend trip: Petrol + Toll + F&B + Activities

HIDDEN_COST — Underestimated recurring expenses (often 40-60% higher than user estimates):
  - Toll: Aggregate all PLUS, LDP, DUKE, SMART, AKLEH, KESAS, MEX, NPE
  - Delivery fees: GrabFood, Foodpanda, Shopee
  - Subscriptions: Netflix, Spotify, Astro, gym, broadband
  - Platform fees: E-wallet charges, transfer fees

TREND — Direction of spending over time:
  - Rising: Category spend increasing month-over-month
  - Falling: Category spend decreasing month-over-month
  - Use TREND for category-level changes, not individual transactions

ANOMALY — Unusual spending events:
  - One-off spikes significantly above category average (>3x)
  - New merchants that never appeared before
  - Single category dominating >40% of total spend (merchant concentration)

MALAYSIAN CONTEXT:
- Toll highways: PLUS, LDP, DUKE, SMART, AKLEH, KESAS, MEX, NPE
- Festival periods: Hari Raya (variable), CNY (Jan/Feb), Deepavali (Oct/Nov)
- Payday patterns: 25th-28th most common in Malaysia
- Weekend definition: Fri evening to Sun (important for Muslim-majority context)
- Common subscriptions: Netflix, Spotify, Astro, Unifi, Maxis, Celcom, TNB, SYABAS

CONFIDENCE GUIDELINES:
- 0.90+: Clear, high-frequency repeating pattern with strong evidence
- 0.80-0.89: Strong contextual match with 2+ months of data
- 0.70-0.79: Reasonable inference from partial data
- Below 0.70: Flag as uncertain — include in output but note low confidence

OUTPUT FORMAT (JSON only, no markdown):
{
  "patterns": [
    {
      "type": "TEMPORAL|BUNDLE|HIDDEN_COST|TREND|ANOMALY",
      "name": "pattern_name",
      "description": "what this means for the user",
      "evidence": ["specific transaction summaries or counts"],
      "impact": RM_amount_as_number,
      "confidence": 0.XX
    }
  ],
  "summary": "overall pattern summary in 1-2 sentences",
  "hidden_cost_total": total_RM_amount_of_HIDDEN_COST_patterns
}

Return an empty patterns array if no patterns are detected — never invent patterns."""


class PatternAnalyzerAgent(BaseAgent):
    """AG-03: Spending pattern discovery agent for Malaysian financial data.

    Accepts categorized transactions from AG-01 and optional debt signals
    from AG-02 to correlate BNPL usage with purchase-day patterns.

    Does NOT provide advice (AG-06), predictions (AG-04), or categorize
    individual transactions (AG-01).
    """

    AGENT_ID = "AG-03"
    AGENT_NAME = "Pattern Analyzer"
    TEMPERATURE = 0.5
    MAX_TOKENS = 4096

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def analyze(
        self,
        transactions: list[dict[str, Any]],
        period: str = "available",
        focus_areas: list[str] | None = None,
        debt_signals: dict[str, Any] | None = None,
    ) -> PatternResult:
        """Analyze spending patterns across categorized transactions.

        Args:
            transactions: List of categorized transaction dicts from AG-01.
                          Each dict should contain at minimum: id, date,
                          category, amount, description.
            period: Analysis window — "3_months", "6_months", or "available".
            focus_areas: Optional list of pattern types to prioritize, e.g.
                         ["hidden_costs", "bundles", "temporal"].
            debt_signals: Optional AG-02 output dict. When provided it is
                          included as "debt_context" in the prompt so the
                          agent can correlate BNPL usage with spending spikes.

        Returns:
            PatternResult containing detected patterns, summary, and
            total hidden cost identified.

        Raises:
            anthropic.APIError: On Claude API failures.
            ValueError: If the API response cannot be parsed as JSON.
            pydantic.ValidationError: If the parsed JSON fails schema validation.
        """
        payload: dict[str, Any] = {
            "transactions": transactions,
            "period": period,
        }

        if focus_areas:
            payload["focus_areas"] = focus_areas

        if debt_signals:
            payload["debt_context"] = debt_signals

        raw = self.invoke(payload)

        # Normalize pattern types — API may return lowercase
        if "patterns" in raw and isinstance(raw["patterns"], list):
            for pattern in raw["patterns"]:
                if "type" in pattern and isinstance(pattern["type"], str):
                    pattern["type"] = pattern["type"].upper()

        logger.info(
            "%s detected %d pattern(s) over period=%s",
            self.AGENT_ID,
            len(raw.get("patterns", [])),
            period,
        )

        return PatternResult(**raw)
