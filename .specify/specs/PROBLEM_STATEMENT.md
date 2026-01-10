# RinggitSense Problem Statement

> Understanding the Malaysian youth financial crisis and why existing solutions fail

---

## The Malaysian Financial Context

### The Youth Debt Crisis

**53,000 Malaysians under age 30 carry nearly RM1.9 billion in cumulative debt**, with bankruptcy cases among youth rising 20% year-over-year. This is not just a statistic—it represents a generation struggling with financial visibility.

| Metric | Value | Source |
|--------|-------|--------|
| Youth bankruptcies (under 30) | 53,000+ | Malaysia Department of Insolvency |
| Total youth debt | RM1.9 billion | Bank Negara Malaysia |
| YoY bankruptcy increase | 20% | 2024-2025 trend |
| Fresh grad salary (avg) | RM2,831-3,379 | DOSM 2024 |
| Salary stagnation | 10+ years | No real wage growth |

### The Perfect Storm

Young Malaysian professionals face a unique combination of challenges:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FACTORS DRIVING YOUTH DEBT                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │   STAGNANT       │  │   FRAGMENTED     │  │    INVISIBLE     │     │
│  │   WAGES          │  │   FINANCES       │  │    BNPL DEBT     │     │
│  │                  │  │                  │  │                  │     │
│  │  Fresh grad      │  │  4+ payment      │  │  5.1M users      │     │
│  │  salaries        │  │  sources with    │  │  RM9.3B in       │     │
│  │  unchanged for   │  │  no unified      │  │  transactions    │     │
│  │  10+ years       │  │  view            │  │  invisible to    │     │
│  │                  │  │                  │  │  credit bureaus  │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │   HUTANG         │  │   HIDDEN         │  │   CULTURAL       │     │
│  │   CULTURE        │  │   COSTS          │  │   OBLIGATIONS    │     │
│  │                  │  │                  │  │                  │     │
│  │  Informal loans  │  │  Toll, commute   │  │  Family support  │     │
│  │  to family and   │  │  and lifestyle   │  │  weddings, zakat │     │
│  │  friends never   │  │  costs           │  │  add unplanned   │     │
│  │  tracked         │  │  underestimated  │  │  expenses        │     │
│  │                  │  │  by 40-60%       │  │                  │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The Fragmentation Problem

### A Typical Malaysian's Financial Landscape

A young professional in Kuala Lumpur might have:

| Source | Type | Visibility | Integration |
|--------|------|------------|-------------|
| Maybank Savings | Bank account | Maybank app only | None |
| RHB Credit Card | Credit | RHB app only | None |
| Touch 'n Go | E-wallet | TnG app only | None |
| GrabPay | E-wallet | Grab app only | None |
| ShopeePay | E-wallet | Shopee app only | None |
| SPayLater | BNPL | Shopee app only | Not in credit bureau |
| Cash | Physical | Untracked | None |

**Result**: No single view of total spending, total debt, or financial health.

### The Tri-Tier Debt Blindspot

Malaysian youth debt exists in three tiers, each with different visibility:

| Tier | Examples | Tracking Status | Risk Level |
|------|----------|-----------------|------------|
| **FORMAL** | PTPTN, car loan, personal loan, mortgage | Visible to credit bureaus | Known |
| **BNPL** | SPayLater, GrabPayLater, Atome | NOT in credit bureau | Hidden |
| **HUTANG** | Family loans, friend borrowings | Never tracked anywhere | Invisible |

**The danger**: Someone can appear "debt-free" on paper while owing thousands in BNPL and hutang.

---

## Why Current Solutions Fail

### Existing Options Analysis

| Solution | Category | What It Does | Why It Fails for Malaysians |
|----------|----------|--------------|----------------------------|
| **Maybank MAE** | Bank app | Single-bank view | No cross-bank, no e-wallets |
| **CIMB Clicks** | Bank app | Single-bank view | No cross-bank, no e-wallets |
| **Touch 'n Go** | E-wallet | TnG transactions | No bank integration |
| **YNAB** | Budgeting | Manual tracking | No Malaysian bank import, USD-focused |
| **Mint** | Aggregator | US bank integration | No Malaysian bank support |
| **Finory** | Malaysian startup | Statement parsing | Manual email forwarding, limited ML |
| **Excel** | Manual | Full control | No automation, no insights, error-prone |

### The Core Gap

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   NO TOOL EXISTS THAT:                                                  │
│                                                                         │
│   [ ] Aggregates ALL Malaysian financial sources                        │
│   [ ] Detects BNPL debt that's invisible to credit bureaus             │
│   [ ] Tracks informal hutang to family/friends                          │
│   [ ] Understands Malaysian spending context (toll, mamak, pasar)      │
│   [ ] Provides culturally-aware financial guidance                      │
│   [ ] Reveals hidden costs (toll often 40-60% underestimated)          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## User Pain Points

