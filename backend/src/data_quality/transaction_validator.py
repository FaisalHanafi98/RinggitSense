"""
RinggitSense - Transaction data quality validation.

Implements validation layers L1-L4 from the controlled strategy session:
  L1: File validation (handled at upload endpoint level)
  L2: Parse validation (individual transaction)
  L3: Business validation (batch-level)
  L4: Deduplication (cross-reference with existing data)
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum

from src.parsers.base import ParsedTransaction, ParserResult


class DuplicateStatus(str, Enum):
    """Result of duplicate check."""
    UNIQUE = "UNIQUE"
    DUPLICATE = "DUPLICATE"
    SUSPICIOUS = "SUSPICIOUS"


@dataclass
class ValidationResult:
    """Result of validating a single transaction."""
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class BatchValidationResult:
    """Result of validating a batch of transactions."""
    total: int
    valid: int
    invalid: int
    results: list[ValidationResult] = field(default_factory=list)
    batch_warnings: list[str] = field(default_factory=list)

    @property
    def all_valid(self) -> bool:
        return self.invalid == 0


@dataclass
class DuplicateCheckResult:
    """Result of checking a transaction for duplicates."""
    status: DuplicateStatus
    matching_description: str | None = None


# Earliest reasonable transaction date for Malaysian bank statements
_MIN_DATE = date(2000, 1, 1)


class TransactionValidator:
    """Validates parsed transactions before database insertion.

    Implements validation layers L2-L4 from the data integrity plan.
    """

    # --- L2: Parse Validation (individual transaction) ---

    def validate_parsed_transaction(
        self, txn: ParsedTransaction
    ) -> ValidationResult:
        """Validate a single parsed transaction.

        Checks:
        - Amount is non-zero
        - Transaction date is not in the future
        - Transaction date is not before 2000-01-01
        - Description is non-empty after stripping
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Amount must be non-zero
        if txn.amount == Decimal("0"):
            errors.append("Transaction amount is zero")

        # Date must not be in the future
        today = date.today()
        if txn.transaction_date > today:
            errors.append(
                f"Transaction date {txn.transaction_date} is in the future"
            )

        # Date must not be unreasonably old
        if txn.transaction_date < _MIN_DATE:
            errors.append(
                f"Transaction date {txn.transaction_date} is before {_MIN_DATE}"
            )

        # Description must be non-empty
        if not txn.description or not txn.description.strip():
            errors.append("Transaction description is empty")

        # Warn on very large amounts (>RM100,000 single transaction)
        if txn.amount > Decimal("100000"):
            warnings.append(
                f"Unusually large amount: RM{txn.amount}"
            )

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    # --- L3: Business Validation (batch-level) ---

    def validate_batch(
        self, result: ParserResult
    ) -> BatchValidationResult:
        """Validate a batch of parsed transactions.

        Checks:
        - All individual transactions pass L2 validation
        - Chronological order (warn if out of order)
        - Balance reconciliation (if opening/closing balance provided)
        """
        individual_results: list[ValidationResult] = []
        valid_count = 0
        invalid_count = 0
        batch_warnings: list[str] = []

        # Validate each transaction individually
        for txn in result.transactions:
            vr = self.validate_parsed_transaction(txn)
            individual_results.append(vr)
            if vr.is_valid:
                valid_count += 1
            else:
                invalid_count += 1

        # Check chronological order
        if len(result.transactions) >= 2:
            dates = [t.transaction_date for t in result.transactions]
            if dates != sorted(dates) and dates != sorted(dates, reverse=True):
                batch_warnings.append(
                    "Transactions are not in chronological order"
                )

        # Balance reconciliation
        if (
            result.opening_balance is not None
            and result.closing_balance is not None
            and result.transactions
        ):
            total_debits = sum(
                t.amount for t in result.transactions
                if t.transaction_type.value == "debit"
            )
            total_credits = sum(
                t.amount for t in result.transactions
                if t.transaction_type.value == "credit"
            )
            expected_closing = (
                result.opening_balance - total_debits + total_credits
            )
            if expected_closing != result.closing_balance:
                batch_warnings.append(
                    f"Balance mismatch: expected RM{expected_closing}, "
                    f"got RM{result.closing_balance}"
                )

        return BatchValidationResult(
            total=len(result.transactions),
            valid=valid_count,
            invalid=invalid_count,
            results=individual_results,
            batch_warnings=batch_warnings,
        )

    # --- L4: Deduplication ---

    def check_duplicates(
        self,
        txn: ParsedTransaction,
        existing: list[ParsedTransaction],
    ) -> DuplicateCheckResult:
        """Check if a transaction is a duplicate of existing transactions.

        Returns:
        - DUPLICATE: Exact match on date + amount + description
        - SUSPICIOUS: Same date + amount, different description
        - UNIQUE: No match found
        """
        for existing_txn in existing:
            same_date = txn.transaction_date == existing_txn.transaction_date
            same_amount = txn.amount == existing_txn.amount
            same_desc = (
                txn.description.strip().lower()
                == existing_txn.description.strip().lower()
            )

            if same_date and same_amount and same_desc:
                return DuplicateCheckResult(
                    status=DuplicateStatus.DUPLICATE,
                    matching_description=existing_txn.description,
                )

            if same_date and same_amount and not same_desc:
                return DuplicateCheckResult(
                    status=DuplicateStatus.SUSPICIOUS,
                    matching_description=existing_txn.description,
                )

        return DuplicateCheckResult(status=DuplicateStatus.UNIQUE)
