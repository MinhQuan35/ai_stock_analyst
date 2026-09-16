"""
Tests for Market Data Tools & Autonomous Tool Agent
"""
import pytest
from src.tools.market_tools import (
    get_global_stock_quote,
    get_ai_tech_sector_movers,
    get_vietnam_stock_quote,
    get_vietnam_market_movers,
    create_rag_search_tool,
)


def test_get_global_stock_quote_nvda():
    """Verify live quote fetching for global tech leader NVDA."""
    result = get_global_stock_quote.invoke("NVDA")
    assert "NVDA" in result
    assert "Current Price" in result or "Market Data" in result


def test_get_ai_tech_sector_movers():
    """Verify AI and cloud infrastructure movers overview."""
    result = get_ai_tech_sector_movers.invoke({})
    assert "NVDA" in result
    assert "MSFT" in result
    assert "Global AI & Cloud Infrastructure Leaders" in result


def test_get_vietnam_stock_quote_fpt():
    """Verify Vietnam stock quote fetching for FPT."""
    result = get_vietnam_stock_quote.invoke("FPT")
    assert "FPT" in result
    assert "Close Price" in result or "VND" in result


def test_get_vietnam_market_movers():
    """Verify Vietnam market movers summary."""
    result = get_vietnam_market_movers.invoke({})
    assert "VN30" in result
    assert "FPT" in result
    assert "VCB" in result


def test_create_rag_search_tool():
    """Verify RAG tool creation wrapper."""
    class DummyRetriever:
        def retrieve(self, query):
            from langchain_core.documents import Document
            return [Document(page_content="FPT Q3 2024 revenue reached 13,800 billion VND.", metadata={"source": "fpt_q3.csv"})]

    tool = create_rag_search_tool(DummyRetriever())
    result = tool.invoke({"query": "FPT Q3 revenue"})
    assert "13,800" in result
    assert "Document Source" in result
