"""
LangChain Tools - Stock financial calculators
"""
from langchain.tools import tool
from typing import Optional


@tool
def calculate_pe_ratio(price: float, eps: float) -> str:
    """Calculate P/E Ratio from stock price and earnings per share (EPS).
    
    Args:
        price: Stock price in VND
        eps: Earnings per share in VND
    
    Returns:
        P/E ratio and valuation assessment
    """
    if eps <= 0:
        return "EPS must be positive"
    
    pe = price / eps
    if pe < 10:
        valuation = "LOW - Potentially undervalued"
    elif pe < 15:
        valuation = "NORMAL"
    elif pe < 20:
        valuation = "HIGH - Fair to expensive"
    else:
        valuation = "VERY HIGH - Expensive"
    
    return f"P/E = {pe:.1f}x ({valuation})"


@tool
def calculate_dividend_yield(annual_dividend: float, price: float) -> str:
    """Calculate Dividend Yield from annual dividend and stock price.
    
    Args:
        annual_dividend: Annual dividend per share in VND
        price: Stock price in VND
    
    Returns:
        Dividend yield percentage and rating
    """
    if price <= 0:
        return "Price must be positive"
    
    yield_pct = (annual_dividend / price) * 100
    if yield_pct > 5:
        level = "HIGH - Good for passive income"
    elif yield_pct > 3:
        level = "MODERATE"
    else:
        level = "LOW"
    
    return f"Dividend Yield = {yield_pct:.2f}% ({level})"


@tool
def calculate_compound_interest(principal: float, rate: float, years: int) -> str:
    """Calculate compound interest for an investment.
    
    Args:
        principal: Initial investment amount in VND
        rate: Annual interest rate as percentage (e.g., 8 for 8%)
        years: Number of years
    
    Returns:
        Final amount and total profit
    """
    if rate <= 0 or years <= 0:
        return "Rate and years must be positive"
    
    final = principal * (1 + rate/100) ** years
    profit = final - principal
    
    return (
        f"Initial: {principal:,.0f} VND\n"
        f"Rate: {rate}%/year\n"
        f"Period: {years} years\n"
        f"Final: {final:,.0f} VND\n"
        f"Profit: {profit:,.0f} VND ({profit/principal*100:.1f}%)"
    )


@tool
def calculate_sma(prices: list, period: int) -> str:
    """Calculate Simple Moving Average from a list of prices.
    
    Args:
        prices: List of closing prices (most recent last)
        period: Number of periods for SMA (e.g., 5, 20, 50, 200)
    
    Returns:
        SMA value and trend direction
    """
    if len(prices) < period:
        return f"Need at least {period} prices"
    
    sma = sum(prices[-period:]) / period
    current = prices[-1]
    trend = "UP" if current > sma else "DOWN"
    
    return f"SMA{period} = {sma:,.0f} | Current: {current:,.0f} | Trend: {trend}"


@tool
def calculate_rsi(prices: list, period: int = 14) -> str:
    """Calculate Relative Strength Index (RSI).
    
    Args:
        prices: List of closing prices (most recent last)
        period: Number of periods (default 14)
    
    Returns:
        RSI value and market signal
    """
    if len(prices) < period + 1:
        return f"Need at least {period + 1} prices"
    
    gains = []
    losses = []
    for i in range(-period, 0):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        rsi = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    if rsi > 70:
        signal = "OVERBOUGHT - May decline"
    elif rsi < 30:
        signal = "OVERSOLD - May rise"
    else:
        signal = "NEUTRAL"
    
    return f"RSI({period}) = {rsi:.1f} ({signal})"


# All tools
TOOLS = [
    calculate_pe_ratio,
    calculate_dividend_yield,
    calculate_compound_interest,
    calculate_sma,
    calculate_rsi,
]
