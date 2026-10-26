# PHASE_<N>_TEST_PLAN.md
<!--
  Template for the test-planner agent.
  Copy this file to docs/plans/PHASE_<N>_TEST_PLAN.md (same <N> as the phase
  plan), fill it in, and delete these comments before handing it to the
  test-coder. Every case must come from the phase plan's objective, file
  inventory or acceptance lines. Never invent acceptance criteria.
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

## Test environment
**Verify command:** `<verify command>`
**Test command:** `<test command>`
**Environment variables / fixtures required:**
-

**Seed and sample size:** <!-- Only if a check samples data or uses randomness. Fix both so reruns are comparable. Otherwise write "not applicable". -->

## Manual test cases
<!-- Cases that need human judgment. Order: task order from the phase plan. -->

### M1 — <short title>
**Related task:** Task N from `PHASE_<N>_PLAN.md`
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
  labelled. Every secured endpoint or function needs an unauthenticated case
  and, where roles exist, an insufficient-permission case.
-->

### A1 — <short title>
**Related task:** Task N from `PHASE_<N>_PLAN.md`
**Precondition:** System state and any fixtures or mocks required.
**Action:** Exact operation or sequence to execute.
**Expected outcome:** The specific result, state or output that constitutes a pass.
**Test file:** `<path/to/test_file>` (where this test will live)
**Todo:** [ ]

---

<!-- Copy the case blocks above for each additional case. Cross-reference a manual and an automated case that cover the same condition. -->

## Quality gates (all must pass before the phase is certified complete)
- [ ] All manual test cases marked Pass by a human tester
- [ ] All automated tests passing (`<test command>`)
- [ ] `<verify command>` passes clean
- [ ] No [~] blocked test cases outstanding without a documented reason
- [ ] Summary signed off by tester below this line

<!-- tester: add sign-off and date here -->
<!-- test-coder: add automation run summary here (files written, new fixtures, anything not run) -->
