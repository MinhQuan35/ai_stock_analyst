"""
Main Entry Point for AI Stock Analyst Agent
Usage:
    python main.py cli        # Interactive CLI mode
    python main.py api        # Launch FastAPI server on port 8000
    python main.py eval       # Run evaluation suite
"""
import sys
import argparse
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import RAGPipeline
from src.utils import logger, AppError


def run_cli():
    """Run CLI interactive mode."""
    logger.info("=" * 50)
    logger.info("AI Stock Analyst Agent - Interactive CLI")
    logger.info("=" * 50)
    
    try:
        pipeline = RAGPipeline()
        pipeline.index()
        logger.info("Ready for queries. Type 'quit' or 'q' to exit.\n")
        
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
            except AppError as e:
                logger.error(f"Query failed: {e}")
                print(f"\nError: {e}\n")
    
    except AppError as e:
        logger.error(f"Pipeline error: {e}")
        sys.exit(1)


def run_api(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Run FastAPI web server."""
    import uvicorn
    logger.info(f"Starting FastAPI server on {host}:{port}...")
    uvicorn.run("src.api.routes:app", host=host, port=port, reload=reload)


def main():
    parser = argparse.ArgumentParser(description="AI Stock Analyst Agent Runner")
    parser.add_argument("mode", nargs="?", default="cli", choices=["cli", "api"], help="Execution mode: cli or api")
    parser.add_argument("--host", default="0.0.0.0", help="Host address for API mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for API mode")
    
    args = parser.parse_args()
    
    if args.mode == "api":
        run_api(host=args.host, port=args.port)
    else:
        run_cli()


if __name__ == "__main__":
    main()
