"""
Generator script to build:
1. data/benchmark/realtime_snapshot_20241030.json
2. data/benchmark/benchmark_150_queries.json
Covers all 150 benchmark queries and 8 categories specified by the user.
"""
import json
from pathlib import Path

SNAPSHOT_DATA = {
    "timestamp": "2024-10-30T15:00:00+07:00",
    "market_date": "2024-10-30",
    "vietnam_stocks": {
        "FPT": {
            "symbol": "FPT",
            "name": "FPT Corporation",
            "close_price": 138500.0,
            "change_pct": 1.84,
            "open": 136000.0,
            "high": 139200.0,
            "low": 135500.0,
            "volume": 4850200,
            "currency": "VND"
        },
        "VCB": {
            "symbol": "VCB",
            "name": "Vietcombank",
            "close_price": 91200.0,
            "change_pct": 0.44,
            "open": 90800.0,
            "high": 91600.0,
            "low": 90500.0,
            "volume": 1320500,
            "currency": "VND"
        },
        "HPG": {
            "symbol": "HPG",
            "name": "Hoa Phat Group",
            "close_price": 26800.0,
            "change_pct": 1.13,
            "open": 26500.0,
            "high": 27000.0,
            "low": 26300.0,
            "volume": 22410000,
            "currency": "VND"
        },
        "MWG": {
            "symbol": "MWG",
            "name": "Mobile World Group",
            "close_price": 65400.0,
            "change_pct": -0.61,
            "open": 65800.0,
            "high": 66200.0,
            "low": 65100.0,
            "volume": 5640000,
            "currency": "VND"
        },
        "VNM": {
            "symbol": "VNM",
            "name": "Vinamilk",
            "close_price": 68000.0,
            "change_pct": 0.00,
            "open": 68000.0,
            "high": 68400.0,
            "low": 67800.0,
            "volume": 2150000,
            "currency": "VND"
        }
    },
    "global_stocks": {
        "NVDA": {
            "symbol": "NVDA",
            "name": "NVIDIA Corporation",
            "price": 141.50,
            "change_pct": 3.20,
            "low": 138.20,
            "high": 142.80,
            "year_low": 45.20,
            "year_high": 144.42,
            "market_cap": 3.48e12,
            "pe_ratio": 64.20,
            "volume": 48200000,
            "currency": "USD"
        },
        "AAPL": {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 232.10,
            "change_pct": 0.85,
            "low": 230.15,
            "high": 233.40,
            "year_low": 164.08,
            "year_high": 237.23,
            "market_cap": 3.52e12,
            "pe_ratio": 35.80,
            "volume": 38100000,
            "currency": "USD"
        },
        "MSFT": {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "price": 428.50,
            "change_pct": 1.10,
            "low": 425.00,
            "high": 430.20,
            "year_low": 335.50,
            "year_high": 468.35,
            "market_cap": 3.18e12,
            "pe_ratio": 36.40,
            "volume": 21400000,
            "currency": "USD"
        },
        "TSLA": {
            "symbol": "TSLA",
            "name": "Tesla, Inc.",
            "price": 258.00,
            "change_pct": 4.50,
            "low": 248.50,
            "high": 261.20,
            "year_low": 138.80,
            "year_high": 271.00,
            "market_cap": 825.0e9,
            "pe_ratio": 72.10,
            "volume": 68500000,
            "currency": "USD"
        },
        "AMD": {
            "symbol": "AMD",
            "name": "Advanced Micro Devices",
            "price": 158.20,
            "change_pct": 2.10,
            "low": 155.00,
            "high": 160.00,
            "currency": "USD"
        },
        "TSM": {
            "symbol": "TSM",
            "name": "Taiwan Semiconductor",
            "price": 192.40,
            "change_pct": 2.80,
            "currency": "USD"
        },
        "GOOGL": {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "price": 178.60,
            "change_pct": 1.40,
            "currency": "USD"
        },
        "AMZN": {
            "symbol": "AMZN",
            "name": "Amazon.com, Inc.",
            "price": 192.80,
            "change_pct": 1.25,
            "currency": "USD"
        }
    },
    "vietnam_market_movers": {
        "index_name": "VN-Index",
        "index_points": 1262.50,
        "index_change_pts": 8.20,
        "index_change_pct": 0.65,
        "top_active_leaders": ["HPG", "FPT", "MWG", "VCB", "VNM"],
        "foreign_net_vnd": 125e9
    },
    "global_tech_movers": [
        {"symbol": "NVDA", "price": 141.50, "change_pct": 3.20},
        {"symbol": "TSM", "price": 192.40, "change_pct": 2.80},
        {"symbol": "AMD", "price": 158.20, "change_pct": 2.10},
        {"symbol": "MSFT", "price": 428.50, "change_pct": 1.10},
        {"symbol": "GOOGL", "price": 178.60, "change_pct": 1.40},
        {"symbol": "AMZN", "price": 192.80, "change_pct": 1.25}
    ]
}


