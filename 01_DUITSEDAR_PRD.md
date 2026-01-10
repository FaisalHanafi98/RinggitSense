# DuitSedar — Product Requirements Document (PRD)

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026  
**Status:** Approved for Development  
**Timeline:** 8 Weeks

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Solution Overview](#3-solution-overview)
4. [Target Audience](#4-target-audience)
5. [User Stories & Journeys](#5-user-stories--journeys)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [Success Metrics](#8-success-metrics)
9. [Constraints & Assumptions](#9-constraints--assumptions)
10. [Risk Assessment](#10-risk-assessment)
11. [Glossary](#11-glossary)

---

## 1. Executive Summary

### 1.1 Product Vision

**DuitSedar** (*"Sedar duit, sedar diri"* — Know your money, know yourself) is an AI-powered financial awareness platform designed specifically for young Malaysian adults (22-35) navigating their first years of employment.

The platform combines:
- **Transaction aggregation** across Malaysian banks and e-wallets
- **Intelligent debt detection** (formal loans, BNPL, informal hutang)
- **Spending pattern analysis** with hidden cost revelation
- **Predictive modeling** for next-month spending
- **Personalized financial guidance** culturally-aware to Malaysian context

### 1.2 Strategic Value

| Stakeholder | Value Delivered |
|-------------|-----------------|
| **Young Professionals** | First unified view of fragmented finances; early debt warning system |
| **Malaysian Fintech Ecosystem** | Demonstrates gaps in current solutions; potential product inspiration |
| **Portfolio Reviewers** | Evidence of production-grade data engineering + ML + full-stack skills |
| **Recruiters** | Clear demonstration of solving real problems with technical depth |

### 1.3 Scope Summary

**In Scope (MVP - 8 Weeks):**
- Multi-source transaction ingestion (4 Malaysian banks/e-wallets)
- AI-powered transaction categorization
- Tri-tier debt tracking (formal, BNPL, hutang)
- Spending pattern analysis and lifestyle bundle detection
- Next-month spending prediction
- Financial health scoring and personalized advice
- React dashboard with responsive design
- Docker deployment to AWS

**Out of Scope (v1):**
- Real-time bank API integration (not available in Malaysia)
- Mobile native applications
- Multi-user/family accounts
- Investment tracking
- Tax optimization features

---

## 2. Problem Statement

### 2.1 The Malaysian Youth Financial Crisis

**53,000 individuals under age 30 carry nearly RM1.9 billion in cumulative debt**, with bankruptcy cases among youth rising 20% year-over-year. This crisis stems from a perfect storm of factors:

| Factor | Impact |
|--------|--------|
| **Stagnant Wages** | Fresh grad salaries (RM2,831-3,379) unchanged for 10+ years |
| **Fragmented Finances** | 4+ payment sources with no unified view |
| **BNPL Blindspot** | 5.1M users, RM9.3B transactions, invisible to credit history |
| **Hutang Culture** | Informal family/friend loans never tracked |
| **Hidden Costs** | Toll, commute, lifestyle bundles underestimated by 40-60% |
| **Cultural Obligations** | Family support, weddings, zakat add unpredictable expenses |

### 2.2 Current State Analysis

**Existing Solutions & Their Gaps:**

| Solution | Type | Gap |
|----------|------|-----|
| Bank Apps (Maybank MAE, RHB) | Single-bank view | No cross-bank aggregation |
| Touch & Go | E-wallet only | No bank integration |
| YNAB, Mint | International apps | No Malaysian bank support, no local context |
| Finory | Malaysian startup | Manual statement forwarding, limited ML |
| Excel Spreadsheets | Manual tracking | No automation, no insights |

**The Core Gap:** No tool provides a unified view across Malaysian financial sources while understanding local context (hutang culture, BNPL fragmentation, cultural obligations).

### 2.3 Desired State

A young Malaysian professional should be able to:
1. See ALL their money in one place (banks + e-wallets + cash)
2. Know EXACTLY how much they owe (loans + BNPL + hutang)
3. Understand WHERE their money actually goes (with hidden costs revealed)
4. PREDICT what next month will look like
5. Receive GUIDANCE that respects their cultural context

---

## 3. Solution Overview

### 3.1 Platform Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React Dashboard + PWA)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│                  (Spring Boot REST APIs)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLAUDE AGENT ORCHESTRATOR                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Categorizer│ │  Debt    │ │ Pattern  │ │Predictor │          │
│  │  Agent   │ │ Detector │ │ Analyzer │ │  Agent   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐                                     │
│  │  Query   │ │ Advisor  │                                     │
│  │  Agent   │ │  Agent   │                                     │
│  └──────────┘ └──────────┘                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│         PostgreSQL (AWS RDS) + pgvector Extension              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Core Modules

| Module | Purpose | Key Features |
|--------|---------|--------------|
| **Transaction Parser** | Ingest multi-source data | RHB, Maybank, T&G, Aeon parsers |
| **Categorization Engine** | Classify transactions | Zero-shot ML, Malaysian merchant awareness |
| **Debt Tracker** | Unified debt view | Formal + BNPL + Hutang tracking |
| **Pattern Analyzer** | Reveal hidden costs | Market basket analysis, trends |
| **Prediction Engine** | Forecast spending | Time-series, seasonal adjustments |
| **Advisor System** | Personalized guidance | Financial health score, tips |

### 3.3 Technology Stack (Locked)

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend | Spring Boot 3.2 (Java 17) | Portfolio requirement, enterprise standard |
| Frontend | React 18 + TypeScript | Modern, recruiter-expected |
| Database | PostgreSQL 15 + pgvector | Free-tier friendly, vector search |
| Auth | Clerk | Free tier, quick integration |
| AI/ML | Claude API (Anthropic) | Agent capabilities, reasoning |
| Monitoring | Sentry | Error tracking, free tier |
| Analytics | Plausible | Privacy-friendly, free tier |
| Deployment | Docker + AWS | Production-realistic |

---

## 4. Target Audience

### 4.1 Primary Persona

**Ahmad, 26, Software Developer in Kuala Lumpur**

| Attribute | Detail |
|-----------|--------|
| **Income** | RM4,500/month (first "real" job) |
| **Debts** | PTPTN (RM287/mo), Car loan (RM650/mo), 2 SPayLater commitments |
| **Family** | Gives parents RM500/month, owes friend RM800 |
| **Payment Methods** | RHB (salary), T&G (tolls), GrabPay (food), ShopeePay (shopping) |
| **Pain Points** | Never has savings by month-end, doesn't know total debt |
| **Goal** | Understand where money goes, get out of debt cycle |

### 4.2 Secondary Personas

**Nurul, 24, Fresh Graduate Teacher**
- Income: RM2,800/month
- Debts: PTPTN only, but using BNPL heavily
- Challenge: Lifestyle inflation, wedding savings pressure

**Raj, 30, Senior Executive**
- Income: RM7,500/month
- Debts: Housing loan, car loan, multiple credit cards
- Challenge: High income but still paycheck-to-paycheck

### 4.3 User Characteristics

| Characteristic | Implication for Design |
|----------------|----------------------|
| Mobile-first generation | Responsive design essential |
| Malay/English bilingual | Support BM transaction descriptions |
| Privacy-conscious | Local data processing, clear data policies |
| Time-poor | Quick insights, not complex configuration |
| Financially anxious | Non-judgmental tone, celebrating small wins |

---

## 5. User Stories & Journeys

### 5.1 Epic: Transaction Aggregation

**US-001: Upload Bank Statement**
> As a user, I want to upload my bank statement so that I can see all my transactions in one place.

Acceptance Criteria:
- [ ] Support PDF and CSV formats for RHB, Maybank, Aeon Bank
- [ ] Parse and normalize transactions within 30 seconds
- [ ] Show data quality report after upload
- [ ] Handle upload errors gracefully with clear messaging

**US-002: View Unified Transaction List**
> As a user, I want to see all my transactions from different sources in one list so that I understand my complete spending.

Acceptance Criteria:
- [ ] Display transactions sorted by date (newest first)
- [ ] Show source badge (which bank/e-wallet)
- [ ] Filter by date range, category, source
- [ ] Search by description or amount

**US-003: Correct Transaction Category**
> As a user, I want to correct a miscategorized transaction so that my spending reports are accurate.

Acceptance Criteria:
- [ ] One-click category correction
- [ ] System learns from corrections
- [ ] Bulk category update for similar transactions

### 5.2 Epic: Debt Management

**US-004: View Total Debt**
> As a user, I want to see my total debt across all sources so that I understand my true financial obligations.

Acceptance Criteria:
- [ ] Show total owed across formal, BNPL, and hutang
- [ ] Break down by debt type with subtotals
- [ ] Show monthly obligation amount
- [ ] Calculate debt-to-income ratio

**US-005: Track BNPL Automatically**
> As a user, I want the system to detect my BNPL purchases so that I don't lose track of installments.

Acceptance Criteria:
- [ ] Detect SPayLater, GrabPayLater, Atome transactions
- [ ] Show total BNPL exposure
- [ ] Alert when BNPL exceeds safe threshold (20% of income)
- [ ] Track remaining installments

**US-006: Manage Hutang**
> As a user, I want to track money I owe to family and friends so that I can maintain good relationships.

Acceptance Criteria:
- [ ] Add hutang with person name, amount, reason
- [ ] Track individual items within a hutang
- [ ] Mark items as paid
- [ ] See two-way ledger (what I owe vs what's owed to me)
- [ ] Sensitive, non-judgmental UI language

### 5.3 Epic: Spending Analysis

**US-007: View Spending Breakdown**
> As a user, I want to see where my money goes each month so that I can make better decisions.

Acceptance Criteria:
- [ ] Pie/bar chart by category
- [ ] Comparison to previous month
- [ ] Drill-down to transactions in each category
- [ ] Show percentage of income

**US-008: Discover Hidden Costs**
> As a user, I want to know my true spending on things like tolls and commuting so that I understand costs I've been underestimating.

Acceptance Criteria:
- [ ] Aggregate toll spending across all sources
- [ ] Calculate true commute cost (toll + petrol)
- [ ] Show as monthly and annual totals
- [ ] Compare to income percentage

**US-009: See Lifestyle Bundles**
> As a user, I want to understand how my spending patterns cluster so that I can identify expensive habits.

Acceptance Criteria:
- [ ] Show detected bundles (e.g., "Night out" = entertainment + food + transport)
- [ ] Display frequency and average cost
- [ ] Explain the pattern in plain language

### 5.4 Epic: Prediction & Planning

**US-010: Predict Next Month**
> As a user, I want to know what next month will likely cost so that I can prepare financially.

Acceptance Criteria:
- [ ] Show predicted total with confidence range
- [ ] Break down by category
- [ ] Highlight fixed commitments (loans, bills)
- [ ] Show expected surplus/deficit

**US-011: Scenario Planning**
> As a user, I want to model "what if" scenarios so that I can make informed decisions.

Acceptance Criteria:
- [ ] Input hypothetical changes (e.g., "work from home 2 days")
- [ ] See projected impact on spending
- [ ] Compare scenarios side-by-side

### 5.5 Epic: Financial Guidance

**US-012: See Financial Health Score**
> As a user, I want to know my overall financial health so that I can track improvement.

Acceptance Criteria:
- [ ] Score from 0-100 with clear meaning
- [ ] Show component breakdown
- [ ] Track score history over time
- [ ] Explain what affects the score

**US-013: Receive Personalized Advice**
> As a user, I want advice specific to my situation so that I can improve my finances.

Acceptance Criteria:
- [ ] Prioritized advice (urgent vs important vs growth)
- [ ] Actionable recommendations
- [ ] Culturally aware (zakat, family support, etc.)
- [ ] Ability to mark as helpful or snooze

**US-014: Ask Natural Language Questions**
> As a user, I want to ask questions in plain language so that I can get quick answers.

Acceptance Criteria:
- [ ] Support questions like "How much did I spend on food last month?"
- [ ] Handle Malay and English
- [ ] Provide accurate answers with source
- [ ] Suggest related questions

---

## 6. Functional Requirements

### 6.1 Data Ingestion Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | System shall accept CSV file uploads for transactions | Must Have |
| FR-002 | System shall accept PDF bank statements (RHB, Maybank) | Must Have |
| FR-003 | System shall parse Touch & Go e-wallet exports | Must Have |
| FR-004 | System shall parse Aeon Bank statements | Must Have |
| FR-005 | System shall normalize dates to ISO 8601 format | Must Have |
| FR-006 | System shall normalize amounts to 2 decimal places | Must Have |
| FR-007 | System shall detect and flag duplicate transactions | Must Have |
| FR-008 | System shall calculate data quality score per upload | Should Have |
| FR-009 | System shall support manual transaction entry | Should Have |
| FR-010 | System shall handle upload errors with clear messaging | Must Have |

### 6.2 Categorization Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-011 | System shall categorize transactions using AI | Must Have |
| FR-012 | System shall recognize Malaysian merchants | Must Have |
| FR-013 | System shall handle mixed BM/EN descriptions | Must Have |
| FR-014 | System shall allow manual category correction | Must Have |
| FR-015 | System shall learn from user corrections | Should Have |
| FR-016 | System shall provide category confidence scores | Should Have |
| FR-017 | Categories shall include: Food, Transport, Bills, Entertainment, Shopping, Transfer, Debt, Other | Must Have |

### 6.3 Debt Tracking Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-018 | System shall detect formal loan repayments | Must Have |
| FR-019 | System shall detect BNPL transactions (SPayLater, GrabPayLater, Atome) | Must Have |
| FR-020 | System shall allow manual hutang entry | Must Have |
| FR-021 | System shall track hutang by person | Must Have |
| FR-022 | System shall support two-way hutang (owe vs owed) | Must Have |
| FR-023 | System shall calculate total debt across all tiers | Must Have |
| FR-024 | System shall calculate monthly debt obligations | Must Have |
| FR-025 | System shall alert when BNPL exceeds 20% of income | Should Have |
| FR-026 | System shall track payment history | Should Have |

### 6.4 Analysis Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-027 | System shall calculate spending by category | Must Have |
| FR-028 | System shall show month-over-month trends | Must Have |
| FR-029 | System shall detect spending anomalies | Should Have |
| FR-030 | System shall perform market basket analysis | Should Have |
| FR-031 | System shall aggregate hidden costs (tolls, commute) | Must Have |
| FR-032 | System shall identify recurring transactions | Should Have |

### 6.5 Prediction Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-033 | System shall predict next month total spending | Must Have |
| FR-034 | System shall predict by category | Should Have |
| FR-035 | System shall show confidence intervals | Should Have |
| FR-036 | System shall adjust for Malaysian holidays | Should Have |
| FR-037 | System shall support scenario modeling | Could Have |

### 6.6 Advisor Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-038 | System shall calculate financial health score | Must Have |
| FR-039 | System shall generate personalized advice | Must Have |
| FR-040 | System shall prioritize advice by urgency | Should Have |
| FR-041 | System shall track advice feedback | Should Have |
| FR-042 | System shall support advice snoozing | Could Have |
| FR-043 | Advice shall be culturally aware (zakat, family support) | Should Have |

### 6.7 Query Module

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-044 | System shall accept natural language queries | Should Have |
| FR-045 | System shall handle English and Malay queries | Should Have |
| FR-046 | System shall provide accurate responses with sources | Should Have |

---

## 7. Non-Functional Requirements

### 7.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-001 | Statement upload processing time | < 30 seconds for 500 transactions |
| NFR-002 | Dashboard initial load time | < 2 seconds |
| NFR-003 | API response time | < 500ms (95th percentile) |
| NFR-004 | AI categorization throughput | 100 transactions/minute |
| NFR-005 | Concurrent users supported | 10 (portfolio demo scale) |

### 7.2 Security

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-006 | Authentication | Clerk integration with JWT |
| NFR-007 | Data encryption at rest | AES-256 |
| NFR-008 | Data encryption in transit | TLS 1.3 |
| NFR-009 | Input validation | All user inputs sanitized |
| NFR-010 | Rate limiting | 100 requests/minute per user |
| NFR-011 | OWASP Top 10 compliance | Address all applicable risks |

### 7.3 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-012 | System uptime | 99% (excluding planned maintenance) |
| NFR-013 | Data backup frequency | Daily |
| NFR-014 | Error logging | All errors captured in Sentry |
| NFR-015 | Graceful degradation | Core features work if AI unavailable |

### 7.4 Usability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-016 | Mobile responsiveness | Full functionality on mobile |
| NFR-017 | Accessibility | WCAG 2.1 AA compliance |
| NFR-018 | Language support | English primary, Malay descriptions supported |
| NFR-019 | Learning curve | New user productive in < 5 minutes |

### 7.5 Maintainability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-020 | Code documentation | JSDoc/JavaDoc for public APIs |
| NFR-021 | Test coverage | > 70% for backend services |
| NFR-022 | Deployment automation | Docker + CI/CD pipeline |

---

## 8. Success Metrics

### 8.1 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Transaction categorization accuracy | > 85% | Manual validation sample |
| BNPL detection rate | > 90% | Against known BNPL transactions |
| Prediction accuracy (MAPE) | < 20% | Actual vs predicted comparison |
| API uptime | > 99% | AWS CloudWatch |
| Error rate | < 1% | Sentry tracking |

### 8.2 User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to first insight | < 2 minutes | From upload to dashboard |
| Task completion rate | > 90% | Key user journeys |
| Advice helpfulness | > 60% marked helpful | User feedback |

### 8.3 Portfolio/Career Metrics

| Metric | Target | Evidence |
|--------|--------|----------|
| Code quality | No critical issues | SonarQube scan |
| Documentation completeness | All modules documented | Review checklist |
| Interview talking points | 5+ technical deep-dives | Preparation notes |
| Demo stability | Zero crashes in demo | Testing |

---

## 9. Constraints & Assumptions

### 9.1 Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| 8-week timeline | Limited feature set | Strict MVP scope |
| Free-tier infrastructure | Performance limits | Optimize queries, cache aggressively |
| No bank APIs in Malaysia | Manual upload required | Streamlined upload UX |
| Single developer | No parallel workstreams | Sequential phase execution |
| Claude API costs | Budget for AI calls | Efficient prompt design, caching |

### 9.2 Assumptions

| Assumption | Risk if Invalid | Validation |
|------------|-----------------|------------|
| Users have bank statements accessible | Low adoption | Provide sample data option |
| Transaction descriptions are parseable | Poor categorization | Robust fallback logic |
| Claude API remains stable | Integration failures | Abstract AI layer, mock fallback |
| AWS free tier sufficient | Cost overruns | Monitor usage, set alerts |

---

## 10. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | High | Strict weekly milestones, feature freeze after week 6 |
| AI accuracy insufficient | Medium | Medium | Rule-based fallbacks, user correction UI |
| Bank statement format changes | Low | Medium | Modular parser architecture |
| Timeline overrun | Medium | High | MVP-first approach, cut features not quality |
| Claude API rate limits | Low | Medium | Implement caching, batch processing |
| Security vulnerabilities | Low | High | OWASP checklist, security review |

---

## 11. Glossary

| Term | Definition |
|------|------------|
| **BNPL** | Buy Now Pay Later - installment payment services like SPayLater |
| **Hutang** | Malaysian/Malay term for informal debt between family/friends |
| **T&G** | Touch 'n Go - Malaysia's dominant e-wallet for tolls and payments |
| **PTPTN** | Perbadanan Tabung Pendidikan Tinggi Nasional - Malaysian student loan |
| **Zakat** | Islamic obligatory charity (2.5% of qualifying wealth) |
| **Balik Kampung** | Return to hometown - significant expense during festivals |
| **DXA** | Document XML Architecture - measurement unit in Word docs (1440 = 1 inch) |
| **pgvector** | PostgreSQL extension for vector similarity search |
| **Zero-shot classification** | ML technique to categorize without training data |

---

**Document End**

*Next Document: 02_TECHNICAL_ARCHITECTURE.md*
