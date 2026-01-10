# DuitSedar — Testing Strategy

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026

---

## Table of Contents

1. [Testing Overview](#1-testing-overview)
2. [Unit Testing](#2-unit-testing)
3. [Integration Testing](#3-integration-testing)
4. [End-to-End Testing](#4-end-to-end-testing)
5. [AI Agent Testing](#5-ai-agent-testing)
6. [Performance Testing](#6-performance-testing)
7. [Security Testing](#7-security-testing)
8. [Test Data Management](#8-test-data-management)

---

## 1. Testing Overview

### 1.1 Testing Pyramid

```
                    ┌─────────────┐
                    │    E2E      │  10%  - Critical user journeys
                    │   Tests     │
                 ┌──┴─────────────┴──┐
                 │   Integration     │  30%  - API & DB integration
                 │      Tests        │
              ┌──┴───────────────────┴──┐
              │      Unit Tests         │  60%  - Business logic
              │                         │
              └─────────────────────────┘
```

### 1.2 Coverage Targets

| Layer | Target Coverage | Priority |
|-------|-----------------|----------|
| Service Layer | 80% | Must |
| Controllers | 70% | Should |
| Repositories | 60% | Should |
| Utilities | 90% | Must |
| Frontend Components | 50% | Could |

### 1.3 Testing Tools

| Tool | Purpose |
|------|---------|
| JUnit 5 | Backend unit tests |
| Mockito | Mocking dependencies |
| Spring Test | Integration testing |
| TestContainers | Database integration |
| Vitest | Frontend unit tests |
| Playwright | E2E testing |

---

## 2. Unit Testing

### 2.1 Service Layer Tests

```java
// TransactionServiceTest.java
@ExtendWith(MockitoExtension.class)
class TransactionServiceTest {
    
    @Mock
    private TransactionRepository transactionRepository;
    
    @Mock
    private AgentOrchestrator agentOrchestrator;
    
    @InjectMocks
    private TransactionService transactionService;
    
    @Test
    void shouldCategorizeTransaction_WhenFoodMerchant() {
        // Given
        RawTransaction raw = RawTransaction.builder()
            .description("MAMAK HJ SYED TMN SRI")
            .amount(BigDecimal.valueOf(15.50))
            .build();
        
        CategoryResult expectedCategory = new CategoryResult("FOOD", 0.95);
        when(agentOrchestrator.categorize(raw)).thenReturn(expectedCategory);
        
        // When
        Transaction result = transactionService.processTransaction(raw);
        
        // Then
        assertThat(result.getCategory()).isEqualTo("FOOD");
        assertThat(result.getCategoryConfidence()).isGreaterThan(0.9);
    }
    
    @Test
    void shouldDetectBNPL_WhenSPayLaterTransaction() {
        // Given
        RawTransaction raw = RawTransaction.builder()
            .description("SPAYLATER*SHOPEE 3/6")
            .amount(BigDecimal.valueOf(150.00))
            .build();
        
        DebtResult expectedDebt = new DebtResult(true, "BNPL", "SPayLater");
        when(agentOrchestrator.detectDebt(raw)).thenReturn(expectedDebt);
        
        // When
        Transaction result = transactionService.processTransaction(raw);
        
        // Then
        assertThat(result.isDebtRelated()).isTrue();
        assertThat(result.getDebtTier()).isEqualTo("BNPL");
    }
    
    @Test
    void shouldCalculateMonthlyTotal_ForSpecificCategory() {
        // Given
        String userId = "user-123";
        YearMonth month = YearMonth.of(2025, 12);
        List<Transaction> transactions = List.of(
            createTransaction("FOOD", 100.00),
            createTransaction("FOOD", 50.00),
            createTransaction("TRANSPORT", 30.00)
        );
        
        when(transactionRepository.findByUserIdAndMonth(userId, month))
            .thenReturn(transactions);
        
        // When
        BigDecimal foodTotal = transactionService.getCategoryTotal(userId, month, "FOOD");
        
        // Then
        assertThat(foodTotal).isEqualByComparingTo(BigDecimal.valueOf(150.00));
    }
}
```

### 2.2 Parser Tests

```java
// RHBParserTest.java
class RHBParserTest {
    
    private RHBParser parser = new RHBParser();
    
    @Test
    void shouldParseValidCSV() {
        // Given
        String csvContent = """
            Date,Description,Debit,Credit,Balance
            15/12/2025,MAMAK HJ SYED TMN SRI,15.50,,1234.50
            16/12/2025,SALARY DEC 2025,,4500.00,5734.50
            """;
        
        // When
        List<RawTransaction> result = parser.parse(csvContent.getBytes());
        
        // Then
        assertThat(result).hasSize(2);
        assertThat(result.get(0).getDescription()).isEqualTo("MAMAK HJ SYED TMN SRI");
        assertThat(result.get(0).getAmount()).isEqualByComparingTo(BigDecimal.valueOf(15.50));
        assertThat(result.get(1).getAmount()).isEqualByComparingTo(BigDecimal.valueOf(-4500.00)); // Credit = negative
    }
    
    @Test
    void shouldHandleMalformedDate() {
        // Given
        String csvContent = """
            Date,Description,Debit,Credit,Balance
            invalid-date,TEST,10.00,,100.00
            """;
        
        // When/Then
        assertThrows(ParsingException.class, () -> parser.parse(csvContent.getBytes()));
    }
    
    @Test
    void shouldNormalizeMalaysianDateFormat() {
        // Given - Malaysian format: DD/MM/YYYY
        String csvContent = """
            Date,Description,Debit,Credit,Balance
            25/01/2025,TEST,10.00,,100.00
            """;
        
        // When
        List<RawTransaction> result = parser.parse(csvContent.getBytes());
        
        // Then - Should be parsed as January 25, not December 1
        assertThat(result.get(0).getDate()).isEqualTo(LocalDate.of(2025, 1, 25));
    }
}
```

### 2.3 Utility Tests

```java
// AmountUtilsTest.java
class AmountUtilsTest {
    
    @Test
    void shouldParsePositiveAmount() {
        assertThat(AmountUtils.parse("1,234.56")).isEqualByComparingTo(new BigDecimal("1234.56"));
    }
    
    @Test
    void shouldParseNegativeAmount() {
        assertThat(AmountUtils.parse("-1,234.56")).isEqualByComparingTo(new BigDecimal("-1234.56"));
    }
    
    @Test
    void shouldHandleRMPrefix() {
        assertThat(AmountUtils.parse("RM 1,234.56")).isEqualByComparingTo(new BigDecimal("1234.56"));
    }
    
    @Test
    void shouldReturnZeroForInvalidInput() {
        assertThat(AmountUtils.parse("N/A")).isEqualByComparingTo(BigDecimal.ZERO);
    }
}
```

---

## 3. Integration Testing

### 3.1 Repository Integration Tests

```java
// TransactionRepositoryIntegrationTest.java
@DataJpaTest
@AutoConfigureTestDatabase(replace = Replace.NONE)
@Testcontainers
class TransactionRepositoryIntegrationTest {
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("pgvector/pgvector:pg15");
    
    @Autowired
    private TransactionRepository repository;
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Test
    void shouldFindTransactionsByCategory() {
        // Given
        User user = createTestUser();
        entityManager.persist(user);
        
        Transaction food1 = createTransaction(user, "FOOD", 100.00);
        Transaction food2 = createTransaction(user, "FOOD", 50.00);
        Transaction transport = createTransaction(user, "TRANSPORT", 30.00);
        
        entityManager.persist(food1);
        entityManager.persist(food2);
        entityManager.persist(transport);
        entityManager.flush();
        
        // When
        List<Transaction> foodTransactions = repository.findByUserIdAndCategory(
            user.getId(), "FOOD"
        );
        
        // Then
        assertThat(foodTransactions).hasSize(2);
        assertThat(foodTransactions).extracting(Transaction::getCategory)
            .containsOnly("FOOD");
    }
    
    @Test
    void shouldCalculateMonthlySummary() {
        // Given
        User user = createTestUser();
        entityManager.persist(user);
        
        // Create transactions for December 2025
        createAndPersistTransactions(user, YearMonth.of(2025, 12));
        
        // When
        MonthlySummary summary = repository.calculateMonthlySummary(
            user.getId(), 
            LocalDate.of(2025, 12, 1),
            LocalDate.of(2025, 12, 31)
        );
        
        // Then
        assertThat(summary.getTotalExpenses()).isPositive();
        assertThat(summary.getTransactionCount()).isGreaterThan(0);
    }
}
```

### 3.2 API Integration Tests

```java
// TransactionControllerIntegrationTest.java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
class TransactionControllerIntegrationTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private ClerkService clerkService;
    
    @Test
    @WithMockUser
    void shouldUploadAndProcessTransactions() throws Exception {
        // Given
        MockMultipartFile file = new MockMultipartFile(
            "file",
            "transactions.csv",
            "text/csv",
            getTestCSVContent()
        );
        
        when(clerkService.validateAndGetUserId(any())).thenReturn("test-user-id");
        
        // When/Then
        mockMvc.perform(multipart("/api/v1/transactions/upload")
                .file(file)
                .param("source_type", "rhb"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.success").value(true))
            .andExpect(jsonPath("$.data.transactions_processed").isNumber());
    }
    
    @Test
    @WithMockUser
    void shouldReturnPaginatedTransactions() throws Exception {
        // When/Then
        mockMvc.perform(get("/api/v1/transactions")
                .param("page", "1")
                .param("limit", "20"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.data.transactions").isArray())
            .andExpect(jsonPath("$.data.pagination.page").value(1));
    }
    
    @Test
    void shouldReturn401WithoutAuth() throws Exception {
        mockMvc.perform(get("/api/v1/transactions"))
            .andExpect(status().isUnauthorized());
    }
}
```

---

## 4. End-to-End Testing

### 4.1 Critical User Journeys

```typescript
// e2e/upload-and-view.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Transaction Upload Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login via Clerk test mode
    await page.goto('/');
    await loginAsTestUser(page);
  });
  
  test('should upload RHB statement and see categorized transactions', async ({ page }) => {
    // Navigate to upload
    await page.goto('/transactions');
    await page.click('button:has-text("Upload Statement")');
    
    // Upload file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-data/rhb-sample.csv');
    
    // Select source type
    await page.selectOption('select[name="source_type"]', 'rhb');
    
    // Submit
    await page.click('button:has-text("Process")');
    
    // Wait for processing
    await expect(page.locator('.upload-success')).toBeVisible({ timeout: 30000 });
    
    // Verify transactions appear
    await expect(page.locator('.transaction-row')).toHaveCount.greaterThan(0);
    
    // Verify categories assigned
    await expect(page.locator('.category-badge')).toBeVisible();
  });
  
  test('should correct transaction category', async ({ page }) => {
    await page.goto('/transactions');
    
    // Click on a transaction
    await page.click('.transaction-row:first-child');
    
    // Click edit category
    await page.click('button:has-text("Edit Category")');
    
    // Select new category
    await page.selectOption('select[name="category"]', 'ENTERTAINMENT');
    
    // Save
    await page.click('button:has-text("Save")');
    
    // Verify update
    await expect(page.locator('.category-badge:has-text("ENTERTAINMENT")')).toBeVisible();
  });
});

test.describe('Debt Management Flow', () => {
  
  test('should add hutang and track items', async ({ page }) => {
    await page.goto('/debts');
    
    // Click add hutang
    await page.click('button:has-text("Add Hutang")');
    
    // Fill form
    await page.fill('input[name="person_name"]', 'Ahmad');
    await page.selectOption('select[name="direction"]', 'OWE');
    await page.fill('textarea[name="notes"]', 'Test hutang');
    
    // Submit
    await page.click('button:has-text("Create")');
    
    // Verify hutang appears
    await expect(page.locator('.hutang-card:has-text("Ahmad")')).toBeVisible();
    
    // Add item
    await page.click('.hutang-card:has-text("Ahmad")');
    await page.click('button:has-text("Add Item")');
    await page.fill('input[name="description"]', 'Lunch');
    await page.fill('input[name="amount"]', '25.00');
    await page.click('button:has-text("Add")');
    
    // Verify item appears
    await expect(page.locator('.hutang-item:has-text("Lunch")')).toBeVisible();
    await expect(page.locator('.hutang-total')).toContainText('25.00');
  });
});

test.describe('Dashboard Flow', () => {
  
  test('should display financial health score', async ({ page }) => {
    await page.goto('/');
    
    // Verify health score visible
    await expect(page.locator('.health-score')).toBeVisible();
    await expect(page.locator('.health-score-value')).toHaveText(/\d+/);
    
    // Verify score breakdown
    await expect(page.locator('.score-component')).toHaveCount.greaterThan(0);
  });
  
  test('should show spending breakdown chart', async ({ page }) => {
    await page.goto('/');
    
    // Verify chart visible
    await expect(page.locator('.spending-chart')).toBeVisible();
    
    // Verify categories shown
    await expect(page.locator('.category-legend-item')).toHaveCount.greaterThan(0);
  });
});
```

---

## 5. AI Agent Testing

### 5.1 Categorizer Agent Tests

```java
// CategorizerAgentTest.java
@SpringBootTest
class CategorizerAgentTest {
    
    @Autowired
    private CategorizerAgent categorizerAgent;
    
    @Test
    void shouldCategorizeMamak_AsFood() {
        // Given
        RawTransaction txn = RawTransaction.builder()
            .description("MAMAK HJ SYED TMN SRI PETALING")
            .amount(BigDecimal.valueOf(15.50))
            .source("rhb")
            .build();
        
        // When
        CategoryResult result = categorizerAgent.categorize(txn);
        
        // Then
        assertThat(result.getCategory()).isEqualTo("FOOD");
        assertThat(result.getConfidence()).isGreaterThan(0.85);
    }
    
    @Test
    void shouldCategorizePLUS_AsTransport() {
        // Given
        RawTransaction txn = RawTransaction.builder()
            .description("PLUS KARAK")
            .amount(BigDecimal.valueOf(7.80))
            .source("tng")
            .build();
        
        // When
        CategoryResult result = categorizerAgent.categorize(txn);
        
        // Then
        assertThat(result.getCategory()).isEqualTo("TRANSPORT");
        assertThat(result.getSubcategory()).isEqualTo("toll");
    }
    
    @Test
    void shouldHandleBatchCategorization() {
        // Given
        List<RawTransaction> transactions = List.of(
            createTransaction("MAMAK HJ SYED", 15.00),
            createTransaction("PLUS LDP", 5.00),
            createTransaction("UNIFI BILL", 150.00),
            createTransaction("TGV CINEMA", 45.00)
        );
        
        // When
        List<CategoryResult> results = categorizerAgent.categorizeBatch(transactions);
        
        // Then
        assertThat(results).hasSize(4);
        assertThat(results.get(0).getCategory()).isEqualTo("FOOD");
        assertThat(results.get(1).getCategory()).isEqualTo("TRANSPORT");
        assertThat(results.get(2).getCategory()).isEqualTo("BILLS");
        assertThat(results.get(3).getCategory()).isEqualTo("ENTERTAINMENT");
    }
    
    @Test
    void shouldFallbackToRules_WhenAPIFails() {
        // This test would mock Claude API to return error
        // and verify rule-based fallback is used
    }
}
```

### 5.2 Accuracy Validation Test

```java
// CategoryAccuracyTest.java
@SpringBootTest
class CategoryAccuracyTest {
    
    @Autowired
    private CategorizerAgent categorizerAgent;
    
    // Pre-labeled test dataset
    private static final List<LabeledTransaction> TEST_DATA = List.of(
        new LabeledTransaction("MAMAK HJ SYED", "FOOD"),
        new LabeledTransaction("PLUS KARAK", "TRANSPORT"),
        new LabeledTransaction("SHELL PETROL", "TRANSPORT"),
        new LabeledTransaction("UNIFI BILL", "BILLS"),
        new LabeledTransaction("CELCOM RELOAD", "BILLS"),
        new LabeledTransaction("TGV CINEMA", "ENTERTAINMENT"),
        new LabeledTransaction("NETFLIX", "ENTERTAINMENT"),
        new LabeledTransaction("SHOPEE ORDER", "SHOPPING"),
        new LabeledTransaction("LAZADA", "SHOPPING"),
        new LabeledTransaction("SPAYLATER*SHOPEE", "DEBT_PAYMENT"),
        new LabeledTransaction("SALARY DEC 2025", "INCOME"),
        new LabeledTransaction("IBG TRANSFER", "TRANSFER")
    );
    
    @Test
    void shouldAchieve85PercentAccuracy() {
        // Given
        int correct = 0;
        int total = TEST_DATA.size();
        
        // When
        for (LabeledTransaction labeled : TEST_DATA) {
            CategoryResult result = categorizerAgent.categorize(
                RawTransaction.builder()
                    .description(labeled.description())
                    .amount(BigDecimal.valueOf(100))
                    .build()
            );
            
            if (result.getCategory().equals(labeled.expectedCategory())) {
                correct++;
            }
        }
        
        // Then
        double accuracy = (double) correct / total;
        assertThat(accuracy).isGreaterThanOrEqualTo(0.85);
    }
}
```

---

## 6. Performance Testing

### 6.1 Load Testing Script

```java
// PerformanceTest.java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class PerformanceTest {
    
    @LocalServerPort
    private int port;
    
    @Test
    void shouldHandleTransactionListUnder500ms() {
        // Given
        RestTemplate restTemplate = new RestTemplate();
        String url = "http://localhost:" + port + "/api/v1/transactions?page=1&limit=50";
        
        // When
        long startTime = System.currentTimeMillis();
        ResponseEntity<String> response = restTemplate.exchange(
            url,
            HttpMethod.GET,
            createAuthenticatedRequest(),
            String.class
        );
        long duration = System.currentTimeMillis() - startTime;
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(duration).isLessThan(500);
    }
    
    @Test
    void shouldProcessUploadUnder30Seconds() {
        // Given - File with 500 transactions
        byte[] fileContent = loadTestFile("large-transactions.csv");
        
        // When
        long startTime = System.currentTimeMillis();
        ResponseEntity<String> response = uploadFile(fileContent);
        long duration = System.currentTimeMillis() - startTime;
        
        // Then
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(duration).isLessThan(30000);
    }
}
```

---

## 7. Security Testing

### 7.1 Security Test Checklist

```java
// SecurityTest.java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class SecurityTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void shouldRejectRequestWithoutAuth() throws Exception {
        mockMvc.perform(get("/api/v1/transactions"))
            .andExpect(status().isUnauthorized());
    }
    
    @Test
    void shouldRejectInvalidToken() throws Exception {
        mockMvc.perform(get("/api/v1/transactions")
                .header("Authorization", "Bearer invalid-token"))
            .andExpect(status().isUnauthorized());
    }
    
    @Test
    void shouldPreventSQLInjection() throws Exception {
        mockMvc.perform(get("/api/v1/transactions")
                .param("search", "'; DROP TABLE transactions; --"))
            .andExpect(status().isOk()); // Should return results, not error
    }
    
    @Test
    void shouldPreventXSSInUserInput() throws Exception {
        mockMvc.perform(put("/api/v1/transactions/{id}/comment", "uuid")
                .content("{\"comment\": \"<script>alert('xss')</script>\"}")
                .contentType(MediaType.APPLICATION_JSON))
            .andExpect(jsonPath("$.data.comment").value(
                not(containsString("<script>"))
            ));
    }
    
    @Test
    void shouldEnforceUserDataIsolation() throws Exception {
        // User A should not see User B's transactions
        // This requires setting up two test users
    }
    
    @Test
    void shouldRateLimitRequests() throws Exception {
        // Make 101 requests rapidly
        for (int i = 0; i < 101; i++) {
            mockMvc.perform(get("/api/v1/transactions"));
        }
        
        // 101st request should be rate limited
        mockMvc.perform(get("/api/v1/transactions"))
            .andExpect(status().isTooManyRequests());
    }
}
```

---

## 8. Test Data Management

### 8.1 Test Data Files

```
test/resources/
├── transactions/
│   ├── rhb-sample.csv           # Sample RHB format
│   ├── maybank-sample.csv       # Sample Maybank format
│   ├── tng-sample.csv           # Sample Touch & Go format
│   ├── aeon-sample.csv          # Sample Aeon Bank format
│   └── large-transactions.csv   # 500+ transactions for load testing
├── debts/
│   ├── hutang-sample.json       # Sample hutang data
│   └── bnpl-patterns.json       # Known BNPL patterns
└── expected/
    ├── categorization-expected.json  # Expected category results
    └── patterns-expected.json        # Expected pattern detection
```

### 8.2 Test Data Factory

```java
// TestDataFactory.java
public class TestDataFactory {
    
    public static User createTestUser() {
        return User.builder()
            .id(UUID.randomUUID())
            .clerkId("test_" + UUID.randomUUID())
            .email("test@example.com")
            .name("Test User")
            .monthlyIncome(BigDecimal.valueOf(4500))
            .build();
    }
    
    public static Transaction createTransaction(User user, String category, double amount) {
        return Transaction.builder()
            .id(UUID.randomUUID())
            .userId(user.getId())
            .transactionDate(LocalDate.now())
            .amount(BigDecimal.valueOf(amount))
            .description("Test Transaction")
            .category(category)
            .categoryConfidence(BigDecimal.valueOf(0.95))
            .build();
    }
    
    public static Debt createHutang(User user, String personName, double amount) {
        return Debt.builder()
            .id(UUID.randomUUID())
            .userId(user.getId())
            .debtTier("HUTANG")
            .debtName("Hutang to " + personName)
            .personName(personName)
            .direction("OWE")
            .currentBalance(BigDecimal.valueOf(amount))
            .status("active")
            .build();
    }
}
```

---

**Document End**

*Next Document: 08_DEPLOYMENT_GUIDE.md*
