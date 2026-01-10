# AG-04: Predictor Agent

> Spending forecast specialist for Malaysian financial data

**Agent ID**: AG-04
**Model**: claude-sonnet-4-20250514
**Temperature**: 0.3 (low-moderate for consistent predictions)
**Status**: Defined

---

## Purpose

Forecast next-month spending based on historical patterns, trends, and known upcoming events. Provide confidence intervals and category-level breakdowns specific to Malaysian spending contexts.

---

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Total spending prediction | Pattern discovery |
| Category-level forecasts | Transaction categorization |
| Confidence intervals | Debt detection |
| Trend consideration | Financial advice |
| Seasonal adjustment | Answering general questions |
| Known event incorporation | Modifying data |

---

## Prediction Methodology

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREDICTION PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  HISTORICAL  │───>│    TREND     │───>│  SEASONAL    │     │
│  │   BASELINE   │    │  ADJUSTMENT  │    │  ADJUSTMENT  │     │
│  │              │    │              │    │              │     │
│  │ Avg of last  │    │ Rising or    │    │ Festival,    │     │
│  │ 3 months     │    │ falling      │    │ year-end     │     │
│  └──────────────┘    └──────────────┘    └──────────────┘     │
│                                                   │             │
│                                                   ▼             │
│                              ┌──────────────┐                  │
│                              │    KNOWN     │                  │
│                              │    EVENTS    │                  │
│                              │              │                  │
│                              │ Bills, salary│                  │
│                              │ due dates    │                  │
│                              └──────┬───────┘                  │
│                                     │                          │
│                                     ▼                          │
│                              ┌──────────────┐                  │
│                              │   FINAL      │                  │
│                              │  PREDICTION  │                  │
│                              │  + Confidence│                  │
│                              └──────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Prompt

```
You are the Predictor Agent for RinggitSense, a Malaysian personal finance app.

YOUR SINGLE RESPONSIBILITY: Forecast next-month spending.

You MUST:
1. Calculate historical baseline from last 3-6 months
2. Apply trend adjustments for rising/falling patterns
3. Account for seasonal factors (festivals, year-end)
4. Incorporate known upcoming events
5. Provide confidence intervals (90%)
6. Break down by category

You MUST NOT:
- Provide financial advice
- Discover patterns (that's Pattern Analyzer's job)
- Categorize transactions
- Detect or comment on debt

PREDICTION FACTORS:

HISTORICAL BASELINE:
- Primary: Weighted average of last 3 months (recent months weighted higher)
- Fallback: Simple average if <3 months data
- By category: Calculate baseline per spending category

TREND ADJUSTMENT:
- RISING: If 3-month trend shows >10% increase, add 5% to prediction
- FALLING: If 3-month trend shows >10% decrease, reduce by 5%
- STABLE: No adjustment needed

SEASONAL FACTORS (Malaysian calendar):
- Hari Raya period: +30-50% (variable date, check Islamic calendar)
- Chinese New Year (Jan/Feb): +25-40% for relevant spending
- Deepavali (Oct/Nov): +15-25%
- Year-end (Dec): +20-30% (holidays, bonuses spent)
- Back-to-school (Jan): +10-20% for families
- Mid-year sales (June/July): +15-25% shopping

KNOWN EVENTS:
- Regular bills: Include at known amounts
- Salary: Include as income
- Annual payments: Insurance, road tax, etc.
- User-flagged events: Weddings, travel, etc.

CONFIDENCE INTERVALS:
- Calculate standard deviation from historical data
- 90% confidence = prediction ± 1.645 × std_dev
- Wider interval for shorter history or high variance

OUTPUT FORMAT (JSON only):
{
  "total_predicted": RM_amount,
  "confidence_interval": {"low": RM, "high": RM},
  "by_category": [
    {"category": "NAME", "predicted": RM, "trend": "RISING|STABLE|FALLING"}
  ],
  "assumptions": ["list of assumptions"],
  "risks": ["factors that could change prediction"]
}
```

---

## Input Schema

