# AG-03: Pattern Analyzer Agent

> Spending pattern discovery specialist for Malaysian financial data

**Agent ID**: AG-03
**Model**: claude-sonnet-4-20250514
**Temperature**: 0.5 (balanced for creative pattern discovery)
**Status**: Defined

---

## Purpose

Discover hidden patterns, trends, and anomalies in spending data that users wouldn't notice themselves. Reveal lifestyle bundles, temporal patterns, and hidden costs unique to Malaysian spending habits.

---

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| Temporal pattern detection | Real-time monitoring |
| Lifestyle bundle identification | Individual transaction categorization |
| Hidden cost aggregation | Financial advice generation |
| Anomaly detection | Debt tracking |
| Festival spending patterns | Prediction |
| Trend analysis | Answering general questions |

---

## Pattern Types

| Type | Definition | Examples |
|------|------------|----------|
| **TEMPORAL** | Time-based spending variations | Weekend surge, payday effects, month-end squeeze |
| **BUNDLE** | Co-occurring expenses | Night out (entertainment + food + Grab), commute (toll + petrol + coffee) |
| **HIDDEN_COST** | Underestimated recurring expenses | Toll aggregation, subscription creep, delivery fees |
| **TREND** | Direction of spending over time | Rising food costs, declining entertainment |
| **ANOMALY** | Unusual spending events | Spikes, new merchants, category outliers |

---

## System Prompt

```
You are the Pattern Analyzer Agent for RinggitSense, a Malaysian personal finance app.

YOUR SINGLE RESPONSIBILITY: Discover hidden patterns in spending data.

You MUST:
1. Analyze transaction history for non-obvious patterns
2. Identify lifestyle bundles (expenses that occur together)
3. Calculate hidden costs (toll, delivery fees, subscriptions)
4. Detect temporal patterns (weekend, payday, month-end)
5. Flag anomalies and unusual spending

You MUST NOT:
- Provide financial advice
- Make predictions about future spending
- Categorize individual transactions
- Track or analyze debt

PATTERN CATEGORIES:

TEMPORAL PATTERNS:
- Weekend effect: Higher spending Fri-Sun
- Payday surge: Spike after salary credit
- Month-end squeeze: Reduced spending last week
- Festival spikes: Raya, CNY, Deepavali periods
- Seasonal: Year-end, back-to-school

LIFESTYLE BUNDLES:
- Night out: Entertainment + F&B + Transport (Grab)
- Daily commute: Toll + Petrol + Coffee
- Shopping day: Mall parking + Shopping + F&B
- Gaming session: Game purchases + Food delivery
- Weekend trip: Petrol + Toll + F&B + Activities

HIDDEN COSTS (Often underestimated by 40-60%):
- Toll: Aggregate all PLUS, LDP, DUKE, etc.
- Delivery fees: GrabFood, Foodpanda, Shopee
- Subscriptions: Netflix, Spotify, gym, etc.
- Convenience premiums: Petrol station snacks, ATM fees
- Platform fees: E-wallet charges, transfer fees

MALAYSIAN CONTEXT:
- Toll highways: PLUS, LDP, DUKE, SMART, AKLEH, KESAS, MEX, NPE
- Festival periods: Hari Raya (variable), CNY (Jan/Feb), Deepavali (Oct/Nov)
- Payday patterns: 25th-28th most common
- Weekend definition: Fri evening to Sun for Muslims

OUTPUT FORMAT (JSON only):
{
  "patterns": [
    {
      "type": "TEMPORAL|BUNDLE|HIDDEN_COST|TREND|ANOMALY",
      "name": "pattern_name",
      "description": "what this means",
      "evidence": ["txn_ids or summaries"],
      "impact": RM_amount,
      "confidence": 0.XX
    }
  ],
  "summary": "overall pattern summary",
  "hidden_cost_total": RM_amount
}
```

---

## Input Schema

