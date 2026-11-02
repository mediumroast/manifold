---
id: INT-22
title: A coordinator agent that runs the cycle
author: Michael Hay
created: 2026-11-02
status: draft
affects: [bundles/base]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: A coordinator agent that runs the cycle

## Problem
In the first real cycle (draft PR #27, Phase 1 security baseline) a Claude session acted as coordinator: it started the reviewer, the planner and the coder, relayed their output to one another and to the owner, and decided when to move on. That role is not defined anywhere in the bundle. As a result:

- Its steps were improvised, and it cannot be told apart from "the user" in the record. It broke no written rule because it had none, which is itself the gap.
- Nothing makes it check that the agents stay inside their rules. Breaches by the `coder` and the `planner` were found afterwards, by hand.
- Nothing requires a review before a pull request is declared ready. The cycle happened to include one; the next may not.
- Every run teaches something about the process, but nothing collects those lessons. This intent, and INT-20 and INT-21, exist only because the owner asked.
- There is no common pull request structure, so each cycle describes its work differently.

## Proposed outcome
A `coordinator` agent in the base bundle that runs the cycle consistently and keeps improving it:

1. **It controls the work of the other agents.** It follows the written loop of INT-21 (review -> `REVIEW_PLAN_X.md` -> planner amendment -> human approval -> coder -> re-review), starts each agent with the inputs it needs, relays results, and stops where a human must decide. It does not do an agent's work itself: no code, no plan, no review.
2. **No PR leaves draft without a review.** At least one review cycle (a review of the final change by the `reviewer`, with `REVIEW_PLAN_X.md` written and its findings dealt with) must have happened before the coordinator marks a pull request ready for review or says it can be merged. It says so in the PR, and refuses to mark it ready otherwise. The human still decides to merge.
3. **A common PR structure.** The coordinator uses one pull request template that every cycle fills the same way (what and why, the plan and intent, checkpoints done, the review state and findings, rule exceptions, what could not be checked, follow-ups).
4. **It watches the guardrails.** It reads each agent's "Rule exceptions" and compares it with what the agent did. When an agent jumps a guardrail, the coordinator records it in the breach record (INT-20) by the written procedure, including its own breaches.
5. **It looks for process gaps after each run.** At the end of a run or iteration it asks what in the process was improvised, ambiguous or missing, and lists the gaps.
6. **It knows how to turn gaps into an improvement intent.** It drafts an intent from the gaps using the intent template, leaves it as draft, and hands it into the normal plan -> execute cycle so the improvement is built the same way as any other work. It never accepts the intent and never starts the work from it on its own.
7. **It exists in both flavors.** The `coordinator` is built for the `claude` and the `copilot` outputs (and installed in the profiles the owner chooses), with the same instructions.
8. **It carries out the review and test handling written in INT-21.** Its duties, in the coordinator's own instructions:
   - **Reviews:** start the `reviewer` in a separate session from the one that wrote the change, give it the change, the approved plan, the intent, the review policy and the coder's "Rule exceptions" line, and check that `REVIEW_PLAN_X.md` exists; pass it to the `planner`; stop for the owner's approval of the amended plan; then run the `coder` on the repair checkpoint(s) and the re-review. It tracks the rounds and stops the loop only under the end condition in INT-21.
   - **Ready check:** before a PR leaves draft, check that a review of the final commit exists, that each finding is repaired, deferred or rejected, that the hosted CI result for the pushed commit has been read and confirmed by a human, and that the review policy's approval rule (INT-23) is met.
   - **Tests:** check each fix has a recorded failing-first run; when a fix needs an existing test changed, stop and relay the coder's question to the owner, and carry the owner's yes into the plan; check each checkpoint report lists the project's gates with real results; keep the coder's local checks separate from the independent `test-planner`/`test-coder` and quality-side scenarios, and never pass held-out scenarios to builders.
   - **CI:** read the CI status of the exact pushed commit, report it, and treat red or missing as a finding.

This agent is an exception to the rule that process improvements do not go into PR #27: it is covered by this intent and ships through this intent's plan.

## Affected users and systems
- **The owner**, who gets a consistent cycle, a ready-state check and a process-improvement feed.
- **All agents** that the coordinator directs: `planner`, `coder`, `bug-coder`, `reviewer`, `test-planner`, `test-coder`, `scenario-writer`.
- **Bundle contents:** `bundles/base/agents/coordinator.agent.md` (new), a PR template under `bundles/base/templates/`, the rules in `bundles/base/rules/core/`, `ROLES` and `PROFILES` in `bundles/base/tools/build.py`, `install.py`, `bundles/base/tests/`, the README and INSTALL guides.
- **Both agent flavors** (`.claude/agents/` and `.github/agents/`).
- **Repositories that install the bundle**, which gain a coordinator and a PR template.
- **Pull requests** that use the template (for example, any later one from this repository).

## Constraints
- **Both flavors.** The coordinator and every change in this intent apply to the `claude` and the `copilot` flavors, from one canonical source.
- **Not in PR #27.** Nothing here lands in draft PR #27 or on branch `claude/sub-agents-access-e9e255`. The coordinator may later be used on PR #27, but that is a separate action.
- **It depends on INT-20 and INT-21.** The coordinator runs the loop (INT-21) and records breaches in the format and place (INT-20). It can be planned in parallel, but it cannot be accepted as done before those exist or are explicitly replaced.
- **A human decides.** The coordinator never accepts an intent, never fills in **Approved by**, never merges, never marks a plan approved, and never closes a phase on its own (`human-confirms-closure`). It may mark a PR ready only under the review condition above and only when asked to.
- **It does not do the others' work.** It does not edit code, plans or reviews, and it does not commit unless the owner asks. It asks the right agent.
- **It is itself bound by the rules.** The rules about files, scratch space and refusals apply to the coordinator, and its breaches are recorded the same way.
- **Independent review.** The coordinator starts the reviewer in a way that the reviewer did not write the change, and does not pass held-out scenarios to builders.
- **No outward action without the owner.** Pushing, opening or merging a PR, posting comments and anything else outward-facing require the owner's go-ahead.
- **Concise.** Process-gap lists and PR descriptions follow the "plans stay concise" rule.
- **Deterministic build and standard library only**, as for the rest of the bundle.

## Scenario seeds

### S1 — The cycle is run the same way each time
**Who:** The owner who asks the coordinator to run a phase.
**Wants:** The steps carried out in the written order.
**So that:** Two cycles can be compared, and nothing is skipped.
**We will know when:** The run shows review -> `REVIEW_PLAN_X.md` -> planner amendment -> a stop for the human's approval -> coder by checkpoint -> re-review, each step started with the named inputs, and the coordinator reports where it is waiting.
**Must never:** Write code, a plan or a review itself, or start the coder on an amended plan that a human has not approved.

### S2 — No review, no ready
**Who:** A person (or the coordinator) about to mark a pull request ready.
**Wants:** The check that a review happened.
**So that:** A PR is never offered for merge unreviewed.
**We will know when:** Asked to mark a PR ready when no review of the final change exists, the coordinator refuses and says what is missing; once a review exists and its findings are repaired, deferred or rejected with a reason, it marks the PR ready and says so in the PR.
**Must never:** Mark a PR ready, or call it mergeable, with no review on record, or merge it.

### S3 — Every PR reads the same way
**Who:** A reviewer or the owner opening a pull request produced by a cycle.
**Wants:** The same sections each time.
**So that:** The state of the work is clear at a glance.
**We will know when:** The PR description follows the template: what and why, plan and intent, checkpoints done, review state, rule exceptions, could-not-check, and follow-ups.
**Must never:** Omit the review state or rule exceptions section, or fill them with text the evidence does not support.

### S4 — A guardrail jump is noticed and recorded
**Who:** The coordinator after an agent's run.
**Wants:** To compare what the agent did with what it reported.
**So that:** Breaches are caught even if the agent did not disclose them.
**We will know when:** For a run in which an agent used a forbidden shell write, the coordinator lists it, adds an entry to the breach record by the written procedure, and tells the owner; where the agent's "Rule exceptions" line differs from what happened, that difference is noted.
**Must never:** Leave a known breach unrecorded, or hide its own.

### S5 — Process gaps are collected after each run
**Who:** The owner at the end of an iteration.
**Wants:** A list of what was improvised or missing.
**So that:** The process improves instead of repeating the same gaps.
**We will know when:** The coordinator ends a run with a short gap list (what was ad hoc, what was unclear, what was repeated), each item with evidence.
**Must never:** Invent a gap with no evidence, or bury it in chat only.

### S6 — A gap becomes an intent, not a quiet change
**Who:** The coordinator with a confirmed gap.
**Wants:** To propose the fix through the normal route.
**So that:** Improvements are planned, reviewed and approved like any other work.
**We will know when:** It produces a draft intent from the intent template with problem, outcome, constraints, scenario seeds and open questions, status draft, and offers to hand it to the `planner`.
**Must never:** Mark the intent accepted, edit agents or templates directly, or put the improvement into an unrelated PR.

### S7 — The coordinator exists in both flavors
**Who:** A maintainer installing the bundle.
**Wants:** The coordinator for Claude Code and for GitHub Copilot.
**So that:** The process does not depend on the client.
**We will know when:** The built outputs contain a `coordinator` agent in both `.claude/agents/` and `.github/agents/` with the same instructions, the installer includes it in the profiles the owner chose, and the bundle's tests check it.
**Must never:** Ship it for one flavor only.

### S8 — The coordinator runs the review as written
**Who:** The owner asking the coordinator to review a finished change.
**Wants:** The review run in its own session and its output handed on.
**So that:** The writer of the change never reviews it, and the output is not lost.
**We will know when:** A `reviewer` session separate from the coder's runs with the named inputs, `REVIEW_PLAN_X.md` appears, the planner is given it, and the coordinator stops for the owner's approval before the repair is run.
**Must never:** Run the review in the coder's session, summarize the findings instead of passing the document, or start the repair unapproved.

### S9 — A test change is asked, not slipped in
**Who:** The coordinator when the coder reports that a fix breaks a test pinning the old behavior.
**Wants:** The owner's decision before the test changes.
**So that:** The rule against editing tests to pass keeps its meaning.
**We will know when:** The coordinator relays the question (test, assertion, reason) to the owner, waits, and records the answer in the plan before the coder edits the test.
**Must never:** Let the test be edited on the coder's own judgment, or lose the owner's approval from the record.

### S10 — Ready needs a confirmed CI result on the right commit
**Who:** The coordinator asked to mark a PR ready.
**Wants:** The review state and the CI result for the pushed commit.
**So that:** "Ready" means ready.
**We will know when:** It reports the review state, the gates and the CI status of the exact commit, asks a human to confirm, and only then marks the PR ready; if any is missing it says which.
**Must never:** Mark a PR ready on a CI result from a different commit, or on a local pass alone.

## Out of scope
- The review document and the loop's detail (INT-21) and the guardrail hook and breach record (INT-20).
- Merging, releasing and deployment.
- Running the cycle for PR #27.
- Scheduling or running agents unattended; the coordinator works inside a session with the owner.
- Choosing which model runs which agent.

## Open questions
- The ready check includes the review policy's approval rule. Whether that rule exists, and what it is in a solo repository, is decided in INT-23. Until then, does the coordinator apply only the "review exists and a human confirms" condition? (the product owner)
- Is the coordinator a true agent definition (in `.claude/agents/`, `.github/agents/`) that starts other agents, or a procedure the main session follows? Subagents in some clients cannot start other subagents; this decides the design. (the product owner, after a check of what each client allows)
- Which install profiles include it (`build`, `quality`, `single`)? (the product owner)
- Where does the PR template live and how is it applied (`.github/pull_request_template.md`, or only in the coordinator's instructions)? (the product owner)
- Does "ready" mean taking the PR out of draft, and who may do it: only the owner, or the coordinator at the owner's request? (the product owner)
- What counts as a sufficient review before ready: any one cycle, or a cycle on the final commit with no open Important findings? (the product owner)
- How does the coordinator observe tool calls in a client where it cannot read another agent's transcript? (the product owner, with a check of the client capabilities)
- Should INT-20, INT-21, INT-22 and INT-23 be accepted and planned as separate phases, in the order 20, 21, 23, 22, or planned together? (INT-23 settles the review policy that INT-21's procedure and this agent's ready check read.) (the product owner)
