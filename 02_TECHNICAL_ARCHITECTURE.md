# DuitSedar — Technical Architecture Document

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026  
**Status:** Approved for Development

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [System Components](#2-system-components)
3. [Claude Agent Architecture](#3-claude-agent-architecture)
4. [Data Flow](#4-data-flow)
5. [Technology Stack Details](#5-technology-stack-details)
6. [Integration Architecture](#6-integration-architecture)
7. [Security Architecture](#7-security-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [Scalability Considerations](#9-scalability-considerations)

---

## 1. Architecture Overview

### 1.1 High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                    CLIENT LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                           React Frontend (TypeScript)                            │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐│ │
│  │  │  Dashboard   │ │ Transactions │ │    Debts     │ │   Insights & Advisor     ││ │
│  │  │   Module     │ │    Module    │ │   Module     │ │        Module            ││ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────────┘│ │
│  │  ┌──────────────────────────────────────────────────────────────────────────────┐│ │
│  │  │                    State Management (Zustand / React Query)                  ││ │
│  │  └──────────────────────────────────────────────────────────────────────────────┘│ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          │ HTTPS / REST API
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                   API GATEWAY LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                        Spring Boot Application (Java 17)                         │ │
│  │  ┌───────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                         REST Controllers                                   │  │ │
│  │  │  /api/v1/transactions  │  /api/v1/debts  │  /api/v1/analysis  │  /api/v1/advice │ │
│  │  └───────────────────────────────────────────────────────────────────────────┘  │ │
│  │  ┌───────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                         Security Layer (Clerk JWT)                         │  │ │
│  │  └───────────────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                   SERVICE LAYER                                       │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐ │
│  │  Transaction    │ │     Debt        │ │    Analysis     │ │      Advisor        │ │
│  │    Service      │ │    Service      │ │    Service      │ │      Service        │ │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └──────────┬──────────┘ │
│           │                   │                   │                      │           │
│           └───────────────────┴───────────────────┴──────────────────────┘           │
│                                          │                                           │
│                                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                         CLAUDE AGENT ORCHESTRATOR                                │ │
│  │                      (Coordinates AI Agent Operations)                           │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                               CLAUDE AGENT LAYER                                      │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐            │
│  │  Categorizer  │ │    Debt       │ │   Pattern     │ │   Predictor   │            │
│  │    Agent      │ │   Detector    │ │   Analyzer    │ │    Agent      │            │
│  └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘            │
│  ┌───────────────┐ ┌───────────────┐                                                │
│  │    Query      │ │   Advisor     │                                                │
│  │    Agent      │ │    Agent      │                                                │
│  └───────────────┘ └───────────────┘                                                │
│                            │                                                         │
│                            │ Claude API (Anthropic)                                  │
│                            ▼                                                         │
│              ┌─────────────────────────────┐                                        │
│              │    Claude 3.5 Sonnet API    │                                        │
│              │    (Tool Use / Agents)      │                                        │
│              └─────────────────────────────┘                                        │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                   DATA LAYER                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                      PostgreSQL 15 (AWS RDS Free Tier)                          │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐           │ │
│  │  │ transactions │ │    debts     │ │  predictions │ │    advice    │           │ │
│  │  │  + vectors   │ │ + debt_items │ │              │ │              │           │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘           │ │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    pgvector Extension (Embeddings)                        │  │ │
│  │  └──────────────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Architecture Principles

| Principle | Implementation |
|-----------|----------------|
| **Separation of Concerns** | Clear boundaries between UI, API, Service, Agent, and Data layers |
| **Agent-First AI** | All AI operations routed through Claude agents with defined responsibilities |
| **Stateless API** | REST endpoints with JWT authentication, no server-side sessions |
| **Data Integrity** | All transactions normalized, validated, and audit-logged |
| **Graceful Degradation** | System functional if AI unavailable (fallback to rules) |
| **Security by Design** | Input validation, rate limiting, encryption at every layer |

---

## 2. System Components

### 2.1 Frontend Components

```
src/
├── components/
│   ├── common/
│   │   ├── Card.tsx
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   ├── Loading.tsx
│   │   └── ErrorBoundary.tsx
│   ├── dashboard/
│   │   ├── HealthScoreCard.tsx
│   │   ├── SpendingChart.tsx
│   │   ├── DebtOverview.tsx
│   │   └── QuickInsights.tsx
│   ├── transactions/
│   │   ├── TransactionList.tsx
│   │   ├── TransactionRow.tsx
│   │   ├── UploadModal.tsx
│   │   ├── CategoryFilter.tsx
│   │   └── CategoryCorrection.tsx
│   ├── debts/
│   │   ├── DebtDashboard.tsx
│   │   ├── FormalDebtCard.tsx
│   │   ├── BNPLTracker.tsx
│   │   ├── HutangManager.tsx
│   │   └── AddHutangModal.tsx
│   ├── insights/
│   │   ├── PatternCards.tsx
│   │   ├── PredictionPanel.tsx
│   │   ├── TrendChart.tsx
│   │   └── BundleVisualization.tsx
│   └── advisor/
│       ├── AdviceList.tsx
│       ├── AdviceCard.tsx
│       ├── QueryInput.tsx
│       └── HealthScoreDetail.tsx
├── hooks/
│   ├── useTransactions.ts
│   ├── useDebts.ts
│   ├── useAnalysis.ts
│   └── useAdvice.ts
├── services/
│   ├── api.ts
│   ├── auth.ts
│   └── fileParser.ts
├── store/
│   └── index.ts (Zustand)
└── types/
    └── index.ts
```

### 2.2 Backend Components

```
src/main/java/com/duitsedar/
├── DuitSedarApplication.java
├── config/
│   ├── SecurityConfig.java
│   ├── ClaudeConfig.java
│   ├── CorsConfig.java
│   └── DatabaseConfig.java
├── controller/
│   ├── TransactionController.java
│   ├── DebtController.java
│   ├── HutangController.java
│   ├── AnalysisController.java
│   ├── PredictionController.java
│   ├── AdviceController.java
│   └── QueryController.java
├── service/
│   ├── TransactionService.java
│   ├── DebtService.java
│   ├── AnalysisService.java
│   ├── PredictionService.java
│   ├── AdviceService.java
│   └── QueryService.java
├── agent/
│   ├── AgentOrchestrator.java
│   ├── CategorizerAgent.java
│   ├── DebtDetectorAgent.java
│   ├── PatternAnalyzerAgent.java
│   ├── PredictorAgent.java
│   ├── QueryAgent.java
│   └── AdvisorAgent.java
├── parser/
│   ├── StatementParser.java
│   ├── RHBParser.java
│   ├── MaybankParser.java
│   ├── TouchNGoParser.java
│   └── AeonParser.java
├── model/
│   ├── entity/
│   │   ├── User.java
│   │   ├── Transaction.java
│   │   ├── Debt.java
│   │   ├── DebtItem.java
│   │   ├── Prediction.java
│   │   └── Advice.java
│   ├── dto/
│   │   ├── TransactionDTO.java
│   │   ├── DebtDTO.java
│   │   ├── AnalysisDTO.java
│   │   └── AdviceDTO.java
│   └── enums/
│       ├── Category.java
│       ├── DebtTier.java
│       └── AdvicePriority.java
├── repository/
│   ├── TransactionRepository.java
│   ├── DebtRepository.java
│   ├── PredictionRepository.java
│   └── AdviceRepository.java
├── exception/
│   ├── GlobalExceptionHandler.java
│   ├── ParsingException.java
│   └── AgentException.java
└── util/
    ├── DateUtils.java
    ├── AmountUtils.java
    └── ValidationUtils.java
```

---

## 3. Claude Agent Architecture

### 3.1 Agent Design Philosophy

DuitSedar uses Claude's tool-use capabilities to create specialized agents, each with:
- **Defined responsibility** (single-purpose)
- **Specific tools** (functions it can call)
- **Clear inputs/outputs** (typed contracts)
- **Fallback behavior** (graceful degradation)

### 3.2 Agent Definitions

#### 3.2.1 Categorizer Agent

**Purpose:** Classify transactions into spending categories

**System Prompt:**
```
You are a Malaysian financial transaction categorizer. Your job is to analyze transaction 
descriptions and assign the most appropriate spending category.

Context:
- Transactions may be in Malay, English, or mixed (Manglish)
- Malaysian-specific merchants: mamak stalls, pasar malam, toll plazas (PLUS, LDP, DUKE)
- E-wallet transactions from Touch & Go, GrabPay, ShopeePay

Categories:
- FOOD: Restaurants, groceries, food delivery, mamak
- TRANSPORT: Toll, petrol, parking, Grab rides, public transit
- BILLS: Utilities, phone, internet, subscriptions
- ENTERTAINMENT: Movies, games, streaming, leisure
- SHOPPING: Retail, online shopping (non-food)
- TRANSFER: Money transfers between accounts
- DEBT_PAYMENT: Loan repayments, BNPL installments
- INCOME: Salary, deposits, refunds
- OTHER: Anything that doesn't fit above

For each transaction, return:
1. category: The most appropriate category
2. confidence: 0.0-1.0 confidence score
3. reasoning: Brief explanation (for debugging)
```

**Tools:**
```json
{
  "name": "categorize_transaction",
  "description": "Categorize a single transaction",
  "input_schema": {
    "type": "object",
    "properties": {
      "description": {"type": "string", "description": "Transaction description"},
      "amount": {"type": "number", "description": "Transaction amount in RM"},
      "source": {"type": "string", "description": "Bank or e-wallet source"},
      "date": {"type": "string", "description": "Transaction date"}
    },
    "required": ["description", "amount"]
  }
}
```

**Output Schema:**
```json
{
  "category": "FOOD",
  "confidence": 0.92,
  "reasoning": "Mamak Hj Syed is a common mamak restaurant name in Malaysia",
  "subcategory": "restaurant",
  "merchant_name": "Mamak Hj Syed"
}
```

#### 3.2.2 Debt Detector Agent

**Purpose:** Identify debt-related transactions and classify debt types

**System Prompt:**
```
You are a Malaysian debt detection specialist. Your job is to identify transactions 
that represent debt obligations and classify them into tiers.

Debt Tiers:
1. FORMAL: Bank loans (PTPTN, car loan, personal loan, housing loan)
   - Patterns: Regular monthly amounts, bank names, "loan", "installment"
   
2. BNPL (Buy Now Pay Later):
   - Providers: SPayLater, GrabPayLater, Atome, Split
   - Patterns: "SPAYLATER", "GPL", "ATOME", installment references
   
3. HUTANG (Informal):
   - Transfers with names in description
   - Comments mentioning "hutang", "pinjam", "bayar balik"

For each transaction, determine:
1. is_debt: Boolean - is this debt-related?
2. debt_tier: FORMAL, BNPL, HUTANG, or null
3. debt_details: Provider name, estimated remaining balance if detectable
```

**Tools:**
```json
{
  "name": "detect_debt",
  "description": "Analyze transaction for debt indicators",
  "input_schema": {
    "type": "object",
    "properties": {
      "description": {"type": "string"},
      "amount": {"type": "number"},
      "source": {"type": "string"},
      "is_recurring": {"type": "boolean"},
      "comment": {"type": "string"}
    },
    "required": ["description", "amount"]
  }
}
```

#### 3.2.3 Pattern Analyzer Agent

**Purpose:** Discover spending patterns and lifestyle bundles

**System Prompt:**
```
You are a financial behavior analyst specializing in Malaysian spending patterns.
Your job is to identify hidden patterns in transaction data.

Pattern Types to Detect:
1. TEMPORAL: Day-of-week patterns, month-end spending spikes, payday effects
2. BUNDLE: Co-occurring categories (entertainment + food = "night out")
3. TREND: Increasing/decreasing categories over time
4. ANOMALY: Unusual spending compared to baseline
5. HIDDEN_COST: Underestimated recurring expenses (tolls, subscriptions)

Malaysian Context:
- Toll spending often underestimated (PLUS, LDP, DUKE, SMART, AKLEH)
- Weekend spending patterns different from weekdays
- Festival periods (Raya, CNY, Deepavali) show spending spikes
- Payday typically 25th-30th of month

Output detailed patterns with:
- Pattern description
- Supporting data points
- Estimated monthly/annual impact
- Confidence level
```

**Tools:**
```json
{
  "name": "analyze_patterns",
  "description": "Analyze transaction patterns",
  "input_schema": {
    "type": "object",
    "properties": {
      "transactions": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "date": {"type": "string"},
            "category": {"type": "string"},
            "amount": {"type": "number"},
            "description": {"type": "string"}
          }
        }
      },
      "analysis_type": {
        "type": "string",
        "enum": ["temporal", "bundle", "trend", "anomaly", "hidden_cost", "all"]
      }
    },
    "required": ["transactions"]
  }
}
```

#### 3.2.4 Predictor Agent

**Purpose:** Forecast future spending based on historical patterns

**System Prompt:**
```
You are a financial forecasting specialist for Malaysian personal finance.
Your job is to predict next month's spending based on historical data.

Prediction Methodology:
1. Fixed Commitments: Loans, bills, subscriptions (high confidence)
2. Variable Spending: Historical average with seasonal adjustment
3. Malaysian Calendar: 
   - Ramadan: Food spending shifts
   - Raya/CNY/Deepavali: +50-100% spending
   - School holidays: +20% for families
   - Month-end: Higher spending (payday effect)

Output:
- Total predicted spending with confidence interval
- Category-level predictions
- Risk flags (potential shortfall)
- Key assumptions
```

#### 3.2.5 Query Agent

**Purpose:** Answer natural language questions about finances

**System Prompt:**
```
You are a helpful financial assistant for Malaysian users.
Your job is to answer questions about their financial data accurately and helpfully.

Capabilities:
- Query transaction history ("How much did I spend on food last month?")
- Calculate totals and averages
- Compare periods
- Find specific transactions
- Explain patterns

Language:
- Respond in the same language as the question (Malay or English)
- Understand mixed language (Manglish)
- Use RM for currency

Always:
- Cite specific data points
- Show your calculation
- Offer follow-up suggestions
```

#### 3.2.6 Advisor Agent

**Purpose:** Generate personalized, culturally-aware financial advice

**System Prompt:**
```
You are a compassionate financial advisor for young Malaysian professionals.
Your job is to provide helpful, non-judgmental guidance.

Advisory Principles:
1. NEVER lecture or shame
2. Celebrate small wins
3. Respect cultural obligations (family support, zakat)
4. Provide actionable steps
5. Explain the "why"

Priority Levels:
- URGENT: Immediate financial risk (e.g., BNPL > 30% income)
- IMPORTANT: Should address soon (e.g., no emergency fund)
- GROWTH: Long-term improvement (e.g., increase savings rate)

Malaysian Context:
- Family support to parents is cultural norm, not waste
- Wedding savings is legitimate priority
- Zakat obligations are non-negotiable for Muslims
- Festival spending has social importance

Advice Format:
- Observation: "Your toll spending is RM487/month"
- Insight: "That's 11% of your income"
- Comparison: "Average is 7% for your income bracket"
- Suggestion: "Consider carpooling 2x/week"
- Impact: "Could save RM120/month = RM1,440/year"
```

### 3.3 Agent Orchestration

```java
@Service
public class AgentOrchestrator {
    
    private final CategorizerAgent categorizer;
    private final DebtDetectorAgent debtDetector;
    private final PatternAnalyzerAgent patternAnalyzer;
    private final PredictorAgent predictor;
    private final QueryAgent queryAgent;
    private final AdvisorAgent advisor;
    
    /**
     * Process new transactions through categorization and debt detection
     */
    public List<ProcessedTransaction> processTransactions(List<RawTransaction> transactions) {
        return transactions.stream()
            .map(txn -> {
                // Step 1: Categorize
                CategoryResult category = categorizer.categorize(txn);
                
                // Step 2: Detect debt
                DebtResult debt = debtDetector.detect(txn);
                
                return ProcessedTransaction.builder()
                    .raw(txn)
                    .category(category.getCategory())
                    .categoryConfidence(category.getConfidence())
                    .isDebtRelated(debt.isDebt())
                    .debtTier(debt.getTier())
                    .build();
            })
            .collect(Collectors.toList());
    }
    
    /**
     * Generate insights for dashboard
     */
    public DashboardInsights generateInsights(String userId) {
        List<Transaction> transactions = transactionRepository.findByUserId(userId);
        
        // Parallel agent invocations
        CompletableFuture<List<Pattern>> patterns = 
            CompletableFuture.supplyAsync(() -> patternAnalyzer.analyze(transactions));
        
        CompletableFuture<Prediction> prediction = 
            CompletableFuture.supplyAsync(() -> predictor.predict(transactions));
        
        CompletableFuture<List<Advice>> advice = 
            CompletableFuture.supplyAsync(() -> advisor.generate(transactions));
        
        return DashboardInsights.builder()
            .patterns(patterns.join())
            .prediction(prediction.join())
            .advice(advice.join())
            .build();
    }
    
    /**
     * Handle natural language query
     */
    public QueryResponse handleQuery(String userId, String query) {
        List<Transaction> transactions = transactionRepository.findByUserId(userId);
        return queryAgent.answer(query, transactions);
    }
}
```

### 3.4 Claude API Integration

```java
@Service
public class ClaudeService {
    
    private final String apiKey;
    private final String model = "claude-sonnet-4-20250514";
    private final RestTemplate restTemplate;
    
    public ClaudeResponse invokeAgent(String systemPrompt, String userMessage, List<Tool> tools) {
        HttpHeaders headers = new HttpHeaders();
        headers.set("x-api-key", apiKey);
        headers.set("anthropic-version", "2023-06-01");
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        Map<String, Object> body = Map.of(
            "model", model,
            "max_tokens", 4096,
            "system", systemPrompt,
            "messages", List.of(Map.of("role", "user", "content", userMessage)),
            "tools", tools
        );
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);
        
        ResponseEntity<ClaudeResponse> response = restTemplate.postForEntity(
            "https://api.anthropic.com/v1/messages",
            request,
            ClaudeResponse.class
        );
        
        return response.getBody();
    }
}
```

### 3.5 Agent Prompt Templates

All agent prompts are stored in a configuration file for easy maintenance:

```yaml
# agent-prompts.yml

categorizer:
  system: |
    You are a Malaysian financial transaction categorizer...
    [full prompt]
  temperature: 0.3
  max_tokens: 500

debt_detector:
  system: |
    You are a Malaysian debt detection specialist...
    [full prompt]
  temperature: 0.2
  max_tokens: 500

pattern_analyzer:
  system: |
    You are a financial behavior analyst...
    [full prompt]
  temperature: 0.5
  max_tokens: 2000

predictor:
  system: |
    You are a financial forecasting specialist...
    [full prompt]
  temperature: 0.4
  max_tokens: 1500

query:
  system: |
    You are a helpful financial assistant...
    [full prompt]
  temperature: 0.7
  max_tokens: 1000

advisor:
  system: |
    You are a compassionate financial advisor...
    [full prompt]
  temperature: 0.6
  max_tokens: 2000
```

---

## 4. Data Flow

### 4.1 Transaction Upload Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TRANSACTION UPLOAD FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

User                    Frontend                Backend                  Claude
 │                         │                       │                        │
 │  Upload bank statement  │                       │                        │
 │ ───────────────────────>│                       │                        │
 │                         │                       │                        │
 │                         │  POST /api/v1/transactions/upload              │
 │                         │ ──────────────────────>│                       │
 │                         │                       │                        │
 │                         │                       │  Detect file type      │
 │                         │                       │  (PDF/CSV/Excel)       │
 │                         │                       │                        │
 │                         │                       │  Select appropriate    │
 │                         │                       │  parser                │
 │                         │                       │                        │
 │                         │                       │  Parse raw transactions│
 │                         │                       │                        │
 │                         │                       │  For each transaction: │
 │                         │                       │ ───────────────────────>│
 │                         │                       │                        │ Categorize
 │                         │                       │ <───────────────────────│
 │                         │                       │                        │
 │                         │                       │ ───────────────────────>│
 │                         │                       │                        │ Detect debt
 │                         │                       │ <───────────────────────│
 │                         │                       │                        │
 │                         │                       │  Save to database      │
 │                         │                       │                        │
 │                         │                       │  Calculate quality     │
 │                         │                       │  score                 │
 │                         │                       │                        │
 │                         │  Return upload summary │                       │
 │                         │ <──────────────────────│                       │
 │                         │                        │                       │
 │  Show upload results    │                        │                       │
 │ <───────────────────────│                        │                       │
 │                         │                        │                       │
```

### 4.2 Dashboard Load Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DASHBOARD LOAD FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

User                    Frontend                Backend                  Claude
 │                         │                       │                        │
 │  Navigate to dashboard  │                       │                        │
 │ ───────────────────────>│                       │                        │
 │                         │                       │                        │
 │                         │  GET /api/v1/analysis/summary                  │
 │                         │ ──────────────────────>│                       │
 │                         │                       │                        │
 │                         │                       │  Fetch transactions    │
 │                         │                       │  from DB               │
 │                         │                       │                        │
 │                         │                       │  Calculate spending    │
 │                         │                       │  breakdown (cached)    │
 │                         │                       │                        │
 │                         │  GET /api/v1/debts/summary                     │
 │                         │ ──────────────────────>│                       │
 │                         │                       │                        │
 │                         │                       │  Aggregate debt totals │
 │                         │                       │                        │
 │                         │  GET /api/v1/predictions/next-month            │
 │                         │ ──────────────────────>│                       │
 │                         │                       │ ───────────────────────>│
 │                         │                       │                        │ Predict
 │                         │                       │ <───────────────────────│
 │                         │                       │                        │
 │                         │  GET /api/v1/advice                            │
 │                         │ ──────────────────────>│                       │
 │                         │                       │ ───────────────────────>│
 │                         │                       │                        │ Generate advice
 │                         │                       │ <───────────────────────│
 │                         │                       │                        │
 │                         │  Return all dashboard data                     │
 │                         │ <──────────────────────│                       │
 │                         │                        │                       │
 │  Render dashboard       │                        │                       │
 │ <───────────────────────│                        │                       │
```

---

## 5. Technology Stack Details

### 5.1 Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | Spring Boot | 3.2.x | REST API, DI, Configuration |
| Language | Java | 17 LTS | Primary backend language |
| Build | Gradle | 8.x | Dependency management, build |
| ORM | Spring Data JPA | 3.2.x | Database access |
| Database | PostgreSQL | 15.x | Primary data store |
| Vector Search | pgvector | 0.5.x | Embedding similarity search |
| HTTP Client | RestTemplate / WebClient | - | Claude API calls |
| Validation | Jakarta Validation | 3.0 | Input validation |
| Logging | SLF4J + Logback | - | Structured logging |
| Testing | JUnit 5 + Mockito | - | Unit and integration tests |

### 5.2 Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | React | 18.x | UI framework |
| Language | TypeScript | 5.x | Type safety |
| Build | Vite | 5.x | Fast development server, bundling |
| State | Zustand | 4.x | Global state management |
| Data Fetching | TanStack Query | 5.x | Server state, caching |
| Routing | React Router | 6.x | Client-side routing |
| Styling | TailwindCSS | 3.x | Utility-first CSS |
| Charts | Recharts | 2.x | Data visualization |
| Forms | React Hook Form | 7.x | Form handling |
| Icons | Lucide React | - | Icon library |
| Testing | Vitest + Testing Library | - | Component testing |

### 5.3 Infrastructure Stack

| Component | Technology | Tier | Purpose |
|-----------|------------|------|---------|
| Compute | AWS EC2 | t3.micro (free tier) | Application hosting |
| Database | AWS RDS | db.t3.micro (free tier) | PostgreSQL hosting |
| Containerization | Docker | - | Application packaging |
| CI/CD | GitHub Actions | Free | Automated builds, deploys |
| Auth | Clerk | Free tier | Authentication |
| Monitoring | Sentry | Free tier | Error tracking |
| Analytics | Plausible | Self-hosted / Free | Usage analytics |

---

## 6. Integration Architecture

### 6.1 Clerk Authentication

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                           │
└─────────────────────────────────────────────────────────────────┘

Browser                 Clerk                   Backend
   │                      │                        │
   │  Login request       │                        │
   │ ────────────────────>│                        │
   │                      │                        │
   │  JWT token           │                        │
   │ <────────────────────│                        │
   │                      │                        │
   │  API request + JWT   │                        │
   │ ─────────────────────────────────────────────>│
   │                      │                        │
   │                      │  Verify JWT with Clerk │
   │                      │ <──────────────────────│
   │                      │                        │
   │                      │  JWT valid             │
   │                      │ ──────────────────────>│
   │                      │                        │
   │  API response        │                        │
   │ <─────────────────────────────────────────────│
```

### 6.2 Claude API Integration

```java
@Configuration
public class ClaudeConfig {
    
    @Value("${claude.api.key}")
    private String apiKey;
    
    @Value("${claude.api.model}")
    private String model;
    
    @Bean
    public ClaudeClient claudeClient() {
        return ClaudeClient.builder()
            .apiKey(apiKey)
            .model(model)
            .timeout(Duration.ofSeconds(30))
            .retryPolicy(RetryPolicy.exponentialBackoff(3))
            .build();
    }
}
```

---

## 7. Security Architecture

### 7.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────┐
                        │    Rate Limiting    │
                        │  (100 req/min/user) │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Input Validation  │
                        │  (All user inputs)  │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Authentication    │
                        │   (Clerk JWT)       │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Authorization     │
                        │   (User can only    │
                        │    access own data) │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Data Encryption   │
                        │   (TLS in transit,  │
                        │    AES at rest)     │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Audit Logging     │
                        │   (All data access) │
                        └─────────────────────┘
```

### 7.2 OWASP Top 10 Mitigations

| Risk | Mitigation |
|------|------------|
| A01: Broken Access Control | Row-level security, user-scoped queries |
| A02: Cryptographic Failures | TLS 1.3, AES-256 encryption |
| A03: Injection | Parameterized queries, input sanitization |
| A04: Insecure Design | Threat modeling, secure defaults |
| A05: Security Misconfiguration | Environment-specific configs, secrets management |
| A06: Vulnerable Components | Dependency scanning, regular updates |
| A07: Authentication Failures | Clerk managed auth, JWT validation |
| A08: Software Integrity Failures | Signed dependencies, CI/CD security |
| A09: Logging Failures | Comprehensive audit logging |
| A10: SSRF | URL validation, allowlisting |

---

## 8. Deployment Architecture

### 8.1 AWS Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                         AWS ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────┘

Internet
    │
    ▼
┌─────────────────┐
│   Route 53      │ (Optional: Custom domain)
│   DNS           │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   EC2 Instance  │
│   t3.micro      │
│                 │
│ ┌─────────────┐ │
│ │   Docker    │ │
│ │  Container  │ │
│ │             │ │
│ │ Spring Boot │ │
│ │    +        │ │
│ │   React     │ │
│ │  (static)   │ │
│ └─────────────┘ │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   RDS Instance  │
│   db.t3.micro   │
│                 │
│   PostgreSQL    │
│   + pgvector    │
└─────────────────┘
```

### 8.2 Docker Configuration

```dockerfile
# Dockerfile
FROM eclipse-temurin:17-jdk-alpine as builder
WORKDIR /app
COPY . .
RUN ./gradlew build -x test

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=prod
      - DATABASE_URL=${DATABASE_URL}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - CLERK_SECRET_KEY=${CLERK_SECRET_KEY}
    depends_on:
      - db
  
  db:
    image: pgvector/pgvector:pg15
    environment:
      - POSTGRES_DB=duitsedar
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## 9. Scalability Considerations

### 9.1 Current Design (MVP)

| Aspect | Design | Capacity |
|--------|--------|----------|
| Users | Single-tenant | 1 user (demo) |
| Transactions | In-memory processing | ~10,000 transactions |
| AI Calls | Synchronous | ~100 calls/minute |
| Database | Single instance | 20GB storage |

### 9.2 Future Scaling Path

| Aspect | Scaling Strategy |
|--------|------------------|
| Users | Multi-tenant with user isolation |
| Transactions | Batch processing, pagination |
| AI Calls | Queue-based async processing, caching |
| Database | Read replicas, connection pooling |
| Compute | Container orchestration (ECS/EKS) |

---

**Document End**

*Next Document: 03_CLAUDE_AGENT_PROMPTS.md*
