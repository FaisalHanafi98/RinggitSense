# RinggitSense PRD Synthesis

> Synthesized Product Requirements Document from existing assets

**Synthesized From**: 01_DUITSEDAR_PRD.md, 02_TECHNICAL_ARCHITECTURE.md, 05_API_SPECIFICATION.md
**Version**: 1.0
**Status**: Approved for Development

---

## Executive Summary

### Product Vision

**RinggitSense** is an AI-powered financial awareness platform designed specifically for young Malaysian adults (22-35) navigating their first years of employment. The platform provides unified visibility across fragmented financial sources, intelligent debt detection across three tiers, and personalized guidance grounded in Malaysian context.

### Value Proposition

| For | Pain Point | Solution |
|-----|------------|----------|
| Young professionals | Fragmented view across 5+ apps | Single unified dashboard |
| BNPL users | Invisible installment debt | Automatic BNPL detection and tracking |
| Family supporters | Untracked informal loans | Hutang tracking with gentle reminders |
| Commuters | Underestimated toll/transport costs | Hidden cost revelation |
| All users | Generic financial advice | Culturally-aware, personalized guidance |

### Scope Definition

**In Scope (MVP - 8 Weeks)**:
- Multi-source transaction ingestion (4 Malaysian banks/e-wallets)
- AI-powered transaction categorization
- Tri-tier debt tracking (formal, BNPL, hutang)
- Spending pattern analysis and lifestyle bundle detection
- Next-month spending prediction
- Financial health scoring and personalized advice
- React dashboard with responsive design
- Docker deployment to AWS

**Out of Scope (v1)**:
- Real-time bank API integration (not available in Malaysia)
- Mobile native applications
- Multi-user/family accounts
- Investment tracking
- Tax optimization features
- Syariah-specific financial products

---

## Functional Requirements

### FR-1: Transaction Ingestion

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1.1 | Accept CSV/PDF bank statement uploads | Must Have | RHB, Maybank, CIMB, Public Bank |
| FR-1.2 | Parse Touch 'n Go transaction history | Must Have | Export from TnG app |
| FR-1.3 | Parse GrabPay transaction history | Should Have | If export available |
| FR-1.4 | Parse ShopeePay transaction history | Should Have | If export available |
| FR-1.5 | Deduplicate transactions across sources | Must Have | Same transaction from card + e-wallet |
| FR-1.6 | Preserve original transaction descriptions | Must Have | For categorization accuracy |

### FR-2: Transaction Categorization

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-2.1 | Automatically categorize transactions into 10 categories | Must Have | See constitution for category list |
| FR-2.2 | Achieve >95% categorization accuracy | Must Have | Measured on test dataset |
| FR-2.3 | Allow user to override categories | Must Have | Learning feedback |
| FR-2.4 | Recognize Malaysian merchants | Must Have | Mamak, pasar malam, local chains |
| FR-2.5 | Handle multi-language descriptions | Should Have | BM, English, Chinese |
| FR-2.6 | Provide confidence scores | Must Have | Flag low-confidence for review |

### FR-3: Debt Detection

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-3.1 | Detect FORMAL debt payments | Must Have | PTPTN, car loan, personal loan |
| FR-3.2 | Detect BNPL installments | Must Have | SPayLater, GrabPayLater, Atome |
| FR-3.3 | Detect HUTANG patterns | Should Have | Transfers with debt indicators |
| FR-3.4 | Calculate total debt obligation | Must Have | Sum of all three tiers |
| FR-3.5 | Project debt payoff timeline | Should Have | Based on current payments |
| FR-3.6 | Alert on missed debt payments | Must Have | Based on expected patterns |

### FR-4: Pattern Analysis

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-4.1 | Identify temporal patterns | Must Have | Weekend vs weekday, payday effects |
| FR-4.2 | Detect lifestyle bundles | Should Have | Night out, commute, weekend shopping |
| FR-4.3 | Reveal hidden costs | Must Have | Toll, delivery fees, subscriptions |
| FR-4.4 | Identify spending anomalies | Should Have | Unusual transactions |
| FR-4.5 | Track festival spending | Should Have | Raya, CNY, Deepavali patterns |

