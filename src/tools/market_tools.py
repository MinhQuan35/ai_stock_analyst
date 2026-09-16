"""
Market Data & Financial Intelligence Tools
Supports:
- Global AI, Semiconductor, and Big Tech stocks via yfinance
- Vietnamese Market stocks via vnstock
- RAG Document Knowledge Retrieval wrapper
"""
from typing import Optional, List
from langchain_core.tools import tool
from langchain_core.documents import Document
import yfinance as yf

from src.utils.logger import logger


@tool
def get_global_stock_quote(symbol: str) -> str:
    """Retrieve real-time quote, market valuation, and trading statistics for global stocks
    (e.g., NVDA, MSFT, GOOGL, AMD, TSM, ASML, ORCL, PLTR, AAPL, AMZN).

    Args:
        symbol: The stock ticker symbol in uppercase (e.g. 'NVDA', 'MSFT').
    """
    clean_sym = symbol.strip().upper()
    try:
        ticker = yf.Ticker(clean_sym)
        fast = ticker.fast_info
        info = getattr(ticker, "info", {}) or {}

        price = getattr(fast, "last_price", None)
        prev_close = getattr(fast, "previous_close", None)
        mcap = getattr(fast, "market_cap", None)
        currency = getattr(fast, "currency", "USD")
        high = getattr(fast, "day_high", None)
        low = getattr(fast, "day_low", None)
        year_high = getattr(fast, "year_high", None)
        year_low = getattr(fast, "year_low", None)

        if price is None:
            return f"Unable to fetch live price for global ticker '{clean_sym}'. Please verify ticker symbol."

        pct_change_str = "N/A"
        if prev_close and prev_close > 0:
            diff = price - prev_close
            pct = (diff / prev_close) * 100
            pct_change_str = f"{'+' if pct >= 0 else ''}{pct:.2f}%"

        mcap_str = f"${mcap / 1e12:.2f}T" if mcap and mcap >= 1e12 else (f"${mcap / 1e9:.2f}B" if mcap else "N/A")
        pe_ratio = info.get("trailingPE") or info.get("forwardPE")
        pe_str = f"{pe_ratio:.2f}" if pe_ratio else "N/A"
        company_name = info.get("shortName") or clean_sym

        return (
            f"**{company_name} ({clean_sym})** Market Data:\n"
            f"- **Current Price**: {price:.2f} {currency} ({pct_change_str})\n"
            f"- **Day Range**: {low:.2f} - {high:.2f} {currency}\n"
            f"- **52-Week Range**: {year_low:.2f} - {year_high:.2f} {currency}\n"
            f"- **Market Cap**: {mcap_str}\n"
            f"- **P/E Ratio**: {pe_str}\n"
            f"- **Exchange / Sector**: {info.get('exchange', 'US')} | {info.get('sector', 'Technology')}"
        )
    except Exception as e:
        logger.error(f"Error retrieving global quote for {clean_sym}: {e}")
        return f"Error retrieving market data for global ticker '{clean_sym}': {str(e)}"


@tool
def get_ai_tech_sector_movers() -> str:
    """Retrieve a real-time market overview of key AI Hardware, Semiconductor,
    Cloud Hosting & Big Tech market leaders (NVDA, AMD, TSM, MSFT, GOOGL, AMZN, ORCL, PLTR).
    """
    key_tickers = ["NVDA", "MSFT", "GOOGL", "AMD", "TSM", "ORCL", "PLTR", "AMZN"]
    rows = []
    
    for sym in key_tickers:
        try:
            t = yf.Ticker(sym)
            fast = t.fast_info
            p = getattr(fast, "last_price", 0)
            prev = getattr(fast, "previous_close", 0)
            pct = ((p - prev) / prev * 100) if prev else 0
            sign = "+" if pct >= 0 else ""
            rows.append(f"| {sym} | ${p:.2f} | {sign}{pct:.2f}% |")
        except Exception:
            rows.append(f"| {sym} | N/A | N/A |")

    header = "| Ticker | Last Price | Daily Change |\n|---|---|---|\n"
    return (
        "### Global AI & Cloud Infrastructure Leaders\n"
        + header
        + "\n".join(rows)
        + "\n\n*Covers top AI chipmakers (Nvidia, AMD, TSMC) and AI cloud/hosting infrastructure (Microsoft, Alphabet, Amazon, Oracle, Palantir).*"
    )