def build_150_queries():
    queries = []
    
    # ----------------------------------------------------
    # 1. VN Historical Financial (25 queries)
    # ----------------------------------------------------
    vn_hist = [
        # Single metric lookup (8)
        ("VN_HIST_001", "Single metric lookup", "easy", "Doanh thu thuần hợp nhất của FPT trong Q3 2024 là bao nhiêu tỷ VND?", "14510", [14510.0], ["fpt_income_statement_quarterly.csv", "fpt_income_statement_summary.md"]),
        ("VN_HIST_002", "Single metric lookup", "easy", "Lợi nhuận sau thuế của FPT trong Q3 2024 đạt bao nhiêu tỷ VND?", "2246", [2246.0], ["fpt_income_statement_quarterly.csv", "fpt_income_statement_summary.md"]),
        ("VN_HIST_003", "Single metric lookup", "easy", "Lợi nhuận gộp của Tập đoàn Hòa Phát (HPG) trong Q3 2024 là bao nhiêu tỷ VND?", "5230", [5230.0], ["hpg_income_statement_quarterly.csv", "hpg_income_statement_summary.md"]),
        ("VN_HIST_004", "Single metric lookup", "easy", "Doanh thu thuần của Vinamilk (VNM) trong Q3 2024 là bao nhiêu tỷ VND?", "15537", [15537.0], ["vnm_income_statement_quarterly.csv", "vnm_income_statement_summary.md"]),
        ("VN_HIST_005", "Single metric lookup", "easy", "Lợi nhuận sau thuế của Vietcombank (VCB) trong Q3 2024 đạt bao nhiêu tỷ VND?", "8690", [8690.0], ["vcb_income_statement_quarterly.csv", "vcb_income_statement_summary.md"]),
        ("VN_HIST_006", "Single metric lookup", "easy", "Doanh thu thuần của Thế Giới Di Động (MWG) trong Q3 2024 là bao nhiêu tỷ VND?", "34147", [34147.0], ["mwg_income_statement_quarterly.csv", "mwg_income_statement_summary.md"]),
        ("VN_HIST_007", "Single metric lookup", "easy", "Lợi nhuận sau thuế của MWG trong Q3 2024 là bao nhiêu tỷ VND?", "806", [806.0], ["mwg_income_statement_quarterly.csv", "mwg_income_statement_summary.md"]),
        ("VN_HIST_008", "Single metric lookup", "easy", "Lợi nhuận sau thuế của Hòa Phát (HPG) trong Q3 2024 là bao nhiêu tỷ VND?", "3022", [3022.0], ["hpg_income_statement_quarterly.csv", "hpg_income_statement_summary.md"]),

        # YoY / QoQ growth (5)
        ("VN_HIST_009", "YoY / QoQ growth", "medium", "Tăng trưởng doanh thu thuần YoY của FPT trong Q3 2024 là bao nhiêu %?", "15.0%", [15.0], ["fpt_income_statement_quarterly.csv", "fpt_income_statement_summary.md"]),
        ("VN_HIST_010", "YoY / QoQ growth", "medium", "Tăng trưởng lợi nhuận sau thuế YoY của FPT trong Q3 2024 đạt mức bao nhiêu?", "19.5%", [19.5], ["fpt_income_statement_quarterly.csv", "fpt_income_statement_summary.md"]),
        ("VN_HIST_011", "YoY / QoQ growth", "medium", "Tăng trưởng lợi nhuận sau thuế của HPG so với cùng kỳ năm trước (YoY) trong Q3 2024?", "51.0%", [51.0], ["hpg_income_statement_quarterly.csv", "hpg_income_statement_summary.md"]),
        ("VN_HIST_012", "YoY / QoQ growth", "medium", "Tăng trưởng doanh thu của Vinamilk (VNM) trong Q3 2024 so với cùng kỳ năm trước đạt bao nhiêu %?", "3.5%", [3.5], ["vnm_income_statement_quarterly.csv", "vnm_income_statement_summary.md"]),
        ("VN_HIST_013", "YoY / QoQ growth", "medium", "Tăng trưởng lợi nhuận sau thuế của MWG trong Q3 2024 so với Q3 2023 là bao nhiêu %?", "1900%", [1900.0], ["mwg_income_statement_quarterly.csv", "mwg_income_statement_summary.md"]),

        # Multi-metric analysis (5)
        ("VN_HIST_014", "Multi-metric analysis", "medium", "Trình bày doanh thu thuần, lợi nhuận gộp và biên lợi nhuận gộp của FPT trong Q3 2024.", "Doanh thu 14510 tỷ, Lợi nhuận gộp 5700 tỷ, Biên gộp khoảng 39.3%", [14510.0, 5700.0, 39.3], ["fpt_income_statement_quarterly.csv"]),
        ("VN_HIST_015", "Multi-metric analysis", "medium", "Chi phí bán hàng và chi phí quản lý doanh nghiệp của MWG trong Q3 2024 lần lượt là bao nhiêu?", "Chi phí bán hàng và QLDN khoảng 6150 tỷ và 1240 tỷ VND", [6150.0, 1240.0], ["mwg_income_statement_quarterly.csv"]),
        ("VN_HIST_016", "Multi-metric analysis", "medium", "Tổng tài sản và vốn chủ sở hữu của Vinamilk (VNM) tại cuối quý 3 năm 2024 là bao nhiêu?", "Tổng tài sản khoảng 55000 tỷ VND, Vốn chủ sở hữu khoảng 37000 tỷ VND", [55000.0, 37000.0], ["vnm_balance_sheet_quarterly.csv"]),
        ("VN_HIST_017", "Multi-metric analysis", "medium", "Thu nhập lãi thuần và lợi nhuận trước thuế của Vietcombank (VCB) trong Q3 2024 là bao nhiêu?", "Thu nhập lãi thuần khoảng 13800 tỷ, Lợi nhuận trước thuế 10690 tỷ VND", [13800.0, 10690.0], ["vcb_income_statement_quarterly.csv"]),
        ("VN_HIST_018", "Multi-metric analysis", "medium", "Chi phí lãi vay và chi phí tài chính của HPG trong Q3 2024 là bao nhiêu tỷ VND?", "Chi phí tài chính khoảng 950 tỷ, chi phí lãi vay khoảng 560 tỷ VND", [950.0, 560.0], ["hpg_income_statement_quarterly.csv"]),

        # Cross-company comparison (4)
        ("VN_HIST_019", "Cross-company comparison", "hard", "So sánh doanh thu thuần Q3 2024 giữa FPT và Thế Giới Di Động (MWG).", "MWG đạt 34147 tỷ VND, cao hơn FPT đạt 14510 tỷ VND", [34147.0, 14510.0], ["mwg_income_statement_quarterly.csv", "fpt_income_statement_quarterly.csv"]),
        ("VN_HIST_020", "Cross-company comparison", "hard", "So sánh lợi nhuận sau thuế giữa HPG và VCB trong Q3 2024.", "VCB đạt 8690 tỷ VND cao hơn đáng kể so với HPG đạt 3022 tỷ VND", [8690.0, 3022.0], ["vcb_income_statement_quarterly.csv", "hpg_income_statement_quarterly.csv"]),
        ("VN_HIST_021", "Cross-company comparison", "hard", "So sánh biên lợi nhuận ròng giữa Vinamilk (VNM) và Hòa Phát (HPG) trong Q3 2024.", "VNM đạt biên ròng khoảng 15.5%, cao hơn HPG đạt khoảng 8.8%", [15.5, 8.8], ["vnm_income_statement_summary.md", "hpg_income_statement_summary.md"]),
        ("VN_HIST_022", "Cross-company comparison", "hard", "So sánh tổng tài sản giữa Vietcombank (VCB) và Vinamilk (VNM) trong năm 2024.", "VCB là ngân hàng có tổng tài sản trên 1.9 triệu tỷ VND, vượt trội quy mô so với VNM khoảng 55 nghìn tỷ VND", [1900000.0, 55000.0], ["vcb_balance_sheet_quarterly.csv", "vnm_balance_sheet_quarterly.csv"]),

        # Financial statement summary (3)
        ("VN_HIST_023", "Financial statement summary", "medium", "Tóm tắt kết quả hoạt động kinh doanh của FPT trong 9 tháng đầu năm 2024.", "FPT duy trì tăng trưởng doanh thu 15% và lợi nhuận trước thuế trên 19%, mảng IT Global dẫn đầu", [15.0, 19.0], ["fpt_income_statement_summary.md"]),
        ("VN_HIST_024", "Financial statement summary", "medium", "Tóm tắt cơ cấu tài sản và nợ phải trả của HPG tính đến Q3 2024.", "Tài sản dở dang tập trung tại Dung Quất 2, nợ vay được kiểm soát an toàn", [], ["hpg_balance_sheet_quarterly.csv"]),
        ("VN_HIST_025", "Financial statement summary", "medium", "Tóm tắt điểm nhấn lưu chuyển tiền tệ từ hoạt động kinh doanh (CFO) của FPT.", "Dòng tiền từ hoạt động kinh doanh của FPT dương và ổn định qua các quý", [], ["fpt_cash_flow_quarterly.csv"])
    ]

    for qid, sub, diff, query, gt, vals, docs in vn_hist:
        queries.append({
            "query_id": qid,
            "category": "vn_historical_financial",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "billion_vnd" if vals else "text",
            "reporting_period": "Q3 2024",
            "source_reference": docs,
            "required_tools": ["search_financial_reports_and_knowledge"],
            "expected_calculation": "Direct cell lookup or ratio division" if vals else "Summary synthesis",
            "evaluation_rubric": "Accurate numbers within 2% tolerance and correct ticker context."
        })

    # ----------------------------------------------------
    # 2. Global Historical Financial (20 queries)
    # ----------------------------------------------------
    global_hist = [
        # Single metric lookup (6)
        ("GL_HIST_001", "Single metric lookup", "easy", "What was NVIDIA's total revenue in Q3 FY2025?", "$35.08 billion", [35.08], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_002", "Single metric lookup", "easy", "What was NVIDIA's Data Center revenue in Q3 FY2025?", "$30.77 billion", [30.77], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_003", "Single metric lookup", "easy", "What was NVIDIA's Gaming segment revenue in Q3 FY2025?", "$3.28 billion", [3.28], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_004", "Single metric lookup", "easy", "What was Apple's (AAPL) closing stock price on the last trading day of 2024 records?", "Around $250.00 USD", [250.0], ["real_aapl_daily_prices_2024.csv"]),
        ("GL_HIST_005", "Single metric lookup", "easy", "What was Microsoft's (MSFT) 52-week high in the 2024 daily price dataset?", "Approximately $468.35 USD", [468.35], ["real_msft_daily_prices_2024.csv"]),
        ("GL_HIST_006", "Single metric lookup", "easy", "What was Tesla's (TSLA) maximum single-day trading volume in 2024?", "Exceeded 100 million shares", [100.0], ["real_tsla_daily_prices_2024.csv"]),

        # Revenue / earnings growth (4)
        ("GL_HIST_007", "Revenue / earnings growth", "medium", "What was NVIDIA's year-over-year (YoY) total revenue growth rate in Q3 FY2025?", "94% YoY growth", [94.0], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_008", "Revenue / earnings growth", "medium", "What was NVIDIA's Data Center revenue YoY growth rate in Q3 FY2025?", "112% YoY growth", [112.0], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_009", "Revenue / earnings growth", "medium", "What was NVIDIA's gross margin percentage in Q3 FY2025?", "GAAP gross margin of 74.6%", [74.6], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_010", "Revenue / earnings growth", "medium", "What was NVIDIA's net income growth rate YoY in Q3 FY2025?", "GAAP net income grew 109% YoY", [109.0], ["nvidia_q3_fy2025_official_results.docx"]),

        # Segment revenue (4)
        ("GL_HIST_011", "Segment revenue", "medium", "What was NVIDIA's Professional Visualization revenue in Q3 FY2025?", "$486 million", [486.0], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_012", "Segment revenue", "medium", "What was NVIDIA's Automotive segment revenue in Q3 FY2025?", "$449 million", [449.0], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_013", "Segment revenue", "medium", "What proportion of NVIDIA's Q3 FY2025 revenue came from the Data Center segment?", "Approximately 87.7% of total revenue", [87.7], ["nvidia_q3_fy2025_official_results.docx"]),
        ("GL_HIST_014", "Segment revenue", "medium", "How much did NVIDIA return to shareholders in share repurchases and cash dividends in Q3 FY2025?", "$11.2 billion returned to shareholders", [11.2], ["nvidia_q3_fy2025_official_results.docx"]),

        # Stock performance (3)
        ("GL_HIST_015", "Stock performance", "medium", "What was NVIDIA's (NVDA) total price return across 2024 daily price records?", "Exceeded 170% total annual return", [170.0], ["real_nvda_daily_prices_2024.csv"]),
        ("GL_HIST_016", "Stock performance", "medium", "What was Tesla's (TSLA) maximum drawdown percentage in 2024?", "Drawdown exceeded 35% from peak", [35.0], ["real_tsla_daily_prices_2024.csv"]),
        ("GL_HIST_017", "Stock performance", "medium", "Compare the price volatility of TSLA vs AAPL in 2024 daily prices.", "TSLA exhibited significantly higher beta and price volatility than AAPL", [], ["real_tsla_daily_prices_2024.csv", "real_aapl_daily_prices_2024.csv"]),

        # Cross-company comparison (3)
        ("GL_HIST_018", "Cross-company comparison", "hard", "Compare Apple (AAPL) and Microsoft (MSFT) stock performance trends in 2024.", "Both showed solid gains with MSFT leading in H1 and AAPL surging on Apple Intelligence in H2", [], ["real_aapl_daily_prices_2024.csv", "real_msft_daily_prices_2024.csv"]),
        ("GL_HIST_019", "Cross-company comparison", "hard", "Compare 2024 stock return between NVIDIA (NVDA) and Tesla (TSLA).", "NVDA strongly outperformed TSLA driven by AI chip demand", [], ["real_nvda_daily_prices_2024.csv", "real_tsla_daily_prices_2024.csv"]),
        ("GL_HIST_020", "Cross-company comparison", "hard", "Which stock among NVDA, AAPL, MSFT, and TSLA had the highest average daily trading volume in 2024?", "NVDA and TSLA recorded the highest daily trading turnover", [], ["real_nvda_daily_prices_2024.csv", "real_tsla_daily_prices_2024.csv"])
    ]

    for qid, sub, diff, query, gt, vals, docs in global_hist:
        queries.append({
            "query_id": qid,
            "category": "global_historical_financial",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "USD / %",
            "reporting_period": "FY2025 / 2024",
            "source_reference": docs,
            "required_tools": ["search_financial_reports_and_knowledge"],
            "expected_calculation": "Document retrieval and calculation",
            "evaluation_rubric": "Correct identification of figures and accurate comparative analysis."
        })

    # ----------------------------------------------------
    # 3. Ratios & Valuation (20 queries)
    # ----------------------------------------------------
    ratios_val = [
        # Single ratio (6)
        ("RATIO_001", "Single ratio", "easy", "Tỷ số P/E trailing (TTM) của Vinamilk (VNM) trong mô hình định giá VN30 2024 là bao nhiêu?", "16.5x", [16.5], ["vinamilk_vn30_financial_model_2024.xlsx"]),
        ("RATIO_002", "Single ratio", "easy", "Tỷ suất sinh lời trên vốn chủ sở hữu (ROE) của Vinamilk (VNM) năm 2024 là bao nhiêu %?", "Khoảng 24.1%", [24.1], ["vinamilk_vn30_financial_model_2024.xlsx", "vnm_income_statement_summary.md"]),
        ("RATIO_003", "Single ratio", "easy", "Tỷ số P/B của Hòa Phát (HPG) trong mô hình định giá VN30 2024 là bao nhiêu?", "Khoảng 1.45x đến 1.6x", [1.5], ["vinamilk_vn30_financial_model_2024.xlsx"]),
        ("RATIO_004", "Single ratio", "easy", "Tỷ suất sinh lời trên vốn chủ sở hữu (ROE) của Vietcombank (VCB) đạt mức bao nhiêu?", "ROE trên 21.5%", [21.5], ["vcb_income_statement_summary.md"]),
        ("RATIO_005", "Single ratio", "easy", "Biên lợi nhuận gộp trung bình của FPT duy trì ở mức bao nhiêu %?", "Khoảng 38% đến 39.5%", [39.0], ["fpt_income_statement_summary.md"]),
        ("RATIO_006", "Single ratio", "easy", "Biên lợi nhuận sau thuế của MWG năm 2024 phục hồi lên mức bao nhiêu?", "Biên ròng khoảng 2.8% đến 3.2%", [3.0], ["mwg_income_statement_summary.md"]),

        # Multi-ratio analysis (6)
        ("RATIO_007", "Multi-ratio analysis", "medium", "Phân tích bộ ba chỉ số P/E, P/B và ROE của Vinamilk (VNM) trong mô hình VN30.", "P/E 16.5x, P/B ~3.8x, ROE ~24.1%", [16.5, 3.8, 24.1], ["vinamilk_vn30_financial_model_2024.xlsx"]),
        ("RATIO_008", "Multi-ratio analysis", "medium", "Liệt kê P/E, ROE và tỷ lệ nợ xấu (NPL) của Vietcombank (VCB).", "P/E ~14.0x, ROE >21%, NPL <1.0%", [14.0, 21.0, 1.0], ["vcb_income_statement_summary.md"]),
        ("RATIO_009", "Multi-ratio analysis", "medium", "Đánh giá khả năng sinh lời của HPG qua biên lợi nhuận gộp và biên EBITDA năm 2024.", "Biên gộp cải thiện lên 17-18%, EBITDA margin đạt trên 22%", [17.5, 22.0], ["hpg_income_statement_summary.md"]),
        ("RATIO_010", "Multi-ratio analysis", "medium", "So sánh ROA và ROE của FPT trong năm 2024.", "ROA đạt ~13.5%, ROE đạt ~27.0%", [13.5, 27.0], ["fpt_income_statement_summary.md"]),
        ("RATIO_011", "Multi-ratio analysis", "medium", "Các chỉ số thanh toán hiện hành và thanh toán nhanh của VNM cho thấy điều gì?", "Khả năng thanh toán dồi dào với tỷ số hiện hành trên 1.8x", [1.8], ["vnm_balance_sheet_quarterly.csv"]),
        ("RATIO_012", "Multi-ratio analysis", "medium", "Phân tích vòng quay tài sản và đòn bẩy tài chính của MWG trong năm 2024.", "Vòng quay tài sản trên 1.5x, đòn bẩy tài chính duy trì ở mức an toàn", [1.5], ["mwg_balance_sheet_quarterly.csv"]),

        # Peer comparison (4)
        ("RATIO_013", "Peer comparison", "hard", "So sánh định giá P/E giữa FPT và VNM theo mô hình VN30.", "FPT giao dịch ở P/E khoảng 24-26x cao hơn VNM ở mức 16.5x do triển vọng tăng trưởng AI/IT", [25.0, 16.5], ["vinamilk_vn30_financial_model_2024.xlsx"]),
        ("RATIO_014", "Peer comparison", "hard", "So sánh ROE giữa HPG và VCB năm 2024.", "VCB duy trì ROE ổn định trên 21% trong khi HPG đang trong chu kỳ hồi phục ROE đạt khoảng 12-14%", [21.0, 13.0], ["vcb_income_statement_summary.md", "hpg_income_statement_summary.md"]),
        ("RATIO_015", "Peer comparison", "hard", "So sánh biên lợi nhuận ròng giữa FPT và MWG.", "FPT đạt biên ròng ~15.5% vượt trội so với biên ròng ngành bán lẻ của MWG ~3.0%", [15.5, 3.0], ["fpt_income_statement_summary.md", "mwg_income_statement_summary.md"]),
        ("RATIO_016", "Peer comparison", "hard", "So sánh hệ số nợ trên vốn chủ sở hữu (D/E) giữa HPG và VNM.", "HPG có D/E cao hơn do tài trợ đại dự án Dung Quất 2, VNM có D/E rất thấp và tiền mặt dồi dào", [], ["hpg_balance_sheet_quarterly.csv", "vnm_balance_sheet_quarterly.csv"]),

        # DCF / valuation framework (4)
        ("RATIO_017", "DCF / valuation framework", "medium", "Nêu công thức tính Chi phí vốn bình quân (WACC) theo chuẩn CFA.", "WACC = (E/V * Re) + (D/V * Rd * (1 - Tc))", [], ["cfa_equity_research_and_valuation_framework.md"]),
        ("RATIO_018", "DCF / valuation framework", "hard", "Giải thích cách tính Dòng tiền tự do cho doanh nghiệp (FCFF) từ EBIT hoặc Net Income.", "FCFF = NI + Non-cash - CapEx - Delta NWC + Int*(1-t) hoặc EBIT*(1-t) + Dep - CapEx - Delta NWC", [], ["cfa_equity_research_and_valuation_framework.md"]),
        ("RATIO_019", "DCF / valuation framework", "hard", "Công thức tính Giá trị tận cùng (Terminal Value) theo mô hình Gordon Growth là gì?", "TV = FCFF_(n+1) / (WACC - g)", [], ["cfa_equity_research_and_valuation_framework.md"]),
        ("RATIO_020", "DCF / valuation framework", "hard", "Sự khác biệt căn bản giữa mô hình định giá FCFF (Enterprise Value) và FCFE (Equity Value) là gì?", "FCFF chiết khấu theo WACC ra Enterprise Value, FCFE chiết khấu theo Cost of Equity ra Equity Value", [], ["cfa_equity_research_and_valuation_framework.md"])
    ]

    for qid, sub, diff, query, gt, vals, docs in ratios_val:
        queries.append({
            "query_id": qid,
            "category": "ratios_and_valuation",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "ratio / %" if vals else "formula",
            "reporting_period": "2024",
            "source_reference": docs,
            "required_tools": ["search_financial_reports_and_knowledge"],
            "expected_calculation": "Ratio calculation and valuation formulas",
            "evaluation_rubric": "Accurate ratio values and complete financial formula representation."
        })

    # ----------------------------------------------------
    # 4. Definitions & Formulas (10 queries)
    # ----------------------------------------------------
    defs_formulas = [
        # Technical indicators (4)
        ("DEF_001", "Technical indicators", "easy", "Chỉ báo RSI (Relative Strength Index) là gì và công thức tính như thế nào?", "RSI = 100 - (100 / (1 + RS)), với RS = Trung bình tăng / Trung bình giảm", [], ["rsi.md"]),
        ("DEF_002", "Technical indicators", "easy", "Vùng quá mua (overbought) và quá bán (oversold) của chỉ báo RSI thường được quy ước ở mức nào?", "Quá mua trên 70, quá bán dưới 30", [70.0, 30.0], ["rsi.md"]),
        ("DEF_003", "Technical indicators", "medium", "Hiện tượng phân kỳ RSI (RSI Divergence) báo hiệu điều gì trong phân tích kỹ thuật?", "Phân kỳ dương báo hiệu đảo chiều tăng giá, phân kỳ âm báo hiệu đảo chiều giảm giá", [], ["rsi.md"]),
        ("DEF_004", "Technical indicators", "medium", "Chỉ báo MACD được cấu tạo từ các đường nào?", "Gồm đường MACD (EMA12 - EMA26), đường tín hiệu Signal (EMA9 của MACD) và biểu đồ Histogram", [], ["cfa_equity_research_and_valuation_framework.md"]),

        # Valuation formulas (3)
        ("DEF_005", "Valuation formulas", "easy", "Chỉ số P/E (Price-to-Earnings) được tính bằng công thức nào?", "P/E = Giá thị trường mỗi cổ phần (Market Price) / Thu nhập trên mỗi cổ phần (EPS)", [], ["pe_ratio.md"]),
        ("DEF_006", "Valuation formulas", "medium", "Phân tích DuPont 3 yếu tố của ROE gồm những thành phần nào?", "ROE = Net Profit Margin * Asset Turnover * Financial Leverage", [], ["cfa_equity_research_and_valuation_framework.md"]),
        ("DEF_007", "Valuation formulas", "medium", "Chỉ số PEG (Price/Earnings to Growth) được tính như thế nào và có ý nghĩa gì?", "PEG = P/E / Tỷ lệ tăng trưởng lợi nhuận (g). PEG < 1 ngụ ý cổ phiếu định giá hấp dẫn so với tăng trưởng", [1.0], ["pe_ratio.md"]),

        # Financial concepts (3)
        ("DEF_008", "Financial concepts", "easy", "Phân biệt biên lợi nhuận gộp (Gross Margin) và biên lợi nhuận ròng (Net Margin).", "Biên gộp = Lợi nhuận gộp / Doanh thu thuần, Biên ròng = Lợi nhuận sau thuế / Doanh thu thuần", [], ["cfa_equity_research_and_valuation_framework.md"]),
        ("DEF_009", "Financial concepts", "medium", "Tại sao Lợi nhuận sau thuế (Net Income) không bằng Dòng tiền hoạt động kinh doanh (CFO)?", "Do nguyên tắc kế toán dồn tích (accrual accounting), chi phí phi tiền mặt (khấu hao) và biến động vốn lưu động", [], ["cfa_equity_research_and_valuation_framework.md"]),
        ("DEF_010", "Financial concepts", "medium", "Nêu định nghĩa và ý nghĩa của EBITDA trong phân tích tài chính.", "EBITDA là lợi nhuận trước lãi vay, thuế và khấu hao, đo lường dòng tiền hoạt động thuần túy của doanh nghiệp", [], ["cfa_equity_research_and_valuation_framework.md"])
    ]

    for qid, sub, diff, query, gt, vals, docs in defs_formulas:
        queries.append({
            "query_id": qid,
            "category": "definitions_and_formulas",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "definition",
            "reporting_period": "N/A",
            "source_reference": docs,
            "required_tools": ["search_financial_reports_and_knowledge"],
            "expected_calculation": "Conceptual explanation",
            "evaluation_rubric": "Accurate definitions, formulas, and financial reasoning."
        })

    # ----------------------------------------------------
    # 5. Realtime Price (25 queries)
    # ----------------------------------------------------
    realtime_prices = [
        # VN single-stock quote (7)
        ("RT_PRICE_001", "VN single-stock quote", "easy", "Giá cổ phiếu FPT hiện tại trên sàn chứng khoán Việt Nam là bao nhiêu?", "138,500 VND", [138500.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_002", "VN single-stock quote", "easy", "Cho biết thị giá hiện tại của cổ phiếu Vietcombank (VCB).", "91,200 VND", [91200.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_003", "VN single-stock quote", "easy", "Cổ phiếu Hòa Phát (HPG) đang khớp lệnh ở mức giá bao nhiêu?", "26,800 VND", [26800.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_004", "VN single-stock quote", "easy", "Thị giá cổ phiếu Thế Giới Di Động (MWG) hiện nay là bao nhiêu?", "65,400 VND", [65400.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_005", "VN single-stock quote", "easy", "Cổ phiếu Vinamilk (VNM) hôm nay đang giao dịch ở giá nào?", "68,000 VND", [68000.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_006", "VN single-stock quote", "easy", "Kiểm tra giá realtime của mã chứng khoán FPT.", "138,500 VND", [138500.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_007", "VN single-stock quote", "easy", "Tra cứu giá cổ phiếu HPG phiên hôm nay.", "26,800 VND", [26800.0], "get_vietnam_stock_quote"),

        # Global single-stock quote (7)
        ("RT_PRICE_008", "Global single-stock quote", "easy", "What is NVIDIA's (NVDA) current stock price on NASDAQ?", "$141.50 USD", [141.50], "get_global_stock_quote"),
        ("RT_PRICE_009", "Global single-stock quote", "easy", "What is Apple's (AAPL) live stock price right now?", "$232.10 USD", [232.10], "get_global_stock_quote"),
        ("RT_PRICE_010", "Global single-stock quote", "easy", "Retrieve current market quote for Microsoft (MSFT).", "$428.50 USD", [428.50], "get_global_stock_quote"),
        ("RT_PRICE_011", "Global single-stock quote", "easy", "What is Tesla's (TSLA) current trading price?", "$258.00 USD", [258.00], "get_global_stock_quote"),
        ("RT_PRICE_012", "Global single-stock quote", "easy", "What is AMD's current stock quote?", "$158.20 USD", [158.20], "get_global_stock_quote"),
        ("RT_PRICE_013", "Global single-stock quote", "easy", "What is the live stock price of TSMC (TSM)?", "$192.40 USD", [192.40], "get_global_stock_quote"),
        ("RT_PRICE_014", "Global single-stock quote", "easy", "Check the latest stock price for Alphabet (GOOGL).", "$178.60 USD", [178.60], "get_global_stock_quote"),

        # Price change / performance (5)
        ("RT_PRICE_015", "Price change / performance", "medium", "Hôm nay cổ phiếu FPT tăng hay giảm bao nhiêu %?", "Tăng +1.84%", [1.84], "get_vietnam_stock_quote"),
        ("RT_PRICE_016", "Price change / performance", "medium", "Biến động tỷ lệ phần trăm trong ngày của HPG là bao nhiêu?", "Tăng +1.13%", [1.13], "get_vietnam_stock_quote"),
        ("RT_PRICE_017", "Price change / performance", "medium", "What is NVIDIA's (NVDA) percentage gain today?", "Up +3.20%", [3.20], "get_global_stock_quote"),
        ("RT_PRICE_018", "Price change / performance", "medium", "What is Tesla's (TSLA) percentage change today?", "Up +4.50%", [4.50], "get_global_stock_quote"),
        ("RT_PRICE_019", "Price change / performance", "medium", "Cổ phiếu MWG hôm nay tăng hay giảm bao nhiêu %?", "Giảm -0.61%", [-0.61], "get_vietnam_stock_quote"),

        # OHLC / price range (3)
        ("RT_PRICE_020", "OHLC / price range", "medium", "Biên độ giá dao động trong ngày (Day Range) của FPT hôm nay là bao nhiêu?", "Dao động từ 135,500 đến 139,200 VND", [135500.0, 139200.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_021", "OHLC / price range", "medium", "Giá mở cửa, cao nhất và thấp nhất của HPG hôm nay là bao nhiêu?", "Mở cửa: 26,500, Cao nhất: 27,000, Thấp nhất: 26,300 VND", [26500.0, 27000.0, 26300.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_022", "OHLC / price range", "medium", "What is the day trading range (Low - High) for NVIDIA (NVDA) today?", "$138.20 - $142.80 USD", [138.20, 142.80], "get_global_stock_quote"),

        # Volume / trading activity (3)
        ("RT_PRICE_023", "Volume / trading activity", "medium", "Khối lượng giao dịch của HPG trong phiên hôm nay đạt bao nhiêu cổ phiếu?", "22,410,000 cổ phiếu", [22410000.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_024", "Volume / trading activity", "medium", "Khối lượng khớp lệnh của cổ phiếu FPT hôm nay đạt bao nhiêu cổ phiếu?", "4,850,200 cổ phiếu", [4850200.0], "get_vietnam_stock_quote"),
        ("RT_PRICE_025", "Volume / trading activity", "medium", "What is the 52-week trading range and market cap for Apple (AAPL)?", "52-week range $164.08 - $237.23, Market Cap $3.52T", [164.08, 237.23, 3.52], "get_global_stock_quote")
    ]

    for qid, sub, diff, query, gt, vals, tool_name in realtime_prices:
        queries.append({
            "query_id": qid,
            "category": "realtime_price",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "VND / USD / %",
            "reporting_period": "Realtime Snapshot 2024-10-30",
            "source_reference": ["realtime_snapshot_20241030.json"],
            "required_tools": [tool_name],
            "expected_calculation": "Realtime quote parsing",
            "evaluation_rubric": "Exact price match and correct sign for percentage change."
        })

    # ----------------------------------------------------
    # 6. Sector / Market Overview (25 queries)
    # ----------------------------------------------------
    sector_market = [
        # VN market movers (6)
        ("MKT_001", "VN market movers", "easy", "Điểm qua các cổ phiếu tâm điểm dẫn dắt rổ VN30 hôm nay.", "Các mã tâm điểm gồm FPT, HPG, VCB, MWG, VNM", [], "get_vietnam_market_movers"),
        ("MKT_002", "VN market movers", "easy", "Thị trường chứng khoán Việt Nam hôm nay các nhóm ngành nào thu hút dòng tiền?", "Nhóm công nghệ (FPT), thép (HPG) và ngân hàng (VCB) dẫn dắt", [], "get_vietnam_market_movers"),
        ("MKT_003", "VN market movers", "medium", "Tình hình giao dịch chung của rổ cổ phiếu VN30 hôm nay như thế nào?", "Độ rộng nghiêng về sắc xanh với FPT (+1.84%) và HPG (+1.13%) tích cực", [], "get_vietnam_market_movers"),
        ("MKT_004", "VN market movers", "medium", "Cổ phiếu thép HPG có diễn biến như thế nào so với toàn thị trường hôm nay?", "HPG tăng 1.13% với thanh khoản khớp lệnh dẫn đầu rổ VN30 trên 22 triệu đơn vị", [1.13, 22.0], "get_vietnam_market_movers"),
        ("MKT_005", "VN market movers", "medium", "Cổ phiếu ngành bán lẻ MWG hôm nay vận động ra sao?", "MWG điều chỉnh nhẹ -0.61% quanh mốc 65,400 VND", [-0.61, 65400.0], "get_vietnam_market_movers"),
        ("MKT_006", "VN market movers", "medium", "Tóm tắt xu hướng thị trường Việt Nam hiện tại qua các cổ phiếu trụ cột.", "VN-Index giữ nhịp tích cực nhờ sự nâng đỡ của trụ công nghệ và sản xuất", [], "get_vietnam_market_movers"),

        # Global market movers (6)
        ("MKT_007", "Global market movers", "easy", "Give me a market overview of Global AI and Cloud Infrastructure leaders today.", "AI leaders showed solid gains led by NVDA (+3.20%) and TSM (+2.80%)", [], "get_ai_tech_sector_movers"),
        ("MKT_008", "Global market movers", "easy", "Which AI semiconductor stocks are gaining the most today?", "NVIDIA (+3.20%), TSMC (+2.80%), and AMD (+2.10%) are leading gainers", [3.20, 2.80, 2.10], "get_ai_tech_sector_movers"),
        ("MKT_009", "Global market movers", "medium", "How are Microsoft, Alphabet, and Amazon trading today in the AI sector?", "MSFT (+1.10%), GOOGL (+1.40%), AMZN (+1.25%) are trading higher", [1.10, 1.40, 1.25], "get_ai_tech_sector_movers"),
        ("MKT_010", "Global market movers", "medium", "What is the daily performance spread among Big Tech cloud providers?", "Cloud providers showed consistent moderate gains around 1% - 1.5%", [1.0, 1.5], "get_ai_tech_sector_movers"),
        ("MKT_011", "Global market movers", "medium", "Compare today's performance between semiconductor chipmakers and cloud hyperscalers.", "Hardware chipmakers (NVDA, TSM, AMD) outperformed cloud hyperscalers (MSFT, AMZN, GOOGL)", [], "get_ai_tech_sector_movers"),
        ("MKT_012", "Global market movers", "medium", "Summary of global tech momentum in today's trading session.", "Strong tech momentum with all major AI infrastructure names in green", [], "get_ai_tech_sector_movers"),

        # Sector performance (5)
        ("MKT_013", "Sector performance", "medium", "Đánh giá hiệu suất nhóm cổ phiếu Công nghệ - Bán dẫn toàn cầu hôm nay.", "Ngành bán dẫn ghi nhận phiên tăng điểm tích cực nhờ kỳ vọng nhu cầu AI chip", [], "get_ai_tech_sector_movers"),
        ("MKT_014", "Sector performance", "medium", "Tổng quan hiệu suất ngành Ngân hàng Việt Nam thông qua đại diện VCB.", "VCB duy trì vị thế trụ đỡ vững chắc với mức tăng nhẹ +0.44%", [0.44], "get_vietnam_stock_quote"),
        ("MKT_015", "Sector performance", "medium", "Nhóm cổ phiếu Bán lẻ tiêu dùng (MWG, VNM) hôm nay thể hiện thế nào?", "Nhóm tiêu dùng đi ngang và tích lũy nhẹ quanh tham chiếu", [], "get_vietnam_market_movers"),
        ("MKT_016", "Sector performance", "hard", "So sánh xung lực tăng giá giữa nhóm AI Hardware (NVDA, TSM) và nhóm Tech Việt Nam (FPT).", "Cả NVDA (+3.20%) và FPT (+1.84%) đều thể hiện sức mạnh vượt trội so với thị trường chung", [3.20, 1.84], "get_ai_tech_sector_movers"),
        ("MKT_017", "Sector performance", "medium", "What is the daily return of TSMC (TSM) and what does it indicate for foundry demand?", "TSM rose +2.80% to $192.40, indicating robust advanced packaging demand", [2.80, 192.40], "get_ai_tech_sector_movers"),

        # Market summary (4)
        ("MKT_018", "Market summary", "easy", "Tóm tắt ngắn gọn thị trường chứng khoán Việt Nam phiên hôm nay.", "Thị trường sắc xanh chiếm ưu thế, dẫn đầu bởi nhóm VN30", [], "get_vietnam_market_movers"),
        ("MKT_019", "Market summary", "easy", "Briefly summarize the overall US tech market today.", "US technology sector posted broad gains led by AI semiconductor momentum", [], "get_ai_tech_sector_movers"),
        ("MKT_020", "Market summary", "medium", "Điểm tin các cổ phiếu vốn hóa lớn VN30: FPT, VNM, VCB, HPG.", "FPT và HPG dẫn dắt chiều tăng, VNM đi ngang tại tham chiếu, VCB giữ nhịp", [], "get_vietnam_market_movers"),
        ("MKT_021", "Market summary", "medium", "Global semiconductor market brief: NVDA, AMD, TSM.", "Chipmaker trio recorded uniform gains above 2%", [2.0], "get_ai_tech_sector_movers"),

        # Market activity / breadth (4)
        ("MKT_022", "Market activity / breadth", "medium", "Độ rộng thị trường nhóm cổ phiếu đầu ngành VN30 nghiêng về chiều nào?", "Độ rộng tích cực với 3 mã tăng (FPT, HPG, VCB), 1 mã tham chiếu (VNM), 1 mã giảm nhẹ (MWG)", [], "get_vietnam_market_movers"),
        ("MKT_023", "Market activity / breadth", "medium", "Cổ phiếu nào trong nhóm VN30 có khối lượng khớp lệnh nổi bật nhất hôm nay?", "HPG với khối lượng giao dịch áp đảo trên 22 triệu cổ phiếu", [22.0], "get_vietnam_market_movers"),
        ("MKT_024", "Market activity / breadth", "medium", "Are all major AI tech sector leaders positive today?", "Yes, all monitored key leaders (NVDA, MSFT, GOOGL, AMD, TSM, AMZN) posted positive daily returns", [], "get_ai_tech_sector_movers"),
        ("MKT_025", "Market activity / breadth", "medium", "Which company between NVDA and MSFT has a higher market capitalization today?", "Apple and NVIDIA maintain market caps around $3.5T, higher than MSFT at $3.18T", [3.5, 3.18], "get_global_stock_quote")
    ]

    for qid, sub, diff, query, gt, vals, tool_name in sector_market:
        queries.append({
            "query_id": qid,
            "category": "sector_market_overview",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "market_summary",
            "reporting_period": "Realtime Snapshot 2024-10-30",
            "source_reference": ["realtime_snapshot_20241030.json"],
            "required_tools": [tool_name],
            "expected_calculation": "Sector ranking and breadth analysis",
            "evaluation_rubric": "Correct identification of market leaders, ranking, and sector trends."
        })

    # ----------------------------------------------------
    # 7. Cross-company Comparison (15 queries)
    # ----------------------------------------------------
    cross_comp = [
        # VN vs VN (5)
        ("COMP_001", "VN vs VN", "medium", "So sánh quy mô vốn chủ sở hữu và tổng tài sản giữa Vietcombank (VCB) và Hòa Phát (HPG).", "VCB có tổng tài sản vượt trội trên 1.9 triệu tỷ VND so với HPG khoảng 200 nghìn tỷ VND", [1900000.0, 200000.0], ["vcb_balance_sheet_quarterly.csv", "hpg_balance_sheet_quarterly.csv"]),
        ("COMP_002", "VN vs VN", "medium", "So sánh biên lợi nhuận ròng giữa Vinamilk (VNM) và Thế Giới Di Động (MWG) năm 2024.", "VNM đạt biên ròng ~15% cao hơn đáng kể so với MWG khoảng ~3%", [15.0, 3.0], ["vnm_income_statement_summary.md", "mwg_income_statement_summary.md"]),
        ("COMP_003", "VN vs VN", "medium", "So sánh tốc độ tăng trưởng doanh thu thuần giữa FPT và MWG trong Q3 2024.", "FPT tăng trưởng ổn định 15% trong khi MWG tăng trưởng hồi phục từ mức nền thấp", [15.0], ["fpt_income_statement_summary.md", "mwg_income_statement_summary.md"]),
        ("COMP_004", "VN vs VN", "hard", "So sánh hiệu quả sử dụng vốn (ROE) giữa FPT và Vinamilk (VNM).", "Cả hai đều có ROE hàng đầu VN30, FPT đạt ~27% và VNM đạt ~24%", [27.0, 24.0], ["fpt_income_statement_summary.md", "vinamilk_vn30_financial_model_2024.xlsx"]),
        ("COMP_005", "VN vs VN", "hard", "So sánh dòng tiền thuần từ hoạt động kinh doanh giữa HPG và VNM năm 2024.", "VNM có dòng tiền hoạt động kinh doanh thặng dư đều đặn, HPG dòng tiền tập trung bù đắp CapEx Dung Quất 2", [], ["hpg_cash_flow_quarterly.csv", "vnm_cash_flow_quarterly.csv"]),

        # Global vs Global (4)
        ("COMP_006", "Global vs Global", "medium", "Compare the market capitalizations of Apple (AAPL) and Microsoft (MSFT).", "Apple and Microsoft both exceed $3.1T - $3.5T in market capitalization", [3.1, 3.5], ["real_aapl_daily_prices_2024.csv", "real_msft_daily_prices_2024.csv"]),
        ("COMP_007", "Global vs Global", "medium", "Compare the 2024 stock return of NVIDIA (NVDA) vs Microsoft (MSFT).", "NVIDIA returned over 170% in 2024, far outperforming Microsoft at ~15-20%", [170.0, 15.0], ["real_nvda_daily_prices_2024.csv", "real_msft_daily_prices_2024.csv"]),
        ("COMP_008", "Global vs Global", "hard", "Compare price volatility and maximum drawdown between Tesla (TSLA) and Apple (AAPL) in 2024.", "TSLA had much larger swings and a >35% drawdown compared to AAPL's resilient trajectory", [35.0], ["real_tsla_daily_prices_2024.csv", "real_aapl_daily_prices_2024.csv"]),
        ("COMP_009", "Global vs Global", "hard", "Compare P/E valuation multiples between NVIDIA and Apple.", "NVIDIA trades at a higher growth P/E multiple (~64x) compared to Apple (~35x)", [64.0, 35.0], ["real_nvda_daily_prices_2024.csv", "real_aapl_daily_prices_2024.csv"]),

        # Cross-market comparison (3)
        ("COMP_010", "Cross-market comparison", "hard", "So sánh định hướng đầu tư AI của FPT tại Việt Nam và NVIDIA trên quy mô toàn cầu.", "FPT là đối tác triển khai AI Factory sử dụng phần cứng GPU của NVIDIA", [], ["fpt_income_statement_summary.md", "nvidia_q3_fy2025_official_results.docx"]),
        ("COMP_011", "Cross-market comparison", "hard", "Compare stock performance of tech champion FPT (Vietnam) vs NVIDIA (US) in 2024.", "Both stocks had extraordinary outperformance in their respective benchmark indices", [], ["fpt_income_statement_summary.md", "real_nvda_daily_prices_2024.csv"]),
        ("COMP_012", "Cross-market comparison", "hard", "So sánh bội số định giá P/E của thị trường VN30 với nhóm Big Tech Mỹ.", "VN30 trung bình P/E 12-16x, thấp hơn đáng kể so với Big Tech Mỹ 30-60x", [14.0, 35.0], ["vinamilk_vn30_financial_model_2024.xlsx", "real_msft_daily_prices_2024.csv"]),

        # Multi-company, multi-metric comparison (3)
        ("COMP_013", "Multi-company, multi-metric comparison", "hard", "So sánh doanh thu, lợi nhuận sau thuế và ROE giữa 3 doanh nghiệp: FPT, HPG, VNM.", "FPT tăng trưởng cao, VNM biên ròng ổn định, HPG lợi nhuận phục hồi theo chu kỳ thép", [], ["fpt_income_statement_summary.md", "hpg_income_statement_summary.md", "vnm_income_statement_summary.md"]),
        ("COMP_014", "Multi-company, multi-metric comparison", "hard", "Xếp hạng quy mô vốn hóa thị trường của 4 mã công nghệ: NVDA, AAPL, MSFT, TSLA.", "Thứ tự: AAPL/NVDA (~$3.5T) > MSFT (~$3.2T) > TSLA (~$825B)", [3.5, 3.2, 825.0], ["real_nvda_daily_prices_2024.csv", "real_aapl_daily_prices_2024.csv", "real_msft_daily_prices_2024.csv", "real_tsla_daily_prices_2024.csv"]),
        ("COMP_015", "Multi-company, multi-metric comparison", "hard", "So sánh đòn bẩy tài chính (Debt/Equity) giữa FPT, MWG, HPG.", "HPG có D/E cao nhất để tài trợ CapEx, FPT và MWG duy trì đòn bẩy vừa phải", [], ["fpt_balance_sheet_quarterly.csv", "mwg_balance_sheet_quarterly.csv", "hpg_balance_sheet_quarterly.csv"])
    ]

    for qid, sub, diff, query, gt, vals, docs in cross_comp:
        queries.append({
            "query_id": qid,
            "category": "cross_company_comparison",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "comparison",
            "reporting_period": "2024",
            "source_reference": docs,
            "required_tools": ["search_financial_reports_and_knowledge"],
            "expected_calculation": "Cross-company synthesis",
            "evaluation_rubric": "Accurate cross-entity facts and objective comparative judgment."
        })

    # ----------------------------------------------------
    # 8. Financial Analysis & Reasoning (10 queries)
    # ----------------------------------------------------
    reasoning = [
        # Financial trend interpretation (3)
        ("REASON_001", "Financial trend interpretation", "hard", "Phân tích động lực giúp mảng Dịch vụ CNTT nước ngoài (Global IT) của FPT duy trì tăng trưởng hai con số.", "Được thúc đẩy bởi nhu cầu chuyển đổi số, dịch vụ AI và các hợp đồng quy mô lớn tại Nhật Bản, Mỹ và APAC", [], ["fpt_income_statement_summary.md"]),
        ("REASON_002", "Financial trend interpretation", "hard", "Giải thích tác động của đại dự án Dung Quất 2 đối với triển vọng doanh thu và biên lợi nhuận của Hòa Phát (HPG).", "Dung Quất 2 bổ sung 5.6 triệu tấn thép HRC chất lượng cao, tối ưu hóa quy mô và tăng trưởng doanh thu dài hạn", [], ["hpg_income_statement_summary.md"]),
        ("REASON_003", "Financial trend interpretation", "hard", "Chuỗi Bách Hóa Xanh đạt điểm hòa vốn có ý nghĩa như thế nào đối với cấu trúc lợi nhuận của MWG?", "Chấm dứt việc bào mòn lợi nhuận từ các năm trước, đóng góp dòng tiền dương và cải thiện biên lợi nhuận ròng hợp nhất", [], ["mwg_income_statement_summary.md"]),

        # Profitability / risk analysis (3)
        ("REASON_004", "Profitability / risk analysis", "hard", "Đánh giá chất lượng tài sản và bộ đệm rủi ro tín dụng của Vietcombank (VCB).", "VCB có tỷ lệ bao phủ nợ xấu (LLR) cao nhất hệ thống ngân hàng, tỷ lệ nPL dưới 1%, an toàn vốn vượt chuẩn Basel II", [1.0], ["vcb_income_statement_summary.md"]),
        ("REASON_005", "Profitability / risk analysis", "hard", "Yếu tố giá nguyên vật liệu sữa bột thế giới biến động ảnh hưởng như thế nào đến biên lợi nhuận gộp của Vinamilk?", "Giá sữa bột nhập khẩu giảm giúp mở rộng biên lợi nhuận gộp; ngược lại giá tăng sẽ tạo áp lực chi phí sản xuất", [], ["vnm_income_statement_summary.md"]),
        ("REASON_006", "Profitability / risk analysis", "hard", "Phân tích rủi ro cạnh tranh giá xe điện (EV Price War) và tác động đến biên lợi nhuận của Tesla (TSLA) năm 2024.", "Chiến dịch giảm giá để bảo vệ thị phần đã làm suy giảm biên lợi nhuận gộp mảng ô tô của Tesla trong năm 2024", [], ["real_tsla_daily_prices_2024.csv"]),

        # Valuation reasoning (2)
        ("REASON_007", "Valuation reasoning", "hard", "Mức định giá P/E 16.5x của Vinamilk (VNM) có phù hợp với vị thế doanh nghiệp sữa đầu ngành trả cổ tức cao không?", "Hợp lý cho cổ phiếu phòng thủ (defensive stock) có tỷ suất cổ tức đều đặn 4-5% và dòng tiền tự do dồi dào", [16.5], ["vinamilk_vn30_financial_model_2024.xlsx"]),
        ("REASON_008", "Valuation reasoning", "hard", "Tại sao thị trường chấp nhận mức định giá P/E cao trên 60x cho NVIDIA (NVDA) trong năm 2024?", "Bởi tốc độ tăng trưởng doanh thu và lợi nhuận trên 100% YoY từ mảng Data Center, mang lại hệ số PEG hấp dẫn", [60.0, 100.0], ["nvidia_q3_fy2025_official_results.docx", "real_nvda_daily_prices_2024.csv"]),

        # Evidence-based conclusion (2)
        ("REASON_009", "Evidence-based conclusion", "hard", "Tổng hợp các luận điểm đầu tư chính đối với cổ phiếu FPT dựa trên báo cáo tài chính và triển vọng AI.", "Luận điểm dựa trên: 1. Doanh thu phần mềm nước ngoài vững chắc; 2. Hợp tác AI Factory; 3. Biên ròng >15% và ROE ~27%", [15.0, 27.0], ["fpt_income_statement_summary.md"]),
        ("REASON_010", "Evidence-based conclusion", "hard", "Dựa trên chu kỳ ngành thép và báo cáo tài chính 2024, rút ra kết luận về vị thế cạnh tranh của Hòa Phát (HPG).", "HPG là nhà sản xuất thép chi phí thấp nhất khu vực, biên gộp hồi phục và sẵn sàng bứt phá khi Dung Quất 2 vận hành", [], ["hpg_income_statement_summary.md"])
    ]

    for qid, sub, diff, query, gt, vals, docs in reasoning:
        queries.append({
            "query_id": qid,
            "category": "financial_analysis_reasoning",
            "subcategory": sub,
            "difficulty": diff,
            "query": query,
            "expected_answer": gt,
            "expected_values": vals,
            "expected_units": "reasoning_thesis",
            "reporting_period": "2024 / FY2025",
            "source_reference": docs,
            "required_tools": ["search_financial_reports_and_knowledge"],
            "expected_calculation": "Analytical financial synthesis",
            "evaluation_rubric": "Sound logic, evidence-supported arguments, and lack of hallucinated claims."
        })

    return queries


def main():
    bench_dir = Path("data/benchmark")
    bench_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save Realtime Snapshot
    snap_path = bench_dir / "realtime_snapshot_20241030.json"
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(SNAPSHOT_DATA, f, indent=2, ensure_ascii=False)
    print(f"Saved realtime snapshot to: {snap_path}")

    # 2. Generate and Save 150 Queries
    queries = build_150_queries()
    bench_path = bench_dir / "benchmark_150_queries.json"
    with open(bench_path, "w", encoding="utf-8") as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {len(queries)} queries to: {bench_path}")

    # Print Category Breakdown
    cat_counts = {}
    diff_counts = {}
    for q in queries:
        cat_counts[q["category"]] = cat_counts.get(q["category"], 0) + 1
        diff_counts[q["difficulty"]] = diff_counts.get(q["difficulty"], 0) + 1

    print("\n--- CATEGORY BREAKDOWN ---")
    for cat, count in cat_counts.items():
        print(f"  {cat}: {count} queries ({count/len(queries)*100:.1f}%)")

    print("\n--- DIFFICULTY BREAKDOWN ---")
    for diff, count in diff_counts.items():
        print(f"  {diff}: {count} queries ({count/len(queries)*100:.1f}%)")


if __name__ == "__main__":
    main()
