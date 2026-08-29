"""
FastAPI Backend for RAG Stock Analyst
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from src.rag import RAGPipeline
from src.rag.evaluation import RAGEvaluator
from src.utils import logger


app = FastAPI(
    title="RAG Stock Analyst API",
    version="2.0.0",
    description="RAG pipeline with Azure OpenAI, Qdrant, Cohere Rerank",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pipeline (initialized on startup)
pipeline: Optional[RAGPipeline] = None
evaluator = RAGEvaluator()


# ============== MODELS ==============

class ChatRequest(BaseModel):
    message: str
    use_reranker: bool = True


class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []


class IndexRequest(BaseModel):
    force_rebuild: bool = False


class EvalRequest(BaseModel):
    query: str
    answer: str
    context: str
    retrieved_docs: List[str]
    relevant_docs: List[str]
    ground_truth: Optional[str] = None
    expected_context: Optional[str] = None
    k: int = 5


# ============== STARTUP / SHUTDOWN ==============

@app.on_event("startup")
async def startup():
    """Initialize pipeline on startup."""
    global pipeline
    try:
        logger.info("Initializing RAG pipeline...")
        pipeline = RAGPipeline()
        pipeline.index()
        logger.info("RAG pipeline ready")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        pipeline = None


# ============== ROUTES ==============

@app.get("/")
async def root():
    """API info."""
    return {
        "name": "RAG Stock Analyst API",
        "version": "2.0.0",
        "status": "ready" if pipeline else "not_initialized",
        "endpoints": {
            "chat": "POST /api/chat",
            "index": "POST /api/index",
            "search": "POST /api/search",
            "evaluate": "POST /api/evaluate",
            "metrics": "GET /api/metrics",
            "health": "GET /api/health",
        }
    }


@app.get("/api/health")
async def health():
    """Health check."""
    return {
        "status": "healthy" if pipeline else "not_ready",
        "pipeline_initialized": pipeline is not None,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with RAG."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        response = pipeline.query(request.message)
        return ChatResponse(
            response=response,
            sources=["RAG pipeline"],
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search", response_model=ChatResponse)
async def search(request: ChatRequest):
    """Search without LLM generation."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        docs = pipeline.retrieve(request.message)
        context = "\n\n---\n\n".join([doc.page_content for doc in docs])
        return ChatResponse(
            response=context if context else "No results",
            sources=[doc.metadata.get("source", "unknown") for doc in docs],
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/index")
async def index(request: IndexRequest):
    """Build/rebuild index."""
    global pipeline
    try:
        pipeline = RAGPipeline()
        pipeline.index(force_rebuild=request.force_rebuild)
        return {"message": "Index built", "force_rebuild": request.force_rebuild}
    except Exception as e:
        logger.error(f"Index error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate")
async def evaluate(request: EvalRequest):
    """Evaluate a RAG query."""
    try:
        result = evaluator.evaluate(
            query=request.query,
            answer=request.answer,
            context=request.context,
            retrieved_docs=request.retrieved_docs,
            relevant_docs=request.relevant_docs,
            ground_truth=request.ground_truth,
            expected_context=request.expected_context,
            k=request.k,
        )
        return result
    except Exception as e:
        logger.error(f"Evaluate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics")
async def metrics():
    """Get RAG metrics summary."""
    return evaluator.get_summary().to_dict()


@app.post("/api/metrics/reset")
async def reset_metrics():
    """Reset RAG metrics."""
    evaluator.reset()
    return {"message": "Metrics reset"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
