# Phase 2: AI Agents

> Implementation of six Claude agents with orchestration

**Target**: Week 3-4
**Status**: Not Started
**Tasks**: 15
**Depends On**: Phase 1

---

## Objectives

1. Implement base agent interface
2. Build orchestration layer
3. Implement all six specialized agents
4. Create sequential processing pipeline
5. Build query routing system
6. Establish agent testing framework

---

## Task Breakdown

### A-001: Base Agent Class

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: F-012

Create abstract base class for all agents:

```python
class BaseAgent(ABC):
    def __init__(self, model: str, temperature: float):
        self.model = model
        self.temperature = temperature
        self.client = Anthropic()

    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        """Process input and return structured output"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the agent's system prompt"""
        pass

    async def call_claude(self, user_message: str) -> str:
        """Make API call to Claude"""
        pass
```

**Acceptance Criteria**:
- [ ] Abstract base class implemented
- [ ] Common Claude API call method
- [ ] Error handling for API failures
- [ ] Retry logic with exponential backoff
- [ ] Response parsing utilities

---

### A-002: Agent Orchestrator

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-001

Central coordinator for all agents:

```python
class AgentOrchestrator:
    async def process_upload(self, transactions: List) -> ProcessingResult
    async def process_query(self, question: str, context: dict) -> QueryResult
    def route(self, request: Request) -> str  # Returns agent ID
```

**Features**:
- Agent registration
- Request routing
- Sequential pipeline execution
- Response aggregation
- Error handling

**Acceptance Criteria**:
- [ ] All agents registered
- [ ] Routing logic implemented
- [ ] Pipeline execution working
- [ ] Error handling for agent failures
- [ ] Logging of agent calls

---

### A-003: AG-01 Categorizer Agent

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-002

Transaction categorization agent:

**Input**: Transaction description, amount, source, date
**Output**: Category, confidence, subcategory, merchant_name, reasoning

**Features**:
- Single transaction processing
- Batch processing (up to 50)
- Malaysian merchant recognition
- Low-confidence flagging

**Acceptance Criteria**:
- [ ] Single transaction categorization working
- [ ] Batch processing working
- [ ] >95% accuracy on test dataset
- [ ] <500ms latency per transaction
- [ ] Malaysian context recognized (toll, mamak, TnG)

---

### A-004: AG-02 Debt Detector Agent

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-002

Tri-tier debt detection agent:

**Input**: Transaction with context (recurring pattern, comments)
**Output**: is_debt_related, debt_tier, provider, confidence, indicators

**Tiers**:
- FORMAL: PTPTN, car loan, personal loan, mortgage
- BNPL: SPayLater, GrabPayLater, Atome
- HUTANG: Transfers with debt keywords

**Acceptance Criteria**:
- [ ] FORMAL debt detection working
- [ ] BNPL detection working
- [ ] HUTANG detection working (comment analysis)
- [ ] >90% recall (catch all debts)
- [ ] >85% precision (minimize false positives)

---

### A-005: AG-03 Pattern Analyzer Agent

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-002

Spending pattern discovery agent:

**Input**: Transaction history (3+ months)
**Output**: List of patterns with type, evidence, impact, confidence

**Pattern Types**:
- TEMPORAL: Weekend surge, payday effect
- BUNDLE: Co-occurring expenses
- HIDDEN_COST: Toll, delivery fees, subscriptions
- TREND: Rising/falling categories
- ANOMALY: Unusual spending

**Acceptance Criteria**:
- [ ] Temporal pattern detection working
- [ ] Bundle detection working
- [ ] Hidden cost aggregation working
- [ ] Trend analysis working
- [ ] Anomaly detection working
- [ ] <3s analysis time

---

### A-006: AG-04 Predictor Agent

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-002

Spending forecast agent:

**Input**: Historical transactions, known upcoming events
**Output**: Total predicted, confidence interval, by-category breakdown

**Methodology**:
1. Historical baseline (weighted average)
2. Trend adjustment
3. Seasonal adjustment (festivals)
4. Known event incorporation

**Acceptance Criteria**:
- [ ] Baseline calculation correct
- [ ] Trend adjustment working
- [ ] Seasonal factors applied
- [ ] Known events included
- [ ] Within 15% of actual (post-validation)
- [ ] Confidence intervals provided

---

### A-007: AG-05 Query Agent

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-002

Natural language question answering agent:

**Input**: User question, transaction context
**Output**: Natural language answer, supporting data, visualization hints

**Query Types**:
- Aggregation: "How much on food?"
- Comparison: "More than last month?"
- Ranking: "Top 3 expenses?"
- Search: "Show Shopee transactions"
- Trend: "How has toll changed?"

