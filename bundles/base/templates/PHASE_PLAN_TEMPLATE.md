# PHASE_<N>_PLAN.md
<!--
  Template for the planner agent.
  Copy this file to docs/plans/PHASE_<N>_PLAN.md, fill it in, and delete these
  comments before the plan is reviewed. Keep it short and complete: link to
  existing documents instead of restating them, and add no sections beyond
  these.
-->

**Approved by:** <!-- name and YYYY-MM-DD; left blank until a human approves. The coder will not start without it. -->

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
> Work tasks in the order listed. For each task: read the named files first,
> implement the described change, run the verify command and the task's
> acceptance check, then update the todo marker `[ ]` → `[x]` and add a
> one-line completion note directly beneath the task header: what changed, the
> command run, the result. If a task is blocked, mark it `[~]` with a note and
> surface it immediately; do not skip ahead. When all tasks are complete, fill
> in the completion summary under the Completion checklist.

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

## Completion checklist
<!-- Replace <verify command> and <test command> with the real commands from the project facts. -->
- [ ] All tasks marked [x] by the coder
- [ ] `<verify command>` passes clean
- [ ] `<test command>` passes clean (no regressions)
- [ ] No [~] blocked items outstanding
- [ ] Summary note added by the coder below this line

<!--
  coder: add your completion summary here:
  - Files changed
  - Deviations from the plan, and why ("None." if none)
  - Verification evidence: command and result for each check; anything not run, and why
  - Deferred items and follow-ups
-->