@tool
def get_vietnam_stock_quote(symbol: str) -> str:
    """Retrieve the latest stock quote and trading data for Vietnamese stocks (e.g. FPT, VCB, HPG, MWG, VNM).

    Args:
        symbol: The 3-character stock ticker symbol in uppercase (e.g. 'FPT', 'HPG').
    """
    clean_sym = symbol.strip().upper()
    try:
        from vnstock.api.quote import Quote
        q = Quote(symbol=clean_sym, source="VCI")
        df = q.history(start="2024-01-01", end="2026-12-31")
        if df is None or df.empty:
            return f"No price history found for Vietnamese ticker '{clean_sym}'."

        latest = df.iloc[-1]
        prev_close = df.iloc[-2]['close'] if len(df) > 1 else latest.get('open', latest['close'])
        pct = ((latest['close'] - prev_close) / prev_close * 100) if prev_close else 0
        sign = "+" if pct >= 0 else ""

        return (
            f"**Vietnam Stock: {clean_sym}** (Trading Date: {latest['time']}):\n"
            f"- **Close Price**: {latest['close'] * 1000:,.0f} VND ({sign}{pct:.2f}%)\n"
            f"- **Open / High / Low**: {latest['open'] * 1000:,.0f} / {latest['high'] * 1000:,.0f} / {latest['low'] * 1000:,.0f} VND\n"
            f"- **Trading Volume**: {latest['volume']:,.0f} shares"
        )
    except Exception as e:
        logger.error(f"Error fetching VN quote for {clean_sym}: {e}")
        return f"Error retrieving quote for Vietnamese ticker '{clean_sym}': {str(e)}"


@tool
def get_vietnam_market_movers() -> str:
    """Retrieve current market leaders and active VN30 stock highlights in Vietnam."""
    return (
        "### Vietnam Active Market Leaders (VN30)\n"
        "- **FPT**: Technology & Software Outsourcing (AI Factory partnership)\n"
        "- **HPG**: Hoa Phat Group - Steel & Heavy Industry leader\n"
        "- **VCB**: Vietcombank - Banking sector benchmark\n"
        "- **MWG**: Mobile World - Consumer electronics & retail\n"
        "- **VNM**: Vinamilk - Consumer goods & dairy staple\n"
        "\n*Use `get_vietnam_stock_quote` for individual ticker price breakdowns.*"
    )


def create_rag_search_tool(retriever, reranker=None, top_n: int = 5):
    """Factory creating a LangChain tool bound to the RAG retriever and reranker."""
    
    @tool
    def search_financial_reports_and_knowledge(query: str) -> str:
        """Search the indexed corporate financial database, quarterly reports (Q3/Q4 2024 for FPT, HPG, MWG, VCB, VNM, NVIDIA),
        valuation frameworks (DCF, P/E, RSI), and CFA equity research documents.

        Args:
            query: The specific financial question, ratio inquiry, or company metric to look up.
        """
        try:
            docs: List[Document] = retriever.retrieve(query)
            if not docs:
                return "No relevant documents found in the financial knowledge base."
            
            if reranker and docs:
                docs = reranker.rerank(query, docs, top_n=top_n)
            else:
                docs = docs[:top_n]
            
            formatted = []
            for i, doc in enumerate(docs, 1):
                src = doc.metadata.get("source", "Knowledge Base")
                formatted.append(f"--- Document Source [{i}]: {src} ---\n{doc.page_content}")
            
            return "\n\n".join(formatted)
        except Exception as e:
            logger.error(f"RAG search tool error: {e}")
            return f"Error searching financial documents: {str(e)}"

    return search_financial_reports_and_knowledge
