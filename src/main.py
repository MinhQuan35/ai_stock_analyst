"""
Main entry point
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag import RAGPipeline
from src.utils import logger
from src.exceptions import RAGError


def main():
    """Run the RAG pipeline."""
    logger.info("=" * 50)
    logger.info("RAG Stock Analyst - Starting")
    logger.info("=" * 50)
    
    try:
        pipeline = RAGPipeline()
        pipeline.index()
        
        logger.info("Ready for queries. Type 'quit' to exit.\n")
        
        while True:
            try:
                query = input("Q: ").strip()
            except EOFError:
                break
            
            if query.lower() in ("quit", "exit", "q"):
                break
            
            if not query:
                continue
            
            try:
                answer = pipeline.query(query)
                print(f"\nA: {answer}\n")
            except RAGError as e:
                logger.error(f"Query failed: {e}")
                print(f"\nError: {e}\n")
    
    except RAGError as e:
        logger.error(f"Pipeline error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
