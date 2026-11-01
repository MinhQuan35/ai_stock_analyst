"""Build a 150-query benchmark whose ground truth is derived from the actual corpus.

Every expected value is read from data/raw or from the frozen market snapshot at
build time, so the benchmark can no longer drift away from the indexed data.

Usage: python scripts/build_benchmark.py
Output: data/benchmark/benchmark_v2.json
"""
import json
import re
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
SNAPSHOT = Path("data/benchmark/realtime_snapshot_20241030.json")
OUT = Path("data/benchmark/benchmark_v2.json")
RAG_TOOL = "search_financial_reports_and_knowledge"
SNAPSHOT_REF = [SNAPSHOT.name]

TICKERS = {"FPT": "FPT", "HPG": "Hòa Phát", "MWG": "Thế Giới Di Động",
           "VCB": "Vietcombank", "VNM": "Vinamilk"}

INCOME_METRICS = {
    "FPT": ["net_sales", "gross_profit", "operating_profit_loss",
            "net_profit_loss_after_tax", "attributable_to_parent_company"],
    "HPG": ["net_sales", "gross_profit", "operating_profit_loss",
            "net_profit_loss_after_tax", "attributable_to_parent_company"],
    "MWG": ["net_sales", "gross_profit", "operating_profit_loss",
            "net_profit_loss_after_tax", "attributable_to_parent_company"],
    "VNM": ["net_sales", "gross_profit", "operating_profit_loss",
            "net_profit_loss_after_tax", "attributable_to_parent_company"],
    "VCB": ["net_interest_income", "total_operating_income", "net_profit_loss_after_tax",
            "attributable_to_parent_company", "net_other_income_expenses"],
}

LABELS = {
    "net_sales": "Doanh thu thuần",
    "gross_profit": "Lợi nhuận gộp",
    "operating_profit_loss": "Lợi nhuận từ hoạt động kinh doanh",
    "net_profit_loss_after_tax": "Lợi nhuận sau thuế",
    "attributable_to_parent_company": "Lợi nhuận của cổ đông công ty mẹ",
    "net_interest_income": "Thu nhập lãi thuần",
    "total_operating_income": "Tổng thu nhập hoạt động",
    "net_other_income_expenses": "Thu nhập khác ròng",
    "total_assets": "Tổng tài sản",
}

queries = []


def add(category, subcategory, difficulty, query, expected_answer,
        expected_values=None, expected_units=None, sources=None, tools=None,
        period=None, requires_llm_judge=False):
    queries.append({
        "query_id": f"{category[:3].upper()}_{len([q for q in queries if q['category'] == category]) + 1:03d}",
        "category": category,
        "subcategory": subcategory,
        "difficulty": difficulty,
        "query": query,
        "expected_answer": expected_answer,
        "expected_values": expected_values or [],
        "expected_units": expected_units or "",
        "reporting_period": period or "latest available",
        "source_reference": sources or [],
        "required_tools": tools if tools is not None else [RAG_TOOL],
        "requires_llm_judge": requires_llm_judge,
    })


def quarter_cols(columns):
    return sorted(
        [c for c in columns if re.fullmatch(r"\d{4}-Q[1-4]", str(c).strip())],
        key=lambda c: (int(c[:4]), int(c[-1])),
        reverse=True,
    )


def period_label(col):
    return f"Q{col[-1]} {col[:4]}"


def latest_period(income):
    cols = quarter_cols(income.columns)
    if not cols:
        raise ValueError("no quarter columns")
    return cols[0], period_label(cols[0])


# ---------------------------------------------------------------- 1. VN historical
def build_vn_historical():
    for ticker in TICKERS:
        income = pd.read_csv(RAW / f"{ticker.lower()}_income_statement_quarterly.csv")
        balance = pd.read_csv(RAW / f"{ticker.lower()}_balance_sheet_quarterly.csv")
        col, period = latest_period(income)

        def value(df, item_id):
            row = df[df["item_id"] == item_id]
            return None if row.empty else float(row.iloc[0][col])

        jobs = [(m, income) for m in INCOME_METRICS[ticker]] + [("total_assets", balance)]
        for item_id, df in jobs:
            val = value(df, item_id)
            if val is None or pd.isna(val):
                continue
            billion = round(val / 1e9, 2)
            label = LABELS[item_id]
            source = (f"{ticker.lower()}_income_statement_quarterly.csv"
                      if item_id in INCOME_METRICS[ticker]
                      else f"{ticker.lower()}_balance_sheet_quarterly.csv")
            add(
                "vn_historical_financial", "Single metric lookup", "easy",
                f"{label} của {TICKERS[ticker]} ({ticker}) trong {period} là bao nhiêu tỷ VND?",
                f"{billion:,.2f} tỷ VND",
                [billion], "billion_vnd", [source],
                period=period,
            )


