# PHASE_<N>_TEST_PLAN.md
**Approved by:** <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>
**Instructions:** read the whole test plan, then replace the whole slug above, brackets included, with your name and the date. An agent leaves it as it is; the test-coder will not start while it holds a slug.
<!--
  Template for the test-planner agent.
  Copy this file to docs/plans/PHASE_<N>_TEST_PLAN.md (same <N> as the phase
  plan), fill it in, and delete these comments before handing it to the
  test-coder. Every case cites a source: an intent line, a "Must never", a
  constraint, a plan acceptance line or "owner-confirmed". The plan judges the
  existing tests and adds only what is missing. Never invent acceptance criteria.
  **Approved by** is written by a human, never by an agent. Leave the slug as it is.
-->

## Purpose
<!--
  One paragraph. What phase this plan certifies and what "passing" means
  for this phase overall.
-->

## Source
**Phase plan:** `PHASE_<N>_PLAN.md`
**Tasks covered:**
- Task 1 — <title>
- Task 2 — <title>

**Tasks excluded:**
- <!-- List any [~] blocked tasks from the phase plan, with the reason -->

## Source intents
<!--
  Each originating intent named in the phase plan: id, status, and which scenario
  seeds, "Must never" lines and constraints apply. Read in full before the
  existing tests.
-->
- `INT-<n>` <title> (status: <status>). Seeds <S1, S2>; constraints <...>; Must never <...>.

## Coverage judgement
<!--
  One row per seed, "Must never" and constraint. Plan cases only for the thin
  and absent rows. Never copy an existing test as a case.
-->

| Seed or constraint | Existing test | Judgement (adequate, thin or absent) | Reason |
|---|---|---|---|
| <S1 ...> | <test id, or none> | <adequate / thin / absent> | <why> |

## Gaps found
<!--
  The gap cases (their ids), or "no gap found" followed by the evidence: what was
  read and which seeds and constraints were checked. No quota of new cases.
-->
- <A1, M1: what each covers>

## Test environment
**Verify command:** `<verify command>`
**Test command:** `<test command>`
**Environment variables / fixtures required:**
-

**Seed and sample size:** <!-- Only if a check samples data or uses randomness. Fix both so reruns are comparable. Otherwise write "not applicable". -->

## Checkpoints
<!--
  These checkpoints mirror the phase plan's: one row per checkpoint of PHASE_<N>_PLAN.md,
  with its tasks and its Verification line as the gate. The test-coder implements one
  checkpoint at a time and stops after each.
  A phase plan without checkpoints is one checkpoint (CP1).
-->

| Checkpoint | Phase-plan tasks | Gate (the phase checkpoint's Verification) |
|---|---|---|
| CP1 | Task 1, Task 2 | |

## Manual test cases
<!-- Cases that need human judgment. Order: task order from the phase plan. -->

### M1 — <short title>
**Checkpoint:** CP<n>
**Related task:** Task N from `PHASE_<N>_PLAN.md`
**Derived from:** <an intent line, a "Must never", a constraint, a plan acceptance line or "owner-confirmed"; with no source write "Unconfirmed: owner to confirm", which counts as neither pass nor fail>
**Existing or new:** <new, or extends <existing test id>; a case that only repeats an existing test is not written>
**Precondition:** Exact state the system must be in before starting.
**Steps:**
1.
**Expected outcome:** Exactly what should be observed.
**Pass criteria:** Unambiguous statement of what "pass" looks like.
**Result:** [ ] Pass  [ ] Fail  [ ] Blocked
**Notes:** (tester fills in)

---

## Automated test cases
<!--
  Cases the test-coder implements. Order: task order. REGRESSION cases go last,
  labeled. Every secured endpoint or function needs an unauthenticated case
  and, where roles exist, an insufficient-permission case. Leave every Todo
  unticked: the test-coder ticks a case when its check is written and run.
-->

### A1 — <short title>
**Checkpoint:** CP<n>
**Related task:** Task N from `PHASE_<N>_PLAN.md`
**Derived from:** <an intent line, a "Must never", a constraint, a plan acceptance line or "owner-confirmed">
**Existing or new:** <new, or extends <existing test id>>
**Precondition:** System state and any fixtures or mocks required.
**Action:** Exact operation or sequence to execute.
**Expected outcome:** The specific result, state or output that constitutes a pass.
**Test file:** `<path/to/test_file>` (where this test will live)
**Todo:** [ ]

---

<!-- Copy the case blocks above for each additional case. Cross-reference a manual and an automated case that cover the same condition. -->

## Questions for the human
<!--
  Each question the planner could not decide or could not source an expected result
  for. The test-coder stops while a blocking question has an empty Answer. If there
  is nothing to ask, replace the entries with one line: "No questions because <reason>".
-->

### Q1 — <question>
**Blocking:** <yes or no>
**Answer:**

## Quality gates (all must pass before the phase is certified complete)
- [ ] All manual test cases marked Pass by a human tester
- [ ] All automated tests passing (`<test command>`)
- [ ] `<verify command>` passes clean
- [ ] No [~] blocked test cases outstanding without a documented reason
- [ ] No blocking question is open
- [ ] **Approved by** is filled in by a human before the test-coder starts
- [ ] Summary signed off by tester below this line

<!-- tester: add sign-off and date here -->
<!-- test-coder: add automation run summary here (files written, new fixtures, anything not run) -->
