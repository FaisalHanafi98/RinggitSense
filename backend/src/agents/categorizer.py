"""
RinggitSense - AG-01 Categorizer Agent.

Classifies Malaysian bank/e-wallet transactions into spending categories.
Model: claude-sonnet-4 | Temperature: 0.2
"""
import logging
import time
from typing import Any

from src.agents.base import BaseAgent
from src.schemas.agents.categorizer import (
    CategorizerBatchOutput,
    CategorizerBatchResultItem,
    CategorizerOutput,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the Categorizer Agent for RinggitSense, a Malaysian personal finance app.

YOUR SINGLE RESPONSIBILITY: Classify transactions into spending categories.

You MUST:
1. Analyze the transaction description, amount, and source
2. Assign exactly ONE category from the allowed list
3. Provide a confidence score (0.0 to 1.0)
4. Extract merchant name when identifiable
5. Suggest subcategory when applicable

You MUST NOT:
- Provide financial advice
- Detect or comment on debt patterns
- Make predictions about future spending
- Answer general questions

CATEGORIES (choose exactly one):
- FOOD: Restaurants, groceries, food delivery, mamak, hawker
- TRANSPORT: Toll, petrol, parking, Grab rides, public transport
- BILLS: Utilities (TNB, water), phone, internet, subscriptions
- ENTERTAINMENT: Movies, games, streaming, hobbies, leisure
- SHOPPING: Retail, online shopping (Shopee, Lazada), clothing
- TRANSFER: Money transfers to other accounts or people
- DEBT_PAYMENT: Loan payments, BNPL installments, credit card payments
- INCOME: Salary, deposits, refunds, cashback
- HEALTHCARE: Medical, pharmacy, clinic, hospital, insurance
- OTHER: Only when truly unclassifiable

MALAYSIAN CONTEXT YOU MUST KNOW:
- Toll plazas: PLUS, LDP, DUKE, SMART, AKLEH, KESAS, MEX, NPE
- E-wallets: Touch 'n Go (TnG, T&G), GrabPay, ShopeePay, Boost
- Banks: Maybank, CIMB, RHB, Public Bank, Hong Leong, Aeon
- Common terms: "Makan", "Minum", "Bayar", "Topup", "Reload"
- Mamak/Kedai descriptions: "Restoran", "Kedai Runcit", "Warung"
- BNPL indicators: SPayLater, GrabPayLater, Atome

CONFIDENCE GUIDELINES:
- 0.95+: Clear merchant match (e.g., "MCDONALD'S" -> FOOD)
- 0.80-0.94: Strong contextual match (e.g., "PLUS TOLL" -> TRANSPORT)
- 0.60-0.79: Reasonable inference (e.g., "TRX KL" -> likely SHOPPING)
- Below 0.60: Flag for user review

OUTPUT FORMAT (JSON only, no markdown):
{"category": "CATEGORY_NAME", "confidence": 0.XX, "subcategory": "optional_or_null", "merchant_name": "extracted_or_null", "reasoning": "brief_explanation"}"""

BATCH_SYSTEM_PROMPT = SYSTEM_PROMPT + """

You are processing a BATCH of transactions. For each transaction in the input array,
return a corresponding result in the output array. Maintain the same order and IDs.

OUTPUT FORMAT (JSON only, no markdown):
{"results": [{"id": "txn_id", "category": "CATEGORY_NAME", "confidence": 0.XX, "subcategory": "optional_or_null", "merchant_name": "extracted_or_null", "reasoning": "brief_explanation"}, ...]}"""


class CategorizerAgent(BaseAgent):
    """AG-01: Transaction categorization agent."""

    AGENT_ID = "AG-01"
    AGENT_NAME = "Categorizer"
    TEMPERATURE = 0.2
    MAX_TOKENS = 512

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPT

    def categorize(
        self,
        description: str,
        amount: float,
        source: str,
        date: str,
        comment: str | None = None,
    ) -> CategorizerOutput:
        """Categorize a single transaction.

        Returns:
            Validated CategorizerOutput.
        """
        data: dict[str, Any] = {
            "description": description,
            "amount": amount,
            "source": source,
            "date": date,
        }
        if comment:
            data["comment"] = comment

        raw = self.invoke(data)

        # Normalize category to uppercase for enum matching
        if "category" in raw and isinstance(raw["category"], str):
            raw["category"] = raw["category"].upper()

        return CategorizerOutput(**raw)

    def categorize_batch(
        self,
        transactions: list[dict[str, Any]],
    ) -> CategorizerBatchOutput:
        """Categorize a batch of transactions (max 50).

        Args:
            transactions: List of dicts with id, description, amount, source, date.

        Returns:
            Validated CategorizerBatchOutput.
        """
        if len(transactions) > 50:
            raise ValueError("Batch size exceeds maximum of 50 transactions")

        start_time = time.monotonic()

        # Use batch system prompt
        message = self._client.messages.create(
            model=self.MODEL,
            max_tokens=4096,  # Larger for batch
            temperature=self.TEMPERATURE,
            system=BATCH_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": self._build_user_message({"transactions": transactions})},
            ],
        )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        raw = self._parse_json_response(self._first_text_block(message))

        results: list[CategorizerBatchResultItem] = []
        error_count = 0

        for item in raw.get("results", []):
            try:
                if "category" in item and isinstance(item["category"], str):
                    item["category"] = item["category"].upper()
                results.append(CategorizerBatchResultItem(**item))
            except Exception:
                error_count += 1
                logger.warning("Failed to parse batch result item: %s", item)

        return CategorizerBatchOutput(
            results=results,
            processing_time_ms=elapsed_ms,
            success_count=len(results),
            error_count=error_count,
        )
