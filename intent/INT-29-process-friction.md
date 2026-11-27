---
id: INT-29
title: Remove process friction that earns nothing
author: Michael Hay
created: 2026-11-27
status: draft
affects: [bundles/base/agents/coordinator.agent.md, bundles/base/agents/reviewer.agent.md, bundles/base/agents/coder.agent.md, docs/templates/PULL_REQUEST_TEMPLATE.md, docs/templates/PHASE_PLAN_TEMPLATE.md, docs/templates/REVIEW_PLAN_TEMPLATE.md, docs/process/REVIEW_CYCLE.md, docs/process/BREACH_PROCEDURE.md, .manifold/hooks/guard.py]
drafted_with: [claude-sonnet-5-5]
accepted_by: "<Insert Name of acceptor on Date of acceptance, ex. M. Kusanagi on Jan-01-2027>"
# Instructions: read the intent, set status to accepted, then replace the whole quoted slug above (the quotes stay, the brackets go) with your name and the date. An agent leaves it as it is.
---

# Intent: Remove process friction that earns nothing

## Problem

The owner says the process has grown steps that do not help and slow the work. INT-28 (accepted Nov 27, 2026) already covers signatures by severity, checkpoint size, one review and one tick per pull request. This intent covers what INT-28 leaves out. Each point below was checked in the files named.

1. **The coordinator is told to fill in the pull request but has no way to write it.** `docs/templates/PULL_REQUEST_TEMPLATE.md` line 4 says the coordinator fills it in; `bundles/base/agents/coordinator.agent.md` lets it write only the breach record and new intent drafts, and the guard enforces that (`.manifold/hooks/guard.py` header). `.manifold/guard-log.jsonl` shows the coordinator refused three times on Nov 27, 2026 (a redirect and two file writes) while updating the bodies of pull requests 40 and 41. A person pastes every update.
2. **Pull request bodies go stale on every push.** The template holds facts that change with each commit: the commit reviewed (line 25), the full hash and CI runs (lines 44 to 47), the ready-check evidence (lines 95 to 98). `docs/process/REVIEW_CYCLE.md` line 66 asks for a CI read and tick for every new commit, even one that changes only text. Pull request 41 gained a commit after its body was written and the body named the old one.
3. **The template is heavy and repeats itself.** It has 105 lines, 11 sections and four **Instructions** blocks. The same fact (CI result, finding decisions) is written in three or four places, and the owner does two acts for one fact: the **Confirmed by** line and the CI tick.
4. **The Rule exceptions check runs after every agent run, in several places.** The line is required of all eight agents; the coordinator compares it with the diff, commit log, guard log, allow file and transcript (`coordinator.agent.md` line 73), the reviewer compares it again (`reviewer.agent.md` line 95), and `docs/process/BREACH_PROCEDURE.md` adds one entry per rule per run. The guard already refuses and logs real breaches.
5. **Many human fields.** `PHASE_4_PLAN.md` holds 22 slugs; the template files define **Approved by**, **Amendment approved by**, **Confirmed by**, **Human confirmation** and `accepted_by`. `REVIEW_CYCLE.md` lines 52 to 58 define how to detect an unreplaced slug.
6. **The review file only grows.** `REVIEW_PLAN_4.md` is 1,136 lines with 20 revision rows; a re-review does not shrink for a small change, and a finding is never deleted (`REVIEW_CYCLE.md` line 24).
7. **The light path is narrow.** `REVIEW_CYCLE.md` lines 81 to 90 allow it only for text in docs and agent instructions, and it still needs a full review, four ready-check lines and a CI tick for each commit.
8. **Plans carry sections nobody uses.** `PHASE_PLAN_TEMPLATE.md` has a file-inventory table that repeats each task's Files line, Needs and Provides lines, a Prerequisites list and a Rollback line, even when they say "none". `PHASE_4_PLAN.md` is 1,458 lines.
9. **The same fact is written three times** per task: the coder's task note, the coder's report and the completion summary (`coder.agent.md` lines 42 and 43; `PHASE_PLAN_TEMPLATE.md` lines 101 to 118). INT-28 covers the owner's per-task ticks, not this.

The cost: the owner and the agents spend effort on the paperwork around a change instead of on the change.

What is new compared with INT-28: points 1 to 9 in full, except the per-task ticks, signatures and checkpoint size that INT-28 owns.

## Proposed outcome

Each ritual either has a way to be done by the agent that is asked to do it, or is dropped. Direction for the planner to confirm or change:

1. **One route for the pull request text.** Either the coordinator may run `gh pr edit` for the generated sections, with the owner's go-ahead recorded once per pull request, or it gives one complete block that the owner pastes once, at ready time. No agent is told to do what the guard blocks.
2. **A stable body, and facts at the end.** The body holds what and why, plan, intent and the owner's boxes. Commit-specific facts (hash, runs, ready check) are written once for the final commit, not on every push. The CI read and tick are for the final commit of the pull request.
3. **A short template** of about five sections, one **Instructions** block, a ready check of three lines (review of the final commit, findings decided, CI of the head) with approval following `AGENTS.md` "Review process". The CI read and the **Confirmed by** line become one act.
4. **One exceptions check per pull request.** Each agent still reports its Rule exceptions line. The guard log is compared once, at the end, by the reviewer; the coordinator repeats it only where the log shows a refusal. Breach entries stay append-only.
5. **Fewer human fields.** The plan **Approved by** and one per-pull-request confirmation remain. **Amendment approved by** stays for Important findings only (INT-28 S2).
6. **A short review for a small change.** A re-review covers the findings and the diff since the last commit; a pull request with no Important finding may have a short review file (counts, findings, gates).
7. **A wider light path** for any change a human judges does not alter behavior, in a solo repository. The review, final-commit CI and the human tick stay.
8. **A leaner plan.** Drop the file inventory, empty Needs and Provides lines and a Prerequisites list with nothing outstanding.
9. **One record per task fact:** the task note in the plan; the report refers to it instead of copying it.

