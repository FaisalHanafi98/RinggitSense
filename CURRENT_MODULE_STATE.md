# CURRENT_MODULE_STATE

> Living engineering state file. Overwrite this in place as execution advances.
> Not a summary — the single source of truth for "where are we right now."
> Last updated: 2026-07-04 (CP-0 promoted, Wave 0 complete, starting Wave 1)

---

Current Program:
Audit remediation & production-readiness refactor
(basis: docs/plans/EXECUTION_PLAN_v1.md)

Current Wave:
Wave 1 — Correctness + Hygiene

Current Epic:
E1 — Correctness Hotfixes

Current Module:
M1.1 — Dashboard metrics correctness (sign fix + window honesty)  [STARTING]

Branch Structure:
  main  = production-grade, deployment-connected (promotion-only)
  dev   = sandbox, primary working branch (module branches merge here)
  Remote: origin
  Worktree: RinggitSense/ on dev, RinggitSense-prod/ on main

Baseline tag:
pre-refactor-baseline -> c83e2c6  (program-wide revert point, on main)

Completed modules:
  M0.1 — Baseline freeze & working agreements  [MERGED]
  M0.2 — Integration test harness               [MERGED]
  M0.3 — E2E pipeline + sign contract tests     [MERGED]
  CP-0: dev → main promotion (Wave 0 complete)  [PROMOTED 1787d10]

  All on main (pushed to origin) and dev.

---

CP-0 Promotion (2026-07-04):
- Wave 0 (E0 — Regression Safety Net) complete
- dev → main merged at 1787d10 (--no-ff), pushed to origin
- Gates at CP-0: unit (263 passed, 90.42%), integration (17 CI pending),
  lint (ruff clean), types (CI mypy)
- main and dev are at parity

Next Action:
- Begin Wave 1: M1.1 — Dashboard metrics correctness
- Fix B1 (income/spending inverted) + B4 interim (200-row window label)
- Branch: refactor/m1.1-dashboard-correctness (off dev, merges to dev)

---

Verification commands (backend venv is at backend/venv, Python 3.14 locally):
  cd backend && ./venv/Scripts/python.exe -m pytest tests/ -q      # 263 passed, 17 skipped
  cd backend && ./venv/Scripts/ruff.exe check .                    # clean
  # NOTE: run mypy in CI, not locally — local mypy exits 1 with no output (M2.3 fixes)
  # NOTE: integration tests auto-skip locally (TEST_DATABASE_URL unset per C1)

Wave 1 modules on deck (small, independent, low risk):
  M1.1 — Dashboard metrics correctness (fix B1 + B4 interim) — STARTING
  M1.2 — Credit-safe deduplication (fix B2, flip M0.3 xfails)
  M1.3 — Compliance copy correction (fix B3)
  M2.1 — Config single-source
  M2.3 — Dependency & runtime pinning (uv, restore local mypy)
  M2.4 — Structured logging baseline
