# Refactor Baseline & Working Agreements (M0.1)

**Program**: Audit remediation & production-readiness refactor
**Module**: M0.1 — Baseline freeze & working agreements
**Date frozen**: 2026-07-04
**Git tag**: `pre-refactor-baseline` → commit `c83e2c6`
**Roadmap**: [refactor-execution-plan.md](refactor-execution-plan.md)

Reverting the entire program = `git checkout pre-refactor-baseline`. Every module
is additionally revertible on its own because each one lands as a single merge.

---

## 1. Baseline Evidence

Captured locally on 2026-07-04 against commit `c83e2c6`:

| Check | Result | Command |
|---|---|---|
| Backend tests | **263 passed**, 1 warning, ~22s | `pytest tests/ -q` (backend venv) |
| Coverage | **90.42%** (floor configured at 80%) | `pytest --cov=src` |
| Lint | **Clean** — "All checks passed!" | `ruff check .` (backend) |
| Types (local) | **BROKEN ENVIRONMENT** — mypy exits 1 with no output, even on `--version` | `mypy src/` |
| Types (CI) | Green as of `d14c030` "chore(ci): fix backend lint and typing gates" | GitHub Actions, Python 3.11 |
| Frontend | **No gates exist** — no tests, no CI job (lint/typecheck/build unenforced) | — |

### Environment notes (pre-existing, not introduced by this program)

- Local venv runs **Python 3.14.6**; CI and Dockerfile pin **3.11**. The local mypy
  breakage is almost certainly this drift. CI is the authoritative mypy gate until
  **M2.3** (dependency & runtime pinning) recreates the venv on 3.11.
- Frontend verification is manual-only until **M7.1** adds Vitest + a frontend CI job
  (M1.1 bootstraps a minimal Vitest earlier).

### Coverage rule

Program-wide: backend coverage never drops below **90.42%** (the baseline), which is
stricter than the configured 80% floor. Any module that lowers it fails its gate.

---

## 2. Known-Defect Register

These four defects are **confirmed present at the baseline**. They exist so that no
new test is ever written to assert (and thereby enshrine) the current broken
behavior. M0.3's E2E tests mark B2-related assertions `xfail` referencing this
register; they flip to passing when the fix module lands.

| ID | Defect | Location | Root cause | Fix module |
|---|---|---|---|---|
| **B1** | Dashboard income/spending inverted | `frontend/src/hooks/useTransactions.ts:19-21` | `computeMetrics` treats positive amounts as income; backend stores debit (expense) = positive, credit (income) = negative per `backend/src/parsers/base.py:29-33` | M1.1 |
| **B2** | Duplicate detection broken for credits | `backend/src/routers/transactions.py:152-160` + `backend/src/data_quality/transaction_validator.py:193-194` | Existing DB rows are compared using their **signed** stored amount (negative for income) against the parser's **unsigned** amount, with `transaction_type` hardcoded to `DEBIT`; re-uploads duplicate every income row | M1.2 |
| **B3** | False "processed locally" compliance claim | `frontend/src/components/dashboard/FinancialDisclaimer.tsx:8` | Copy asserts local processing; data is processed on the backend and by Anthropic's API. PDPA-relevant misstatement | M1.3 |
| **B4** | Dashboard metrics silently limited to newest 200 transactions | `frontend/src/pages/DashboardPage.tsx:10` | Metrics/charts computed client-side over one `limit: 200` page | M1.1 (interim label) → M7.3 (server aggregates) |

**Sign convention (authoritative until `docs/CONVENTIONS.md` exists, M0.3):**
debit/expense is stored **positive**; credit/income is stored **negative**
(`ParsedTransaction.signed_amount`, `backend/src/parsers/base.py:29-33`). The API
serializes the stored value unchanged.

---

## 3. Working Agreements

1. **One module = one branch = one merge to `dev`.** Branch naming:
   `refactor/m<id>-<slug>`. Flow per module:
   branch off `dev` → implement → gates → merge to `dev` → **stop and report**
   → approval → next module. No module starts before its predecessor is merged
   and approved. `dev` → `main` promotion happens at integration checkpoints
   (§12 of the execution plan) or on owner demand. `main` is deployment-connected
   and only receives promoted, fully-gated state.
2. **Gates before merge** (tiers defined in the roadmap §Test Strategy):
   lint → types (CI authoritative until M2.3) → build → unit → integration (once
   M0.2 exists) → coverage ≥ 90.42% → perf evidence for T3 modules → docs updated →
   review/approval.