**Features**:
- English and Malay support
- Delegation to other agents
- Follow-up question suggestions

**Acceptance Criteria**:
- [ ] All query types handled
- [ ] Malay queries understood
- [ ] Delegation working
- [ ] <2s response time
- [ ] Natural conversational tone

---

### A-008: AG-06 Advisor Agent

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-002

Financial guidance agent:

**Input**: User profile, patterns, debt summary, goals
**Output**: Prioritized recommendations with disclaimers

**Categories**:
- SPENDING: Cut unnecessary expenses
- SAVING: Build emergency fund
- DEBT: Payoff prioritization
- BUDGETING: Allocation recommendations
- BEHAVIOR: Habit changes

**Mandatory**:
- Disclaimers in EVERY response
- Cultural sensitivity (family obligations OK)

**Acceptance Criteria**:
- [ ] All advice categories covered
- [ ] Disclaimers always present
- [ ] Recommendations specific, not generic
- [ ] Prioritized by impact
- [ ] Culturally sensitive

---

### A-009: Sequential Pipeline

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-003, A-004, A-005, A-006, A-008

Upload processing pipeline:

```
Upload → Categorizer → Debt Detector → Pattern Analyzer → Predictor → Advisor
```

**Features**:
- Transaction batching
- Inter-agent data passing
- Progress tracking
- Partial failure handling

**Acceptance Criteria**:
- [ ] Full pipeline executes
- [ ] Data passes between agents correctly
- [ ] Handles partial failures gracefully
- [ ] <30s for 100 transactions
- [ ] Results aggregated correctly

---

### A-010: Query Routing Logic

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-007

Intent classification for query routing:

**Routes**:
- Category questions → AG-01
- Debt questions → AG-02
- Pattern questions → AG-03
- Prediction questions → AG-04
- Advice questions → AG-06
- General questions → AG-05

**Acceptance Criteria**:
- [ ] Intent classification accurate (>90%)
- [ ] Routing to correct agent
- [ ] Delegation from AG-05 working
- [ ] Fallback to AG-05 for ambiguous queries

---

### A-011: Agent Response Caching

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: A-002

Cache expensive agent responses:

**Cache Strategy**:
- Pattern analysis: 24 hours
- Predictions: 24 hours
- Categorization: Permanent (same input = same output)
- Advice: 1 hour

**Implementation**: Redis

**Acceptance Criteria**:
- [ ] Caching layer implemented
- [ ] TTL per response type
- [ ] Cache invalidation on new data
- [ ] Cache hit/miss logging

---

### A-012: Claude API Rate Limiting

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: A-002

Prevent API overuse:

**Limits**:
- Per user: 100 agent calls/hour
- Global: 1000 calls/hour
- Batch optimization for categorization

**Acceptance Criteria**:
- [ ] Rate limiting implemented
- [ ] User-level tracking
- [ ] Graceful degradation message
- [ ] Batch processing to reduce calls

---

### A-013: Golden Dataset - Categorizer

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-003

Create test dataset for Categorizer agent:

**Dataset**:
- 500 labeled transactions
- All categories represented
- Malaysian merchants included
- Edge cases included

**Acceptance Criteria**:
- [ ] 500 transactions labeled
- [ ] Human-verified ground truth
- [ ] Covers all categories
- [ ] Includes Malaysian-specific examples
- [ ] >95% accuracy on this dataset

---

### A-014: Agent Unit Tests

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-003 through A-008

Unit tests for each agent:

**Coverage**:
- AG-01: 50+ test cases
- AG-02: 30+ test cases
- AG-03: 20+ test cases
- AG-04: 20+ test cases
- AG-05: 50+ test cases
- AG-06: 30+ test cases

**Acceptance Criteria**:
- [ ] All agents tested
- [ ] Edge cases covered
- [ ] Mock Claude API for fast tests
- [ ] 80% coverage per agent

---

### A-015: Pipeline Integration Tests

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: A-009

End-to-end pipeline tests:

**Scenarios**:
- New user upload (first statement)
- Returning user upload (additional data)
- Query after upload
- Error handling (agent failure)

**Acceptance Criteria**:
- [ ] Full pipeline tested
- [ ] Data integrity verified
- [ ] Error scenarios tested
- [ ] Performance benchmarks established

---

## Exit Criteria

Phase 2 is complete when:

1. ✅ All 6 agents implemented and functional
2. ✅ Sequential pipeline processes uploads
3. ✅ Query routing works correctly
4. ✅ >90% accuracy on golden dataset
5. ✅ All A-xxx tasks marked Done

---

## Dependencies

| External | Internal |
|----------|----------|
| Anthropic Claude API key | Phase 1 complete |
| Redis (for caching) | A-011 |

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
