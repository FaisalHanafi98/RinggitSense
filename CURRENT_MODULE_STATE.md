# CURRENT_MODULE_STATE

> Living engineering state file. Overwrite this in place as execution advances.
> Not a summary — the single source of truth for "where are we right now."
> Last updated: 2026-07-04 (M0.3 implemented, awaiting merge approval to dev)

---

Current Program:
Audit remediation & production-readiness refactor
(basis: docs/plans/EXECUTION_PLAN_v1.md)

Current Wave:
Wave 0 — Regression Safety Net

Current Epic:
E0 — Regression Safety Net

Current Module:
M0.3 — E2E pipeline test + amount-sign contract tests  [IMPLEMENTED — AWAITING MERGE]

Status:
100% implemented on branch · verified locally (263 passed + 17 skipped, ruff clean) · CI run pending merge

Branch:
refactor/m0.3-e2e-pipeline-tests  (off dev at dc3fec5)

Baseline tag:
pre-refactor-baseline -> c83e2c6  (program-wide revert point, on main)

Branch Structure:
  main  = production-grade, deployment-connected (promotion-only)
  dev   = sandbox, primary working branch (module branches merge here)
  Remote: origin

Previous modules:
  M0.1 — Baseline freeze & working agreements  [MERGED to main at e689d92]
  M0.2 — Integration test harness               [MERGED to main at 24b92c3]

---

Completed (M0.3):
- docs/CONVENTIONS.md: sign convention as the single source of truth
  - Debit/expense = positive, credit/income = negative
  - Canonical reference: ParsedTransaction.signed_amount (parsers/base.py:29-33)
  - API serializes stored value unchanged
  - B1/B2 defect register references
  - Pipeline stage naming, Malaysian-first rules
- backend/tests/integration/test_amount_contract.py: 8 contract tests
  - TestParserSignConvention: parser signed_amount (debits positive, credits negative)
  - TestStorageSignConvention: DB stores signed amounts correctly
  - TestApiSerialization: API returns stored value unchanged (no sign flipping)
  - TestDedupSignContract: B2 xfail — re-upload must not duplicate credits
    (xfail strict=True, references defect register B2, flips in M1.2)
- backend/tests/integration/test_upload_pipeline_e2e.py: 5 E2E tests
  - test_upload_stores_transactions: upload golden CSV, assert stored rows with correct signs
  - test_pipeline_run_created_and_transitioned: pipeline_run status pending -> completed
  - test_pipeline_writes_categories: mocked AG-01 assigns categories to all txns
  - test_api_list_after_pipeline: GET /transactions returns all stored rows with categories
  - test_pipeline_stage_results_populated: stage_results has all 6 stages (4 completed + 2 skipped)
  - Uses a committing session (not savepoint-isolated) because the pipeline
    creates its own session via async_session_maker; agents mocked via patch

Verification (local, 2026-07-04):
- pytest tests/: 263 passed, 17 skipped, 90.42% coverage (unchanged from baseline)
  - 17 skipped = 4 (M0.2) + 13 (M0.3) integration tests (TEST_DATABASE_URL unset — C1)
- ruff check . : All checks passed!
- mypy: not run locally (CI-authoritative until M2.3)

CI verification (pending merge + push):
- CI will run: pytest tests/integration/ -m integration --no-cov -v
  against the existing Postgres 15 service with TEST_DATABASE_URL set
- The 17 integration tests are expected to PASS in CI
- The B2 xfail test is expected to xfail in CI (documenting the known defect)

Remaining (this module):
- MERGE branch refactor/m0.3-e2e-pipeline-tests -> dev (needs owner confirmation)
- PUSH dev to origin after merge
- Verify CI passes (integration tests green in CI)
- After M0.3 merges to dev: Wave 0 is complete → CP-0 promotion (dev → main)

Blocked:
- Merge to dev is gated on explicit owner approval (PDPA project rule: no auto-merge)

Regression Risk:
- Low. Touches zero source code. New files only (2 test files + 1 doc).
  Unit suite verified unaffected: 263 passed, 90.42% coverage.

Next Action:
- STOP. Await owner instruction. On approval: merge to dev, push, verify CI green.
- After M0.3 merges to dev: Wave 0 (E0) is complete.
  First promotion CP-0: dev → main (all Wave 0 gates pass).
  Then Wave 1 begins (M1.1, M1.2, M1.3, M2.1, M2.3, M2.4 — small, independent, low risk).

Quality Gate:
- Lint: PASS (ruff "All checks passed!")
- Types: pending CI (local mypy broken pre-existing — M2.3 fixes)
- Build: N/A (no source code changed)
- Unit tests: PASS (263 passed, 90.42% coverage, unchanged from baseline)
- Integration: locally auto-skipped (C1); CI run pending merge
- Docs updated: YES (CONVENTIONS.md + this file)
- Worktree: has uncommitted M0.3 changes (about to be committed)
- Approval: PENDING (merge to dev)

---

Verification commands (backend venv is at backend/venv, Python 3.14 locally):
  cd backend && ./venv/Scripts/python.exe -m pytest tests/ -q      # 263 passed, 17 skipped
  cd backend && ./venv/Scripts/ruff.exe check .                    # clean
  # NOTE: run mypy in CI, not locally — local mypy exits 1 with no output (M2.3 fixes)
  # NOTE: integration tests auto-skip locally (TEST_DATABASE_URL unset per C1)

Next module on deck (await owner go-ahead after M0.3 merges to dev):
  Wave 1 — Correctness + Hygiene (small, independent, low risk):
  M1.1 — Dashboard metrics correctness (sign fix + window honesty, fix B1/B4)
  M1.2 — Credit-safe deduplication (fix B2, flip M0.3 xfails)
  M1.3 — Compliance copy correction (fix B3)
  M2.1 — Config single-source
  M2.3 — Dependency & runtime pinning (uv, restore local mypy)
  M2.4 — Structured logging baseline

Next promotion on deck (after M0.3 merges to dev):
  CP-0: dev → main promotion (Wave 0 complete)
  Gates at CP-0: unit (263+), integration (17 CI green), lint (ruff), types (CI mypy)