3. **Scope is the module card.** Anything discovered mid-module is recorded as a
   GitHub issue labeled `deferred-from-refactor` (Decision #4) — never implemented
   inline.
4. **At most one High-risk module in flight at any time** (M3.1, M4.4, M6.3 never
   overlap — trivially satisfied by rule 1, kept explicit in case of future
   parallelism).
5. **RinggitSense is a PDPA project**: no auto-commits; every merge is explicitly
   confirmed by the owner (per repository SOP §13.3).
6. **Existing test assertions are never modified silently.** Changing one requires a
   PR note referencing this register or the module card that authorizes the change.
7. **Temporary artifacts carry removal tickets from birth**: M1.1 window label,
   M4.4 `JOB_BACKEND` dual path, M7.3 client-side fallback.
8. **Recommended manual step (owner)**: enable branch protection on `main` in GitHub
   settings (require PR + green checks). Not scriptable from this repo; noted here
   so it isn't lost.

---

## 4. Decision Log

Approved by owner on 2026-07-03/04:

| # | Decision | Outcome | Consumed by |
|---|---|---|---|
| D1 | Fate of orphan tables | **Approved as recommended**: persist `debts`+`debt_items`, `patterns`, `predictions`; defer `advice` (until AG-06 exists) and `audit_logs` (own future initiative). M5.1 writes ADR-004 recording this — the decision itself is already made | M5.1, M5.2, M5.3 |
| D2 | Job backend | **arq** (async-native, minimal ceremony; Redis already planned). ADR-005 written inside M4.4 | M4.4 |
| D3 | Lock tooling | **uv** | M2.3 |
| D4 | Live tracker | **GitHub issues** adopted; static task registry retired as historical | M9.2, change control |
| D5 | Nightly accuracy budget | **Approved** (~USD 15–30/mo ceiling) | M8.1 |

---

## 5. Program Constraints

### C1 — Docker is OFF-LIMITS locally (owner constraint, 2026-07-04)

The owner currently has local Docker issues. Until lifted, **no module may require
local Docker**, and `docker-compose.yml` / `Dockerfile` are not modified or relied on
for verification. GitHub Actions service containers run on GitHub-hosted runners
(not the owner's machine) and remain available.

Impact on planned modules:

| Module | Adjustment |
|---|---|
| M0.2 | Integration tests are **CI-first**: they run against the Actions Postgres service; locally they auto-skip when `TEST_DATABASE_URL` is unset/unreachable. Local runs are optional (native Postgres install would enable them), never required |
| M2.2 | "Fresh clone boots API" acceptance stands — the app boots without a DB (lazy engine); DB-dependent steps verified in CI |
| M2.3 | Docker image build drops out of the module gate; CI-green from lock file is the gate. Image build re-verified when C1 lifts |
| M4.4 | Worker runs as a plain process (`arq` CLI). Compose service definition deferred until C1 lifts. Local Redis strategy decided at Wave 3 (options: CI-only verification, native Redis/Memurai, or fakeredis for tests) |
| M10.x | Horizon epic already deferred; container hardening (M10.3) blocked on C1 |

### C2 — One PR = one module (owner directive, 2026-07-04)

Already agreement #1 above; recorded as an explicit owner directive.

---

## 6. Module Progress Ledger

Updated as each module merges. Status: ☐ pending · ◐ in progress · ☑ merged.

| Module | Status | Merged | Notes |
|---|---|---|---|
| M0.1 Baseline freeze & working agreements | ☑ | 2026-07-04 | this document |
| M0.2 Integration test harness | ☐ | — | CI-first per C1 |
| M0.3 E2E pipeline + sign-contract tests | ☐ | — | |
| M9.1 Live-doc truth pass | ☐ | — | parallel-eligible |
| M5.1 ADR-004 (decision pre-approved, D1) | ☐ | — | parallel-eligible |
| M1.3 Compliance copy correction | ☐ | — | parallel-eligible |
| M2.2 Onboarding truth | ☐ | — | parallel-eligible |
| M1.1 Dashboard metrics correctness | ☐ | — | |
| M1.2 Credit-safe deduplication | ☐ | — | |
| M2.1 Config single-source | ☐ | — | |
| M2.3 Dependency & runtime pinning (uv, D3) | ☐ | — | fixes local mypy |
| M2.4 Structured logging baseline | ☐ | — | |
| M3.1 Async client, timeouts, retries | ☐ | — | High risk — solo |
| M3.2 Batch execution & stage hygiene | ☐ | — | |
| M3.3 AG-03/04 input windowing | ☐ | — | |
| M3.4 Merchant category cache | ☐ | — | optional |
| M4.1 Stale-run recovery | ☐ | — | |
| M4.2 DB-level active-run uniqueness | ☐ | — | |
| M4.3 Pipeline spend quota | ☐ | — | |
| M4.4 Worker backend, arq (D2) | ☐ | — | High risk — solo; C1 applies |
| M5.2 Debt persistence | ☐ | — | |
| M5.3 Pattern & prediction persistence | ☐ | — | |
| M5.5 Composite index | ☐ | — | |
| M6.1 TransactionService extraction | ☐ | — | before M5.4 |
| M5.4 Hash-based deduplication | ☐ | — | after M6.1 |
| M6.2 Dead scaffolding removal | ☐ | — | |
| M6.3 JWKS lifecycle hardening | ☐ | — | High risk — solo |
| M6.4 Request rate limiting | ☐ | — | |
| M6.5 Server-side aggregates endpoint | ☐ | — | |
| M7.1 Frontend test & CI infrastructure | ☐ | — | |
| M7.2 Pipeline status UI | ☐ | — | |
| M7.3 Dashboard on server aggregates | ☐ | — | retires B4 label |
| M8.1 Golden accuracy harness (D5) | ☐ | — | |
| M8.2 Accuracy as release gate | ☐ | — | |
| M9.2 Legacy archive & index regeneration (D4) | ☐ | — | |
| M9.3 ADR & prompt-library consolidation | ☐ | — | |
