# Feature Specification: Claude Agent System

> Detailed specification for the 6-agent AI architecture

**Version**: 1.0
**Status**: Approved
**Last Updated**: 2026-01-10

---

## Overview

RinggitSense employs a **six-agent architecture** where each Claude agent has a single, well-defined responsibility. This design ensures:

1. **Separation of concerns**: No agent tries to do too much
2. **Testability**: Each agent can be tested independently
3. **Maintainability**: Changes to one agent don't affect others
4. **Cost optimization**: Right-sized model for each task

---

## Agent Registry

| ID | Agent Name | Primary Function | Model | Temperature |
|----|------------|------------------|-------|-------------|
| AG-01 | Categorizer | Classify transactions | claude-sonnet-4-20250514 | 0.2 |
| AG-02 | Debt Detector | Identify debt obligations | claude-sonnet-4-20250514 | 0.1 |
| AG-03 | Pattern Analyzer | Discover spending patterns | claude-sonnet-4-20250514 | 0.5 |
| AG-04 | Predictor | Forecast future spending | claude-sonnet-4-20250514 | 0.3 |
| AG-05 | Query Agent | Answer natural language questions | claude-sonnet-4-20250514 | 0.7 |
| AG-06 | Advisor | Provide financial guidance | claude-sonnet-4-20250514 | 0.6 |

---

## Agent Specifications

### AG-01: Categorizer Agent

**Purpose**: Analyze transaction descriptions and assign the most appropriate spending category.

#### Scope

| In Scope | Out of Scope |
|----------|--------------|
| Category assignment | Providing financial advice |
| Confidence scoring | Detecting debt patterns |
| Merchant identification | Predicting future spending |
| Subcategory detection | Answering user questions |

#### Input Schema

```json
{
  "description": "string - Transaction description from bank/e-wallet",
  "amount": "number - Transaction amount in RM",
  "source": "string - Source bank or e-wallet (RHB, Maybank, T&G, etc.)",
  "date": "string - Transaction date in ISO format",
  "comment": "string? - Optional user comment"
}
```

#### Output Schema

```json
{
  "category": "enum - FOOD|TRANSPORT|BILLS|ENTERTAINMENT|SHOPPING|TRANSFER|DEBT_PAYMENT|INCOME|HEALTHCARE|OTHER",
  "confidence": "number - 0.0 to 1.0",
  "subcategory": "string? - Optional specific type (e.g., 'toll', 'restaurant')",
  "merchant_name": "string? - Extracted merchant if identifiable",
  "reasoning": "string - Brief explanation for debugging"
}
```

#### Malaysian Context

Must recognize:
- Local merchants: Mamak Hj Syed, Restoran Syed, kedai runcit
- E-wallets: Touch 'n Go (TnG, T&G), GrabPay, ShopeePay, Boost
- Toll plazas: PLUS, LDP, DUKE, SMART, AKLEH, KESAS, MEX, NPE
- BNPL indicators: SPayLater, GrabPayLater, Atome
- Common terms: "Makan", "Minum", "Bayar", "Topup", "Reload"

#### Quality Criteria

- [ ] >95% accuracy on test dataset
- [ ] Processes single transaction in <500ms
- [ ] Handles batch of 100 transactions in <10s
- [ ] Confidence below 0.7 flags for user review

---

### AG-02: Debt Detector Agent

**Purpose**: Identify debt-related transactions and classify into three tiers.

#### Scope

| In Scope | Out of Scope |
|----------|--------------|
| FORMAL debt detection | Transaction categorization |
| BNPL installment detection | Pattern analysis |
| HUTANG pattern identification | Financial advice |
| Debt provider identification | Spending prediction |

#### Debt Tiers

| Tier | Definition | Detection Signals |
|------|------------|-------------------|
| **FORMAL** | Bank/institution loans | PTPTN, HP, PERSONAL LOAN, MORTGAGE, CC PAYMENT |
| **BNPL** | Buy Now Pay Later | SPAYLATER, GRABPAYLATER, ATOME, installment patterns |
| **HUTANG** | Informal debts | Transfers to individuals with debt keywords in comments |

