# RinggitSense — Refactor Execution Plan

**Program**: Audit remediation & production-readiness refactor
**Basis**: Architecture Maturity & Scalability Audit, 2026-07-03
**Companion**: [refactor-baseline.md](refactor-baseline.md) — baseline evidence,
defect register (B1–B4), working agreements, decision log (D1–D5),
constraints (C1 Docker off-limits locally, C2 one PR = one module),
and the live module progress ledger.
**Version**: 1.1 (2026-07-04) — decisions applied, Docker constraint annotated
**Change control**: plan changes are edits to this file with a one-line rationale.

## How to read this plan

| Scale | Values |
|---|---|
| Complexity | **S** ≤ ½ day · **M** 1–2 days · **L** 3–5 days (solo-dev days) |
| Risk | **Low** additive/isolated · **Med** modifies existing behavior · **High** touches auth, jobs, or runtime model |
| Regression risk | Likelihood of breaking behavior users/tests rely on |
| Test tier | **T1** static+unit · **T2** +integration · **T3** +performance evidence · **T4** +manual E2E (see §Test Strategy) |

Execution protocol per module (C2): branch `refactor/m<id>-<slug>` → implement →
gates → merge → stop, report, await approval. Scope is the module card; discoveries
become GitHub issues labeled `deferred-from-refactor` (D4).

---

## 1 · Audit Traceability

| Audit finding | Module |
|---|---|
| B1 dashboard income/spending inverted | M1.1 |
| B2 credit dedup broken | M1.2 |
| B3 false "processed locally" claim | M1.3 |
| B4 metrics over 200-row window | M1.1 (interim) → M7.3 (final) |
| P1 sync client blocks event loop | M3.1 |
| P2 per-transaction API calls | M3.2 |
| P3 no timeout/retry; ineffective semaphore | M3.1 |
| P4 no caching | M3.4 |
| P5 AG-03 unbounded prompt | M3.3 |
| P6 O(N×M) dedup | M5.4 |
| P7 client-side aggregates | M6.5 + M7.3 |
| P8 missing composite index | M5.5 |
| P9 no rate limit / spend quota | M4.3 (pipeline quota) + M6.4 (request rate) |
| Orphan tables (6 of 10) | M5.1 → M5.2, M5.3 (per D1) |
| Dead scaffolding packages | M6.2 |
| No durable jobs / stuck-run recovery | M4.1, M4.2, M4.4 |
| JWKS never refreshes | M6.3 |
| Config duplication | M2.1 |
| 200-line upload controller | M6.1 |
| Unwired validator; hardcoded `is_recurring`; PII in `stage_results` | M3.2 |
| Pipeline-trigger race | M4.2 |
| Zero integration coverage | M0.2, M0.3 |
| No accuracy harness; unused golden fixtures | M8.1, M8.2 |
| Zero frontend tests / no frontend CI | M1.1 (bootstrap) + M7.1 (full) |
| Unpinned deps, Python drift, `print()` logging | M2.3, M2.4 |
| Stale `.env.example` / README | M2.2 |
| Doc rot: duplicates, phantom index, dead registry, dual ADR homes, legacy files | M9.1, M9.2, M9.3 |
| No CD/staging/monitoring | M10.1–M10.3 (horizon) |

**Out of scope** (feature work, enters backlog after the program): AG-05/AG-06
implementation, RHB/TnG parsers, PDF parsing, pgvector/semantic search, advice UI,
PWA/dark-mode backlog.

---

## 2 · Epic Portfolio

| # | Epic | Modules | Theme | Aggregate risk |
|---|---|---|---|---|
| E0 | Regression Safety Net | 3 | Build the net before walking the wire | Low |
| E1 | Correctness Hotfixes | 3 | The three confirmed bugs | Low–Med |
| E2 | Configuration & Environment Hygiene | 4 | One source of truth for config, deps, logging | Low |
| E3 | Agent Runtime Modernisation | 4 | Async, batching, bounded inputs, caching | Med–High |
| E4 | Background Job Durability | 4 | Jobs that survive restarts and contain cost | Med–High |
| E5 | Data Layer Reconciliation | 5 | Make the schema and the data model agree | Med |
| E6 | API & Service Layer | 5 | Thin controllers, hardened auth, server aggregates | Med |
| E7 | Frontend Reliability | 3 | Tests, job visibility, true numbers | Low–Med |
| E8 | Agent Quality Measurement | 2 | Make ">90% accuracy" measurable | Low |
| E9 | Documentation Consolidation | 3 | Paper matches code | Zero code risk |
| E10 | Deployment Readiness (Horizon) | 3 | CD, staging, observability — planned after refactor; blocked in part by C1 | — |

---

## 3 · Module Specifications

### E0 — Regression Safety Net

