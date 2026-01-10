# Phase 1: Foundation

> Backend infrastructure, database, and basic API setup

**Target**: Week 1-2
**Status**: Not Started
**Tasks**: 12

---

## Objectives

1. Set up FastAPI project structure
2. Design and implement database schema
3. Implement JWT authentication
4. Create transaction CRUD API
5. Build Malaysian bank statement parsers
6. Establish testing foundation

---

## Task Breakdown

### F-001: Project Scaffolding

**Priority**: High | **Status**: ⬜ Not Started

Create FastAPI project with proper folder structure:

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   ├── dependencies.py
│   │   └── middleware/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── agents/
│   └── utils/
├── tests/
├── alembic/
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

**Acceptance Criteria**:
- [ ] FastAPI app runs on `localhost:8000`
- [ ] `/health` endpoint returns 200
- [ ] OpenAPI docs accessible at `/docs`
- [ ] Environment configuration working

---

### F-002: Database Schema Design

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: F-001

Design and implement PostgreSQL schema:

**Tables**:
- `users` - User accounts
- `transactions` - Financial transactions
- `categories` - Transaction categories
- `debts` - Detected debt obligations
- `patterns` - Discovered patterns
- `predictions` - Spending forecasts

**Acceptance Criteria**:
- [ ] Alembic migration created
- [ ] All tables created with proper indexes
- [ ] Foreign key relationships established
- [ ] Timestamps (created_at, updated_at) on all tables

---

### F-003: User Authentication

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: F-002

Implement JWT-based authentication:

**Endpoints**:
- `POST /auth/register` - Create account
- `POST /auth/login` - Get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Invalidate refresh token

**Acceptance Criteria**:
- [ ] Password hashing with bcrypt
- [ ] Access token (15 min expiry)
- [ ] Refresh token (7 day expiry)
- [ ] Protected route middleware
- [ ] User can only access own data

---

### F-004: Transaction CRUD API

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: F-003

Basic transaction management:

**Endpoints**:
- `GET /transactions` - List with pagination/filters
- `GET /transactions/{id}` - Get single transaction
- `POST /transactions` - Create transaction
- `PATCH /transactions/{id}` - Update transaction
- `DELETE /transactions/{id}` - Delete transaction

**Filters**:
- Date range
- Category
- Amount range
- Source (bank/e-wallet)

**Acceptance Criteria**:
- [ ] All CRUD operations working
- [ ] Pagination implemented (default 50 per page)
- [ ] Filters working correctly
- [ ] User scoping (user sees only their data)

---

### F-005: Statement Parser - Maybank

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: F-004

Parse Maybank PDF/CSV statements:

**Supported Formats**:
- PDF bank statement
- CSV export from Maybank2u

**Fields to Extract**:
- Date
- Description
- Debit/Credit
- Balance
- Reference number

**Acceptance Criteria**:
- [ ] PDF parsing working
- [ ] CSV parsing working
- [ ] All fields correctly extracted
- [ ] Handles edge cases (multi-page, special characters)
- [ ] Unit tests with sample data

---

### F-006: Statement Parser - CIMB

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: F-005

Parse CIMB PDF/CSV statements.

**Acceptance Criteria**:
- [ ] PDF parsing working
- [ ] CSV parsing working
- [ ] All fields correctly extracted

---

### F-007: Statement Parser - RHB

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: F-005

Parse RHB PDF/CSV statements.

**Acceptance Criteria**:
- [ ] PDF parsing working
- [ ] CSV parsing working
- [ ] All fields correctly extracted

---

### F-008: Statement Parser - Touch 'n Go

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: F-005

Parse Touch 'n Go e-wallet export:

**Supported Formats**:
- CSV export from TnG app
- PDF statement

**Acceptance Criteria**:
- [ ] CSV parsing working
- [ ] PDF parsing working (if available)
- [ ] All fields correctly extracted

---

### F-009: File Upload Endpoint

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: F-004

Handle statement file uploads:

**Endpoint**: `POST /upload/statement`

**Features**:
- Accept PDF, CSV files
- Auto-detect bank from file content
- Parse and store transactions
- Return processing summary

**Acceptance Criteria**:
- [ ] File upload working (multipart/form-data)
- [ ] File type validation
- [ ] Size limit (10MB)
- [ ] Bank auto-detection working
- [ ] Transactions stored in DB
- [ ] Processing summary returned

---

### F-010: Error Handling Middleware

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: F-001

Standardized error responses:

**Error Format**:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

**Error Types**:
- Validation errors (422)
- Authentication errors (401)
- Authorization errors (403)
- Not found (404)
- Server errors (500)

**Acceptance Criteria**:
- [ ] All errors return consistent format
- [ ] Validation errors include field details
- [ ] No stack traces in production
- [ ] Errors logged for debugging

---

### F-011: Logging and Monitoring

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: F-001

Set up logging infrastructure:

**Features**:
- Structured JSON logging
- Request/response logging (sanitized)
- Error logging with stack traces
- Performance metrics

**Acceptance Criteria**:
- [ ] All requests logged
- [ ] Sensitive data (passwords, tokens) redacted
- [ ] Log levels configurable
- [ ] Logs written to stdout (for container compatibility)

---

### F-012: Foundation Unit Tests

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: F-004

Comprehensive tests for foundation layer:

**Coverage Targets**:
- Auth: 90%+
- CRUD: 80%+
- Parsers: 80%+

**Test Types**:
- Unit tests (pytest)
- API tests (pytest-asyncio)
- Parser tests with sample files

**Acceptance Criteria**:
- [ ] All auth endpoints tested
- [ ] All CRUD operations tested
- [ ] Parser tests with sample data
- [ ] Coverage report generated
- [ ] Tests pass in CI

---

## Exit Criteria

Phase 1 is complete when:

1. ✅ API can receive statement upload
2. ✅ Parser extracts transactions from at least Maybank
3. ✅ Transactions stored in PostgreSQL
4. ✅ User authentication working
5. ✅ 80% test coverage on foundation code
6. ✅ All F-xxx tasks marked Done

---

## Dependencies

| External | Internal |
|----------|----------|
| PostgreSQL | None |
| Redis (optional for Phase 1) | None |
| Sample bank statements | None |

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