#### Input Schema

```json
{
  "description": "string - Transaction description",
  "amount": "number - Transaction amount in RM",
  "source": "string - Source bank or e-wallet",
  "is_recurring": "boolean - Whether amount recurs monthly",
  "comment": "string? - User's comment on transaction",
  "similar_transactions": "array? - Other transactions to same recipient"
}
```

#### Output Schema

```json
{
  "is_debt_related": "boolean",
  "debt_tier": "enum? - FORMAL|BNPL|HUTANG",
  "debt_type": "string? - Specific debt type (education_loan, installment, etc.)",
  "provider": "string? - Lender/platform name",
  "confidence": "number - 0.0 to 1.0",
  "indicators": "array - List of detection reasons",
  "estimated_monthly": "number? - Estimated monthly payment if detectable",
  "person_name": "string? - For HUTANG, the person involved"
}
```

#### Quality Criteria

- [ ] >90% recall on debt detection (catch all debts)
- [ ] >85% precision (minimize false positives)
- [ ] Correctly identifies all three tiers
- [ ] Extracts provider name when present

---

### AG-03: Pattern Analyzer Agent

**Purpose**: Discover hidden patterns, trends, and anomalies in spending data.

#### Scope

| In Scope | Out of Scope |
|----------|--------------|
| Temporal pattern detection | Real-time monitoring |
| Lifestyle bundle identification | Individual transaction categorization |
| Hidden cost aggregation | Financial advice generation |
| Anomaly detection | Debt tracking |
| Festival spending patterns | Prediction |

#### Pattern Types

| Type | Examples |
|------|----------|
| **Temporal** | Weekend spending surge, payday effects, month-end squeeze |
| **Lifestyle Bundles** | Night out (entertainment + food + transport), commute (toll + petrol + food) |
| **Hidden Costs** | Toll aggregation, subscription accumulation, delivery fees |
| **Trends** | Rising/declining category spending month-over-month |
| **Anomalies** | Unusual spending spikes, new merchants, category outliers |

#### Input Schema

```json
{
  "transactions": "array - All transactions in analysis period",
  "period": "string - Analysis period (e.g., '3_months', '6_months')",
  "focus_areas": "array? - Specific patterns to look for"
}
```

#### Output Schema

```json
{
  "patterns": [
    {
      "type": "enum - TEMPORAL|BUNDLE|HIDDEN_COST|TREND|ANOMALY",
      "name": "string - Pattern name",
      "description": "string - What this pattern means",
      "evidence": "array - Transactions supporting this pattern",
      "impact": "number - Estimated RM impact",
      "confidence": "number - 0.0 to 1.0"
    }
  ],
  "summary": "string - Overall pattern summary",
  "hidden_cost_total": "number - Total hidden costs identified"
}
```

#### Quality Criteria

- [ ] Identifies at least 3 patterns per month of data
- [ ] Hidden cost calculation within 10% of actual
- [ ] Analysis completes in <3 seconds
- [ ] Patterns are actionable, not just interesting

---

### AG-04: Predictor Agent

**Purpose**: Forecast next-month spending based on historical patterns.

#### Scope

| In Scope | Out of Scope |
|----------|--------------|
| Total spending prediction | Pattern discovery |
| Category-level forecasts | Transaction categorization |
| Confidence intervals | Debt detection |
| Trend consideration | Financial advice |

#### Prediction Methodology

1. **Historical baseline**: Average of last 3 months
2. **Trend adjustment**: Account for rising/falling patterns
3. **Seasonal adjustment**: Festival periods, year-end
4. **Known events**: Upcoming bills, expected income

#### Input Schema

```json
{
  "historical_transactions": "array - Past 3-6 months of transactions",
  "known_upcoming": "array? - Known future transactions (bills, salary)",
  "prediction_month": "string - Month to predict (ISO format)"
}
```

#### Output Schema