**M0.1 — Baseline freeze & working agreements** — ✅ this module produced
[refactor-baseline.md](refactor-baseline.md) and tag `pre-refactor-baseline`.
See that file for the full record.

**M0.2 — Integration test harness on real PostgreSQL**
- Purpose: make the DB boundary testable. CI provisions a Postgres service no test uses.
- Scope: pytest fixtures creating/dropping schema per session against
  `TEST_DATABASE_URL`; FastAPI dependency-override for Clerk auth (test-user
  injection); async `httpx` client fixture; `integration` marker; CI step runs it.
  **C1**: CI-first — locally the marker auto-skips when `TEST_DATABASE_URL` is
  unset/unreachable; local runs optional, never required.
- Files: `backend/tests/conftest.py`, new `backend/tests/integration/`,
  `backend/pyproject.toml`, `.github/workflows/ci.yml`
- Depends: M0.1 | Risk: Low | Complexity: M | Regression risk: Low
- Acceptance: trivial round-trip (create user → insert transaction → list via API)
  green in CI; unit suite unaffected; local run without DB skips cleanly.
- Testing: T2. Rollback: delete new files, revert conftest.
- Gains: unlocks safe execution of E1, E3–E6.

**M0.3 — E2E pipeline test + amount-sign contract tests**
- Purpose: one executable spec of upload→pipeline→DB→API, and of the sign
  convention behind B1/B2.
- Scope: upload `maybank_golden.csv` (mocked Claude) → assert stored rows,
  categories, `pipeline_runs` transitions, API list output; contract test: credits
  serialize negative, debits positive; write `docs/CONVENTIONS.md`. B2-related
  assertions marked `xfail` referencing the defect register; flipped in M1.2.
- Files: `backend/tests/integration/test_upload_pipeline_e2e.py`,
  `test_amount_contract.py`, `docs/CONVENTIONS.md`
- Depends: M0.2 | Risk: Low | Complexity: M | Regression risk: none
- Acceptance: E2E green with today's behavior (registered `xfail`s aside);
  convention doc reviewed.
- Testing: T2. Rollback: delete files.
- Gains: the regression net for E3, E4, E5, E6.

### E1 — Correctness Hotfixes

**M1.1 — Dashboard metrics correctness (sign fix + window honesty)**
- Purpose: fix B1; neutralize B4 pending M7.3.
- Scope: correct `computeMetrics`/`groupByMonth` to the convention (negative =
  income); "based on latest 200 transactions" label until M7.3 (removal ticket at
  birth); bootstrap **minimal Vitest** (config + these unit tests only; full infra
  is M7.1).
- Files: `frontend/src/hooks/useTransactions.ts`,
  `frontend/src/pages/DashboardPage.tsx`, `frontend/package.json`,
  new `useTransactions.test.ts`
- Depends: M0.3 | Risk: Low | Complexity: M | Regression risk: Med — every
  dashboard number changes; that is the intended outcome
- Acceptance: unit tests encode the convention; manual golden-data check shows
  salary under Income; window label visible.
- Testing: T2 + manual. Rollback: revert (3 files).
- Gains: correct headline numbers; first frontend tests in the repo.

**M1.2 — Credit-safe deduplication**
- Purpose: fix B2 — re-uploads must not duplicate income rows.
- Scope: normalize the comparison (signed vs signed, or reconstruct type from
  stored sign) in the upload dedup path; flip M0.3 `xfail`s. No redesign — the
  hash-based replacement is M5.4.
- Files: `backend/src/routers/transactions.py` (dedup block),
  possibly `backend/src/data_quality/transaction_validator.py`
- Depends: M0.3 | Risk: Low | Complexity: S–M | Regression risk: Med — dedup
  verdicts change for credits (intended); SUSPICIOUS classifications may shift
- Acceptance: E2E golden CSV uploaded twice → second upload stores 0 rows,
  reports all as duplicates including salary/bonus.
- Testing: T2. Rollback: revert; `xfail`s restored.
- Gains: data integrity — the top PDPA-adjacent correctness risk closed.

