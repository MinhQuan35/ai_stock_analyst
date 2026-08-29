# AI Stock Analyst

> RAG-powered stock analysis platform built with LangChain and Azure OpenAI.

## Project Structure

```
ai_stock_analyst/
└── rag-stock-analyst/       # Main RAG product
    ├── src/
    │   ├── config/          # Settings
    │   ├── exceptions.py    # Custom exceptions
    │   ├── utils/           # Logger
    │   ├── llm/             # LLM factory
    │   └── rag/             # RAG pipeline
    ├── data/
    │   ├── raw/             # Source documents
    │   └── vector_store/    # FAISS index
    ├── tests/               # Tests
    ├── docs/                # Documentation
    ├── .env.example         # Environment template
    ├── .gitignore
    └── README.md
```

## Quick Start

```bash
cd rag-stock-analyst
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

python -m venv .venv
.venv\Scripts\activate
pip install langchain langchain-openai langchain-community faiss-cpu pydantic-settings

python tests/test_pipeline.py
```

## ⚠️ Security

**NEVER commit `.env` to git!** This is configured via `.gitignore`.

If you accidentally commit secrets:
1. Rotate the keys immediately in Azure
2. Use `git filter-branch` or BFG to clean history
3. Force push

## Documentation

See [rag-stock-analyst/README.md](rag-stock-analyst/README.md) for full documentation.
