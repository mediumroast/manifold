# PHASE_9_TEST_PLAN.md
**Approved by:**

<!-- Checker fixture for tests/live/plan_check.py: a test plan written by hand to the new template, with an invented intent (INT-99). It is not a real plan, and plan_check must report nothing on it. -->

## Purpose
This plan certifies Phase 9 (an invented export feature, used only as a fixture) by adding the checks the builders' tests do not make. "Passing" means each gap check below fails when the behavior is wrong, no blocking question is open, and a human has written **Approved by**.

## Source
**Phase plan:** `docs/plans/PHASE_9_PLAN.md`
**Tasks covered:**
- Task 1 — Add the export command

**Tasks excluded:**
- none

## Source intents
- `INT-99` Export a wiki to a file (status: accepted). Seeds S1 (export writes one file) and S2 (export refuses an existing file); constraint "never overwrite a file silently"; Must never "export a page the caller cannot read".

## Coverage judgement

| Seed or constraint | Existing test | Judgement | Reason |
|---|---|---|---|
| S1 export writes one file | `tests/test_export.py::test_writes_file` | adequate | asserts the file exists and holds every page |
| S2 export refuses an existing file | none | absent | no test calls export twice on the same target |
| constraint: never overwrite silently | `tests/test_export.py::test_overwrite` | thin | asserts the error text, not that the file is unchanged |
| Must never: export an unreadable page | none | absent | no test uses a caller with a denied component |

## Gaps found
- A1 covers S2 and the overwrite constraint (absent and thin).
- M1 covers the unreadable-page Must never as a manual check until a fixture exists.

## Test environment
**Verify command:** none
**Test command:** `.venv/bin/python -m pytest -q`

**Seed and sample size:** not applicable

## Checkpoints

| Checkpoint | Phase-plan tasks | Gate (the phase checkpoint's Verification) |
|---|---|---|
| CP1 | Task 1 | `.venv/bin/python -m pytest -q` passes |

## Manual test cases

### M1 — Export skips nothing the caller may not read
**Checkpoint:** CP1
**Related task:** Task 1 from `PHASE_9_PLAN.md`
**Derived from:** Unconfirmed: owner to confirm
**Existing or new:** new
**Precondition:** An instance with one component the caller is denied.
**Steps:**
1. Run the export as the denied caller.
**Expected outcome:** The file holds no page of the denied component.
**Pass criteria:** The file holds no page of the denied component.
**Result:** [ ] Pass  [ ] Fail  [ ] Blocked
**Notes:** Counts as neither pass nor fail until the owner confirms the expected result (Q1).

---

## Automated test cases

### A1 — A second export to the same target leaves the first file unchanged
**Checkpoint:** CP1
**Related task:** Task 1 from `PHASE_9_PLAN.md`
**Derived from:** INT-99 S2 and the constraint "never overwrite a file silently"
**Existing or new:** extends `tests/test_export.py::test_overwrite`
**Precondition:** A temporary folder holding one export file.
**Action:** Run the export a second time to the same target.
**Expected outcome:** The command refuses with a non-zero exit and the file's bytes are identical to before.
**Test file:** `tests/test_export.py`
**Todo:** [ ]

---

## Questions for the human

### Q1 — Which pages may a denied caller see in an export?
**Blocking:** yes
**Answer:**

## Quality gates (all must pass before the phase is certified complete)
- [ ] All manual test cases marked Pass by a human tester
- [ ] All automated tests passing (`.venv/bin/python -m pytest -q`)
- [ ] No verify command exists (noted)
- [ ] No [~] blocked test cases outstanding without a documented reason
- [ ] No blocking question is open
- [ ] **Approved by** is filled in by a human before the test-coder starts
- [ ] Summary signed off by tester below this line