```json
{
  "total_predicted": "number - Total predicted spending in RM",
  "confidence_interval": {
    "low": "number - Lower bound (90% confidence)",
    "high": "number - Upper bound (90% confidence)"
  },
  "by_category": [
    {
      "category": "string",
      "predicted": "number",
      "trend": "enum - RISING|STABLE|FALLING"
    }
  ],
  "assumptions": "array - Key assumptions made",
  "risks": "array - Factors that could change prediction"
}
```

#### Quality Criteria

- [ ] Within 15% of actual spending (measured post-month)
- [ ] Prediction generated in <3 seconds
- [ ] Confidence interval covers actual 90% of time
- [ ] Category predictions rank-ordered correctly

---

### AG-05: Query Agent

**Purpose**: Answer natural language questions about the user's finances.

#### Scope

| In Scope | Out of Scope |
|----------|--------------|
| Answering spending questions | Modifying data |
| Retrieving specific data | Making transactions |
| Summarizing trends | Providing financial advice |
| Explaining patterns | Predicting future |

#### Supported Query Types

| Type | Examples |
|------|----------|
| **Aggregation** | "How much did I spend on food in December?" |
| **Comparison** | "Is my spending higher this month than last?" |
| **Ranking** | "What are my top 3 expenses?" |
| **Search** | "Show me all Shopee transactions" |
| **Trend** | "How has my toll spending changed?" |

#### Input Schema

```json
{
  "question": "string - Natural language question",
  "context": {
    "transactions": "array - Relevant transactions",
    "patterns": "object? - Pre-computed patterns",
    "date_range": "object - Current date range in view"
  }
}
```

#### Output Schema

```json
{
  "answer": "string - Natural language answer",
  "data": "object? - Structured data supporting answer",
  "visualization_hint": "string? - Suggested chart type",
  "follow_up_questions": "array? - Related questions user might ask"
}
```

#### Quality Criteria

- [ ] Correctly interprets 90%+ of supported query types
- [ ] Response in <2 seconds
- [ ] Graceful handling of unsupported questions
- [ ] Conversational, not robotic tone

---

### AG-06: Advisor Agent

**Purpose**: Provide personalized, actionable financial guidance.

#### Scope

| In Scope | Out of Scope |
|----------|--------------|
| Personalized recommendations | Investment advice |
| Actionable suggestions | Tax advice |
| Culturally-aware guidance | Specific product recommendations |
| Prioritized advice | Predictions |

#### Advice Categories

| Category | Focus |
|----------|-------|
| **Spending** | Cut unnecessary expenses |
| **Saving** | Build emergency fund |
| **Debt** | Payoff prioritization |
| **Budgeting** | Allocation recommendations |
| **Behavior** | Habit changes |

#### Mandatory Disclaimers

Every advice response MUST include:
1. "This is not professional financial advice"
2. "Consult a licensed financial advisor for major decisions"
3. "Past patterns do not guarantee future results"

#### Input Schema

```json
{
  "user_profile": {
    "income": "number - Monthly income",
    "fixed_expenses": "number - Fixed monthly expenses",
    "debt_total": "number - Total debt obligation"
  },
  "patterns": "object - Identified spending patterns",
  "debt_summary": "object - Debt by tier",
  "goals": "array? - User-defined financial goals"
}
```

#### Output Schema

```json
{
  "recommendations": [
    {
      "priority": "number - 1 (highest) to 5 (lowest)",
      "category": "enum - SPENDING|SAVING|DEBT|BUDGETING|BEHAVIOR",
      "title": "string - Short recommendation title",
      "description": "string - Detailed explanation",
      "potential_impact": "number - Estimated RM impact per month",
      "difficulty": "enum - EASY|MEDIUM|HARD",
      "action_steps": "array - Specific steps to take"
    }
  ],
  "disclaimer": "string - Mandatory disclaimer text",
  "overall_assessment": "string - Summary of financial health"
}
```

#### Quality Criteria

