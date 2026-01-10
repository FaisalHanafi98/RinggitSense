# RinggitSense Constitution

> *"Sedar duit, sedar diri"* — Know your money, know yourself

## Project Identity

| Field | Value |
|-------|-------|
| **Canonical Name** | RinggitSense |
| **Deprecated Names** | DuitSedar (do not use in new code/docs) |
| **Domain** | AI-powered personal finance management |
| **Target Market** | Malaysian young professionals (22-35) |
| **Strategic Intent** | Portfolio flagship + Production deployment |
| **Timeline** | 8 weeks MVP |

---

## Core Principles

### I. Malaysian-First Design

Every feature, every interaction, every piece of advice MUST be grounded in Malaysian context:

- **Currency**: Always RM (Malaysian Ringgit), never USD unless explicitly converting
- **Banks**: Support Maybank, CIMB, RHB, Public Bank, Hong Leong, Aeon Bank
- **E-wallets**: Touch 'n Go, GrabPay, ShopeePay, Boost, BigPay
- **BNPL**: SPayLater, GrabPayLater, Atome, Split, Hoolah
- **Tolls**: PLUS, LDP, DUKE, SMART, AKLEH, KESAS, MEX, NPE
- **Cultural terms**: "Hutang" (debt), "Makan" (food), "Bayar" (pay), "Topup", "Reload"
- **Festivals**: Hari Raya, CNY, Deepavali spending patterns
- **Regulations**: PDPA Malaysia compliance required

### II. Six-Agent Architecture

The AI layer consists of exactly SIX specialized Claude agents:

| Agent | Single Responsibility | Cannot Do |
|-------|----------------------|-----------|
| **Categorizer** | Classify transactions into categories | Provide advice |
| **Debt Detector** | Identify debt across 3 tiers (Formal, BNPL, Hutang) | Make predictions |
| **Pattern Analyzer** | Discover spending patterns and anomalies | Give recommendations |
| **Predictor** | Forecast next-month spending | Categorize transactions |
| **Query Agent** | Answer natural language questions | Modify data |
| **Advisor** | Provide personalized financial guidance | Make predictions |

**Non-negotiable**: Each agent has ONE job. No agent crosses boundaries.

### III. Anti-Hallucination Protocol

Financial data accuracy is CRITICAL. All agents MUST:

1. **Ground claims in data**: Never invent statistics or bank formats
2. **Mark uncertainty**: Use `[NEEDS INPUT]` for unknown information
3. **No invented regulations**: Mark as `[LEGAL REVIEW REQUIRED]`
4. **No fake bank formats**: Mark as `[REQUIRES SAMPLE DATA]`
5. **Confidence scores**: Always include 0.0-1.0 confidence in outputs
6. **Source tracing**: Every claim traceable to input data

**Violation of anti-hallucination rules is a blocking defect.**

### IV. Legal Disclaimer Mandate

Every piece of financial advice MUST include disclaimers:

```
REQUIRED DISCLAIMERS:
1. "This is not professional financial advice"
2. "Consult a licensed financial advisor for major decisions"
3. "Past patterns do not guarantee future results"
4. "RinggitSense does not have access to real-time bank data"
```

Disclaimers must be:
- Present in API responses
- Visible in UI before advice display
- Logged for audit purposes
- Tested in automated quality checks

### V. Test-First Development

TDD is MANDATORY for this project:

1. **Write test first** → Get approval → Test fails → Implement
2. **Red-Green-Refactor** cycle strictly enforced
3. **80% code coverage** minimum for all modules
4. **Agent testing**: Golden dataset + behavioral + adversarial tests
5. **No merge without tests** — CI blocks PRs with failing tests

### VI. Portfolio-Ready Documentation

This is a FLAGSHIP portfolio project. All code and documentation must be:

1. **Interview-defensible**: Every architectural decision explainable
2. **Recruiter-readable**: Executive summaries for non-technical reviewers
3. **Achievement-extractable**: STAR-format bullets derivable from each feature
4. **Visually professional**: Diagrams, screenshots, clear formatting

### VII. Simplicity & YAGNI

- Start simple, add complexity only when proven necessary
- No premature optimization
- No speculative features
- Each abstraction must justify its existence
- Prefer explicit over implicit

