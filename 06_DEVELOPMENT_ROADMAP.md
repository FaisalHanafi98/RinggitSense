# DuitSedar — Development Roadmap

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026  
**Timeline:** 8 Weeks  
**Start Date:** Week of January 6, 2026

---

## Table of Contents

1. [Roadmap Overview](#1-roadmap-overview)
2. [Week 1: Foundation](#2-week-1-foundation)
3. [Week 2: Data Ingestion](#3-week-2-data-ingestion)
4. [Week 3: Categorization & Claude Integration](#4-week-3-categorization--claude-integration)
5. [Week 4: Debt Detection & Tracking](#5-week-4-debt-detection--tracking)
6. [Week 5: Pattern Analysis](#6-week-5-pattern-analysis)
7. [Week 6: Prediction Engine](#7-week-6-prediction-engine)
8. [Week 7: Advisor System & Query](#8-week-7-advisor-system--query)
9. [Week 8: Polish & Deploy](#9-week-8-polish--deploy)
10. [Risk Mitigation](#10-risk-mitigation)
11. [Definition of Done](#11-definition-of-done)

---

## 1. Roadmap Overview

### 1.1 Visual Timeline

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           DUITSEDAR 8-WEEK DEVELOPMENT ROADMAP                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

Week    1         2         3         4         5         6         7         8
        │         │         │         │         │         │         │         │
        ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ FOUNDATION │ INGESTION │ CATEGORY │  DEBT   │ PATTERNS │ PREDICT │ ADVISOR │ DEPLOY │
│            │           │          │         │          │         │         │        │
│ • Project  │ • Parsers │ • Claude │ • BNPL  │ • Market │ • Time  │ • Health│ • Docker│
│   setup    │ • Upload  │   agents │   detect│   basket │   series│   score │ • AWS  │
│ • Database │ • Normal- │ • Categ- │ • Hutang│ • Trends │ • Fore- │ • Tips  │ • Docs │
│ • Auth     │   ization │   orize  │   mgmt  │ • Hidden │   cast  │ • Query │ • Demo │
│ • React    │ • Quality │ • Review │ • Dash  │   costs  │ • Scene │ • NL    │ • Video│
└─────────────────────────────────────────────────────────────────────────────────────┘
        │         │         │         │         │         │         │         │
        ▼         ▼         ▼         ▼         ▼         ▼         ▼         ▼
     MILESTONE  MILESTONE  MILESTONE  MILESTONE  MILESTONE  MILESTONE  MILESTONE  LAUNCH
        M1        M2         M3        M4         M5        M6         M7        M8

Legend:
█████ Backend Focus
░░░░░ Frontend Focus  
▓▓▓▓▓ AI/ML Focus
```

### 1.2 Milestone Summary

| Week | Milestone | Deliverable | Success Criteria |
|------|-----------|-------------|------------------|
| 1 | M1: Foundation | Dev environment ready | All tools installed, DB connected, basic UI renders |
| 2 | M2: Ingestion | File upload working | Can upload your actual transaction file and see raw data |
| 3 | M3: Categorization | AI categorization | Transactions auto-categorized with 80%+ accuracy |
| 4 | M4: Debt Tracking | Debt dashboard | All 3 debt tiers visible, hutang management working |
| 5 | M5: Patterns | Insights generated | Hidden costs and bundles revealed from your data |
| 6 | M6: Prediction | Forecast ready | Next month prediction with confidence intervals |
| 7 | M7: Advisor | Guidance system | Financial health score + personalized advice |
| 8 | M8: Launch | Production ready | Live demo, documentation complete, portfolio-ready |

### 1.3 Daily Time Allocation

Assuming ~3-4 hours/day available for development:

| Activity | Time | Purpose |
|----------|------|---------|
| Coding | 2.5-3 hours | Primary development |
| Testing | 30 min | Manual + automated tests |
| Documentation | 15 min | Update as you build |
| Review | 15 min | Code quality, planning next day |

---

## 2. Week 1: Foundation

### 2.1 Goals
- Set up complete development environment
- Initialize Spring Boot + React projects
- Configure PostgreSQL with pgvector
- Implement Clerk authentication
- Create basic project structure

### 2.2 Daily Breakdown

**Day 1: Backend Setup**
```
Tasks:
├── Initialize Spring Boot 3.2 project with Gradle
├── Configure application.yml for dev/prod profiles
├── Set up project structure (controller/service/repository/model)
├── Add dependencies: Spring Web, JPA, Security, Validation
└── Verify application starts successfully

Deliverable: Spring Boot app running on localhost:8080
```

**Day 2: Database Setup**
```
Tasks:
├── Install PostgreSQL 15 locally (or Docker)
├── Create duitsedar database
├── Enable pgvector extension
├── Create initial migration (V1__initial_schema.sql)
├── Configure Spring Data JPA connection
└── Verify database connectivity

Deliverable: Database connected, tables created
```

**Day 3: Authentication**
```
Tasks:
├── Create Clerk account and application
├── Configure Clerk SDK in Spring Boot
├── Implement JWT validation filter
├── Create SecurityConfig with protected routes
├── Test authentication flow with Postman
└── Create basic /api/v1/health endpoint

Deliverable: Protected endpoints require valid Clerk JWT
```

**Day 4: Frontend Setup**
```
Tasks:
├── Initialize React 18 project with Vite + TypeScript
├── Configure TailwindCSS
├── Set up project structure (components/hooks/services/types)
├── Install dependencies: React Router, Zustand, TanStack Query, Recharts
├── Create basic routing (Dashboard, Transactions, Debts, Insights)
└── Configure Clerk React SDK

Deliverable: React app with navigation and auth
```

**Day 5: Integration & Polish**
```
Tasks:
├── Connect frontend to backend API
├── Implement auth flow end-to-end
├── Create basic layout component (Header, Sidebar, Main)
├── Set up environment variables (.env files)
├── Create Docker Compose for local development
└── Write README with setup instructions

Deliverable: Full stack running locally with auth
```

### 2.3 Week 1 Checklist

- [ ] Spring Boot project initialized
- [ ] PostgreSQL with pgvector running
- [ ] All database tables created
- [ ] Clerk authentication working
- [ ] React project initialized
- [ ] Basic routing in place
- [ ] Frontend-backend communication working
- [ ] Docker Compose configured
- [ ] README written

### 2.4 Exit Criteria

✅ Can login via Clerk and access protected dashboard
✅ Database accepts sample transaction insert
✅ API returns authenticated user info

---

## 3. Week 2: Data Ingestion

### 3.1 Goals
- Build parsers for 4 Malaysian bank/e-wallet formats
- Implement file upload API
- Create normalization pipeline
- Build upload UI with progress feedback
- Handle your actual transaction data

### 3.2 Daily Breakdown

**Day 1: Parser Architecture**
```
Tasks:
├── Design StatementParser interface
├── Create ParserFactory for format detection
├── Implement base parsing utilities (date, amount, description cleaning)
├── Create DataSource entity and repository
└── Build file upload endpoint skeleton

Deliverable: Parser framework ready
```

**Day 2: RHB + Maybank Parsers**
```
Tasks:
├── Analyze your RHB statement format
├── Implement RHBParser (CSV/PDF handling)
├── Analyze Maybank format
├── Implement MaybankParser
├── Write unit tests with sample data
└── Handle edge cases (missing fields, encoding)

Deliverable: RHB and Maybank files parseable
```

**Day 3: T&G + Aeon Parsers**
```
Tasks:
├── Analyze Touch & Go export format
├── Implement TouchNGoParser
├── Analyze Aeon Bank format
├── Implement AeonParser
├── Write unit tests
└── Create manual CSV parser for custom formats

Deliverable: All 4 sources parseable
```

**Day 4: Normalization Pipeline**
```
Tasks:
├── Implement NormalizationService
│   ├── Date standardization (ISO 8601)
│   ├── Amount cleaning (handle negatives, currency symbols)
│   ├── Description cleaning (trim, normalize whitespace)
│   └── Source tagging
├── Implement duplicate detection algorithm
├── Calculate quality score per transaction
└── Create TransactionRepository with bulk insert

Deliverable: Clean, normalized transactions in database
```

**Day 5: Upload UI**
```
Tasks:
├── Create UploadModal component
├── Implement file drag-and-drop
├── Add source type selection
├── Show upload progress
├── Display upload results (count, quality, duplicates)
└── Test with your actual transaction files

Deliverable: Can upload your files through UI
```

### 3.3 Week 2 Checklist

- [ ] RHB parser working
- [ ] Maybank parser working
- [ ] Touch & Go parser working
- [ ] Aeon Bank parser working
- [ ] Normalization pipeline complete
- [ ] Duplicate detection working
- [ ] Quality scoring implemented
- [ ] Upload UI functional
- [ ] Your actual data loaded

### 3.4 Exit Criteria

✅ Upload your 1,448 transactions successfully
✅ All transactions normalized and stored
✅ Quality score > 0.9 for most transactions
✅ Duplicates correctly identified

---

## 4. Week 3: Categorization & Claude Integration

### 4.1 Goals
- Integrate Claude API for transaction categorization
- Implement Categorizer Agent
- Build category correction UI
- Achieve 85%+ categorization accuracy

### 4.2 Daily Breakdown

**Day 1: Claude API Integration**
```
Tasks:
├── Create ClaudeService for API communication
├── Implement rate limiting and retry logic
├── Create ClaudeConfig with API key management
├── Build response parsing utilities
├── Test basic Claude API call
└── Implement error handling

Deliverable: Claude API callable from backend
```

**Day 2: Categorizer Agent**
```
Tasks:
├── Create CategorizerAgent class
├── Implement system prompt from documentation
├── Define tool schema for categorize_transaction
├── Build batch categorization for efficiency
├── Implement response parsing to CategoryResult
└── Create caching layer for repeated descriptions

Deliverable: Agent categorizes transactions
```

**Day 3: Rule-Based Fallback**
```
Tasks:
├── Implement RuleBasedCategorizer
├── Define regex patterns for Malaysian merchants
│   ├── Food: mamak, makan, restaurant patterns
│   ├── Transport: toll, petrol, grab patterns
│   ├── Bills: utility, telco patterns
│   └── etc.
├── Create fallback logic when Claude unavailable
└── Test fallback accuracy

Deliverable: System works without Claude
```

**Day 4: Categorization Pipeline**
```
Tasks:
├── Integrate categorization into upload flow
├── Create CategoryService to orchestrate
├── Implement parallel processing for speed
├── Store category and confidence in database
├── Create API endpoint for manual re-categorization
└── Test with your full dataset

Deliverable: All transactions categorized
```

**Day 5: Category UI**
```
Tasks:
├── Create TransactionList component with categories
├── Add category badges with confidence indicators
├── Implement CategoryCorrection modal
├── Add bulk category update functionality
├── Create category filter in transaction list
└── Test correction flow

Deliverable: Can view and correct categories
```

### 4.3 Week 3 Checklist

- [ ] Claude API integrated
- [ ] Categorizer Agent functional
- [ ] Rule-based fallback working
- [ ] Batch processing implemented
- [ ] Caching for repeated descriptions
- [ ] Category correction UI
- [ ] 85%+ accuracy on your data

### 4.4 Exit Criteria

✅ All 1,448 transactions categorized
✅ Category accuracy > 85% (manual sample check)
✅ Can correct categories through UI
✅ System handles Claude API failures gracefully

---

## 5. Week 4: Debt Detection & Tracking

### 5.1 Goals
- Implement Debt Detector Agent
- Build tri-tier debt model (Formal, BNPL, Hutang)
- Create Hutang management UI
- Load your actual hutang data

### 5.2 Daily Breakdown

**Day 1: Debt Detector Agent**
```
Tasks:
├── Create DebtDetectorAgent class
├── Implement BNPL pattern detection
│   ├── SPayLater patterns
│   ├── GrabPayLater patterns
│   └── Atome patterns
├── Implement formal loan detection
├── Link detected debts to transactions
└── Test with your transaction data

Deliverable: BNPL auto-detected
```

**Day 2: Debt Data Model**
```
Tasks:
├── Implement Debt entity with tier support
├── Implement DebtItem entity for hutang items
├── Create DebtRepository with tier queries
├── Build DebtService with CRUD operations
├── Create debt calculation utilities
└── Test data model

Deliverable: Debt data layer complete
```

**Day 3: Hutang Management**
```
Tasks:
├── Create HutangController with APIs
├── Implement add/edit hutang
├── Implement add item to hutang
├── Implement mark item as paid
├── Link payments to transactions
└── Calculate running balances

Deliverable: Hutang APIs complete
```

**Day 4: Debt Dashboard UI**
```
Tasks:
├── Create DebtDashboard component
├── Build DebtOverviewCard (total, by tier)
├── Create FormalDebtList component
├── Create BNPLTracker component with alerts
├── Create HutangManager component
└── Add AddHutangModal

Deliverable: Debt dashboard functional
```

**Day 5: Load Your Data**
```
Tasks:
├── Import your hutang spreadsheet data
│   ├── Eqi: RM459.74
│   ├── Haziq: RM161.99
│   ├── Dyad: RM91.50
│   └── Ummi: RM1,247.14
├── Create data import utility
├── Verify all debt calculations
├── Test full debt flow end-to-end
└── Polish UI based on real data

Deliverable: Your actual debt data visible
```

### 5.3 Week 4 Checklist

- [ ] Debt Detector Agent working
- [ ] BNPL auto-detection functional
- [ ] Hutang CRUD APIs complete
- [ ] Debt dashboard showing all tiers
- [ ] Your hutang data imported
- [ ] Payment tracking working
- [ ] Debt-to-income calculation

### 5.4 Exit Criteria

✅ All 3 debt tiers visible in dashboard
✅ Your 4 hutang relationships imported correctly
✅ Can add new hutang items
✅ Can mark items as paid
✅ BNPL exposure percentage calculated

---

## 6. Week 5: Pattern Analysis

### 6.1 Goals
- Implement Pattern Analyzer Agent
- Detect hidden costs (tolls, commute)
- Implement market basket analysis
- Reveal lifestyle bundles

### 6.2 Daily Breakdown

**Day 1: Pattern Analyzer Agent**
```
Tasks:
├── Create PatternAnalyzerAgent class
├── Implement system prompt for Malaysian context
├── Define pattern types (Bundle, Trend, Anomaly, Hidden Cost)
├── Build pattern output parsing
└── Test with sample data

Deliverable: Agent generates patterns
```

**Day 2: Hidden Cost Detection**
```
Tasks:
├── Implement toll aggregation logic
├── Calculate true commute cost (toll + petrol)
├── Identify underestimated recurring costs
├── Create hidden cost report structure
└── Test with your toll data (251 transactions)

Deliverable: Toll blindspot revealed
```

**Day 3: Market Basket Analysis**
```
Tasks:
├── Implement daily transaction baskets
├── Create Apriori algorithm integration
│   ├── Find frequent itemsets
│   ├── Generate association rules
│   └── Calculate lift scores
├── Detect lifestyle bundles
└── Format bundle insights

Deliverable: Bundles detected (e.g., Weekend Splurge)
```

**Day 4: Trend & Anomaly Detection**
```
Tasks:
├── Implement category trend analysis
├── Calculate month-over-month changes
├── Detect spending anomalies (outliers)
├── Create trend visualization data
└── Test anomaly detection accuracy

Deliverable: Trends and anomalies identified
```

**Day 5: Pattern UI**
```
Tasks:
├── Create PatternCards component
├── Build HiddenCostCard with toll breakdown
├── Create BundleVisualization component
├── Add TrendChart component
├── Integrate into Insights page
└── Polish with your actual insights

Deliverable: Patterns visible in dashboard
```

### 6.3 Week 5 Checklist

- [ ] Pattern Analyzer Agent working
- [ ] Hidden toll cost calculated
- [ ] Market basket analysis running
- [ ] Lifestyle bundles detected
- [ ] Trends calculated
- [ ] Anomalies flagged
- [ ] Pattern UI complete

### 6.4 Exit Criteria

✅ Your RM487/month toll spending revealed
✅ At least 2-3 lifestyle bundles detected
✅ Category trends visible (rising/falling)
✅ Anomalies correctly identified

---

## 7. Week 6: Prediction Engine

### 7.1 Goals
- Implement Predictor Agent
- Build time-series forecasting
- Add Malaysian calendar awareness
- Create scenario modeling

### 7.2 Daily Breakdown

**Day 1: Predictor Agent**
```
Tasks:
├── Create PredictorAgent class
├── Implement system prompt with Malaysian context
├── Define prediction output schema
├── Build historical data preparation
└── Test basic prediction

Deliverable: Agent generates predictions
```

**Day 2: Fixed Commitment Detection**
```
Tasks:
├── Identify recurring transactions (same amount, monthly)
├── Detect loan repayments from patterns
├── Extract BNPL remaining installments
├── Calculate total fixed obligations
└── Store as prediction inputs

Deliverable: Fixed commitments identified
```

**Day 3: Variable Spending Forecast**
```
Tasks:
├── Implement 3-month rolling average
├── Add day-count adjustments
├── Calculate category volatility
├── Generate confidence intervals
└── Test prediction accuracy (backtest)

Deliverable: Variable predictions with confidence
```

**Day 4: Malaysian Calendar Integration**
```
Tasks:
├── Create MalaysianCalendar utility
├── Add Raya/CNY/Deepavali adjustments
├── Add school holiday factors
├── Implement payday timing logic
├── Adjust predictions for context
└── Test seasonal accuracy

Deliverable: Context-aware predictions
```

**Day 5: Prediction UI**
```
Tasks:
├── Create PredictionPanel component
├── Build ForecastChart with confidence bands
├── Add FixedCommitmentsList
├── Create ScenarioModeler component
├── Integrate into dashboard
└── Test with February 2026 prediction

Deliverable: Prediction dashboard complete
```

### 7.3 Week 6 Checklist

- [ ] Predictor Agent working
- [ ] Fixed commitments detected
- [ ] Variable forecasting implemented
- [ ] Confidence intervals calculated
- [ ] Malaysian calendar integrated
- [ ] Scenario modeling working
- [ ] Prediction UI complete

### 7.4 Exit Criteria

✅ February 2026 prediction generated
✅ Fixed commitments correctly totaled
✅ Confidence intervals reasonable
✅ Can run what-if scenarios

---

## 8. Week 7: Advisor System & Query

### 8.1 Goals
- Implement Advisor Agent
- Build financial health scoring
- Create personalized advice generation
- Implement Query Agent for NL questions

### 8.2 Daily Breakdown

**Day 1: Financial Health Score**
```
Tasks:
├── Define health score algorithm
│   ├── Debt-to-income (25%)
│   ├── Savings rate (25%)
│   ├── Emergency fund (20%)
│   ├── Bill timeliness (15%)
│   └── Spending stability (15%)
├── Implement HealthScoreService
├── Calculate your current score
└── Create score history tracking

Deliverable: Health score calculated
```

**Day 2: Advisor Agent**
```
Tasks:
├── Create AdvisorAgent class
├── Implement culturally-aware system prompt
├── Define advice priority levels
├── Build advice generation pipeline
├── Create advice templates for common scenarios
└── Test advice quality

Deliverable: Agent generates advice
```

**Day 3: Advice Management**
```
Tasks:
├── Create AdviceService with CRUD
├── Implement advice prioritization
├── Add read/helpful/snooze tracking
├── Create advice expiration logic
├── Build advice refresh scheduler
└── Test advice lifecycle

Deliverable: Advice management complete
```

**Day 4: Query Agent**
```
Tasks:
├── Create QueryAgent class
├── Implement NL understanding
├── Build query-to-data mapping
├── Support English and Malay
├── Create response formatting
└── Test with sample queries

Deliverable: Can answer "How much did I spend on food?"
```

**Day 5: Advisor UI**
```
Tasks:
├── Create HealthScoreCard with breakdown
├── Build AdviceList component
├── Create AdviceCard with actions
├── Add QueryInput for NL questions
├── Integrate into dashboard
└── Polish interaction flows

Deliverable: Advisor system complete
```

### 8.3 Week 7 Checklist

- [ ] Health score algorithm implemented
- [ ] Advisor Agent generating advice
- [ ] Advice prioritization working
- [ ] Advice feedback tracking
- [ ] Query Agent answering questions
- [ ] Bilingual support (EN/BM)
- [ ] Advisor UI complete

### 8.4 Exit Criteria

✅ Your financial health score calculated
✅ At least 3-5 pieces of relevant advice
✅ Can ask "Berapa saya belanja makan bulan lepas?"
✅ Advice can be marked helpful/snoozed

---

## 9. Week 8: Polish & Deploy

### 9.1 Goals
- Containerize application with Docker
- Deploy to AWS
- Complete documentation
- Prepare demo and portfolio materials

### 9.2 Daily Breakdown

**Day 1: Docker & Testing**
```
Tasks:
├── Create production Dockerfile
├── Optimize build (multi-stage)
├── Create docker-compose.prod.yml
├── Run full integration tests
├── Fix any bugs discovered
└── Verify all features work in container

Deliverable: Containerized application
```

**Day 2: AWS Deployment**
```
Tasks:
├── Set up EC2 instance (t3.micro)
├── Configure security groups
├── Set up RDS PostgreSQL instance
├── Configure environment variables
├── Deploy application
└── Set up domain (optional)

Deliverable: Application live on AWS
```

**Day 3: Monitoring & Security**
```
Tasks:
├── Configure Sentry error tracking
├── Set up Plausible analytics (optional)
├── Implement rate limiting
├── Security audit (OWASP checklist)
├── Set up SSL/TLS
└── Configure backups

Deliverable: Production-ready security
```

**Day 4: Documentation**
```
Tasks:
├── Complete README with screenshots
├── Write API documentation
├── Create setup guide
├── Document architecture decisions
├── Write interview talking points
└── Create portfolio description

Deliverable: Comprehensive documentation
```

**Day 5: Demo Preparation**
```
Tasks:
├── Record demo video (5-10 min)
├── Prepare live demo script
├── Create presentation slides (optional)
├── Test demo end-to-end
├── Prepare for common questions
└── Celebrate! 🎉

Deliverable: Portfolio-ready project
```

### 9.3 Week 8 Checklist

- [ ] Docker build successful
- [ ] Deployed to AWS
- [ ] HTTPS enabled
- [ ] Sentry configured
- [ ] README complete with screenshots
- [ ] Demo video recorded
- [ ] Interview talking points ready

### 9.4 Exit Criteria

✅ Live demo accessible
✅ Zero crashes in 1-hour testing
✅ Documentation complete
✅ Demo video uploaded
✅ Portfolio entry written

---

## 10. Risk Mitigation

### 10.1 Risk Matrix

| Risk | Probability | Impact | Mitigation | Trigger |
|------|-------------|--------|------------|---------|
| Scope creep | High | High | Strict weekly milestones | Any feature request after Week 6 |
| Claude API issues | Medium | Medium | Rule-based fallback ready | API down > 1 hour |
| Time underestimation | High | High | Cut features, not quality | Behind schedule by Week 4 |
| Bank format changes | Low | Medium | Modular parsers | Can't parse new file |
| AWS costs exceed free tier | Low | Medium | Monitor daily, set alerts | Any unexpected charges |

### 10.2 Feature Triage (If Behind Schedule)

**Must Have (Core):**
- Transaction upload & display
- Basic categorization
- Debt tracking (all 3 tiers)
- Simple spending summary
- Basic predictions

**Should Have:**
- Pattern analysis
- Market basket bundles
- Financial health score
- Personalized advice

**Could Have (Cut First):**
- NL query agent
- Scenario modeling
- Detailed trend charts
- Advice feedback tracking

---

## 11. Definition of Done

### 11.1 Feature Complete Criteria

Each feature is "done" when:
- [ ] Code written and working
- [ ] Unit tests passing (if applicable)
- [ ] Manual testing completed
- [ ] UI polished and responsive
- [ ] Error handling implemented
- [ ] Documentation updated

### 11.2 Week Complete Criteria

Each week is "done" when:
- [ ] All checklist items completed
- [ ] Exit criteria verified
- [ ] No critical bugs outstanding
- [ ] Code committed and pushed
- [ ] Brief progress note written

### 11.3 Project Complete Criteria

Project is "done" when:
- [ ] All 8 week checklists complete
- [ ] Live demo working reliably
- [ ] Documentation comprehensive
- [ ] Demo video recorded
- [ ] Portfolio entry published
- [ ] Ready for job interviews

---

**Document End**

*Next Document: 07_FRONTEND_COMPONENTS.md*
