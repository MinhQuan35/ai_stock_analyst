"""
Comprehensive Evaluation Benchmark Runner across the 150-Query Dataset.
Evaluates:
- 3 Upgraded Metrics: Chunk-level Context Precision, Chunk-level Context Recall, Overall Answer Accuracy (binary 0/1)
- 7 Tier 1 Metrics: Numerical Accuracy, Tool Selection Accuracy, MAP@K, Hit@K, Financial Entities Recall, Tool Success Rate, Fallback Rate
- Plus: Retrieval Recall@5, Precision@5, MRR, Latency, Category-level breakdown.
"""
import sys
import os
import json
import time
import random
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ensure UTF-8 output encoding on Windows console
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from src.agent import RAGPipeline
from src.agent.evaluation import RAGEvaluator
from src.utils.logger import logger


def run_benchmark(limit: int = 150, use_llm_judge: bool = False, category_filter: str = None, rebuild: bool = False):
    print("=" * 80)
    print("  AI STOCK ANALYST AGENT — 150 QUERIES BENCHMARK EVALUATION")
    print("=" * 80)

    benchmark_file = Path("data/benchmark/benchmark_v2.json")
    if not benchmark_file.exists():
        raise FileNotFoundError(
            f"Benchmark file not found: {benchmark_file}. Run: python scripts/build_benchmark.py"
        )

    with open(benchmark_file, "r", encoding="utf-8") as f:
        queries = json.load(f)

    # Freeze market tools to the snapshot so realtime queries are reproducible
    snapshot = Path("data/benchmark/realtime_snapshot_20241030.json")
    if snapshot.exists():
        os.environ["MARKET_DATA_SNAPSHOT"] = str(snapshot.resolve())
        print(f"Market tools pinned to snapshot: {snapshot}")

    if category_filter:
        queries = [q for q in queries if q["category"] == category_filter]
        print(f"Filtered to category: '{category_filter}' ({len(queries)} queries)")

    if limit and limit < len(queries):
        queries = queries[:limit]
        print(f"Running limited set of {limit} queries for quick validation.")

    total_queries = len(queries)
    print(f"Total benchmark queries to evaluate: {total_queries}\n")

    # 1. Initialize RAG Pipeline
    logger.info("Initializing Financial RAG & Tool Agent Pipeline...")
    pipeline = RAGPipeline()
    pipeline.index(force_rebuild=rebuild)

    # 2. Initialize Evaluator
    evaluator = RAGEvaluator(use_llm_judge=use_llm_judge)

    results = []
    latencies = []
    category_stats = {}

    start_total_time = time.time()

    for idx, item in enumerate(queries, 1):
        qid = item["query_id"]
        cat = item["category"]
        subcat = item["subcategory"]
        diff = item["difficulty"]
        query = item["query"]
        ground_truth = item.get("expected_answer", "")
        expected_values = item.get("expected_values", [])
        expected_tools = item.get("required_tools", [])
        relevant_docs = (item.get("source_reference", [])
                         if "search_financial_reports_and_knowledge" in item.get("required_tools", [])
                         else [])

        print(f"[{idx}/{total_queries}] ({qid}) [{diff.upper()}] [{cat}]")
        print(f"  Q: {query}")

        t0 = time.time()

        # Step 1: Agent Execution with Trajectory
        try:
            exec_res = pipeline.query_with_details(query)
            answer = exec_res.get("answer", "")
            actual_tools = exec_res.get("tools_called", [])
            tool_calls_detail = exec_res.get("tool_calls_detail", [])
            fallback_triggered = exec_res.get("fallback_triggered", False)
        except Exception as e:
            logger.error(f"Error querying pipeline: {e}")
            answer = f"Agent execution error: {e}"
            actual_tools = []
            tool_calls_detail = []
            fallback_triggered = True

        latency = time.time() - t0
        latencies.append(latency)

        # Step 2: Retrieval Context (only for queries expected to use the RAG tool)
        retrieved_docs = []
        context_text = ""
        if "search_financial_reports_and_knowledge" in expected_tools:
            try:
                docs = pipeline.retrieve(query)
                retrieved_docs = [d.metadata.get("source", "") for d in docs]
                context_text = "\n\n".join([d.page_content for d in docs])
            except Exception:
                pass

        # Step 3: Compute Comprehensive Metrics
        metrics = evaluator.evaluate(
            query=query,
            answer=answer,
            context=context_text,
            retrieved_docs=retrieved_docs,
            relevant_docs=relevant_docs,
            ground_truth=ground_truth,
            expected_values=expected_values,
            expected_tools=expected_tools,
            actual_tools=actual_tools,
            tool_calls_detail=tool_calls_detail,
            fallback_triggered=fallback_triggered,
            k=5,
        )

        fin_acc = metrics["financial_accuracy"]
        agent_t = metrics["agent_tools"]
        ret_m = metrics["retrieval"]
        ctx_m = metrics["context_chunk_level"]

        print(f"  A: {answer[:110]}...")
        print(f"  -> Tools: {actual_tools} (Expected: {expected_tools})")

        def pct(value):
            return "n/a" if value is None else f"{value:.1%}"

        print(f"  -> Numerical Acc: {pct(fin_acc['numerical_accuracy'])} | Entities Recall: {pct(fin_acc['entities_recall'])} | Overall Acc: {fin_acc['overall_answer_accuracy']}")
        print(f"  -> Tool Sel Acc: {pct(agent_t['tool_selection_accuracy'])} | Tool Succ Rate: {pct(agent_t['tool_success_rate'])} | Latency: {latency}s")
        print("-" * 80)

        # Track Category Stats
        if cat not in category_stats:
            category_stats[cat] = {
                "count": 0,
                "overall": [],
                "numeric": [],
                "tool_sel": [],
                "entities": [],
                "latency": [],
            }
        cs = category_stats[cat]
        cs["count"] += 1
        cs["overall"].append(fin_acc["overall_answer_accuracy"])
        cs["numeric"].append(fin_acc["numerical_accuracy"])
        cs["tool_sel"].append(agent_t["tool_selection_accuracy"])
        cs["entities"].append(fin_acc["entities_recall"])
        cs["latency"].append(latency)

        results.append({
            "query_id": qid,
            "category": cat,
            "subcategory": subcat,
            "difficulty": diff,
            "query": query,
            "answer": answer,
            "ground_truth": ground_truth,
            "latency_seconds": latency,
            "metrics": metrics,
        })

    total_duration = time.time() - start_total_time

    # ---- Aggregation: None means "no signal for this query" and is excluded ----
    def mean(values):
        vals = [v for v in values if v is not None]
        return (sum(vals) / len(vals)) if vals else None

    def fmt(value, pct=True):
        if value is None:
            return "n/a"
        return f"{value:.2%}" if pct else f"{value:.4f}"

    def bootstrap_ci(values, n=1000):
        vals = [v for v in values if v is not None]
        if len(vals) < 2:
            return None
        rng = random.Random(42)
        means = sorted(sum(rng.choice(vals) for _ in vals) / len(vals) for _ in range(n))
        return means[int(0.025 * n)], means[int(0.975 * n)]

    overall_values = [r["metrics"]["financial_accuracy"]["overall_answer_accuracy"] for r in results]
    num_values = [r["metrics"]["financial_accuracy"]["numerical_accuracy"] for r in results]
    entities_values = [r["metrics"]["financial_accuracy"]["entities_recall"] for r in results]
    tool_sel_values = [r["metrics"]["agent_tools"]["tool_selection_accuracy"] for r in results]
    tool_succ_values = [r["metrics"]["agent_tools"]["tool_success_rate"] for r in results]
    fallback_values = [r["metrics"]["agent_tools"]["fallback_rate"] for r in results]

    # Retrieval metrics only apply to queries that require the RAG tool (defined a priori)
    ret_queries = [r for r, item in zip(results, queries)
                   if "search_financial_reports_and_knowledge" in item.get("required_tools", [])]
    retrieval = {
        "precision@5": mean([r["metrics"]["retrieval"]["precision"] for r in ret_queries]),
        "doc_precision@5": mean([r["metrics"]["retrieval"]["doc_precision"] for r in ret_queries]),
        "recall@5": mean([r["metrics"]["retrieval"]["recall"] for r in ret_queries]),
        "mrr": mean([r["metrics"]["retrieval"]["mrr"] for r in ret_queries]),
        "map@5": mean([r["metrics"]["retrieval"]["map_at_k"] for r in ret_queries]),
        "hit@5": mean([r["metrics"]["retrieval"]["hit@5"] for r in ret_queries]),
        "ndcg@5": mean([r["metrics"]["retrieval"]["ndcg"] for r in ret_queries]),
        "context_precision": mean([r["metrics"]["context_chunk_level"]["precision"] for r in ret_queries]),
        "context_recall": mean([r["metrics"]["context_chunk_level"]["recall"] for r in ret_queries]),
    }

    overall_ci = bootstrap_ci(overall_values)

    print("\n" + "=" * 80)
    print("                    BENCHMARK SCOREBOARD & METRICS REPORT")
    print("=" * 80)
    print(f"Total Evaluated Queries: {len(results)} | Execution Time: {total_duration:.2f}s "
          f"| Avg Latency: {sum(latencies)/len(latencies):.4f}s")
    print("-" * 80)
    print(" [GENERATION / ANSWER]")
    print(f"  • Overall Answer Accuracy (binary) : {fmt(mean(overall_values))}"
          f"   (n={sum(1 for v in overall_values if v is not None)}"
          + (f", 95% CI {fmt(overall_ci[0])}–{fmt(overall_ci[1])}" if overall_ci else "") + ")")
    print(f"  • Numerical Accuracy               : {fmt(mean(num_values))}"
          f"   (n={sum(1 for v in num_values if v is not None)})")
    print(f"  • Financial Entities Recall        : {fmt(mean(entities_values))}"
          f"   (n={sum(1 for v in entities_values if v is not None)})")
    print("\n [AGENT / TOOLS]")
    print(f"  • Tool Selection Accuracy          : {fmt(mean(tool_sel_values))}")
    print(f"  • Tool Execution Success Rate      : {fmt(mean(tool_succ_values))}"
          f"   (n={sum(1 for v in tool_succ_values if v is not None)})")
    print(f"  • Fallback Rate                    : {fmt(mean(fallback_values))}")
    print(f"\n [RETRIEVAL] (n={len(ret_queries)} queries requiring RAG tool)")
    for key, value in retrieval.items():
        print(f"  • {key:<19} : {fmt(value)}")
    print("-" * 80)
    print("\n [PER-CATEGORY BREAKDOWN]")
    print(f"{'Category':<32} | {'Queries':<7} | {'Overall':<9} | {'Numeric':<9} | {'Tool Sel':<9} | {'Latency'}")
    print("-" * 85)
    category_summary = {}
    for cat, cs in category_stats.items():
        n = cs["count"]
        cat_overall = mean(cs["overall"])
        cat_num = mean(cs["numeric"])
        cat_tool = mean(cs["tool_sel"])
        cat_lat = mean(cs["latency"])
        category_summary[cat] = {
            "count": n,
            "overall_accuracy": cat_overall,
            "numerical_accuracy": cat_num,
            "tool_selection_accuracy": cat_tool,
            "average_latency": cat_lat,
        }
        print(f"{cat:<32} | {n:<7} | {fmt(cat_overall):<9} | {fmt(cat_num):<9} | {fmt(cat_tool):<9} | {cat_lat:.4f}s")
    print("=" * 85)

    # Save Report
    output_path = Path("data/benchmark/benchmark_150_report.json")
    summary_report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "benchmark_file": str(benchmark_file),
        "total_queries_evaluated": len(results),
        "total_duration_seconds": total_duration,
        "average_latency_seconds": (sum(latencies) / len(latencies)) if latencies else 0.0,
        "metrics_summary": {
            "overall_answer_accuracy": mean(overall_values),
            "overall_answer_accuracy_ci95": overall_ci,
            "overall_answer_accuracy_n": sum(1 for v in overall_values if v is not None),
            "numerical_accuracy": mean(num_values),
            "numerical_accuracy_n": sum(1 for v in num_values if v is not None),
            "entities_recall": mean(entities_values),
            "tool_selection_accuracy": mean(tool_sel_values),
            "tool_execution_success_rate": mean(tool_succ_values),
            "fallback_rate": mean(fallback_values),
            **retrieval,
            "retrieval_queries_n": len(ret_queries),
        },
        "category_breakdown": category_summary,
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    print(f"\nSaved full evaluation report to: {output_path.resolve()}\n")
    return summary_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run 150-query Benchmark Evaluation")
    parser.add_argument("--limit", type=int, default=150, help="Number of queries to evaluate (default: 150)")
    parser.add_argument("--category", type=str, default=None, help="Filter to specific category")
    parser.add_argument("--llm-judge", action="store_true", help="Enable LLM Judge evaluation")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of the vector index")
    args = parser.parse_args()

    run_benchmark(limit=args.limit, use_llm_judge=args.llm_judge,
                  category_filter=args.category, rebuild=args.rebuild)
