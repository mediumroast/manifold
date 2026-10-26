# PHASE_<N>_TEST_PLAN.md
<!--
  Template for the test-planner agent.
  Copy this file, rename it PHASE_<N>_TEST_PLAN.md, and delete
  these comments before handing to the test-coder for implementation.
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
- <!-- List any [~] blocked tasks from the phase plan with reason -->

## Test environment
**Verify command:** `<verify command>`
**Test command:** `<test command>`
**Environment variables / fixtures required:**
-

## Test cases

### T01 — <short title>
**Related task:** Task N from `PHASE_<N>_PLAN.md`
**Precondition:**
**Action:**
**Expected outcome:**
**Pass criteria:**
**Todo:** [ ]

---

### T02 — <short title>
**Related task:**
**Precondition:**
**Action:**
**Expected outcome:**
**Pass criteria:**
**Todo:** [ ]

---

<!-- Copy the test case block above for each additional test -->

## Quality gates
- [ ] All test cases passing
- [ ] `<verify command>` passes clean
- [ ] `<test command>` passes clean (no regressions)
- [ ] No [~] blocked test cases outstanding without documented reason
- [ ] Summary signed off below this line

<!-- add sign-off and date here -->
