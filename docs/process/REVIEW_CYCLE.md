# Review cycle

How a change is reviewed and repaired, who does each step and when it ends. This file ships in every install (at `docs/process/REVIEW_CYCLE.md`) and is read by the `reviewer`, the `planner`, the `coder` and the `coordinator`. It is not `REVIEW.md`: that file is optional and per repository, and the standard below cannot live there. The templates and agents are linked, not restated: the review document is written from `docs/templates/REVIEW_PLAN_TEMPLATE.md`, a plan is written from `docs/templates/PHASE_PLAN_TEMPLATE.md`, and each agent's rules are in its own definition.

## The sequence

In one line: review -> `docs/plans/REVIEW_PLAN_<N>.md` -> planner amendment -> human approval -> coder repair checkpoint -> re-review of the same file, repeated until the cycle ends (below).

| Step | Who | Input | Output |
|---|---|---|---|
| Review | the `reviewer`, in its own session (started by the `coordinator`, or by the owner when there is none) | the change, the approved plan with its completion notes, the intent, the review policy, the `coder`'s "Rule exceptions" line | `docs/plans/REVIEW_PLAN_<N>.md`, revision 1 |
| Amendment | the `planner` | the review file and the plan | a `## Review amendment (round <n>)` section in `PHASE_<N>_PLAN.md`: a repair checkpoint, the findings not repaired with a reason, open questions. **Amendment approved by** stays blank |
| Approval | a human (the owner) | the amendment | name and date on **Amendment approved by**, and answers to the open questions, recorded in the plan |
| Repair | the `coder`, not the agent that reviewed | the approved repair checkpoint | the checkpoint's tasks checked off with evidence, gates reported with real counts, then a stop |
| Re-review | the `reviewer`, in a new session, never the agent that made the repair | the same review file, the new commit | a new revision of the same file: each earlier finding shown as repaired, deferred or rejected with evidence, and any new findings |
| Close | a human | the last revision | the human says the cycle is done, or accepts the remainder in writing |

Nobody approves their own work in this sequence: the `planner` never fills in an approval line, the `reviewer` never approves or blocks, and the `coder` does not start a repair checkpoint before a human has approved the amendment. Every finding ends in one of three states: repaired, deferred (with a reason) or rejected (with a reason). Every repair task names the finding it answers (**Source:** `REVIEW_PLAN_<N>.md F<id>`).

## How a review is handled

