# Stock Analyst Agent

> Multi-Agent Stock Analysis Platform built with LangChain

## Overview

A comprehensive stock analysis platform using multi-agent architecture:
- **4 specialized agents** working together (Triage, Research, Analyst, Reporter)
- **18+ tools** for financial calculations and market data
- **RAG** with FAISS vector store
- **Persistent memory** with SQLite
- **FastAPI** with async support
- **Comprehensive metrics** tracking

## Architecture

```
stock-analyst-agent/
├── src/
│   ├── agents/              # Multi-agent system
│   │   ├── base/           # Base agent class
│   │   ├── specialized/    # Triage, Analyst, Research, Reporter
│   │   └── orchestrator/   # Agent coordinator
│   ├── chains/             # LangChain LCEL chains
│   │   ├── rag/            # RAG chain
│   │   ├── analysis/       # Analysis chain
│   │   └── report/         # Report generation
│   ├── tools/              # 18+ tools
│   │   ├── financial/      # P/E, RSI, SMA, etc.
│   │   ├── market_data/    # Quotes, indices, news
│   │   └── portfolio/      # Portfolio management
│   ├── memory/             # Memory system
│   │   ├── short_term/     # Buffer memory
│   │   ├── long_term/      # Entity memory
│   │   └── persistence/    # SQLite store
│   ├── vector_store/       # RAG components
│   │   ├── stores/         # FAISS
│   │   ├── retrievers/     # Similarity search
│   │   ├── loaders/        # Document loaders
│   │   └── splitters/      # Text splitters
│   ├── llm/                # LLM factory
│   ├── monitoring/         # Metrics & tracing
│   │   ├── metrics/        # Cost, latency, tokens
│   │   └── tracing/        # Span tracking
│   ├── api/                # FastAPI routes
│   │   └── v1/routes/      # chat, agents, rag, metrics
│   ├── config/             # Settings (pydantic)
│   ├── schemas/            # Pydantic models
│   ├── constants/          # Enums
│   ├── exceptions/         # Custom exceptions
│   └── main.py             # FastAPI app
├── data/                    # Knowledge base
├── tests/                   # Tests
├── deploy/                  # Docker, K8s
├── docs/                    # Documentation
├── demo.py                  # Demo script
└── README.md
```

## Quick Start

```bash
# Install dependencies
pip install langchain langchain-openai langchain-community faiss-cpu

# Set environment variables
cp .env.example .env

# Run demo
python demo.py

# Run API server
python -m src.main
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/api/v1/chat/` | Chat (multi-agent) |
| POST | `/api/v1/chat/simple` | Simple chat (analyst only) |
| POST | `/api/v1/agents/invoke` | Invoke specific agent |
| GET | `/api/v1/agents/list` | List agents |
| POST | `/api/v1/rag/evaluate` | Evaluate RAG |
| POST | `/api/v1/rag/build` | Build RAG index |
| POST | `/api/v1/metrics/track` | Track metrics |
| GET | `/api/v1/metrics/` | Get metrics |
| GET | `/api/v1/metrics/pricing` | Get pricing |

## Tools (18+)

### Financial (9)
- calculate_pe_ratio, calculate_pb_ratio
- calculate_dividend_yield, calculate_compound_interest
- calculate_sma, calculate_ema
- calculate_rsi, calculate_macd, calculate_bollinger_bands

### Market Data (5)
- get_stock_quote, get_market_index
- get_company_info, get_historical_prices, search_news

### Portfolio (4)
- get_portfolio, calculate_portfolio_value
- suggest_rebalance, calculate_diversification_score

## Agents

### Triage Agent
Routes queries to the right specialist.

### Research Agent
Gathers market data and news.

### Analyst Agent
Performs technical and fundamental analysis.

### Reporter Agent
Creates comprehensive reports.

## License

MIT
