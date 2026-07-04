# CURRENT_MODULE_STATE

> Living engineering state file. Overwrite this in place as execution advances.
> Not a summary — the single source of truth for "where are we right now."
> Last updated: 2026-07-04 (M0.2 merged to main, pushed to remote)

---

Current Program:
Audit remediation & production-readiness refactor
(basis: docs/plans/EXECUTION_PLAN_v1.md, supersedes refactor-execution-plan.md)

Current Wave:
Wave 0 — Regression Safety Net

Current Epic:
E0 — Regression Safety Net

Current Module:
M0.2 — Integration test harness on real PostgreSQL  [MERGED]

Status:
MERGED to main (merge commit 24b92c3, --no-ff) · verified stable on main · pushed to remote
Remote renamed from `origin` to `main` (2026-07-04, owner directive)

Baseline tag:
pre-refactor-baseline -> c83e2c6  (program-wide revert point)

Previous module:
M0.1 — Baseline freeze & working agreements  [MERGED to main at e689d92; pushed to origin]

---

Completed (M0.2):
- backend/tests/conftest.py: extended with integration-tier fixtures
  - pytest_configure: registers "integration" marker
  - test_database_url: session-scoped, skips if TEST_DATABASE_URL unset (C1)
  - integration_engine: session-scoped async engine, create_all/drop_all, skips on unreachable DB
  - integration_db: function-scoped session with join_transaction_mode="create_savepoint"
    (per-test isolation via outer-transaction rollback; app commits release SAVEPOINT only)
- backend/tests/integration/__init__.py: new package
- backend/tests/integration/conftest.py:
  - _skip_if_no_test_db: autouse fixture, skips when TEST_DATABASE_URL unset (C1)
  - test_user: creates a real User row in the test DB
  - client: async httpx client with get_current_user + get_db overridden
- backend/tests/integration/test_round_trip.py: 4 integration tests
  - test_create_user_insert_transaction_list_via_api: the trivial round-trip acceptance test
  - test_list_empty_for_fresh_user: empty list for new user
  - test_transaction_is_user_scoped: multi-tenancy isolation check
  - test_transaction_persists_within_test: DB write readable via fresh select
- backend/pyproject.toml: registered "integration" marker
- .github/workflows/ci.yml: added TEST_DATABASE_URL env var + integration test step

Verification (local, 2026-07-04):
- pytest tests/: 263 passed, 4 skipped, 90.42% coverage (unchanged from baseline)
  - 4 skipped = integration tests (TEST_DATABASE_URL unset locally — C1 auto-skip)
- pytest tests/ -m "not integration": 263 passed, 4 deselected (unit suite clean)
- pytest tests/integration/ -rs: 4 skipped with correct reason
- ruff check . : All checks passed!
- mypy: not run locally (CI-authoritative until M2.3)

CI verification (pending CI run after push):
- CI will run: pytest tests/integration/ -m integration --no-cov -v
  against the existing Postgres 15 service with TEST_DATABASE_URL set
- The 4 integration tests are expected to PASS in CI

Remaining (this module):
- Verify CI passes (integration tests green in CI for the first time)
- Optional owner action: enable GitHub branch protection on main (manual, not scriptable)

Blocked:
- None. Module is closed.

Regression Risk:
- Low. Touches conftest.py (additive — existing anyio_backend fixture preserved),
  pyproject.toml (additive marker), ci.yml (additive env var + step). Zero source
  code changed. Unit suite verified unaffected: 263 passed, 90.42% coverage.

Next Action:
- M0.2 is CLOSED. Next module is M0.3 (E2E pipeline test + amount-sign contract tests).
- Do NOT begin M0.3 until the owner explicitly says go.

Quality Gate:
- Lint: PASS (ruff "All checks passed!")
- Types: pending CI (local mypy broken pre-existing — M2.3 fixes)
- Build: N/A (no source code changed)
- Unit tests: PASS (263 passed, 90.42% coverage, unchanged from baseline)
- Integration: locally auto-skipped (C1); CI run pending push
- Docs updated: YES (this file)
- Worktree: CLEAN
- Approval: APPROVED & MERGED (24b92c3)

---

Verification commands (backend venv is at backend/venv, Python 3.14 locally):
  cd backend && ./venv/Scripts/python.exe -m pytest tests/ -q      # 263 passed, 4 skipped
  cd backend && ./venv/Scripts/ruff.exe check .                    # clean
  # NOTE: run mypy in CI, not locally — local mypy exits 1 with no output (M2.3 fixes)
  # NOTE: integration tests auto-skip locally (TEST_DATABASE_URL unset per C1)

Next module on deck (await owner go-ahead):
  M0.3 — E2E pipeline test + amount-sign contract tests
  Branch: refactor/m0.3-e2e-pipeline-tests
  Files: backend/tests/integration/test_upload_pipeline_e2e.py,
         backend/tests/integration/test_amount_contract.py,
         docs/CONVENTIONS.md
  Acceptance: E2E green with today's behavior (xfails aside); convention doc reviewed.
  Gains: the regression net for E3, E4, E5, E6 — highest-leverage artifact in the program.