---

## Technology Constraints

### Required Stack

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Backend | Python | 3.11+ | Agent SDK compatibility |
| API Framework | FastAPI | 0.100+ | Async, type hints, OpenAPI |
| Frontend | React | 18+ | Modern hooks, TypeScript |
| Database | PostgreSQL | 15+ | Financial data integrity |
| AI | Claude API | Sonnet 4 | Cost-effective, accurate |
| Infrastructure | AWS | - | Production-grade |
| Container | Docker | - | Consistent deployment |

### Forbidden Patterns

- No hardcoded secrets (use environment variables)
- No SQL string concatenation (use parameterized queries)
- No unvalidated user input to agents
- No storing raw API keys in database
- No committing .env files

---

## Malaysian Financial Context

### Debt Tiers (Tri-Tier Model)

| Tier | Type | Examples | Detection Method |
|------|------|----------|------------------|
| **FORMAL** | Bank/institution loans | PTPTN, car loan, personal loan, mortgage, credit card | Bank statement keywords |
| **BNPL** | Buy Now Pay Later | SPayLater, GrabPayLater, Atome | E-commerce patterns |
| **HUTANG** | Informal debts | Family loans, friend borrowings | Transfer + comment analysis |

### Transaction Categories

| Category | Definition | Examples |
|----------|------------|----------|
| FOOD | Food & beverages, dining, groceries | McDonalds, Mamak, Jaya Grocer |
| TRANSPORT | Tolls, petrol, parking, rides | PLUS toll, Shell, Grab ride |
| BILLS | Utilities, phone, internet, subscriptions | TNB, Unifi, Celcom, Netflix |
| ENTERTAINMENT | Leisure, movies, games, hobbies | TGV, Steam, Spotify |
| SHOPPING | Retail purchases, online shopping | Shopee, Lazada, Uniqlo |
| TRANSFER | Money transfers between accounts/people | IBG, DuitNow |
| DEBT_PAYMENT | Loan repayments, BNPL installments | PTPTN, SPayLater |
| INCOME | Salary, deposits, refunds | Salary, bonus, cashback |
| HEALTHCARE | Medical, pharmacy, insurance | Pharmacy, clinic |
| OTHER | Anything that doesn't fit above | Use sparingly |

### Regulatory Compliance

| Regulation | Requirement | Implementation |
|------------|-------------|----------------|
| **PDPA Malaysia** | Personal data protection | Encryption at rest + transit, consent flows |
| **BNM Guidelines** | Not a licensed financial advisor | Clear disclaimers on all advice |
| **LHDN** | No tax advice provided | Explicit exclusion in scope |

---

## Development Workflow

### Branch Strategy

```
main                 ← Production-ready code only
├── develop          ← Integration branch
│   ├── feature/*    ← New features
│   ├── bugfix/*     ← Bug fixes
│   └── agent/*      ← Agent-specific work
```

### Commit Message Format

```
type(scope): subject

Types: feat, fix, docs, style, refactor, test, chore
Scope: categorizer, debt-detector, api, ui, db, etc.

Example: feat(categorizer): add Maybank statement parser
```

### Quality Gates

| Gate | Requirement | Blocks |
|------|-------------|--------|
| Lint | Zero errors | PR merge |
| Unit Tests | 80% coverage | PR merge |
| Integration Tests | All passing | Merge to develop |
| E2E Tests | Critical paths pass | Merge to main |
| Agent Tests | Golden dataset pass | Agent changes |
| Security Scan | No critical issues | Deployment |

---

## Governance

### Constitution Authority

1. This constitution supersedes all other documentation when conflicts arise
2. Amendments require:
   - Documented rationale
   - Impact analysis
   - Migration plan (if breaking)
3. All PRs must verify constitution compliance
4. Complexity additions must justify against Principle VII (Simplicity)

### Exception Process

To request an exception to any principle:
1. Document the specific principle being violated
2. Explain why violation is necessary
3. Propose mitigation measures
4. Get explicit approval before implementation

---

**Version**: 1.0.0 | **Ratified**: 2026-01-10 | **Last Amended**: 2026-01-10
