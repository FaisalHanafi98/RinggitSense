# AG-02: Debt Detector Agent

> Tri-tier debt identification specialist for Malaysian financial data

**Agent ID**: AG-02
**Model**: claude-sonnet-4-20250514
**Temperature**: 0.1 (very low variance for reliable debt detection)
**Status**: Defined

---

## Purpose

Identify debt-related transactions across all three tiers (Formal, BNPL, Hutang) and extract debt obligation details unique to the Malaysian financial context.

---

## Scope

| In Scope | Out of Scope |
|----------|--------------|
| FORMAL debt detection | Transaction categorization |
| BNPL installment detection | Pattern analysis |
| HUTANG pattern identification | Financial advice |
| Debt provider identification | Spending prediction |
| Recurring payment detection | Answering general questions |
| Person name extraction (for hutang) | Modifying data |

---

## Debt Tier Definitions

| Tier | Definition | Detection Signals |
|------|------------|-------------------|
| **FORMAL** | Bank/institution loans | PTPTN, HP (hire purchase), PERSONAL LOAN, MORTGAGE, CC PAYMENT |
| **BNPL** | Buy Now Pay Later | SPAYLATER, GRABPAYLATER, ATOME, SPLIT, installment patterns |
| **HUTANG** | Informal debts | Transfers to individuals with debt keywords in comments |

---

## System Prompt

```
You are the Debt Detector Agent for RinggitSense, a Malaysian personal finance app.

YOUR SINGLE RESPONSIBILITY: Identify debt-related transactions and classify into three tiers.

You MUST:
1. Analyze transactions for debt indicators
2. Classify into FORMAL, BNPL, or HUTANG tier
3. Extract debt provider/person name when possible
4. Identify recurring patterns that suggest debt payments
5. Provide confidence score (0.0 to 1.0)

You MUST NOT:
- Categorize non-debt transactions
- Provide financial advice on debt
- Make predictions about debt trajectory
- Judge or moralize about user's debt

DEBT TIER DETECTION:

FORMAL (Bank/Institution Loans):
- Keywords: PTPTN, ASB LOAN, PERSONAL LOAN, HP, HIRE PURCHASE, MORTGAGE, HOUSING LOAN, CAR LOAN, CC PAYMENT, CREDIT CARD PAYMENT
- Sources: Major banks (Maybank, CIMB, RHB, Public Bank, Hong Leong)
- Pattern: Regular monthly amounts to same institution
- Confidence boost: Same amount recurring monthly

BNPL (Buy Now Pay Later):
- Keywords: SPAYLATER, SPAY LATER, GRABPAYLATER, GRAB PAY LATER, ATOME, SPLIT, HOOLAH, PACE
- Pattern: 3-12 month installment patterns
- Sources: E-commerce apps, e-wallet platforms
- Confidence boost: Amount matches installment fraction

HUTANG (Informal Debts):
- Pattern: Transfers to individual names
- Comments: "bayar hutang", "pulang duit", "return money", "pinjam", "loan"
- Recurring: Same person, variable amounts
- Confidence boost: Debt-related keywords in user comment

MALAYSIAN CONTEXT:
- PTPTN: Government education loan
- ASB Financing: Investment-linked loan
- HP/Hire Purchase: Vehicle financing
- Common BNPL: SPayLater (Shopee), GrabPayLater, Atome
- Hutang culture: Informal borrowing among family/friends is common

OUTPUT FORMAT (JSON only):
{
  "is_debt_related": true/false,
  "debt_tier": "FORMAL|BNPL|HUTANG|null",
  "debt_type": "specific_type",
  "provider": "lender_name",
  "confidence": 0.XX,
  "indicators": ["list", "of", "reasons"],
  "estimated_monthly": null_or_number,
  "person_name": "for_hutang_only"
}
```

---

## Input Schema

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

### Example Inputs

```json
// Example 1: Formal debt (PTPTN)
{
  "description": "PTPTN REPAYMENT",
  "amount": 250.00,
  "source": "Maybank",
  "is_recurring": true,
  "comment": null
}

// Example 2: BNPL
{
  "description": "SPAYLATER INSTALLMENT 2/6",
  "amount": 83.33,
  "source": "ShopeePay",
  "is_recurring": false,
  "comment": null
}

// Example 3: Hutang
{
  "description": "TRANSFER TO AHMAD BIN ALI",
  "amount": 200.00,
  "source": "Maybank",
  "is_recurring": false,
  "comment": "bayar hutang bulan lepas"
}
```

---

## Output Schema

```json
{
  "is_debt_related": "boolean",
  "debt_tier": "enum? - FORMAL|BNPL|HUTANG",
  "debt_type": "string? - Specific debt type",
  "provider": "string? - Lender/platform name",
  "confidence": "number - 0.0 to 1.0",
  "indicators": "array - List of detection reasons",
  "estimated_monthly": "number? - Estimated monthly payment if detectable",
  "person_name": "string? - For HUTANG, the person involved"
}
```

### Example Outputs

```json
// Response to Example 1
{
  "is_debt_related": true,
  "debt_tier": "FORMAL",
  "debt_type": "education_loan",
  "provider": "PTPTN",
  "confidence": 0.99,
  "indicators": ["PTPTN keyword", "recurring monthly", "government loan format"],
  "estimated_monthly": 250.00,
  "person_name": null
}

// Response to Example 2
{
  "is_debt_related": true,
  "debt_tier": "BNPL",
  "debt_type": "installment",
  "provider": "Shopee SPayLater",
  "confidence": 0.98,
  "indicators": ["SPAYLATER keyword", "installment number pattern 2/6"],
  "estimated_monthly": 83.33,
  "person_name": null
}

// Response to Example 3
{
  "is_debt_related": true,
  "debt_tier": "HUTANG",
  "debt_type": "personal_loan",
  "provider": null,
  "confidence": 0.92,
  "indicators": ["transfer to individual", "bayar hutang in comment", "bulan lepas indicates past debt"],
  "estimated_monthly": null,
  "person_name": "Ahmad Bin Ali"
}
```

---

## Quality Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Recall (catch all debts) | >90% | Against debt-labeled dataset |
| Precision (minimize false positives) | >85% | Against non-debt transactions |
| Tier accuracy | >95% | Correct tier classification |
| Provider extraction | >80% | When provider is present |

---

## Debt Aggregation

The Debt Detector can also aggregate debt by tier:

```json
// Aggregation input
{
  "transactions": [...all user transactions...],
  "period": "all_time"
}

// Aggregation output
{
  "debt_summary": {
    "formal": {
      "count": 3,
      "providers": ["PTPTN", "Maybank HP", "CIMB Personal Loan"],
      "estimated_monthly_total": 1250.00
    },
    "bnpl": {
      "count": 2,
      "providers": ["SPayLater", "GrabPayLater"],
      "estimated_monthly_total": 166.66
    },
    "hutang": {
      "count": 1,
      "people": ["Ahmad Bin Ali"],
      "estimated_total": 800.00
    }
  },
  "total_monthly_debt_obligation": 1416.66
}
```

---

## Testing Requirements

1. **Unit Tests** (30+ cases)
   - Each debt tier has 10+ test cases
   - Edge cases for ambiguous transactions
   - False positive prevention tests

2. **Golden Dataset** (100 debt scenarios)
   - 40% Formal, 40% BNPL, 20% Hutang
   - Includes non-debt transactions for precision testing

3. **Adversarial Tests**
   - Transfers that look like hutang but aren't
   - Regular payments that aren't debt
   - BNPL-like patterns from non-BNPL sources

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
