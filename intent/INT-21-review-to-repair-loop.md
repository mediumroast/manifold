---
id: INT-21
title: A written review-to-repair loop with checkpoints
author: Michael Hay
created: 2026-11-02
status: draft
affects: [bundles/base]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: A written review-to-repair loop with checkpoints

## Problem
The first real full cycle ran on draft PR #27 (Phase 1 security baseline): plan -> coder -> reviewer -> planner amendment -> coder. It worked, but the middle of it was improvised.

- The `reviewer` produced its findings only as a chat report. The report has no home in the repository, so what was found, how it was checked and what could not be checked is lost once the conversation ends.
- The `planner` was given that report by pasting it, and amended `PHASE_1_PLAN.md` with repair tasks by hand. Nothing says what the amendment must contain, how a repair task points back to the finding it answers, or where open questions go.
- Nothing encodes the steps between: who approves the amended plan before the `coder` runs again, and that the repair is reviewed again.
- The plan already grouped its tasks into checkpoints (CP1-CP6), but only informally. The `planner` and `coder` definitions do not mention checkpoints, so the coder reported and stopped on whatever boundary it chose, and the plan template has no place for them.

The owner's observation is the core of this intent: **producing and consuming the review output was ad hoc, with no encoded procedure.** A cycle that depends on whoever is coordinating remembering the steps will drift, and the next one will not be comparable to this one.

## Proposed outcome
1. **A review is a document.** The `reviewer` writes `REVIEW_PLAN_X.md` (X is the phase number, next to `PHASE_X_PLAN.md`) from the review template. It holds the findings by pass and severity with their evidence, counts, what was reviewed (commit, plan version), and what the reviewer could not check. The chat report is a short pointer to it.
2. **The planner consumes that document.** Given `REVIEW_PLAN_X.md`, the `planner` amends the matching `PHASE_X_PLAN.md`: it adds repair tasks, each tracing to the finding it answers; records findings it does not repair and why; and lists open questions for the human. It does not change completed tasks or the original acceptance lines, and it never approves its own amendment.
3. **The loop is encoded, not remembered.** One written procedure covers the whole sequence: review -> `REVIEW_PLAN_X.md` -> planner amendment -> human approval -> coder -> re-review, with who does each step, what it produces and what condition ends the loop (for example, no open Important finding, or the human accepts the remainder explicitly). The procedure lives in the bundle, so any installed repository gets the same loop.
4. **Work is grouped into checkpoints.** The `planner` groups tasks into numbered checkpoints (CP1, CP2, ...) that each end in something verifiable, and the plan template carries the checkpoint structure. The `coder` executes checkpoint by checkpoint: finishes and verifies one, reports, and stops before the next unless told otherwise. Repair tasks added by an amendment form their own checkpoint(s).
5. **The same, for both flavors.** The `claude` agents and the `copilot` agents carry the same procedure, the same document names and the same checkpoint behavior.
6. **The procedure answers two sets of questions in writing**, below.

### How a review is handled
The written procedure states, for each point, who and where:
- **Who runs it, and in which session.** The `reviewer` runs in its own session, not the session of the agent that wrote the change (the coordinator of INT-22 starts it, or the owner does when there is none).
- **What it reads.** The change (diff, branch or PR), the approved `PHASE_X_PLAN.md` with its completion notes, the intent, the review policy (see INT-23 for whether that is a `REVIEW.md`), and the `coder`'s "Rule exceptions" line (INT-20).
- **Where the output goes.** `REVIEW_PLAN_X.md`, next to the plan.
- **Who consumes it.** The `planner`, which amends the plan; the owner, who decides what to repair, defer or reject; the coordinator, which checks it before a PR is marked ready.
- **How findings become plan tasks.** Each Important finding to be repaired becomes a repair task in its own checkpoint, tracing back to the finding. Nits and deferred items are listed with a reason, not turned into tasks unless the owner asks.
- **What stops a PR from being checked in before one review cycle.** A PR is not marked ready, and not merged, until a review of the final change exists, its findings are repaired, deferred or rejected, and a human has said so (the coordinator enforces this; see INT-22).
- **How repeat cycles end.** A cycle ends when the re-review has no open Important finding, or the owner accepts the remainder in writing. A limit on rounds is an open question.

