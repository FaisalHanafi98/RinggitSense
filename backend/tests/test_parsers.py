"""
Test bank statement parsers
"""
import pytest
from datetime import date
from decimal import Decimal

from src.parsers import (
    MaybankParser,
    CIMBParser,
    get_parser,
    detect_bank,
    ParsedTransaction,
    ParserResult,
)
from src.parsers.base import TransactionType


class TestParserImports:
    """Test that parser modules can be imported."""

    def test_import_parsers(self):
        from src.parsers import MaybankParser, CIMBParser, BaseParser
        assert MaybankParser is not None
        assert CIMBParser is not None
        assert BaseParser is not None

    def test_get_parser(self):
        maybank = get_parser("maybank")
        assert isinstance(maybank, MaybankParser)

        cimb = get_parser("cimb")
        assert isinstance(cimb, CIMBParser)

    def test_get_parser_case_insensitive(self):
        assert isinstance(get_parser("MAYBANK"), MaybankParser)
        assert isinstance(get_parser("Cimb"), CIMBParser)

    def test_get_parser_unknown(self):
        with pytest.raises(ValueError, match="Unknown bank code"):
            get_parser("unknown_bank")


class TestBankDetection:
    """Test automatic bank detection from content."""

    def test_detect_maybank(self):
        content = "Account Statement from Maybank for January 2026"
        assert detect_bank(content) == "maybank"

    def test_detect_maybank2u(self):
        content = "Downloaded from Maybank2u"
        assert detect_bank(content) == "maybank"

    def test_detect_cimb(self):
        content = "CIMB Bank Statement"
        assert detect_bank(content) == "cimb"

    def test_detect_unknown(self):
        content = "Some random bank statement"
        assert detect_bank(content) is None


class TestMaybankParser:
    """Test Maybank CSV parser."""

    def test_parse_simple_csv(self):
        csv_content = """Date,Description,Debit,Credit,Balance
15/01/2026,MAMAK RESTAURANT,-,25.50,1000.00
16/01/2026,SALARY,-,4500.00,5500.00
17/01/2026,GRAB TAXI,15.00,-,5485.00
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        assert result.success
        assert result.bank_name == "Maybank"
        assert result.transaction_count == 3

        # Check first transaction (credit)
        txn1 = result.transactions[0]
        assert txn1.transaction_date == date(2026, 1, 15)
        assert "MAMAK" in txn1.description.upper()
        assert txn1.amount == Decimal("25.50")
        assert txn1.transaction_type == TransactionType.CREDIT
        assert txn1.balance == Decimal("1000.00")

        # Check debit transaction
        txn3 = result.transactions[2]
        assert txn3.amount == Decimal("15.00")
        assert txn3.transaction_type == TransactionType.DEBIT

    def test_parse_different_date_format(self):
        csv_content = """Transaction Date,Details,Debit,Credit,Balance
2026-01-15,PAYMENT,100.00,-,900.00
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        assert result.success
        assert result.transactions[0].transaction_date == date(2026, 1, 15)

    def test_parse_with_reference(self):
        csv_content = """Date,Description,Debit,Credit,Balance,Reference
15/01/2026,DUITNOW TRANSFER,50.00,-,950.00,REF123456
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        assert result.success
        assert result.transactions[0].reference == "REF123456"

    def test_parse_empty_csv(self):
        csv_content = """Date,Description,Debit,Credit,Balance
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        # Empty CSV has no transactions, so success is False
        assert not result.success
        assert result.transaction_count == 0
        assert len(result.errors) == 0  # But no errors either

    def test_parse_no_headers(self):
        csv_content = """15/01/2026,PAYMENT,100.00,-,900.00
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        # Should fail gracefully
        assert not result.success or result.transaction_count == 0

    def test_parse_malformed_date(self):
        csv_content = """Date,Description,Debit,Credit,Balance
invalid-date,PAYMENT,100.00,-,900.00
15/01/2026,VALID,50.00,-,850.00
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        # Should skip invalid row but continue
        assert result.transaction_count == 1
        assert result.transactions[0].description == "VALID"

    def test_parse_amount_with_comma(self):
        csv_content = """Date,Description,Debit,Credit,Balance
15/01/2026,SALARY,-,"4,500.00","10,500.00"
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        assert result.success
        assert result.transactions[0].amount == Decimal("4500.00")
        assert result.transactions[0].balance == Decimal("10500.00")

    def test_parse_amount_with_rm(self):
        csv_content = """Date,Description,Debit,Credit,Balance
15/01/2026,PAYMENT,RM 100.00,-,RM 900.00
"""
        parser = MaybankParser()
        result = parser.parse_csv(csv_content)

        assert result.success
        assert result.transactions[0].amount == Decimal("100.00")


class TestCIMBParser:
    """Test CIMB CSV parser."""

    def test_parse_simple_csv(self):
        csv_content = """Date,Description,Debit,Credit,Balance
15/01/2026,CIMB ONLINE PAYMENT,50.00,-,950.00
16/01/2026,SALARY CREDIT,-,3000.00,3950.00
"""
        parser = CIMBParser()
        result = parser.parse_csv(csv_content)

        assert result.success
        assert result.bank_name == "CIMB"
        assert result.transaction_count == 2

    def test_parse_with_header_rows(self):
        """CIMB statements often have extra header rows."""
        csv_content = """CIMB Bank Berhad
Account Statement
Generated: 15/01/2026

Date,Description,Debit,Credit,Balance
15/01/2026,PAYMENT,100.00,-,900.00
"""
        parser = CIMBParser()
        result = parser.parse_csv(csv_content)

        assert result.success
        assert result.transaction_count == 1


class TestParsedTransaction:
    """Test ParsedTransaction data class."""

    def test_signed_amount_debit(self):
        txn = ParsedTransaction(
            transaction_date=date(2026, 1, 15),
            description="Test",
            amount=Decimal("100.00"),
            transaction_type=TransactionType.DEBIT,
        )
        assert txn.signed_amount == Decimal("100.00")

    def test_signed_amount_credit(self):
        txn = ParsedTransaction(
            transaction_date=date(2026, 1, 15),
            description="Test",
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
        )
        assert txn.signed_amount == Decimal("-100.00")


class TestParserResult:
    """Test ParserResult data class."""

    def test_success_with_transactions(self):
        txn = ParsedTransaction(
            transaction_date=date(2026, 1, 15),
            description="Test",
            amount=Decimal("100.00"),
            transaction_type=TransactionType.DEBIT,
        )
        result = ParserResult(
            transactions=[txn],
            bank_name="Test Bank",
        )
        assert result.success
        assert result.transaction_count == 1

    def test_failure_with_errors(self):
        result = ParserResult(
            transactions=[],
            bank_name="Test Bank",
            errors=["Something went wrong"],
        )
        assert not result.success

    def test_failure_no_transactions(self):
        result = ParserResult(
            transactions=[],
            bank_name="Test Bank",
        )
        assert not result.success
