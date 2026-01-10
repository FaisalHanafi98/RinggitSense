# DuitSedar — Claude Code Implementation Prompts

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026  
**Purpose:** Optimal prompts for building DuitSedar with Claude Code

---

## Table of Contents

1. [Master System Prompt](#1-master-system-prompt)
2. [Project Initialization Prompt](#2-project-initialization-prompt)
3. [Week 1: Foundation Prompts](#3-week-1-foundation-prompts)
4. [Week 2: Data Ingestion Prompts](#4-week-2-data-ingestion-prompts)
5. [Week 3: Categorization Prompts](#5-week-3-categorization-prompts)
6. [Week 4: Debt System Prompts](#6-week-4-debt-system-prompts)
7. [Week 5: Pattern Analysis Prompts](#7-week-5-pattern-analysis-prompts)
8. [Week 6: Prediction Prompts](#8-week-6-prediction-prompts)
9. [Week 7: Advisor & Query Prompts](#9-week-7-advisor--query-prompts)
10. [Week 8: Polish & Deploy Prompts](#10-week-8-polish--deploy-prompts)
11. [Troubleshooting Prompts](#11-troubleshooting-prompts)
12. [Best Practices](#12-best-practices)

---

## 1. Master System Prompt

**Use this as the system prompt or project context for Claude Code:**

```
# DuitSedar Project Context

## Project Overview
DuitSedar ("Sedar duit, sedar diri" - Know your money, know yourself) is an AI-powered personal finance platform for young Malaysian professionals. It combines transaction aggregation, debt tracking, pattern analysis, spending prediction, and personalized advice.

## Technical Stack (LOCKED - Do not change)
- Backend: Spring Boot 3.2 (Java 17)
- Frontend: React 18 + TypeScript + Vite
- Database: PostgreSQL 15 with pgvector extension
- Auth: Clerk
- AI: Claude API (Anthropic) for agent capabilities
- Deployment: Docker + AWS EC2/RDS

## Core Modules
1. Transaction Parser - Multi-source ingestion (RHB, Maybank, T&G, Aeon Bank)
2. Categorizer Agent - AI-powered transaction classification
3. Debt Detector Agent - BNPL + formal loan + hutang detection
4. Pattern Analyzer Agent - Hidden costs, lifestyle bundles, trends
5. Predictor Agent - Next month spending forecast
6. Advisor Agent - Personalized financial guidance
7. Query Agent - Natural language questions

## Malaysian Context (CRITICAL)
- Currency: RM (Malaysian Ringgit)
- Banks: RHB, Maybank, CIMB, Public Bank, Aeon Bank
- E-wallets: Touch 'n Go (TnG/T&G), GrabPay, ShopeePay, Boost
- Toll plazas: PLUS, LDP, DUKE, SMART, AKLEH, KESAS
- BNPL: SPayLater (Shopee), GrabPayLater, Atome
- Cultural: Hutang (informal debt), zakat, family support obligations
- Date format: DD/MM/YYYY
- Salary typically paid 25th-30th of month

## User's Transaction Data
- 1,448 transactions across 10 months (March-December 2025)
- Sources: RHB (490), Touch & Go (441), Aeon Bank (208), Maybank (176)
- Categories: Transfer (324), Makan (315), Toll (251), Bill (236)
- Hutang relationships: Eqi, Haziq, Dyad, Ummi

## Code Standards
- Use clear, descriptive variable names
- Follow Spring Boot best practices
- Use TypeScript strict mode
- Handle errors gracefully with proper logging
- Write code comments for complex logic
- Create unit tests for business logic

## Key Files to Reference
When implementing, read the documentation in /mnt/project/:
- DUITSEDAR_PRD.md for requirements
- TECHNICAL_ARCHITECTURE.md for system design
- DATABASE_SCHEMA.md for data models
- API_SPECIFICATION.md for endpoints
- CLAUDE_AGENT_PROMPTS.md for AI agent design
```

---

## 2. Project Initialization Prompt

**Use this to start the project from scratch:**

```
Create the initial project structure for DuitSedar, a Malaysian personal finance platform.

## Requirements

### Backend (Spring Boot 3.2)
Create a Spring Boot project with:
- Java 17
- Gradle build system
- Dependencies: Spring Web, Spring Data JPA, PostgreSQL driver, Validation, Lombok
- Package structure:
  - com.duitsedar.controller
  - com.duitsedar.service
  - com.duitsedar.repository
  - com.duitsedar.model.entity
  - com.duitsedar.model.dto
  - com.duitsedar.agent
  - com.duitsedar.parser
  - com.duitsedar.config
  - com.duitsedar.exception

### Frontend (React + TypeScript + Vite)
Create a React project with:
- TypeScript strict mode
- Vite as build tool
- TailwindCSS for styling
- Folder structure:
  - src/components/
  - src/pages/
  - src/hooks/
  - src/services/
  - src/store/
  - src/types/

### Docker
Create docker-compose.yml with:
- PostgreSQL 15 with pgvector extension (image: pgvector/pgvector:pg15)
- Backend service
- Frontend dev service

### Configuration Files
- Backend: application.yml with profiles (dev, prod)
- Frontend: .env.example with required variables
- Root: .gitignore, README.md

Generate the complete project structure with all necessary files.
```

---

## 3. Week 1: Foundation Prompts

### 3.1 Database Schema Setup

```
Create the complete PostgreSQL database schema for DuitSedar.

## Tables Required

1. **users** - User accounts
   - id (UUID, PK)
   - clerk_id (VARCHAR, unique)
   - email (VARCHAR, unique)
   - name (VARCHAR)
   - monthly_income (DECIMAL)
   - settings (JSONB)
   - timestamps

2. **data_sources** - Bank/e-wallet connections
   - id (UUID, PK)
   - user_id (FK to users)
   - source_type (VARCHAR) - enum: rhb, maybank, touch_n_go, aeon_bank, etc.
   - source_name (VARCHAR)
   - last_synced (TIMESTAMP)
   - config (JSONB)

3. **transactions** - All financial transactions
   - id (UUID, PK)
   - user_id (FK)
   - source_id (FK)
   - transaction_date (DATE)
   - amount (DECIMAL)
   - description (TEXT)
   - category (VARCHAR) - enum: FOOD, TRANSPORT, BILLS, etc.
   - category_confidence (DECIMAL)
   - is_debt_related (BOOLEAN)
   - debt_tier (VARCHAR) - enum: FORMAL, BNPL, HUTANG
   - embedding (vector(384)) - for pgvector
   - timestamps

4. **debts** - Debt obligations
   - id (UUID, PK)
   - user_id (FK)
   - debt_tier (VARCHAR)
   - debt_name (VARCHAR)
   - provider (VARCHAR)
   - original_amount, current_balance, monthly_payment (DECIMAL)
   - person_name (VARCHAR) - for hutang
   - direction (VARCHAR) - OWE or OWED
   - status (VARCHAR)

5. **debt_items** - Individual hutang items
   - id (UUID, PK)
   - debt_id (FK)
   - description (TEXT)
   - amount (DECIMAL)
   - item_date (DATE)
   - is_paid (BOOLEAN)

6. **predictions** - Monthly spending predictions
7. **advice** - Generated financial advice
8. **patterns** - Detected spending patterns

Create:
1. SQL migration file (V1__initial_schema.sql)
2. All indexes for performance
3. Views for common queries (monthly_summary, debt_overview)
4. Enable pgvector extension

Reference: /mnt/project/04_DATABASE_SCHEMA.md for complete specifications.
```

### 3.2 Clerk Authentication Setup

```
Implement Clerk JWT authentication for the Spring Boot backend.

## Requirements

1. **SecurityConfig.java**
   - Configure Spring Security to validate Clerk JWT tokens
   - Protect all /api/v1/** endpoints
   - Allow /actuator/health without auth
   - Extract user_id from token claims

2. **ClerkService.java**
   - Validate JWT tokens against Clerk JWKS
   - Extract clerk_id from token
   - Map clerk_id to internal user_id

3. **BaseController.java**
   - Helper method getCurrentUserId(HttpServletRequest request)
   - Annotation for protecting endpoints

4. **application.yml configuration**
   ```yaml
   clerk:
     secret-key: ${CLERK_SECRET_KEY}
     jwks-url: https://api.clerk.com/.well-known/jwks.json
   ```

5. **Frontend Clerk Integration**
   - Configure ClerkProvider in main.tsx
   - Create useAuth hook for token access
   - Add Authorization header to all API calls

Include error handling for:
- Missing token (401)
- Invalid token (401)
- Expired token (401)
```

### 3.3 Base API Structure

```
Create the base API structure for DuitSedar with proper response formatting.

## Requirements

1. **ApiResponse.java** - Standard response wrapper
   ```java
   {
     "success": true/false,
     "data": { ... },
     "error": { "code": "...", "message": "..." },
     "meta": { "timestamp": "...", "request_id": "..." }
   }
   ```

2. **GlobalExceptionHandler.java**
   - Handle ValidationException → 400
   - Handle AuthenticationException → 401
   - Handle ResourceNotFoundException → 404
   - Handle RateLimitException → 429
   - Handle all other exceptions → 500
   - Log all errors with request context

3. **RequestLoggingFilter.java**
   - Log all incoming requests
   - Generate unique request_id
   - Log response time

4. **RateLimitingFilter.java**
   - 100 requests per minute per user
   - Return 429 with Retry-After header

5. **CorsConfig.java**
   - Allow localhost:5173 in development
   - Allow production domain in production

Create these files with full implementation.
```

---

## 4. Week 2: Data Ingestion Prompts

### 4.1 Statement Parser Implementation

```
Implement multi-source transaction parsers for Malaysian banks and e-wallets.

## Context
User has transaction files from:
- RHB Bank (CSV format)
- Maybank (CSV format)  
- Touch & Go e-wallet (Excel/CSV export)
- Aeon Bank (CSV format)

## Requirements

1. **StatementParser.java** - Interface
   ```java
   public interface StatementParser {
       List<RawTransaction> parse(byte[] fileContent);
       boolean canParse(String sourceType);
   }
   ```

2. **RHBParser.java**
   - Parse RHB CSV format
   - Handle Malaysian date format (DD/MM/YYYY)
   - Identify debits (expenses) vs credits (income)
   - Clean description text

3. **MaybankParser.java**
   - Parse Maybank CSV/Excel format
   - Handle different column layouts
   - Extract transaction reference

4. **TouchNGoParser.java**
   - Parse TnG e-wallet export
   - Identify toll transactions
   - Handle reload/topup transactions

5. **AeonParser.java**
   - Parse Aeon Bank format
   - Handle credit card vs savings account

6. **NormalizationService.java**
   - Standardize dates to ISO format
   - Normalize amounts to 2 decimal places
   - Clean and standardize descriptions
   - Detect and flag duplicates (same date, amount, similar description)
   - Calculate data quality score (0-1)

7. **RawTransaction.java** - DTO
   - date (LocalDate)
   - amount (BigDecimal)
   - description (String)
   - originalDescription (String)
   - source (String)
   - balance (BigDecimal, optional)

## Malaysian-Specific Handling
- Date format: DD/MM/YYYY (not MM/DD/YYYY)
- Amount format: May have RM prefix, thousand separators
- Description: May be in Malay, English, or mixed

Create robust parsers that handle edge cases and malformed data gracefully.
```

### 4.2 File Upload API

```
Implement the transaction file upload API endpoint.

## Endpoint
POST /api/v1/transactions/upload
Content-Type: multipart/form-data

## Request
- file: Binary file (CSV, Excel)
- source_type: rhb | maybank | touch_n_go | aeon_bank

## Response
```json
{
  "success": true,
  "data": {
    "upload_id": "uuid",
    "transactions_processed": 150,
    "transactions_new": 142,
    "transactions_duplicate": 8,
    "date_range": {
      "start": "2025-03-01",
      "end": "2025-03-31"
    },
    "quality_score": 0.95,
    "categorization_summary": {
      "auto_categorized": 135,
      "needs_review": 7
    }
  }
}
```

## Implementation

1. **TransactionController.java**
   - uploadTransactions(@RequestParam MultipartFile file, @RequestParam String sourceType)
   - Validate file size (<10MB)
   - Validate source_type enum

2. **TransactionService.java**
   - processUpload(MultipartFile file, String sourceType, String userId)
   - Select appropriate parser
   - Parse transactions
   - Normalize data
   - Detect duplicates against existing transactions
   - Save new transactions
   - Return upload summary

3. **Error Handling**
   - FILE_TOO_LARGE (413)
   - INVALID_SOURCE_TYPE (400)
   - PARSE_ERROR (400) with details
   - DUPLICATE_FILE (409) if identical file already uploaded

Create the complete upload flow with proper error handling.
```

### 4.3 Transaction List API

```
Implement the paginated transaction list API with filtering.

## Endpoint
GET /api/v1/transactions

## Query Parameters
- page (default: 1)
- limit (default: 50, max: 100)
- start_date (YYYY-MM-DD)
- end_date (YYYY-MM-DD)
- category (FOOD, TRANSPORT, etc.)
- source_id (UUID)
- min_amount (decimal)
- max_amount (decimal)
- search (string, searches description)
- is_debt (boolean)

## Response
```json
{
  "success": true,
  "data": {
    "transactions": [...],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total_items": 1448,
      "total_pages": 29
    }
  }
}
```

## Implementation

1. **TransactionRepository.java**
   - Use Spring Data JPA Specifications for dynamic filtering
   - Efficient pagination with total count

2. **TransactionSpecification.java**
   - Build dynamic WHERE clauses based on filters
   - Handle date ranges, category, amount ranges
   - Full-text search on description

3. **TransactionDTO.java**
   - Map entity to API response
   - Include source details
   - Format dates and amounts

Create efficient, paginated API with all filtering options.
```

---

## 5. Week 3: Categorization Prompts

### 5.1 Claude API Integration

```
Implement the Claude API integration service for DuitSedar agents.

## Requirements

1. **ClaudeService.java**
   - HTTP client for Anthropic API
   - Support for tool/function calling
   - Retry logic with exponential backoff
   - Rate limiting (10 requests/second)
   - Response parsing

2. **ClaudeConfig.java**
   ```java
   @Configuration
   public class ClaudeConfig {
       @Value("${claude.api.key}")
       private String apiKey;
       
       @Value("${claude.api.model}")
       private String model; // claude-sonnet-4-20250514
   }
   ```

3. **ClaudeRequest.java / ClaudeResponse.java**
   - Request/response DTOs for API
   - Support for messages, system prompt, tools

4. **Tool Definition Format**
   ```java
   Tool tool = Tool.builder()
       .name("categorize_transaction")
       .description("Categorize a transaction")
       .inputSchema(schema)
       .build();
   ```

5. **Error Handling**
   - API errors (400, 401, 429, 500)
   - Timeout handling (30 second limit)
   - Graceful degradation to fallback

Create a robust, production-ready Claude API client.
```

### 5.2 Categorizer Agent Implementation

```
Implement the CategorizerAgent for transaction classification.

## System Prompt
Use the complete system prompt from /mnt/project/03_CLAUDE_AGENT_PROMPTS.md - Section 2.

## Requirements

1. **CategorizerAgent.java**
   ```java
   @Service
   public class CategorizerAgent {
       public CategoryResult categorize(RawTransaction transaction);
       public List<CategoryResult> categorizeBatch(List<RawTransaction> transactions);
   }
   ```

2. **CategoryResult.java**
   - category (String)
   - confidence (double 0-1)
   - subcategory (String, optional)
   - merchantName (String, optional)
   - reasoning (String, for debugging)

3. **Batch Processing**
   - Process up to 20 transactions per API call
   - Build single prompt with all transactions
   - Parse array response
   - Cache results by description hash

4. **RuleBasedCategorizer.java** (Fallback)
   - Pattern matching for common Malaysian merchants
   - Toll detection: PLUS, LDP, DUKE, SMART
   - BNPL detection: SPAYLATER, GRABPAYLATER, ATOME
   - Bank transfer detection
   - 70% confidence for rule-based results

5. **Categories Enum**
   ```java
   public enum Category {
       FOOD, TRANSPORT, BILLS, ENTERTAINMENT, SHOPPING,
       TRANSFER, DEBT_PAYMENT, INCOME, HEALTHCARE, OTHER
   }
   ```

## Malaysian Context in Prompt
- Mamak restaurants
- Pasar malam
- Malaysian toll plazas
- Local bank names
- Mixed BM/EN descriptions

Create the complete categorization system with AI and fallback.
```

### 5.3 Category Correction API

```
Implement the category correction feature with learning capability.

## Endpoint
PUT /api/v1/transactions/{id}/category

## Request
```json
{
  "category": "ENTERTAINMENT",
  "comment": "This was actually a movie, not food"
}
```

## Implementation

1. **Update Transaction**
   - Update category
   - Set category_confidence to 1.0 (user verified)
   - Store user comment
   - Log the correction for future training

2. **Similar Transaction Detection**
   - Find transactions with similar description
   - Optionally update them too (with lower confidence)
   - Use sentence similarity via embeddings

3. **Correction Learning**
   - Store corrections in separate table
   - Use for future rule-based improvements
   - Track accuracy metrics

4. **Frontend Component**
   - CategoryCorrectionModal.tsx
   - Dropdown with all categories
   - Optional comment field
   - Show similar transactions to update

Create the correction flow that improves over time.
```

---

## 6. Week 4: Debt System Prompts

### 6.1 Debt Detector Agent

```
Implement the DebtDetectorAgent for identifying debt-related transactions.

## System Prompt
Use the complete system prompt from /mnt/project/03_CLAUDE_AGENT_PROMPTS.md - Section 3.

## Requirements

1. **DebtDetectorAgent.java**
   ```java
   @Service
   public class DebtDetectorAgent {
       public DebtResult detect(RawTransaction transaction);
       public List<DebtResult> detectBatch(List<RawTransaction> transactions);
   }
   ```

2. **DebtResult.java**
   - isDebtRelated (boolean)
   - debtTier (FORMAL, BNPL, HUTANG, null)
   - debtType (education_loan, bnpl_installment, etc.)
   - provider (PTPTN, SPayLater, etc.)
   - confidence (double)
   - indicators (List<String>)
   - personName (for HUTANG)
   - estimatedMonthly (BigDecimal)

3. **Detection Patterns**

   **FORMAL Debt:**
   - PTPTN repayment
   - Car loan / Hire Purchase
   - Housing loan
   - Personal loan
   - Credit card payment

   **BNPL Debt:**
   - SPAYLATER, SPL
   - GRABPAYLATER, GPL
   - ATOME
   - Installment patterns (3/6, 2 of 6)

   **HUTANG:**
   - Transfers with person names
   - Comments with "hutang", "pinjam", "bayar balik"

4. **Integration with Upload Flow**
   - Run debt detection after categorization
   - Link detected debts to debt records
   - Alert if BNPL exceeds threshold

Create comprehensive debt detection for Malaysian debt landscape.
```

### 6.2 Hutang Management System

```
Implement the complete hutang (informal debt) tracking system.

## Requirements

1. **HutangController.java**
   - GET /api/v1/hutang - List all hutang relationships
   - POST /api/v1/hutang - Create new hutang
   - GET /api/v1/hutang/{id} - Get hutang with items
   - PUT /api/v1/hutang/{id} - Update hutang
   - DELETE /api/v1/hutang/{id} - Delete hutang
   - POST /api/v1/hutang/{id}/items - Add item
   - PUT /api/v1/hutang/{id}/items/{itemId}/pay - Mark paid

2. **HutangService.java**
   - Create hutang with person name, direction (OWE/OWED)
   - Add individual items (description, amount, date)
   - Mark items as paid
   - Link payments to transactions
   - Calculate totals

3. **Data Model**
   ```java
   Debt (debt_tier = HUTANG)
   ├── person_name: "Ummi"
   ├── direction: "OWE"
   ├── current_balance: 1247.14
   └── items: [
       { description: "Lunch", amount: 25.00, is_paid: false },
       { description: "Petrol", amount: 50.00, is_paid: true }
   ]
   ```

4. **Frontend Components**
   - HutangManager.tsx - Main component
   - HutangCard.tsx - Individual relationship card
   - AddHutangModal.tsx - Create new hutang
   - HutangItemList.tsx - Show items with pay button
   - Two-way view: What I owe vs What's owed to me

5. **Import Existing Data**
   - Parse user's hutang Excel files (Eqi, Haziq, Dyad, Ummi)
   - Create script to import existing data

## UX Considerations
- Non-judgmental language (avoid "debt collector" tone)
- Sensitive relationship handling
- Easy payment tracking
- Clear totals and history

Create a culturally-sensitive hutang management system.
```

### 6.3 Debt Dashboard

```
Implement the unified debt dashboard showing all three tiers.

## Requirements

1. **DebtController.java**
   - GET /api/v1/debts - Overview of all debts
   - GET /api/v1/debts/summary - Totals by tier

2. **DebtOverviewDTO.java**
   ```java
   {
     totalDebt: 15847.00,
     monthlyObligations: 937.00,
     debtToIncomeRatio: 20.8,
     byTier: {
       formal: { count, balance, monthly, debts: [...] },
       bnpl: { count, balance, monthly, alertLevel, debts: [...] },
       hutang: { count, totalOwed, totalOwedToYou, relationships: [...] }
     }
   }
   ```

3. **BNPL Alert Logic**
   - Calculate BNPL as % of income
   - Alert levels: OK (<10%), Warning (10-20%), Critical (>20%)
   - Show specific recommendations

4. **Frontend: DebtDashboard.tsx**
   - Three-tier visualization
   - Total debt card
   - Debt-to-income gauge
   - Individual debt cards
   - Progress indicators for payoff

5. **Calculations**
   - Total debt across all tiers
   - Monthly payment obligations
   - Debt-to-income ratio
   - Time to debt-free (if maintaining current payments)

Create a comprehensive debt visibility dashboard.
```

---

## 7. Week 5: Pattern Analysis Prompts

### 7.1 Pattern Analyzer Agent

```
Implement the PatternAnalyzerAgent for discovering spending patterns.

## System Prompt
Use the complete system prompt from /mnt/project/03_CLAUDE_AGENT_PROMPTS.md - Section 4.

## Requirements

1. **PatternAnalyzerAgent.java**
   ```java
   @Service
   public class PatternAnalyzerAgent {
       public List<Pattern> analyzePatterns(List<Transaction> transactions, String userId);
       public List<Pattern> detectHiddenCosts(List<Transaction> transactions);
       public List<Pattern> detectBundles(List<Transaction> transactions);
       public List<Pattern> detectTrends(List<Transaction> transactions);
   }
   ```

2. **Pattern Types**

   **HIDDEN_COST** - Underestimated expenses
   - Aggregate toll transactions
   - Calculate true monthly/annual cost
   - Compare to user perception

   **BUNDLE** - Co-occurring spending
   - Market basket analysis concept
   - Example: {Entertainment, Food, Transport} = "Night Out"
   - Calculate bundle frequency and cost

   **TREND** - Category changes over time
   - Month-over-month comparison
   - Identify increasing/decreasing categories
   - Calculate change percentage

   **ANOMALY** - Unusual spending
   - Detect spending spikes
   - Compare to historical baseline
   - Flag unusual merchants

   **TEMPORAL** - Time-based patterns
   - Day-of-week patterns
   - Payday effects
   - Weekend vs weekday

3. **Pattern.java Entity**
   - type, name, description
   - dataPoints (List<String>)
   - frequency
   - monthlyImpact, annualImpact
   - confidence
   - actionableInsight

4. **Pattern Refresh**
   - Scheduled daily analysis
   - Store patterns in database
   - Track pattern changes over time

Create intelligent pattern detection with Malaysian context.
```

### 7.2 Hidden Cost Revelation

```
Implement specific hidden cost analysis for Malaysian users.

## Focus Areas

1. **Toll Analysis**
   - Aggregate all toll transactions (PLUS, LDP, DUKE, etc.)
   - Calculate daily, monthly, annual totals
   - Compare to typical commute benchmarks
   - Show as percentage of income

2. **Food Delivery Premium**
   - Identify food delivery transactions (GrabFood, FoodPanda, etc.)
   - Compare to dine-in equivalent
   - Calculate convenience premium

3. **Subscription Audit**
   - Detect recurring charges
   - Netflix, Spotify, subscriptions
   - Flag forgotten subscriptions

4. **Implementation**
   ```java
   public class HiddenCostAnalyzer {
       public TollAnalysis analyzeTolls(List<Transaction> transactions);
       public DeliveryAnalysis analyzeDelivery(List<Transaction> transactions);
       public SubscriptionAnalysis findSubscriptions(List<Transaction> transactions);
   }
   ```

5. **Frontend: HiddenCostCards.tsx**
   - Toll revelation card with shock value
   - "You spent RM487 on tolls - that's RM5,844/year!"
   - Comparison charts
   - Actionable suggestions

Create eye-opening hidden cost visibility.
```

---

## 8. Week 6: Prediction Prompts

### 8.1 Predictor Agent

```
Implement the PredictorAgent for spending forecasting.

## System Prompt
Use the complete system prompt from /mnt/project/03_CLAUDE_AGENT_PROMPTS.md - Section 5.

## Requirements

1. **PredictorAgent.java**
   ```java
   @Service
   public class PredictorAgent {
       public Prediction predictNextMonth(String userId);
       public Prediction predictWithScenario(String userId, List<Adjustment> adjustments);
   }
   ```

2. **Prediction Components**

   **Fixed Commitments (High Confidence)**
   - Detected loan repayments
   - Known bills (detected recurring)
   - BNPL installments
   - Family support (if regular)

   **Variable Spending (Medium Confidence)**
   - 3-month rolling average per category
   - Adjusted for number of days/weekends
   - Seasonal adjustments

   **Malaysian Calendar**
   - Ramadan: Food pattern shifts
   - Raya, CNY, Deepavali: +50-100%
   - School holidays: +20%
   - Year-end: +30%

3. **Prediction.java**
   ```java
   {
     predictionMonth: "2026-02",
     totalPredicted: { amount, low, high, confidence },
     incomeExpected: 4500.00,
     fixedCommitments: { total, items: [...] },
     variablePredictions: [{ category, predicted, range, confidence }],
     contextualAdjustments: [...],
     projectedBalance: { amount, range },
     riskFlags: [...]
   }
   ```

4. **Confidence Levels**
   - High: Fixed obligations (>90%)
   - Medium: Historical patterns (70-90%)
   - Low: Variable categories (<70%)

Create forecasting with Malaysian calendar awareness.
```

### 8.2 Scenario Modeling

```
Implement what-if scenario modeling for financial planning.

## Endpoint
POST /api/v1/predictions/scenario

## Request
```json
{
  "base_month": "2026-02",
  "adjustments": [
    { "type": "reduce_category", "category": "FOOD", "amount": -200 },
    { "type": "add_expense", "description": "Wedding gift", "amount": 300 },
    { "type": "reduce_recurring", "name": "Toll", "percentage": -40 }
  ]
}
```

## Implementation

1. **ScenarioService.java**
   - Take base prediction
   - Apply adjustments
   - Recalculate totals
   - Compare to baseline

2. **Adjustment Types**
   - reduce_category: Reduce specific category by amount
   - increase_category: Increase specific category
   - add_expense: One-time expense
   - remove_expense: Remove recurring expense
   - reduce_recurring: Reduce recurring by percentage

3. **Frontend: ScenarioBuilder.tsx**
   - List of adjustment inputs
   - Real-time recalculation
   - Side-by-side comparison
   - Save scenario for reference

Create interactive financial planning tool.
```

---

## 9. Week 7: Advisor & Query Prompts

### 9.1 Advisor Agent

```
Implement the AdvisorAgent for personalized financial guidance.

## System Prompt
Use the complete system prompt from /mnt/project/03_CLAUDE_AGENT_PROMPTS.md - Section 7.

## Requirements

1. **AdvisorAgent.java**
   ```java
   @Service
   public class AdvisorAgent {
       public FinancialHealthScore calculateHealthScore(String userId);
       public List<Advice> generateAdvice(String userId);
   }
   ```

2. **Financial Health Score (0-100)**
   ```java
   Components:
   - Debt-to-Income Ratio (25 points)
   - Savings Rate (25 points)
   - Emergency Fund Progress (20 points)
   - Bill Payment Timeliness (15 points)
   - Spending Stability (15 points)
   ```

3. **Advice Priority Levels**
   - URGENT: Immediate financial risk
   - IMPORTANT: Should address soon
   - GROWTH: Long-term improvements

4. **Advice Types**
   - debt_warning: High debt alert
   - bnpl_alert: BNPL exposure
   - spending_spike: Category spike
   - savings_tip: Increase savings
   - hidden_cost: Reveal hidden costs
   - positive_reinforcement: Celebrate wins
   - goal_progress: Track goals
   - seasonal_reminder: Festival planning

5. **Malaysian Cultural Awareness**
   - Family support is respected, not criticized
   - Zakat obligations acknowledged
   - Wedding savings legitimate
   - Festival spending understood

6. **Advice Structure**
   ```java
   {
     priority: "URGENT",
     type: "bnpl_alert",
     title: "BNPL Exposure High",
     content: {
       observation: "Your BNPL commitments total RM847...",
       insight: "That's 19% of your income...",
       suggestion: "Pause new BNPL purchases...",
       expectedResult: "Your BNPL-to-income will drop...",
       actionableSteps: [...]
     }
   }
   ```

Create compassionate, culturally-aware financial advisor.
```

### 9.2 Query Agent

```
Implement the QueryAgent for natural language questions.

## System Prompt
Use the complete system prompt from /mnt/project/03_CLAUDE_AGENT_PROMPTS.md - Section 6.

## Requirements

1. **QueryAgent.java**
   ```java
   @Service
   public class QueryAgent {
       public QueryResponse answer(String query, QueryContext context);
   }
   ```

2. **QueryContext.java**
   - List<Transaction> recentTransactions
   - DebtOverview debts
   - BigDecimal userIncome
   - List<Pattern> patterns

3. **Query Types Supported**
   - Totals: "How much did I spend on food last month?"
   - Comparisons: "Is my transport spending higher than last month?"
   - Lookups: "Find my biggest expense this week"
   - Averages: "What's my average daily spending?"
   - Trends: "Am I spending more on Grab lately?"
   - Debt: "How much do I owe in total?"
   - Predictions: "Will I have money left this month?"

4. **Language Support**
   - English
   - Malay (Bahasa Malaysia)
   - Manglish (mixed)

5. **QueryResponse.java**
   ```java
   {
     answer: "Last month, you spent RM1,245.50 on food...",
     dataPoints: { total, period, transactionCount, topMerchants },
     followUpSuggestions: [...]
   }
   ```

6. **Frontend: QueryInput.tsx**
   - Chat-like interface
   - Suggested questions
   - Response with data cards
   - Follow-up suggestions as buttons

Create conversational financial assistant.
```

---

## 10. Week 8: Polish & Deploy Prompts

### 10.1 UI Polish

```
Complete the UI polish for production readiness.

## Requirements

1. **Responsive Design**
   - Test all components on mobile (320px - 768px)
   - Test on tablet (768px - 1024px)
   - Fix any layout issues
   - Touch-friendly buttons (min 44px)

2. **Loading States**
   - Skeleton loaders for all data-dependent components
   - Button loading states
   - Page transition loading

3. **Error States**
   - Empty states for no data
   - Error messages with retry options
   - Offline handling

4. **Animations**
   - Page transitions
   - Card hover effects
   - Number count-up animations
   - Chart animations

5. **Accessibility**
   - Color contrast (WCAG AA)
   - Keyboard navigation
   - Screen reader labels
   - Focus indicators

6. **Final Design Touches**
   - Consistent spacing
   - Typography hierarchy
   - Icon consistency
   - Dark mode (optional)

Polish to portfolio quality.
```

### 10.2 AWS Deployment

```
Deploy DuitSedar to AWS production environment.

## Steps

1. **EC2 Setup**
   - Launch t3.micro instance (Free Tier)
   - Amazon Linux 2 AMI
   - Configure security group (80, 443, 22)
   - Allocate Elastic IP

2. **RDS Setup**
   - Launch db.t3.micro PostgreSQL 15
   - Enable pgvector extension
   - Configure security group for EC2 access
   - Run database migrations

3. **Docker Deployment**
   - Build production Docker image
   - Push to container registry
   - Pull and run on EC2
   - Configure environment variables

4. **Domain & SSL (Optional)**
   - Configure Route 53 or CloudFlare
   - Set up SSL certificate
   - Configure HTTPS redirect

5. **Health Checks**
   - Verify /actuator/health
   - Test all API endpoints
   - Test frontend loading
   - Test Claude API integration

6. **Monitoring**
   - Configure Sentry for errors
   - Set up CloudWatch alarms
   - Configure log retention

Deploy stable production environment.
```

---

## 11. Troubleshooting Prompts

### 11.1 Database Issues

```
Help me troubleshoot database connection issues in DuitSedar.

Current error: [paste error message]

## Checklist
1. Is PostgreSQL running?
2. Is pgvector extension enabled?
3. Are connection credentials correct?
4. Is the security group allowing connections?
5. Is the database created?

Provide step-by-step debugging.
```

### 11.2 Claude API Issues

```
Help me troubleshoot Claude API integration issues.

Current error: [paste error message]

## Checklist
1. Is API key valid?
2. Is rate limit exceeded?
3. Is request format correct?
4. Is response being parsed correctly?
5. Is fallback working?

Provide solution with code fix.
```

---

## 12. Best Practices

### 12.1 Prompting Tips for Claude Code

1. **Be Specific**: Include exact file names, package paths, and class names
2. **Provide Context**: Reference documentation files in /mnt/project/
3. **Incremental Building**: Build one feature at a time
4. **Test Early**: Ask for tests alongside implementation
5. **Error Handling**: Always request error handling
6. **Malaysian Context**: Remind about Malaysian specifics

### 12.2 Checkpoint Questions

After each major implementation, ask:
- "Show me the current project structure"
- "Run the tests for [module]"
- "What's left to complete for [week]?"
- "Are there any TODO comments to address?"

### 12.3 Recovery Prompts

If something breaks:
- "The [feature] stopped working after [change]. Help me debug."
- "Revert [file] to working state and try a different approach."
- "Show me the git diff for recent changes."

---

**Document End**

*Next Document: 10_PROPOSED_IMPROVEMENTS.md*
