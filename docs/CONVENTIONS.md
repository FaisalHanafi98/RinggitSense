# RinggitSense — Conventions

**Document type**: Engineering convention (authoritative)
**Scope**: Amount sign convention, transaction types, storage rules
**Established**: M0.3 (2026-07-04)
**Source of truth**: this document supersedes all inline comments and ad-hoc
references for the conventions it covers.

---

## 1. Amount Sign Convention

RinggitSense stores transaction amounts using a **signed** convention:

| Transaction type | Direction | Stored sign | Example |
|---|---|---|---|
| Debit (expense) | money out | **positive** | `RM 50.00` → `+50.00` |
| Credit (income) | money in | **negative** | `RM 5000.00` → `-5000.00` |

### Canonical reference

- **Parser layer**: `ParsedTransaction.signed_amount` in
  `backend/src/parsers/base.py:29-33` — returns `-amount` for credits,
  `+amount` for debits. This is the single point where the sign is applied.
- **Storage layer**: `Transaction.amount` in
  `backend/src/models/transaction.py:34` — stores the signed value as
  `Numeric(12, 2)`. The upload endpoint writes `txn.signed_amount` to this
  column (`backend/src/routers/transactions.py:225`).
- **API layer**: `TransactionResponse.amount` in
  `backend/src/schemas/transaction.py:21` — serializes the stored value
  unchanged (no sign flipping). Consumers receive the signed value.

### Why signed storage?

1. **SQL aggregations are correct without conditional logic**:
   `SUM(amount)` yields net cash flow directly (income reduces the total,
   spending increases it). An unsigned convention would require
   `SUM(CASE WHEN type = 'credit' THEN -amount ELSE amount END)` everywhere.
2. **One column, one truth**: the sign encodes direction; no separate
   `transaction_type` column is needed for financial calculations.
3. **Consistent with the parser contract**: the parser produces
   `signed_amount` as the canonical value; storage and API preserve it.

### Defects related to this convention

| Defect | Status | Fix module |
|---|---|---|
| **B1** — Dashboard treats positive as income (inverted) | Confirmed | M1.1 |
| **B2** — Dedup compares signed DB amount vs unsigned parser amount | Confirmed | M1.2 |

Both defects exist because parts of the codebase were written assuming an
unsigned convention. M1.1 and M1.2 reconcile them to this document.

### Rule for new code

Every component that reads, writes, or displays `Transaction.amount` MUST
treat the value as signed per this convention. New code must never assume
unsigned amounts. If a display layer needs to show `RM 50.00` for a
`-50.00` income row, it flips the sign at the presentation boundary only
and never writes the flipped value back.

---

## 2. Transaction Type

`ParsedTransaction.transaction_type` (`TransactionType` enum in
`backend/src/parsers/base.py:11-14`):

- `DEBIT` — expense / money out
- `CREDIT` — income / money in

The type is determined by the parser from the source statement's columns
(Debit/Credit columns in CSV). It is NOT stored as a separate column on
`Transaction` — the sign of `amount` encodes it implicitly. Code that
needs to distinguish type should check `amount < 0` (credit) or
`amount > 0` (debit).

---

## 3. Pipeline Stage Naming

The pipeline has 6 stages defined in `backend/src/services/pipeline.py:26-33`:

| Stage | Agent | Status |
|---|---|---|
| AG-01 | categorizer | Implemented |
| AG-02 | debt_detector | Implemented |
| AG-03 | pattern_analyzer | Implemented |
| AG-04 | predictor | Implemented |
| AG-05 | query | Stub (returns "skipped") |
| AG-06 | advisor | Stub (returns "skipped") |

`PipelineRun.total_stages` is always 6. `stages_completed` increments after
each stage. `stage_results` is a JSON blob with per-stage results. The
`total_stages=6` presentation is honest — skipped stages are recorded as
`{"status": "skipped", "reason": "..."}`.

---

## 4. Deduplication (current state — B2 documented)

The current dedup algorithm compares parsed transactions against existing
DB rows by date + amount + description. Defect B2 (fix: M1.2) causes
credits to be re-stored on re-upload because the comparison mixes signed
and unsigned amounts. The hash-based replacement lands in M5.4 (after
M6.1 extracts the service). Until M1.2, re-uploading the same statement
will duplicate income rows — this is a known defect, not a convention.

---

## 5. Malaysian-First Rules (from constitution)

- **Currency**: RM (Malaysian Ringgit), stored as `Numeric(12, 2)`.
- **Banks**: Maybank, CIMB (implemented); RHB, Public Bank, Hong Leong,
  Aeon (planned).
- **E-wallets**: Touch 'n Go, GrabPay, ShopeePay, Boost, BigPay (planned).
- **Debt tiers**: FORMAL (PTPTN, bank loans), BNPL (SPayLater, GrabPayLater,
  Atome, Split, Hoolah), HUTANG (informal person-to-person).
- **Mandatory disclaimers** on all advice: "This is not professional
  financial advice", "Consult a licensed financial advisor for major
  decisions", "Past patterns do not guarantee future results".
- **Anti-hallucination**: all agent outputs include confidence scores
  (0.0–1.0); every claim traces to input data.
