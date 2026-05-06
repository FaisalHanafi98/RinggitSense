"""
RinggitSense - AG-02 Debt Detector Agent.

Classifies Malaysian bank transactions into three debt tiers:
  FORMAL — Bank loans, PTPTN, ASB financing, hire purchase, housing loans, credit cards
  BNPL   — SPayLater, GrabPayLater, Atome, Hoolah, Split
  HUTANG — Informal borrowing (pinjam, hutang, bayar balik + person name)

Model: claude-sonnet-4 | Temperature: 0.1
"""
import logging
import time
from typing import Any

from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.schemas.agents.debt_detector import (
    DebtDetectorOutput,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Debt Detector Agent for RinggitSense, a Malaysian personal finance app.

YOUR SINGLE RESPONSIBILITY: Identify whether a transaction is debt-related and classify it.

You MUST:
1. Analyze the transaction description, amount, and context
2. Determine if the transaction is debt-related
3. If debt-related, classify into exactly ONE tier: FORMAL, BNPL, or HUTANG
4. Provide a confidence score (0.0 to 1.0)
5. List specific indicators that led to your classification
6. Extract provider name or person name when identifiable

You MUST NOT:
- Provide financial advice
- Categorize non-debt transactions into spending categories
- Make predictions about future debt behavior
- Answer general questions

THREE-TIER DEBT CLASSIFICATION:

FORMAL — Institutional / regulated debt:
  - Bank loans: personal loan, housing loan / mortgage, car loan / hire purchase
  - Education: PTPTN (Perbadanan Tabung Pendidikan Tinggi Nasional)
  - Investment: ASB financing (Amanah Saham Bumiputera)
  - Credit cards: monthly credit card payments
  - Keywords: "loan", "financing", "hire purchase", "housing loan", "credit card",
    "PTPTN", "ASB", "installment" (from bank)
  - Providers: Maybank, CIMB, RHB, Public Bank, Hong Leong, Aeon Bank, PTPTN, ASB

BNPL — Buy Now Pay Later platforms:
  - SPayLater (Shopee), GrabPayLater, Atome, Hoolah, Split
  - Indicators: provider name + "installment", "payment X/Y" pattern (e.g., "2/3", "1/4")
  - Usually smaller amounts (RM20-500 per installment)
  - Keywords: "SPayLater", "GrabPayLater", "Atome", "Hoolah", "Split", "installment"

HUTANG — Informal debt between individuals:
  - Borrowing from or lending to family/friends
  - Malay keywords: "pinjam" (borrow), "hutang" (owe/debt), "bayar balik" (pay back)
  - Often includes a person's name
  - Transfer descriptions with debt context
  - Keywords: "pinjam", "hutang", "bayar balik", "duit" (money) + person name

IMPORTANT DISTINCTIONS:
- Regular transfers (e.g., "TRANSFER TO ALI") are NOT automatically debt
- Only classify as HUTANG if debt keywords (pinjam/hutang/bayar balik) are present
- Insurance payments are NOT debt (they are expenses)
- Subscription payments are NOT debt (they are bills)
- E-wallet top-ups are NOT debt (they are transfers)

CONFIDENCE GUIDELINES:
- 0.90+: Exact keyword match (e.g., "PTPTN REPAYMENT", "SPAYLATER INSTALLMENT")
- 0.80-0.89: Strong contextual match (e.g., "MAYBANK HIRE PURCHASE")
- 0.70-0.79: Reasonable inference (e.g., "BAYAR HUTANG KAMAL")
- Below 0.70: Uncertain — flag for user review

OUTPUT FORMAT (JSON only, no markdown):
{"is_debt_related": true/false, "debt_tier": "FORMAL"/"BNPL"/"HUTANG"/null, "debt_type": "education_loan"/"personal_loan"/"housing_loan"/"hire_purchase"/"credit_card"/"investment_loan"/"installment"/"informal_loan"/"informal_repayment"/null, "provider": "provider_name_or_null", "confidence": 0.XX, "indicators": ["keyword1", "keyword2"], "estimated_monthly": amount_or_null, "person_name": "name_or_null"}"""

BATCH_SYSTEM_PROMPT = SYSTEM_PROMPT + """

You are processing a BATCH of transactions. For each transaction in the input array,
return a corresponding result in the output array. Maintain the same order and IDs.

OUTPUT FORMAT (JSON only, no markdown):
{"results": [{"id": "txn_id", "is_debt_related": true/false, "debt_tier": "FORMAL"/"BNPL"/"HUTANG"/null, "debt_type": "type_or_null", "provider": "provider_or_null", "confidence": 0.XX, "indicators": ["keyword1"], "estimated_monthly": amount_or_null, "person_name": "name_or_null"}, ...]}"""


class DebtDetectorBatchResultItem(DebtDetectorOutput):
    """Single item in a batch detection result."""
    id: str


class DebtDetectorBatchResult(BaseModel):
    """Batch output from AG-02 Debt Detector."""
    results: list[DebtDetectorBatchResultItem] = Field(default_factory=list)
    processing_time_ms: int = 0
    success_count: int = 0
    error_count: int = 0


class DebtDetectorAgent(BaseAgent):
    """AG-02: Three-tier debt detection agent for Malaysian transactions."""

    AGENT_ID = "AG-02"
    AGENT_NAME = "Debt Detector"
    TEMPERATURE = 0.1
    MAX_TOKENS = 1024

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def detect(
        self,
        description: str,
        amount: float,
        source: str,
        is_recurring: bool = False,
        comment: str | None = None,
    ) -> DebtDetectorOutput:
        """Detect debt in a single transaction.

        Returns:
            Validated DebtDetectorOutput.
        """
        data: dict[str, Any] = {
            "description": description,
            "amount": amount,
            "source": source,
            "is_recurring": is_recurring,
        }
        if comment:
            data["comment"] = comment

        raw = self.invoke(data)

        # Normalize debt_tier to uppercase for enum matching
        if "debt_tier" in raw and isinstance(raw["debt_tier"], str):
            raw["debt_tier"] = raw["debt_tier"].upper()

        return DebtDetectorOutput(**raw)

    def detect_batch(
        self,
        transactions: list[dict[str, Any]],
    ) -> DebtDetectorBatchResult:
        """Detect debt in a batch of transactions (max 50).

        Args:
            transactions: List of dicts with id, description, amount, source.

        Returns:
            DebtDetectorBatchResult with per-transaction results.
        """
        if len(transactions) > 50:
            raise ValueError("Batch size exceeds maximum of 50 transactions")

        start_time = time.monotonic()

        message = self._client.messages.create(
            model=self.MODEL,
            max_tokens=4096,
            temperature=self.TEMPERATURE,
            system=BATCH_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": self._build_user_message({"transactions": transactions})},
            ],
        )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        raw = self._parse_json_response(self._first_text_block(message))

        results: list[DebtDetectorBatchResultItem] = []
        error_count = 0

        for item in raw.get("results", []):
            try:
                if "debt_tier" in item and isinstance(item["debt_tier"], str):
                    item["debt_tier"] = item["debt_tier"].upper()
                results.append(DebtDetectorBatchResultItem(**item))
            except Exception:
                error_count += 1
                logger.warning("Failed to parse batch result item: %s", item)

        return DebtDetectorBatchResult(
            results=results,
            processing_time_ms=elapsed_ms,
            success_count=len(results),
            error_count=error_count,
        )
