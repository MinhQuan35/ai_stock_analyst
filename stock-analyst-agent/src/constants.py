"""
Constants
"""
from enum import Enum


class ModelType(str, Enum):
    """LLM model types."""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"


class AnalysisType(str, Enum):
    """Stock analysis types."""
    FUNDAMENTAL = "fundamental"
    TECHNICAL = "technical"
    COMPARATIVE = "comparative"
    SENTIMENT = "sentiment"
    RISK = "risk"


class Recommendation(str, Enum):
    """Investment recommendations."""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"


class Signal(str, Enum):
    """Trading signals."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    OVERBOUGHT = "overbought"
    OVERSOLD = "oversold"


class TimeFrame(str, Enum):
    """Time frames."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class AgentRole(str, Enum):
    """Agent roles in multi-agent system."""
    TRIAGE = "triage"
    ANALYST = "analyst"
    RESEARCHER = "researcher"
    REPORTER = "reporter"
    VALIDATOR = "validator"


class MarketType(str, Enum):
    """Market types."""
    HOSE = "HOSE"
    HNX = "HNX"
    UPCOM = "UPCOM"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"


# Pricing (USD per 1M tokens)
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "text-embedding-3-large": {"input": 0.13, "output": 0.0},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
}


# Limits
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 60
MAX_TOKENS = 4000
