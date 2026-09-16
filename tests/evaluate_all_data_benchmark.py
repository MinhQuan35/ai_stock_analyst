"""
Comprehensive RAG Evaluation Benchmark across ALL raw datasets (33 files: CSV, PDF, DOCX, XLSX, MD).
Runs end-to-end RAG Pipeline retrieval & LLM generation and computes all evaluation metrics.
"""
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import RAGPipeline
from src.agent.evaluation import RAGEvaluator
from src.utils.logger import logger


# Benchmark queries across all raw datasets in data/raw
DATASET_BENCHMARK_QUERIES = [
    {
        "id": 1,
        "dataset": "fpt_2024_consolidated_financial_report.pdf & fpt_income_statement_summary.md",
        "query": "What was FPT's consolidated net revenue and net profit in Q3 2024?",
        "ground_truth": "FPT reported consolidated net revenue of 14,510 billion VND and net profit after tax of 2,246 billion VND in Q3 2024.",
        "relevant_docs": ["fpt_2024_consolidated_financial_report.pdf", "fpt_income_statement_summary.md"],
    },
    {
        "id": 2,
        "dataset": "nvidia_q3_fy2025_official_results.docx",
        "query": "What was NVIDIA's Data Center revenue in Q3 FY2025 and what was the growth rate?",
        "ground_truth": "NVIDIA Data Center revenue reached $30.77 billion in Q3 FY2025, representing 112% growth YoY.",
        "relevant_docs": ["nvidia_q3_fy2025_official_results.docx"],
    },
    {
        "id": 3,
        "dataset": "cfa_equity_research_and_valuation_framework.md",
        "query": "Explain the Discounted Cash Flow (DCF) Enterprise Value valuation formula in the CFA framework.",
        "ground_truth": "Enterprise Value (EV) is calculated as the sum of discounted Free Cash Flow to Firm (FCFF_t / (1 + WACC)^t) plus Terminal Value discounted to present value.",
        "relevant_docs": ["cfa_equity_research_and_valuation_framework.md"],
    },
    {
        "id": 4,
        "dataset": "hpg_income_statement_summary.md & hpg_balance_sheet_quarterly.csv",
        "query": "What is Hoa Phat Group's (HPG) gross margin and steel production trend in 2024?",
        "ground_truth": "Hoa Phat Group (HPG) reported strong crude steel production recovery and improving gross margins around 17-18% in 2024.",
        "relevant_docs": ["hpg_income_statement_summary.md", "hpg_balance_sheet_quarterly.csv"],
    },
    {
        "id": 5,
        "dataset": "vinamilk_vn30_financial_model_2024.xlsx & vnm_income_statement_summary.md",
        "query": "What are the key financial ratios for Vinamilk (VNM) including P/E ratio and ROE in 2024?",
        "ground_truth": "Vinamilk (VNM) maintains a TTM P/E ratio around 16.5x, an ROE of ~24.1%, and strong net margins.",
        "relevant_docs": ["vinamilk_vn30_financial_model_2024.xlsx", "vnm_income_statement_summary.md"],
    },
    {
        "id": 6,
        "dataset": "real_aapl_daily_prices_2024.csv & real_msft_daily_prices_2024.csv",
        "query": "Compare Apple (AAPL) and Microsoft (MSFT) stock price trends and market data in 2024.",
        "ground_truth": "Apple (AAPL) and Microsoft (MSFT) daily stock prices show steady tech sector growth with strong trading volume throughout 2024.",
        "relevant_docs": ["real_aapl_daily_prices_2024.csv", "real_msft_daily_prices_2024.csv"],
    },
    {
        "id": 7,
        "dataset": "vcb_income_statement_summary.md & vcb_balance_sheet_quarterly.csv",
        "query": "What is Vietcombank's (VCB) credit growth, net profit, and NPL ratio?",
        "ground_truth": "Vietcombank (VCB) maintains industry-leading net profit growth, ROE above 20%, and low non-performing loan (NPL) ratio under 1%.",
        "relevant_docs": ["vcb_income_statement_summary.md", "vcb_balance_sheet_quarterly.csv"],
    },
    {
        "id": 8,
        "dataset": "rsi.md & pe_ratio.md",
        "query": "How are Relative Strength Index (RSI) and Price-to-Earnings (P/E) ratio interpreted in stock analysis?",
        "ground_truth": "RSI measures price momentum (overbought above 70, oversold below 30), while P/E ratio measures company valuation relative to per-share earnings.",
        "relevant_docs": ["rsi.md", "pe_ratio.md"],
    },
    {
        "id": 9,
        "dataset": "mwg_income_statement_summary.md & mwg_balance_sheet_quarterly.csv",
        "query": "What is Mobile World Group's (MWG) revenue recovery and store network profitability in 2024?",
        "ground_truth": "Mobile World Group (MWG) showed revenue recovery driven by Bach Hoa Xanh achieving break-even and retail electronics margin expansion.",
        "relevant_docs": ["mwg_income_statement_summary.md", "mwg_balance_sheet_quarterly.csv"],
    },
    {
        "id": 10,
        "dataset": "real_nvda_daily_prices_2024.csv & real_tsla_daily_prices_2024.csv",
        "query": "What were the major price movements for NVIDIA (NVDA) and Tesla (TSLA) in 2024 daily price records?",
        "ground_truth": "NVIDIA (NVDA) experienced exponential price appreciation driven by AI chip demand, while Tesla (TSLA) showed higher volatility around EV margins.",
        "relevant_docs": ["real_nvda_daily_prices_2024.csv", "real_tsla_daily_prices_2024.csv"],
    },
]