### FR-5: Prediction

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-5.1 | Predict next-month total spending | Must Have | Within 15% accuracy |
| FR-5.2 | Predict by-category spending | Should Have | Top 5 categories |
| FR-5.3 | Forecast month-end balance | Must Have | Based on prediction |
| FR-5.4 | Alert on predicted overspending | Must Have | Before it happens |

### FR-6: Financial Advice

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-6.1 | Generate personalized recommendations | Must Have | Based on user's data |
| FR-6.2 | Include mandatory disclaimers | Must Have | Not professional advice |
| FR-6.3 | Provide actionable suggestions | Must Have | Specific, not generic |
| FR-6.4 | Respect cultural context | Must Have | Non-judgmental on family obligations |
| FR-6.5 | Prioritize advice by impact | Should Have | Highest ROI first |

### FR-7: User Interface

| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-7.1 | Dashboard with spending overview | Must Have | Cards, charts, totals |
| FR-7.2 | Transaction list with search/filter | Must Have | By date, category, amount |
| FR-7.3 | Debt summary view | Must Have | All three tiers visible |
| FR-7.4 | Natural language query interface | Should Have | "How much did I spend on food?" |
| FR-7.5 | Responsive design (mobile-friendly) | Must Have | Primary mobile usage |
| FR-7.6 | Dark mode support | Could Have | User preference |

---

## Non-Functional Requirements

### NFR-1: Performance

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-1.1 | Page load time | <2 seconds | 90th percentile |
| NFR-1.2 | Transaction categorization | <500ms per transaction | Batch average |
| NFR-1.3 | Full statement processing | <30 seconds for 500 transactions | End-to-end |
| NFR-1.4 | Dashboard data refresh | <5 seconds | After new upload |

### NFR-2: Security

| ID | Requirement | Implementation |
|----|-------------|----------------|
| NFR-2.1 | Data encryption at rest | AES-256 |
| NFR-2.2 | Data encryption in transit | TLS 1.3 |
| NFR-2.3 | Authentication | JWT with refresh tokens |
| NFR-2.4 | Session management | 24-hour expiry, secure cookies |
| NFR-2.5 | Input validation | All user inputs sanitized |
| NFR-2.6 | PDPA compliance | Consent flow, data deletion option |

### NFR-3: Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-3.1 | Uptime | 99.5% (excluding planned maintenance) |
| NFR-3.2 | Data backup | Daily, 30-day retention |
| NFR-3.3 | Recovery time objective | <4 hours |
| NFR-3.4 | Recovery point objective | <24 hours |

### NFR-4: Scalability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-4.1 | Concurrent users | 100 (MVP) |
| NFR-4.2 | Transactions per user | 10,000 (2+ years history) |
| NFR-4.3 | Statement size | Up to 5MB per file |

---

## User Stories

### Epic 1: Transaction Management

```
US-1.1: As a user, I want to upload my bank statement so that my transactions are imported automatically.
Acceptance Criteria:
- Support PDF and CSV formats
- Show progress during upload
- Display count of imported transactions
- Highlight any parsing errors

US-1.2: As a user, I want to see all my transactions in one place so that I don't have to switch between apps.
Acceptance Criteria:
- List view with date, description, amount, category
- Filter by date range, category, source
- Search by description or amount
- Sort by any column

US-1.3: As a user, I want to correct miscategorized transactions so that my reports are accurate.
Acceptance Criteria:
- One-click category change
- System learns from corrections
- Bulk edit option
```

### Epic 2: Debt Tracking

```
US-2.1: As a user, I want to see all my debts including BNPL so that I know my true financial obligation.
Acceptance Criteria:
- Three-tier breakdown (Formal, BNPL, Hutang)
- Total amount owed
- Monthly payment summary
- Remaining balance per debt

US-2.2: As a user, I want to track informal loans to family/friends so that I don't forget to pay them back.
Acceptance Criteria:
- Manual hutang entry option
- Auto-detection from transfers with keywords
- Reminder for outstanding hutang
```

### Epic 3: Insights & Predictions

```
US-3.1: As a user, I want to know my hidden costs so that I can make informed decisions.
Acceptance Criteria:
- Toll cost aggregation (often underestimated)
- Subscription detection
- Delivery fee totals
- Comparison to user's estimate

US-3.2: As a user, I want to see predicted spending for next month so that I can plan ahead.
Acceptance Criteria:
- Total predicted amount
- By-category breakdown
- Confidence interval
- Comparison to budget (if set)
```