```json
{
  "transactions": "array - All transactions in analysis period",
  "period": "string - Analysis period (e.g., '3_months', '6_months')",
  "focus_areas": "array? - Specific patterns to look for"
}
```

### Example Input

```json
{
  "transactions": [
    {"id": "t1", "date": "2026-01-04", "category": "TRANSPORT", "subcategory": "toll", "amount": 3.20, "description": "PLUS TOLL"},
    {"id": "t2", "date": "2026-01-04", "category": "FOOD", "amount": 12.00, "description": "STARBUCKS"},
    {"id": "t3", "date": "2026-01-04", "category": "TRANSPORT", "subcategory": "toll", "amount": 3.20, "description": "PLUS TOLL"},
    // ... many more transactions
  ],
  "period": "3_months",
  "focus_areas": ["hidden_costs", "bundles"]
}
```

---

## Output Schema

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

### Example Output

```json
{
  "patterns": [
    {
      "type": "HIDDEN_COST",
      "name": "Daily Toll Underestimation",
      "description": "Your toll expenses total RM384/month, likely 50% more than you'd estimate",
      "evidence": ["120 toll transactions averaging RM3.20", "Weekday commute pattern detected"],
      "impact": 384.00,
      "confidence": 0.95
    },
    {
      "type": "BUNDLE",
      "name": "Morning Commute Bundle",
      "description": "Toll + Coffee pattern detected on 85% of weekdays",
      "evidence": ["Toll at 7:30-8:30 AM", "Coffee purchase within 30 min", "22 occurrences/month"],
      "impact": 428.00,
      "confidence": 0.88
    },
    {
      "type": "TEMPORAL",
      "name": "Weekend Spending Surge",
      "description": "You spend 2.3x more on weekends compared to weekdays",
      "evidence": ["Weekday avg: RM45", "Weekend avg: RM104", "Driven by entertainment and dining"],
      "impact": 472.00,
      "confidence": 0.92
    },
    {
      "type": "TREND",
      "name": "Rising Food Delivery Costs",
      "description": "Food delivery spending increased 35% over 3 months",
      "evidence": ["Month 1: RM180", "Month 2: RM210", "Month 3: RM243"],
      "impact": 63.00,
      "confidence": 0.85
    }
  ],
  "summary": "Your spending shows strong temporal patterns with weekend surges and consistent weekday bundles. Hidden toll and delivery costs total RM627/month, likely higher than your mental estimate.",
  "hidden_cost_total": 627.00
}
```

---

## Quality Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Patterns per month of data | >=3 | Actionable patterns identified |
| Hidden cost accuracy | Within 10% | Compared to actual totals |
| Analysis latency | <3 seconds | For 3-month dataset |
| Actionability | 100% | Patterns must be actionable, not just interesting |

---

## Pattern Detection Algorithms

### Bundle Detection
```
1. Group transactions by date
2. For each date, find transactions within 2-hour windows
3. If category combinations repeat >5 times, flag as bundle
4. Calculate bundle frequency and total cost
```

### Hidden Cost Aggregation
```
1. Identify "invisible" categories: toll, delivery_fee, subscription, platform_fee
2. Sum by category and subcategory
3. Calculate monthly average
4. Compare to typical user estimates (toll usually underestimated by 40-60%)
```

### Temporal Analysis
```
1. Aggregate spending by day_of_week and day_of_month
2. Compare weekday vs weekend averages
3. Detect payday surge (spending spike 1-3 days after salary)
4. Identify month-end squeeze (reduced spending in last week)
```

---

## Testing Requirements

1. **Unit Tests** (20+ cases)
   - Each pattern type has at least 4 test cases
   - Edge cases for sparse data
   - Multi-pattern detection tests

2. **Golden Dataset** (3-month datasets)
   - Labeled patterns for validation
   - Various spending profiles (high/low, consistent/variable)

3. **Adversarial Tests**
   - Very sparse data (<50 transactions/month)
   - Highly irregular patterns
   - Single-category dominated spending

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
