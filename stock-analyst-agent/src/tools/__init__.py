"""
Tools - All available tools
"""
from src.tools.financial import FINANCIAL_TOOLS
from src.tools.market_data import MARKET_DATA_TOOLS
from src.tools.portfolio import PORTFOLIO_TOOLS


# All tools combined
ALL_TOOLS = FINANCIAL_TOOLS + MARKET_DATA_TOOLS + PORTFOLIO_TOOLS


__all__ = [
    "ALL_TOOLS",
    "FINANCIAL_TOOLS",
    "MARKET_DATA_TOOLS",
    "PORTFOLIO_TOOLS",
]
