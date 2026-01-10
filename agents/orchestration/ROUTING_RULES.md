# Agent Routing Rules

> Decision logic for directing requests to the appropriate agent

**Version**: 1.0.0
**Last Updated**: 2026-01-10

---

## Overview

The RinggitSense orchestration layer uses a rule-based routing system to direct incoming requests to the appropriate specialized agent. This document defines the routing logic.

---

## Routing Decision Tree

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         INCOMING REQUEST                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │   What type of request?       │
                    └───────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │   UPLOAD      │       │    QUERY      │       │   SCHEDULED   │
    │ New statement │       │ User question │       │ Background job│
    └───────┬───────┘       └───────┬───────┘       └───────┬───────┘
            │                       │                       │
            ▼                       ▼                       ▼
    Sequential Pipeline      Intent Classification      Direct Agent
    (AG-01→02→03→04→06)           │                     Invocation
                                  │
                    ┌─────────────┴─────────────┐
                    │    Classify Question      │
                    └─────────────┬─────────────┘
                                  │
    ┌──────────┬──────────┬───────┴───────┬──────────┬──────────┐
    │          │          │               │          │          │
    ▼          ▼          ▼               ▼          ▼          ▼
 CATEGORY   DEBT      PATTERN        PREDICT    GENERAL    ADVICE
    │          │          │               │          │          │
    ▼          ▼          ▼               ▼          ▼          ▼
  AG-01      AG-02      AG-03           AG-04      AG-05      AG-06
```

---

## Request Types

### 1. UPLOAD Request

Triggered when user uploads a new bank/e-wallet statement.

**Route**: Sequential Pipeline
```
AG-01 (Categorizer)
    ↓
AG-02 (Debt Detector)
    ↓
AG-03 (Pattern Analyzer)
    ↓
AG-04 (Predictor)
    ↓
AG-06 (Advisor)
```

**Pipeline Logic**:
```python
def process_upload(transactions: List[Transaction]) -> ProcessingResult:
    # Step 1: Categorize all transactions
    categorized = await categorizer.batch_process(transactions)

    # Step 2: Detect debt transactions
    debt_analysis = await debt_detector.analyze(categorized)

    # Step 3: Discover patterns (needs 1+ months of data)
    patterns = await pattern_analyzer.analyze(
        transactions=categorized,
        period="available"
    )

    # Step 4: Generate prediction (needs 3+ months of data)
    prediction = None
    if has_sufficient_history(categorized):
        prediction = await predictor.forecast(categorized)

    # Step 5: Generate advice
    advice = await advisor.generate(
        patterns=patterns,
        debt_summary=debt_analysis,
        prediction=prediction
    )

    return ProcessingResult(
        categorized=categorized,
        debt_analysis=debt_analysis,
        patterns=patterns,
        prediction=prediction,
        advice=advice
    )
```

---

### 2. QUERY Request

Triggered when user asks a question.

**Route**: Intent Classification → Appropriate Agent

**Intent Keywords**:

| Intent | Keywords (EN) | Keywords (MY) | Route To |
|--------|--------------|---------------|----------|
| CATEGORY | "category", "categorize", "type", "what is" | "kategori", "jenis" | AG-01 |
| DEBT | "debt", "loan", "owe", "hutang", "PTPTN", "BNPL" | "hutang", "pinjam" | AG-02 |
| PATTERN | "pattern", "trend", "hidden", "bundle" | "corak", "trend" | AG-03 |
| PREDICT | "predict", "next month", "forecast", "will I" | "ramalan", "bulan depan" | AG-04 |
| ADVICE | "advice", "should", "recommend", "what to do" | "nasihat", "patut" | AG-06 |
| GENERAL | All other questions | - | AG-05 |

**Routing Logic**:
```python
def route_query(question: str) -> str:
    question_lower = question.lower()

    # Check for category intent
    if any(word in question_lower for word in ["category", "categorize", "kategorikan"]):
        return "AG-01"

    # Check for debt intent
    if any(word in question_lower for word in ["debt", "loan", "owe", "hutang", "ptptn", "bnpl"]):
        return "AG-02"

    # Check for pattern intent
    if any(word in question_lower for word in ["pattern", "trend", "hidden", "corak"]):
        return "AG-03"

    # Check for prediction intent
    if any(word in question_lower for word in ["predict", "next month", "forecast", "will i", "bulan depan"]):
        return "AG-04"

    # Check for advice intent
    if any(word in question_lower for word in ["advice", "should", "recommend", "what to do", "nasihat", "patut"]):
        return "AG-06"

    # Default to Query Agent
    return "AG-05"
```

---

### 3. SCHEDULED Request

Background jobs triggered by scheduler.

| Job Type | Trigger | Route To |
|----------|---------|----------|
| Daily Summary | 8:00 AM | AG-05 (summary generation) |
| Weekly Pattern Refresh | Monday 6:00 AM | AG-03 |
| Monthly Prediction | 1st of month | AG-04 |
| Bill Reminder | 3 days before due | AG-05 (notification) |

---

## Agent Delegation Rules

Some agents can delegate to others during processing:

### AG-05 (Query Agent) Can Delegate To:

| Scenario | Delegate To | Example |
|----------|-------------|---------|
| Prediction question | AG-04 | "What will I spend next month?" |
| Advice question | AG-06 | "Should I reduce my food spending?" |
| Debt clarification | AG-02 | "How much total debt do I have?" |
| Pattern explanation | AG-03 | "What are my hidden costs?" |

### Delegation Flow:
```
User → AG-05 → [Detects delegation needed] → AG-04/AG-06/etc → Response → AG-05 → User
```

---

## Priority Rules

When multiple agents could handle a request:

| Priority | Rule |
|----------|------|
| 1 | Explicit intent (user says "categorize") |
| 2 | Specific agent keywords |
| 3 | Question structure ("what will" → prediction) |
| 4 | Default to AG-05 (Query Agent) |

---

## Error Handling Routes

| Error Type | Handling |
|------------|----------|
| Agent timeout | Retry up to 2x, then return cached/partial result |
| Agent error | Return graceful error message, log for debugging |
| Ambiguous intent | Route to AG-05, let it clarify with user |
| No data available | Return "insufficient data" message |

---

## Rate Limiting

| Agent | Max Calls/Minute | Reason |
|-------|------------------|--------|
| AG-01 | 100 | Batch processing support |
| AG-02 | 50 | Lower volume of debt detection |
| AG-03 | 10 | Heavy analysis |
| AG-04 | 20 | Moderate complexity |
| AG-05 | 60 | High user interaction |
| AG-06 | 30 | Thoughtful advice generation |

---

## Routing Metrics

Track these metrics for routing optimization:

| Metric | Description |
|--------|-------------|
| `route_accuracy` | % of correctly routed requests |
| `delegation_rate` | % of AG-05 requests that delegate |
| `avg_latency_by_route` | Average response time per route |
| `fallback_rate` | % of requests falling back to AG-05 |

---

## Implementation Notes

### FastAPI Router Example

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/agent")

class QueryRequest(BaseModel):
    question: str
    context: dict = {}

@router.post("/query")
async def handle_query(request: QueryRequest):
    # Determine route
    agent_id = route_query(request.question)

    # Get agent instance
    agent = get_agent(agent_id)

    # Process request
    result = await agent.process(request.question, request.context)

    # Check for delegation
    if result.routed_to:
        delegate_agent = get_agent(result.routed_to)
        result = await delegate_agent.process(request.question, request.context)

    return result
```

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
