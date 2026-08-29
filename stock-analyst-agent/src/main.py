"""
Stock Analyst Agent - Main FastAPI App
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
from dotenv import load_dotenv
_env_path = Path(__file__).parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import app_settings, api_settings
from src.api import chat_router, agents_router, rag_router, metrics_router


app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.app_version,
    description="Multi-Agent Stock Analysis Platform with LangChain",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=api_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")
app.include_router(rag_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": app_settings.app_name,
        "version": app_settings.app_version,
        "docs": "/docs",
        "endpoints": {
            "chat": "/api/v1/chat",
            "agents": "/api/v1/agents",
            "rag": "/api/v1/rag",
            "metrics": "/api/v1/metrics",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=api_settings.host,
        port=api_settings.port,
        reload=app_settings.debug,
    )
