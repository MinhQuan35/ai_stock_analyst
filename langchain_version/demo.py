"""
LangChain Demo - Test the refactored version
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_version.agent import chat, rag_chat
from langchain_version.metrics import LangChainMetrics


def main():
    print("=" * 60)
    print("  AI STOCK ANALYST - LangChain Version")
    print("=" * 60)
    
    metrics_tracker = LangChainMetrics()
    
    # Test 1: Simple chat
    print("\n[Test 1] Simple Chat with Tools")
    result, m1 = metrics_tracker.track(
        chat,
        "Analyze VNM: price 75000, EPS 4200, dividend 3000",
    )
    print(f"\nResponse: {result['response'][:300]}...")
    print(f"Cost: ${m1['cost_usd']:.6f} | Tokens: {m1['total_tokens']}")
    
    # Test 2: Compound interest
    print("\n[Test 2] Compound Interest Calculation")
    result, m2 = metrics_tracker.track(
        chat,
        "If I invest 100 million VND at 8% per year for 10 years, what do I get?",
    )
    print(f"\nResponse: {result['response'][:300]}...")
    print(f"Cost: ${m2['cost_usd']:.6f} | Tokens: {m2['total_tokens']}")
    
    # Test 3: RSI
    print("\n[Test 3] RSI Calculation")
    prices = [42000, 42500, 43000, 42800, 43200, 43500, 44000, 43800, 44200, 44500,
              44800, 45000, 45200, 45500, 45800]
    result, m3 = metrics_tracker.track(
        chat,
        f"Calculate RSI for this price series: {prices}",
    )
    print(f"\nResponse: {result['response'][:300]}...")
    print(f"Cost: ${m3['cost_usd']:.6f} | Tokens: {m3['total_tokens']}")
    
    # Test 4: RAG
    print("\n[Test 4] RAG Knowledge Base")
    result, m4 = metrics_tracker.track(
        rag_chat,
        "What is RSI and how to interpret it?",
    )
    print(f"\nResponse: {result['response'][:300]}...")
    print(f"Sources: {result['sources']}")
    print(f"Cost: ${m4['cost_usd']:.6f} | Tokens: {m4['total_tokens']}")
    
    # Summary
    print("\n")
    metrics_tracker.print_summary()


if __name__ == "__main__":
    main()
