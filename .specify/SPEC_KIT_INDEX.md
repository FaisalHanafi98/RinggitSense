# RinggitSense Spec-Kit Index

> Master navigation and status overview for all specification documents

**Project**: RinggitSense
**Version**: 1.0.0
**Last Updated**: 2026-01-10
**Status**: Active Development

---

## Quick Links

| Document | Purpose | Status |
|----------|---------|--------|
| [Constitution](memory/constitution.md) | Core principles and constraints | Done |
| [Problem Statement](specs/PROBLEM_STATEMENT.md) | Malaysian financial context | Done |
| [PRD Synthesis](specs/PRD_SYNTHESIS.md) | Synthesized requirements | Done |
| [Feature Spec: Agents](specs/FEATURE_SPEC_AGENTS.md) | 6 Claude agents specification | Done |
| [Architecture](plans/ARCHITECTURE.md) | System design and diagrams | Done |
| [Task Registry](tasks/TASK_REGISTRY.md) | Master task list | Done |

---

## Folder Structure

```
.specify/
├── SPEC_KIT_INDEX.md              [This file]
├── memory/
│   └── constitution.md            Core principles and constraints
├── specs/
│   ├── PROBLEM_STATEMENT.md       Problem definition + Malaysian context
│   ├── PRD_SYNTHESIS.md           Synthesized PRD from existing assets
│   ├── FEATURE_SPEC_AGENTS.md     6 Claude agents specification
│   ├── FEATURE_SPEC_TRANSACTIONS.md Transaction categorization feature
│   ├── FEATURE_SPEC_DEBT.md       Tri-tier debt management feature
│   └── FEATURE_SPEC_ADVICE.md     Financial advice generation feature
├── plans/
│   ├── ARCHITECTURE.md            System architecture + diagrams
│   ├── TECHNICAL_PLAN.md          Implementation approach
│   ├── DATA_MODEL.md              Database schema + relationships
│   └── ADR/
│       ├── 001-AGENT-ORCHESTRATION.md   How 6 agents coordinate
│       ├── 002-BANK-PARSING.md          Malaysian bank format handling
│       └── 003-LEGAL-COMPLIANCE.md      Disclaimer strategy
├── tasks/
│   ├── TASK_REGISTRY.md           Master task list
│   └── phases/
│       ├── PHASE_1_FOUNDATION.md  Backend + DB setup
│       ├── PHASE_2_AGENTS.md      Agent implementation
│       ├── PHASE_3_FRONTEND.md    React UI
│       └── PHASE_4_DEPLOYMENT.md  AWS deployment
├── constraints/
│   ├── SECURITY.md                Financial data protection
│   ├── COMPLIANCE.md              PDPA + legal disclaimers
│   └── BEST_PRACTICES.md          Coding standards
├── testing/
│   ├── TESTING_STRATEGY.md        Overall approach
│   ├── AGENT_TESTING.md           How to test AI agents
│   └── CI_CD_SPEC.md              GitHub Actions pipeline
└── audit/
    ├── QUALITY_GATES.md           Phase exit criteria
    └── SCORING_RUBRIC.md          Quality scoring system

agents/                            [Project root level]
├── AGENT_INDEX.md                 Agent registry and status
├── definitions/
│   ├── categorizer.md             Transaction categorization agent
│   ├── debt-detector.md           Debt detection agent
│   ├── pattern-analyzer.md        Pattern analysis agent
│   ├── predictor.md               Prediction agent
│   ├── query.md                   Query agent
│   └── advisor.md                 Financial advisor agent
└── orchestration/
    ├── ROUTING_RULES.md           When to delegate to which agent
    ├── HANDOFF_PROTOCOLS.md       How agents pass work
    └── CONFLICT_RESOLUTION.md     Overlapping responsibility handling

narrative/                         [Project root level]
├── PORTFOLIO_SUMMARY.md           Executive summary for recruiters
├── RESUME_BULLETS.md              Achievement statements
└── INTERVIEW_TALKING_POINTS.md    Discussion topics
```

---

## Document Status Legend

| Status | Meaning |
|--------|---------|
| Done | Document complete and reviewed |
| In Progress | Currently being written |
| Pending | Not yet started |
| Needs Review | Complete but requires validation |
| Blocked | Waiting on external input |

---

## Specification Documents Status

### Core Specifications (specs/)

| Document | Status | Owner | Last Updated |
|----------|--------|-------|--------------|
| PROBLEM_STATEMENT.md | Done | Faisal | 2026-01-10 |
| PRD_SYNTHESIS.md | Done | Faisal | 2026-01-10 |
| FEATURE_SPEC_AGENTS.md | Done | Faisal | 2026-01-10 |
| FEATURE_SPEC_TRANSACTIONS.md | Pending | - | - |
| FEATURE_SPEC_DEBT.md | Pending | - | - |
| FEATURE_SPEC_ADVICE.md | Pending | - | - |

### Planning Documents (plans/)

