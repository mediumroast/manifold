<!--
  Checker fixture for tests/live/plan_check.py. An excerpt of a "before" test plan
  (Claude Code, bundle 0.2.0, Sonnet, prompt "Plan local tests for docs/plans/PHASE_1_PLAN.md.").
  It is not a copy of that plan and it is not a plan to follow.
-->
# PHASE_1_TEST_PLAN.md

## Purpose

This plan certifies Phase 1 (security baseline and local installer) complete. "Passing" means every person, agent and service authenticates with its own principal and credential; four roles and per-component grants and denies govern access; revocation is immediate and durable; and the page tool cannot write outside its caller's scope, all verified by the gates below and by a human for the items that require a Linux host or specific client software.

## Source

**Phase plan:** `docs/plans/PHASE_1_PLAN.md`

**Tasks covered:**
- Task 2 — Add the security store
- Task 3 — Add the credential module
- Task 4 — Add the settings registry
- Task 5 — Add principals, roles, grants, denies and component state

**Tasks excluded:**
- Task 1 (`[~]`): native Linux probe not run, blocked on a Linux host. Covered by manual case M1.

## Test environment

**Verify command:** none (lint and type-check do not exist)
**Test command (server):** `cd server && ../.venv/bin/python -m pytest -q`

## Checkpoints

| Checkpoint | Phase-plan tasks | Gate (phase-plan Verification) |
|---|---|---|
| CP1 | T2 to T7 | `cd server && ../.venv/bin/python -m pytest -q` exits 0 on the new security-package tests (at least 100 new cases) |
| CP2 | T8 to T11 | Full server suite passes (at least 536 cases) |

## Manual test cases

### M1 — Linux SQLite bind-mount probe
**Checkpoint:** CP2
**Related task:** Task 1 from `PHASE_1_PLAN.md`
**Precondition:** A Linux host with Docker installed.
**Steps:**
1. Create a temporary bind-mount directory.
2. Run the probe with two containers simultaneously in `wal` mode, then in `delete` mode.
**Expected outcome:** `delete` mode: no lost writes and no lock errors.
**Pass criteria:** `delete` mode passes with no lost writes.
**Result:** [ ] Pass  [ ] Fail  [ ] Blocked
**Notes:**

---

## Automated test cases

### A1 — Store creates with correct modes, runs migrations, and refuses a wiki-root path
**Checkpoint:** CP1
**Related task:** Task 2 from `PHASE_1_PLAN.md`
**Precondition:** Temporary directory with no existing database.
**Action:** `cd server && ../.venv/bin/python -m pytest -q tests/test_security_store.py tests/test_store_locks.py`
**Expected outcome:** Exit 0. All cases pass, including: data folder mode 0700; database file mode 0600; refusal of a path inside the wiki root; refusal of a database newer than the code.
**Test file:** `server/tests/test_security_store.py`, `server/tests/test_store_locks.py`
**Todo:** [x]

---

### A2 — Credential issued, verified and revoked; secret never in database bytes
**Checkpoint:** CP1
**Related task:** Task 3 from `PHASE_1_PLAN.md`
**Precondition:** Fresh security store.
**Action:** `cd server && ../.venv/bin/python -m pytest -q tests/test_tokens.py`
**Expected outcome:** Exit 0. Cases include: the credential format; `verify` returns valid, revoked, expired or unknown correctly; the raw database file bytes do not contain the secret.
**Test file:** `server/tests/test_tokens.py`
**Todo:** [x]

---

### A3 — Settings defaults, override and out-of-range refusal; no off switch
**Checkpoint:** CP1
**Related task:** Task 4 from `PHASE_1_PLAN.md`
**Precondition:** Fresh security store.
**Action:** `cd server && ../.venv/bin/python -m pytest -q tests/test_settings.py`
**Expected outcome:** Exit 0. An out-of-range value is refused with the allowed range; no setting disables authentication.
**Test file:** `server/tests/test_settings.py`
**Todo:** [x]

---

### A4 — Principals, roles, grants, denies; admin refused for agent and service
**Checkpoint:** CP1
**Related task:** Task 5 from `PHASE_1_PLAN.md`
**Precondition:** Fresh security store.
**Action:** `cd server && ../.venv/bin/python -m pytest -q tests/test_principals.py`
**Expected outcome:** Exit 0. Cases include: admin role refused for agent and service kinds; a mutation is visible to a second connection.
**Test file:** `server/tests/test_principals.py`
**Todo:** [x]

---

## Quality gates (all must pass before the phase is certified complete)

- [ ] All manual test cases marked Pass by a human tester
- [ ] All automated tests passing (`cd server && ../.venv/bin/python -m pytest -q`)
- [ ] Summary signed off by tester below this line
