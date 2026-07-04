# CURRENT_MODULE_STATE

> Living engineering state file. Overwrite this in place as execution advances.
> Not a summary — the single source of truth for "where are we right now."
> Last updated: 2026-07-04 (branch structure change: dev/main split)

---

Current Program:
Audit remediation & production-readiness refactor
(basis: docs/plans/EXECUTION_PLAN_v1.md, supersedes refactor-execution-plan.md)

Current Wave:
Wave 0 — Regression Safety Net

Current Epic:
E0 — Regression Safety Net

Current Module:
M0.2 — Integration test harness on real PostgreSQL  [MERGED to dev + main]

Status:
M0.2 merged (24b92c3) · branch structure changed to dev/main split · pushed to origin

Branch Structure (2026-07-04, owner directive):
  - main  = production-grade, deployment-connected. Only receives promotions
    from dev at integration checkpoints (CP-0…CP-6) when all available gates
    pass (unit, integration, lint, types, + performance/frontend/security
    as those gates are built in later waves).
  - dev   = sandbox, primary working branch. Module branches
    (refactor/m<x>-<slug>) branch off dev and merge to dev (owner-approved
    per module, same C2 discipline). This is where active work lives.
  - Promotion dev → main happens at integration checkpoints or on owner
    demand. See EXECUTION_PLAN_v1.md §4 and §14 for the updated protocol.

Worktree layout:
  - RinggitSense      (this directory) → on dev   [primary, where we work]
  - RinggitSense-prod (sibling)         → on main [promotion-only]

Remote: origin (renamed back from `main` to avoid branch-name ambiguity)

Baseline tag:
pre-refactor-baseline -> c83e2c6  (program-wide revert point, on main)

Completed modules:
  M0.1 — Baseline freeze & working agreements  [MERGED to main at e689d92]
  M0.2 — Integration test harness               [MERGED to main at 24b92c3]
  Both are on main AND dev (dev was branched from main after M0.2).

---

Completed (branch structure change, 2026-07-04):
- Remote renamed: main → origin (eliminates refname ambiguity)
- dev branch created off main (at 3b69e13, post-M0.2)
- dev pushed to origin with upstream tracking
- Prod worktree created: ../RinggitSense-prod on main (promotion-only)
- CI workflow updated: triggers on push/PR to both main and dev
- EXECUTION_PLAN_v1.md updated: C2, §4 execution protocol, §14 quality gates,
  new §4.1 branch structure documentation
- refactor-baseline.md updated: working agreement #1 reflects dev/main split
- CURRENT_MODULE_STATE.md updated (this file)

Verification (local, 2026-07-04):
- git worktree list: two worktrees confirmed (dev + main)
- git remote -v: origin (no ambiguity)
- pytest tests/: 263 passed, 4 skipped, 90.42% coverage (unchanged)
- ruff check . : All checks passed!
- git status: clean on dev

Next Action:
- Branch structure change is complete. Next module is M0.3 (E2E pipeline test
  + amount-sign contract tests), to be branched off dev and merged to dev.
- Do NOT begin M0.3 until the owner explicitly says go.

---

Verification commands (backend venv is at backend/venv, Python 3.14 locally):
  cd backend && ./venv/Scripts/python.exe -m pytest tests/ -q      # 263 passed, 4 skipped
  cd backend && ./venv/Scripts/ruff.exe check .                    # clean
  # NOTE: run mypy in CI, not locally — local mypy exits 1 with no output (M2.3 fixes)
  # NOTE: integration tests auto-skip locally (TEST_DATABASE_URL unset per C1)

Next module on deck (await owner go-ahead):
  M0.3 — E2E pipeline test + amount-sign contract tests
  Branch: refactor/m0.3-e2e-pipeline-tests (off dev, merges to dev)
  Files: backend/tests/integration/test_upload_pipeline_e2e.py,
         backend/tests/integration/test_amount_contract.py,
         docs/CONVENTIONS.md
  Acceptance: E2E green with today's behavior (xfails aside); convention doc reviewed.
  Gains: the regression net for E3, E4, E5, E6 — highest-leverage artifact in the program.

Next promotion on deck (after M0.3 merges to dev):
  CP-0: dev → main promotion (Wave 0 complete)
  Gates at CP-0: unit (263+), integration (CI green), lint (ruff), types (CI mypy)
