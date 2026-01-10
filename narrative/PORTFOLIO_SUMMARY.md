# RinggitSense Portfolio Summary

> Executive summary for recruiters and portfolio reviewers

---

## Project Overview

**RinggitSense** is an AI-powered personal finance platform designed specifically for Malaysian users. It addresses the unique financial challenges faced by young Malaysian professionals: fragmented payment sources, invisible BNPL debt, and lack of local context in existing tools.

### The Problem

- **53,000 Malaysians under 30** carry nearly RM1.9 billion in debt
- Youth bankruptcy cases rising 20% year-over-year
- Money fragmented across 4+ apps (banks, e-wallets, BNPL)
- No tool understands Malaysian context (toll, mamak, hutang)

### The Solution

RinggitSense provides:
- **Unified View**: Aggregate all Malaysian banks and e-wallets
- **Tri-Tier Debt Tracking**: Formal loans, BNPL, and informal "hutang"
- **AI-Powered Insights**: Six specialized Claude agents for analysis
- **Culturally-Aware Advice**: Respects Malaysian family obligations and customs

---

## Technical Highlights

### Six-Agent AI Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│           RINGGITSENSE AI AGENT ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Categorizer │  │ Debt        │  │ Pattern     │            │
│  │   Agent     │  │ Detector    │  │ Analyzer    │            │
│  │             │  │             │  │             │            │
│  │ 95%+ acc.   │  │ 90%+ recall │  │ Hidden cost │            │
│  │ 10 categories│ │ 3 tiers     │  │ discovery   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ Predictor   │  │ Query       │  │ Advisor     │            │
│  │   Agent     │  │ Agent       │  │             │            │
│  │             │  │             │  │             │            │
│  │ 15% accuracy│  │ NL queries  │  │ Personalized│            │
│  │ forecasting │  │ EN + Malay  │  │ + Disclaimers│           │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Six separate agents** | Single responsibility, testability, cost optimization |
| **Claude Sonnet 4** | Best accuracy-to-cost ratio for financial analysis |
| **Golden dataset testing** | AI reliability requires domain-specific validation |
| **Anti-hallucination protocol** | Financial data accuracy is non-negotiable |

### Technology Stack

| Layer | Technology | Why |
|-------|------------|-----|
| Backend | FastAPI (Python) | Async, type-safe, Claude SDK support |
| Frontend | React 18 + TypeScript | Modern, type-safe, component reusability |
| Database | PostgreSQL | ACID compliance for financial data |
| AI | Claude Sonnet 4 | Best-in-class reasoning for financial context |
| Deploy | AWS (ECS Fargate) | Production-grade, Malaysia region available |

---

## Key Features

### 1. Malaysian Bank Statement Parsing
- Supports Maybank, CIMB, RHB, Touch 'n Go
- PDF and CSV parsing
- Auto-detection of bank format

### 2. AI-Powered Categorization
- 10 spending categories
- 95%+ accuracy on Malaysian merchants
- Recognizes local context (toll plazas, mamak, BNPL)

### 3. Tri-Tier Debt Detection
| Tier | Description |
|------|-------------|
| FORMAL | Bank loans, PTPTN, mortgages |
| BNPL | SPayLater, GrabPayLater, Atome |
| HUTANG | Informal debts to family/friends |

### 4. Pattern Discovery
- Weekend spending surge detection
- Hidden cost aggregation (toll often underestimated 40-60%)
- Lifestyle bundle identification

### 5. Spending Prediction
- Next-month forecasting with 90% confidence intervals
- Trend analysis by category
- Festival period adjustments

### 6. Culturally-Aware Advice
- Respects family obligations
- Non-judgmental about hutang
- Always includes legal disclaimers

---

## Engineering Excellence

### Quality Assurance
- **80%+ code coverage** with pytest and Jest
- **Golden dataset testing** for all AI agents
- **Adversarial testing** for edge cases
- **E2E testing** with Playwright

### DevOps & Infrastructure
- **Docker containerization** for consistent deployment
- **GitHub Actions CI/CD** for automated testing and deployment
- **AWS infrastructure as code** (Terraform/CDK)
- **CloudWatch monitoring** with alerting

### Security & Compliance
- **PDPA Malaysia compliance** for personal data
- **Encryption at rest and in transit**
- **JWT authentication** with refresh tokens
- **Mandatory disclaimers** on all financial advice

---

## Impact Metrics (Targets)

| Metric | Target |
|--------|--------|
| Transaction categorization accuracy | >95% |
| Debt detection recall | >90% |
| Hidden cost revelation | >RM100/month per user |
| Prediction accuracy | Within 15% of actual |
| User time-to-insight | <5 minutes |

---

## Skills Demonstrated

### AI/ML Engineering
- LLM prompt engineering for specialized tasks
- Multi-agent orchestration patterns
- Golden dataset creation and testing
- Confidence scoring and uncertainty handling

### Full-Stack Development
- REST API design with FastAPI
- React component architecture
- State management (Zustand)
- Responsive UI design

### Data Engineering
- PDF/CSV parsing and extraction
- Database schema design
- Data validation and normalization
- Caching strategies

### DevOps
- Docker containerization
- CI/CD pipeline implementation
- AWS cloud deployment
- Monitoring and alerting

### Domain Knowledge
- Malaysian financial ecosystem
- BNPL market understanding
- Cultural sensitivity in fintech
- Regulatory compliance (PDPA, BNM guidelines)

---

## Project Structure

```
RinggitSense/
├── CLAUDE.md                    # AI instructions
├── agents/                      # 6 agent specifications
│   ├── definitions/             # Individual agent specs
│   └── orchestration/           # Routing and handoffs
├── .specify/                    # Spec-kit documentation
│   ├── specs/                   # Feature specifications
│   ├── plans/                   # Architecture & ADRs
│   └── tasks/                   # Phase breakdowns
├── backend/                     # Python FastAPI
├── frontend/                    # React TypeScript
└── narrative/                   # Portfolio materials
```

---

## Links

- **GitHub Repository**: [github.com/FaisalHanafi98/RinggitSense](https://github.com/FaisalHanafi98/RinggitSense)
- **Live Demo**: (Coming soon)
- **Technical Documentation**: See `.specify/` folder

---

## About the Developer

**Faisal Hanafi** - Software Engineer with expertise in AI-powered applications, full-stack development, and Malaysian fintech domain knowledge.

This project demonstrates:
- End-to-end product thinking from problem to solution
- Advanced AI/LLM engineering with Claude
- Production-ready software engineering practices
- Deep understanding of Malaysian financial context

---

*Last Updated: 2026-01-10*
