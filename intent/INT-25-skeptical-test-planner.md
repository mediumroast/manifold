---
id: INT-25
title: A skeptical test planner: independent gap checks where there is no quality repository
author: Michael Hay
created: 2026-11-08
status: accepted
affects: [bundle, agents]
drafted_with: [claude-sonnet-5-5]
accepted_by: Michael Hay on November 8, 2026
---

# Intent: A skeptical test planner: independent gap checks where there is no quality repository

## Problem
Given `Plan local tests for docs/plans/PHASE_1_PLAN.md.` on a repository where Phase 1 was already implemented and tested, the `test-planner` in both flavors (Copilot with Sonnet 4.6, Claude Code with bundle 0.2.0 and Sonnet) did the same thing. It mapped each acceptance line to a test that already existed and wrote 45 automated cases, every one pre-ticked `[x]`, plus 3 or 6 manual cases. It cited no intent and asked no substantive question. The `test-coder` would have had nothing to do. The result looks like testing and finds nothing.

The cause is in the bundle text, not the model:
- the rule `derive-tests-from-plan`: "Test cases come from the phase plan's objective, file inventory and acceptance lines";
- "so you do not duplicate coverage" in the `test-planner` definition;
- the intent is not an input of the `test-planner`;
- the `test-coder` does "Only what the plan says".

A test plan derived from the plan, by the agents that built it, can only confirm what they already believed. [INT-21](INT-21-review-to-repair-loop.md) says the coder's checks are not a substitute for the independent test agents, but gives no mechanism and puts the test-side agents out of scope.

## Proposed outcome
A pseudo hold-out for repositories that have no separate quality repository. Tests written by the planner, the coder and the reviewer are assumed insufficient, and the test side is asked to look for what they missed.

1. **The test-planner reads the originating intent(s) and the plan,** and looks for gaps before it reads the existing tests.
2. **It judges the existing tests,** per scenario seed and per constraint: adequate, thin or absent, each with a reason. It does not copy them into the plan as cases.
3. **It plans only added cases:** automated "gap checks" (local, integration-level checks, not behavior scenarios and not an acceptance suite) and manual checks. No quota: if it finds no gap it says "no gap found" with the evidence, in chat and in the test plan, and asks the human.
4. **The test plan asks questions.** A "Questions for the human" section holds each question with a `Blocking` flag and an `Answer:` line. It carries an **Approved by** line that a human fills in.
5. **The test-coder tries to make the new checks fail.** It starts only when the plan is approved and no blocking question is open. A failing check is a defect found: it stays red and goes to the `bug-coder`, through the human or the coordinator.
6. **The reviewer checks a test plan for reflection:** no intent cited, every case pre-ticked, no gaps, no questions.
7. **Both flavors, one source,** concise.

## Affected users and systems
- **The owner** who approves test plans and answers their questions.
- **The agents:** `test-planner`, `test-coder`, `reviewer` (reflection check), and the hand-off to `bug-coder`.
- **Bundle contents:** the agent definitions, the rule `derive-tests-from-plan`, `docs/templates/PHASE_TEST_PLAN_TEMPLATE.md`, the bundle tests, and the bundle documentation.
- **Both agent flavors** (`.claude/agents/` and `.github/agents/`), built from the same canonical sources.
- **Repositories that install the bundle** and have no quality repository.

## Constraints
Owner decisions of 2026-11-08:
- **Intents may be read; held-out scenarios may not.** The pseudo hold-out applies only where no quality repository exists. It never replaces held-out scenarios.
- **Every case cites a source:** an intent line, a "Must never", a constraint, a plan acceptance line, or "owner-confirmed". A manual case with no source is marked "Unconfirmed: owner to confirm" and counts as neither pass nor fail.
- **No quota** of new tests.
- **Questions block.** A "Questions for the human" section with a `Blocking` flag and an `Answer:` line; the `test-coder` stops while a blocking question is open.
- **A human approves.** The test plan carries an **Approved by** line written by a human, never an agent. The `test-coder` checks it before starting.
- **Failing checks stay red.** A red suite is acceptable on a branch. The owner may later decide a test is not worth the effort and remove it; that is recorded as a decision, never skipped or weakened silently. The rule "Tests under fix" stays.
- **Expected values come from intents, plans and public documentation.** The `test-coder` may read implementation source for call shape and fixtures only.
- **Both flavors from one source.** Concise artifacts.

