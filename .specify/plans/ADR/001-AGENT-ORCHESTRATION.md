# ADR-001: Agent Orchestration Strategy

> Architecture Decision Record for the six-agent coordination system

**Status**: Accepted
**Date**: 2026-01-10
**Decision Makers**: Faisal

---

## Context

RinggitSense requires multiple AI capabilities:
- Transaction categorization
- Debt detection across three tiers
- Spending pattern analysis
- Future spending prediction
- Natural language query handling
- Personalized financial advice

We need to decide how to structure these capabilities within the system.

---

## Decision

**We will implement a six-agent architecture with centralized orchestration.**

Each agent has a single, well-defined responsibility:

| Agent | Responsibility |
|-------|---------------|
| AG-01 Categorizer | Classify transactions into categories |
| AG-02 Debt Detector | Identify debt across FORMAL/BNPL/HUTANG tiers |
| AG-03 Pattern Analyzer | Discover spending patterns and anomalies |
| AG-04 Predictor | Forecast future spending |
| AG-05 Query Agent | Answer natural language questions |
| AG-06 Advisor | Provide financial guidance |

### Orchestration Model

A centralized orchestrator will:
1. Route incoming requests to appropriate agents
2. Manage sequential pipelines for statement processing
3. Handle delegation between agents
4. Cache agent responses
5. Enforce rate limits

---

## Alternatives Considered

### Alternative 1: Single Monolithic Agent

**Description**: One large prompt handles all capabilities.

**Pros**:
- Simpler implementation
- No orchestration overhead
- Lower latency for simple queries

**Cons**:
- Prompt becomes unwieldy (>10,000 tokens)
- Difficult to test individual capabilities
- Higher variance in outputs
- Cannot optimize cost per capability
- Changes affect everything

**Rejected because**: Violates single-responsibility principle, makes testing and iteration difficult.

### Alternative 2: Autonomous Multi-Agent System

**Description**: Agents communicate peer-to-peer without central orchestrator.

**Pros**:
- Flexible agent interactions
- Emergent problem-solving
- Agents can self-organize

**Cons**:
- Unpredictable behavior
- Difficult to debug
- Higher latency from agent negotiation
- Cost unpredictable
- Hallucination risk increases

**Rejected because**: Financial domain requires predictable, auditable behavior.

### Alternative 3: Microservice-per-Agent

**Description**: Each agent deployed as separate microservice.

**Pros**:
- Independent scaling
- Independent deployment
- Technology flexibility

**Cons**:
- Operational complexity
- Network overhead
- Overkill for MVP
- Higher infrastructure cost

**Rejected because**: Premature optimization for our scale.

---

## Consequences

### Positive

1. **Testability**: Each agent tested in isolation
2. **Maintainability**: Changes to one agent don't affect others
3. **Cost optimization**: Different temperature/token limits per agent
4. **Predictability**: Clear routing rules, deterministic behavior
5. **Debuggability**: Can trace which agent produced which output

### Negative

1. **Orchestration complexity**: Need to build routing logic
2. **Latency**: Sequential pipelines add latency
3. **State management**: Need to pass context between agents
4. **Testing overhead**: Need tests for each agent plus integration tests

### Mitigations

| Risk | Mitigation |
|------|------------|
| Orchestration complexity | Use well-documented routing rules |
| Pipeline latency | Parallelize where possible, cache results |
| State management | Standardized context format |
| Testing overhead | Golden datasets, automated testing |

---

## Implementation Notes

### Orchestrator Interface

```python
class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "AG-01": CategorizerAgent(),
            "AG-02": DebtDetectorAgent(),
            "AG-03": PatternAnalyzerAgent(),
            "AG-04": PredictorAgent(),
            "AG-05": QueryAgent(),
            "AG-06": AdvisorAgent(),
        }

    async def process_upload(self, transactions):
        """Sequential pipeline for statement upload"""
        pass

    async def process_query(self, question, context):
        """Route query to appropriate agent"""
        pass

    def route(self, request):
        """Determine which agent handles request"""
        pass
```

### Routing Logic

```python
def route(self, request):
    if request.type == "UPLOAD":
        return ["AG-01", "AG-02", "AG-03", "AG-04", "AG-06"]

    if request.type == "QUERY":
        return self._classify_intent(request.question)

def _classify_intent(self, question):
    # Keyword-based routing (see ROUTING_RULES.md)
    pass
```

### Agent Communication

Agents do NOT communicate directly. All communication goes through the orchestrator:

```
User → Orchestrator → Agent A → Orchestrator → Agent B → Orchestrator → User
```

This ensures auditability and control.

---

## Related Documents

- [FEATURE_SPEC_AGENTS.md](../../specs/FEATURE_SPEC_AGENTS.md)
- [ROUTING_RULES.md](../../agents/orchestration/ROUTING_RULES.md)
- [Agent definitions](../../agents/definitions/)

---

## Review History

| Date | Reviewer | Action |
|------|----------|--------|
| 2026-01-10 | Faisal | Created, Accepted |

---

**Last Updated**: 2026-01-10
