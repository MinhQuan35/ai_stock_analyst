"""
FastAPI Backend for RAG Stock Analyst (Forwarder to src.api.routes)
"""
from src.api.routes import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.routes:app", host="0.0.0.0", port=8000, reload=True)