### Primary Persona: Ahmad, 27

> *"I know I should save more, but I don't even know where my money goes."*

| Attribute | Value |
|-----------|-------|
| Age | 27 |
| Occupation | Software Developer |
| Salary | RM4,500/month |
| Location | Petaling Jaya, works in KL |
| Banks | Maybank (salary), RHB (savings) |
| E-wallets | TnG, GrabPay, ShopeePay |
| BNPL | SPayLater (active) |
| Hutang | RM800 to sister |

**Ahmad's frustrations**:
1. "I check 5 different apps to see my money"
2. "I forgot I had SPayLater installments this month"
3. "I never know how much toll actually costs me"
4. "I borrowed from my sister 3 months ago and keep forgetting"
5. "By the 20th I'm always broke but don't know why"

### Secondary Persona: Mei Ling, 24

> *"I just started working and I'm already drowning. My mom keeps asking for money but I have PTPTN to pay."*

| Attribute | Value |
|-----------|-------|
| Age | 24 |
| Occupation | Marketing Executive |
| Salary | RM3,200/month |
| Debt | PTPTN (RM25,000), GrabPayLater |
| Family obligation | RM500/month to parents |

**Mei Ling's frustrations**:
1. "PTPTN, GrabPayLater, helping my parents—I can't keep track"
2. "I don't know if I can afford this purchase or not"
3. "Everyone says 'budget' but I don't even know my real expenses"

---

## The Desired State

### What Success Looks Like

A young Malaysian professional should be able to:

| Need | Current State | Desired State |
|------|---------------|---------------|
| **Unified view** | Check 5+ apps | One dashboard shows everything |
| **Debt awareness** | Formal debt only visible | All 3 tiers tracked and totaled |
| **Spending insight** | "I don't know where it goes" | Category breakdown with hidden costs revealed |
| **Future planning** | Surprised by month-end | Predicted spending before it happens |
| **Guidance** | Generic "save more" advice | Personalized, culturally-aware recommendations |

### User Journey: After RinggitSense

```
BEFORE:
Ahmad checks Maybank → checks RHB → checks TnG → checks Shopee →
still confused → forgets SPayLater → month-end: "Where did my money go?"

AFTER:
Ahmad opens RinggitSense → sees all accounts in one view →
sees upcoming SPayLater payment → sees toll costs him RM450/month →
receives alert: "You're on track to overspend by RM300" → adjusts behavior
```

---

## Problem Validation

### Evidence of Need

| Signal | Evidence |
|--------|----------|
| Market size | 5.1M BNPL users in Malaysia |
| Pain intensity | 53,000 youth bankruptcies |
| Willingness to pay | Fintech adoption rate 95% in Malaysia |
| Gap in market | No integrated solution exists |

### Why Now?

1. **BNPL explosion**: From near-zero to RM9.3B in transactions
2. **Digital payment maturity**: TnG, GrabPay ubiquitous
3. **AI capability**: Claude can understand Malaysian context
4. **Youth awareness**: Growing financial literacy movement

---

## Constraints & Considerations

### Technical Constraints

| Constraint | Implication |
|------------|-------------|
| No open banking API in Malaysia | Must use statement parsing |
| Statement formats vary by bank | Need bank-specific parsers |
| Real-time not possible | Batch processing acceptable |

### Regulatory Constraints

| Regulation | Requirement |
|------------|-------------|
| PDPA Malaysia | User consent required, data encryption mandatory |
| BNM | Cannot provide licensed financial advice |
| Anti-money laundering | Cannot facilitate suspicious transactions |

### Cultural Considerations

| Factor | Design Implication |
|--------|---------------------|
| Hutang is sensitive | Non-judgmental language |
| Family obligations are expected | Don't treat as "problem" |
| Raya/CNY spending spikes | Expected, not anomalous |
| Halal/syariah sensitivity | Be neutral on financial products |

---

## Success Metrics

### Primary Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Transaction categorization accuracy | >95% | Core functionality |
| Debt detection recall | >90% | Must catch all debt types |
| User-reported financial clarity | 8/10 | Subjective improvement |
| Time to first insight | <5 minutes | Onboarding efficiency |

### Secondary Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Hidden cost revelation | >RM100/month average | Value demonstration |
| Prediction accuracy (next month) | Within 15% | Useful forecasting |
| User retention (weekly) | >50% | Ongoing value |

---

## Summary

**Problem**: Young Malaysians are financially blind—their money is fragmented across multiple apps, their debt exists in invisible layers, and no tool understands their local context.

**Opportunity**: Build the first AI-powered financial awareness platform designed specifically for Malaysians, with local bank integration, tri-tier debt tracking, and culturally-aware guidance.

**RinggitSense**: *Sedar duit, sedar diri.* Know your money, know yourself.

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
**Synthesized From**: 01_DUITSEDAR_PRD.md, market research, user persona analysis
