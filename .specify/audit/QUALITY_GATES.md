# Quality Gates

> Exit criteria for each development phase

**Version**: 1.0.0
**Last Updated**: 2026-01-10

---

## Overview

Quality gates define the minimum requirements that must be met before moving to the next phase. No phase is complete until ALL gates pass.

---

## Phase 1: Foundation

| Gate | Requirement | Verification |
|------|-------------|--------------|
| **G1.1** API Health | `/health` returns 200 | Automated test |
| **G1.2** Authentication | JWT login/register working | Manual + automated |
| **G1.3** Transaction CRUD | All CRUD operations functional | Automated tests |
| **G1.4** Parser Functional | At least 1 bank parser works | Unit tests |
| **G1.5** Upload Working | File upload processes correctly | Integration test |
| **G1.6** Test Coverage | >=80% on foundation code | Coverage report |
| **G1.7** No Critical Bugs | Zero P0/P1 bugs open | Bug tracker |
| **G1.8** Documentation | API docs generated | OpenAPI spec |

### Phase 1 Sign-off Checklist

```
[ ] G1.1 - API Health check passes
[ ] G1.2 - Can register, login, access protected routes
[ ] G1.3 - Create, read, update, delete transactions
[ ] G1.4 - Maybank statement parsed correctly
[ ] G1.5 - Upload endpoint accepts and processes file
[ ] G1.6 - pytest --cov shows >=80%
[ ] G1.7 - No critical bugs in tracker
[ ] G1.8 - /docs endpoint shows OpenAPI
```

---

## Phase 2: AI Agents

| Gate | Requirement | Verification |
|------|-------------|--------------|
| **G2.1** All Agents Implemented | 6 agents functional | Smoke tests |
| **G2.2** Categorizer Accuracy | >95% on golden dataset | Golden dataset test |
| **G2.3** Debt Detection Recall | >90% catches all debts | Golden dataset test |
| **G2.4** Pipeline Executes | Full pipeline completes | Integration test |
| **G2.5** Query Routing | Routes to correct agent | Unit tests |
| **G2.6** Advisor Disclaimers | 100% responses have disclaimers | Automated check |
| **G2.7** Latency Targets | Pipeline <30s for 100 txns | Performance test |
| **G2.8** Agent Tests Pass | All agent tests green | CI pipeline |

### Phase 2 Sign-off Checklist

```
[ ] G2.1 - All 6 agents respond to test inputs
[ ] G2.2 - Categorizer achieves 95%+ on 500-transaction dataset
[ ] G2.3 - Debt detector catches 90%+ of labeled debts
[ ] G2.4 - Upload triggers full AG-01→02→03→04→06 pipeline
[ ] G2.5 - Questions route to expected agents
[ ] G2.6 - Every advisor response contains all 3 disclaimers
[ ] G2.7 - 100 transactions processed in under 30 seconds
[ ] G2.8 - pytest tests/agents all pass
```

---

## Phase 3: Frontend

| Gate | Requirement | Verification |
|------|-------------|--------------|
| **G3.1** Auth Flow | Login/register works | E2E test |
| **G3.2** Dashboard Loads | Dashboard shows data | E2E test |
| **G3.3** Upload Works | File upload triggers pipeline | E2E test |
| **G3.4** Chat Functional | Query returns answers | E2E test |
| **G3.5** Debt View | Tri-tier display works | Manual test |
| **G3.6** Mobile Responsive | All pages work on mobile | Manual test |
| **G3.7** Accessibility | No critical a11y issues | Lighthouse/axe |
| **G3.8** Performance | LCP <2.5s, FID <100ms | Lighthouse |

### Phase 3 Sign-off Checklist

```
[ ] G3.1 - Can register, login, see dashboard
[ ] G3.2 - Dashboard shows spending summary, charts
[ ] G3.3 - Upload PDF, see processed transactions
[ ] G3.4 - Ask question, receive answer with data
[ ] G3.5 - Debt tracker shows FORMAL/BNPL/HUTANG tiers
[ ] G3.6 - Test on 375px width (iPhone SE)
[ ] G3.7 - axe-core reports no critical violations
[ ] G3.8 - Lighthouse performance score >=80
```

---

## Phase 4: Deployment

| Gate | Requirement | Verification |
|------|-------------|--------------|
| **G4.1** Docker Builds | Images build successfully | CI pipeline |
| **G4.2** Local Dev Works | docker-compose up works | Manual test |
| **G4.3** AWS Deployed | App accessible on AWS | Smoke test |
| **G4.4** HTTPS Working | SSL certificate valid | Browser test |
| **G4.5** CI/CD Functional | Push to main deploys | End-to-end |
| **G4.6** Monitoring Active | Alarms configured | AWS console |
| **G4.7** Security Scan | No critical vulnerabilities | Security scan |
| **G4.8** Performance Test | Handles 10 concurrent users | Load test |

### Phase 4 Sign-off Checklist

```
[ ] G4.1 - docker build succeeds for backend and frontend
[ ] G4.2 - docker-compose up starts all services
[ ] G4.3 - ringgitsense.com (or IP) loads the app
[ ] G4.4 - https:// works, certificate valid
[ ] G4.5 - Push to main triggers deploy, app updates
[ ] G4.6 - CloudWatch alarms for errors, latency
[ ] G4.7 - No critical/high vulnerabilities in scan
[ ] G4.8 - App responsive with 10 simultaneous users
```

---

## Pre-Launch Checklist

Final checklist before public launch:

### Security

```
[ ] All API keys rotated from development
[ ] Database encrypted at rest
[ ] All traffic over HTTPS
[ ] Rate limiting enabled
[ ] CORS configured correctly
[ ] No secrets in codebase
[ ] Security headers set (CSP, HSTS, etc.)
```

### Compliance

```
[ ] PDPA consent flow implemented
[ ] Data deletion capability exists
[ ] Disclaimers on all advice
[ ] No unlicensed financial advice
```

### Operations

```
[ ] Monitoring dashboards set up
[ ] Alerting configured and tested
[ ] Backup strategy documented
[ ] Runbook for common issues
[ ] Support email configured
```

### Documentation

```
[ ] User documentation complete
[ ] API documentation published
[ ] Architecture diagrams updated
[ ] README files current
```

---

## Gate Failure Protocol

If a quality gate fails:

1. **Document** the failure in the task tracker
2. **Assess** severity (blocker vs. can-proceed)
3. **Fix** the issue before proceeding
4. **Re-verify** the gate passes
5. **Update** this document if gate criteria need adjustment

**Never proceed with a failing mandatory gate.**

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