### Planning exception (INT-25 only)
By the owner's decision of 2026-11-08, INT-25 is planned inside Phase 2 (`docs/plans/PHASE_2_PLAN.md`), not in its own phase plan. Phase 2 exists to make the agents reasonably functional, and a separate phase is "attractive to follow but not practical". What changes: Phase 2's source-intent list, its traceability table (T43) and its completion checklist gain INT-25, and the new work is added as Phase 2 checkpoints that carry their own amendment approval line for the owner. This exception applies to INT-25 only; other intents keep their own phase plans.

## Scenario seeds

### S1 — A reflected plan is refused
**Who:** The reviewer, or the owner, reading a test plan.
**Wants:** To tell a test plan that only mirrors the existing tests from one that tests.
**So that:** Confirmation is not mistaken for coverage.
**We will know when:** A check names every reflection sign (no intent cited, every case pre-ticked, no gaps, no questions) and a test plan showing them is sent back.
**Must never:** Mark a case done because a test already exists.

### S2 — The intent drives the cases
**Who:** The `test-planner`.
**Wants:** To derive new cases from the intent as well as the plan.
**So that:** The cases test what was asked for, not what was built.
**We will know when:** Each new case names its source (intent line, "Must never", constraint, plan acceptance line or "owner-confirmed").
**Must never:** State an expected result that has no source.

### S3 — Existing tests are judged, not repeated
**Who:** The `test-planner`.
**Wants:** To say how well the existing tests cover each seed and constraint.
**So that:** The human sees where the thin spots are.
**We will know when:** The test plan lists each seed and constraint as adequate, thin or absent, with a reason, and plans cases only for the thin and absent ones.
**Must never:** Copy an existing test as a new case.

### S4 — A stuck planner asks
**Who:** The `test-planner`, when it finds nothing to add or cannot decide.
**Wants:** To ask the human rather than pad.
**So that:** The test plan is honest about what was and was not found.
**We will know when:** The planner asks in chat and in the "Questions for the human" section, and states "no gap found" with evidence where that is the case.
**Must never:** Pad the plan with filler cases, or hand off with a blocking question open.

### S5 — A skeptical check can fail and the failure is kept
**Who:** The `test-coder`.
**Wants:** To write each new check to find a defect.
**So that:** A real gap shows up as a red check.
**We will know when:** A check that fails stays in the suite, is reported as a defect found, and goes to the `bug-coder` through the human or the coordinator.
**Must never:** Skip, weaken or delete the check, or change production code to make it pass.

### S6 — Manual cases a person can run and judge
**Who:** A person running the manual cases.
**Wants:** Steps and an expected result that can be followed and judged.
**So that:** The result means something.
**We will know when:** Each manual case has steps, an expected result and a source, or is marked "Unconfirmed: owner to confirm".
**Must never:** Count an unconfirmed case as a pass or a fail.

### S7 — A quality repository still wins
**Who:** A team that has a separate quality repository.
**Wants:** The held-out scenarios to stay the independent check.
**So that:** The pseudo hold-out does not weaken the real one.
**We will know when:** Where a quality repository exists, the `test-planner` works in its existing mode and the pseudo hold-out is not used.
**Must never:** Read or replace held-out scenarios.

### S8 — The same text in both flavors, and the reviewer checks it
**Who:** A maintainer installing the bundle for Claude Code and for GitHub Copilot.
**Wants:** The same behavior in both, and a check on the test plan.
**So that:** The process does not depend on the client or on the planner's own judgment.
**We will know when:** The built `.claude/agents/` and `.github/agents/` outputs carry the same text, the bundle tests check it, and the reviewer reports the reflection signs it finds in a test plan.
**Must never:** Let the reviewer approve a test plan.

## Out of scope
- Writing held-out scenarios.
- A test-side review loop beyond the reflection check.
- Per-agent model choice.
- Keeping the Phase 1 gap tests or the plans from the comparison runs. They are throw-away and serve as "before" evidence only.

## Open questions
- Which model or effort is recommended for the `test-planner`? (the owner, after the "after" run)
- How does the reflection check fit the reviewer's four passes, given that INT-21 says "no new pass"? (the owner) Answer: I need more details place them in the plan for review. This doesn't make sense to me as worded.

## Concerns flagged
None.
