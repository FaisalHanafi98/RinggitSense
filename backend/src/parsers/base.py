"""
RinggitSense - Base parser class for bank statements
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import BinaryIO, Optional
import csv
import io


class TransactionType(str, Enum):
    """Transaction type (debit or credit)."""
    DEBIT = "debit"
    CREDIT = "credit"


@dataclass
class ParsedTransaction:
    """A single parsed transaction from a bank statement."""
    transaction_date: date
    description: str
    amount: Decimal
    transaction_type: TransactionType
    balance: Optional[Decimal] = None
    reference: Optional[str] = None
    raw_data: dict = field(default_factory=dict)

    @property
    def signed_amount(self) -> Decimal:
        """Return amount with sign (positive for debit/expense, negative for credit/income)."""
        if self.transaction_type == TransactionType.CREDIT:
            return -self.amount
        return self.amount


@dataclass
class ParserResult:
    """Result of parsing a bank statement."""
    transactions: list[ParsedTransaction]
    bank_name: str
    account_number: Optional[str] = None
    statement_period_start: Optional[date] = None
    statement_period_end: Optional[date] = None
    opening_balance: Optional[Decimal] = None
    closing_balance: Optional[Decimal] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Return True if parsing was successful (has transactions, no errors)."""
        return len(self.transactions) > 0 and len(self.errors) == 0

    @property
    def transaction_count(self) -> int:
        """Return number of parsed transactions."""
        return len(self.transactions)


class BaseParser(ABC):
    """Abstract base class for bank statement parsers."""

    BANK_NAME: str = "Unknown"
    SUPPORTED_FORMATS: list[str] = ["csv"]

    def parse(self, file_content: str | bytes, filename: str = "") -> ParserResult:
        """
        Parse a bank statement file.

        Args:
            file_content: File content as string (CSV) or bytes (PDF)
            filename: Original filename (used for format detection)

        Returns:
            ParserResult with parsed transactions
        """
        file_ext = filename.lower().split(".")[-1] if filename else ""

        if isinstance(file_content, bytes):
            # Try to decode as text for CSV
            try:
                file_content = file_content.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    file_content = file_content.decode("latin-1")
                except UnicodeDecodeError:
                    # Binary content (PDF)
                    if file_ext == "pdf" or not file_ext:
                        return self.parse_pdf(file_content)
                    raise ValueError("Unable to decode file content")

        # Text content - assume CSV
        if file_ext == "csv" or not file_ext:
            return self.parse_csv(file_content)
        elif file_ext == "pdf":
            raise ValueError("PDF content should be bytes, not string")
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    @abstractmethod
    def parse_csv(self, content: str) -> ParserResult:
        """Parse CSV content. Must be implemented by subclasses."""
        pass

    def parse_pdf(self, content: bytes) -> ParserResult:
        """Parse PDF content. Override in subclasses that support PDF."""
        return ParserResult(
            transactions=[],
            bank_name=self.BANK_NAME,
            errors=["PDF parsing not implemented for this bank"],
        )

    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string to Decimal, handling Malaysian formats."""
        if not amount_str:
            return Decimal("0")

        # Remove currency symbols and whitespace
        cleaned = amount_str.strip()
        cleaned = cleaned.replace("RM", "").replace("MYR", "").strip()

        # Handle negative amounts in parentheses: (100.00) -> -100.00
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = "-" + cleaned[1:-1]

        # Remove thousand separators (comma in MY format)
        cleaned = cleaned.replace(",", "")

        try:
            return Decimal(cleaned)
        except Exception:
            return Decimal("0")

    def _parse_date(self, date_str: str, formats: list[str] | None = None) -> date | None:
        """Parse date string using common Malaysian formats."""
        from datetime import datetime

        if not date_str:
            return None

        date_str = date_str.strip()

        # Common date formats in Malaysian bank statements
        if formats is None:
            formats = [
                "%d/%m/%Y",  # 15/01/2026
                "%d-%m-%Y",  # 15-01-2026
                "%Y-%m-%d",  # 2026-01-15
                "%d %b %Y",  # 15 Jan 2026
                "%d %B %Y",  # 15 January 2026
                "%d/%m/%y",  # 15/01/26
            ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        return None

    def _clean_description(self, description: str) -> str:
        """Clean and normalize transaction description."""
        if not description:
            return ""

        # Remove extra whitespace
        cleaned = " ".join(description.split())

        # Remove common prefixes
        prefixes_to_remove = [
            "IBG CR",
            "IBG DR",
            "INSTANT",
            "DUITNOW",
            "FPX",
        ]

        for prefix in prefixes_to_remove:
            if cleaned.upper().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()

        return cleaned