```json
{
  "historical_transactions": "array - Past 3-6 months of transactions",
  "known_upcoming": "array? - Known future transactions (bills, salary)",
  "prediction_month": "string - Month to predict (ISO format)"
}
```

### Example Input

```json
{
  "historical_transactions": [
    // Last 3 months of categorized transactions
    {"month": "2025-10", "category": "FOOD", "total": 850.00},
    {"month": "2025-10", "category": "TRANSPORT", "total": 420.00},
    {"month": "2025-11", "category": "FOOD", "total": 920.00},
    {"month": "2025-11", "category": "TRANSPORT", "total": 450.00},
    {"month": "2025-12", "category": "FOOD", "total": 1100.00},
    {"month": "2025-12", "category": "TRANSPORT", "total": 380.00}
    // ... more categories
  ],
  "known_upcoming": [
    {"type": "bill", "name": "Car Insurance", "amount": 1200.00, "date": "2026-01-15"},
    {"type": "income", "name": "Salary", "amount": 4500.00, "date": "2026-01-25"}
  ],
  "prediction_month": "2026-01"
}
```

---

## Output Schema

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

### Example Output

```json
{
  "total_predicted": 4850.00,
  "confidence_interval": {
    "low": 4200.00,
    "high": 5500.00
  },
  "by_category": [
    {"category": "FOOD", "predicted": 980.00, "trend": "RISING"},
    {"category": "TRANSPORT", "predicted": 420.00, "trend": "STABLE"},
    {"category": "BILLS", "predicted": 1650.00, "trend": "STABLE"},
    {"category": "SHOPPING", "predicted": 600.00, "trend": "FALLING"},
    {"category": "ENTERTAINMENT", "predicted": 200.00, "trend": "STABLE"},
    {"category": "DEBT_PAYMENT", "predicted": 800.00, "trend": "STABLE"},
    {"category": "OTHER", "predicted": 200.00, "trend": "STABLE"}
  ],
  "assumptions": [
    "Based on 3-month historical average",
    "Food trend adjusted +8% for rising pattern",
    "Car insurance RM1,200 included in BILLS",
    "No festival adjustment for January 2026"
  ],
  "risks": [
    "CNY may fall in late January (check exact date)",
    "Year-end spending hangover may reduce January spending",
    "Salary timing affects month-end behavior"
  ]
}
```

---

## Quality Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Prediction accuracy | Within 15% of actual | Measured post-month |
| Generation latency | <3 seconds | API response time |
| Confidence interval coverage | 90% | Actual falls within interval 90% of time |
| Category rank accuracy | Top 3 correct | Categories ranked by predicted spend |

---

## Calculation Examples

### Historical Baseline
```
Given: Oct=RM3500, Nov=RM3800, Dec=RM4200
Weights: 0.2, 0.3, 0.5 (recent months weighted higher)
Baseline = (3500×0.2) + (3800×0.3) + (4200×0.5) = RM3940
```

### Trend Adjustment
```
Oct→Nov change: +8.6%
Nov→Dec change: +10.5%
Average trend: +9.5% (close to 10% threshold)
Adjustment: +5% applied
Adjusted baseline: RM3940 × 1.05 = RM4137
```

### Confidence Interval
```
Historical values: [3500, 3800, 4200]
Std dev: 350
90% CI = 4137 ± (1.645 × 350) = RM3563 to RM4711
```

---

## Edge Cases

| Scenario | Handling |
|----------|----------|
| <3 months history | Use available data, widen confidence interval |
| Single category dominates | Predict that category separately |
| High variance month | Note in risks, widen interval |
| Festival month | Apply festival multiplier |
| New user | Cannot predict, return error with minimum data requirements |

---

## Testing Requirements

1. **Unit Tests** (20+ cases)
   - Baseline calculation tests
   - Trend detection tests
   - Seasonal adjustment tests
   - Confidence interval tests

2. **Golden Dataset** (6-month datasets)
   - Known outcomes for validation
   - Various spending profiles
   - Festival periods included

3. **Adversarial Tests**
   - Highly irregular spending
   - Missing months
   - Single large transaction skewing average

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
