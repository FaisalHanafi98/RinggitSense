"""
RinggitSense - Bank Statement Parsers

Supports parsing of Malaysian bank statements from:
- Maybank (CSV, PDF)
- CIMB (CSV, PDF)
- RHB (CSV, PDF)
- Touch 'n Go (CSV)
"""
from src.parsers.base import BaseParser, ParsedTransaction, ParserResult
from src.parsers.maybank import MaybankParser
from src.parsers.cimb import CIMBParser

__all__ = [
    "BaseParser",
    "ParsedTransaction",
    "ParserResult",
    "MaybankParser",
    "CIMBParser",
]


# Parser registry for auto-detection
PARSER_REGISTRY = {
    "maybank": MaybankParser,
    "cimb": CIMBParser,
}


def get_parser(bank_code: str) -> BaseParser:
    """Get parser instance for a bank code."""
    parser_class = PARSER_REGISTRY.get(bank_code.lower())
    if parser_class is None:
        raise ValueError(f"Unknown bank code: {bank_code}")
    return parser_class()


def detect_bank(content: str) -> str | None:
    """Attempt to detect bank from file content."""
    content_lower = content.lower()

    if "maybank" in content_lower or "maybank2u" in content_lower:
        return "maybank"
    if "cimb" in content_lower or "cimb bank" in content_lower:
        return "cimb"
    if "rhb" in content_lower or "rhb bank" in content_lower:
        return "rhb"
    if "touch" in content_lower and "go" in content_lower:
        return "touch_n_go"

    return None
