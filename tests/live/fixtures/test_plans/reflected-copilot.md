<!--
  Checker fixture for tests/live/plan_check.py. An excerpt of a "before" test plan
  (Copilot, Sonnet 4.6, prompt "Plan local tests for docs/plans/PHASE_1_PLAN.md.").
  It is not a copy of that plan and it is not a plan to follow.
-->
# PHASE_1_TEST_PLAN.md

## Purpose
This plan certifies Phase 1 (the Manifold security baseline and local installer) complete. "Passing" means: every automated case runs clean under the project's test commands, all three manual gates are signed off by a human tester, and no `[~]`-blocked item is outstanding without a documented reason. The coder's local run is necessary but not sufficient; a human must close M1 to M3 before the phase is certified.

## Source
**Phase plan:** `docs/plans/PHASE_1_PLAN.md`
**Tasks covered:** T2 to T33, T35, T37 to T58

**Tasks excluded:**
- **T1** `[~]`: native Linux SQLite probe not run (no Linux host); becomes M1.
- **T34** `[~]`: HTTPS TLS client connections not observed; becomes M2.

## Test environment
**Verify command:** none (no lint or type-check)
**Test command:**
- Server tests: `cd server && ../.venv/bin/python -m pytest -q`

## Checkpoints

| Checkpoint | Phase-plan tasks | Gate (phase checkpoint Verification) |
|---|---|---|
| CP1 | T2 to T7 | `pytest tests/test_security_store.py tests/test_tokens.py tests/test_settings.py` passes |
| CP2 | T8 to T11 | `pytest tests/test_path_policy.py tests/test_auth.py` passes |

## Manual test cases

### M1 — Linux SQLite probe (T1)
**Checkpoint:** CP2
**Related task:** Task 1 from `PHASE_1_PLAN.md`
**Precondition:** A Linux host with Docker installed.
**Steps:**
1. Create a temporary bind-mount directory.
2. Run the probe with two containers simultaneously in `wal` mode.
**Expected outcome:** `delete` mode: no lost writes and no lock errors for both tags.
**Pass criteria:** `delete` mode passes both tags with no lost writes or lock errors.
**Result:** [ ] Pass  [ ] Fail  [ ] Blocked
**Notes:**

---

## Automated test cases

### A1 — Security store: creation modes, migration and wiki-root refusal (T2)
**Checkpoint:** CP1
**Related task:** Task 2 from `PHASE_1_PLAN.md`
**Precondition:** Isolated temporary directory; no existing database.
**Action:** Call `open_store` with a fresh directory; re-call on the same directory; call with a path inside the wiki root.
**Expected outcome:** Directory created mode 0700, file created mode 0600; migration applied exactly once on re-open; a wiki-root path raises with a clear message.
**Test file:** `server/tests/test_security_store.py`
**Todo:** [x]

---

### A2 — Credential issue, verify and revoke; secret never in database bytes (T3)
**Checkpoint:** CP1
**Related task:** Task 3 from `PHASE_1_PLAN.md`
**Precondition:** Open security store in an isolated temporary directory.
**Action:** Issue a credential; verify it; revoke it; attempt to verify again; read the database file bytes raw.
**Expected outcome:** `verify` returns `valid` before revocation and `revoked` after; the raw database bytes do not contain the secret string.
**Test file:** `server/tests/test_tokens.py`
**Todo:** [x]

---

### A3 — Settings defaults, override and out-of-range refusal (T4)
**Checkpoint:** CP1
**Related task:** Task 4 from `PHASE_1_PLAN.md`
**Precondition:** Open security store.
**Action:** Read each setting without overriding it; set a setting within its allowed range; set a setting outside its range; set an unknown key.
**Expected outcome:** Defaults match plan values; an in-range override is stored and read back; out-of-range and unknown keys are refused with a message naming the allowed range.
**Test file:** `server/tests/test_settings.py`
**Todo:** [x]

---

### A4 — Principals, roles, grants and denies (T5)
**Checkpoint:** CP1
**Related task:** Task 5 from `PHASE_1_PLAN.md`
**Precondition:** Open security store.
**Action:** Create principals of each kind; grant and deny a component; ask the authorizer.
**Expected outcome:** Deny beats grant; the admin role is refused for an agent principal.
**Test file:** `server/tests/test_principals.py`
**Todo:** [x]

---

## Quality gates (all must pass before the phase is certified complete)
- [ ] All manual test cases marked Pass by a human tester
- [ ] All automated tests passing (`cd server && ../.venv/bin/python -m pytest -q`)
- [ ] Summary signed off by tester below this line
