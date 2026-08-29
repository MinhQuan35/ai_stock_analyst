"""
Financial Tools
"""
from langchain_core.tools import tool
from typing import Optional


@tool
def calculate_pe_ratio(price: float, eps: float) -> str:
    """Calculate Price-to-Earnings (P/E) ratio.
    
    Args:
        price: Current stock price
        eps: Earnings per share
    
    Returns:
        P/E ratio with valuation assessment
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
    elif pe < 30:
        valuation = "VERY HIGH - Expensive"
    else:
        valuation = "EXTREME - Highly speculative"
    
    return f"P/E = {pe:.2f}x ({valuation})"


@tool
def calculate_pb_ratio(price: float, book_value_per_share: float) -> str:
    """Calculate Price-to-Book (P/B) ratio.
    
    Args:
        price: Current stock price
        book_value_per_share: Book value per share
    
    Returns:
        P/B ratio with assessment
    """
    if book_value_per_share <= 0:
        return "Book value must be positive"
    
    pb = price / book_value_per_share
    if pb < 1:
        return f"P/B = {pb:.2f} (UNDERVALUED - Trading below book value)"
    elif pb < 3:
        return f"P/B = {pb:.2f} (NORMAL)"
    else:
        return f"P/B = {pb:.2f} (OVERVALUED - High premium to book)"


@tool
def calculate_dividend_yield(annual_dividend: float, price: float) -> str:
    """Calculate dividend yield.
    
    Args:
        annual_dividend: Annual dividend per share
        price: Current stock price
    
    Returns:
        Dividend yield percentage
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
    """Calculate compound interest.
    
    Args:
        principal: Initial investment
        rate: Annual interest rate (percentage)
        years: Number of years
    
    Returns:
        Final amount and profit
    """
    if rate <= 0 or years <= 0:
        return "Rate and years must be positive"
    
    final = principal * (1 + rate/100) ** years
    profit = final - principal
    
    return (
        f"Principal: {principal:,.0f} VND\n"
        f"Rate: {rate}%/year\n"
        f"Period: {years} years\n"
        f"Final: {final:,.0f} VND\n"
        f"Profit: {profit:,.0f} VND ({profit/principal*100:.1f}%)"
    )


@tool
def calculate_sma(prices: list, period: int) -> str:
    """Calculate Simple Moving Average.
    
    Args:
        prices: List of closing prices (most recent last)
        period: SMA period
    
    Returns:
        SMA value and trend
    """
    if len(prices) < period:
        return f"Need at least {period} prices, got {len(prices)}"
    
    sma = sum(prices[-period:]) / period
    current = prices[-1]
    trend = "UP" if current > sma else "DOWN"
    pct_diff = ((current - sma) / sma) * 100
    
    return f"SMA{period} = {sma:,.0f} | Current: {current:,.0f} | Trend: {trend} ({pct_diff:+.2f}%)"


@tool
def calculate_ema(prices: list, period: int) -> str:
    """Calculate Exponential Moving Average.
    
    Args:
        prices: List of closing prices
        period: EMA period
    
    Returns:
        EMA value
    """
    if len(prices) < period:
        return f"Need at least {period} prices"
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period  # Start with SMA
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return f"EMA{period} = {ema:,.0f}"


@tool
def calculate_rsi(prices: list, period: int = 14) -> str:
    """Calculate Relative Strength Index.
    
    Args:
        prices: List of closing prices
        period: RSI period (default 14)
    
    Returns:
        RSI value and signal
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
    elif rsi > 60:
        signal = "BULLISH"
    elif rsi < 40:
        signal = "BEARISH"
    else:
        signal = "NEUTRAL"
    
    return f"RSI({period}) = {rsi:.2f} ({signal})"


@tool
def calculate_macd(prices: list) -> str:
    """Calculate MACD indicator.
    
    Args:
        prices: List of closing prices (need at least 26)
    
    Returns:
        MACD, Signal, Histogram
    """
    if len(prices) < 26:
        return "Need at least 26 prices for MACD"
    
    # Calculate EMA12
    multiplier_12 = 2 / 13
    ema_12 = sum(prices[:12]) / 12
    for price in prices[12:]:
        ema_12 = (price - ema_12) * multiplier_12 + ema_12
    
    # Calculate EMA26
    multiplier_26 = 2 / 27
    ema_26 = sum(prices[:26]) / 26
    for price in prices[26:]:
        ema_26 = (price - ema_26) * multiplier_26 + ema_26
    
    macd_line = ema_12 - ema_26
    
    # Calculate Signal line (9-period EMA of MACD)
    # Simplified - just use MACD * 0.8 as approximation
    signal_line = macd_line * 0.8
    histogram = macd_line - signal_line
    
    return f"MACD = {macd_line:.2f} | Signal = {signal_line:.2f} | Histogram = {histogram:.2f}"


@tool
def calculate_bollinger_bands(prices: list, period: int = 20, std_dev: float = 2.0) -> str:
    """Calculate Bollinger Bands.
    
    Args:
        prices: List of closing prices
        period: Moving average period
        std_dev: Number of standard deviations
    
    Returns:
        Upper, middle, lower bands
    """
    if len(prices) < period:
        return f"Need at least {period} prices"
    
    import statistics
    
    recent = prices[-period:]
    middle = sum(recent) / period
    std = statistics.stdev(recent)
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    current = prices[-1]
    
    if current > upper:
        signal = "ABOVE UPPER BAND - Overbought"
    elif current < lower:
        signal = "BELOW LOWER BAND - Oversold"
    else:
        signal = "WITHIN BANDS - Normal"
    
    return f"Upper: {upper:,.0f} | Middle: {middle:,.0f} | Lower: {lower:,.0f} | Current: {current:,.0f} ({signal})"


# All financial tools
FINANCIAL_TOOLS = [
    calculate_pe_ratio,
    calculate_pb_ratio,
    calculate_dividend_yield,
    calculate_compound_interest,
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
]