def run_comprehensive_benchmark():
    print("=" * 75)
    print("  RUNNING FULL-DATASET RAG BENCHMARK EVALUATION (33 RAW DATA FILES)")
    print("=" * 75)
    
    # Initialize RAG Pipeline
    logger.info("Building / Loading RAG Pipeline Index...")
    pipeline = RAGPipeline()
    pipeline.index(force_rebuild=False)
    
    # Initialize Evaluator with LLM Judge
    evaluator = RAGEvaluator(use_llm_judge=True)
    
    results = []
    latencies = []
    
    print(f"\nEvaluating {len(DATASET_BENCHMARK_QUERIES)} Benchmark Queries across all financial datasets...\n")
    
    for item in DATASET_BENCHMARK_QUERIES:
        query_id = item["id"]
        query = item["query"]
        ground_truth = item["ground_truth"]
        relevant_docs = item["relevant_docs"]
        dataset_source = item["dataset"]
        
        print(f"[Query #{query_id}] ({dataset_source})")
        print(f"  Q: {query}")
        
        # Step 1: Retrieve documents
        t0 = time.time()
        retrieved_docs = pipeline.retrieve(query)
        retrieved_sources = [d.metadata.get("source", "") for d in retrieved_docs]
        context_text = "\n\n".join([d.page_content for d in retrieved_docs])
        
        # Step 2: Generate Answer
        answer = pipeline.query(query)
        latency = round(time.time() - t0, 2)
        latencies.append(latency)
        
        # Step 3: Run Evaluation Metrics
        eval_metrics = evaluator.evaluate(
            query=query,
            answer=answer,
            context=context_text,
            retrieved_docs=retrieved_sources,
            relevant_docs=relevant_docs,
            ground_truth=ground_truth,
            k=5,
        )
        
        print(f"  A: {answer[:130]}...")
        print(f"  -> Latency: {latency}s")
        print(f"  -> Retrieval Precision@5: {eval_metrics['retrieval']['precision']:.2%}")
        print(f"  -> Retrieval Recall@5:    {eval_metrics['retrieval']['recall']:.2%}")
        
        if "generation_llm" in eval_metrics and eval_metrics["generation_llm"]:
            llm_eval = eval_metrics["generation_llm"]
            print(f"  -> LLM Faithfulness:     {llm_eval.get('faithfulness', {}).get('score', 0.0):.2f}")
            print(f"  -> LLM Answer Relevancy: {llm_eval.get('answer_relevancy', {}).get('score', 0.0):.2f}")
            print(f"  -> LLM Correctness:      {llm_eval.get('correctness', {}).get('score', 0.0):.2f}")
        else:
            word_eval = eval_metrics["generation_word"]
            print(f"  -> Faithfulness (Word):  {word_eval.get('faithfulness', 0.0):.2%}")
            print(f"  -> Relevancy (Word):     {word_eval.get('relevancy', 0.0):.2%}")
        
        print("-" * 75)
        
        results.append({
            "id": query_id,
            "dataset": dataset_source,
            "query": query,
            "answer": answer,
            "ground_truth": ground_truth,
            "latency_seconds": latency,
            "metrics": eval_metrics,
        })
    
    # Save Report
    output_file = Path("data/ragas_benchmark_report.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    summary_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_datasets_indexed": 33,
        "total_queries_evaluated": len(DATASET_BENCHMARK_QUERIES),
        "average_latency_seconds": round(sum(latencies) / len(latencies), 2) if latencies else 0,
        "results": results,
    }
    
    output_file.write_text(json.dumps(summary_report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nFull benchmark evaluation report successfully saved to: {output_file.resolve()}")
    print("=" * 75)


if __name__ == "__main__":
    run_comprehensive_benchmark()
