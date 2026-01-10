# Agent Handoff Protocols

> How agents pass work and context to each other

**Version**: 1.0.0
**Last Updated**: 2026-01-10

---

## Overview

Agents do NOT communicate directly. All communication flows through the orchestrator to ensure auditability and control.

```
Agent A → Orchestrator → Agent B
         (validates)
         (logs)
         (transforms)
```

---

## Standard Handoff Format

When one agent needs to pass work to another:

```json
{
  "handoff": {
    "from_agent": "AG-01",
    "to_agent": "AG-02",
    "reason": "Debt-related transaction detected",
    "context": {
      "transaction_id": "txn_12345",
      "preliminary_analysis": { ... },
      "confidence": 0.85
    },
    "timestamp": "2026-01-10T10:30:00Z"
  }
}
```

---

## Pipeline Handoffs

### Sequential Pipeline Flow

```
┌─────────────┐
│   Upload    │
│   Handler   │
└──────┬──────┘
       │ Transactions[]
       ▼
┌─────────────┐
│   AG-01     │ Input: Raw transactions
│ Categorizer │ Output: Categorized transactions
└──────┬──────┘
       │ {transactions: CategorizedTransaction[]}
       ▼
┌─────────────┐
│   AG-02     │ Input: Categorized transactions
│ Debt Detect │ Output: Debt analysis + transactions
└──────┬──────┘
       │ {transactions, debt_analysis: DebtAnalysis}
       ▼
┌─────────────┐
│   AG-03     │ Input: Transactions + debt info
│ Pattern     │ Output: Patterns discovered
└──────┬──────┘
       │ {transactions, debt_analysis, patterns: Pattern[]}
       ▼
┌─────────────┐
│   AG-04     │ Input: All above context
│ Predictor   │ Output: Next month prediction
└──────┬──────┘
       │ {transactions, debt_analysis, patterns, prediction: Prediction}
       ▼
┌─────────────┐
│   AG-06     │ Input: All accumulated context
│ Advisor     │ Output: Personalized recommendations
└─────────────┘
```

---

## Context Accumulation

Each agent in the pipeline receives ALL context from previous agents:

### AG-01 → AG-02 Handoff

```json
{
  "handoff": {
    "from_agent": "AG-01",
    "to_agent": "AG-02",
    "context": {
      "transactions": [
        {
          "id": "txn_001",
          "description": "PTPTN REPAYMENT",
          "amount": 250.00,
          "category": "DEBT_PAYMENT",
          "confidence": 0.95,
          "merchant_name": "PTPTN"
        }
      ],
      "categorization_summary": {
        "total_processed": 100,
        "high_confidence": 85,
        "needs_review": 15
      }
    }
  }
}
```

### AG-02 → AG-03 Handoff

```json
{
  "handoff": {
    "from_agent": "AG-02",
    "to_agent": "AG-03",
    "context": {
      "transactions": [...],  // From AG-01
      "debt_analysis": {
        "formal": {
          "count": 2,
          "providers": ["PTPTN", "Maybank HP"],
          "monthly_total": 850.00
        },
        "bnpl": {
          "count": 1,
          "providers": ["SPayLater"],
          "monthly_total": 83.33
        },
        "hutang": {
          "count": 0,
          "people": [],
          "total": 0
        },
        "total_monthly_obligation": 933.33
      }
    }
  }
}
```

### AG-03 → AG-04 Handoff

```json
{
  "handoff": {
    "from_agent": "AG-03",
    "to_agent": "AG-04",
    "context": {
      "transactions": [...],
      "debt_analysis": {...},
      "patterns": [
        {
          "type": "HIDDEN_COST",
          "name": "Daily Toll",
          "impact": 384.00,
          "confidence": 0.95
        },
        {
          "type": "TEMPORAL",
          "name": "Weekend Surge",
          "impact": 472.00,
          "confidence": 0.88
        }
      ],
      "hidden_cost_total": 627.00
    }
  }
}
```

### AG-04 → AG-06 Handoff

```json
{
  "handoff": {
    "from_agent": "AG-04",
    "to_agent": "AG-06",
    "context": {
      "transactions": [...],
      "debt_analysis": {...},
      "patterns": [...],
      "prediction": {
        "total_predicted": 4850.00,
        "confidence_interval": {
          "low": 4200.00,
          "high": 5500.00
        },
        "by_category": [
          {"category": "FOOD", "predicted": 980.00, "trend": "RISING"}
        ]
      }
    }
  }
}
```

---

## Query Agent Delegation

AG-05 (Query Agent) can delegate to other agents:

### Delegation Request Format

```json
{
  "delegation": {
    "from_agent": "AG-05",
    "to_agent": "AG-04",
    "user_question": "What will I spend next month?",
    "context": {
      "user_id": "user_123",
      "date_range": {
        "start": "2025-10-01",
        "end": "2026-01-10"
      },
      "transactions": [...],
      "patterns": [...cached...]
    }
  }
}
```

### Delegation Response Format

```json
{
  "delegation_response": {
    "from_agent": "AG-04",
    "to_agent": "AG-05",
    "result": {
      "total_predicted": 4850.00,
      "confidence_interval": {...},
      "by_category": [...]
    },
    "should_transform": true,
    "transform_hint": "Convert to natural language answer"
  }
}
```

AG-05 then transforms the structured response into a conversational answer.

---

## Error Handoffs

When an agent fails, it passes an error handoff:

```json
{
  "handoff": {
    "from_agent": "AG-03",
    "to_agent": "ORCHESTRATOR",
    "status": "ERROR",
    "error": {
      "code": "INSUFFICIENT_DATA",
      "message": "Less than 30 days of data, cannot analyze patterns",
      "recoverable": true,
      "fallback_action": "SKIP_AGENT"
    },
    "partial_result": null
  }
}
```

### Error Recovery Options

| Error Type | Recovery Action |
|------------|-----------------|
| `INSUFFICIENT_DATA` | Skip agent, continue pipeline |
| `API_TIMEOUT` | Retry up to 2 times |
| `INVALID_INPUT` | Return validation error to user |
| `RATE_LIMITED` | Queue for later, return partial result |

---

## Context Size Limits

To prevent context overflow:

| Agent | Max Context Size |
|-------|------------------|
| AG-01 | 50 transactions per batch |
| AG-02 | Full categorized output |
| AG-03 | Last 6 months of transactions |
| AG-04 | Last 6 months + patterns |
| AG-05 | As needed for query |
| AG-06 | Summary data only (not full transactions) |

### Context Compression

For AG-06, compress transaction data:

```json
// Instead of full transactions:
{
  "monthly_summaries": [
    {"month": "2025-10", "total": 3500, "by_category": {...}},
    {"month": "2025-11", "total": 3800, "by_category": {...}},
    {"month": "2025-12", "total": 4200, "by_category": {...}}
  ]
}
```

---

## Handoff Logging

Every handoff is logged for debugging and audit:

```json
{
  "log_entry": {
    "timestamp": "2026-01-10T10:30:00Z",
    "session_id": "sess_abc123",
    "handoff_id": "ho_xyz789",
    "from_agent": "AG-01",
    "to_agent": "AG-02",
    "context_size_bytes": 45678,
    "latency_ms": 1250,
    "status": "SUCCESS"
  }
}
```

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
