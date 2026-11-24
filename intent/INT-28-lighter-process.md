---
id: INT-28
title: Lighter process, fewer signatures, fewer and larger checkpoints
author: Michael Hay
created: 2026-11-24
status: draft
affects: [bundles/base, docs/templates, docs/process, bundles/base/agents/planner.agent.md, bundles/base/agents/coordinator.agent.md, bundles/base/agents/reviewer.agent.md]
drafted_with: [claude-sonnet-5-5]
accepted_by: "<Insert Name of acceptor on Date of acceptance, ex. M. Kusanagi on Jan-01-2027>"
# Instructions: read the intent, set status to accepted, then replace the whole quoted slug above (the quotes stay, the brackets go) with your name and the date. An agent leaves it as it is.
---

# Intent: Lighter process, fewer signatures, fewer and larger checkpoints

## Problem

The owner says the process puts too much load on the human and costs too much. Evidence from Phase 4 (`docs/plans/PHASE_4_PLAN.md`, `docs/plans/REVIEW_PLAN_4.md`):

1. **Every amendment needs a signature, even for nits.** The loop in `docs/process/REVIEW_CYCLE.md` makes the owner sign **Amendment approved by** before the coder starts any repair. Phase 4 has had 8 amendment rounds; the last ones repaired the wording of a note.
2. **Every checkpoint is its own pull request** with its own body, CI read, ready check, ticks and Approve review.
3. **Tasks and checkpoints are cut too finely, and they grow.** Phase 4 was planned as 40 tasks in 6 checkpoints. After 8 rounds it holds 76 tasks and 11 checkpoint headings. Checkpoint 4 (the Megaroast testbed, planned as Tasks 28 to 31) took pull requests 38 to 40, four amendment rounds and five added tasks.
4. **Many per-task boxes for the human.** Several tasks exist only so that the owner can tick or sign one thing (for example Task 31 and Task 76), and the owner ticks them one by one.
5. **One review revision per round.** Each amendment round is followed by a re-review revision of `REVIEW_PLAN_4.md` (over 1,100 lines and 11 revisions so far), so cost grows with every round, whatever the size of the finding.

The cost: the human is the bottleneck for work that is mostly wording, and the process spends more effort on itself than on the product.

## Proposed outcome

The human is asked to decide only what needs a human, once, and the work is cut into units a person can judge as a whole. Direction from the owner and coordinator (the planner confirms or changes it; see Open questions):

