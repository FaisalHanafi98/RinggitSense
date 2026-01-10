# RinggitSense Task Registry

> Master task list and progress tracker

**Project**: RinggitSense
**Version**: 1.0.0
**Last Updated**: 2026-01-10

---

## Overview

This document tracks all implementation tasks across four development phases.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPMENT TIMELINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Week 1-2          Week 3-4          Week 5-6          Week 7-8            │
│  ┌────────┐        ┌────────┐        ┌────────┐        ┌────────┐          │
│  │ PHASE 1│───────>│ PHASE 2│───────>│ PHASE 3│───────>│ PHASE 4│          │
│  │        │        │        │        │        │        │        │          │
│  │ Found- │        │ AI     │        │ Front- │        │ Deploy │          │
│  │ ation  │        │ Agents │        │  end   │        │ ment   │          │
│  └────────┘        └────────┘        └────────┘        └────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase Summary

| Phase | Name | Tasks | Status | Target |
|-------|------|-------|--------|--------|
| 1 | [Foundation](phases/PHASE_1_FOUNDATION.md) | 12 | Not Started | Week 1-2 |
| 2 | [AI Agents](phases/PHASE_2_AGENTS.md) | 15 | Not Started | Week 3-4 |
| 3 | [Frontend](phases/PHASE_3_FRONTEND.md) | 10 | Not Started | Week 5-6 |
| 4 | [Deployment](phases/PHASE_4_DEPLOYMENT.md) | 8 | Not Started | Week 7-8 |

**Total Tasks**: 45

---

## Task Status Legend

| Status | Icon | Definition |
|--------|------|------------|
| Not Started | ⬜ | Work not begun |
| In Progress | 🔄 | Currently being worked on |
| Blocked | 🚫 | Waiting on dependency |
| Review | 👀 | Completed, awaiting review |
| Done | ✅ | Completed and verified |

---

## Phase 1: Foundation (Week 1-2)

**Objective**: Set up backend infrastructure, database, and basic API.

| ID | Task | Status | Priority | Depends On |
|----|------|--------|----------|------------|
| F-001 | Project scaffolding (FastAPI, folder structure) | ⬜ | High | - |
| F-002 | Database schema design and migration | ⬜ | High | F-001 |
| F-003 | User authentication (JWT) | ⬜ | High | F-002 |
| F-004 | Basic transaction CRUD API | ⬜ | High | F-003 |
| F-005 | Statement parser - Maybank | ⬜ | High | F-004 |
| F-006 | Statement parser - CIMB | ⬜ | Medium | F-005 |
| F-007 | Statement parser - RHB | ⬜ | Medium | F-005 |
| F-008 | Statement parser - Touch 'n Go | ⬜ | Medium | F-005 |
| F-009 | File upload endpoint | ⬜ | High | F-004 |
| F-010 | Error handling middleware | ⬜ | Medium | F-001 |
| F-011 | Logging and monitoring setup | ⬜ | Medium | F-001 |
| F-012 | Unit tests for foundation layer | ⬜ | High | F-004 |

**Exit Criteria**: API can receive statement, parse transactions, store in DB.

---

## Phase 2: AI Agents (Week 3-4)

**Objective**: Implement all six Claude agents with orchestration.

| ID | Task | Status | Priority | Depends On |
|----|------|--------|----------|------------|
| A-001 | Base agent class and interface | ⬜ | High | F-012 |
| A-002 | Agent orchestrator implementation | ⬜ | High | A-001 |
| A-003 | AG-01 Categorizer agent | ⬜ | High | A-002 |
| A-004 | AG-02 Debt Detector agent | ⬜ | High | A-002 |
| A-005 | AG-03 Pattern Analyzer agent | ⬜ | High | A-002 |
| A-006 | AG-04 Predictor agent | ⬜ | High | A-002 |
| A-007 | AG-05 Query agent | ⬜ | High | A-002 |
| A-008 | AG-06 Advisor agent | ⬜ | High | A-002 |
| A-009 | Sequential pipeline (upload flow) | ⬜ | High | A-003, A-004, A-005, A-006, A-008 |
| A-010 | Query routing logic | ⬜ | High | A-007 |
| A-011 | Agent response caching | ⬜ | Medium | A-002 |
| A-012 | Rate limiting for Claude API | ⬜ | Medium | A-002 |
| A-013 | Golden dataset for Categorizer | ⬜ | High | A-003 |
| A-014 | Agent unit tests | ⬜ | High | A-003 through A-008 |
| A-015 | Integration tests for pipeline | ⬜ | High | A-009 |

