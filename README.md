# RinggitSense

[![CI](https://github.com/FaisalHanafi98/RinggitSense/actions/workflows/ci.yml/badge.svg)](https://github.com/FaisalHanafi98/RinggitSense/actions/workflows/ci.yml)

AI-powered Malaysian personal finance tracker that unifies bank statements, e-wallets, and three-tier debt tracking (Formal, BNPL, Hutang).

## Tech Stack

- **Backend**: Python 3.11 / FastAPI / SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15 with pgvector
- **Cache**: Redis 7
- **AI**: Claude Sonnet 4 (6-agent pipeline)
- **Auth**: Clerk JWT

## Quick Start

```bash
# Start infrastructure
cd backend
docker-compose up -d

# Install dependencies
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt -r requirements-dev.txt

# Copy environment config
cp .env.example .env

# Run the API
uvicorn src.main:app --reload --port 8000
```

## Development

```bash
# Lint
ruff check backend/

# Type check
mypy backend/src/

# Test with coverage
cd backend && pytest tests/ --cov=src --cov-report=term-missing
```

## Project Status

Phase 1: Foundation (in progress)
