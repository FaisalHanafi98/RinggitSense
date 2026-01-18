
# DuitSedar — Database Schema Documentation

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026  
**Database:** PostgreSQL 15 with pgvector extension

---

## Table of Contents

1. [Schema Overview](#1-schema-overview)
2. [Core Tables](#2-core-tables)
3. [Relationships](#3-relationships)
4. [Indexes](#4-indexes)
5. [Views](#5-views)
6. [Sample Queries](#6-sample-queries)
7. [Migration Scripts](#7-migration-scripts)

---

## 1. Schema Overview

### 1.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DUITSEDAR DATABASE SCHEMA                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────────────┐       ┌──────────────────┐
│    users     │       │    data_sources      │       │   transactions   │
├──────────────┤       ├──────────────────────┤       ├──────────────────┤
│ id (PK)      │──┐    │ id (PK)              │──┐    │ id (PK)          │
│ clerk_id     │  │    │ user_id (FK)         │  │    │ user_id (FK)     │
│ email        │  │    │ source_type          │  │    │ source_id (FK)   │
│ name         │  └───>│ source_name          │  └───>│ date             │
│ income       │       │ last_synced          │       │ amount           │
│ created_at   │       │ config               │       │ description      │
└──────────────┘       └──────────────────────┘       │ category         │
       │                                               │ confidence       │
       │                                               │ is_debt_related  │
       │                                               │ embedding        │
       │                                               └──────────────────┘
       │                                                        │
       │       ┌──────────────────────┐                        │
       │       │       debts          │                        │
       │       ├──────────────────────┤                        │
       │       │ id (PK)              │<───────────────────────┘
       └──────>│ user_id (FK)         │
               │ debt_tier            │       ┌──────────────────┐
               │ debt_name            │       │    debt_items    │
               │ provider             │       ├──────────────────┤
               │ original_amount      │──────>│ id (PK)          │
               │ current_balance      │       │ debt_id (FK)     │
               │ monthly_payment      │       │ description      │
               │ person_name          │       │ amount           │
               │ direction            │       │ date             │
               └──────────────────────┘       │ is_paid          │
                                              └──────────────────┘
       │
       │       ┌──────────────────────┐       ┌──────────────────┐
       │       │    predictions       │       │      advice      │
       │       ├──────────────────────┤       ├──────────────────┤
       └──────>│ id (PK)              │       │ id (PK)          │
               │ user_id (FK)         │<──────│ user_id (FK)     │
               │ prediction_month     │       │ advice_type      │
               │ category             │       │ priority         │
               │ predicted_amount     │       │ title            │
               │ actual_amount        │       │ content          │
               │ created_at           │       │ is_read          │
               └──────────────────────┘       │ is_helpful       │
                                              └──────────────────┘
```

### 1.2 Table Summary

| Table | Purpose | Estimated Rows |
|-------|---------|----------------|
| users | User accounts | 1 (single user MVP) |
| data_sources | Bank/e-wallet connections | 4-6 |
| transactions | All financial transactions | 1,500-5,000 |
| debts | Debt obligations (3 tiers) | 5-20 |
| debt_items | Individual debt items (for hutang) | 20-100 |
| predictions | Monthly spending predictions | 12-24 |
| advice | Generated financial advice | 20-50 |
| patterns | Detected spending patterns | 10-30 |
| audit_log | Data access audit trail | 1,000+ |

---

## 2. Core Tables

### 2.1 Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    monthly_income DECIMAL(12, 2),
    currency VARCHAR(3) DEFAULT 'MYR',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Settings JSONB structure:
-- {
--   "notifications": {
--     "email": true,
--     "push": false
--   },
--   "dashboard": {
--     "default_period": "month",
--     "show_predictions": true
--   },
--   "privacy": {
--     "share_anonymous_data": false
--   }
-- }

COMMENT ON TABLE users IS 'User accounts linked to Clerk authentication';
COMMENT ON COLUMN users.clerk_id IS 'Clerk authentication provider user ID';
COMMENT ON COLUMN users.monthly_income IS 'Self-reported monthly income for calculations';
```

### 2.2 Data Sources Table

```sql
CREATE TABLE data_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    source_name VARCHAR(255) NOT NULL,
    last_synced TIMESTAMP WITH TIME ZONE,
    total_transactions INTEGER DEFAULT 0,
    date_range_start DATE,
    date_range_end DATE,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_source_type CHECK (source_type IN (
        'rhb', 'maybank', 'cimb', 'public_bank', 'hong_leong', 
        'aeon_bank', 'touch_n_go', 'grabpay', 'shopeepay', 'boost', 'manual'
    ))
);

-- Config JSONB structure:
-- {
--   "parser_version": "1.0",
--   "file_format": "csv",
--   "column_mapping": {
--     "date": "Transaction Date",
--     "amount": "Amount (RM)",
--     "description": "Description"
--   },
--   "last_file_hash": "abc123..."
-- }

CREATE INDEX idx_data_sources_user ON data_sources(user_id);

COMMENT ON TABLE data_sources IS 'Connected banks and e-wallets for transaction import';
```

### 2.3 Transactions Table

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_id UUID REFERENCES data_sources(id) ON DELETE SET NULL,
    
    -- Core transaction data
    transaction_date DATE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    description TEXT NOT NULL,
    original_description TEXT, -- Before any cleaning
    
    -- Categorization
    category VARCHAR(50),
    category_confidence DECIMAL(3, 2),
    subcategory VARCHAR(100),
    merchant_name VARCHAR(255),
    
    -- Debt detection
    is_debt_related BOOLEAN DEFAULT FALSE,
    debt_tier VARCHAR(20),
    debt_id UUID REFERENCES debts(id) ON DELETE SET NULL,
    
    -- Metadata
    raw_data JSONB,
    user_comment TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_group_id UUID,
    
    -- Vector embedding for similarity search
    embedding vector(384),
    
    -- Quality flags
    quality_score DECIMAL(3, 2),
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of UUID REFERENCES transactions(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_category CHECK (category IN (
        'FOOD', 'TRANSPORT', 'BILLS', 'ENTERTAINMENT', 'SHOPPING',
        'TRANSFER', 'DEBT_PAYMENT', 'INCOME', 'HEALTHCARE', 'OTHER'
    )),
    CONSTRAINT valid_debt_tier CHECK (debt_tier IN ('FORMAL', 'BNPL', 'HUTANG') OR debt_tier IS NULL)
);

-- Indexes for common queries
CREATE INDEX idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
CREATE INDEX idx_transactions_category ON transactions(user_id, category);
CREATE INDEX idx_transactions_debt ON transactions(user_id, is_debt_related) WHERE is_debt_related = TRUE;
CREATE INDEX idx_transactions_amount ON transactions(user_id, amount);

-- Vector similarity index (for semantic search)
CREATE INDEX idx_transactions_embedding ON transactions 
    USING ivfflat (embedding vector_cosine_ops) 
    WITH (lists = 100);

COMMENT ON TABLE transactions IS 'All financial transactions from all sources';
COMMENT ON COLUMN transactions.embedding IS 'Sentence embedding for semantic similarity search';
COMMENT ON COLUMN transactions.quality_score IS 'Data quality score 0-1 based on completeness and validity';
```

### 2.4 Debts Table

```sql
CREATE TABLE debts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Classification
    debt_tier VARCHAR(20) NOT NULL,
    debt_name VARCHAR(255) NOT NULL,
    
    -- For FORMAL and BNPL
    provider VARCHAR(100),
    original_amount DECIMAL(12, 2),
    current_balance DECIMAL(12, 2),
    interest_rate DECIMAL(5, 2),
    monthly_payment DECIMAL(12, 2),
    start_date DATE,
    expected_end_date DATE,
    remaining_installments INTEGER,
    
    -- For HUTANG (informal)
    person_name VARCHAR(255),
    relationship VARCHAR(50),
    direction VARCHAR(10),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_debt_tier CHECK (debt_tier IN ('FORMAL', 'BNPL', 'HUTANG')),
    CONSTRAINT valid_direction CHECK (direction IN ('OWE', 'OWED') OR direction IS NULL),
    CONSTRAINT valid_status CHECK (status IN ('active', 'paid_off', 'defaulted', 'paused'))
);

CREATE INDEX idx_debts_user_tier ON debts(user_id, debt_tier);
CREATE INDEX idx_debts_status ON debts(user_id, status) WHERE status = 'active';

COMMENT ON TABLE debts IS 'All debt obligations across three tiers: FORMAL, BNPL, HUTANG';
COMMENT ON COLUMN debts.direction IS 'For HUTANG: OWE = user owes them, OWED = they owe user';
```

### 2.5 Debt Items Table

```sql
CREATE TABLE debt_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    debt_id UUID NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
    
    -- Item details
    description TEXT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    item_date DATE NOT NULL,
    
    -- Payment tracking
    is_paid BOOLEAN DEFAULT FALSE,
    paid_date DATE,
    paid_amount DECIMAL(12, 2),
    linked_transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_debt_items_debt ON debt_items(debt_id);
CREATE INDEX idx_debt_items_unpaid ON debt_items(debt_id, is_paid) WHERE is_paid = FALSE;

COMMENT ON TABLE debt_items IS 'Individual items within a debt (especially for HUTANG tracking)';
```

### 2.6 Predictions Table

```sql
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Prediction target
    prediction_month DATE NOT NULL, -- First of the month
    category VARCHAR(50), -- NULL for total prediction
    
    -- Prediction values
    predicted_amount DECIMAL(12, 2) NOT NULL,
    confidence_low DECIMAL(12, 2),
    confidence_high DECIMAL(12, 2),
    confidence_level VARCHAR(20),
    
    -- Actual (filled after month ends)
    actual_amount DECIMAL(12, 2),
    accuracy_score DECIMAL(5, 2),
    
    -- Metadata
    model_version VARCHAR(50),
    factors JSONB, -- What influenced the prediction
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_confidence_level CHECK (confidence_level IN ('high', 'medium', 'low'))
);

-- Factors JSONB structure:
-- {
--   "historical_weight": 0.6,
--   "seasonal_adjustment": 150.00,
--   "holiday_factor": "CNY",
--   "working_days": 22,
--   "fixed_commitments": 1937.00
-- }

CREATE UNIQUE INDEX idx_predictions_unique ON predictions(user_id, prediction_month, COALESCE(category, 'TOTAL'));
CREATE INDEX idx_predictions_month ON predictions(user_id, prediction_month DESC);

COMMENT ON TABLE predictions IS 'Monthly spending predictions and actual outcomes';
```

### 2.7 Advice Table

```sql
CREATE TABLE advice (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Advice content
    advice_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    
    -- Trigger data
    trigger_metric VARCHAR(100),
    trigger_value JSONB,
    
    -- User interaction
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    is_helpful BOOLEAN,
    feedback_at TIMESTAMP WITH TIME ZONE,
    is_snoozed BOOLEAN DEFAULT FALSE,
    snoozed_until TIMESTAMP WITH TIME ZONE,
    
    -- Lifecycle
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_priority CHECK (priority IN ('URGENT', 'IMPORTANT', 'GROWTH')),
    CONSTRAINT valid_advice_type CHECK (advice_type IN (
        'debt_warning', 'bnpl_alert', 'spending_spike', 'savings_tip',
        'hidden_cost', 'positive_reinforcement', 'goal_progress',
        'seasonal_reminder', 'general_tip'
    ))
);

CREATE INDEX idx_advice_user_unread ON advice(user_id, is_read, priority) WHERE is_read = FALSE;
CREATE INDEX idx_advice_user_recent ON advice(user_id, created_at DESC);

COMMENT ON TABLE advice IS 'Generated financial advice and user interactions';
```

### 2.8 Patterns Table

```sql
CREATE TABLE patterns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Pattern definition
    pattern_type VARCHAR(50) NOT NULL,
    pattern_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Analysis results
    data_points JSONB NOT NULL,
    frequency VARCHAR(50),
    monthly_impact DECIMAL(12, 2),
    annual_impact DECIMAL(12, 2),
    confidence DECIMAL(3, 2),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    first_detected DATE,
    last_seen DATE,
    
    -- User interaction
    is_acknowledged BOOLEAN DEFAULT FALSE,
    user_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_pattern_type CHECK (pattern_type IN (
        'BUNDLE', 'TREND', 'ANOMALY', 'HIDDEN_COST', 'TEMPORAL', 'RECURRING'
    ))
);

CREATE INDEX idx_patterns_user_active ON patterns(user_id, is_active) WHERE is_active = TRUE;

COMMENT ON TABLE patterns IS 'Detected spending patterns and lifestyle bundles';
```

### 2.9 Audit Log Table

```sql
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Action details
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    
    -- Change tracking
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_log(user_id, created_at DESC);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);

COMMENT ON TABLE audit_log IS 'Audit trail for data access and modifications';
```

---

## 3. Relationships

### 3.1 Foreign Key Relationships

```sql
-- Summary of all foreign key relationships

-- users -> data_sources (1:N)
-- A user can have multiple bank/e-wallet connections

-- users -> transactions (1:N)
-- A user has many transactions

-- data_sources -> transactions (1:N)
-- Each transaction comes from one source

-- users -> debts (1:N)
-- A user can have multiple debts

-- debts -> debt_items (1:N)
-- Each debt can have multiple items (especially hutang)

-- debts -> transactions (1:N)
-- A debt can be linked to payment transactions

-- transactions -> transactions (self-referential)
-- For duplicate detection
```

### 3.2 Cascade Rules

| Parent | Child | On Delete |
|--------|-------|-----------|
| users | data_sources | CASCADE |
| users | transactions | CASCADE |
| users | debts | CASCADE |
| users | predictions | CASCADE |
| users | advice | CASCADE |
| users | patterns | CASCADE |
| data_sources | transactions | SET NULL |
| debts | debt_items | CASCADE |
| debts | transactions.debt_id | SET NULL |
| transactions | debt_items.linked_transaction_id | SET NULL |

---

## 4. Indexes

### 4.1 Primary Indexes (Created with tables)

```sql
-- All primary keys are automatically indexed

-- Additional indexes created above:
-- idx_data_sources_user
-- idx_transactions_user_date
-- idx_transactions_category
-- idx_transactions_debt
-- idx_transactions_amount
-- idx_transactions_embedding (vector)
-- idx_debts_user_tier
-- idx_debts_status
-- idx_debt_items_debt
-- idx_debt_items_unpaid
-- idx_predictions_unique
-- idx_predictions_month
-- idx_advice_user_unread
-- idx_advice_user_recent
-- idx_patterns_user_active
-- idx_audit_user
-- idx_audit_entity
```

### 4.2 Composite Indexes for Common Queries

```sql
-- Monthly spending summary by category
CREATE INDEX idx_transactions_monthly_category 
ON transactions(user_id, date_trunc('month', transaction_date), category);

-- Date range queries with category
CREATE INDEX idx_transactions_date_range 
ON transactions(user_id, transaction_date, category) 
WHERE is_duplicate = FALSE;

-- Debt-related transactions
CREATE INDEX idx_transactions_debt_full 
ON transactions(user_id, debt_tier, transaction_date) 
WHERE is_debt_related = TRUE;

-- Active hutang with unpaid items
CREATE INDEX idx_debts_active_hutang 
ON debts(user_id, person_name) 
WHERE debt_tier = 'HUTANG' AND status = 'active';
```

### 4.3 Partial Indexes

```sql
-- Only index non-duplicate transactions
CREATE INDEX idx_transactions_valid 
ON transactions(user_id, transaction_date DESC) 
WHERE is_duplicate = FALSE AND quality_score > 0.5;

-- Only index unread advice
CREATE INDEX idx_advice_actionable 
ON advice(user_id, priority, created_at DESC) 
WHERE is_read = FALSE AND is_snoozed = FALSE AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP);
```

---

## 5. Views

### 5.1 Monthly Summary View

```sql
CREATE OR REPLACE VIEW v_monthly_summary AS
SELECT 
    user_id,
    date_trunc('month', transaction_date)::date AS month,
    category,
    COUNT(*) AS transaction_count,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_expenses,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS total_income,
    AVG(amount) AS avg_transaction,
    MIN(amount) AS min_transaction,
    MAX(amount) AS max_transaction
FROM transactions
WHERE is_duplicate = FALSE
GROUP BY user_id, date_trunc('month', transaction_date), category;
```

### 5.2 Debt Overview View

```sql
CREATE OR REPLACE VIEW v_debt_overview AS
SELECT 
    d.user_id,
    d.debt_tier,
    COUNT(*) AS debt_count,
    SUM(d.current_balance) AS total_balance,
    SUM(d.monthly_payment) AS total_monthly,
    AVG(d.interest_rate) AS avg_interest_rate
FROM debts d
WHERE d.status = 'active'
GROUP BY d.user_id, d.debt_tier;
```

### 5.3 Hutang Summary View

```sql
CREATE OR REPLACE VIEW v_hutang_summary AS
SELECT 
    d.user_id,
    d.id AS debt_id,
    d.person_name,
    d.direction,
    d.current_balance AS total_amount,
    COUNT(di.id) AS item_count,
    SUM(CASE WHEN di.is_paid = FALSE THEN di.amount ELSE 0 END) AS unpaid_amount,
    SUM(CASE WHEN di.is_paid = TRUE THEN di.amount ELSE 0 END) AS paid_amount,
    MIN(di.item_date) AS oldest_item,
    MAX(di.item_date) AS newest_item
FROM debts d
LEFT JOIN debt_items di ON d.id = di.debt_id
WHERE d.debt_tier = 'HUTANG' AND d.status = 'active'
GROUP BY d.user_id, d.id, d.person_name, d.direction, d.current_balance;
```

### 5.4 Financial Health View

```sql
CREATE OR REPLACE VIEW v_financial_health AS
WITH monthly_data AS (
    SELECT 
        user_id,
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_expenses,
        SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS total_income
    FROM transactions
    WHERE transaction_date >= date_trunc('month', CURRENT_DATE)
      AND is_duplicate = FALSE
    GROUP BY user_id
),
debt_data AS (
    SELECT 
        user_id,
        SUM(current_balance) AS total_debt,
        SUM(monthly_payment) AS monthly_debt_payment
    FROM debts
    WHERE status = 'active'
    GROUP BY user_id
)
SELECT 
    u.id AS user_id,
    u.monthly_income,
    COALESCE(m.total_expenses, 0) AS month_expenses,
    COALESCE(m.total_income, 0) AS month_income,
    COALESCE(d.total_debt, 0) AS total_debt,
    COALESCE(d.monthly_debt_payment, 0) AS monthly_debt_payment,
    CASE 
        WHEN u.monthly_income > 0 
        THEN ROUND((COALESCE(d.monthly_debt_payment, 0) / u.monthly_income * 100)::numeric, 2)
        ELSE 0 
    END AS debt_to_income_ratio,
    CASE 
        WHEN COALESCE(m.total_income, 0) > 0 
        THEN ROUND(((COALESCE(m.total_income, 0) - COALESCE(m.total_expenses, 0)) / m.total_income * 100)::numeric, 2)
        ELSE 0 
    END AS savings_rate
FROM users u
LEFT JOIN monthly_data m ON u.id = m.user_id
LEFT JOIN debt_data d ON u.id = d.user_id;
```

---

## 6. Sample Queries

### 6.1 Get Monthly Spending by Category

```sql
SELECT 
    category,
    COUNT(*) AS transactions,
    SUM(amount) AS total,
    ROUND(AVG(amount)::numeric, 2) AS average
FROM transactions
WHERE user_id = :userId
  AND transaction_date >= :startDate
  AND transaction_date < :endDate
  AND amount > 0
  AND is_duplicate = FALSE
GROUP BY category
ORDER BY total DESC;
```

### 6.2 Find Similar Transactions (Using Vector Similarity)

```sql
SELECT 
    t.id,
    t.description,
    t.amount,
    t.category,
    1 - (t.embedding <=> :queryEmbedding) AS similarity
FROM transactions t
WHERE t.user_id = :userId
  AND t.embedding IS NOT NULL
ORDER BY t.embedding <=> :queryEmbedding
LIMIT 10;
```

### 6.3 Calculate Total Debt by Tier

```sql
SELECT 
    debt_tier,
    COUNT(*) AS count,
    SUM(current_balance) AS total_balance,
    SUM(monthly_payment) AS total_monthly
FROM debts
WHERE user_id = :userId
  AND status = 'active'
GROUP BY debt_tier
ORDER BY 
    CASE debt_tier 
        WHEN 'FORMAL' THEN 1 
        WHEN 'BNPL' THEN 2 
        WHEN 'HUTANG' THEN 3 
    END;
```

### 6.4 Get Hutang Details with Items

```sql
SELECT 
    d.id,
    d.person_name,
    d.direction,
    d.current_balance,
    json_agg(
        json_build_object(
            'id', di.id,
            'description', di.description,
            'amount', di.amount,
            'date', di.item_date,
            'is_paid', di.is_paid
        ) ORDER BY di.item_date DESC
    ) AS items
FROM debts d
LEFT JOIN debt_items di ON d.id = di.debt_id
WHERE d.user_id = :userId
  AND d.debt_tier = 'HUTANG'
  AND d.status = 'active'
GROUP BY d.id, d.person_name, d.direction, d.current_balance;
```

### 6.5 Identify Potential BNPL Transactions

```sql
SELECT 
    t.id,
    t.description,
    t.amount,
    t.transaction_date,
    t.source_id
FROM transactions t
WHERE t.user_id = :userId
  AND t.is_debt_related = FALSE -- Not yet categorized as debt
  AND (
    t.description ILIKE '%SPAYLATER%'
    OR t.description ILIKE '%GRABPAYLATER%'
    OR t.description ILIKE '%ATOME%'
    OR t.description ILIKE '%PAY LATER%'
    OR t.description ~* '\d+/\d+\s*(of|installment)'
  )
ORDER BY t.transaction_date DESC;
```

### 6.6 Monthly Spending Trend

```sql
SELECT 
    date_trunc('month', transaction_date)::date AS month,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS expenses,
    SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END) AS income,
    SUM(amount) AS net
FROM transactions
WHERE user_id = :userId
  AND transaction_date >= :startDate
  AND is_duplicate = FALSE
GROUP BY date_trunc('month', transaction_date)
ORDER BY month;
```

---

## 7. Migration Scripts

### 7.1 Initial Migration (V1)

```sql
-- V1__initial_schema.sql

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create users table
CREATE TABLE users (
    -- ... (as defined above)
);

-- Create data_sources table
CREATE TABLE data_sources (
    -- ... (as defined above)
);

-- Create transactions table
CREATE TABLE transactions (
    -- ... (as defined above)
);

-- Create debts table
CREATE TABLE debts (
    -- ... (as defined above)
);

-- Create debt_items table
CREATE TABLE debt_items (
    -- ... (as defined above)
);

-- Create predictions table
CREATE TABLE predictions (
    -- ... (as defined above)
);

-- Create advice table
CREATE TABLE advice (
    -- ... (as defined above)
);

-- Create patterns table
CREATE TABLE patterns (
    -- ... (as defined above)
);

-- Create audit_log table
CREATE TABLE audit_log (
    -- ... (as defined above)
);

-- Create all indexes
-- ... (as defined above)

-- Create all views
-- ... (as defined above)
```

### 7.2 Seed Data for Testing

```sql
-- V2__seed_test_data.sql

-- Insert test user
INSERT INTO users (id, clerk_id, email, name, monthly_income)
VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'user_test123',
    'faisal.test@example.com',
    'Faisal Test',
    4500.00
);

-- Insert data sources
INSERT INTO data_sources (user_id, source_type, source_name)
VALUES 
    ('550e8400-e29b-41d4-a716-446655440000', 'rhb', 'RHB Bank'),
    ('550e8400-e29b-41d4-a716-446655440000', 'maybank', 'Maybank'),
    ('550e8400-e29b-41d4-a716-446655440000', 'touch_n_go', 'Touch n Go eWallet'),
    ('550e8400-e29b-41d4-a716-446655440000', 'aeon_bank', 'AEON Bank');
```

---

**Document End**

*Next Document: 05_API_SPECIFICATION.md*
