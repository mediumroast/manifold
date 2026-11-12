# PHASE_<N>_PLAN.md
<!--
  Template for the planner agent.
  Copy this file to docs/plans/PHASE_<N>_PLAN.md, fill it in, and delete these
  comments before the plan is reviewed. Keep it short and complete: link to
  existing documents instead of restating them, and add no sections beyond
  these.
-->

**Approved by:** <!-- name and YYYY-MM-DD; left blank until a human approves. The coder will not start without it. -->
**Source intent:** <!-- INT-<n> and its path, or "none" -->

## Objective
<!--
  One paragraph. What will be true when this phase is complete that is not
  true now. Write it as a statement of outcome, not a list of tasks.
-->

## Scope

**In scope:**
-

**Out of scope:**
<!-- Things you noticed but are deliberately not doing. -->
-

**Needs from other repositories:**
<!-- Repository and the thing that must change or exist first, or "None." -->

**Provides to other repositories:**
<!-- Repository and the thing this change offers them, or "None." -->

## Concerns flagged
<!--
  Conflicts between requirements or policies, and anything the planner could not resolve,
  each with who needs to decide. Write "None." if there are none.
-->

## Prerequisites
<!--
  Work that must be complete before this phase begins: prior phase plans,
  API contracts, environment variables, secrets, decisions.
  Mark each [x] satisfied or [ ] outstanding.
-->
- [ ]

## File inventory

| Path | Action | Reason |
|------|--------|--------|
| `` | CREATE \| MODIFY \| DELETE | |

## Tasks

> **Instructions for the coder:**
> Work one checkpoint at a time, tasks in the order listed. For each task: read
> the named files first, implement the described change, run the verify command
> and the task's acceptance check, then update the todo marker `[ ]` → `[x]` and
> add a one-line completion note directly beneath the task header: what changed,
> the command run, the result. At the end of a checkpoint run its Verification,
> report the gates with command and real counts, and stop until told to
> continue. If a task is blocked, mark it `[~]` with a note and surface it
> immediately; do not skip ahead. When all tasks are complete, fill in the
> completion summary under the Completion checklist.

<!--
  Group the tasks into numbered checkpoints, in dependency order, every task in
  exactly one. Each checkpoint ends in a demonstrable result (its Verification).
  Older plans stay valid: a plan without checkpoints is one checkpoint.
-->

### CP1 — <name>

### Task 1 — <imperative short title>
**Files:**
**Action:** CREATE | MODIFY | DELETE
**Change:** <!-- Name every symbol: file, function, class, field, route, flag. One change per task. -->
**Acceptance:** <!-- A command to run or something to observe. "Works correctly" is not acceptance. -->
**Rollback:** <!-- Only for destructive or hard-to-reverse tasks; delete this line otherwise. -->
**Todo:** [ ]

---

### Task 2 — <imperative short title>
**Files:**
**Action:** CREATE | MODIFY | DELETE
**Change:**
**Acceptance:**
**Todo:** [ ]

---

<!-- Copy the task block above for each additional task. Put a test task next to the code task it verifies. -->

**Verification:** <!-- A demonstrable result that ends this checkpoint: a command and the output that shows it. -->

<!-- Copy the checkpoint heading and the Verification line for each additional checkpoint. -->

## Completion checklist
<!-- Replace <verify command> and <test command> with the real commands from the project facts. -->
- [ ] All tasks marked [x] by the coder
- [ ] `<verify command>` passes clean
- [ ] `<test command>` passes clean (no regressions)
- [ ] No [~] blocked items outstanding
- [ ] Level aimed at: <mergeable | releasable | done> (see "Definition of done" in `docs/process/REVIEW_CYCLE.md`)
- [ ] Summary note added by the coder below this line

<!--
  coder: add your completion summary here:
  - Files changed
  - Deviations from the plan, and why ("None." if none)
  - Verification evidence: command and result for each check; anything not run, and why
  - Gates run: each command with its real counts, or "not run" and why
  - Rule exceptions: none, or each (command, file, reason)
  - Deferred items and follow-ups
-->

<!--
  Review amendment (planner, from a review document). Delete this whole section
  in a plan that has none. Add one section per review round, below the checklist.
  The planner adds the repair checkpoint; a human fills in the approval line;
  the coder runs the checkpoint only after that. Do not change completed tasks
  or the original acceptance lines.
-->

## Review amendment (round <n>)
**Source:** <!-- `docs/plans/REVIEW_PLAN_<N>.md`, revision <r> -->
**Amendment approved by:** <!-- name and YYYY-MM-DD; blank until a human fills it in. The planner never fills in this line. The coder will not run the repair checkpoint without it. -->

### CP<n> — Repairs from review round <n>

### Task <n> — <imperative short title>
**Source:** `REVIEW_PLAN_<N>.md F<id>`
**Files:**
**Action:** CREATE | MODIFY | DELETE
**Change:**
**Acceptance:**
**Todo:** [ ]

**Verification:** <!-- A demonstrable result that ends the repair checkpoint. -->

**Findings not repaired:**

| Finding | End | Reason |
|---|---|---|
| `F<id>` | deferred \| rejected | |

**Open questions:** <!-- For the human, or "None." -->