**M1.3 — Compliance copy correction**
- Purpose: fix B3.
- Scope: reword `FinancialDisclaimer.tsx` (processed on RinggitSense servers; AI
  analysis via Anthropic's API; PDPA notice); repo-wide grep for other local-only
  claims; one matching README line. Constitution's 3 mandatory sentences retained.
- Files: `frontend/src/components/dashboard/FinancialDisclaimer.tsx`, `README.md`
- Depends: — | Risk: Low | Complexity: S | Regression risk: none (copy only)
- Acceptance: no source or doc claims local-only processing.
- Testing: T1 + docs verification. Rollback: revert.
- Gains: compliance exposure closed.

### E2 — Configuration & Environment Hygiene

**M2.1 — Config single-source**
- Purpose: kill config drift (settings claim PDF+CSV; router hardcodes CSV-only).
- Scope: router reads `settings.MAX_UPLOAD_SIZE_MB`/`settings.ALLOWED_EXTENSIONS`;
  settings set to actual capability (`["csv"]`); module-level constants deleted.
- Files: `backend/src/config.py`, `backend/src/routers/transactions.py`
- Depends: M0.2 | Risk: Low | Complexity: S | Regression risk: Low (behavior
  preserved by design; upload tests prove it)
- Acceptance: one definition (grep); upload tests unchanged and green.
- Testing: T2. Rollback: revert.

**M2.2 — Onboarding truth (`.env.example` + README)**
- Purpose: docs-following developer gets a working setup.
- Scope: add `CLERK_DOMAIN`, `CLERK_JWT_AUDIENCE`, `CLAUDE_MODEL`; remove dead JWT
  keys; README quick-start gains Clerk prerequisite + honest status line.
  **C1**: app boots without a DB (lazy engine) so local boot check stands;
  DB-dependent steps verified in CI.
- Files: `backend/.env.example`, `README.md`
- Depends: — | Risk: Low | Complexity: S | Regression risk: none
- Acceptance: fresh clone + example-following boots the API (manual).
- Testing: T4-lite. Rollback: revert.

**M2.3 — Dependency & runtime pinning** *(tooling: uv — D3)*
- Purpose: reproducible builds; end the 3.14/3.11 drift; **restore local mypy**
  (broken at baseline — see baseline doc §1).
- Scope: uv lock file; `pytest`/`anyio` to dev deps; verify `psycopg2-binary`
  necessity (drop if alembic env is async; document if kept); recreate venv on
  3.11; CI installs from lock. **C1**: no Docker image build in the gate; CI-green
  from lock is the gate; image build re-verified when C1 lifts.
- Files: `backend/requirements*.txt` → `requirements.in`/lock or
  `pyproject.toml`-managed, `.github/workflows/ci.yml`, `backend/pyproject.toml`
- Depends: M0.2 | Risk: Low–Med | Complexity: M | Regression risk: Low — full
  suite is the gate
- Acceptance: CI green from lock; `pip check` clean; local `mypy src/` works again
  on the 3.11 venv.
- Testing: T2 + build verification (CI). Rollback: restore old requirements files
  (kept until module accepted).

**M2.4 — Structured logging baseline**
- Purpose: replace `print()`/ad-hoc logging before E4 needs real logs.
- Scope: stdlib logging config (optional JSON formatter flag), uvicorn
  integration, replace `print` in `src/main.py` lifespan; level from settings.
- Files: `backend/src/main.py`, `backend/src/config.py`, new
  `backend/src/logging_config.py`
- Depends: — | Risk: Low | Complexity: S–M | Regression risk: Low
- Acceptance: startup/shutdown + one request path emit structured records; no
  `print` in `src/`.
- Testing: T1 + manual log inspection. Rollback: revert.

### E3 — Agent Runtime Modernisation

*Sequential within the epic — each module rewrites what the previous stabilized.*

**M3.1 — Async client, timeouts, retries, call-level concurrency**
- Purpose: fix P1/P3 — stop blocking the event loop; bound and retry every call.
- Scope: `AsyncAnthropic` in `agents/base.py`; `invoke`/`invoke_batch` become
  async; explicit client timeout; bounded exponential-backoff retry on retryable
  errors; semaphore moves from stage level to around individual calls; size into
  settings. Mechanical update of all mocked agent tests.
- Files: `backend/src/agents/base.py`, all 4 agent modules,
  `backend/src/services/pipeline.py` call sites, `backend/src/config.py`,
  tests: `test_categorizer.py`, `test_debt_detector.py`,
  `test_pattern_analyzer.py`, `test_predictor.py`, `test_pipeline.py`
- Depends: M0.3 | Risk: **High** | Complexity: L | Regression risk: Med —
  mitigated by the E2E net and unchanged output schemas
- Acceptance: E2E green; performance evidence: `/health` p95 <100ms while a
  pipeline runs (scripted); a simulated hung call times out and fails the stage,
  not the server.
- Testing: T3. Rollback: revert branch — no schema/data changes.
- Gains: server no longer freezes during pipelines (audit's #1 defect).

**M3.2 — Batch execution & stage hygiene**
- Purpose: fix P2 plus three findings living in the same two functions: unwired
  `AgentOutputValidator`, hardcoded `is_recurring=False`, PII-bearing error
  strings in `stage_results`.
- Scope: `_run_categorizer`/`_run_debt_detector` use existing
  `categorize_batch`/`detect_batch` chunked ≤50 with id-mapped application;
  unmatched ids → per-item errors; error entries carry codes + transaction ids,
  never raw descriptions; wire `AgentOutputValidator` at stage boundaries; pass
  real `is_recurring`/`user_comment`. One module because all four changes rewrite
  the same ~80 lines.
- Files: `backend/src/services/pipeline.py`, minor: `agents/categorizer.py`,
  `agents/debt_detector.py`, `data_quality/agent_output_validator.py`,
  `tests/test_pipeline.py`
- Depends: M3.1 | Risk: Med | Complexity: L | Regression risk: Med —
  `stage_results` shape stays backward-compatible (asserted by E2E)
- Acceptance: E2E green; call-count assertion: 100-txn statement ⇒ ≤4 categorizer
  + ≤4 debt calls (was ~200); no description text in any `stage_results` error;
  perf evidence: mocked-latency simulation inside the documented <30s envelope.
- Testing: T3. Rollback: revert (single code path — no dual paths kept live).
- Gains: ~50× latency & major token-cost reduction; PDPA hygiene in stored blobs.

**M3.3 — AG-03/AG-04 input windowing**
- Purpose: fix P5 — bound prompt size (pipelines fail at ~1–2K transactions).
- Scope: cap AG-03 input (last 3 months or max 500 txns, most recent first);
  formalize monthly pre-aggregation for AG-04; note limits in agent definition
  docs (mirror-note only).
- Files: `backend/src/services/pipeline.py`, `agents/pattern_analyzer.py`
  (docstring), `tests/test_pipeline.py`
- Depends: M3.2 | Risk: Low | Complexity: S–M | Regression risk: Low
- Acceptance: 2,000 synthetic txns produce bounded prompt and complete.
- Testing: T2. Rollback: revert.

**M3.4 — Merchant→category cache** *(optional — deferrable without blocking)*
- Purpose: fix P4 — stop re-categorizing "TNB BILL PAYMENT" forever.
- Scope: before AG-01 batching, resolve exact-normalized-description matches from
  the user's own high-confidence (≥0.9) history; misses go to API; write-through.
  DB-only (no Redis — Redis arrives with M4.4).
- Files: `backend/src/services/pipeline.py`, `tests/test_pipeline.py`
- Depends: M3.2 | Risk: Low–Med | Complexity: M | Regression risk: Low
- Acceptance: re-upload of same-merchant txns makes 0 categorizer calls for known
  descriptions; correctness spot-check vs golden expectations.
- Testing: T2. Rollback: `CATEGORY_CACHE_ENABLED` flag — read-optional by design.

### E4 — Background Job Durability

**M4.1 — Stale-run recovery**
- Purpose: restarts must never leave runs stuck in `running` (which also
  permanently 409-blocks the source).
- Scope: startup sweep + periodic task marking `pending`/`running` older than a
  configurable deadline as `failed` ("timed out / interrupted"); retrigger allowed.
- Files: `backend/src/services/pipeline.py`, `backend/src/main.py`,
  `backend/src/config.py`, integration test simulating an orphaned run
- Depends: M0.3, M2.4 | Risk: Low–Med | Complexity: M | Regression risk: Low
- Acceptance: orphaned-run test recovers; recovered source accepts a new trigger.
- Testing: T2 + manual (kill server mid-run, restart, observe). Rollback: revert.

**M4.2 — DB-level active-run uniqueness**
- Purpose: close the SELECT-then-INSERT race on concurrent triggers.
- Scope: partial unique index on `pipeline_runs(source_id) WHERE status IN
  ('pending','running')` (Alembic); triggers catch `IntegrityError` → 409.
- Files: new migration, `backend/src/routers/jobs.py`,
  `backend/src/routers/transactions.py`, concurrency integration test
- Depends: M4.1 (recovery before hard uniqueness) | Risk: Med (migration) |
  Complexity: S–M | Regression risk: Low
- Acceptance: two concurrent triggers → exactly one run; migration up/down.
- Testing: T2 + migration round-trip. Rollback: `alembic downgrade` (index drop).

**M4.3 — Pipeline spend quota**
- Purpose: close the cost-DoS vector — bounded Claude spend per user.
- Scope: configurable daily run cap per user; exceeded → 429; surfaced in upload
  response. Default generous (e.g., 10/day).
- Files: `backend/src/services/pipeline.py` or new `services/quota.py`, both
  trigger routers, `backend/src/config.py`, tests
- Depends: M4.2 | Risk: Low | Complexity: S–M | Regression risk: Low
- Acceptance: (cap+1)th trigger in a day → 429; resets next day; configurable.
- Testing: T2. Rollback: set cap to ∞ via config (built-in kill switch).

**M4.4 — Worker execution backend (arq — D2), behind a flag**
- Purpose: fix the structural scaling blocker — jobs pinned to the serving process.
- Scope: arq worker; `run_pipeline` becomes an arq task; enqueue from routers;
  `JOB_BACKEND=background_tasks|arq` keeps the current path exactly one release
  (removal ticket at birth); ADR-005 records the arq decision. **C1**: worker runs
  as a plain process (`arq` CLI); compose service deferred until C1 lifts; local
  Redis strategy decided at Wave 3 (CI-only verification, native Redis/Memurai, or
  fakeredis for tests).
- Files: new `backend/src/worker.py`, `services/pipeline.py`, both trigger
  routers, `config.py`, deps, `docs/adr/ADR-005-job-backend.md`, integration
  tests for both backends
- Depends: M3.1, M4.1, M4.2, M2.3 | Risk: **High** | Complexity: L | Regression
  risk: Med — flag defaults to the old path until acceptance
- Acceptance: with `JOB_BACKEND=arq`: E2E green; kill worker mid-run → M4.1
  recovers; API restart does not kill an in-flight worker run; API responsive
  throughout.
- Testing: T3 + T4 chaos check. Rollback: flip flag — instant, zero-migration.

### E5 — Data Layer Reconciliation

**M5.1 — ADR-004: agent-output persistence** *(decision pre-approved: D1)*
- Purpose: record the already-made decision ending schema/data-model divergence.
- Scope: write ADR-004: persist `debts`+`debt_items`, `patterns`, `predictions`;
  defer `advice` (until AG-06) and `audit_logs` (own initiative, revisit date).
- Files: `docs/adr/ADR-004-agent-output-persistence.md`
- Depends: — | Risk: Low | Complexity: S | Regression risk: none
- Acceptance: ADR merged. Testing: docs verification. Rollback: supersede.

**M5.2 — Debt persistence (AG-02 → `debts`/`debt_items`)**
- Purpose: give tri-tier debt a real home (today: two booleans + JSON blob).
- Scope: post-AG-02 grouping (provider+tier → `Debt`; occurrences → `DebtItem`;
  link `transactions.debt_id`); idempotent on re-runs (upsert by
  user+provider+tier); `person_name` documented as PII per PDPA.
- Files: `backend/src/services/pipeline.py` (or new
  `services/debt_persistence.py`), tests, small migration if constraints needed
- Depends: M5.1, M3.2 | Risk: Med | Complexity: L | Regression risk: Low–Med
  (additive writes; re-run idempotency tested)
- Acceptance: golden upload produces expected Debt rows (PTPTN→FORMAL,
  SPayLater→BNPL, hutang→HUTANG per `expected_debts.json`); re-run does not
  duplicate.
- Testing: T2. Rollback: revert writer — tables return to documented-orphan state.

**M5.3 — Pattern & prediction persistence**
- Purpose: same reconciliation for AG-03/AG-04.
- Scope: write-through to `patterns`/`predictions` (superseding per user+month
  where applicable); `stage_results` demoted to execution log.
- Files: `backend/src/services/pipeline.py`, tests
- Depends: M5.1, M3.3 | Risk: Low–Med | Complexity: M | Regression risk: Low
- Acceptance: E2E asserts rows match stage outputs; re-run supersedes.
- Testing: T2. Rollback: revert writers.

**M5.4 — Hash-based deduplication** *(lands after M6.1 to avoid rewriting the router twice)*
- Purpose: fix P6 — replace the O(N×M) loop with DB-enforced identity.
- Scope: `content_hash` column (hash of date|signed_amount|normalized_description);
  backfill migration; unique index `(user_id, content_hash)`; conflict-detecting
  insert; SUSPICIOUS retained as a query.
- Files: migration, `backend/src/models/transaction.py`, the transaction service
  (post-M6.1), `data_quality/transaction_validator.py`, tests
- Depends: M1.2 (its contract tests keep passing), M6.1 | Risk: Med (data
  migration + backfill) | Complexity: L | Regression risk: Med — verdicts must be
  provably identical (golden re-upload matrix)
- Acceptance: M1.2 E2E dedup tests pass unchanged; backfill verified on seeded
  data; migration down works.
- Testing: T3 (dedup 1K-new vs 10K-existing measured). Rollback: downgrade drops
  column/index; loop path restored by revert.

**M5.5 — Composite index & query review**
- Purpose: fix P8 before volume makes it an incident.
- Scope: migration adding `(user_id, transaction_date)`; EXPLAIN review of list
  (and future aggregate) queries; drop redundant single-column index if covered.
- Files: migration
- Depends: M0.2 | Risk: Low | Complexity: S | Regression risk: ~none
- Acceptance: EXPLAIN shows index usage; migration round-trips.
- Testing: T2 + EXPLAIN evidence in PR. Rollback: downgrade.

### E6 — API & Service Layer

**M6.1 — TransactionService extraction**
- Purpose: 200-line upload controller → thin router over a service. Pure
  structural refactor, zero behavior change (why M5.4 waits for it).
- Scope: move parse→validate→dedup→persist→trigger into
  `services/transaction_service.py`; router keeps HTTP concerns; **no logic
  edits**.
- Files: `backend/src/routers/transactions.py`, new
  `backend/src/services/transaction_service.py`,
  `tests/test_upload_endpoint.py` (import paths only)
- Depends: M0.3, M1.2 | Risk: Med | Complexity: M–L | Regression risk: Med —
  upload E2E + endpoint suite must pass with **unmodified assertions**
- Acceptance: all upload tests green with unchanged expectations; router <60 lines.
- Testing: T2. Rollback: revert (single-commit move).

**M6.2 — Dead scaffolding removal**
- Purpose: delete the four empty packages contradicting the real layout
  (repository pattern explicitly rejected — services own data access; recorded in
  the PR).
- Scope: remove `src/repositories/`, `src/api/`, `src/utils/`; fix imports (audit
  found none); ARCHITECTURE.md updated in M9.1.
- Files: deletions only
- Depends: M6.1 | Risk: Low | Complexity: S | Regression risk: ~none
- Acceptance: suite green; grep confirms no references.
- Testing: T1 + build. Rollback: trivial revert.

**M6.3 — JWKS lifecycle hardening** *(High blast radius — runs solo)*
- Purpose: Clerk key rotation must not take the service down until restart.
- Scope: TTL on JWKS cache; forced refetch on unknown `kid` (once, then fail);
  single-flight lock against refetch stampede.
- Files: `backend/src/auth.py`, `tests/test_auth.py` (extend)
- Depends: M0.2 | Risk: **High** | Complexity: M | Regression risk: Med —
  mitigated by the dense existing auth suite
- Acceptance: unit tests for expiry-refresh, unknown-kid-refetch, stampede; full
  suite green.
- Testing: T2 + manual login check. Rollback: revert single file.

**M6.4 — Request rate limiting**
- Purpose: complement M4.3's spend quota with per-user request limits.
- Scope: `slowapi` (or equivalent) on upload + job-trigger endpoints; in-memory
  store now; Redis backend is a recorded deferred item (post-M4.4).
- Files: `backend/src/main.py`, affected routers, `config.py`, tests
- Depends: M4.3 | Risk: Low | Complexity: S–M | Regression risk: Low
- Acceptance: burst beyond limit → 429; configurable; normal E2E unaffected.
- Testing: T2. Rollback: middleware removal / config disable.

**M6.5 — Server-side aggregates endpoint**
- Purpose: fix P7 at the source — truth computed in SQL.
- Scope: `GET /api/v1/transactions/summary` (totals, by-category, by-month,
  honoring list filters); SQL aggregation on M5.5's index; schema in
  `schemas/transaction.py`.
- Files: transaction service/router, `backend/src/schemas/transaction.py`, tests
- Depends: M5.5, M6.1 | Risk: Low–Med | Complexity: M | Regression risk: Low
  (new endpoint; sign convention asserted against `docs/CONVENTIONS.md` fixtures)
- Acceptance: summary equals ground truth on seeded 1K-txn dataset (sign-correct);
  p95 <200ms on that dataset.
- Testing: T3. Rollback: endpoint removal — frontend still on M1.1 fallback.

### E7 — Frontend Reliability

**M7.1 — Frontend test & CI infrastructure**
- Purpose: frontend has zero tests and zero CI presence.
- Scope: expand M1.1's Vitest bootstrap (RTL, coverage); frontend CI job:
  `tsc -b`, `eslint`, `vitest`, `vite build`.
- Files: `frontend/package.json`, vitest config, `.github/workflows/ci.yml`,
  starter component tests
- Depends: M1.1 | Risk: Low | Complexity: M | Regression risk: none
- Acceptance: CI fails on frontend type/lint/test/build errors.
- Testing: T1 + build. Rollback: remove CI job.

**M7.2 — Pipeline status UI**
- Purpose: connect the existing job-status API — today a multi-minute run is
  invisible and failures are silent.
- Scope: after upload, poll `GET /jobs/{job_id}` (TanStack Query
  `refetchInterval`, stop on terminal status); render stage progress and failure
  states in `StatementUpload.tsx`.
- Files: `frontend/src/components/upload/StatementUpload.tsx`, new
  `useJobStatus.ts`, `frontend/src/types/api.ts`, tests
- Depends: M7.1 (API exists already) | Risk: Low | Complexity: M | Regression
  risk: Low
- Acceptance: upload → visible progression → completed/failed rendered; polling
  stops on terminal status; RTL tests for all three states.
- Testing: T2 + manual T4. Rollback: revert component.

**M7.3 — Dashboard on server aggregates**
- Purpose: final fix for B4 — remove the 200-row window entirely.
- Scope: dashboard consumes M6.5 summary for metrics/charts; client helpers
  retained only where genuinely client-side; M1.1 label removed; client-side
  fallback kept one release behind a trivial conditional (removal ticket at
  birth).
- Files: `frontend/src/pages/DashboardPage.tsx`,
  `frontend/src/hooks/useTransactions.ts`, new `useSummary.ts`, component tests
- Depends: M6.5, M7.1 | Risk: Low–Med | Complexity: M | Regression risk: Med —
  acceptance compares old-vs-new on a ≤200-txn account (exact match) and a
  >200-txn account (new matches DB truth)
- Acceptance: that comparison matrix; loading/error states tested.
- Testing: T2 + manual. Rollback: flip to client-side path.

### E8 — Agent Quality Measurement

**M8.1 — Golden accuracy harness (nightly)** *(budget approved: D5)*
- Purpose: make ">90% accuracy" measurable — `expected_categories.json` currently
  scores nothing.
- Scope: script scoring live AG-01 vs `expected_categories.json` and AG-02 vs
  `expected_debts.json` on golden CSVs; nightly GitHub Actions workflow gated on
  `ANTHROPIC_API_KEY` secret; report artifact (per category/tier); report-only;
  budget guard: ~150 txns ⇒ ~USD 0.50–1/run with M3.2 batching.
- Files: new `backend/tests/accuracy/`, new `.github/workflows/accuracy.yml`
- Depends: M3.2 | Risk: Low | Complexity: M | Regression risk: none (out-of-band)
- Acceptance: nightly run produces scored report; failure alerts, doesn't block.
- Testing: T1 + one manual live run. Rollback: disable workflow.

**M8.2 — Accuracy as a release gate**
- Purpose: promote from report to gate once a baseline exists.
- Scope: after ≥5 nightly runs, set thresholds (proposal: AG-01 ≥90%, AG-02
  tier-recall ≥85% — calibrated to observed baseline); required check for PRs
  touching `agents/**` prompts; update `QUALITY_GATES.md`.
- Depends: M8.1 + baseline data | Risk: Low | Complexity: S
- Acceptance: prompt-change PRs blocked below threshold; documented.
  Rollback: demote to report-only.

### E9 — Documentation Consolidation *(zero code risk — parallel-eligible)*

**M9.1 — Live-doc truth pass**
- Scope: fix or stub `AGENTS.md` (the "Codex Sonnet 4" corruption — recommend
  5-line pointer at CLAUDE.md); correct project `CLAUDE.md` (parser path, "to be
  created", 4-of-6 agent reality); annotate `ARCHITECTURE.md` superseded sections
  (auth → Clerk, layout → actual, Celery/Zustand/shadcn → not adopted) rather
  than rewriting.
- Depends: — | Risk/Complexity: Low/M
- Acceptance: no live doc asserts something the code disproves.

**M9.2 — Legacy archive & index regeneration** *(tracker: GitHub issues — D4)*
- Scope: move `04/05/08/10_*.md` + `run-specify.ps1` + `verify-aws-cli.ps1` →
  `docs/legacy/` with tombstone README (move, never delete); regenerate
  `SPEC_KIT_INDEX.md` to list only existing files; stamp `TASK_REGISTRY.md` + 4
  phase docs "HISTORICAL — superseded by GitHub issues"; create the issue set
  from this roadmap (one issue per module, epic labels,
  `deferred-from-refactor` label created).
- Depends: M0.1 | Risk/Complexity: Low/M
- Acceptance: index has zero phantom links; issues exist with dependencies noted.

**M9.3 — ADR & prompt-library consolidation** *(scheduled late — needs ADR-004/005 to exist)*
- Scope: single ADR home at `docs/adr/` (migrate `.specify/plans/ADR/001` as
  `ADR-000-agent-orchestration` with supersession note, resolving the
  duplicate-001 clash); ADR-003 marked "Accepted — not yet implemented"; agent
  definition docs get an "Implemented — canonical prompt lives in
  `src/agents/*.py`" header (AG-01–04) or "Design — not implemented" (AG-05/06);
  orchestration docs stamped "ASPIRATIONAL — superseded by sequential pipeline";
  purge references to deleted files.
- Depends: M5.1, M4.4 | Risk/Complexity: Low/S–M
- Acceptance: one ADR sequence, no number clashes; every prompt doc states its
  implementation status.

### E10 — Deployment Readiness *(horizon — full planning after Wave 4; M10.3 and compose work blocked by C1)*

| Module | Purpose | Depends | Risk/Complexity |
|---|---|---|---|
| M10.1 CD + staging | Deploy pipeline + staging env, promotion flow | M2.3, M4.4, E5 done | High/L |
| M10.2 Observability baseline | Error tracking, log shipping, basic metrics | M2.4, M10.1 | Med/M |
| M10.3 Container hardening | Multi-stage Dockerfile, slimming | M2.3, **C1 lifted** | Low/S–M |

---

## 4 · Implementation Order

```
WAVE 0  Safety Net           M0.1 → M0.2 → M0.3            ║ parallel: M9.1, M5.1, M1.3, M2.2
WAVE 1  Correctness+Hygiene  M1.1, M1.2, M2.1, M2.3, M2.4  (small, independent, low risk)
WAVE 2  Agent Runtime        M3.1 → M3.2 → M3.3            ║ parallel: M9.2
WAVE 3  Job Durability       M4.1 → M4.2 → M4.3 → M4.4
WAVE 4  Data Layer           M5.2, M5.3 → M5.5 → [M6.1 → M5.4]   ║ parallel: M3.4 (optional)
WAVE 5  API & Frontend       M6.2, M6.3*, M6.4, M6.5 → M7.1 → M7.2, M7.3
WAVE 6  Quality & Closeout   M8.1 → M8.2 · M9.3 · retire M1.1 label & M4.4 flag
HORIZON Deployment           E10 (planned separately after Wave 4)

*M6.3 (auth) runs solo — never concurrent with another High-risk module.
```

**Critical path**: M0.2 → M0.3 → M3.1 → M3.2 → M4.4 → M5.2/M5.3 → M6.5 → M7.3

**Binding sequencing rules**
1. No module starts until its dependencies passed all gates.
2. At most one High-risk module in flight (M3.1, M4.4, M6.3 never overlap).
3. Decision modules resolve early (M5.1's decision is already made — D1).
4. E9 may proceed in parallel with anything.
5. Refactor-only modules (M6.1) never ship with behavior changes (M5.4);
   `M6.1 → M5.4` ordering is mandatory.
6. Every temporary artifact has a named removal ticket at creation.
7. **C2**: one module = one branch = one merge; stop and await approval between
   modules.

**Calendar estimate** (solo dev): Waves 0–3 ≈ 3.5–4 weeks (core de-risk milestone);
Waves 4–6 ≈ 3–4 further weeks. E10 excluded.

## 5 · Test Strategy

Global pre-implementation validation: recorded in
[refactor-baseline.md](refactor-baseline.md) (green baseline, defect register
preventing enshrined bugs).

| Tier | Contents | Gate evidence |
|---|---|---|
| T1 | ruff + mypy + unit tests + build | CI green |
| T2 | T1 + integration suite on real Postgres (+ migration up/down where schema changes) | CI green incl. `integration` marker |
| T3 | T2 + performance evidence (call counts, latency assertion, or EXPLAIN in PR) | artifact in PR |
| T4 | T2/T3 + scripted manual verification with checklist in PR | checklist ticked |

Standing rules: coverage ≥ 90.42% (baseline, stricter than the 80% floor);
regression = prior suite runs with unmodified assertions (changes require a PR note
referencing the defect register or authorizing module card); frontend modules also
require `tsc -b` + `vite build` (self-carried until M7.1 adds the CI job).
**C1**: mypy gate is CI-authoritative until M2.3 restores the local toolchain;
integration tier is CI-authoritative until C1 lifts.

## 6 · Quality Gates

```
Module complete → Lint → Types → Build → Unit → Integration
→ Coverage ≥ baseline → Perf evidence (T3) → Docs updated
→ Review & approval → MERGE → stop; await approval → next module
```

Failure protocol: any gate fails → stop; diagnose root cause (no blind retries);
fix exceeds module scope → revert to last green, record deferred item, re-plan.
A red gate is never carried forward as "known flaky."

## 7 · Change Control

1. Scope is the module card. Mid-module discoveries → GitHub issue,
   label `deferred-from-refactor`. The module does not grow.
2. Pre-registered deferred items: Redis backend for rate limiting (post-M4.4);
   removal tickets for the three temporary artifacts; `advice`/`audit_logs`
   revisit (per ADR-004); frontend E2E (Playwright, post-E7); all §1 out-of-scope
   features; Docker-dependent verifications suspended under C1 (image build,
   compose worker service) — re-verified when C1 lifts.
3. New defects found mid-program: severity triage — data-integrity/security
   defects preempt the wave plan; everything else queues.
4. Plan changes are edits to this document with a one-line rationale.

## 8 · Program Success Criteria

Re-tested at closeout against the audit scorecard: pipeline 100 txns <30s with
zero event-loop blocking · re-upload idempotent · dashboard matches DB truth at
any volume · jobs survive restart · per-user spend bounded · coverage ≥ 90.42%
including integration tier · accuracy measured nightly · every live document
verifiably true · dependencies locked · expected scorecard movement:
Performance 3→7, Testing 6→8, Documentation 4→7, Scalability 4→7,
overall debt 5→7.5.