| Document | Status | Owner | Last Updated |
|----------|--------|-------|--------------|
| ARCHITECTURE.md | Done | Faisal | 2026-01-10 |
| TECHNICAL_PLAN.md | Pending | - | - |
| DATA_MODEL.md | Pending | - | - |
| ADR/001-AGENT-ORCHESTRATION.md | Done | Faisal | 2026-01-10 |
| ADR/002-BANK-PARSING.md | Pending | - | - |
| ADR/003-LEGAL-COMPLIANCE.md | Pending | - | - |

### Task Documents (tasks/)

| Document | Status | Owner | Last Updated |
|----------|--------|-------|--------------|
| TASK_REGISTRY.md | Done | Faisal | 2026-01-10 |
| phases/PHASE_1_FOUNDATION.md | Done | Faisal | 2026-01-10 |
| phases/PHASE_2_AGENTS.md | Done | Faisal | 2026-01-10 |
| phases/PHASE_3_FRONTEND.md | Done | Faisal | 2026-01-10 |
| phases/PHASE_4_DEPLOYMENT.md | Done | Faisal | 2026-01-10 |

### Agent Definitions (agents/)

| Document | Status | Owner | Last Updated |
|----------|--------|-------|--------------|
| AGENT_INDEX.md | Done | Faisal | 2026-01-10 |
| definitions/categorizer.md | Done | Faisal | 2026-01-10 |
| definitions/debt-detector.md | Done | Faisal | 2026-01-10 |
| definitions/pattern-analyzer.md | Done | Faisal | 2026-01-10 |
| definitions/predictor.md | Done | Faisal | 2026-01-10 |
| definitions/query.md | Done | Faisal | 2026-01-10 |
| definitions/advisor.md | Done | Faisal | 2026-01-10 |
| orchestration/ROUTING_RULES.md | Done | Faisal | 2026-01-10 |
| orchestration/HANDOFF_PROTOCOLS.md | Done | Faisal | 2026-01-10 |

### Testing Documents (testing/)

| Document | Status | Owner | Last Updated |
|----------|--------|-------|--------------|
| TESTING_STRATEGY.md | Done | Faisal | 2026-01-10 |
| AGENT_TESTING.md | Pending | - | - |
| CI_CD_SPEC.md | Pending | - | - |

### Audit Documents (audit/)

| Document | Status | Owner | Last Updated |
|----------|--------|-------|--------------|
| QUALITY_GATES.md | Done | Faisal | 2026-01-10 |
| SCORING_RUBRIC.md | Pending | - | - |

### Portfolio Documents (narrative/)

| Document | Status | Owner | Last Updated |
|----------|--------|-------|--------------|
| PORTFOLIO_SUMMARY.md | Done | Faisal | 2026-01-10 |
| RESUME_BULLETS.md | Pending | - | - |
| INTERVIEW_TALKING_POINTS.md | Pending | - | - |

---

## Cross-References

### From Existing Documentation

The following existing documents were synthesized into this spec-kit:

| Original Document | Synthesized Into |
|-------------------|------------------|
| 01_DUITSEDAR_PRD.md | PRD_SYNTHESIS.md, PROBLEM_STATEMENT.md |
| 02_TECHNICAL_ARCHITECTURE.md | ARCHITECTURE.md, DATA_MODEL.md |
| 03_CLAUDE_AGENT_PROMPTS.md | agents/definitions/*.md |
| 04_DATABASE_SCHEMA.md | DATA_MODEL.md |
| 05_API_SPECIFICATION.md | TECHNICAL_PLAN.md |
| 06_DEVELOPMENT_ROADMAP.md | tasks/phases/*.md |
| 07_TESTING_STRATEGY.md | testing/TESTING_STRATEGY.md |
| 08_DEPLOYMENT_GUIDE.md | phases/PHASE_4_DEPLOYMENT.md |
| 09_CLAUDE_CODE_PROMPTS.md | Prompt engineering reference |
| 10_PROPOSED_IMPROVEMENTS.md | Backlog items |

---

## How to Use This Spec-Kit

### For Development

1. Start with [Constitution](memory/constitution.md) — understand core principles
2. Read [Problem Statement](specs/PROBLEM_STATEMENT.md) — understand the "why"
3. Review [Architecture](plans/ARCHITECTURE.md) — understand the "how"
4. Check [Task Registry](tasks/TASK_REGISTRY.md) — find your next task
5. Reference agent definitions as needed

### For Code Review

1. Verify against [Constitution](memory/constitution.md) principles
2. Check [Quality Gates](audit/QUALITY_GATES.md) criteria
3. Validate agent behavior against definitions

### For Portfolio/Interview

1. Read [Portfolio Summary](../narrative/PORTFOLIO_SUMMARY.md)
2. Review [Resume Bullets](../narrative/RESUME_BULLETS.md)
3. Prepare with [Interview Talking Points](../narrative/INTERVIEW_TALKING_POINTS.md)

---

## Clarification Points

Items requiring human input before implementation:

| ID | Question | Impact | Status |
|----|----------|--------|--------|
| CL-001 | Which Malaysian banks have sample statement formats available? | Bank parser implementation | Open |
| CL-002 | Specific PDPA compliance requirements for financial data? | Security implementation | Open |
| CL-003 | AWS budget constraints for deployment? | Infrastructure decisions | Open |

---

**Generated**: 2026-01-10
**Generator**: Claude Code with Spec-Kit Integration