- **Who runs it, and in which session.** The `reviewer`, in its own session and never in the session of the agent that wrote the change. The `coordinator` starts it; where there is none, the owner does.
- **What it reads.** The change (a diff, a branch or a pull request), the approved `PHASE_<N>_PLAN.md` with its completion notes, the intent, the review policy (`REVIEW.md` if the repository has one, otherwise the reviewer's built-in defaults), the `Review process` section of `AGENTS.md`, and the "Rule exceptions" line of the agent that made the change.
- **Where the output goes.** `docs/plans/REVIEW_PLAN_<N>.md`, next to the plan, the only file the `reviewer` writes. The chat reply is a pointer to it with the counts by severity. A re-review revises the same file in place: it raises the revision number, adds a row to the revision log with a timestamp, and changes the state of each earlier finding with its evidence. A finding is never deleted.
- **Who consumes it.** The `planner`, which amends the plan; the owner, who decides what to repair, defer or reject; the `coordinator`, which checks it before a pull request is called ready.
- **How findings become plan tasks.** Each Important finding to be repaired becomes one task in a repair checkpoint of the amendment, tracing back to the finding. Nits and deferred items are listed with a reason and are not turned into tasks unless the owner asks. The amendment adds to the plan: completed tasks keep their notes and the original acceptance lines stay as written.
- **What stops a pull request from being marked ready.** A pull request is not marked ready, and not merged, until a review of the final commit exists, each of its findings is repaired, deferred or rejected, and a human has said so. The `coordinator` states the result of this check (see "The ready check"); only a human moves a pull request out of draft or merges it.
- **How cycles end.** The ideal end is a re-review with nothing open, or only Nits. The limit is three runs (the first review is run 1, each re-review the next) or until the human says enough. After the third run with an Important finding still open, the owner decides; the human may set another limit.

## How tests are handled

- **Who writes tests.** The `coder` writes the local unit and integration checks alongside the code, and the `bug-coder` writes a regression test. The `test-planner` and `test-coder` are separate: the coder's checks are not a substitute for them. The `coder` neither writes nor reads held-out behavior scenarios, and neither does the `reviewer`.
- **Test plans.** A person approves the test plan, a failing gap check goes to the `bug-coder` and is not edited to pass, and the `reviewer` checks the test plan for reflection under its **Tests** pass (the signs the `reviewer` agent lists).
- **Failing-first evidence.** A fix has a regression test that is shown failing before the fix and passing after. The command and both results are recorded in the task's completion note, so the `reviewer` can reproduce them. A security fix with no failing-first test is an Important finding.
- **A fix that breaks a test that pinned the old behavior.** The rule is not to edit a test to make it pass. When a fix legitimately changes behavior an existing test pinned, the `coder` stops, names the test and the assertion, explains why the old expectation is wrong and asks the owner. It edits the test only after a yes, and records the approval and the change in the plan note. The `reviewer` lists every such change and checks that the approval is recorded.
- **How gates are run and reported.** The project's gates (the commands under "Project commands" in `AGENTS.md`) are run by the `coder` at the end of each checkpoint and by the `reviewer` to confirm. Each result is reported with the command and the real output, as counts and not as "passed". A gate that could not be run is reported as "not run", with the reason.
- **Who confirms CI on a pushed commit.** The `coordinator` reads the hosted CI result for the exact commit that was pushed and reports it; a human confirms it before the pull request is marked ready. A run for an older commit is not the result for this one. A red or missing CI result is a finding, not a note.

## The ready check

Before a pull request is called ready, the `coordinator` writes, in the pull request, what exists and what is missing. It refuses to say "ready" while any line is missing:

1. A review of the final commit exists: the latest revision of `docs/plans/REVIEW_PLAN_<N>.md` names the commit at the head of the branch.
2. Each finding is repaired, deferred or rejected: the counts table of that revision shows no open finding, or a human has accepted the remainder in writing.
3. CI of that exact commit has been read, and a human has confirmed it.
4. Approval follows the `Review process` section of `AGENTS.md` (the repository type and, for a team, the second-approver rule written there). No other approval rule is invented.

Then a human decides. The `coordinator` does not move a pull request out of draft and does not merge.

## What earlier cycles taught

These lessons are now part of the steps: the review must be a file, not a chat message; the amendment lists how every finding ends, so none is dropped; the first repair task is the failing tests and the last is a replay with the gates; the owner's decisions and answers are written into the plan, not left in chat; a completed task's note is not edited, so a correction goes in the note of a later task; and the loop has a limit, so a round can be declared the last.

## Compatibility

Plans and reviews written before this change stay valid. A plan without checkpoints is one checkpoint, and the `coder` runs it as such. A repository with no `docs/plans/REVIEW_PLAN_<N>.md` is read as having had no review document: the `reviewer` creates one the next time it runs. An existing `REVIEW.md` stays the review policy; a repository without one uses the built-in defaults.

## Reviewing documents and agent instructions

The change is mostly documents and agent instructions, so a review of it, and of any similar change, means:

(a) traceability: every "we will know when" line maps to a named file and section (table under Completion checklist);
(b) consistency: no two documents, rules, agent definitions or templates contradict each other, including the rendered `AGENTS.md` against the rule sources;
(c) verified claims: every command, flag, path, key or file format a document states was run or read, or is marked "unverified: confirm with <source>", and every link and path resolves;
(d) behavior: a document that prescribes behavior is checked in real use on Manifold work, by agents and reviewers that did not write it, and the evidence is recorded (guard log, breach records, review documents, PR summaries, `tests/results/` records); until that use has happened the scenario is reported as "no evidence yet" (reworded 2026-11-06 because the owner replaced the toy walk-throughs with real use; reconfirmed by the owner on 2026-11-06 with the `tests/results/` records added to the evidence list);
(e) code gets normal tests plus the bundle build and lint;
(f) an independent reviewer, not the author, using the review policy in force;
(g) owner approval of any text that changes agent behavior.

Severity for prose: **Important** if an agent could behave differently or be misled by it; otherwise Nit.

Confirmed by the owner (Michael Hay), 2026-11-03.

## Where things live

`docs/process/REVIEW_CYCLE.md` is this file. The review document is `docs/plans/REVIEW_PLAN_<N>.md`, written from `docs/templates/REVIEW_PLAN_TEMPLATE.md`. The optional repository policy is `REVIEW.md` (from `docs/templates/REVIEW_TEMPLATE.md`). Who approves is stated in `AGENTS.md` under "Review process". Breaches found during a cycle go to the record described in `docs/process/BREACH_PROCEDURE.md`. In the Manifold repository, `tests/results/` holds the records of runs.
