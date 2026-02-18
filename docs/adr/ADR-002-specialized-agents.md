# ADR-002: Six Specialized Agents Over Single Monolithic Prompt

**Status**: Accepted
**Date**: 2026-02-19
**Context**: RinggitSense AI Architecture Design

## Decision

Use 6 specialized, single-responsibility agents (AG-01 through AG-06) connected via a sequential pipeline with validated data contracts, rather than a single monolithic prompt that handles all tasks.

## Context

RinggitSense needs to categorize transactions, detect debts, find patterns, predict spending, answer questions, and give advice. These could be handled by one large prompt or by dedicated agents.

## Rationale

### 1. Accuracy Through Specialization

Each agent has a focused system prompt with domain-specific context:
- AG-01 knows Malaysian merchant names, toll plazas, and food terms
- AG-02 knows the three-tier debt system (FORMAL/BNPL/HUTANG)
- AG-06 knows cultural sensitivity around hutang

A single prompt would need to carry all this context simultaneously, reducing attention on the specific task.

### 2. Cost Optimization

Not every transaction needs every agent:
- **Upload flow**: AG-01 + AG-02 (mandatory), AG-03/04/06 (periodic batch)
- **Query flow**: AG-05 only, with optional routing to AG-04 or AG-06

A monolithic prompt would process everything regardless of need.

### 3. Testability and Debugging

Each agent has:
- Isolated input/output contracts (Pydantic models in `src/schemas/agents/`)
- Independent test harness with golden datasets
- Traceable failures to a specific agent

A monolithic prompt failure is a black box — you can't tell which subtask failed.

### 4. Independent Iteration

Agents can be improved independently:
- Upgrade AG-01's prompt without touching debt detection
- Switch AG-04 to a different model if prediction accuracy is low
- A/B test prompt variations per agent

### 5. Contract Validation

The `AgentPipeline` class validates data at each handoff point. If AG-01 produces malformed output, `AgentContractViolation` is raised before AG-02 ever sees it. This catches data quality issues at the boundary rather than letting them cascade.

## Consequences

- 6 separate prompt files to maintain (manageable, each is focused)
- Pipeline orchestration adds ~100ms latency per handoff
- More API calls per full analysis (but each call is cheaper and more focused)
- Data contracts (`src/schemas/agents/`) must be kept in sync with agent prompts

## Alternatives Considered

1. **Single monolithic prompt**: Simpler architecture but poor debuggability, higher per-call cost, no selective execution. Rejected.
2. **3 agents (categorize+detect, analyze+predict, query+advise)**: Partial specialization, but couples unrelated tasks. Rejected.
3. **12 micro-agents (one per sub-task)**: Over-engineering at current scale. Deferred.