### Epic 4: Financial Guidance

```
US-4.1: As a user, I want personalized financial advice so that I can improve my financial health.
Acceptance Criteria:
- Specific to my spending patterns
- Includes disclaimer
- Actionable (not generic)
- Prioritized by impact

US-4.2: As a user, I want to ask questions about my finances in natural language.
Acceptance Criteria:
- "How much did I spend on food in December?"
- "What's my biggest expense?"
- "Am I on track this month?"
- Conversational responses
```

---

## Technical Architecture Summary

### System Components

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            USER INTERFACE                                │
│                         React 18 + TypeScript                           │
│                   (Dashboard, Transactions, Insights)                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY                                   │
│                    FastAPI (Python 3.11+)                               │
│            (Authentication, Validation, Rate Limiting)                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        AGENT ORCHESTRATOR                                │
│                                                                         │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐              │
│  │Categorizer│ │   Debt    │ │  Pattern  │ │ Predictor │              │
│  │   Agent   │ │ Detector  │ │ Analyzer  │ │   Agent   │              │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘              │
│  ┌───────────┐ ┌───────────┐                                           │
│  │   Query   │ │  Advisor  │                                           │
│  │   Agent   │ │   Agent   │                                           │
│  └───────────┘ └───────────┘                                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                     │
│                    PostgreSQL (AWS RDS)                                 │
│              (Users, Transactions, Categories, Debt)                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Agent Responsibility Matrix

| Agent | Input | Output | Latency Target |
|-------|-------|--------|----------------|
| Categorizer | Transaction description, amount | Category, confidence, merchant | <500ms |
| Debt Detector | Transaction + history | Debt tier, type, provider | <500ms |
| Pattern Analyzer | Transaction set | Patterns, anomalies, insights | <3s |
| Predictor | Historical data | Next-month forecast | <3s |
| Query | Natural language question | Structured answer | <2s |
| Advisor | User profile + patterns | Recommendations with disclaimers | <3s |

---

## Clarification Points

Items requiring input before implementation:

| ID | Question | Context | Suggested Default |
|----|----------|---------|-------------------|
| CL-001 | Which exact bank statement formats are available for testing? | Need sample files | Start with RHB CSV |
| CL-002 | Should BNPL detection be opt-in or automatic? | Privacy consideration | Automatic with disclosure |
| CL-003 | Maximum historical transaction period? | Storage/cost implication | 2 years |
| CL-004 | Real user testing availability? | Validation need | Use synthetic data first |
| CL-005 | Budget for AWS deployment? | Infrastructure sizing | Start with t3.small |

---

## Success Criteria

### MVP Launch Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Transaction categorization accuracy | >95% | Test dataset |
| Statement parsing success rate | >98% | Supported banks |
| Page load performance | <2 seconds | 90th percentile |
| Zero critical security vulnerabilities | 0 | Security scan |
| Core user journeys functional | 100% | E2E tests pass |

### Post-Launch Metrics (Week 4+)

| Metric | Target | Notes |
|--------|--------|-------|
| User retention (weekly active) | >50% | Return users |
| Hidden cost revelation | >RM100/user avg | Value demonstration |
| Prediction accuracy | Within 15% | Month-end validation |
| User satisfaction | >4/5 rating | In-app survey |

---

## Constraints Summary

| Category | Constraint | Implication |
|----------|------------|-------------|
| Technical | No Malaysian open banking API | Statement upload only |
| Legal | Not a licensed financial advisor | Disclaimers mandatory |
| Timeline | 8 weeks to MVP | Scope must be tight |
| Budget | Cost-conscious AWS deployment | No over-engineering |
| Team | Solo developer | Prioritize automation |

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-10 | Initial synthesis from existing docs | Faisal |

---

**Synthesized From**:
- 01_DUITSEDAR_PRD.md (24 KB)
- 02_TECHNICAL_ARCHITECTURE.md (50 KB)
- 05_API_SPECIFICATION.md (21 KB)
- 06_DEVELOPMENT_ROADMAP.md (27 KB)

**Status**: Approved for Development
