# DuitSedar — API Specification

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026  
**API Style:** RESTful  
**Base URL:** `/api/v1`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Transaction APIs](#3-transaction-apis)
4. [Debt APIs](#4-debt-apis)
5. [Analysis APIs](#5-analysis-apis)
6. [Prediction APIs](#6-prediction-apis)
7. [Advice APIs](#7-advice-apis)
8. [Query APIs](#8-query-apis)
9. [Error Handling](#9-error-handling)
10. [Rate Limiting](#10-rate-limiting)

---

## 1. Overview

### 1.1 Base Configuration

```yaml
Base URL: https://api.duitsedar.com/api/v1
Content-Type: application/json
Authentication: Bearer Token (Clerk JWT)
Rate Limit: 100 requests/minute
```

### 1.2 Common Headers

```http
Authorization: Bearer <clerk_jwt_token>
Content-Type: application/json
Accept: application/json
X-Request-ID: <uuid>  # Optional, for tracing
```

### 1.3 Response Format

All responses follow this structure:

```json
{
  "success": true,
  "data": { /* response payload */ },
  "meta": {
    "timestamp": "2026-01-15T10:30:00Z",
    "request_id": "uuid"
  }
}
```

Error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { /* additional context */ }
  },
  "meta": {
    "timestamp": "2026-01-15T10:30:00Z",
    "request_id": "uuid"
  }
}
```

---

## 2. Authentication

### 2.1 Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                           │
└─────────────────────────────────────────────────────────────────┘

1. User logs in via Clerk (frontend)
2. Frontend receives JWT token from Clerk
3. Frontend includes token in Authorization header
4. Backend validates token with Clerk
5. Backend extracts user_id and proceeds with request
```

### 2.2 Token Validation

All protected endpoints require a valid Clerk JWT:

```java
@RestController
@RequestMapping("/api/v1")
public class BaseController {
    
    @Autowired
    private ClerkService clerkService;
    
    protected String getCurrentUserId(HttpServletRequest request) {
        String token = extractToken(request);
        return clerkService.validateAndGetUserId(token);
    }
}
```

---

## 3. Transaction APIs

### 3.1 Upload Transactions

**Endpoint:** `POST /transactions/upload`

**Description:** Upload a bank statement or transaction file for processing.

**Request:**
```http
POST /api/v1/transactions/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <binary file>
source_type: rhb
```

**Supported Source Types:**
- `rhb`, `maybank`, `cimb`, `public_bank`, `hong_leong`
- `aeon_bank`, `touch_n_go`, `grabpay`, `shopeepay`, `boost`
- `manual_csv`

**Response:**
```json
{
  "success": true,
  "data": {
    "upload_id": "550e8400-e29b-41d4-a716-446655440000",
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
    },
    "debt_detected": {
      "bnpl_count": 3,
      "formal_count": 2
    }
  }
}
```

### 3.2 List Transactions

**Endpoint:** `GET /transactions`

**Description:** Get paginated list of transactions with optional filters.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| limit | integer | No | Items per page (default: 50, max: 100) |
| start_date | date | No | Filter from date (YYYY-MM-DD) |
| end_date | date | No | Filter to date (YYYY-MM-DD) |
| category | string | No | Filter by category |
| source_id | uuid | No | Filter by data source |
| min_amount | decimal | No | Minimum amount |
| max_amount | decimal | No | Maximum amount |
| search | string | No | Search in description |
| is_debt | boolean | No | Filter debt-related only |

**Request:**
```http
GET /api/v1/transactions?page=1&limit=20&category=FOOD&start_date=2025-12-01
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "date": "2025-12-15",
        "amount": 15.50,
        "description": "MAMAK HJ SYED TMN SRI",
        "category": "FOOD",
        "category_confidence": 0.95,
        "subcategory": "restaurant",
        "merchant_name": "Mamak Hj Syed",
        "source": {
          "id": "uuid",
          "type": "rhb",
          "name": "RHB Bank"
        },
        "is_debt_related": false,
        "user_comment": null
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_items": 245,
      "total_pages": 13
    }
  }
}
```

### 3.3 Get Transaction by ID

**Endpoint:** `GET /transactions/{id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "date": "2025-12-15",
    "amount": 15.50,
    "description": "MAMAK HJ SYED TMN SRI",
    "original_description": "MAMAK HJ SYED TMN SRI PETALING",
    "category": "FOOD",
    "category_confidence": 0.95,
    "subcategory": "restaurant",
    "merchant_name": "Mamak Hj Syed",
    "source": {
      "id": "uuid",
      "type": "rhb",
      "name": "RHB Bank"
    },
    "is_debt_related": false,
    "is_recurring": false,
    "user_comment": null,
    "quality_score": 0.98,
    "raw_data": {
      "original_row": "2025-12-15,MAMAK HJ SYED TMN SRI PETALING,15.50"
    },
    "created_at": "2026-01-10T08:30:00Z",
    "similar_transactions": [
      {
        "id": "uuid",
        "date": "2025-11-20",
        "amount": 18.00,
        "description": "MAMAK HJ SYED"
      }
    ]
  }
}
```

### 3.4 Update Transaction Category

**Endpoint:** `PUT /transactions/{id}/category`

**Description:** Correct the category of a transaction.

**Request:**
```json
{
  "category": "ENTERTAINMENT",
  "comment": "This was actually a movie, not food"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "previous_category": "FOOD",
    "new_category": "ENTERTAINMENT",
    "similar_updated": 0
  }
}
```

### 3.5 Get Spending Summary

**Endpoint:** `GET /transactions/summary`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| period | string | No | 'month', 'week', 'year' (default: 'month') |
| start_date | date | No | Custom period start |
| end_date | date | No | Custom period end |

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2025-12-01",
      "end": "2025-12-31",
      "type": "month"
    },
    "income": {
      "total": 4500.00,
      "transaction_count": 2,
      "sources": [
        {"name": "Salary", "amount": 3532.35},
        {"name": "Bonus", "amount": 967.65}
      ]
    },
    "expenses": {
      "total": 3847.23,
      "transaction_count": 178,
      "by_category": [
        {
          "category": "FOOD",
          "amount": 1245.50,
          "percentage": 32.4,
          "transaction_count": 47
        },
        {
          "category": "TRANSPORT",
          "amount": 687.00,
          "percentage": 17.9,
          "transaction_count": 58
        }
      ]
    },
    "net": 652.77,
    "comparison_to_previous": {
      "expenses_change": -8.5,
      "income_change": 0,
      "net_change": 15.2
    }
  }
}
```

---

## 4. Debt APIs

### 4.1 Get Debt Overview

**Endpoint:** `GET /debts`

**Response:**
```json
{
  "success": true,
  "data": {
    "total_debt": 15847.00,
    "monthly_obligations": 937.00,
    "debt_to_income_ratio": 20.8,
    "by_tier": {
      "formal": {
        "count": 2,
        "total_balance": 12500.00,
        "monthly_payment": 937.50,
        "debts": [
          {
            "id": "uuid",
            "name": "PTPTN",
            "provider": "PTPTN",
            "original_amount": 45000.00,
            "current_balance": 8500.00,
            "monthly_payment": 287.50,
            "interest_rate": 1.0,
            "remaining_months": 30
          },
          {
            "id": "uuid",
            "name": "Car Loan",
            "provider": "Maybank",
            "original_amount": 65000.00,
            "current_balance": 4000.00,
            "monthly_payment": 650.00,
            "interest_rate": 3.5,
            "remaining_months": 6
          }
        ]
      },
      "bnpl": {
        "count": 3,
        "total_balance": 847.00,
        "monthly_payment": 300.00,
        "alert_level": "warning",
        "percentage_of_income": 18.8,
        "debts": [
          {
            "id": "uuid",
            "name": "SPayLater - Laptop",
            "provider": "SPayLater",
            "original_amount": 2500.00,
            "current_balance": 500.00,
            "monthly_payment": 150.00,
            "remaining_installments": 4
          }
        ]
      },
      "hutang": {
        "count": 4,
        "total_owed": 2500.00,
        "total_owed_to_you": 350.00,
        "relationships": [
          {
            "id": "uuid",
            "person_name": "Ummi",
            "direction": "OWE",
            "total_amount": 1247.14,
            "item_count": 43,
            "oldest_item": "2025-10-01",
            "newest_item": "2025-12-10"
          }
        ]
      }
    }
  }
}
```

### 4.2 Add Debt

**Endpoint:** `POST /debts`

**Request (Formal/BNPL):**
```json
{
  "debt_tier": "FORMAL",
  "debt_name": "Personal Loan",
  "provider": "RHB Bank",
  "original_amount": 10000.00,
  "current_balance": 8500.00,
  "monthly_payment": 450.00,
  "interest_rate": 8.5,
  "start_date": "2024-06-01",
  "expected_end_date": "2026-06-01"
}
```

**Request (Hutang):**
```json
{
  "debt_tier": "HUTANG",
  "debt_name": "Loan to Ahmad",
  "person_name": "Ahmad",
  "relationship": "friend",
  "direction": "OWED",
  "notes": "For emergency car repair"
}
```

### 4.3 Add Hutang Item

**Endpoint:** `POST /debts/{debtId}/items`

**Request:**
```json
{
  "description": "Lunch at Mamak",
  "amount": 25.00,
  "item_date": "2025-12-20"
}
```

### 4.4 Mark Hutang Item Paid

**Endpoint:** `PUT /debts/{debtId}/items/{itemId}/pay`

**Request:**
```json
{
  "paid_date": "2025-12-25",
  "paid_amount": 25.00,
  "linked_transaction_id": "uuid"
}
```

---

## 5. Analysis APIs

### 5.1 Get Patterns

**Endpoint:** `GET /analysis/patterns`

**Response:**
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "id": "uuid",
        "type": "HIDDEN_COST",
        "name": "Toll Blindspot",
        "description": "Your daily toll spending accumulates to a significant monthly expense.",
        "data_points": [
          "Average 15 toll transactions/month",
          "Average RM8.50 per toll",
          "Mostly PLUS Karak and LDP"
        ],
        "frequency": "daily on workdays",
        "monthly_impact": 487.00,
        "annual_impact": 5844.00,
        "confidence": 0.95,
        "actionable_insight": "This is 11% of your income. Consider carpooling 2x/week.",
        "first_detected": "2025-11-01",
        "is_acknowledged": false
      },
      {
        "id": "uuid",
        "type": "BUNDLE",
        "name": "Weekend Splurge Pattern",
        "description": "Entertainment on Saturday triggers additional food and transport spending.",
        "data_points": [
          "{Entertainment, Food, Transport} co-occur 78% of Saturdays",
          "Average bundle cost: RM180"
        ],
        "frequency": "3-4 weekends per month",
        "monthly_impact": 630.00,
        "annual_impact": 7560.00,
        "confidence": 0.82,
        "actionable_insight": "Set a weekend budget of RM150 to control this pattern."
      }
    ],
    "last_analyzed": "2026-01-15T06:00:00Z"
  }
}
```

### 5.2 Get Trends

**Endpoint:** `GET /analysis/trends`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| months | integer | No | Number of months to analyze (default: 6) |
| category | string | No | Focus on specific category |

**Response:**
```json
{
  "success": true,
  "data": {
    "period": {
      "start": "2025-07-01",
      "end": "2025-12-31"
    },
    "overall_trend": "stable",
    "category_trends": [
      {
        "category": "FOOD",
        "trend": "increasing",
        "change_percentage": 12.5,
        "monthly_values": [
          {"month": "2025-07", "amount": 980.00},
          {"month": "2025-08", "amount": 1020.00},
          {"month": "2025-12", "amount": 1245.50}
        ],
        "insight": "Food spending has increased 12.5% over 6 months"
      }
    ]
  }
}
```

### 5.3 Get Anomalies

**Endpoint:** `GET /analysis/anomalies`

**Response:**
```json
{
  "success": true,
  "data": {
    "anomalies": [
      {
        "type": "SPENDING_SPIKE",
        "severity": "medium",
        "date": "2025-12-10",
        "category": "ENTERTAINMENT",
        "amount": 350.00,
        "baseline_average": 85.00,
        "deviation_percentage": 311.8,
        "transactions": [
          {
            "id": "uuid",
            "description": "TGV CINEMA",
            "amount": 180.00
          },
          {
            "id": "uuid",
            "description": "BOWLING ALLEY",
            "amount": 170.00
          }
        ],
        "possible_reason": "Weekend activity with friends"
      }
    ]
  }
}
```

---

## 6. Prediction APIs

### 6.1 Get Next Month Prediction

**Endpoint:** `GET /predictions/next-month`

**Response:**
```json
{
  "success": true,
  "data": {
    "prediction_month": "2026-02",
    "total_predicted": {
      "amount": 3850.00,
      "confidence_low": 3400.00,
      "confidence_high": 4200.00,
      "confidence_level": "medium"
    },
    "income_expected": 4500.00,
    "fixed_commitments": {
      "total": 1937.00,
      "items": [
        {"name": "PTPTN", "amount": 287.50, "confidence": "high"},
        {"name": "Car Loan", "amount": 650.00, "confidence": "high"},
        {"name": "SPayLater", "amount": 300.00, "confidence": "high"},
        {"name": "Internet", "amount": 149.00, "confidence": "high"},
        {"name": "Phone", "amount": 50.00, "confidence": "high"},
        {"name": "Family Support", "amount": 500.00, "confidence": "medium"}
      ]
    },
    "variable_predictions": [
      {
        "category": "FOOD",
        "predicted": 1200.00,
        "range": {"low": 1000, "high": 1400},
        "confidence": "medium",
        "basis": "3-month average with slight increase trend"
      }
    ],
    "contextual_adjustments": [
      {
        "factor": "CNY period",
        "adjustment": 400.00,
        "reason": "Historical CNY spending pattern"
      }
    ],
    "projected_balance": {
      "amount": 650.00,
      "range": {"low": 300, "high": 1100}
    },
    "risk_flags": [
      {
        "level": "warning",
        "message": "CNY ang pow obligations may create cash flow pressure"
      }
    ]
  }
}
```

### 6.2 Run Scenario

**Endpoint:** `POST /predictions/scenario`

**Request:**
```json
{
  "base_month": "2026-02",
  "adjustments": [
    {
      "type": "reduce_category",
      "category": "FOOD",
      "amount": -200
    },
    {
      "type": "add_expense",
      "description": "Wedding gift",
      "amount": 300
    },
    {
      "type": "reduce_recurring",
      "name": "Toll",
      "percentage": -40,
      "reason": "Work from home 2 days"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "scenario_name": "Custom Scenario",
    "base_prediction": {
      "total": 3850.00,
      "balance": 650.00
    },
    "adjusted_prediction": {
      "total": 3750.00,
      "balance": 750.00
    },
    "impact_summary": {
      "net_change": -100.00,
      "balance_improvement": 100.00
    },
    "adjustments_applied": [
      {"description": "Reduce FOOD by RM200", "impact": -200.00},
      {"description": "Add Wedding gift", "impact": 300.00},
      {"description": "Reduce Toll by 40%", "impact": -200.00}
    ]
  }
}
```

---

## 7. Advice APIs

### 7.1 Get Advice

**Endpoint:** `GET /advice`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| priority | string | No | Filter by priority (URGENT, IMPORTANT, GROWTH) |
| unread_only | boolean | No | Show only unread advice |
| limit | integer | No | Number of advice to return (default: 10) |

**Response:**
```json
{
  "success": true,
  "data": {
    "financial_health_score": 62,
    "score_breakdown": {
      "debt_to_income": {"value": 43, "score": 15, "max": 25, "status": "warning"},
      "savings_rate": {"value": 14, "score": 18, "max": 25, "status": "okay"},
      "emergency_fund": {"value": 2100, "score": 14, "max": 20, "status": "building"},
      "bill_timeliness": {"value": 100, "score": 15, "max": 15, "status": "excellent"},
      "spending_stability": {"value": 78, "score": 12, "max": 15, "status": "good"}
    },
    "advice": [
      {
        "id": "uuid",
        "priority": "URGENT",
        "type": "bnpl_alert",
        "title": "BNPL Exposure High",
        "content": {
          "observation": "Your BNPL commitments total RM847 across 3 platforms.",
          "insight": "That's 19% of your income - above the healthy 10% threshold.",
          "suggestion": "Pause new BNPL purchases until current ones are paid off.",
          "expected_result": "Your BNPL-to-income will drop to 0% in 3 months.",
          "actionable_steps": [
            "Delete saved payment methods from Shopee and Lazada",
            "Use cash or debit for the next 3 months",
            "Set a reminder to review in March"
          ]
        },
        "is_read": false,
        "created_at": "2026-01-15T06:00:00Z"
      }
    ],
    "positive_notes": [
      "You've never missed a bill payment - excellent discipline! 💪",
      "Your spending is fairly stable month-to-month."
    ]
  }
}
```

### 7.2 Mark Advice Read

**Endpoint:** `POST /advice/{id}/read`

### 7.3 Provide Advice Feedback

**Endpoint:** `POST /advice/{id}/feedback`

**Request:**
```json
{
  "is_helpful": true,
  "comment": "This was really useful, I didn't realize my BNPL was that high"
}
```

### 7.4 Snooze Advice

**Endpoint:** `POST /advice/{id}/snooze`

**Request:**
```json
{
  "snooze_days": 7
}
```

---

## 8. Query APIs

### 8.1 Natural Language Query

**Endpoint:** `POST /query`

**Request:**
```json
{
  "query": "How much did I spend on food last month?",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "answer": "Last month (December 2025), you spent RM1,245.50 on food across 47 transactions. That's about RM40 per day, with most spending at mamak restaurants and food delivery services.",
    "data_points": {
      "total": 1245.50,
      "period": "2025-12",
      "transaction_count": 47,
      "top_merchants": [
        {"name": "Food Delivery", "amount": 420.00},
        {"name": "Mamak", "amount": 380.00},
        {"name": "Groceries", "amount": 280.50}
      ]
    },
    "follow_up_suggestions": [
      "Compare to previous month",
      "Show food spending trend",
      "Which day do I spend most on food?"
    ]
  }
}
```

---

## 9. Error Handling

### 9.1 Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTH_REQUIRED | 401 | No authentication token provided |
| AUTH_INVALID | 401 | Invalid or expired token |
| FORBIDDEN | 403 | User doesn't have access to resource |
| NOT_FOUND | 404 | Resource not found |
| VALIDATION_ERROR | 400 | Invalid request parameters |
| FILE_PARSE_ERROR | 400 | Unable to parse uploaded file |
| RATE_LIMITED | 429 | Too many requests |
| SERVER_ERROR | 500 | Internal server error |
| AI_UNAVAILABLE | 503 | AI service temporarily unavailable |

### 9.2 Error Response Examples

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "fields": [
        {"field": "start_date", "error": "Must be a valid date in YYYY-MM-DD format"},
        {"field": "amount", "error": "Must be a positive number"}
      ]
    }
  }
}
```

---

## 10. Rate Limiting

### 10.1 Limits

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Standard APIs | 100 requests | 1 minute |
| Upload APIs | 10 requests | 1 minute |
| AI Query APIs | 20 requests | 1 minute |

### 10.2 Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

---

**Document End**

*Next Document: 06_DEVELOPMENT_ROADMAP.md*