1. **Signature by severity.** Only Important or higher findings need a signed amendment round. Nits and small repairs are either fixed inside the checkpoint's own pull request before it is signed, or batched into one cleanup task at the end of the phase. The nit decisions are recorded once, in the pull request.
2. **A checkpoint is a coherent deliverable of about 4 to 8 tasks and one pull request.** A checkpoint that would need more is split by deliverable, not by round. Repairs from review stay in the checkpoint they belong to and do not create a new checkpoint heading unless they are Important and a person asks.
3. **Related owner-only confirmations or one release are one task with sub-steps**, not several tasks (for example the owner's setup steps for one testbed).
4. **One review per pull request, at the end,** not one revision per amendment round. The limit of three review runs in `REVIEW_CYCLE.md` stays.
5. **The owner ticks once per pull request** to accept all its tasks, not once per task. The ready check still lists what is met and what is missing.
6. **What stays:** the owner's signature on the plan before coding starts, the independent review, held-out scenarios, and facts only the owner can supply (private repositories, an App created, a version chosen).

## Affected users and systems

- **The owner** (solo repository), who signs, ticks and approves less often. A team repository keeps its second approver.
- **Agents:** `planner` (sizing, one cleanup task, owner-only sub-steps), `coordinator` (one ready check per pull request, one-tick form), `reviewer` (one review per pull request, severity of nits), `coder` (repairs nits inside the checkpoint).
- **Files:** `docs/process/REVIEW_CYCLE.md` (sequence, "How findings become plan tasks", light path), `docs/process/HOWTO.md`, `docs/templates/PHASE_PLAN_TEMPLATE.md` (task and checkpoint format, completion checklist, amendment section), `docs/templates/PULL_REQUEST_TEMPLATE.md` ("What remains for you", ticks), `docs/templates/REVIEW_PLAN_TEMPLATE.md`, and their sources under `bundles/base/`.
- **Both flavors** (`claude` and `copilot`) and every repository that installs the bundle.

## Constraints

- **A human keeps the final say.** No agent signs, ticks, approves or fills in a human field for the human. The one-tick-per-PR form is still a human act (INT-26 "A human keeps the final say"; INT-27 slugs).
- **An Important finding always needs a human decision.** Lighter means fewer, not none: repaired, deferred or rejected is still recorded by a human for every Important or higher finding (INT-21 S2; `REVIEW_CYCLE.md` "Where each fact is recorded").
- **Ready still means reviewed.** A review of the final commit, each finding decided, and CI of that exact commit confirmed by a human stay required (INT-22; INT-26 "Ready still means reviewed"). Only how often they are recorded changes.
- **Approval follows the review policy.** The rule in `AGENTS.md` "Review process" and INT-23 stays: a solo repository may be lighter, a team is not weakened.
- **Independent review and held-out scenarios stay** (INT-21 S6; `AGENTS.md` "Held-out scenarios"). The reviewer never reviews its own change and never approves.
- **Secrets stay protected.** Nothing here relaxes the secret rules (`AGENTS.md` "Secrets"), the commit-hook rule or the staging rule.
- **Plan approval stays.** The coder does not start a plan whose **Approved by** is a slug (`AGENTS.md` "Plan approval").
- **Builds on INT-21, INT-26 and INT-27; contradicts none.** INT-21 answered the checkpoint size with "Demonstrable result": this intent keeps that test and adds the rule of thumb of 4 to 8 tasks on top of it. INT-26's light path for text fixes stays as the route for text-only pull requests.
- **Both flavors from one source**, deterministic build, standard library only for any script (INT-22, INT-26).
- **Shipped text stays generic** and concise; no repository-specific history in installed files.
- **No outward action without the owner.** Editing a live pull request, the GitHub ruleset or the workflow needs the owner's go-ahead.

## Scenario seeds

### S1 — A nit does not stop the work for a signature

**Who:** The owner of a solo repository.
**Wants:** A review that finds only Nits to be repaired without a signed amendment round.
**So that:** The coder is not waiting on a signature for wording.
**We will know when:** After a review with only Nits, the pull request shows the nits fixed or listed in one place, and no new **Amendment approved by** line was needed.
**Must never:** Let an Important finding skip a human decision, or let an agent decide that a finding is only a Nit without the reviewer's severity showing it.

### S2 — An Important finding still gets a human decision

**Who:** The owner.
**Wants:** To decide on each Important finding once: repair, defer or reject.
**So that:** Nothing serious is dropped.
**We will know when:** Each Important finding has a recorded human decision, and the amendment that repairs it carries a name and date written by the owner.
**Must never:** Sign, tick or fill in a name for the owner, or start a repair of an Important finding before the signature.

### S3 — A checkpoint is one deliverable in one pull request

**Who:** The owner reading a new plan.
**Wants:** Checkpoints of about 4 to 8 tasks, each ending in a result I can check, each in one pull request.
**So that:** There are few pull requests to read, tick and approve.
**We will know when:** A new plan's checkpoints each fall in that range, or the plan says why one does not; review repairs show up inside the checkpoint they belong to.
**Must never:** Cut tasks so fine that one change needs several tasks, or break dependency order or leave a task outside every checkpoint (INT-21 S4).

### S4 — Owner-only steps are one task

**Who:** The owner.
**Wants:** The steps only I can do for one purpose (create the private repositories, create the App, record a sign-off) as one task with sub-steps.
**So that:** I tick once for the purpose, not once per step.
**We will know when:** A plan with owner-only work for one purpose has one task with numbered sub-steps and one place for my confirmation.
**Must never:** Mark an owner-only sub-step done on the owner's behalf, or ask the owner to confirm a fact an agent can read from the repository.

### S5 — One review at the end of a pull request

**Who:** The owner and the reviewer.
**Wants:** One review of the final commit of a pull request, with repairs made before it.
**So that:** The review file does not grow by a revision for every small round.
**We will know when:** A pull request that needed no Important repair has one review revision naming its final commit.
**Must never:** Skip the review of the final commit, let the author review its own change, or run more than three review runs without the owner deciding (`REVIEW_CYCLE.md` "How cycles end").

### S6 — One tick per pull request

**Who:** The owner.
**Wants:** One place to say I accept every task of this pull request, with the ready check showing what is met.
**So that:** I do not tick each task one by one.
**We will know when:** The pull request has one acceptance tick covering its tasks, still next to its **Instructions** block (INT-27), and the ready check still lists each of its four lines.
**Must never:** Tick for the owner, merge several decisions into one tick the owner cannot see, or drop a ready-check line.

### S7 — The things that earn their place are untouched

**Who:** Any maintainer.
**Wants:** The plan signature, held-out separation and owner-only facts to work as before.
**So that:** Lighter does not mean weaker.
**We will know when:** The coder still stops on a plan whose **Approved by** holds a slug, the coder and the reviewer still do not read the held-out scenarios, and the coordinator still treats an unreplaced slug as missing.
**Must never:** Weaken a secret rule, a held-out rule or the plan approval, or lighten a team repository.

## Out of scope

- Any change to `PHASE_4_PLAN.md`, to Phase 4's checkpoints, tasks or amendment rounds, or to `REVIEW_PLAN_4.md`. Applying this to Phase 4 is a separate step, after the owner accepts this intent.
- Changing the passes or severity definitions of the `reviewer` (INT-21, INT-23), except what a "Nit" may skip.
- Changing the GitHub ruleset, the required review count or the CI workflow.
- Any weakening for a team repository.
- A script that merges or ticks pull requests.
- Merging, releasing and choosing a version.

## Open questions

- **Where is the line between a nit and a small repair that needs no signature?** Recommendation: a Nit is whatever the reviewer marks as Nit under the existing severity rules; a small repair is a Nit-only change to text or a comment, with no change to code, rules, agent permissions, hooks or tests. Anything else is Important and takes the signed round. Who: the owner. Answer:
- **Where do batched nits go?** Options: fixed inside the checkpoint's own pull request before the owner signs, or one cleanup task at the end of the phase. Recommendation: fix them in the pull request when they touch files the pull request already changes; otherwise one cleanup task at the end of the phase. Who: the owner. Answer:
- **How is the one tick per pull request recorded?** Recommendation: one checkbox in "What remains for you" that reads "I accept all tasks of this pull request"; the per-task completion notes stay in the plan as the coder's evidence, and the owner no longer ticks them. Who: the owner. Answer:
- **Does a checkpoint's size limit (4 to 8 tasks) bind the planner or only guide it?** Recommendation: guide, with one sentence in the plan when a checkpoint falls outside it. Who: the owner. Answer:
- **Should a repair of an Important finding live in the original checkpoint or in a numbered repair checkpoint?** Recommendation: in the original checkpoint's pull request while it is open; a numbered repair checkpoint only after merge. Who: the owner. Answer:
- **Does the light path (INT-26) widen to cover Nit-only rounds in a code pull request?** Recommendation: no; keep it to text-only pull requests and use the nit rule above for code ones. Who: the owner. Answer:
- **Which release carries this change?** Recommendation: the next release after acceptance; do not hold Phase 4 for it. Who: the owner. Answer:
