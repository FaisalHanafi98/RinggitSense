# RinggitSense Agent Registry

> Master index and status overview for all Claude agents

**Project**: RinggitSense
**Version**: 1.0.0
**Last Updated**: 2026-01-10

---

## Agent Overview

RinggitSense uses a **six-agent architecture** where each Claude agent has a single, well-defined responsibility. This design ensures separation of concerns, testability, and cost optimization.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RINGGITSENSE AGENT ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                   │
│    │ CATEGORIZER │    │    DEBT     │    │   PATTERN   │                   │
│    │   AG-01     │    │  DETECTOR   │    │  ANALYZER   │                   │
│    │             │    │   AG-02     │    │   AG-03     │                   │
│    │ Classify    │    │ Identify    │    │ Discover    │                   │
│    │ transactions│    │ debt tiers  │    │ patterns    │                   │
│    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                   │
│           │                  │                  │                           │
│           ▼                  ▼                  ▼                           │
│    ┌─────────────────────────────────────────────────────┐                 │
│    │              ORCHESTRATION LAYER                    │                 │
│    │  Routes requests • Manages handoffs • Resolves conflicts              │
│    └─────────────────────────────────────────────────────┘                 │
│           │                  │                  │                           │
│           ▼                  ▼                  ▼                           │
│    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                   │
│    │  PREDICTOR  │    │    QUERY    │    │   ADVISOR   │                   │
│    │   AG-04     │    │   AGENT     │    │   AG-06     │                   │
│    │             │    │   AG-05     │    │             │                   │
│    │ Forecast    │    │ Answer      │    │ Provide     │                   │
│    │ spending    │    │ questions   │    │ guidance    │                   │
│    └─────────────┘    └─────────────┘    └─────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Agent Registry Table

| ID | Agent Name | Primary Function | Model | Temperature | Status |
|----|------------|------------------|-------|-------------|--------|
| AG-01 | [Categorizer](definitions/categorizer.md) | Classify transactions | claude-sonnet-4-20250514 | 0.2 | Defined |
| AG-02 | [Debt Detector](definitions/debt-detector.md) | Identify debt obligations | claude-sonnet-4-20250514 | 0.1 | Defined |
| AG-03 | [Pattern Analyzer](definitions/pattern-analyzer.md) | Discover spending patterns | claude-sonnet-4-20250514 | 0.5 | Defined |
| AG-04 | [Predictor](definitions/predictor.md) | Forecast future spending | claude-sonnet-4-20250514 | 0.3 | Defined |
| AG-05 | [Query Agent](definitions/query.md) | Answer natural language questions | claude-sonnet-4-20250514 | 0.7 | Defined |
| AG-06 | [Advisor](definitions/advisor.md) | Provide financial guidance | claude-sonnet-4-20250514 | 0.6 | Defined |

---

## Agent Responsibilities Matrix

| Responsibility | AG-01 | AG-02 | AG-03 | AG-04 | AG-05 | AG-06 |
|----------------|-------|-------|-------|-------|-------|-------|
| Categorize transactions | **YES** | - | - | - | - | - |
| Detect debt patterns | - | **YES** | - | - | - | - |
| Discover spending patterns | - | - | **YES** | - | - | - |
| Predict future spending | - | - | - | **YES** | - | - |
| Answer questions | - | - | - | - | **YES** | - |
| Provide financial advice | - | - | - | - | - | **YES** |
| Access transaction data | Read | Read | Read | Read | Read | Read |
| Modify transaction data | - | - | - | - | - | - |
| Generate disclaimers | - | - | - | - | - | **YES** |

---

## Agent Communication Flows

### Sequential Pipeline (Statement Upload)

```
Transaction Upload
       │
       ▼
┌──────────────┐
│  AG-01       │ ── Each transaction categorized
│  Categorizer │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  AG-02       │ ── Debt transactions identified
│  Debt Detector│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  AG-03       │ ── Patterns discovered
│  Pattern     │
│  Analyzer    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  AG-04       │ ── Next month forecasted
│  Predictor   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  AG-06       │ ── Recommendations generated
│  Advisor     │
└──────────────┘
```

### On-Demand Query Flow

```
User Question
       │
       ▼
┌──────────────┐
│  AG-05       │ ── Answer generated
│  Query Agent │
└──────┬───────┘
       │
       ├── May delegate to AG-01 for "what category is X?"
       ├── May delegate to AG-04 for "what will I spend?"
       └── May delegate to AG-06 for "what should I do?"
```

---

## Orchestration Documents

| Document | Purpose |
|----------|---------|
| [ROUTING_RULES.md](orchestration/ROUTING_RULES.md) | When to delegate to which agent |
| [HANDOFF_PROTOCOLS.md](orchestration/HANDOFF_PROTOCOLS.md) | How agents pass work between each other |
| [CONFLICT_RESOLUTION.md](orchestration/CONFLICT_RESOLUTION.md) | Handling overlapping responsibilities |

---

## Quality Standards

All agents must adhere to:

1. **Anti-Hallucination Protocol**: Never invent data, always cite sources
2. **Confidence Scoring**: Include 0.0-1.0 confidence in all outputs
3. **Malaysian Context**: Understand local banks, e-wallets, and cultural terms
4. **Legal Compliance**: Include disclaimers where required (especially AG-06)
5. **Performance**: Meet latency targets (see individual agent specs)

---

## Testing Requirements

| Agent | Unit Tests | Golden Dataset | Adversarial Tests |
|-------|------------|----------------|-------------------|
| AG-01 Categorizer | 50+ cases | 500 transactions | Edge cases |
| AG-02 Debt Detector | 30+ cases | 100 debt scenarios | False positives |
| AG-03 Pattern Analyzer | 20+ cases | 3-month datasets | Sparse data |
| AG-04 Predictor | 20+ cases | 6-month datasets | Irregular patterns |
| AG-05 Query Agent | 50+ cases | 100 questions | Malformed queries |
| AG-06 Advisor | 30+ cases | 50 profiles | Edge cases |

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
