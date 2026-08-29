"""
Market Data Tools
"""
from langchain_core.tools import tool
from datetime import datetime, timedelta
import random


@tool
def get_stock_quote(symbol: str) -> str:
    """Get current stock quote (mock data).
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Current quote information
    """
    # Mock data - in production would call real API
    base_prices = {
        "VNM": 75000, "VIC": 45000, "HPG": 25000, "VCB": 95000,
        "FPT": 145000, "MWG": 50000, "MSN": 85000,
    }
    
    price = base_prices.get(symbol, random.randint(10000, 100000))
    change = random.uniform(-3, 3)
    volume = random.randint(100000, 5000000)
    
    return (
        f"Symbol: {symbol}\n"
        f"Price: {price:,.0f} VND\n"
        f"Change: {change:+.2f}%\n"
        f"Volume: {volume:,}"
    )


@tool
def get_market_index(index_name: str = "VN-Index") -> str:
    """Get market index information.
    
    Args:
        index_name: Index name (VN-Index, HNX-Index, UPCOM-Index)
    
    Returns:
        Index data
    """
    indices = {
        "VN-Index": (1280.5, 0.85),
        "HNX-Index": (235.4, 0.42),
        "UPCOM-Index": (92.1, -0.15),
        "VN30": (1285.3, 0.92),
    }
    
    value, change = indices.get(index_name, (1000.0, 0.0))
    
    return (
        f"{index_name}\n"
        f"Value: {value:,.2f}\n"
        f"Change: {change:+.2f}%\n"
        f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )


@tool
def get_company_info(symbol: str) -> str:
    """Get company information.
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Company details
    """
    # Mock data
    companies = {
        "VNM": ("Vinamilk", "Consumer Goods", "Dairy products"),
        "VIC": ("Vingroup", "Real Estate", "Conglomerate"),
        "HPG": ("Hoa Phat Group", "Materials", "Steel"),
        "VCB": ("Vietcombank", "Financials", "Banking"),
        "FPT": ("FPT Corporation", "Technology", "IT Services"),
    }
    
    info = companies.get(symbol, (symbol, "Unknown", "Unknown"))
    return f"Name: {info[0]}\nSector: {info[1]}\nIndustry: {info[2]}\nMarket Cap: Large"


@tool
def get_historical_prices(symbol: str, days: int = 30) -> str:
    """Get historical price data.
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days to retrieve
    
    Returns:
        Historical price summary
    """
    base = 50000
    prices = []
    current = base
    
    for _ in range(days):
        current *= (1 + random.uniform(-0.03, 0.03))
        prices.append(current)
    
    return (
        f"Symbol: {symbol}\n"
        f"Days: {days}\n"
        f"Start: {prices[0]:,.0f}\n"
        f"End: {prices[-1]:,.0f}\n"
        f"High: {max(prices):,.0f}\n"
        f"Low: {min(prices):,.0f}\n"
        f"Avg: {sum(prices)/len(prices):,.0f}"
    )


@tool
def search_news(symbol: str, days: int = 7) -> str:
    """Search recent news for a stock.
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days to look back
    
    Returns:
        Recent news summary
    """
    # Mock news
    return (
        f"Recent news for {symbol} (last {days} days):\n"
        f"- Q3 earnings report released\n"
        f"- New product launch announced\n"
        f"- Management changes\n"
        f"- Industry analysis published"
    )


MARKET_DATA_TOOLS = [
    get_stock_quote,
    get_market_index,
    get_company_info,
    get_historical_prices,
    search_news,
]
