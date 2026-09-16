"""
RAGAS Industry-Standard Evaluation Benchmark
Runs RAGAS / LLM-as-a-Judge evaluation on real financial stock data
"""
import sys
import json
import time
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent import RAGPipeline, RAGEvaluator
from src.utils import logger


def run_benchmark():
    print("=" * 70)
    print("  RUNNING INDUSTRY-STANDARD RAGAS BENCHMARK EVALUATION")
    print("=" * 70)

    # 1. Initialize RAG Pipeline and Evaluator
    logger.info("Initializing RAG pipeline agent...")
    pipeline = RAGPipeline()
    pipeline.index()

    logger.info("Initializing RAGAS LLM-as-a-Judge Evaluator...")
    evaluator = RAGEvaluator(use_llm_judge=True)

    # 2. Define Golden Standard Benchmark Dataset (Real Financial QA)
    benchmark_dataset = [
        {
            "id": 1,
            "query": "What was FPT's net revenue in Q3 2024 and how much did it grow YoY?",
            "ground_truth": "FPT reported Q3 2024 consolidated net revenue of 14,510 billion VND, representing an 18.4% growth year-over-year.",
            "relevant_docs": ["fpt_2024_consolidated_financial_report.pdf"],
        },
        {
            "id": 2,
            "query": "What was NVIDIA's Data Center revenue in Q3 FY2025 and how much did it grow?",
            "ground_truth": "NVIDIA Data Center revenue reached $30.77 billion in Q3 FY2025, up 112% from a year ago.",
            "relevant_docs": ["nvidia_q3_fy2025_official_results.docx"],
        },
        {
            "id": 3,
            "query": "What is the formula for Discounted Cash Flow (DCF) Enterprise Value in the CFA framework?",
            "ground_truth": "Enterprise Value (EV) is the sum of FCFF_t / (1 + WACC)^t for t=1 to N, plus Terminal Value / (1 + WACC)^N.",
            "relevant_docs": ["cfa_equity_research_and_valuation_framework.md"],
        },
        {
            "id": 4,
            "query": "What are the P/E ratio and ROE of Vinamilk (VNM) according to the VN30 valuation matrix?",
            "ground_truth": "Vinamilk (VNM) has a TTM P/E of 16.5x and an ROE of 24.1%.",
            "relevant_docs": ["vinamilk_vn30_financial_model_2024.xlsx"],
        },
        {
            "id": 5,
            "query": "What is a Golden Cross in technical analysis?",
            "ground_truth": "A Golden Cross is a technical signal where the 50-day Simple Moving Average (SMA) crosses above the 200-day SMA, confirming a bullish trend.",
            "relevant_docs": ["cfa_equity_research_and_valuation_framework.md"],
        },
    ]

    results_detail = []

    print("\n--- Running Evaluation over Benchmark Questions ---\n")

    for item in benchmark_dataset:
        print(f"[Q{item['id']}] {item['query']}")
        
        # Step A: Retrieve docs
        retrieved_docs = pipeline.retrieve(item["query"])
        retrieved_doc_names = [d.metadata.get("source", "") for d in retrieved_docs]
        context_str = "\n\n".join([d.page_content for d in retrieved_docs])
        
        # Step B: Generate Answer
        start_time = time.time()
        answer = pipeline.query(item["query"])
        latency = round(time.time() - start_time, 2)
        
        # Step C: Evaluate via RAGAS / LLM-as-a-Judge
        eval_res = evaluator.evaluate(
            query=item["query"],
            answer=answer,
            context=context_str,
            retrieved_docs=retrieved_doc_names,
            relevant_docs=item["relevant_docs"],
            ground_truth=item["ground_truth"],
            k=5,
        )
        
        item_summary = {
            "id": item["id"],
            "query": item["query"],
            "answer": answer,
            "ground_truth": item["ground_truth"],
            "latency_sec": latency,
            "eval_result": eval_res,
        }
        results_detail.append(item_summary)
        
        # Print mini summary
        word_eval = eval_res.get("generation_word", {})
        llm_eval = eval_res.get("generation_llm", {})
        
        print(f"  -> Answer ({len(answer)} chars): {answer[:120]}...")
        if llm_eval:
            print(f"  -> Faithfulness (RAGAS): {llm_eval.get('faithfulness', {}).get('score', 0.0):.2f}")
            print(f"  -> Relevancy (RAGAS):    {llm_eval.get('answer_relevancy', {}).get('score', 0.0):.2f}")
        else:
            print(f"  -> Faithfulness (Word):  {word_eval.get('faithfulness', 0.0):.2%}")
        print(f"  -> Overall Score:       {eval_res.get('overall_score', 0.0):.4f}\n")

    # 3. Print Aggregate Summary Metrics
    summary = evaluator.get_summary()
    print("\n" + "=" * 60)
    print("  RAGAS BENCHMARK AGGREGATE SUMMARY METRICS")
    print("=" * 60)
    print(f"  Total Benchmark Queries: {summary.total_queries}")
    print(f"  Faithfulness (LLM-as-Judge): {summary.faithfulness_llm:.2%}")
    print(f"  Answer Relevancy (LLM-as-Judge): {summary.relevancy_llm:.2%}")
    print(f"  Hallucination Rate: {summary.hallucination_rate:.2%}")
    print("=" * 60)

    # 4. Save Benchmark Output Report
    output_path = Path("data/ragas_benchmark_report.json")
    report_data = {
        "metrics_summary": evaluator.get_summary().to_dict(),
        "query_details": results_detail,
    }
    output_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    print(f"\nSaved benchmark report to: {output_path.resolve()}\n")


if __name__ == "__main__":
    run_benchmark()
