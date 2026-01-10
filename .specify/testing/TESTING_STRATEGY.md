# RinggitSense Testing Strategy

> Comprehensive testing approach for AI-powered financial platform

**Version**: 1.0.0
**Last Updated**: 2026-01-10

---

## Testing Philosophy

RinggitSense handles sensitive financial data and provides AI-generated insights. Our testing strategy must ensure:

1. **Data Accuracy**: Financial calculations are always correct
2. **Agent Reliability**: AI agents produce consistent, accurate outputs
3. **Security**: User data is protected at all times
4. **User Experience**: Application works smoothly across devices

---

## Test Pyramid

```
                    ┌─────────────────┐
                    │      E2E        │  5%
                    │     Tests       │  (Playwright)
                    ├─────────────────┤
                    │   Integration   │  15%
                    │     Tests       │  (API + DB)
                    ├─────────────────┤
                    │   Agent Tests   │  20%
                    │  (Golden Data)  │  (Claude mocks)
                    ├─────────────────┤
                    │                 │
                    │   Unit Tests    │  60%
                    │                 │  (pytest, jest)
                    └─────────────────┘
```

---

## Testing Layers

### 1. Unit Tests (60%)

**Backend (pytest)**:
- Models and schemas
- Service functions
- Utility functions
- Statement parsers
- Agent prompt formatting

**Frontend (Jest + React Testing Library)**:
- Components
- Hooks
- Utility functions
- Store actions

**Coverage Target**: 80% minimum

**Example Backend Test**:
```python
# tests/unit/services/test_categorizer.py
import pytest
from src.agents.categorizer import CategorizerAgent

class TestCategorizerAgent:
    def test_categorize_food_transaction(self, mock_claude):
        agent = CategorizerAgent()
        result = agent.categorize({
            "description": "MCDONALD'S SUNWAY",
            "amount": 25.90,
            "source": "Maybank"
        })
        assert result["category"] == "FOOD"
        assert result["confidence"] >= 0.9

    def test_categorize_toll_transaction(self, mock_claude):
        agent = CategorizerAgent()
        result = agent.categorize({
            "description": "PLUS TOLL PLZ SUBANG",
            "amount": 3.20,
            "source": "Touch n Go"
        })
        assert result["category"] == "TRANSPORT"
        assert result["subcategory"] == "toll"
```

---

### 2. Agent Tests (20%)

AI agents require special testing approaches:

#### Golden Dataset Testing

Pre-labeled datasets to verify agent accuracy:

| Agent | Dataset Size | Accuracy Target |
|-------|--------------|-----------------|
| AG-01 Categorizer | 500 transactions | >95% |
| AG-02 Debt Detector | 100 debt scenarios | >90% recall, >85% precision |
| AG-03 Pattern Analyzer | 10 3-month datasets | >=3 patterns per dataset |
| AG-04 Predictor | 10 6-month datasets | Within 15% of actual |
| AG-05 Query Agent | 100 questions | >90% correct interpretation |
| AG-06 Advisor | 50 profiles | 100% disclaimers present |

**Golden Dataset Format**:
```json
// golden_datasets/categorizer/transactions.json
{
  "dataset_version": "1.0",
  "created_date": "2026-01-10",
  "cases": [
    {
      "id": "cat_001",
      "input": {
        "description": "MCDONALD'S SUNWAY PYRAMID",
        "amount": 25.90,
        "source": "Maybank"
      },
      "expected_output": {
        "category": "FOOD",
        "subcategory": "fast_food",
        "merchant_name": "McDonald's"
      },
      "min_confidence": 0.90
    }
  ]
}
```

#### Behavioral Testing

Test agent behavior in edge cases:

```python
# tests/agents/test_categorizer_behavioral.py
class TestCategorizerBehavioral:
    def test_low_confidence_flagged(self, agent):
        """Ambiguous transactions should have low confidence"""
        result = agent.categorize({
            "description": "TRX DIGITAL",
            "amount": 150.00,
            "source": "RHB"
        })
        assert result["confidence"] < 0.7

    def test_malaysian_context_recognized(self, agent):
        """Should understand Malaysian merchants"""
        result = agent.categorize({
            "description": "MAMAK HJ SYED PJ",
            "amount": 12.50,
            "source": "Touch n Go"
        })
        assert result["category"] == "FOOD"
        assert "mamak" in result["subcategory"].lower()

    def test_malay_terms_understood(self, agent):
        """Should understand Malay transaction terms"""
        result = agent.categorize({
            "description": "BAYAR BILL TNB",
            "amount": 150.00,
            "source": "Maybank"
        })
        assert result["category"] == "BILLS"
```

#### Adversarial Testing

Test agent resilience to unusual inputs:

```python
# tests/agents/test_categorizer_adversarial.py
class TestCategorizerAdversarial:
    def test_empty_description(self, agent):
        """Should handle empty description gracefully"""
        result = agent.categorize({
            "description": "",
            "amount": 50.00,
            "source": "Maybank"
        })
        assert result["category"] == "OTHER"
        assert result["confidence"] < 0.5

    def test_special_characters(self, agent):
        """Should handle special characters"""
        result = agent.categorize({
            "description": "TXN@#$%^&*()_+=",
            "amount": 100.00,
            "source": "RHB"
        })
        assert result is not None  # No crash

    def test_very_long_description(self, agent):
        """Should truncate and handle long descriptions"""
        result = agent.categorize({
            "description": "A" * 1000,
            "amount": 50.00,
            "source": "Maybank"
        })
        assert result is not None  # No crash
```

---

### 3. Integration Tests (15%)

Test component interactions:

**API + Database**:
```python
# tests/integration/test_transaction_api.py
class TestTransactionAPI:
    async def test_create_and_retrieve_transaction(self, client, db):
        # Create
        response = await client.post("/transactions", json={
            "description": "TEST TRANSACTION",
            "amount": 100.00,
            "category": "FOOD"
        })
        assert response.status_code == 201
        txn_id = response.json()["data"]["id"]

        # Retrieve
        response = await client.get(f"/transactions/{txn_id}")
        assert response.status_code == 200
        assert response.json()["data"]["description"] == "TEST TRANSACTION"
```

**API + Agent Pipeline**:
```python
# tests/integration/test_upload_pipeline.py
class TestUploadPipeline:
    async def test_full_pipeline_execution(self, client, mock_claude):
        # Upload statement
        with open("tests/fixtures/sample_statement.pdf", "rb") as f:
            response = await client.post(
                "/upload/statement",
                files={"file": f}
            )

        assert response.status_code == 200
        result = response.json()["data"]

        # Verify all agents were called
        assert result["categorization"]["processed"] > 0
        assert "debt_analysis" in result
        assert "patterns" in result
        assert "prediction" in result
        assert "advice" in result
```

---

### 4. End-to-End Tests (5%)

Critical user journeys using Playwright:

```typescript
// tests/e2e/upload-journey.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Statement Upload Journey', () => {
  test('user can upload statement and see results', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to upload
    await page.click('text=Upload Statement');

    // Upload file
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.click('text=Choose File');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles('tests/fixtures/sample_statement.pdf');

    // Wait for processing
    await expect(page.locator('text=Processing')).toBeVisible();
    await expect(page.locator('text=Complete')).toBeVisible({ timeout: 30000 });

    // Verify results displayed
    await expect(page.locator('[data-testid="transaction-count"]')).toContainText(/\d+ transactions/);
    await expect(page.locator('[data-testid="category-chart"]')).toBeVisible();
  });
});
```

---

## Test Data Management

### Fixtures

```
tests/
├── fixtures/
│   ├── statements/
│   │   ├── maybank_sample.pdf
│   │   ├── cimb_sample.csv
│   │   └── tng_sample.csv
│   ├── transactions/
│   │   └── sample_transactions.json
│   └── users/
│       └── test_user.json
└── golden_datasets/
    ├── categorizer/
    ├── debt_detector/
    ├── pattern_analyzer/
    ├── predictor/
    ├── query_agent/
    └── advisor/
```

### Data Generation

```python
# tests/factories.py
import factory
from src.models import Transaction, User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@test.com')
    name = factory.Faker('name')

class TransactionFactory(factory.Factory):
    class Meta:
        model = Transaction

    description = factory.Faker('sentence', nb_words=3)
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    category = factory.Iterator(['FOOD', 'TRANSPORT', 'BILLS', 'SHOPPING'])
```

---

## Mocking Strategy

### Claude API Mocking

```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_claude(monkeypatch):
    async def mock_create(*args, **kwargs):
        # Return predictable responses based on input
        user_message = kwargs.get('messages', [{}])[0].get('content', '')

        if 'MCDONALD' in user_message.upper():
            return MockResponse(content='{"category": "FOOD", "confidence": 0.98}')
        elif 'TOLL' in user_message.upper():
            return MockResponse(content='{"category": "TRANSPORT", "confidence": 0.99}')
        else:
            return MockResponse(content='{"category": "OTHER", "confidence": 0.5}')

    monkeypatch.setattr('anthropic.AsyncAnthropic.messages.create', mock_create)
```

### Database Mocking

```python
@pytest.fixture
async def test_db():
    """Create test database for each test"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run unit tests
        run: pytest tests/unit --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  agent-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run agent tests
        run: pytest tests/agents -v
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY_TEST }}

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: pytest tests/integration

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Playwright
        run: npx playwright install
      - name: Run E2E tests
        run: npx playwright test
```

---

## Test Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Code Coverage | 80% | pytest-cov |
| Agent Accuracy | Per agent target | Golden dataset |
| Test Reliability | <1% flaky | CI history |
| Test Speed | Unit <10s, Full <5min | CI timing |

---

## Testing Checklist

Before merging any PR:

- [ ] Unit tests pass
- [ ] Agent tests pass (if agent modified)
- [ ] Integration tests pass (if API modified)
- [ ] No decrease in coverage
- [ ] New code has tests
- [ ] E2E for critical paths

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
