"""
Portfolio Tools
"""
from langchain_core.tools import tool
from typing import Optional


# Mock portfolio data
_portfolio_db = {
    "user_001": {
        "holdings": [
            {"symbol": "VNM", "shares": 100, "avg_price": 70000},
            {"symbol": "FPT", "shares": 50, "avg_price": 130000},
        ]
    }
}


@tool
def get_portfolio(user_id: str = "user_001") -> str:
    """Get user's portfolio holdings.
    
    Args:
        user_id: User identifier
    
    Returns:
        Portfolio summary
    """
    portfolio = _portfolio_db.get(user_id, {"holdings": []})
    holdings = portfolio["holdings"]
    
    if not holdings:
        return f"No holdings found for {user_id}"
    
    result = f"Portfolio for {user_id}:\n"
    for h in holdings:
        result += f"- {h['symbol']}: {h['shares']} shares @ {h['avg_price']:,.0f}\n"
    
    return result


@tool
def calculate_portfolio_value(user_id: str = "user_001", current_prices: Optional[dict] = None) -> str:
    """Calculate total portfolio value.
    
    Args:
        user_id: User identifier
        current_prices: Dict of current prices
    
    Returns:
        Portfolio valuation
    """
    portfolio = _portfolio_db.get(user_id, {"holdings": []})
    holdings = portfolio["holdings"]
    
    if not holdings:
        return "No holdings"
    
    prices = current_prices or {"VNM": 75000, "FPT": 145000}
    
    total_cost = 0
    total_value = 0
    
    for h in holdings:
        cost = h["shares"] * h["avg_price"]
        value = h["shares"] * prices.get(h["symbol"], h["avg_price"])
        total_cost += cost
        total_value += value
    
    profit = total_value - total_cost
    pct = (profit / total_cost) * 100 if total_cost > 0 else 0
    
    return (
        f"Total Cost: {total_cost:,.0f} VND\n"
        f"Current Value: {total_value:,.0f} VND\n"
        f"Profit/Loss: {profit:,.0f} VND ({pct:+.2f}%)"
    )


@tool
def suggest_rebalance(user_id: str = "user_001") -> str:
    """Suggest portfolio rebalancing.
    
    Args:
        user_id: User identifier
    
    Returns:
        Rebalancing suggestions
    """
    return (
        "Rebalancing suggestions:\n"
        "- Technology sector: 40% (slightly overweight)\n"
        "- Financials: 30% (on target)\n"
        "- Consumer: 20% (slightly underweight)\n"
        "- Cash reserve: 10% (consider increasing to 15%)"
    )


@tool
def calculate_diversification_score(user_id: str = "user_001") -> str:
    """Calculate portfolio diversification score.
    
    Args:
        user_id: User identifier
    
    Returns:
        Diversification analysis
    """
    return (
        "Diversification Score: 7.5/10 (Good)\n"
        "- Sectors: 4 (Good)\n"
        "- Geographic: 1 (Concentrated)\n"
        "- Market cap: Mixed (Good)\n"
        "Recommendation: Consider international diversification"
    )


PORTFOLIO_TOOLS = [
    get_portfolio,
    calculate_portfolio_value,
    suggest_rebalance,
    calculate_diversification_score,
]


# All tools
ALL_TOOLS = []  # Will be populated by combining from all modules
