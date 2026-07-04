# RinggitSense — EXECUTION PLAN v1
## Master Implementation Specification (Complete Context Externalisation)

**Document purpose**: This is the project's master implementation specification for
the audit-remediation & production-readiness refactor program. It is written so
that an engineer or AI model with ZERO access to any prior conversation can
continue execution using only the repository and this document.

**Version**: 1.0 · **Date**: 2026-07-04 · **Owner**: Faisal (repo owner)
**Supersedes nothing; consolidates**: `docs/plans/refactor-execution-plan.md`
(roadmap v1.1) and `docs/plans/refactor-baseline.md` (baseline & agreements).
Those two files remain authoritative for their sections; this document is the
single self-contained export. On conflict, the most recently edited of the three
wins and the others must be reconciled in the same commit.

**Companion live-state file**: `CURRENT_MODULE_STATE.md` (repo root) — overwrite
in place at every transition; it is the "where are we right now" pointer.

---

# 1. Executive Overview

RinggitSense is an AI-powered personal-finance tracker for Malaysian young
professionals (22–35). Users upload bank/e-wallet statements (CSV); a pipeline of
specialized Claude agents categorizes transactions, detects debt across three
Malaysian tiers (FORMAL / BNPL / HUTANG), discovers spending patterns, and
forecasts next-month spending.

A comprehensive Architecture Maturity & Scalability Audit (completed 2026-07-03)
found: a well-engineered vertical slice (263 tests, 90.42% coverage, typed, real
CI) wearing the documentation of a finished platform. Roughly a third of the
documented system was never built; the AI pipeline has a critical performance
defect (synchronous Claude calls inside the async event loop, one API call per
transaction); three confirmed cross-layer bugs prove the system was never
exercised end-to-end; six of ten database tables are never written to.

**Audit verdict**: refactor first (surgical, not a redesign), then continue
building. This program executes that refactor as ~39 independently testable
modules across 11 epics, one module per branch per merge, with a regression
safety net built before any behavior change.

**Current status at time of writing**: Module M0.1 (baseline freeze) is COMPLETE
and MERGED to `main` (merge commit `e689d92`). Module M0.2 is next, pending
owner go-ahead. No other module has been started. See §5.1 and
`CURRENT_MODULE_STATE.md`.

**Audit scorecard (baseline → target)**:

| Category | Baseline | Target |
|---|---|---|
| Architecture | 6/10 | 7+ |
| Performance | 3/10 | 7 |
| Scalability | 4/10 | 7 |
| Maintainability | 7/10 | 7+ |
| Documentation | 4/10 | 7 |
| Developer Experience | 6/10 | 7 |
| Deployment Readiness | 3/10 | 5 (E10 horizon) |
| Testing | 6/10 | 8 |
| Security | 6/10 | 7 |
| Code Quality | 7/10 | 8 |
| Configuration | 5/10 | 7 |
| Overall Technical Debt | 5/10 | 7.5 |

---

# 2. Engineering Objectives

1. **Correctness**: eliminate the four confirmed defects (B1–B4, §18.1) and the
   data-integrity risks around deduplication and sign conventions.
2. **Performance**: make the documented targets achievable — statement pipeline
   (100 transactions) < 30 s; API p95 < 500 ms; zero event-loop blocking.
3. **Durability**: background jobs survive restarts; no stuck states; bounded
   retries and timeouts on all external calls.
4. **Cost containment**: ~50× reduction in Claude API calls via batching;
   per-user spend quotas; category caching for recurring merchants.
5. **Data-model integrity**: agent outputs persisted to the normalized tables
   that already exist (per Decision D1), demoting JSON blobs to run-logs.
6. **Testability**: real integration tier on PostgreSQL; frontend test + CI
   gates; nightly agent-accuracy scoring against golden datasets.
7. **Documentation truth**: every live document verifiably matches the code;
   legacy artifacts archived, phantom references purged.
8. **NO new features** during the program (see §16 out-of-scope register).

---

# 3. Architectural Principles

1. **Layering preserved**: routers → services → agents → models, Pydantic
   contracts at every boundary. The audit found this sound; protect it.
2. **Services own data access** — the repository pattern is explicitly rejected
   (empty `src/repositories/` scaffolding is deleted in M6.2).
3. **Async end-to-end in the serving path**: no synchronous network I/O on the
   event loop, ever (root cause of audit finding P1).
