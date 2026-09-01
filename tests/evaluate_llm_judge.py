"""
Test RAG metrics with LLM-as-Judge (RAGAS-style)
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag.evaluation import RAGEvaluator
from src.rag.crawlers import NewsCrawler
from src.utils import logger


# Test cases based on crawled articles
TEST_CASES = [
    {
        "query": "What is Vinamilk's revenue growth in Q3 2024?",
        "relevant_doc_titles": ["VNM Report Q3 2024: Revenue Growth 8%"],
        "ground_truth": "Vinamilk Q3 2024 revenue grew 8% YoY to VND 16,200 billion, with net profit up 12% to VND 2,750 billion.",
        "answer": "Vinamilk's Q3 2024 revenue grew 8% year-over-year to VND 16,200 billion. Net profit increased 12% to VND 2,750 billion. EPS reached VND 4,200.",
    },
    {
        "query": "How is FPT's AI services performing?",
        "relevant_doc_titles": ["FPT Report: AI Services Drive Growth"],
        "ground_truth": "FPT's AI services revenue grew 85% YoY to VND 1,200 billion.",
        "answer": "FPT's AI services revenue grew 85% YoY, reaching VND 1,200 billion, making it a major growth driver.",
    },
    {
        "query": "What is Apple iPhone revenue?",
        "relevant_doc_titles": ["Apple Q4 2024: iPhone Sales Strong"],
        "ground_truth": "Apple iPhone revenue was $46.2 billion in Q4 2024, up 5% YoY.",
        "answer": "Apple's iPhone revenue for Q4 2024 was $46.2 billion, representing a 5% year-over-year increase.",
    },
    {
        "query": "What is Nvidia data center growth?",
        "relevant_doc_titles": ["Nvidia Q3 2024: AI Chip Demand Soars"],
        "ground_truth": "Nvidia data center revenue grew 112% YoY to $30.8 billion.",
        "answer": "Nvidia's data center revenue experienced 112% year-over-year growth, reaching $30.8 billion in Q3.",
    },
    {
        "query": "How is Vietcombank performing?",
        "relevant_doc_titles": ["VCB Q3 2024: Credit Growth Strong"],
        "ground_truth": "VCB reported 15% net profit growth, ROE of 22.5%, and credit growth of 11.2% YTD.",
        "answer": "Vietcombank (VCB) reported strong Q3 2024 results with 15% net profit growth, ROE of 22.5%, credit growth of 11.2% YTD, and NPL ratio of only 0.95%.",
    },
]


def main():
    print("=" * 60)
    print("  RAG METRICS TEST - LLM-as-Judge (RAGAS-style)")
    print("=" * 60)
    
    # Load articles
    print("\n[1] Loading crawled articles...")
    crawler = NewsCrawler()
    articles = crawler.load_sample_articles()
    print(f"  Loaded {len(articles)} articles")
    
    # Initialize evaluator with LLM Judge
    print("\n[2] Initializing evaluator with LLM Judge...")
    evaluator = RAGEvaluator(use_llm_judge=True)
    
    # Run evaluation
    print("\n[3] Running evaluation on test cases...")
    print(f"  Total test cases: {len(TEST_CASES)}")
    
    for i, test in enumerate(TEST_CASES, 1):
        # Get relevant doc content
        relevant_content = None
        for article in articles:
            if article["title"] == test["relevant_doc_titles"][0]:
                relevant_content = article["content"]
                break
        
        # Simulate context (use relevant doc)
        context = relevant_content or "No context"
        
        # Evaluate
        result = evaluator.evaluate(
            query=test["query"],
            answer=test["answer"],
            context=context,
            retrieved_docs=[context],
            relevant_docs=[context],
            ground_truth=test["ground_truth"],
            k=1,
        )
        
        print(f"\n  Test {i}: {test['query'][:50]}...")
        print(f"    Word - Faithfulness: {result['generation_word']['faithfulness']:.2%}")
        print(f"    Word - Relevancy:    {result['generation_word']['relevancy']:.2%}")
        if 'generation_llm' in result:
            print(f"    LLM  - Faithfulness: {result['generation_llm']['faithfulness']['score']:.2%}")
            print(f"    LLM  - Relevancy:    {result['generation_llm']['answer_relevancy']['score']:.2%}")
            print(f"    LLM  - Correctness:  {result['generation_llm'].get('correctness', {}).get('score', 0):.2%}")
    
    # Print final summary
    print("\n[4] Final Results:")
    evaluator.print_summary()
    
    # Save report
    print("\n[5] Saving report...")
    report = evaluator.get_summary().to_dict()
    
    report_path = Path("data/crawled/llm_judge_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved to: {report_path}")
    print("\n" + "=" * 60)
    print("  EVALUATION COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