**Exit Criteria**: All agents functional, pipeline processes statements end-to-end.

---

## Phase 3: Frontend (Week 5-6)

**Objective**: Build React dashboard with all major views.

| ID | Task | Status | Priority | Depends On |
|----|------|--------|----------|------------|
| U-001 | React project setup (Vite, TypeScript) | ⬜ | High | - |
| U-002 | Authentication pages (login, register) | ⬜ | High | U-001 |
| U-003 | Dashboard overview page | ⬜ | High | U-002 |
| U-004 | Transaction list with filters | ⬜ | High | U-003 |
| U-005 | Statement upload interface | ⬜ | High | U-003 |
| U-006 | Debt tracker view (tri-tier) | ⬜ | High | U-003 |
| U-007 | Pattern visualization | ⬜ | Medium | U-003 |
| U-008 | Chat/query interface | ⬜ | High | U-003 |
| U-009 | Advice display with disclaimers | ⬜ | High | U-003 |
| U-010 | Mobile responsive design | ⬜ | Medium | U-003 through U-009 |

**Exit Criteria**: Functional UI connecting to all backend features.

---

## Phase 4: Deployment (Week 7-8)

**Objective**: Deploy to AWS with CI/CD pipeline.

| ID | Task | Status | Priority | Depends On |
|----|------|--------|----------|------------|
| D-001 | Docker containerization | ⬜ | High | U-010 |
| D-002 | Docker Compose for local dev | ⬜ | High | D-001 |
| D-003 | AWS infrastructure (Terraform/CDK) | ⬜ | High | D-001 |
| D-004 | RDS PostgreSQL setup | ⬜ | High | D-003 |
| D-005 | ECS Fargate deployment | ⬜ | High | D-003 |
| D-006 | GitHub Actions CI/CD | ⬜ | High | D-005 |
| D-007 | SSL/TLS and domain setup | ⬜ | High | D-005 |
| D-008 | Monitoring and alerting | ⬜ | Medium | D-005 |

**Exit Criteria**: Application live on AWS, accessible via custom domain.

---

## Critical Path

The following tasks are on the critical path (blocking all downstream work):

```
F-001 → F-002 → F-003 → F-004 → F-005 → A-001 → A-002 → A-003 → A-009 → U-003 → D-001 → D-005
```

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Claude API rate limits | High | Medium | Implement caching, batch requests |
| Bank statement format changes | Medium | Low | Abstract parser interface, easy to update |
| PDPA compliance issues | High | Low | Early legal review, encryption |
| Agent hallucination | High | Medium | Anti-hallucination prompts, testing |
| Scope creep | Medium | High | Strict MVP definition, feature freeze |

---

## Progress Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tasks Completed | 0 | 45 |
| Code Coverage | 0% | 80% |
| Agent Accuracy | N/A | >90% |
| API Endpoints | 0 | 15 |
| UI Pages | 0 | 8 |

---

## Quick Links

- [Phase 1: Foundation](phases/PHASE_1_FOUNDATION.md)
- [Phase 2: AI Agents](phases/PHASE_2_AGENTS.md)
- [Phase 3: Frontend](phases/PHASE_3_FRONTEND.md)
- [Phase 4: Deployment](phases/PHASE_4_DEPLOYMENT.md)

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
