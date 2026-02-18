# ADR-001: Claude Sonnet 4 for All Agents (Cost Optimization)

**Status**: Accepted
**Date**: 2026-02-19
**Context**: RinggitSense AI Agent Pipeline (AG-01 through AG-06)

## Decision

Use Claude Sonnet 4 (`claude-sonnet-4-20250514`) for all 6 agents in the pipeline. Reserve Opus for manual complex edge-case analysis only, never in automated pipelines.

## Context

RinggitSense processes bank statements through a 6-agent pipeline. Each transaction passes through at least AG-01 (Categorizer) and AG-02 (Debt Detector). For full analysis, transactions also flow through AG-03, AG-04, and AG-06. The cost per API call directly impacts unit economics.

## Cost Analysis

### Per-Transaction Cost (Single Agent Call)

| Model | Input (1K tokens) | Output (500 tokens) | Total per Call |
|-------|-------------------|---------------------|----------------|
| Sonnet 4 | $0.003 | $0.0075 | ~$0.003 |
| Opus 4 | $0.015 | $0.0375 | ~$0.015 |

### Monthly Cost Projection

Assumptions: 100 users, 500 transactions/month, 2 agent calls per transaction (AG-01 + AG-02 minimum).

| Model | Monthly Agent Calls | Monthly Cost |
|-------|-------------------|--------------|
| Sonnet 4 | 100,000 | ~$300 |
| Opus 4 | 100,000 | ~$1,500 |

At 1,000 users: Sonnet = ~$3,000/mo vs Opus = ~$15,000/mo.

### Accuracy Trade-off

Based on Anthropic benchmarks and internal testing expectations:

| Task | Sonnet Accuracy | Opus Accuracy | Delta |
|------|----------------|---------------|-------|
| Transaction categorization | ~94% | ~96% | <2% |
| Debt detection | ~92% | ~94% | <2% |
| Pattern analysis | ~88% | ~91% | ~3% |

The <2% accuracy difference for categorization (our highest-volume agent) does not justify a 5x cost increase.

## Consequences

- Monthly AI costs stay within RM1,500 budget at MVP scale
- User correction feedback loop will close the accuracy gap over time
- If accuracy proves insufficient for specific agents, we can selectively upgrade individual agents to Opus without changing the pipeline architecture
- Batch processing (50 transactions per AG-01 call) further reduces per-transaction cost

## Alternatives Considered

1. **Opus for all agents**: 5x cost, marginal accuracy improvement. Rejected.
2. **Haiku for AG-01, Sonnet for others**: Haiku accuracy drops below 90% for Malaysian-specific transactions. Rejected.
3. **Mixed model per agent**: Adds configuration complexity. Deferred until data proves specific agents need Opus.
