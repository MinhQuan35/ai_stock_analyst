# RAG Stock Analyst

> A clean, production-ready RAG (Retrieval-Augmented Generation) pipeline for stock analysis.

## Overview

A simple but production-quality RAG implementation with:
- **Document loading** from local files (.md, .txt)
- **Text chunking** with configurable size/overlap
- **Embeddings** via Azure OpenAI
- **FAISS vector store** with persistence
- **LCEL chains** for clean composition
- **Async support** built-in
- **Clean architecture** with proper separation of concerns

## Project Structure

```
rag-stock-analyst/
├── src/
│   ├── config/              # Settings (Pydantic)
│   ├── exceptions.py        # Custom exceptions
│   ├── utils/               # Logger
│   ├── llm/                 # LLM factory
│   └── rag/                 # RAG modules
│       ├── loaders/         # Document loaders
│       ├── splitters/       # Text splitters
│       ├── stores/          # Vector stores
│       ├── retrievers/      # Retrievers
│       ├── chains/          # LCEL chains
│       └── rag_pipeline.py  # End-to-end pipeline
├── data/
│   ├── raw/                 # Source documents
│   └── vector_store/        # FAISS index
├── tests/                    # Tests
├── docs/                     # Documentation
├── .env.example              # Environment template
├── .gitignore
└── README.md
```

## Quick Start

### 1. Setup

```bash
# Clone
git clone https://github.com/MinhQuan35/ai_stock_analyst.git
cd ai_stock_analyst/rag-stock-analyst

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install langchain langchain-openai langchain-community faiss-cpu pydantic-settings
```

### 2. Configure

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
# NEVER commit .env to git!
```

### 3. Add Documents

Place your `.md` or `.txt` files in `data/raw/`

### 4. Run

```bash
# Interactive mode
python -m src.main

# Run tests
python tests/test_pipeline.py
```

## Usage

### As a Library

```python
from src.rag import RAGPipeline

# Create and index
pipeline = RAGPipeline()
pipeline.index()

# Query
answer = pipeline.query("What is P/E ratio?")
print(answer)

# Async query
import asyncio
answer = asyncio.run(pipeline.aquery("What is RSI?"))
```

### With Custom Settings

```python
from src.rag import RAGPipeline

# Custom data directory
pipeline = RAGPipeline(data_dir="/path/to/your/docs")
pipeline.index(force_rebuild=True)
```

## How It Works

### RAG Pipeline

```
Documents (.md, .txt)
    ↓ [1] LOAD
Document objects
    ↓ [2] SPLIT
Chunks (500 chars each)
    ↓ [3] EMBED
Vectors (3072 dims)
    ↓ [4] STORE
FAISS Index
    ↓ [5] QUERY
Top K relevant chunks
    ↓ [6] AUGMENT
Context + Question
    ↓ [7] GENERATE
LLM Answer
```

### Code Example

```python
# 1. Load documents
loader = DirectoryLoader("data/raw")
documents = loader.load()

# 2. Split into chunks
splitter = RecursiveTextSplitter(chunk_size=500)
chunks = splitter.split(documents)

# 3. Create embeddings and store
from src.llm import get_embeddings_model
embeddings = get_embeddings_model()
store = FAISSStore(embeddings)
store.create_from_documents(chunks)
store.save("my_index")

# 4. Create retriever
retriever = SimilarityRetriever(store, k=3)

# 5. Create RAG chain
chain = RAGChain(retriever)

# 6. Query
answer = chain.query("Your question here")
```

## Configuration

All settings in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_OPENAI_API_KEY` | - | Your Azure OpenAI key |
| `AZURE_OPENAI_ENDPOINT` | - | Azure endpoint URL |
| `AZURE_OPENAI_API_VERSION` | `2024-10-21` | API version |
| `AZURE_CHAT_DEPLOYMENT` | `gpt-4o` | Chat model deployment |
| `AZURE_EMBEDDING_DEPLOYMENT` | `text-embedding-3-large` | Embedding model |
| `RAG_CHUNK_SIZE` | `500` | Characters per chunk |
| `RAG_CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `RAG_TOP_K` | `5` | Number of results to retrieve |

## Architecture

### Clean Architecture Principles

- **Separation of concerns**: Each module has one responsibility
- **Dependency injection**: Components are injected, not hardcoded
- **Configuration externalized**: All settings in `.env`
- **Error handling**: Custom exceptions for each layer
- **Logging**: Structured logging throughout
- **Async-ready**: Both sync and async APIs

### Module Dependencies

```
src/main.py
    └── src/rag/rag_pipeline.py
            ├── src/rag/loaders/
            ├── src/rag/splitters/
            ├── src/rag/stores/  → uses src/llm
            ├── src/rag/retrievers/
            └── src/rag/chains/  → uses src/llm
```

## License

MIT
