"""
RinggitSense - CIMB statement parser
"""
import csv
import io
from decimal import Decimal

from src.parsers.base import (
    BaseParser,
    ParsedTransaction,
    ParserResult,
    TransactionType,
)


class CIMBParser(BaseParser):
    """Parser for CIMB bank statements (CSV and PDF)."""

    BANK_NAME = "CIMB"
    SUPPORTED_FORMATS = ["csv", "pdf"]

    # Common column names in CIMB CSV exports
    DATE_COLUMNS = ["date", "transaction date", "trans date", "value date", "posting date"]
    DESCRIPTION_COLUMNS = ["description", "details", "transaction description", "particulars", "narrative"]
    DEBIT_COLUMNS = ["debit", "withdrawal", "debit amount", "dr", "money out"]
    CREDIT_COLUMNS = ["credit", "deposit", "credit amount", "cr", "money in"]
    BALANCE_COLUMNS = ["balance", "running balance", "ledger balance"]
    REFERENCE_COLUMNS = ["reference", "ref", "reference no", "transaction ref"]

    def parse_csv(self, content: str) -> ParserResult:
        """Parse CIMB CSV export."""
        transactions: list[ParsedTransaction] = []
        errors: list[str] = []
        warnings: list[str] = []

        try:
            # Skip header lines that CIMB often includes
            lines = content.strip().split("\n")
            data_start = 0

            for i, line in enumerate(lines):
                # Look for the header row with column names
                line_lower = line.lower()
                if any(col in line_lower for col in ["date", "description", "debit", "credit"]):
                    data_start = i
                    break

            # Rejoin content from data start
            content = "\n".join(lines[data_start:])

            # Try to detect CSV dialect
            sample = content[:2048]
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel

            reader = csv.DictReader(io.StringIO(content), dialect=dialect)

            # Normalize column names
            if reader.fieldnames is None:
                errors.append("CSV file has no headers")
                return ParserResult(
                    transactions=[],
                    bank_name=self.BANK_NAME,
                    errors=errors,
                )

            # Create column mapping
            col_map = self._map_columns(list(reader.fieldnames))

            if not col_map.get("date"):
                errors.append("Could not find date column in CSV")
                return ParserResult(
                    transactions=[],
                    bank_name=self.BANK_NAME,
                    errors=errors,
                )

            row_num = data_start + 1
            for row in reader:
                row_num += 1
                try:
                    txn = self._parse_row(row, col_map, row_num)
                    if txn:
                        transactions.append(txn)
                except Exception as e:
                    warnings.append(f"Row {row_num}: {str(e)}")

        except csv.Error as e:
            errors.append(f"CSV parsing error: {str(e)}")
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")

        return ParserResult(
            transactions=transactions,
            bank_name=self.BANK_NAME,
            errors=errors,
            warnings=warnings,
        )

    def _map_columns(self, fieldnames: list[str]) -> dict[str, str]:
        """Map CSV column names to standard fields."""
        col_map: dict[str, str] = {}
        normalized = {name.lower().strip(): name for name in fieldnames}

        # Find date column
        for col in self.DATE_COLUMNS:
            if col in normalized:
                col_map["date"] = normalized[col]
                break

        # Find description column
        for col in self.DESCRIPTION_COLUMNS:
            if col in normalized:
                col_map["description"] = normalized[col]
                break

        # Find debit column
        for col in self.DEBIT_COLUMNS:
            if col in normalized:
                col_map["debit"] = normalized[col]
                break

        # Find credit column
        for col in self.CREDIT_COLUMNS:
            if col in normalized:
                col_map["credit"] = normalized[col]
                break

        # Find balance column
        for col in self.BALANCE_COLUMNS:
            if col in normalized:
                col_map["balance"] = normalized[col]
                break

        # Find reference column
        for col in self.REFERENCE_COLUMNS:
            if col in normalized:
                col_map["reference"] = normalized[col]
                break

        # Fallback: if no separate debit/credit, look for amount column
        if "debit" not in col_map and "credit" not in col_map:
            for key, val in normalized.items():
                if "amount" in key:
                    col_map["amount"] = val
                    break

        return col_map

    def _parse_row(
        self,
        row: dict[str, str],
        col_map: dict[str, str],
        row_num: int
    ) -> ParsedTransaction | None:
        """Parse a single CSV row into a transaction."""
        # Get date
        date_str = row.get(col_map.get("date", ""), "").strip()
        txn_date = self._parse_date(date_str)
        if not txn_date:
            return None  # Skip rows without valid date

        # Get description
        description = row.get(col_map.get("description", ""), "").strip()
        if not description:
            description = "Unknown transaction"

        # Get amount and type
        amount = Decimal("0")
        txn_type = TransactionType.DEBIT

        if "debit" in col_map and "credit" in col_map:
            # Separate debit/credit columns
            debit_str = row.get(col_map["debit"], "").strip()
            credit_str = row.get(col_map["credit"], "").strip()

            if debit_str and debit_str not in ["0", "0.00", "-", ""]:
                amount = self._parse_amount(debit_str)
                txn_type = TransactionType.DEBIT
            elif credit_str and credit_str not in ["0", "0.00", "-", ""]:
                amount = self._parse_amount(credit_str)
                txn_type = TransactionType.CREDIT
            else:
                return None  # No amount
        elif "amount" in col_map:
            # Single amount column (negative = debit, positive = credit)
            amount_str = row.get(col_map["amount"], "").strip()
            amount = self._parse_amount(amount_str)
            if amount < 0:
                amount = abs(amount)
                txn_type = TransactionType.DEBIT
            else:
                txn_type = TransactionType.CREDIT
        else:
            return None  # No amount columns

        if amount == Decimal("0"):
            return None

        # Get balance
        balance: Decimal | None = None
        if "balance" in col_map:
            balance_str = row.get(col_map["balance"], "").strip()
            if balance_str:
                balance = self._parse_amount(balance_str)

        # Get reference
        reference: str | None = None
        if "reference" in col_map:
            reference = row.get(col_map["reference"], "").strip() or None

        return ParsedTransaction(
            transaction_date=txn_date,
            description=self._clean_description(description),
            amount=amount,
            transaction_type=txn_type,
            balance=balance,
            reference=reference,
            raw_data=dict(row),
        )

    def parse_pdf(self, content: bytes) -> ParserResult:
        """Parse CIMB PDF statement."""
        # PDF parsing requires pdfplumber or similar library
        return ParserResult(
            transactions=[],
            bank_name=self.BANK_NAME,
            errors=["PDF parsing requires pdfplumber library. Please export as CSV from CIMB Clicks."],
        )
