Golden Dataset — Synthetic Malaysian Bank Statements

Covers all 10 transaction categories, 3 debt tiers, and common edge cases.
Spans 3 months (Jan-Mar 2026) for pattern analysis.

## Files

| File | Purpose |
|------|---------|
| `maybank_golden.csv` | Synthetic Maybank statement (~99 transactions) |
| `cimb_golden.csv` | Synthetic CIMB statement (~59 transactions) |
| `expected_categories.json` | AG-01 expected categorization per transaction |
| `expected_debts.json` | AG-02 expected debt detection (tiers, groups, indicators) |
| `expected_patterns.json` | AG-03 expected pattern analysis (recurring, trends, anomalies) |
| `generate_golden_dataset.py` | Script to regenerate all fixtures |

## Regeneration

```bash
cd backend
python tests/fixtures/golden/generate_golden_dataset.py
```

## Category coverage (10/10)
- FOOD: McDonald's, Nasi Kandar, Jaya Grocer, Grab Food, mamak, KFC, Domino's, Starbucks, Tealive
- TRANSPORT: PLUS/DUKE/LDP/SMART/KESAS/MEX/NPE/AKLEH tolls, Petronas/Shell, Grab Car, MRT topup, parking
- BILLS: TNB, Unifi, Celcom, Maxis, Astro, Syabas, Netflix, Spotify, Apple Music
- ENTERTAINMENT: GSC/TGV cinema, Steam, PlayStation Store
- SHOPPING: Shopee, Lazada, Zara, Uniqlo, H&M, Mr DIY, Watson's
- TRANSFER: Transfer to/from persons, TnG/Boost/BigPay topup, Tabung Haji
- DEBT_PAYMENT: PTPTN, personal loans, hire purchase, housing loan, credit card, ASB financing, BNPL
- INCOME: Salary, bonus, refunds, cashback, salary advance
- HEALTHCARE: Guardian/Watsons pharmacy, clinics, KPJ/Gleneagles hospital, insurance
- OTHER: Kedai runcit, barber, special characters

## Debt tier coverage (3/3)
- FORMAL: PTPTN, Maybank personal loan, hire purchase, CIMB housing loan, Aeon credit card, ASB financing
- BNPL: SPayLater, GrabPayLater, Atome, Hoolah, Split
- HUTANG: Pinjam duit Ahmad, hutang Siti, bayar balik, bayar hutang Kamal

## Edge cases
- Credits (salary, refund, cashback, transfer-in, bonus)
- Small amounts (RM1.20 toll, RM5.60 kedai runcit)
- Large amounts (RM1200 housing loan, RM850 hire purchase)
- CIMB header rows (bank name, statement period, account number)
- Multiple transactions same day
- 3-month span for recurring pattern detection
- Special characters in descriptions
- Installment notation (2/3, 3/6, 1/4)
