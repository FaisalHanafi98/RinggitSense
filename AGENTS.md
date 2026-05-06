> **GOVERNANCE NOTICE**: This project-level AGENTS.md operates under the authority of the root AGENTS.md. In case of conflict, root AGENTS.md (Section 0.2 Override Hierarchy) prevails. This file may define project-specific constraints but may not override root governance.

---

# RinggitSense Project Instructions

> *"Sedar duit, sedar diri"* — Know your money, know yourself

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | RinggitSense |
| **Domain** | AI-powered personal finance management |
| **Target** | Malaysian young professionals (22-35) |
| **Status** | Active Development |

---

## Quick Reference

### Core Documents

| Document | Purpose | Location |
|----------|---------|----------|
| Constitution | Core principles | [.specify/memory/constitution.md](.specify/memory/constitution.md) |
| Problem Statement | Why this project exists | [.specify/specs/PROBLEM_STATEMENT.md](.specify/specs/PROBLEM_STATEMENT.md) |
| Architecture | System design | [.specify/plans/ARCHITECTURE.md](.specify/plans/ARCHITECTURE.md) |
| Task Registry | What to work on | [.specify/tasks/TASK_REGISTRY.md](.specify/tasks/TASK_REGISTRY.md) |
| Agent Index | AI agent specifications | [agents/AGENT_INDEX.md](agents/AGENT_INDEX.md) |

---

## Development Rules

### 1. Malaysian-First Context

All code, data, and outputs MUST use Malaysian context:

- **Currency**: Always RM (Malaysian Ringgit)
- **Banks**: Maybank, CIMB, RHB, Public Bank, Hong Leong, Aeon
- **E-wallets**: Touch 'n Go, GrabPay, ShopeePay, Boost, BigPay
- **BNPL**: SPayLater, GrabPayLater, Atome, Split
- **Tolls**: PLUS, LDP, DUKE, SMART, AKLEH, KESAS, MEX, NPE

### 2. Six-Agent Architecture

The AI layer consists of exactly 6 specialized Codex agents:

| Agent | Responsibility | Definition |
|-------|---------------|------------|
| AG-01 | Categorize transactions | [agents/definitions/categorizer.md](agents/definitions/categorizer.md) |
| AG-02 | Detect debt (3 tiers) | [agents/definitions/debt-detector.md](agents/definitions/debt-detector.md) |
| AG-03 | Analyze patterns | [agents/definitions/pattern-analyzer.md](agents/definitions/pattern-analyzer.md) |
| AG-04 | Predict spending | [agents/definitions/predictor.md](agents/definitions/predictor.md) |
| AG-05 | Answer questions | [agents/definitions/query.md](agents/definitions/query.md) |
| AG-06 | Provide advice | [agents/definitions/advisor.md](agents/definitions/advisor.md) |

**Rule**: Each agent has ONE job. Never cross boundaries.

### 3. Anti-Hallucination Protocol

Financial data accuracy is CRITICAL:

- ❌ Never invent statistics or bank formats
- ❌ Never guess Malaysian regulations
- ✅ Use `[NEEDS INPUT]` for unknown information
- ✅ Include confidence scores (0.0-1.0) in all outputs
- ✅ Trace every claim to input data

### 4. Mandatory Disclaimers

Every piece of financial advice MUST include:

```
1. "This is not professional financial advice"
2. "Consult a licensed financial advisor for major decisions"
3. "Past patterns do not guarantee future results"
```

### 5. Test-First Development

TDD is MANDATORY:

1. Write test first → Get approval → Test fails → Implement
2. 80% code coverage minimum
3. No merge without tests

---

## Project Structure

```
RinggitSense/
├── AGENTS.md                    # This file
├── agents/                      # AI agent specifications
│   ├── AGENT_INDEX.md
│   ├── definitions/             # Individual agent specs
│   └── orchestration/           # Routing rules
├── .specify/                    # Spec-kit documentation
│   ├── memory/constitution.md   # Core principles
│   ├── specs/                   # Feature specifications
│   ├── plans/                   # Architecture & ADRs
│   └── tasks/                   # Task breakdown
├── backend/                     # Python FastAPI (to be created)
├── frontend/                    # React TypeScript (to be created)
└── docs/                        # Additional documentation
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+ / FastAPI |
| Frontend | React 18 / TypeScript |
| Database | PostgreSQL 15+ |
| Cache | Redis 7+ |
| AI | Codex Sonnet 4 |
| Deploy | AWS (ECS Fargate) |

---

## Agent Routing Rules

### When to use each agent:

```python
def route_request(request):
    question = request.question.lower()

    if "category" in question or "kategorikan" in question:
        return "AG-01"  # Categorizer

    if any(word in question for word in ["debt", "hutang", "loan", "ptptn", "bnpl"]):
        return "AG-02"  # Debt Detector

    if any(word in question for word in ["pattern", "trend", "hidden", "corak"]):
        return "AG-03"  # Pattern Analyzer

    if any(word in question for word in ["predict", "next month", "forecast"]):
        return "AG-04"  # Predictor

    if any(word in question for word in ["advice", "should", "recommend", "nasihat"]):
        return "AG-06"  # Advisor

    return "AG-05"  # Query Agent (default)
```

### Sequential Pipeline (Statement Upload):

```
Upload → AG-01 → AG-02 → AG-03 → AG-04 → AG-06
```

---

## Common Tasks

### Starting a new feature

1. Check [TASK_REGISTRY.md](.specify/tasks/TASK_REGISTRY.md) for task details
2. Read relevant agent definition in [agents/definitions/](agents/definitions/)
3. Write tests first
4. Implement feature
5. Update task status

### Working with agents

1. Read agent definition file
2. Follow the system prompt exactly
3. Validate input/output schemas
4. Include confidence scores
5. Test against golden dataset

### Adding a new bank parser

1. Get sample statement (PDF/CSV)
2. Create parser in `backend/src/services/statement_parser/`
3. Implement abstract interface
4. Add tests with sample data
5. Register in parser factory

---

## Quality Gates

| Gate | Requirement |
|------|-------------|
| Lint | Zero errors |
| Unit Tests | 80% coverage |
| Agent Tests | Golden dataset pass |
| Security | No critical issues |

---

## DO NOT

- ❌ Hardcode secrets
- ❌ Use SQL string concatenation
- ❌ Store raw API keys in database
- ❌ Commit .env files
- ❌ Skip disclaimers on advice
- ❌ Cross agent boundaries
- ❌ Invent Malaysian regulations

---

## Related Projects

This project is part of the portfolio orchestration system:

- **Parent**: [../.orchestrator/](../.orchestrator/)
- **Siblings**: CREAMS, Sen2Nal, Portfolio, AUTO_RECRUIT

---

**Version**: 1.0.0 | **Last Updated**: 2026-01-10
