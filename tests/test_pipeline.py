"""
Test the RAG pipeline
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import RAGPipeline
from src.utils import logger


def main():
    print("=" * 50)
    print("  RAG Stock Analyst - Test")
    print("=" * 50)
    
    pipeline = RAGPipeline()
    
    print("\n[1] Indexing documents...")
    pipeline.index(force_rebuild=True)
    
    print("\n[2] Test retrieval...")
    docs = pipeline.retrieve("What is P/E?")
    print(f"Retrieved {len(docs)} docs")
    for i, doc in enumerate(docs):
        print(f"  Doc {i+1}: {doc.page_content[:100]}...")
    
    print("\n[3] Test queries...")
    queries = [
        "What is P/E ratio?",
        "When is RSI overbought?",
        "Explain RSI with numbers",
    ]
    
    for q in queries:
        print(f"\nQ: {q}")
        answer = pipeline.query(q)
        print(f"A: {answer[:200]}")
    
    print("\n" + "=" * 50)
    print("  TEST COMPLETE!")
    print("=" * 50)


if __name__ == "__main__":
    main()