### How tests are handled
The same procedure states:
- **Who writes tests.** The `coder` writes the local unit and integration checks alongside the code (the `bug-coder` writes a regression test). The independent `test-planner` and `test-coder`, and the quality side's behavior scenarios, are separate: the coder's checks are not a substitute for them, and the coder neither writes nor reads held-out scenarios.
- **Failing-first evidence.** A fix has a regression test that is shown failing before the fix and passing after. The command and both results are recorded in the task's completion note, so the reviewer can reproduce them.
- **A fix that breaks a test pinning the old behavior.** The rule is not to edit a test to make it pass. When a fix legitimately changes behavior that an existing test pinned, the coder stops, names the test and the assertion, explains why the old expectation is wrong, and asks the owner. It edits the test only after the owner approves, and records the approval and the change (this cycle: one assertion changed with the owner's approval). The reviewer flags any such change and checks that an approval is recorded.
- **How gates are run and reported.** The project's gates (for this repository: the server suite, the bundle tests and the vendored-files check) are run by the coder at each checkpoint and by the reviewer to confirm; each result is reported with the command and the real output (pass counts, not "passed"). A gate that could not be run is reported as not run, with the reason.
- **Who confirms CI on a pushed commit.** The coordinator checks the hosted CI result on the pushed commit and reports it; a human confirms it before the PR is marked ready. A red or missing CI result is a finding, not a note.

## Affected users and systems
- **The owner** who approves plans and decides what to do with review findings.
- **The agents:** `reviewer` (writes `REVIEW_PLAN_X.md`), `planner` (reads it, amends the plan, groups tasks into checkpoints), `coder` (executes by checkpoint; its test-side siblings `test-planner` and `test-coder` need a check for whether checkpoints apply to them).
- **The coordinating agent** (INT-22), which will run the procedure.
- **Bundle contents:** `bundles/base/agents/{reviewer,planner,coder}.agent.md`, `bundles/base/templates/REVIEW_TEMPLATE.md` (and a possible `REVIEW_PLAN_TEMPLATE.md` if the repository-level review policy and the per-phase report need separate templates), `PHASE_PLAN_TEMPLATE.md`, the rules in `bundles/base/rules/core/`, `bundles/base/tools/build.py`, `install.py`, `bundles/base/tests/`, and the bundle documentation.
- **Both agent flavors** (`.claude/agents/` and `.github/agents/`).
- **Repositories that install the bundle**, which receive the new documents and procedure.

## Constraints
- **Both flavors.** Every change applies to the `claude` and the `copilot` flavors, built from the same canonical sources by `build.py`. A change that only lands in one is not done.
- **Not in PR #27.** None of this goes into draft PR #27 or onto branch `claude/sub-agents-access-e9e255`. PR #27 may be repaired by the loop once it exists, but that is a separate action.
- **The reviewer stays read-only.** It writes the review document, which is a new file, and nothing else. Today it has no edit tool and never edits (its role says so); how it may write exactly one file without becoming able to edit code is an open question, not something to settle by loosening the rule silently.
- **A human approves.** The planner never marks an amended plan approved or fills in **Approved by**; the reviewer never approves or blocks; a human accepts the end of the loop. The existing rules (`approved-plan-before-execution`, `human-confirms-closure`, `plan-means-stop`) still hold.
- **Review is independent.** The agent that wrote the change does not review it, and the reviewer does not read held-out behavior scenarios.
- **Traceability.** Every repair task names the finding it answers (document, pass, id), and every finding ends the loop in one of three states: repaired, deferred with a reason, or rejected with a reason.
- **Concise artifacts.** The review document and the amendment follow the "plans stay concise" rule: link to evidence instead of restating it.
- **No change to completed history.** An amendment adds to the plan. Tasks already checked off keep their completion notes.
- **Deterministic build and standard library only**, as for the rest of the bundle.
- **Compatibility.** Plans and reviews written before this change stay valid input; a plan without checkpoints is still executable (treated as one checkpoint) and a review without a `REVIEW_PLAN_X.md` is still readable.

## Scenario seeds

### S1 — A review leaves a document behind
**Who:** The owner, after the `reviewer` has run on a phase.
**Wants:** The review findings in the repository, not only in chat.
**So that:** Anyone can read what was found and what was checked, later, without the conversation.
**We will know when:** A `REVIEW_PLAN_X.md` exists next to `PHASE_X_PLAN.md` and lists findings by pass and severity, each with a location and evidence; the counts by severity; the commit and plan version reviewed; and a "could not check" section. The chat reply points to the file.
**Must never:** Edit code or the plan, or say the change is approved or blocked.

### S2 — The planner turns findings into repair tasks
**Who:** The owner who gives the `planner` a `REVIEW_PLAN_X.md`.
**Wants:** The plan amended, not rewritten.
**So that:** Repairs are scoped, ordered and verifiable like any other task.
**We will know when:** `PHASE_X_PLAN.md` gains a repair checkpoint whose tasks each name the finding they answer and have an acceptance line; findings not repaired are listed with a reason; open questions for the human are listed; and completed tasks are untouched.
**Must never:** Silently drop a finding, fill in **Approved by**, or alter the original acceptance lines.

### S3 — The coder works one checkpoint at a time
**Who:** The `coder` executing a plan with checkpoints.
**Wants:** To finish and verify one checkpoint, report, and wait.
**So that:** The owner sees progress in verifiable steps and can redirect early.
**We will know when:** After each checkpoint the plan shows its tasks checked off with evidence, the report names the checkpoint, and the coder has not started the next one without being asked. A plan with no checkpoints runs as one.
**Must never:** Run past a checkpoint boundary on its own, or check off a task without evidence.

### S4 — The planner groups tasks into checkpoints
**Who:** The `planner` writing a new plan.
**Wants:** Logical groups of tasks, each ending in something that can be checked.
**So that:** The coder and the reviewer have natural stopping points.
**We will know when:** The plan has numbered checkpoints, each with the tasks in it and a verification at its end, and the task ordering still follows dependency.
**Must never:** Put tasks into a checkpoint in a way that breaks dependency order, or leave a task outside every checkpoint.

### S5 — The loop is a written procedure
**Who:** Whoever runs a cycle (the coordinating agent or a person).
**Wants:** The steps and the stop condition written down.
**So that:** The next cycle is run the same way as this one, and is comparable.
**We will know when:** One document in the bundle lists review -> `REVIEW_PLAN_X.md` -> planner amendment -> human approval -> coder -> re-review, with who does each step, what each produces and the condition that ends the loop; and both agent flavors point to it.
**Must never:** Leave a step to be remembered, or let the coder run the repair before a human has approved the amended plan.

### S6 — The re-review checks the repairs
**Who:** The `reviewer`, after the repair checkpoint is done.
**Wants:** To confirm each finding was dealt with.
**So that:** The loop ends on evidence.
**We will know when:** The review document is updated or a new revision is written, shows each earlier finding as repaired, deferred or rejected with evidence, and lists any new findings.
**Must never:** Close a finding without evidence, or be the same agent that made the repair.

### S7 — Both flavors behave the same
**Who:** A maintainer installing the bundle for Claude Code and for GitHub Copilot.
**Wants:** The same loop in both.
**So that:** The process does not depend on the client.
**We will know when:** The built `.claude/agents/` and `.github/agents/` outputs both contain the review document step, the amendment step and the checkpoint behavior, and the bundle's tests check this.
**Must never:** Ship the change to one flavor only.

### S8 — Everyone can see how a review is handled
**Who:** A maintainer or agent about to start a review cycle.
**Wants:** To know who runs the review, what it reads, where the output goes, who consumes it and what ends the cycle.
**So that:** The cycle does not depend on someone remembering.
**We will know when:** The written procedure answers each of those points in a place both flavors point to, and a cycle run by following it produces `REVIEW_PLAN_X.md`, an amended plan and a re-review without any step improvised.
**Must never:** Leave "who runs the review" or "when does it end" to the person in the room, or let the writer of a change run its review.

### S9 — A fix shows its failing-first test
**Who:** The reviewer checking a bug fix.
**Wants:** Evidence that the regression test failed before the fix.
**So that:** The test is known to catch the bug.
**We will know when:** The completion note has the command, the failing result before and the passing result after, and the reviewer reproduces both.
**Must never:** Accept a regression test with no recorded failing run.

### S10 — A fix breaks a test that pinned the old behavior
**Who:** The `coder`, whose fix makes an existing test fail.
**Wants:** To change that test legitimately.
**So that:** The rule against editing a test to make it pass stays meaningful.
**We will know when:** The coder stops and asks the owner, naming the test and assertion and why the old expectation is wrong; the test is edited only after a yes; the plan notes the owner's approval; and the reviewer lists the change and finds the approval.
**Must never:** Edit the test first and report afterwards, or change the assertion without a recorded approval.

### S11 — Gates are run and reported with their real results
**Who:** The owner reading a checkpoint report.
**Wants:** To see which gates ran and what they said.
**So that:** "Tests pass" can be trusted.
**We will know when:** Each checkpoint report lists the server suite, the bundle tests and the vendored-files check with the command, the counts and the result, and names any gate not run with a reason.
**Must never:** Claim a gate passed that was not run, or report only "all green".

### S12 — CI on the pushed commit is confirmed
**Who:** The owner before a PR is marked ready.
**Wants:** The hosted CI result for the pushed commit.
**So that:** A local pass is not mistaken for a pass where it counts.
**We will know when:** The coordinator reports the CI status for the exact commit, and a human confirms it before the PR leaves draft.
**Must never:** Treat a CI run on an older commit as the result for the pushed one.

## Out of scope
- The coordinator agent itself (INT-22), the hook-level enforcement and the breach record (INT-20).
- A tool or script that parses `REVIEW_PLAN_X.md` automatically.
- Changing the review passes or what counts as Important in the template, except where needed to add the document's fields.
- Applying the loop to PR #27 or to any plan other than as the first user of the procedure.
- Test-side agents' own review loop (`test-planner`, `test-coder`), unless the owner asks.

## Open questions
- How does the `reviewer`, which has no edit tool, write `REVIEW_PLAN_X.md`? Options: allow `edit` with a rule limited to that one file; or have the coordinator or a human save the report. (the product owner)
- Is `REVIEW_PLAN_X.md` a revision-in-place across re-reviews or a new file each time (`REVIEW_PLAN_X.1.md`)? (the product owner)
- Does the review template (the repository's policy, becomes `REVIEW.md`) stay as is, with a separate `REVIEW_PLAN_TEMPLATE.md` for the per-phase document? (the product owner)
- What ends the loop: no open Important findings, or a named human decision? And is there a maximum number of rounds? (the product owner)
- Does the planner amend the plan file in place, or write an addendum section? The ask says amend; confirm that completed tasks must stay untouched. (the product owner)
- Should the checkpoints apply to bug fixes and to the test-side agents? (the product owner)
- Whether the review policy stays a `REVIEW.md`, is folded into this procedure, or is dropped is decided in INT-23. Until then the procedure reads `REVIEW.md` if present and uses built-in defaults if not. (the product owner)
- Is there a maximum number of review rounds before the owner must decide? (the product owner)
- Who edits an existing test when the owner approves the change: the `coder` itself, or a separate step? (the product owner)
- Does the coordinator check CI itself (needs read access to the host) or ask a human to report it? (the product owner)
- Which checkpoint size is right (a rule of thumb such as "at most N tasks" or "ends in a demonstrable result")? (the product owner)
