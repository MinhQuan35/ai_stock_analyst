"""Regression checks for corpus loading used by the benchmark (Phase 3)."""
from pathlib import Path

from src.tools.loaders import MultiFormatLoader

RAW = Path("data/raw")
loader = MultiFormatLoader(str(RAW))


def test_xlsx_rows_keep_column_names():
    docs = loader._load_xlsx(RAW / "vinamilk_vn30_financial_model_2024.xlsx")
    matrix = [d for d in docs if "TTM P/E" in d.page_content]
    assert matrix, "valuation matrix rows should carry their column labels"
    assert any("Ticker: FPT" in d.page_content for d in matrix)


def test_price_csv_has_row_docs_and_summary():
    docs = loader._load_csv(RAW / "real_aapl_daily_prices_2024.csv")
    assert any(d.metadata["type"] == "csv_row" for d in docs)
    summary = [d for d in docs if d.metadata["type"] == "price_summary"][0]
    assert summary.page_content.startswith("AAPL price summary")
    assert "average close" in summary.page_content


def test_financial_csv_rows_are_self_contained():
    docs = loader._load_csv(RAW / "fpt_income_statement_quarterly.csv")
    net_sales = [d for d in docs if "net_sales" in d.page_content][0]
    assert "FPT" in net_sales.page_content
    assert "2026-Q2" in net_sales.page_content