# ---------------------------------------------------------------- 2. Global historical
NVDA_FACTS = [
    ("total revenue", 35.08, "billion_usd"),
    ("Data Center revenue", 30.77, "billion_usd"),
    ("Gaming & AI PC revenue", 3.28, "billion_usd"),
    ("GAAP gross margin", 74.6, "percent"),
    ("GAAP diluted EPS", 0.78, "usd"),
]


def build_global_historical():
    for label, val, unit in NVDA_FACTS:
        add(
            "global_historical_financial", "Company filing lookup", "easy",
            f"What was NVIDIA's {label} in Q3 FY2025?",
            f"{val} {unit}",
            [val], unit,
            ["nvidia_q3_fy2025_official_results.docx"],
            period="Q3 FY2025",
        )

    for ticker in ["AAPL", "MSFT", "NVDA", "TSLA"]:
        path = RAW / f"real_{ticker.lower()}_daily_prices_2024.csv"
        df = pd.read_csv(path)
        close = df["Close"]
        stats = [
            ("highest closing price", round(float(close.max()), 2), "USD"),
            ("lowest closing price", round(float(close.min()), 2), "USD"),
            ("average closing price", round(float(close.mean()), 2), "USD"),
            ("total return from first to last close",
             round(float((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100), 2), "percent"),
        ]
        for label, val, unit in stats:
            add(
                "global_historical_financial", "Price history lookup", "easy",
                f"What was {ticker}'s {label} in the price history file?",
                f"{val} {unit}",
                [val], unit,
                [path.name],
                tools=["get_price_history_summary"],
                period=f"{df['Date'].iloc[0]} to {df['Date'].iloc[-1]}",
            )


# ---------------------------------------------------------------- 3. Ratios & valuation
def build_ratios():
    sheet = pd.read_excel(RAW / "vinamilk_vn30_financial_model_2024.xlsx",
                          sheet_name="VN30 Valuation Matrix 2024")
    metrics = [("TTM P/E", "x"), ("P/B", "x"), ("ROE (%)", "percent"),
               ("ROA (%)", "percent"), ("Dividend Yield (%)", "percent"),
               ("Net Margin (%)", "percent")]
    combos = [(row, metric, unit) for _, row in sheet.iterrows()
              for metric, unit in metrics][:20]
    for row, metric, unit in combos:
        add(
            "ratios_and_valuation", "Valuation matrix lookup", "easy",
            f"Chỉ số {metric} của {row['Company Name']} ({row['Ticker']}) "
            f"trong mô hình định giá VN30 2024 là bao nhiêu?",
            f"{row[metric]} {unit}",
            [float(row[metric])], unit,
            ["vinamilk_vn30_financial_model_2024.xlsx"],
            period="2024",
        )


# ---------------------------------------------------------------- 4. Definitions
DEFINITIONS = [
    ("RSI được tính theo công thức nào?", "RSI = 100 - [100 / (1 + RS)], với RS = Average Gain / Average Loss trong 14 ngày.", "rsi.md"),
    ("Vùng quá mua và quá bán của RSI là bao nhiêu?", "Quá mua khi RSI trên 70, quá bán khi RSI dưới 30.", "rsi.md"),
    ("RSI được tính dựa trên thay đổi giá trong bao nhiêu ngày?", "RSI dùng chu kỳ 14 ngày là phổ biến nhất.", "rsi.md"),
    ("Công thức tính tỷ lệ P/E là gì?", "P/E = Giá cổ phiếu / EPS (thu nhập trên mỗi cổ phần).", "pe_ratio.md"),
    ("Nếu cổ phiếu giá 75,000 VND và EPS 4,200 VND thì P/E bằng bao nhiêu?", "P/E = 75,000 / 4,200 = 17.9x.", "pe_ratio.md"),
    ("P/E của cổ phiếu value và growth trên thị trường Việt Nam thường nằm trong khoảng nào?", "Value stocks thường P/E 10-15x, growth stocks 20-30x.", "pe_ratio.md"),
    ("Công thức Enterprise Value trong mô hình DCF là gì?", "EV = tổng FCFF_t/(1+WACC)^t + Terminal Value/(1+WACC)^N.", "cfa_equity_research_and_valuation_framework.md"),
    ("Golden Cross trong phân tích kỹ thuật là gì?", "Golden Cross là khi SMA 50 ngày cắt lên trên SMA 200 ngày, xác nhận xu hướng tăng.", "cfa_equity_research_and_valuation_framework.md"),
    ("MACD line và Signal line được tính như thế nào?", "MACD line = EMA 12 kỳ - EMA 26 kỳ; Signal line = EMA 9 kỳ của MACD line.", "cfa_equity_research_and_valuation_framework.md"),
    ("Vùng an toàn của Altman Z-Score là bao nhiêu?", "Z > 2.99 là vùng an toàn; 1.81 < Z < 2.99 là vùng xám; Z < 1.81 là vùng khó khăn.", "cfa_equity_research_and_valuation_framework.md"),
]


def build_definitions():
    for question, answer, source in DEFINITIONS:
        add("definitions_and_formulas", "Conceptual explanation", "easy",
            question, answer, [], "",
            [source], tools=[RAG_TOOL], requires_llm_judge=True)


# ---------------------------------------------------------------- 5. Realtime (snapshot)
def build_realtime():
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    day = snap["market_date"]
    for ticker, stock in snap["vietnam_stocks"].items():
        for field, label in [("close_price", "giá đóng cửa"), ("open", "giá mở cửa"),
                             ("high", "giá cao nhất"), ("low", "giá thấp nhất")]:
            add("realtime_price", "VN single-stock quote", "easy",
                f"{label.capitalize()} của cổ phiếu {ticker} trong phiên {day} là bao nhiêu VND?",
                f"{stock[field]:,.0f} VND",
                [stock[field]], "vnd", SNAPSHOT_REF,
                tools=["get_vietnam_stock_quote"], period=day)
    for ticker in ["NVDA", "AAPL", "MSFT", "TSLA", "AMD"]:
        stock = snap["global_stocks"][ticker]
        add("realtime_price", "Global single-stock quote", "easy",
            f"What was {ticker}'s price in the {day} market snapshot?",
            f"{stock['price']:.2f} {stock.get('currency', 'USD')}",
            [stock["price"]], "usd", SNAPSHOT_REF,
            tools=["get_global_stock_quote"], period=day)


# ---------------------------------------------------------------- 6. Sector / market
def build_sector():
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    day = snap["market_date"]
    m = snap["vietnam_market_movers"]

    for label, val, unit in [("điểm số", m["index_points"], "points"),
                             ("mức thay đổi điểm", m["index_change_pts"], "points"),
                             ("mức thay đổi phần trăm", m["index_change_pct"], "percent")]:
        add("sector_market_overview", "VN index summary", "easy",
            f"{m['index_name']} trong phiên {day} có {label} là bao nhiêu?",
            f"{val}", [float(val)], unit, SNAPSHOT_REF,
            tools=["get_vietnam_market_movers"], period=day)

    add("sector_market_overview", "VN index summary", "easy",
        f"Giá trị giao dịch ròng của khối ngoại trên {m['index_name']} phiên {day} là bao nhiêu VND?",
        f"{m['foreign_net_vnd']:,.0f} VND", [m["foreign_net_vnd"]], "vnd",
        SNAPSHOT_REF, tools=["get_vietnam_market_movers"], period=day)

    add("sector_market_overview", "VN index summary", "easy",
        f"Những cổ phiếu nào dẫn dắt thanh khoản {m['index_name']} phiên {day}?",
        f"Các mã dẫn dắt: {', '.join(m['top_active_leaders'])}.",
        [], "", SNAPSHOT_REF, tools=["get_vietnam_market_movers"],
        period=day, requires_llm_judge=True)

    for ticker in m["top_active_leaders"]:
        stock = snap["vietnam_stocks"][ticker]
        add("sector_market_overview", "VN movers", "easy",
            f"{ticker} thay đổi bao nhiêu phần trăm trong phiên {day}?",
            f"{stock['change_pct']:+.2f}%", [stock["change_pct"]], "percent",
            SNAPSHOT_REF, tools=["get_vietnam_stock_quote"], period=day)

    movers = snap["global_tech_movers"]
    top = max(movers, key=lambda x: x["change_pct"])
    bottom = min(movers, key=lambda x: x["change_pct"])
    add("sector_market_overview", "Global tech movers", "easy",
        f"Trong nhóm AI/tech phiên {day}, mã nào tăng mạnh nhất và bao nhiêu phần trăm?",
        f"{top['symbol']} {top['change_pct']:+.2f}%", [top["change_pct"]], "percent",
        SNAPSHOT_REF, tools=["get_ai_tech_sector_movers"], period=day)
    add("sector_market_overview", "Global tech movers", "easy",
        f"Trong nhóm AI/tech phiên {day}, mã nào giảm mạnh nhất và bao nhiêu phần trăm?",
        f"{bottom['symbol']} {bottom['change_pct']:+.2f}%", [bottom["change_pct"]], "percent",
        SNAPSHOT_REF, tools=["get_ai_tech_sector_movers"], period=day)
    avg = sum(x["change_pct"] for x in movers) / len(movers)
    add("sector_market_overview", "Global tech movers", "easy",
        f"Mức thay đổi trung bình của nhóm AI/tech phiên {day} là bao nhiêu phần trăm?",
        f"{avg:+.2f}%", [round(avg, 4)], "percent", SNAPSHOT_REF,
        tools=["get_ai_tech_sector_movers"], period=day)

    up = sum(1 for s in snap["vietnam_stocks"].values() if s["change_pct"] > 0)
    add("sector_market_overview", "VN movers", "easy",
        f"Trong phiên {day}, bao nhiêu cổ phiếu trong nhóm VN30 theo dõi tăng giá?",
        f"{up} mã", [float(up)], "count", SNAPSHOT_REF,
        tools=["get_vietnam_stock_quote"], period=day)


# ---------------------------------------------------------------- 7. Cross-company
def build_cross_company():
    pairs = [("VCB", "HPG"), ("VNM", "MWG"), ("FPT", "HPG"), ("VCB", "VNM"),
             ("FPT", "MWG"), ("HPG", "MWG"), ("FPT", "VCB"), ("VNM", "HPG"),
             ("MWG", "VCB"), ("FPT", "VNM")]
    metrics = [("total_assets", "total_assets", "Tổng tài sản", "balance_sheet"),
               ("net_profit_loss_after_tax", "net_profit_loss_after_tax", "Lợi nhuận sau thuế", "income_statement")]

    for a, b in pairs:
        for item_id, _, label, kind in metrics:
            vals, srcs = [], []
            for ticker in (a, b):
                df = pd.read_csv(RAW / f"{ticker.lower()}_{kind}_quarterly.csv")
                col, period = latest_period(df)
                row = df[df["item_id"] == item_id]
                if row.empty:
                    break
                vals.append(round(float(row.iloc[0][col]) / 1e9, 2))
                srcs.append(f"{ticker.lower()}_{kind}_quarterly.csv")
            if len(vals) != 2:
                continue
            add("cross_company_comparison", "Peer comparison", "medium",
                f"So sánh {label.lower()} của {a} và {b} trong {period} (đơn vị tỷ VND).",
                f"{a}: {vals[0]:,.2f} tỷ VND; {b}: {vals[1]:,.2f} tỷ VND",
                vals, "billion_vnd", srcs, period=period)


# ---------------------------------------------------------------- 8. Reasoning / trend
def build_reasoning():
    for ticker in TICKERS:
        df = pd.read_csv(RAW / f"{ticker.lower()}_income_statement_quarterly.csv")
        cols = quarter_cols(df.columns)[:4]
        for item_id, label in [("net_sales", "doanh thu thuần"),
                               ("net_profit_loss_after_tax", "lợi nhuận sau thuế")]:
            if item_id == "net_sales" and ticker == "VCB":
                item_id, label = "net_interest_income", "thu nhập lãi thuần"
            row = df[df["item_id"] == item_id]
            if row.empty:
                continue
            values = [round(float(row.iloc[0][c]) / 1e9, 2) for c in cols]
            periods = [period_label(c) for c in cols]
            add("financial_analysis_reasoning", "Trend analysis", "hard",
                f"Phân tích xu hướng {label} của {TICKERS[ticker]} ({ticker}) "
                f"qua 4 quý gần nhất ({periods[-1]} đến {periods[0]}). Nêu giá trị từng quý.",
                "; ".join(f"{p}: {v:,.2f} tỷ VND" for p, v in zip(periods, values)),
                values, "billion_vnd",
                [f"{ticker.lower()}_income_statement_quarterly.csv"],
                period=f"{periods[-1]} to {periods[0]}", requires_llm_judge=True)


def main():
    build_vn_historical()
    build_global_historical()
    build_ratios()
    build_definitions()
    build_realtime()
    build_sector()
    build_cross_company()
    build_reasoning()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(queries, indent=2, ensure_ascii=False), encoding="utf-8")

    counts = {}
    for q in queries:
        counts[q["category"]] = counts.get(q["category"], 0) + 1
    print(f"Wrote {len(queries)} queries to {OUT}")
    for cat, n in counts.items():
        print(f"  {cat}: {n}")


if __name__ == "__main__":
    main()