4. **One code path**: temporary dual paths (e.g., M4.4's `JOB_BACKEND` flag) are
   allowed for exactly one release and carry a removal ticket from birth.
5. **Behavior-preserving refactors ship separately from behavior changes**
   (e.g., M6.1 extraction must precede M5.4 dedup redesign).
6. **DB-enforced invariants over in-memory checks** (unique indexes for
   dedup/active-run guards, not SELECT-then-INSERT).
7. **User-scoped multi-tenancy**: every query filters by `user_id` (already
   consistently enforced; must remain so).
8. **YAGNI**: no speculative abstractions; the constitution's Principle VII.
9. **Malaysian-first domain rules** (constitution): RM currency; banks Maybank/
   CIMB/RHB/Public/Hong Leong/Aeon; tri-tier debt FORMAL/BNPL/HUTANG; mandatory
   financial disclaimers; PDPA compliance; anti-hallucination protocol with
   confidence scores on all agent outputs.

---

# 4. Overall Refactoring Strategy

**Safety-net-first** (a deliberate deviation from the audit's tier order, which
put correctness first): Wave 0 builds integration/E2E tests BEFORE the bug fixes,
because all three shipped bugs live at boundaries no existing test crosses. Then
correctness, then performance, then durability, then data-model, then API/
frontend, then measurement, with documentation running in parallel throughout.

**Execution protocol per module (binding)**:
branch `refactor/m<id>-<slug>` → implement to the module card → pass quality
gates (§14) → merge to `main` (owner-confirmed) → **stop, report, await
approval** → next module. One PR = one module (Constraint C2). Scope is the
module card; discoveries become GitHub issues labeled `deferred-from-refactor`
(Decision D4) — never implemented inline.

**Calendar estimate** (solo dev): Waves 0–3 ≈ 3.5–4 weeks (core de-risk
milestone); Waves 4–6 ≈ 3–4 further weeks. E10 horizon excluded.

---

# 5. Complete Implementation Roadmap

## 5.1 Current execution status (2026-07-04)

- ✅ Audit complete (2026-07-03).
- ✅ Planning complete; roadmap committed.
- ✅ **M0.1 merged to `main`** (`e689d92`, --no-ff). Verified post-merge:
  263 tests pass, 90.42% coverage, ruff clean, worktree clean.
- ✅ Baseline tag `pre-refactor-baseline` → commit `c83e2c6`.
- ✅ Branch streamline done: only `main` exists. Two pre-existing WIP branches
  were deleted and preserved as deferred issues (see §16.3): AG-05 WIP commit
  `70226e6` (issue #1), deployment-config WIP commit `4f7b598` (issue #2).
  Recovery: `git cherry-pick <sha>`.
- ⏸️ `main` NOT yet pushed to `origin` (separate owner-confirmed action).
- ⬜ **Next module: M0.2** — do not start until the owner says go.
- ⬜ All other modules not started.

## 5.2 Wave plan

```
WAVE 0  Safety Net           M0.1✅ → M0.2 → M0.3          ║ parallel: M9.1, M5.1, M1.3, M2.2
WAVE 1  Correctness+Hygiene  M1.1, M1.2, M2.1, M2.3, M2.4  (small, independent, low risk)
WAVE 2  Agent Runtime        M3.1 → M3.2 → M3.3            ║ parallel: M9.2
WAVE 3  Job Durability       M4.1 → M4.2 → M4.3 → M4.4
WAVE 4  Data Layer           M5.2, M5.3 → M5.5 → [M6.1 → M5.4]  ║ parallel: M3.4 (optional)
WAVE 5  API & Frontend       M6.2, M6.3*, M6.4, M6.5 → M7.1 → M7.2, M7.3
WAVE 6  Quality & Closeout   M8.1 → M8.2 · M9.3 · retire M1.1 label & M4.4 flag
HORIZON Deployment           E10 (planned in detail only after Wave 4; partly blocked by C1)

*M6.3 (auth) runs solo — never concurrent with another High-risk module.
```

**Critical path**: M0.2 → M0.3 → M3.1 → M3.2 → M4.4 → M5.2/M5.3 → M6.5 → M7.3

## 5.3 How to read module cards

| Scale | Values |
|---|---|
| Complexity | **S** ≤ ½ day · **M** 1–2 days · **L** 3–5 days (solo-dev days) |
| Risk (implementation) | **Low** additive/isolated · **Med** modifies existing behavior · **High** touches auth, jobs, or runtime model |
| Regression risk | Likelihood of breaking behavior users/tests currently rely on |
| Test tier | **T1** static+unit · **T2** +integration · **T3** +performance evidence · **T4** +manual E2E (§13) |

---

# 6–7. Epics and Modules (complete — 39 modules across 11 epics)

## EPIC E0 — Regression Safety Net (3 modules)

*Rationale: all three shipped bugs live at boundaries no test crosses. Nothing
else starts until the net exists.*

### M0.1 — Baseline freeze & working agreements ✅ MERGED (e689d92)
- **Purpose**: freeze current behavior as reference; establish refactor discipline.
- **Delivered**: tag `pre-refactor-baseline` at `c83e2c6`;
  `docs/plans/refactor-baseline.md` (baseline evidence, defect register B1–B4,
  working agreements, decision log D1–D5, constraints C1/C2, module ledger);
  `docs/plans/refactor-execution-plan.md`; `CURRENT_MODULE_STATE.md`.
- **Files**: docs + git tag only. Zero source/test/config touched.
- **Depends**: — | **Risk**: Low | **Complexity**: S | **Regression risk**: none
- **Acceptance (MET)**: tag exists; register lists B1–B4 with file:line; PR
  discipline documented.
- **Validation performed**: pytest 263 passed / 90.42% coverage; ruff clean;
  re-verified identical on `main` post-merge.
- **Rollback**: n/a (additive). Program-wide rollback = checkout the tag.

### M0.2 — Integration test harness on real PostgreSQL  ⬅ NEXT MODULE
- **Purpose**: make the DB boundary testable. CI already provisions a Postgres
  service (`.github/workflows/ci.yml`) that no test uses.
- **Scope**: pytest fixtures creating/dropping schema per session against
  `TEST_DATABASE_URL`; FastAPI dependency-override replacing `get_current_user`
  (`backend/src/auth.py:124`) with test-user injection; async `httpx` client
  fixture bound to the app; `integration` pytest marker; CI step runs the marker.
  **Constraint C1**: CI-first — locally the marker auto-skips when
  `TEST_DATABASE_URL` is unset/unreachable; local runs optional, never required.
- **Files**: `backend/tests/conftest.py`, new `backend/tests/integration/`,
  `backend/pyproject.toml` (marker), `.github/workflows/ci.yml`
- **Depends**: M0.1 | **Risk**: Low (additive) | **Complexity**: M |
  **Regression risk**: Low (touches conftest only)
- **Acceptance**: trivial round-trip (create user → insert transaction → list via
  `GET /api/v1/transactions`) green in CI; unit suite unaffected; local run
  without a DB skips cleanly.
- **Testing**: T2. **Rollback**: delete new files; revert conftest.
- **Gains**: unlocks safe execution of E1, E3–E6.

### M0.3 — E2E pipeline test + amount-sign contract tests
- **Purpose**: one executable spec of upload→pipeline→DB→API, and of the sign
  convention behind defects B1/B2.
- **Scope**: test uploads `backend/tests/fixtures/golden/maybank_golden.csv`
  (Claude mocked) → assert stored rows, categories written, `pipeline_runs`
  status transitions, API list output. Contract test: credits serialize
  negative, debits positive (per `ParsedTransaction.signed_amount`,
  `backend/src/parsers/base.py:29-33`). Write `docs/CONVENTIONS.md` documenting
  the sign convention as the single source of truth. **B2-related assertions are
  marked `xfail` referencing the defect register** — they flip to passing in
  M1.2. Never write a test asserting current broken behavior.
- **Files**: `backend/tests/integration/test_upload_pipeline_e2e.py`,
  `backend/tests/integration/test_amount_contract.py`, `docs/CONVENTIONS.md`
- **Depends**: M0.2 | **Risk**: Low | **Complexity**: M | **Regression risk**: none
- **Acceptance**: E2E green with today's behavior (registered `xfail`s aside);
  convention doc reviewed.
- **Testing**: T2. **Rollback**: delete files.
- **Gains**: the regression net for E3, E4, E5, E6 — highest-leverage artifact
  in the program.

## EPIC E1 — Correctness Hotfixes (3 modules)

### M1.1 — Dashboard metrics correctness (sign fix + window honesty)
- **Purpose**: fix B1 (inverted income/spending); neutralize B4 (silent 200-row
  window) pending the real fix in M7.3.
- **Scope**: correct `computeMetrics`/`groupByMonth` in
  `frontend/src/hooks/useTransactions.ts` to the documented convention
  (negative = income); add a "based on latest 200 transactions" label to the
  dashboard until M7.3 (removal ticket at creation); bootstrap **minimal
  Vitest** (config + these unit tests only — full frontend infra is M7.1) so the
  module is independently testable.
- **Files**: `frontend/src/hooks/useTransactions.ts`,
  `frontend/src/pages/DashboardPage.tsx`, `frontend/package.json`,
  new `frontend/src/hooks/useTransactions.test.ts`
- **Depends**: M0.3 (convention doc) | **Risk**: Low | **Complexity**: M |
  **Regression risk**: Med — every dashboard number changes; that is the
  intended outcome
- **Acceptance**: unit tests encode the convention (credit → income); manual
  golden-data check shows salary under Income; window label visible.
- **Testing**: T2 + manual. **Rollback**: revert commit (3 files).
- **Gains**: correct headline numbers; first frontend tests in the repo.

### M1.2 — Credit-safe deduplication
- **Purpose**: fix B2 — re-uploads must not duplicate income rows.
- **Scope**: normalize the comparison in the upload dedup path
  (`backend/src/routers/transactions.py:152-160` builds existing rows with the
  DB's **signed** amount and hardcoded `TransactionType.DEBIT`, compared against
  the parser's **unsigned** amount in
  `backend/src/data_quality/transaction_validator.py:193-194`). Compare signed
  vs signed, or reconstruct type from the stored sign. Flip M0.3's `xfail`s to
  passing. **No dedup redesign** — the hash-based replacement is M5.4; this
  module only makes today's algorithm correct.
- **Files**: `backend/src/routers/transactions.py`, possibly
  `backend/src/data_quality/transaction_validator.py`
- **Depends**: M0.3 | **Risk**: Low | **Complexity**: S–M | **Regression risk**:
  Med — dedup verdicts change for credits (intended); SUSPICIOUS
  classifications may shift
- **Acceptance**: E2E: golden CSV uploaded twice → second upload stores 0 rows,
  reports all as duplicates including salary/bonus rows.
- **Testing**: T2. **Rollback**: revert; `xfail` markers restored.
- **Gains**: data integrity — top PDPA-adjacent correctness risk closed.

### M1.3 — Compliance copy correction
- **Purpose**: fix B3 — remove the false "processed locally" claim.
- **Scope**: reword `frontend/src/components/dashboard/FinancialDisclaimer.tsx:8`
  (data processed on RinggitSense servers; AI analysis via Anthropic's API;
  PDPA notice); repo-wide grep for other local-only claims; one matching README
  line. The constitution's three mandatory disclaimer sentences must remain
  ("This is not professional financial advice", "Consult a licensed financial
  advisor for major decisions", "Past patterns do not guarantee future results").
- **Files**: `frontend/src/components/dashboard/FinancialDisclaimer.tsx`,
  `README.md`
- **Depends**: — (parallel-eligible in Wave 0) | **Risk**: Low |
  **Complexity**: S | **Regression risk**: none (copy only)
- **Acceptance**: no source or doc claims local-only processing.
- **Testing**: T1 + docs verification. **Rollback**: revert.
- **Gains**: compliance exposure closed.

## EPIC E2 — Configuration & Environment Hygiene (4 modules)

### M2.1 — Config single-source
- **Purpose**: kill config drift — `backend/src/config.py:46-47` claims
  PDF+CSV / 10 MB while `backend/src/routers/transactions.py:34-44` hardcodes
  CSV-only / 10 MB; the settings version is dead code.
- **Scope**: router reads `settings.MAX_UPLOAD_SIZE_MB` /
  `settings.ALLOWED_EXTENSIONS`; settings set to actual capability (`["csv"]` —
  PDF parsing is a stub); module-level constants deleted.
- **Files**: `backend/src/config.py`, `backend/src/routers/transactions.py`
- **Depends**: M0.2 | **Risk**: Low | **Complexity**: S | **Regression risk**:
  Low (behavior preserved by design; upload tests prove it)
- **Acceptance**: one definition (grep); upload tests unchanged and green.
- **Testing**: T2. **Rollback**: revert.

### M2.2 — Onboarding truth (`.env.example` + README)
- **Purpose**: a developer following the docs must get a working setup. Today
  `.env.example` contains removed JWT keys (`ACCESS_TOKEN_EXPIRE_MINUTES`,
  `REFRESH_TOKEN_EXPIRE_DAYS`) and is missing required `CLERK_DOMAIN`.
- **Scope**: add `CLERK_DOMAIN`, `CLERK_JWT_AUDIENCE`, `CLAUDE_MODEL`; remove
  dead JWT keys; README quick-start gains Clerk prerequisite + honest status
  line. **C1**: the app boots without a DB (lazy engine, `/health` touches no
  DB), so the local boot check stands; DB-dependent steps verified in CI.
- **Files**: `backend/.env.example`, `README.md`
- **Depends**: — (parallel-eligible in Wave 0) | **Risk**: Low |
  **Complexity**: S | **Regression risk**: none
- **Acceptance**: fresh clone + example-following boots the API (manual).
- **Testing**: T4-lite (manual boot). **Rollback**: revert.

### M2.3 — Dependency & runtime pinning (tooling: uv — Decision D3)
- **Purpose**: reproducible builds; end the Python 3.14-local / 3.11-CI drift;
  **restore local mypy** (broken at baseline: exits 1 with no output, even on
  `--version` — a 3.14 incompatibility, not a code defect).
- **Scope**: uv lock file; `pytest`/`anyio` move to dev deps; verify
  `psycopg2-binary` necessity (drop if alembic env is async; document if kept);
  recreate venv on Python 3.11; CI installs from the lock. **C1**: no Docker
  image build in the gate — CI-green from the lock is the gate; image build
  re-verified when C1 lifts.
- **Files**: `backend/requirements*.txt` → `requirements.in`/lock (or
  pyproject-managed), `.github/workflows/ci.yml`, `backend/pyproject.toml`
- **Depends**: M0.2 | **Risk**: Low–Med (dependency resolution surprises) |
  **Complexity**: M | **Regression risk**: Low — full suite is the gate
- **Acceptance**: CI green from lock; `pip check` clean; local `mypy src/` works
  again on the 3.11 venv.
- **Testing**: T2 + build verification (CI). **Rollback**: restore old
  requirements files (kept until module accepted).

### M2.4 — Structured logging baseline
- **Purpose**: replace `print()` (in `backend/src/main.py` lifespan) and ad-hoc
  logging before E4 needs real logs.
- **Scope**: stdlib logging config (optional JSON formatter flag), uvicorn
  integration, level from settings.
- **Files**: `backend/src/main.py`, `backend/src/config.py`, new
  `backend/src/logging_config.py`
- **Depends**: — | **Risk**: Low | **Complexity**: S–M | **Regression risk**: Low
- **Acceptance**: startup/shutdown + one request path emit structured records;
  no `print` in `src/`.
- **Testing**: T1 + manual log inspection. **Rollback**: revert.

## EPIC E3 — Agent Runtime Modernisation (4 modules)

*Sequential within the epic — each module rewrites what the previous stabilized.
Highest performance value in the program.*

### M3.1 — Async client, timeouts, retries, call-level concurrency  [HIGH RISK — runs solo]
- **Purpose**: fix audit P1/P3. `BaseAgent` uses the synchronous
  `anthropic.Anthropic` client (`backend/src/agents/base.py:28`) called directly
  inside `async def` pipeline functions — every Claude call freezes the entire
  event loop; one upload makes the whole API unresponsive. No timeout, no retry;
  the `asyncio.Semaphore(3)` wraps whole stages
  (`backend/src/services/pipeline.py:106`) and, with sync calls, limits nothing.
- **Scope**: `AsyncAnthropic`; `invoke`/`invoke_batch` become async; explicit
  client timeout; bounded exponential-backoff retry on retryable errors;
  semaphore moves to around individual API calls; size into settings.
  Mechanical update of all mocked agent tests. Output schemas unchanged.
- **Files**: `backend/src/agents/base.py`, `agents/categorizer.py`,
  `agents/debt_detector.py`, `agents/pattern_analyzer.py`,
  `agents/predictor.py`, `services/pipeline.py` call sites, `config.py`, tests:
  `test_categorizer.py`, `test_debt_detector.py`, `test_pattern_analyzer.py`,
  `test_predictor.py`, `test_pipeline.py`
- **Depends**: M0.3 | **Risk**: **High** | **Complexity**: L |
  **Regression risk**: Med — mitigated by the E2E net + unchanged schemas
- **Acceptance**: E2E green; **performance evidence**: `/health` p95 < 100 ms
  while a pipeline runs (scripted check — the P1 proof); a simulated hung call
  times out and fails the stage, not the server.
- **Testing**: T3. **Rollback**: revert branch — no schema/data changes.
- **Gains**: server no longer freezes during pipelines (audit's #1 defect).

### M3.2 — Batch execution & stage hygiene
- **Purpose**: fix audit P2 — the pipeline loops `agent.categorize()` /
  `agent.detect()` once per transaction
  (`backend/src/services/pipeline.py:182-196` and `:281-296`) while implemented
  `categorize_batch`/`detect_batch` (≤50/call) sit unused: a 100-txn statement
  costs ~200 sequential calls (~3–7 min) vs the documented <30 s. Plus three
  findings living in the same two functions: unwired `AgentOutputValidator`
  (`backend/src/data_quality/agent_output_validator.py` — tested, used nowhere),
  hardcoded `is_recurring=False`, and PII-bearing exception strings stored into
  `stage_results` JSON.
- **Scope**: `_run_categorizer`/`_run_debt_detector` use the batch methods
  chunked ≤50 with id-mapped result application; unmatched ids → per-item
  errors; error entries carry error codes + transaction ids, never raw
  descriptions; wire `AgentOutputValidator` at stage boundaries; pass real
  `is_recurring`/`user_comment` from the model. **One module deliberately**: all
  four changes rewrite the same ~80 lines; splitting guarantees merge churn
  without isolating risk. `stage_results` shape stays backward-compatible.
- **Files**: `backend/src/services/pipeline.py`, minor: `agents/categorizer.py`,
  `agents/debt_detector.py`, `data_quality/agent_output_validator.py`,
  `tests/test_pipeline.py`
- **Depends**: M3.1 | **Risk**: Med | **Complexity**: L | **Regression risk**:
  Med (E2E asserts result shape)
- **Acceptance**: E2E green; call-count assertion: 100-txn statement ⇒ ≤4
  categorizer + ≤4 debt-detector calls (was ~200); no description text in any
  `stage_results` error; perf evidence: mocked-latency simulation inside the
  <30 s envelope.
- **Testing**: T3. **Rollback**: revert (single code path — never keep the
  per-row path live alongside).
- **Gains**: ~50× latency & major token-cost reduction (restores the cost model
  in `docs/adr/ADR-001-cost-optimization.md`); PDPA hygiene in stored blobs.

### M3.3 — AG-03/AG-04 input windowing
- **Purpose**: fix audit P5 — AG-03 receives the entire transaction history in
  one prompt (`backend/src/services/pipeline.py:223-242`); unbounded growth hits
  context limits around 1–2 K transactions and 4096-token outputs risk
  truncation → JSON parse failure → failed stage.
- **Scope**: cap AG-03 input (last 3 months or max 500 txns, most recent first —
  matches its documented analysis window); formalize the existing monthly
  pre-aggregation for AG-04; note limits in agent definition docs (mirror-note).
- **Files**: `backend/src/services/pipeline.py`,
  `backend/src/agents/pattern_analyzer.py` (docstring),
  `backend/tests/test_pipeline.py`
- **Depends**: M3.2 | **Risk**: Low | **Complexity**: S–M | **Regression risk**:
  Low (output schema unchanged; pattern quality on >3-month histories may
  shift — acceptable, documented)
- **Acceptance**: 2,000 synthetic transactions produce a bounded prompt and the
  pipeline completes.
- **Testing**: T2. **Rollback**: revert.

### M3.4 — Merchant→category cache  [OPTIONAL — deferrable without blocking]
- **Purpose**: fix audit P4 — the same "TNB BILL PAYMENT" is re-categorized via
  paid API on every statement, every user. No caching exists anywhere.
- **Scope**: before AG-01 batching, resolve exact-normalized-description matches
  from the user's own high-confidence (≥0.9) categorized history; only misses go
  to the API; write-through on success. **DB-only** — no Redis dependency
  (Redis arrives with M4.4).
- **Files**: `backend/src/services/pipeline.py`, `backend/tests/test_pipeline.py`
- **Depends**: M3.2 | **Risk**: Low–Med (wrong-cache-hit risk bounded by
  confidence threshold + exact match) | **Complexity**: M | **Regression
  risk**: Low
- **Acceptance**: re-upload of same-merchant transactions makes 0 categorizer
  calls for known descriptions; correctness spot-check vs golden expectations.
- **Testing**: T2. **Rollback**: `CATEGORY_CACHE_ENABLED` config flag —
  read-optional by design.

## EPIC E4 — Background Job Durability (4 modules)

### M4.1 — Stale-run recovery
- **Purpose**: pipelines run in-process via FastAPI `BackgroundTasks`; a restart
  mid-run leaves the job in `running` forever, and the 409 duplicate-run guard
  then permanently blocks that source.
- **Scope**: startup sweep + periodic task marking `pending`/`running` runs older
  than a configurable deadline as `failed` ("timed out / interrupted");
  retrigger allowed afterwards.
- **Files**: `backend/src/services/pipeline.py`, `backend/src/main.py`
  (lifespan), `backend/src/config.py`, integration test simulating an orphaned
  run
- **Depends**: M0.3, M2.4 | **Risk**: Low–Med | **Complexity**: M |
  **Regression risk**: Low
- **Acceptance**: orphaned-run test recovers; recovered source accepts a new
  trigger.
- **Testing**: T2 + manual (kill server mid-run, restart, observe).
  **Rollback**: revert — additive sweep only.

### M4.2 — DB-level active-run uniqueness
- **Purpose**: close the SELECT-then-INSERT race in
  `backend/src/routers/jobs.py:52-63` — two concurrent triggers can both pass
  the existing-run check.
- **Scope**: partial unique index `pipeline_runs(source_id) WHERE status IN
  ('pending','running')` (Alembic migration); trigger endpoints catch
  `IntegrityError` → 409.
- **Files**: new migration, `backend/src/routers/jobs.py`,
  `backend/src/routers/transactions.py`, concurrency integration test
- **Depends**: M4.1 (recovery must exist before hard uniqueness, or a stuck run
  bricks the source) | **Risk**: Med (migration) | **Complexity**: S–M |
  **Regression risk**: Low
- **Acceptance**: two concurrent triggers → exactly one run; migration up/down
  verified.
- **Testing**: T2 + migration round-trip. **Rollback**: `alembic downgrade`
  (index drop — no data loss).

### M4.3 — Pipeline spend quota
- **Purpose**: fix audit P9 (cost half) — any authenticated user can loop
  uploads and burn unbounded Claude spend (cost-DoS vector).
- **Scope**: configurable daily run cap per user (count `pipeline_runs` created
  today); exceeded → 429 with clear message; surfaced in upload response.
  Default generous (e.g., 10/day).
- **Files**: `backend/src/services/pipeline.py` or new
  `backend/src/services/quota.py`, both trigger routers,
  `backend/src/config.py`, tests
- **Depends**: M4.2 | **Risk**: Low | **Complexity**: S–M | **Regression
  risk**: Low
- **Acceptance**: (cap+1)th trigger in a day → 429; resets next day;
  configurable.
- **Testing**: T2. **Rollback**: set cap to ∞ via config (built-in kill switch).

### M4.4 — Worker execution backend (arq — Decision D2), behind a flag  [HIGH RISK — runs solo]
- **Purpose**: fix the structural scaling blocker — jobs pinned to the serving
  process cannot scale horizontally, die on deploys, and (pre-M3.1) block the
  event loop.
- **Scope**: arq worker; `run_pipeline` becomes an arq task; enqueue from
  routers; `JOB_BACKEND=background_tasks|arq` setting keeps the current path
  exactly one release (removal ticket at creation); ADR-005 records the arq
  decision (see §DECISIONS D2). **Constraint C1**: worker runs as a plain
  process via the `arq` CLI; docker-compose service definition deferred until C1
  lifts; local Redis strategy decided at Wave 3 start (options: CI-only
  verification, native Redis/Memurai on Windows, or fakeredis for tests).
- **Files**: new `backend/src/worker.py`, `services/pipeline.py`, both trigger
  routers, `config.py`, dependency lock update,
  `docs/adr/ADR-005-job-backend.md`, integration tests for both backends
- **Depends**: M3.1 (async runtime), M4.1, M4.2, M2.3 (lock file) |
  **Risk**: **High** | **Complexity**: L | **Regression risk**: Med — flag
  defaults to the old path until acceptance
- **Acceptance**: with `JOB_BACKEND=arq`: E2E green; kill worker mid-run → M4.1
  recovers; API process restart does NOT kill an in-flight worker run; API
  responsive throughout.
- **Testing**: T3 + T4 chaos check (the kill tests above). **Rollback**: flip
  the flag — instant, zero-migration.

## EPIC E5 — Data Layer Reconciliation (5 modules)

### M5.1 — ADR-004: agent-output persistence (decision PRE-APPROVED: D1)
- **Purpose**: record the already-made decision ending the schema/data-model
  divergence (six tables migrated, modeled, never written: `debts`,
  `debt_items`, `patterns`, `predictions`, `advice`, `audit_logs`; agent outputs
  live only in the `pipeline_runs.stage_results` JSON blob).
- **Scope**: write `docs/adr/ADR-004-agent-output-persistence.md`: persist
  `debts`+`debt_items` (M5.2), `patterns`+`predictions` (M5.3); DEFER `advice`
  (until AG-06 exists) and `audit_logs` (own future initiative, revisit date
  set). Deferred = documented as intentionally unused, NOT dropped.
- **Files**: `docs/adr/ADR-004-agent-output-persistence.md`
- **Depends**: — (parallel-eligible in Wave 0; decision already made) |
  **Risk**: Low | **Complexity**: S | **Regression risk**: none
- **Acceptance**: ADR merged. **Testing**: docs verification. **Rollback**:
  supersede with a new ADR.

### M5.2 — Debt persistence (AG-02 → `debts`/`debt_items`)
- **Purpose**: give the product differentiator (tri-tier debt) a real home —
  today AG-02 results are two booleans on `transactions` plus a JSON blob.
- **Scope**: post-AG-02 grouping (provider+tier → `Debt` row; occurrences →
  `DebtItem`; link `transactions.debt_id`); idempotent on re-runs (upsert by
  user+provider+tier); `person_name` (HUTANG detection) documented as a PII
  field per PDPA.
- **Files**: `backend/src/services/pipeline.py` (or new
  `backend/src/services/debt_persistence.py`), tests, small migration if
  constraints needed
- **Depends**: M5.1, M3.2 | **Risk**: Med | **Complexity**: L |
  **Regression risk**: Low–Med (additive writes; re-run idempotency is the
  risk — tested)
- **Acceptance**: golden upload produces expected Debt rows (PTPTN→FORMAL,
  SPayLater→BNPL, hutang→HUTANG per
  `backend/tests/fixtures/golden/expected_debts.json`); pipeline re-run does not
  duplicate.
- **Testing**: T2. **Rollback**: revert writer — tables return to
  documented-orphan state; no destructive path.

### M5.3 — Pattern & prediction persistence
- **Purpose**: same reconciliation for AG-03/AG-04 outputs.
- **Scope**: write-through from pipeline stages to `patterns`/`predictions`
  (superseding rows per user+month where applicable); `stage_results` demoted to
  execution log only.
- **Files**: `backend/src/services/pipeline.py`, tests
- **Depends**: M5.1, M3.3 | **Risk**: Low–Med | **Complexity**: M |
  **Regression risk**: Low
- **Acceptance**: E2E asserts rows exist and match stage outputs; re-run
  supersedes, not duplicates.
- **Testing**: T2. **Rollback**: revert writers.

### M5.4 — Hash-based deduplication  [lands AFTER M6.1 — mandatory ordering]
- **Purpose**: fix audit P6 — dedup is O(new×existing) in Python with the full
  date-range loaded to memory; degrades quadratically past ~10 K rows/user.
- **Scope**: `content_hash` column (hash of
  date|signed_amount|normalized_description); backfill migration; unique index
  `(user_id, content_hash)`; conflict-detecting insert; SUSPICIOUS (same
  date+amount, different description) retained as a query, not a loop.
- **Files**: migration, `backend/src/models/transaction.py`, the transaction
  service (post-M6.1), `backend/src/data_quality/transaction_validator.py`,
  tests
- **Depends**: M1.2 (its contract tests must keep passing), M6.1 (so the router
  isn't rewritten twice) | **Risk**: Med (data migration + backfill) |
  **Complexity**: L | **Regression risk**: Med — dedup verdicts must be
  provably identical (golden re-upload matrix in tests)
- **Acceptance**: M1.2's E2E dedup tests pass unchanged; backfill verified on
  seeded data; migration down works.
- **Testing**: T3 (dedup of 1K-new vs 10K-existing measured). **Rollback**:
  `alembic downgrade` drops column/index; loop path restored by revert.

### M5.5 — Composite index & query review
- **Purpose**: fix audit P8 — only single-column indexes exist; the dominant
  query pattern filters `(user_id, transaction_date)` together.
- **Scope**: migration adding the composite index; EXPLAIN review of the list
  (and future aggregate) queries; drop redundant single-column index if fully
  covered.
- **Files**: migration
- **Depends**: M0.2 | **Risk**: Low | **Complexity**: S | **Regression risk**:
  ~none
- **Acceptance**: EXPLAIN shows index usage on the list query; migration
  round-trips.
- **Testing**: T2 + EXPLAIN evidence in PR. **Rollback**: downgrade.

## EPIC E6 — API & Service Layer (5 modules)

### M6.1 — TransactionService extraction
- **Purpose**: the upload endpoint is a ~200-line controller doing
  parse→validate→dedup→persist→trigger (`backend/src/routers/transactions.py`).
  Pure structural refactor, zero behavior change — which is exactly why M5.4
  waits for it.
- **Scope**: move the flow into `backend/src/services/transaction_service.py`;
  router keeps HTTP concerns only; **no logic edits**.
- **Files**: `backend/src/routers/transactions.py`, new
  `backend/src/services/transaction_service.py`,
  `backend/tests/test_upload_endpoint.py` (import paths ONLY — assertions
  unmodified)
- **Depends**: M0.3, M1.2 | **Risk**: Med (large mechanical move) |
  **Complexity**: M–L | **Regression risk**: Med — mitigated: upload E2E + the
  440-line endpoint suite must pass with unmodified assertions
- **Acceptance**: all upload tests green with unchanged expectations; router
  < 60 lines.
- **Testing**: T2. **Rollback**: revert (single-commit move).

### M6.2 — Dead scaffolding removal
- **Purpose**: delete the four empty packages mirroring the documented-but-
  abandoned architecture: `backend/src/repositories/`,
  `backend/src/api/middleware/`, `backend/src/api/routes/`,
  `backend/src/utils/`. The repository pattern is explicitly rejected — services
  own data access (decision recorded in the module PR).
- **Scope**: remove the packages; fix any imports (audit found none);
  ARCHITECTURE.md updated in M9.1.
- **Files**: deletions only
- **Depends**: M6.1 (layout decision settled) | **Risk**: Low |
  **Complexity**: S | **Regression risk**: ~none (empty `__init__.py`s)
- **Acceptance**: suite green; grep confirms no references.
- **Testing**: T1 + build. **Rollback**: trivial revert.

### M6.3 — JWKS lifecycle hardening  [HIGH BLAST RADIUS — runs solo]
- **Purpose**: the JWKS cache in `backend/src/auth.py:37-44` never expires —
  Clerk key rotation would break ALL auth until process restart; no
  refetch-on-unknown-kid fallback exists.
- **Scope**: TTL on the JWKS cache; forced refetch on unknown `kid` (once, then
  fail); single-flight lock against refetch stampede.
- **Files**: `backend/src/auth.py`, `backend/tests/test_auth.py` (extend — 289
  lines of dense auth coverage already exist)
- **Depends**: M0.2 | **Risk**: **High** (auth path) — never concurrent with
  another High-risk module | **Complexity**: M | **Regression risk**: Med —
  mitigated by the existing auth suite
- **Acceptance**: unit tests for expiry-refresh, unknown-kid-refetch, stampede;
  full suite green.
- **Testing**: T2 + manual login check. **Rollback**: revert single file.

### M6.4 — Request rate limiting
- **Purpose**: fix audit P9 (rate half) — no rate limiting exists anywhere
  despite docs claiming Redis-based limits.
- **Scope**: `slowapi` (or equivalent) per-user limits on upload + job-trigger
  endpoints; in-memory store now; Redis backend is a recorded deferred item
  (post-M4.4). Limits generous by default.
- **Files**: `backend/src/main.py`, affected routers, `backend/src/config.py`,
  tests
- **Depends**: M4.3 | **Risk**: Low | **Complexity**: S–M | **Regression
  risk**: Low
- **Acceptance**: burst beyond limit → 429; limits configurable; normal E2E
  unaffected.
- **Testing**: T2. **Rollback**: middleware removal / config disable.

### M6.5 — Server-side aggregates endpoint
- **Purpose**: fix audit P7 at the source — dashboard truth computed in SQL,
  not over a 200-row page in the browser.
- **Scope**: `GET /api/v1/transactions/summary` (totals, by-category, by-month,
  honoring the same filters as the list endpoint); SQL aggregation using M5.5's
  index; response schema in `backend/src/schemas/transaction.py`; sign
  convention asserted against `docs/CONVENTIONS.md` fixtures.
- **Files**: transaction service/router, `backend/src/schemas/transaction.py`,
  tests
- **Depends**: M5.5, M6.1 | **Risk**: Low–Med | **Complexity**: M |
  **Regression risk**: Low (new endpoint)
- **Acceptance**: summary equals ground truth on a seeded 1 K-txn dataset
  (sign-correct income/spending); p95 < 200 ms on that dataset.
- **Testing**: T3. **Rollback**: endpoint removal — frontend still on M1.1
  fallback until M7.3.

## EPIC E7 — Frontend Reliability (3 modules)

### M7.1 — Frontend test & CI infrastructure
- **Purpose**: the frontend has zero tests and ZERO CI presence — no lint,
  typecheck, test, or build gate runs anywhere.
- **Scope**: expand M1.1's Vitest bootstrap (React Testing Library, coverage);
  add a frontend CI job: `tsc -b`, `eslint`, `vitest`, `vite build`.
- **Files**: `frontend/package.json`, vitest config,
  `.github/workflows/ci.yml`, starter component tests
- **Depends**: M1.1 | **Risk**: Low | **Complexity**: M | **Regression risk**:
  none (additive)
- **Acceptance**: CI fails on frontend type/lint/test/build errors; at minimum
  the M1.1 tests run in CI.
- **Testing**: T1 + build. **Rollback**: remove CI job.

### M7.2 — Pipeline status UI
- **Purpose**: connect the existing job-status API
  (`GET /api/v1/jobs/{job_id}`, built in `backend/src/routers/jobs.py`, ZERO
  frontend consumers today) — a multi-minute background run is invisible and
  failures are silently swallowed.
- **Scope**: after upload success, poll the job endpoint (TanStack Query
  `refetchInterval`, stop on terminal status); render stage progress
  (`stages_completed`/`total_stages`) and failure state in
  `frontend/src/components/upload/StatementUpload.tsx`. Wiring an existing API
  = refactor-adjacent, not new-feature scope.
- **Files**: `frontend/src/components/upload/StatementUpload.tsx`, new
  `frontend/src/hooks/useJobStatus.ts`, `frontend/src/types/api.ts`, tests
- **Depends**: M7.1 | **Risk**: Low | **Complexity**: M | **Regression risk**:
  Low
- **Acceptance**: upload → visible progression → completed/failed rendered;
  polling stops on terminal status; RTL tests for all three states.
- **Testing**: T2 + manual T4. **Rollback**: revert component.

### M7.3 — Dashboard on server aggregates
- **Purpose**: final fix for defect B4 — remove the 200-row window entirely.
- **Scope**: dashboard consumes M6.5's summary endpoint for metrics/charts;
  client helpers retained only where genuinely client-side (recent list); M1.1's
  window label removed; client-side fallback kept exactly one release behind a
  trivial conditional (removal ticket at creation).
- **Files**: `frontend/src/pages/DashboardPage.tsx`,
  `frontend/src/hooks/useTransactions.ts`, new
  `frontend/src/hooks/useSummary.ts`, component tests
- **Depends**: M6.5, M7.1 | **Risk**: Low–Med | **Complexity**: M |
  **Regression risk**: Med — acceptance compares old-vs-new on a ≤200-txn
  account (exact match required) and a >200-txn account (new must match DB
  truth)
- **Acceptance**: that comparison matrix; loading/error states tested.
- **Testing**: T2 + manual. **Rollback**: flip to the client-side path.

## EPIC E8 — Agent Quality Measurement (2 modules)

### M8.1 — Golden accuracy harness (nightly; budget approved: Decision D5)
- **Purpose**: make the documented ">90% accuracy" quality gate measurable.
  Today `backend/tests/fixtures/golden/expected_categories.json` is generated
  but consumed by NOTHING; `expected_debts.json`/`expected_patterns.json` get
  structure checks only. No test measures actual agent accuracy — all agent
  tests mock the API.
- **Scope**: script scoring LIVE AG-01 vs `expected_categories.json` and AG-02
  vs `expected_debts.json` on the golden CSVs; nightly GitHub Actions workflow
  gated on the `ANTHROPIC_API_KEY` secret; report artifact (accuracy per
  category/tier); REPORT-ONLY at this stage; budget guard: golden set ≈150 txns
  ⇒ ~USD 0.50–1.00/run with M3.2 batching (owner-approved ceiling USD 15–30/mo).
- **Files**: new `backend/tests/accuracy/`, new `.github/workflows/accuracy.yml`
- **Depends**: M3.2 (batched async client) | **Risk**: Low | **Complexity**: M |
  **Regression risk**: none (out-of-band)
- **Acceptance**: nightly run produces a scored report; failure alerts but does
  not block PRs.
- **Testing**: T1 + one manual live run. **Rollback**: disable workflow.

### M8.2 — Accuracy as a release gate
- **Purpose**: promote from report to gate once a baseline exists.
- **Scope**: after ≥5 nightly runs, set thresholds calibrated to the OBSERVED
  baseline (proposal: AG-01 ≥90% category accuracy, AG-02 ≥85% tier recall —
  adjust to reality, don't gate on aspiration); required check for PRs touching
  `agents/**` prompts; update `.specify/audit/QUALITY_GATES.md`.
- **Depends**: M8.1 + ≥5 runs of baseline data | **Risk**: Low |
  **Complexity**: S | **Regression risk**: none
- **Acceptance**: prompt-change PRs blocked below threshold; documented.
- **Testing**: docs + workflow verification. **Rollback**: demote to
  report-only.

## EPIC E9 — Documentation Consolidation (3 modules — zero code risk, parallel-eligible)

### M9.1 — Live-doc truth pass
- **Purpose**: no live document may assert something the code disproves.
  Currently: `AGENTS.md` is a corrupted mechanical duplicate of `CLAUDE.md` with
  "Claude"→"Codex" find-replace damage ("Codex Sonnet 4" does not exist); both
  say backend/frontend are "to be created"; both reference
  `backend/src/services/statement_parser/` (real path:
  `backend/src/parsers/`); `.specify/plans/ARCHITECTURE.md` describes custom
  JWT auth (superseded by Clerk), a layout that doesn't match `src/`, and
  Celery/Zustand/shadcn adoptions that never happened.
- **Scope**: fix or stub `AGENTS.md` (recommend a 5-line pointer at CLAUDE.md);
  correct project `CLAUDE.md` (parser path, "to be created", 4-of-6 agent
  reality); ANNOTATE `ARCHITECTURE.md` superseded sections rather than
  rewriting.
- **Files**: `AGENTS.md`, `CLAUDE.md`, `.specify/plans/ARCHITECTURE.md`
- **Depends**: — | **Risk**: Low | **Complexity**: M | **Regression risk**: none
- **Acceptance**: no live doc asserts something the code disproves; AI-agent
  instruction files describe the real repo.
- **Testing**: docs review against source. **Rollback**: revert.

### M9.2 — Legacy archive & index regeneration (tracker: GitHub issues — Decision D4)
- **Purpose**: `SPEC_KIT_INDEX.md` references ~15 documents that do not exist;
  `TASK_REGISTRY.md` + 4 phase docs are frozen at "0 of 45 tasks, Not Started"
  since 2026-01-10 while the code is ~70% of Phases 1–3; four root-level
  numbered docs (`04/05/08/10_*.md`) use the deprecated "DuitSedar" name and
  were superseded by the spec-kit.
- **Scope**: move `04_DATABASE_SCHEMA.md`, `05_API_SPECIFICATION.md`,
  `08_DEPLOYMENT_GUIDE.md`, `10_PROPOSED_IMPROVEMENTS.md`, `run-specify.ps1`,
  `verify-aws-cli.ps1` → `docs/legacy/` with a tombstone README (MOVE, never
  delete); regenerate `.specify/SPEC_KIT_INDEX.md` listing only existing files;
  stamp `TASK_REGISTRY.md` + phase docs "HISTORICAL — superseded by GitHub
  issues"; create the GitHub issue set from this plan (one issue per remaining
  module, epic labels; `deferred-from-refactor` label exists — issues #1 and #2
  already use it).
- **Files**: moves + `docs/legacy/README.md`, `.specify/SPEC_KIT_INDEX.md`,
  `.specify/tasks/*`
- **Depends**: M0.1 | **Risk**: Low | **Complexity**: M | **Regression risk**:
  none
- **Acceptance**: index has zero phantom links; issues exist with dependencies
  noted.
- **Testing**: docs verification (link check). **Rollback**: move files back.

### M9.3 — ADR & prompt-library consolidation  [scheduled LATE — needs ADR-004/005 to exist]
- **Purpose**: two ADR homes with clashing numbers exist
  (`.specify/plans/ADR/001-AGENT-ORCHESTRATION.md` from January vs
  `docs/adr/ADR-001..003` from February — two different "ADR-001"s); prompt
  docs don't state implementation status; phantom references persist
  (`CONFLICT_RESOLUTION.md` referenced but never written; deleted
  `03_/09_` prompt docs still cross-referenced).
- **Scope**: single ADR home at `docs/adr/` (migrate the January ADR as
  `ADR-000-agent-orchestration` with a supersession note); mark ADR-003
  (pgvector) "Accepted — not yet implemented"; agent definition docs
  (`agents/definitions/*.md`) get an "Implemented — canonical prompt lives in
  `src/agents/*.py`" header (AG-01–04; the prompts currently match the code
  nearly verbatim — keep it that way) or "Design — not implemented" (AG-05/06);
  orchestration docs (`agents/orchestration/*.md`) stamped "ASPIRATIONAL —
  superseded by the sequential pipeline"; purge phantom references.
- **Files**: `docs/adr/*`, `.specify/plans/ADR/*`, `agents/definitions/*.md`,
  `agents/orchestration/*.md`, `agents/AGENT_INDEX.md`
- **Depends**: M5.1 (ADR-004 exists), M4.4 (ADR-005 exists) | **Risk**: Low |
  **Complexity**: S–M | **Regression risk**: none
- **Acceptance**: one ADR sequence, no number clashes; every prompt doc states
  its implementation status.
- **Testing**: docs verification. **Rollback**: revert.

## EPIC E10 — Deployment Readiness (3 modules — HORIZON)

*Deliberately specified to placeholder depth: full planning happens only after
Wave 4, because worker topology (M4.4) changes the deployment shape. Partly
blocked by Constraint C1.*

### M10.1 — CD + staging
- **Purpose**: deploy pipeline to a staging environment; promotion flow to
  production. No CD exists today (CI only); Phase-4 deployment work is 0%.
- **Depends**: M2.3, M4.4, E5 complete | **Risk**: High | **Complexity**: L
- **Acceptance/testing/rollback**: defined during horizon planning.

### M10.2 — Observability baseline
- **Purpose**: error tracking (e.g., Sentry), log shipping (builds on M2.4),
  basic metrics endpoint.
- **Depends**: M2.4, M10.1 | **Risk**: Med | **Complexity**: M

### M10.3 — Container hardening
- **Purpose**: multi-stage Dockerfile, image slimming, non-root verified (a
  non-root user + healthcheck already exist in `backend/Dockerfile`).
- **Depends**: M2.3, **Constraint C1 lifted** | **Risk**: Low |
  **Complexity**: S–M

---

# 8. Module Dependency Matrix (consolidated)

```
M0.1 → M0.2 → M0.3 ─┬→ M1.1
                    ├→ M1.2 ─┬→ M6.1 → M5.4        M1.2 also → (xfail flip in M0.3 tests)
                    ├→ M3.1 → M3.2 ─┬→ M3.3 → M5.3
                    │               ├→ M3.4 (optional)
                    │               ├→ M5.2 (also needs M5.1)
                    │               └→ M8.1 → M8.2
                    └→ M4.1 → M4.2 → M4.3 → M6.4
M3.1 + M4.1 + M4.2 + M2.3 → M4.4 → (ADR-005) → M9.3
M5.1 (no deps; decision D1 pre-approved) → M5.2, M5.3
M0.2 → M2.1, M2.3, M5.5, M6.3
M5.5 + M6.1 → M6.5 → M7.3
M1.1 → M7.1 → M7.2, M7.3
M2.4 → M4.1
M0.1 → M9.2 ;  M9.1, M1.3, M2.2 have no dependencies
M5.1 + M4.4 → M9.3
E10: M2.3 + M4.4 + E5 → M10.1 → M10.2 ; M2.3 + C1-lifted → M10.3
```

Audit-finding → module traceability: B1→M1.1 · B2→M1.2 · B3→M1.3 ·
B4→M1.1/M7.3 · P1→M3.1 · P2→M3.2 · P3→M3.1 · P4→M3.4 · P5→M3.3 · P6→M5.4 ·
P7→M6.5+M7.3 · P8→M5.5 · P9→M4.3+M6.4 · orphan tables→M5.1/M5.2/M5.3 ·
dead packages→M6.2 · job durability→M4.1/M4.2/M4.4 · JWKS→M6.3 ·
config drift→M2.1 · fat controller→M6.1 · validator/is_recurring/PII→M3.2 ·
trigger race→M4.2 · no integration tests→M0.2/M0.3 · no accuracy→M8.1/M8.2 ·
no frontend tests→M1.1/M7.1 · deps/logging→M2.3/M2.4 · env docs→M2.2 ·
doc rot→M9.1/M9.2/M9.3 · no CD→E10.

---

# 9. Recommended Execution Order — binding rules

1. No module starts until its dependencies passed all gates (§14).
2. **At most one High-risk module in flight at any time** (M3.1, M4.4, M6.3
   never overlap — trivially satisfied by one-at-a-time execution; kept
   explicit in case of future parallelism).
3. Decision modules resolve early (M5.1's decision is already made — D1).
4. E9 documentation work may proceed in parallel with anything (zero code risk).
5. Refactor-only modules (M6.1) never ship in the same PR as behavior changes
   (M5.4); the `M6.1 → M5.4` ordering is mandatory.
6. Every temporary artifact has a named removal ticket at creation
   (M1.1 window label → removed by M7.3; M4.4 `JOB_BACKEND` flag → removed one
   release after acceptance; M7.3 client-side fallback → removed next release).
7. **Constraint C2**: one module = one branch = one merge; stop and await owner
   approval between modules.

---

# 10–11. Acceptance Criteria & Validation Requirements

Acceptance criteria are specified per module in §6–7 (every card has an
"Acceptance" line — those are the binding criteria). Validation requirements
are the test tiers per card plus the standing rules in §13.

---

# 12. Integration Checkpoints

| Checkpoint | After | Verifies |
|---|---|---|
| CP-0 | Wave 0 | Integration harness green in CI; E2E pipeline test running; conventions documented; `xfail` register in place |
| CP-1 | Wave 1 | Golden re-upload ⇒ 0 duplicates; dashboard signs correct; CI installs from lock; local mypy restored |
| CP-2 | Wave 2 | `/health` p95 < 100 ms during a pipeline run; 100-txn statement ⇒ ≤8 agent API calls & <30 s envelope |
| CP-3 | Wave 3 | Kill-worker chaos test recovers; concurrent triggers ⇒ exactly 1 run; `JOB_BACKEND` flag switchable both ways |
| CP-4 | Wave 4 | Golden upload populates `debts`/`patterns`/`predictions` idempotently; hash-dedup perf evidence; router < 60 lines |
| CP-5 | Wave 5 | Dashboard matches DB truth at >200 txns; JWKS rotation survivable; frontend gates in CI |
| CP-6 (closeout) | Wave 6 | Nightly accuracy report + thresholds; zero phantom doc links; no dual code paths remain; §19 success criteria re-tested |

---

# 13. Testing Strategy

**Baseline (frozen 2026-07-04, recorded in `docs/plans/refactor-baseline.md`)**:
263 tests pass · 90.42% coverage (configured floor 80%) · ruff clean · local
mypy BROKEN (Python 3.14 venv vs 3.11 CI — CI is the authoritative mypy gate
until M2.3) · frontend has no gates until M1.1/M7.1.

**Test tiers**:

| Tier | Contents | Gate evidence |
|---|---|---|
| T1 | ruff + mypy + unit tests + build | CI green |
| T2 | T1 + integration suite on real Postgres (+ migration up/down where schema changes) | CI green incl. `integration` marker |
| T3 | T2 + performance evidence (call counts, latency assertion, or EXPLAIN attached to PR) | artifact in PR |
| T4 | T2/T3 + scripted manual verification with checklist in PR | checklist ticked |

**Standing rules**:
- Backend coverage never drops below **90.42%** (the baseline — stricter than
  the configured 80%). Any module lowering it fails its gate.
- Existing test assertions are NEVER modified silently; a change requires a PR
  note referencing the defect register or the authorizing module card.
- Never write a test that asserts the current broken behavior of B1–B4.
- Frontend modules additionally require `tsc -b` + `vite build`
  (self-carried until M7.1 adds the CI job).
- **C1**: the integration tier is CI-authoritative until C1 lifts; local
  integration runs are optional and auto-skip without `TEST_DATABASE_URL`.

**Local verification commands** (backend venv at `backend/venv`, currently
Python 3.14 until M2.3):
```
cd backend && ./venv/Scripts/python.exe -m pytest tests/ -q     # expect 263+ passed
cd backend && ./venv/Scripts/ruff.exe check .                   # expect clean
# do NOT run mypy locally until M2.3 — use CI
```

---

# 14. Quality Gates

```
Module complete → Lint → Types (CI-authoritative until M2.3) → Build
→ Unit → Integration (once M0.2 exists) → Coverage ≥ 90.42%
→ Perf evidence (T3 modules) → Docs updated (incl. CURRENT_MODULE_STATE.md)
→ Owner review & approval → MERGE → stop; await approval → next module
```

**Failure protocol**: any gate fails → STOP; diagnose root cause (no blind
retries); if the fix exceeds module scope → revert to last green, record a
deferred item, re-plan the module. A red gate is never carried forward as
"known flaky."

**Governance**: RinggitSense is a PDPA project — no auto-commits; every merge
is explicitly owner-confirmed. Commit format `type(scope): subject` with body
bullets. Never commit secrets, `.env`, or real personal data.

---

# 15. Rollback Strategy

- **Program-wide**: `git checkout pre-refactor-baseline` (tag at `c83e2c6`)
  reverts everything.
- **Per module**: every module is one merge; revert the merge commit. Specific
  strategies per card (§6–7). Notable:
  - Migrations (M4.2, M5.4, M5.5): `alembic downgrade` verified as part of the
    module's own gate before merge.
  - M4.4 worker: flip `JOB_BACKEND=background_tasks` — instant, zero-migration.
  - M3.4 cache: `CATEGORY_CACHE_ENABLED=false`.
  - M4.3 quota: set cap to ∞ via config.
  - M7.3 dashboard: conditional flip to the retained client-side path.
- **Data-writing modules** (M5.2/M5.3/M5.4): writers are additive; reverting a
  writer returns tables to documented-orphan state without data destruction;
  backfills are verified reversible before merge.

---

# 16. Deferred Work

## 16.1 Deferred by decision
- `advice` + `audit_logs` table persistence — deferred per Decision D1; revisit
  when AG-06 exists / audit initiative starts.
- Redis backend for rate limiting — after M4.4 lands.
- Playwright frontend E2E — after E7.
- Docker-dependent verification (image build gate, compose worker service,
  M10.3) — suspended under Constraint C1; re-verify when lifted.
- GitHub branch protection on `main` — manual owner action, not scriptable.

## 16.2 Temporary artifacts with removal tickets
- M1.1 "latest 200 transactions" label → removed by M7.3.
- M4.4 `JOB_BACKEND` dual path → removed one release after acceptance.
- M7.3 client-side metrics fallback → removed the following release.

## 16.3 Pre-existing WIP preserved as issues (branch streamline, 2026-07-04)
- **Issue #1** — AG-05 Query Agent WIP (452 lines): was branch
  `feat/ag-05-query-agent`, commit `70226e6`. Recover:
  `git cherry-pick 70226e6`. Out of program scope (feature work); revisit after
  the program with the async runtime (M3.1) in place.
- **Issue #2** — Deployment config WIP (589 lines): was branch
  `chore/deployment-config`, commit `4f7b598`. Recover:
  `git cherry-pick 4f7b598`. Feeds E10 horizon planning.
- Both labeled `deferred-from-refactor` at
  https://github.com/FaisalHanafi98/RinggitSense/issues/1 and /issues/2.
  The commits remain in git's object store, recoverable by SHA.

## 16.4 Process for new discoveries
Mid-module discoveries → GitHub issue, label `deferred-from-refactor`. The
module never grows. New DEFECTS are severity-triaged: data-integrity/security
defects preempt the wave plan; everything else queues.

---

# 17. Future Roadmap (post-program — explicitly OUT of current scope)

Feature backlog that resumes only after program closeout: AG-05 Query agent +
AG-06 Advisor agent (definitions exist at `agents/definitions/query.md` and
`advisor.md`; Pydantic schemas already in `backend/src/schemas/agents/`);
RHB and Touch 'n Go parsers; PDF statement parsing; pgvector semantic search
(ADR-003, accepted-not-implemented); advice UI with mandatory disclaimers;
debt-tracker and pattern-visualization pages; chat/query interface; PWA/dark
mode and other items from the legacy `10_PROPOSED_IMPROVEMENTS.md` backlog;
E10 deployment (AWS ECS Fargate per original architecture) after horizon
planning.

---

# 18. Known Risks

## 18.1 Confirmed defects at baseline (defect register — fix modules assigned)
- **B1** — Dashboard income/spending INVERTED.
  `frontend/src/hooks/useTransactions.ts:19-21` treats positive as income;
  backend stores expense=positive, income=negative
  (`backend/src/parsers/base.py:29-33`). Fix: M1.1.
- **B2** — Duplicate detection BROKEN for credits.
  `backend/src/routers/transactions.py:152-160` +
  `backend/src/data_quality/transaction_validator.py:193-194` (signed vs
  unsigned comparison; type hardcoded DEBIT). Re-uploads duplicate every income
  row. Fix: M1.2.
- **B3** — FALSE "processed locally" compliance claim.
  `frontend/src/components/dashboard/FinancialDisclaimer.tsx:8`. PDPA-relevant.
  Fix: M1.3.
- **B4** — Dashboard metrics silently limited to newest 200 transactions.
  `frontend/src/pages/DashboardPage.tsx:10`. Fix: M1.1 interim → M7.3 final.

## 18.2 Program risks & mitigations
- **Solo developer, cross-model AI execution** → everything externalized to the
  repo (this document); `CURRENT_MODULE_STATE.md` updated at every transition;
  one-module-one-merge keeps the tree always releasable.
- **High-risk modules (M3.1, M4.4, M6.3)** → run solo, never concurrently;
  each has an instant rollback (revert / flag / single-file revert).
- **Local environment drift** (Python 3.14 venv, broken mypy, no Docker) →
  CI is authoritative for mypy + integration until M2.3 / C1-lift.
- **Claude API cost during accuracy runs** → budget guard + owner-approved
  ceiling (D5).
- **Clerk dependency** (auth SaaS) → M6.3 hardens rotation; JWKS outage
  degrades to 503 on token verification (existing behavior).
- **`main` not yet pushed to origin** → until pushed, the merged program state
  exists only locally; pushing is a pending owner-confirmed action (risk of
  local loss until then).

## 18.3 Architectural risks accepted knowingly
- AG-05/AG-06 remain stubs throughout the program ("skipped" pipeline stages) —
  by design; the pipeline's `total_stages=6` presentation is honest in
  `stage_results`.
- pgvector capability provisioned but unused until a future feature needs it.
- `.specify/` spec-kit docs remain partially historical after M9.2 stamps them.

---

# 19. Program Success Criteria (re-tested at closeout, CP-6)

- Pipeline: 100 transactions < 30 s with ZERO event-loop blocking.
- Re-upload of any statement is idempotent (0 duplicates, including credits).
- Dashboard matches DB truth at any data volume, with correct sign convention.
- Jobs survive process restarts; no permanently stuck runs possible.
- Per-user Claude spend bounded (quota + rate limit + cache).
- Backend coverage ≥ 90.42% including the integration tier; frontend gated in CI.
- Agent accuracy measured nightly with calibrated thresholds.
- Every live document verifiably true; single ADR sequence; zero phantom links.
- Dependencies locked; Python 3.11 aligned local/CI; local mypy restored.
- Scorecard movement achieved (§1 table): Performance 3→7, Testing 6→8,
  Documentation 4→7, Scalability 4→7, overall debt 5→7.5.

---

# 20. Definition of Done — per phase

**Per module**: card scope fully implemented · all gates in §14 passed ·
acceptance criteria demonstrably met (evidence in PR) · docs + ledger +
`CURRENT_MODULE_STATE.md` updated · merged to `main` by owner approval · report
delivered · STOP until next approval.

**Per wave**: all wave modules merged · the wave's integration checkpoint
(§12) verified · no red gates carried forward · deferred-items log current.

**Program done (closeout)**: CP-6 passed · §19 criteria re-tested with evidence
· temporary artifacts removed · module ledger 100% ☑ (E10 horizon may remain
open as its own follow-on program) · final report against the audit scorecard.

---

# APPENDIX A — Engineering Decision Log (with rationale & alternatives)

**D1 — Agent-output persistence (orphan tables)** · APPROVED 2026-07-04
- Decision: persist `debts`+`debt_items`, `patterns`, `predictions`; defer
  `advice` and `audit_logs` (documented as intentionally unused, not dropped).
- Rationale: tri-tier debt is the product differentiator and needs a queryable
  home; JSON blobs undermine relational integrity; the tables already exist.
- Alternatives considered: (a) drop all six tables and stay JSON-only —
  rejected: forfeits the product's core data model; (b) persist all six now —
  rejected: `advice` has no producer (AG-06 unbuilt) and `audit_logs` deserves
  its own initiative.
- Constraints/assumptions: writers must be idempotent on pipeline re-runs.
- Impact: M5.1 (ADR), M5.2, M5.3.

**D2 — Job backend: arq over Celery** · APPROVED 2026-07-04
- Decision: arq. ADR-005 formalizes it inside M4.4.
- Rationale: async-native (matches the M3.1 runtime), minimal ceremony,
  Redis-only dependency, tiny API surface for a solo project.
- Alternatives: Celery (heavier, richer ecosystem, sync-first — overkill);
  RQ (sync); custom asyncio loop (reinvents durability).
- Constraints: C1 — worker verified as a plain process; compose service and
  local-Redis strategy resolved at Wave 3 start.
- Impact: M4.4; unlocks horizontal scaling; deploy shape for E10.

**D3 — Lock tooling: uv** · APPROVED 2026-07-04
- Decision: uv for dependency locking and venv management.
- Rationale: speed, single tool for lock+install, growing standard.
- Alternatives: pip-tools (slower, adequate); Poetry (heavier workflow change).
- Impact: M2.3; CI install step changes.

**D4 — Live tracker: GitHub issues** · APPROVED 2026-07-04
- Decision: GitHub issues replace the static task registry; label
  `deferred-from-refactor` for discoveries (already in use: issues #1, #2).
- Rationale: the static registry rotted immediately (frozen at 0% since
  2026-01-10 while code advanced) — proof that static tracking fails here.
- Alternatives: keep updating markdown registries — rejected on evidence.
- Impact: M9.2 creates the issue set; change control (§16.4).

**D5 — Nightly accuracy budget** · APPROVED 2026-07-04
- Decision: recurring API budget approved, ceiling ~USD 15–30/mo.
- Rationale: agent accuracy is a documented quality gate with zero enforcement;
  ~USD 1/night is cheap insurance on the product's core competence.
- Impact: M8.1, M8.2.

**Constraint C1 — Docker off-limits locally** · OWNER DIRECTIVE 2026-07-04
- The owner has local Docker problems. No module may require local Docker;
  `docker-compose.yml`/`Dockerfile` are neither modified nor relied on for
  verification until lifted. GitHub Actions service containers (GitHub-hosted
  runners) remain available. Impacts: M0.2 (CI-first harness), M2.2 (boot check
  without DB), M2.3 (no image-build gate), M4.4 (plain-process worker), M10.3
  (blocked).

**Constraint C2 — One PR = one module** · OWNER DIRECTIVE 2026-07-04
- Module → branch → commit → test → verify → merge → stop → approval → next.

**Earlier in-repo ADRs (pre-program, still standing)**:
- `docs/adr/ADR-001-cost-optimization.md` — Sonnet 4 for all agents (its cost
  model assumed per-transaction calls; M3.2 restores the economics it intended).
- `docs/adr/ADR-002-specialized-agents.md` — six specialized agents over one
  monolithic prompt (4 of 6 built; the "AG-03/04 periodic batch" mitigation was
  never implemented — they run every upload; windowing M3.3 partially
  compensates).
- `docs/adr/ADR-003-postgresql-pgvector.md` — pgvector over dedicated vector DB
  (accepted, NOT implemented; M9.3 stamps it).
- Embedded program decisions: safety-net-first ordering (§4); services over
  repositories (M6.2); DB-only cache before Redis (M3.4); AsyncAnthropic over
  run_in_executor (M3.1 — fixes the root cause instead of wrapping it);
  hash-based dedup over the Python loop (M5.4); CI-first integration testing
  (C1).

# APPENDIX B — Self-verification checklist (per export requirements)

✓ Every planned Epic documented (E0–E10, 11 epics) ·
✓ Every planned Module documented (39: E0×3, E1×3, E2×4, E3×4, E4×4, E5×5,
E6×5, E7×3, E8×2, E9×3, E10×3) ·
✓ Every dependency documented (§8 + per card) ·
✓ Every execution phase documented (§5.2, §9, §20) ·
✓ Every quality gate documented (§14) ·
✓ Every testing requirement documented (§13 + per card) ·
✓ Every acceptance criterion documented (per card, §6–7) ·
✓ Every engineering decision documented (Appendix A) ·
✓ Current status externalized (§5.1, `CURRENT_MODULE_STATE.md`) ·
✓ No implementation knowledge remains only in conversation history.

*End of EXECUTION_PLAN_v1.md*