- [ ] All advice includes disclaimer
- [ ] Recommendations are specific, not generic
- [ ] Respects cultural context (family obligations)
- [ ] Prioritized by potential impact
- [ ] Actionable within user's control

---

## Orchestration Patterns

### Sequential Pipeline

For new statement uploads:

```
Transaction Upload
    │
    ▼
┌─────────────────┐
│   Categorizer   │ ── Each transaction categorized
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Debt Detector  │ ── Debt transactions identified
└─────────────────┘
    │
    ▼
┌─────────────────┐
│Pattern Analyzer │ ── Patterns discovered
└─────────────────┘
    │
    ▼
┌─────────────────┐
│    Predictor    │ ── Next month forecasted
└─────────────────┘
    │
    ▼
┌─────────────────┐
│    Advisor      │ ── Recommendations generated
└─────────────────┘
```

### On-Demand Query

```
User Question
    │
    ▼
┌─────────────────┐
│   Query Agent   │ ── Answer generated
└─────────────────┘
    │
    ├── May call Categorizer for "what category is X?"
    ├── May call Predictor for "what will I spend next month?"
    └── Routes to Advisor for "what should I do about X?"
```

### Routing Rules

```python
def route_request(request):
    if request.type == "UPLOAD":
        return SequentialPipeline([
            "categorizer", "debt_detector",
            "pattern_analyzer", "predictor", "advisor"
        ])

    if request.type == "QUERY":
        question = request.question.lower()

        if any(word in question for word in ["category", "categorize"]):
            return "categorizer"

        if any(word in question for word in ["debt", "loan", "owe", "hutang"]):
            return "debt_detector"

        if any(word in question for word in ["pattern", "trend", "hidden"]):
            return "pattern_analyzer"

        if any(word in question for word in ["predict", "next month", "forecast"]):
            return "predictor"

        if any(word in question for word in ["advice", "should", "recommend"]):
            return "advisor"

        # Default to query agent
        return "query_agent"
```

---

## Cost Optimization

### Token Management

| Agent | Avg Input Tokens | Avg Output Tokens | Cost per Call |
|-------|------------------|-------------------|---------------|
| Categorizer | 200 | 100 | ~$0.001 |
| Debt Detector | 300 | 150 | ~$0.001 |
| Pattern Analyzer | 5000 | 1000 | ~$0.02 |
| Predictor | 3000 | 500 | ~$0.01 |
| Query Agent | 500 | 300 | ~$0.003 |
| Advisor | 2000 | 800 | ~$0.01 |

### Optimization Strategies

1. **Batch categorization**: Process 50 transactions per call
2. **Cache patterns**: Don't re-analyze unchanged data
3. **Limit history**: Use last 6 months, not full history
4. **Progressive disclosure**: Only run Advisor on user request

---

## Error Handling

### Fallback Rules

| Agent | Fallback Behavior |
|-------|-------------------|
| Categorizer | Return "OTHER" with low confidence |
| Debt Detector | Return is_debt_related: false |
| Pattern Analyzer | Return empty patterns array |
| Predictor | Use simple historical average |
| Query Agent | "I couldn't understand that question" |
| Advisor | Generic advice with disclaimer |

### Retry Policy

- Max 2 retries with exponential backoff
- Circuit breaker after 5 consecutive failures
- Graceful degradation: show cached data

---

## Testing Requirements

### Per-Agent Test Coverage

| Agent | Unit Tests | Golden Dataset | Adversarial |
|-------|------------|----------------|-------------|
| Categorizer | 50+ cases | 500 transactions | Edge cases |
| Debt Detector | 30+ cases | 100 debt scenarios | False positives |
| Pattern Analyzer | 20+ cases | 3-month datasets | Sparse data |
| Predictor | 20+ cases | 6-month datasets | Irregular patterns |
| Query Agent | 50+ cases | 100 questions | Malformed queries |
| Advisor | 30+ cases | 50 profiles | Edge cases |

---

**Document Status**: Complete
**Synthesized From**: 03_CLAUDE_AGENT_PROMPTS.md, Agent Architecture Prompt