## Affected users and systems

- **The owner** (solo repository): fewer pastes, fields and ticks.
- **Agents:** `coordinator`, `reviewer`, `coder`, `planner`.
- **Files:** the files in `affects`, their sources under `bundles/base/`, and `.manifold/hooks/guard.py` only if the owner chooses `gh pr edit` for the coordinator (point 1).
- Both flavors (`claude` and `copilot`) and every repository that installs the bundle.

## Constraints

- **A human keeps the final say.** No agent signs, ticks, approves, moves a pull request out of draft or merges (INT-26, INT-27).
- **Independent review stays.** The reviewer is never the writer or the repairer and never approves (INT-21).
- **Held-out scenarios stay with the quality side** (`AGENTS.md` "Held-out scenarios").
- **Secrets, commit hooks and the staging rule stay** (`AGENTS.md`).
- **Plan approval stays.** The coder does not start a plan whose **Approved by** is a slug.
- **Every Important finding still gets a human decision, and CI of the exact head commit is still confirmed by a human.**
- **The guard and the breach record stay.** Lighter means a smaller ritual, not less enforcement. Any widening of what the coordinator may write is the owner's choice and recorded in `.manifold/guard-allow.json` or the guard itself.
- **Team repositories keep their second approver** (`AGENTS.md` "Review process").
- **Builds on INT-21, INT-22, INT-26, INT-27 and INT-28; adjusts INT-22 (what the coordinator may write), INT-26 (the light path) and INT-27 (the slugs), contradicts none** unless the owner says so in the open questions.
- Both flavors from one source, deterministic build, standard library only for any script; shipped text generic and concise.
- No outward action without the owner: editing a live pull request, the ruleset or the workflow needs the owner's go-ahead.

## Scenario seeds

### S1 — The coordinator can do what it is told
**Who:** The owner.
**Wants:** The pull request description to be updated by the coordinator, or to get one complete block to paste once.
**So that:** I do not paste a changed body after each push.
**We will know when:** A pull request ready for review has a description naming its final commit and its CI runs, with no guard refusal in the log for that update.
**Must never:** Let the coordinator write a human field, tick a box, or edit the body without the owner's go-ahead.

### S2 — A push does not make the description wrong
**Who:** The owner.
**Wants:** The description's commit-specific facts to be written for the final commit.
**So that:** I do not read stale hashes.
**We will know when:** The hash and runs in the description equal the pull request head when the owner ticks.
**Must never:** Accept a CI tick for a commit that is not the head.

### S3 — A shorter pull request description
**Who:** The owner.
**Wants:** About five sections and one **Instructions** block.
**So that:** I read less and tick once.
**We will know when:** A new pull request body has no repeated CI or findings text, and the ready check lists review, findings and CI of the head.
**Must never:** Drop the review, findings or CI lines, or the **Instructions** the owner needs for the tick.

### S4 — One exceptions check per pull request
**Who:** The coordinator and the owner.
**Wants:** The guard log compared with the agents' Rule exceptions lines once at the end.
**So that:** A real breach is still found, with less repeated work.
**We will know when:** A refusal in the guard log without a matching exceptions line is still recorded as a breach.
**Must never:** Hide a breach, skip recording one, or edit the guard log.

### S5 — A short review for a small change
**Who:** The owner and the reviewer.
**Wants:** A re-review that covers only the findings and the new diff.
**So that:** The review file stays readable.
**We will know when:** A pull request with no Important finding has a review file that fits on a page and names its final commit.
**Must never:** Skip the review of the final commit or delete a finding.

### S6 — Fewer fields to fill
**Who:** The owner.
**Wants:** The plan approval and one confirmation per pull request.
**So that:** I sign what needs me.
**We will know when:** A pull request for Nits only needs no **Amendment approved by**, and the confirmation of CI and the tick are one act.
**Must never:** Fill a field for the owner, or treat a slug as met.

## Out of scope

- Signatures by severity, checkpoint size, one review and one tick per pull request (INT-28).
- Changing the reviewer's passes or severity definitions (INT-21, INT-23).
- Changing the GitHub ruleset, required review count or the CI workflow.
- Any weakening for a team repository.
- Merging, releasing and choosing a version.
- Applying this to Phase 4's plan or its pull requests.

## Open questions

- **May the coordinator run `gh pr edit` on a pull request body?** Why: the template tells it to fill the description and the guard blocks it (guard log, Nov 27, 2026). Consequence: yes means a recorded owner go-ahead per pull request and a narrow guard allowance (a body file in the scratchpad, or an inline body); no means it gives one block to paste. Recommendation: no change to the guard; one paste block at ready time. Who: the owner. Answer:
- **Is the CI tick the CI confirmation?** Why: **Confirmed by** and the tick are two acts for one fact. Consequence: one fewer field. Recommendation: yes, with the commit hash written next to the tick. Who: the owner. Answer:
- **Is the guard log compared once per pull request?** Why: the Rule exceptions line comes from the Phase 2 guardrails work (INT-20). Consequence: fewer repeated checks; a breach is found later. Recommendation: yes, by the reviewer at the end; the coordinator only on a refusal. Who: the owner. Answer:
- **Widen the light path to any no-behavior change?** Why: it covers only text today (INT-26). Recommendation: yes for a solo repository, a human judges. Who: the owner. Answer:
- **Drop the file inventory and empty Needs and Provides lines from the plan template?** Recommendation: yes. Who: the owner. Answer:
- **Which release carries this?** Recommendation: the release after INT-28; do not hold Phase 4. Who: the owner. Answer:
