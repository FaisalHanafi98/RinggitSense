# RinggitSense System Architecture

> Technical architecture for the AI-powered Malaysian personal finance platform

**Version**: 1.0.0
**Last Updated**: 2026-01-10
**Status**: Approved

---

## Architecture Overview

RinggitSense follows a **layered architecture** with clear separation between presentation, API, business logic, AI agents, and data persistence layers.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                 │
│                                                                              │
│    ┌──────────────────────────────────────────────────────────────────┐    │
│    │                    React 18 + TypeScript                          │    │
│    │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │    │
│    │  │ Dashboard  │ │Transactions│ │   Debts    │ │   Chat     │    │    │
│    │  │   View     │ │   List     │ │  Tracker   │ │ Interface  │    │    │
│    │  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │    │
│    └──────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS / REST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│                                                                              │
│    ┌──────────────────────────────────────────────────────────────────┐    │
│    │                    FastAPI (Python 3.11+)                         │    │
│    │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐    │    │
│    │  │  /upload   │ │   /query   │ │  /agents   │ │   /auth    │    │    │
│    │  │   POST     │ │   POST     │ │   GET/POST │ │   POST     │    │    │
│    │  └────────────┘ └────────────┘ └────────────┘ └────────────┘    │    │
│    └──────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                                 │
│                                                                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│  │  Statement      │ │   Transaction   │ │    Agent        │               │
│  │  Parser         │ │   Service       │ │  Orchestrator   │               │
│  │                 │ │                 │ │                 │               │
│  │  - Maybank      │ │  - CRUD ops     │ │  - Routing      │               │
│  │  - CIMB         │ │  - Filtering    │ │  - Delegation   │               │
│  │  - RHB          │ │  - Aggregation  │ │  - Caching      │               │
│  │  - TnG          │ │                 │ │                 │               │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AI AGENT LAYER                                    │
│                                                                              │
│    ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│    │ AG-01   │ │ AG-02   │ │ AG-03   │ │ AG-04   │ │ AG-05   │ │ AG-06   ││
│    │Category │ │  Debt   │ │ Pattern │ │Predictor│ │  Query  │ │ Advisor ││
│    │  izer   │ │Detector │ │Analyzer │ │         │ │  Agent  │ │         ││
│    └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘│
│                                                                              │
│    ┌──────────────────────────────────────────────────────────────────┐    │
│    │                    Claude API (Sonnet 4)                          │    │
│    └──────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA PERSISTENCE LAYER                              │
│                                                                              │
│    ┌──────────────────────────────────────────────────────────────────┐    │
│    │                     PostgreSQL 15+                                │    │
│    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│    │  │  users   │ │  trans-  │ │  debts   │ │ patterns │            │    │
│    │  │          │ │  actions │ │          │ │          │            │    │
│    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘            │    │
│    └──────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│    ┌──────────────────────────────────────────────────────────────────┐    │
│    │                       Redis (Cache)                               │    │
│    │  - Session storage                                                │    │
│    │  - Agent response cache                                           │    │
│    │  - Rate limiting                                                  │    │
│    └──────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| Language | Python | 3.11+ | Claude SDK compatibility, async support |
| Framework | FastAPI | 0.100+ | Async-first, OpenAPI docs, type hints |
| ORM | SQLAlchemy | 2.0+ | Async support, mature ecosystem |
| Validation | Pydantic | 2.0+ | Built into FastAPI, type safety |
| Task Queue | Celery | 5.3+ | Background processing (optional) |

### Frontend

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| Framework | React | 18+ | Modern hooks, concurrent features |
| Language | TypeScript | 5.0+ | Type safety, IDE support |
| State | Zustand | 4.0+ | Simple, performant |
| UI Library | shadcn/ui | Latest | Accessible, customizable |
| Charts | Recharts | 2.0+ | React-native charting |
| HTTP | Axios | 1.0+ | Interceptors, error handling |

### Database

| Component | Technology | Version | Justification |
|-----------|------------|---------|---------------|
| Primary DB | PostgreSQL | 15+ | ACID compliance, financial data |
| Cache | Redis | 7.0+ | Session, rate limiting |
| Migrations | Alembic | 1.12+ | Version-controlled schema |

### Infrastructure

| Component | Technology | Justification |
|-----------|------------|---------------|
| Container | Docker | Consistent deployment |
| Orchestration | Docker Compose (dev) | Local development |
| Cloud | AWS | Production-grade, Malaysia region |
| CI/CD | GitHub Actions | Native to GitHub |

### AI

| Component | Technology | Justification |
|-----------|------------|---------------|
| LLM Provider | Anthropic Claude | Best-in-class reasoning |
| Model | claude-sonnet-4-20250514 | Cost-effective, accurate |
| SDK | anthropic Python SDK | Official client |

---

## Component Details

### 1. API Layer

```
src/api/
├── __init__.py
├── main.py                 # FastAPI app initialization
├── dependencies.py         # Dependency injection
├── middleware/
│   ├── auth.py            # JWT authentication
│   ├── rate_limit.py      # Rate limiting
│   └── logging.py         # Request logging
└── routes/
    ├── auth.py            # /auth endpoints
    ├── upload.py          # /upload endpoints
    ├── transactions.py    # /transactions endpoints
    ├── agents.py          # /agents endpoints
    └── query.py           # /query endpoints
```

### 2. Business Logic Layer

```
src/services/
├── __init__.py
├── statement_parser/
│   ├── base.py            # Abstract parser
│   ├── maybank.py         # Maybank parser
│   ├── cimb.py            # CIMB parser
│   ├── rhb.py             # RHB parser
│   └── tng.py             # Touch 'n Go parser
├── transaction_service.py  # Transaction CRUD
├── debt_service.py         # Debt management
└── analytics_service.py    # Aggregations
```

### 3. Agent Layer

```
src/agents/
├── __init__.py
├── base.py                 # BaseAgent class
├── orchestrator.py         # Agent routing
├── categorizer.py          # AG-01
├── debt_detector.py        # AG-02
├── pattern_analyzer.py     # AG-03
├── predictor.py            # AG-04
├── query_agent.py          # AG-05
└── advisor.py              # AG-06
```

### 4. Data Layer

```
src/models/
├── __init__.py
├── user.py                 # User model
├── transaction.py          # Transaction model
├── debt.py                 # Debt model
├── pattern.py              # Pattern model
└── prediction.py           # Prediction model

src/repositories/
├── __init__.py
├── base.py                 # Generic repository
├── user_repo.py
├── transaction_repo.py
└── debt_repo.py
```

---

## Data Flow

### Statement Upload Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────>│  API    │────>│ Parser  │────>│   DB    │
│ uploads │     │ /upload │     │ Service │     │  Store  │
│  PDF    │     │         │     │         │     │         │
└─────────┘     └─────────┘     └────┬────┘     └─────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │   Agent     │
                              │ Orchestrator│
                              └──────┬──────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
   ┌──────────┐               ┌──────────┐               ┌──────────┐
   │Categorize│──────────────>│  Detect  │──────────────>│ Analyze  │
   │  AG-01   │               │  Debt    │               │ Patterns │
   │          │               │  AG-02   │               │  AG-03   │
   └──────────┘               └──────────┘               └────┬─────┘
                                                              │
                                     ┌────────────────────────┘
                                     │
                                     ▼
                              ┌──────────┐               ┌──────────┐
                              │ Predict  │──────────────>│ Generate │
                              │  AG-04   │               │  Advice  │
                              │          │               │  AG-06   │
                              └──────────┘               └────┬─────┘
                                                              │
                                                              ▼
                                                       ┌──────────┐
                                                       │ Response │
                                                       │ to User  │
                                                       └──────────┘
```

### Query Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────>│  API    │────>│ Intent  │────>│ Route   │
│  asks   │     │ /query  │     │Classify │     │ Agent   │
│question │     │         │     │         │     │         │
└─────────┘     └─────────┘     └─────────┘     └────┬────┘
                                                     │
                         ┌───────────────────────────┼───────────────────────────┐
                         │           │               │               │           │
                         ▼           ▼               ▼               ▼           ▼
                   ┌──────────┐┌──────────┐   ┌──────────┐   ┌──────────┐┌──────────┐
                   │  AG-01   ││  AG-02   │   │  AG-05   │   │  AG-04   ││  AG-06   │
                   │Category  ││  Debt    │   │  Query   │   │ Predict  ││ Advisor  │
                   └──────────┘└──────────┘   └────┬─────┘   └──────────┘└──────────┘
                                                   │
                                                   ▼
                                            ┌──────────┐
                                            │ Response │
                                            │ to User  │
                                            └──────────┘
```

---

## Security Architecture

### Authentication Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────>│  Login  │────>│ Verify  │────>│  Issue  │
│         │     │  /auth  │     │Password │     │   JWT   │
└─────────┘     └─────────┘     └─────────┘     └────┬────┘
                                                     │
                                                     ▼
                                              ┌──────────┐
                                              │  Return  │
                                              │  Token   │
                                              └──────────┘

Subsequent requests:
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Request │────>│ Extract │────>│ Verify  │────>│ Process │
│  + JWT  │     │ Bearer  │     │   JWT   │     │ Request │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
```

### Security Measures

| Layer | Measure | Implementation |
|-------|---------|----------------|
| Transport | TLS 1.3 | All traffic encrypted |
| Authentication | JWT | 15-min access, 7-day refresh |
| Authorization | RBAC | User can only access own data |
| Data at Rest | AES-256 | Encrypted database columns |
| Input Validation | Pydantic | All inputs validated |
| Rate Limiting | Redis | Per-user, per-endpoint limits |
| CORS | Whitelist | Only allowed origins |

---

## Deployment Architecture

### Development (Local)

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Compose                              │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   React     │  │   FastAPI   │  │  PostgreSQL │             │
│  │   :3000     │  │   :8000     │  │   :5432     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
│                        ┌─────────────┐                          │
│                        │    Redis    │                          │
│                        │    :6379    │                          │
│                        └─────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

### Production (AWS)

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS Cloud                                │
│                                                                  │
│  ┌─────────────┐                    ┌─────────────────────────┐│
│  │ CloudFront  │                    │        VPC              ││
│  │    CDN      │                    │                         ││
│  └──────┬──────┘                    │  ┌─────────────────┐   ││
│         │                           │  │   ECS Fargate   │   ││
│         │                           │  │   (FastAPI)     │   ││
│         │                           │  └────────┬────────┘   ││
│         │                           │           │            ││
│         │       ┌───────────────────┼───────────┘            ││
│         │       │                   │                        ││
│         ▼       ▼                   │  ┌─────────────────┐   ││
│  ┌─────────────────┐               │  │   RDS           │   ││
│  │      ALB        │               │  │  (PostgreSQL)   │   ││
│  │ (Load Balancer) │               │  └─────────────────┘   ││
│  └─────────────────┘               │                        ││
│                                     │  ┌─────────────────┐   ││
│  ┌─────────────────┐               │  │  ElastiCache    │   ││
│  │       S3        │               │  │    (Redis)      │   ││
│  │ (Static Assets) │               │  └─────────────────┘   ││
│  └─────────────────┘               │                        ││
│                                     └─────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## API Specification

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | User registration |
| POST | /auth/login | User login |
| POST | /auth/refresh | Refresh token |
| POST | /upload/statement | Upload bank statement |
| GET | /transactions | List transactions |
| GET | /transactions/{id} | Get single transaction |
| PATCH | /transactions/{id} | Update transaction |
| POST | /query | Natural language query |
| GET | /debts | List detected debts |
| GET | /patterns | Get spending patterns |
| GET | /predictions | Get spending predictions |
| GET | /advice | Get financial advice |

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2026-01-10T10:30:00Z",
    "version": "1.0.0"
  },
  "error": null
}
```

### Error Format

```json
{
  "success": false,
  "data": null,
  "meta": {
    "timestamp": "2026-01-10T10:30:00Z",
    "version": "1.0.0"
  },
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": { ... }
  }
}
```

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (p95) | <500ms | All endpoints except agent calls |
| Agent Response Time (p95) | <3s | AI agent endpoints |
| Statement Processing | <30s | Full pipeline for 100 transactions |
| Database Query Time | <100ms | 95th percentile |
| Uptime | 99.5% | Monthly availability |

---

## Related Documents

- [ADR-001: Agent Orchestration](ADR/001-AGENT-ORCHESTRATION.md)
- [ADR-002: Bank Parsing](ADR/002-BANK-PARSING.md)
- [ADR-003: Legal Compliance](ADR/003-LEGAL-COMPLIANCE.md)
- [Data Model](DATA_MODEL.md)
- [Technical Plan](TECHNICAL_PLAN.md)

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
