"""
RinggitSense - AI Agent Pipeline

AG-01: Categorizer - Transaction classification
AG-02: Debt Detector - Three-tier debt detection (FORMAL/BNPL/HUTANG)
AG-03: Pattern Analyzer - Spending pattern analysis
AG-04: Predictor - Spending prediction
AG-05: Query - Natural language queries (future)
AG-06: Advisor - Financial advice (future)
"""
from src.agents.categorizer import CategorizerAgent
from src.agents.debt_detector import DebtDetectorAgent
from src.agents.pattern_analyzer import PatternAnalyzerAgent
from src.agents.predictor import PredictorAgent

__all__ = [
    "CategorizerAgent",
    "DebtDetectorAgent",
    "PatternAnalyzerAgent",
    "PredictorAgent",
]
