---
id: INT-26
title: Make finishing a phase clear and light for the human
author: Michael Hay
created: 2026-11-11
status: draft
affects: [bundles/base, docs/process, .github/workflows, GitHub ruleset on main]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Make finishing a phase clear and light for the human

## Problem
Finishing Phase 2 (INT-20 to INT-25) took a long session and was frustrating and unclear, in the owner's words. The process of INT-21, INT-22 and INT-23 works, but closing a phase costs the human more effort than the risk justifies, and it is hard to tell what is still open. Causes seen in that session:

1. **One fact lived in many places and the copies drifted.** CI confirmation, finding decisions and approvals were each recorded in some mix of the plan, `REVIEW_PLAN_N.md`, the PR body, the test plan and chat. The coordinating session told the owner approvals were blank when they were filled.
2. **Recording a decision restarted the check that confirms it.** Plan-only commits after review changed the head commit, which restarted CI, which needed a new human CI confirmation (ready-check item 3 in `docs/process/REVIEW_CYCLE.md`), which was recorded in another commit. The owner confirmed CI four times on effectively the same code.
3. **Agents spoke in internal IDs** (K5, CP2b, T37d, F4) and asked for decisions without saying what, why, the consequence and a default. The owner objected to shorthand lists.
4. **Two files disagree about findings.** `REVIEW_PLAN_N.md` keeps findings `open` (only the reviewer may revise it) while the decisions live in the plan.
5. **Ceremony is not scaled to risk.** This repository is solo (`AGENTS.md`, Review process) yet got the same amendment, approval-line and confirmation steps a team would. Even a text-only fix to shipped docs needs the full amendment round.
6. **"Ready to merge" and "ready to release" were run together.** No definition of done exists. Three deferred text findings ship in v0.2.0 as known issues because fixing them needed the amendment ceremony: `REVIEW_PLAN_2.md` F4 (shipped text says the hook was never seen live; the breach record shows one live refusal on 2026-11-09), F5 (the shipped `REVIEW_CYCLE.md` carries this repository's history and a pronoun) and F1 (the guard's stated limits do not name the write-capable tools it allows).
7. **Branch rules are written nowhere.** A GitHub ruleset on `main` still required a `test (3.8)` check after Python 3.8 was dropped from CI, so no PR could merge until the owner removed it by hand. The ruleset allows squash only, which breaks stacked PRs (they need a rebase after the squash). Neither fact is in a process document.
8. **Cross-worktree edits are blocked by a hook**, forcing delegation to another session for a one-file change.

## Proposed outcome
Finishing a phase is a short, predictable path in which the human is asked few questions, each in plain words, and can see at any time what remains.

1. **First task: ship the three deferred text fixes** (REVIEW_PLAN_2 F4, F5, F1) by the lighter path in item 5, so the pilot of the new path is real work.
2. **Record each fact once and link to it.** Each kind of fact (CI result, finding decision, approval) has one home; other documents link, not copy. Status that changes after review (CI confirmation, which finding is settled) lives in the PR, not in repository files, so recording it never changes the head commit.
3. **A definition of done with distinct levels:** mergeable, releasable, done. It lives in the phase plan or as a checklist the coordinator owns. The ready check names which level it proves.
4. **A deterministic phase status.** A slash command (for example `/phase-status <N>`) returns a structured list of what is open for a phase's plan files. It is backed by a read-only script, not an agent's recollection.
5. **Ceremony scaled to risk.** In a solo repository, a text-only fix to a shipped document or agent instruction has a lighter path than a full amendment round. A team repository keeps the full path.
6. **Fewer, clearer human steps.** The PR states what remains for the human, and per file what to review and which steps complete it. Approval is a tick of a checkbox in the PR. Finding decisions are batched, each with a recommendation and consequence, and answered with "accept all" or named exceptions.
7. **Every agent ask is self-contained:** what, why, consequence and default, with no bare internal IDs.
8. **Branch and merge rules are documented.** A process document records required checks, squash only, linear history, review count and bypass. The coordinator compares them with the workflows before a phase ends, so a stale required check is found by the check, not by a blocked PR. Stacked-PR handling under squash-only is written down.
9. **Reduce CI repeats.** Investigate whether CI can be skipped for docs-only changes without a loss of assurance (unverified; see Open questions).

## Affected users and systems
- **The owner**, who is the only human in this repository and carries every confirmation.
- **Agents:** `coordinator`, `reviewer`, `planner`, `coder`, whose instructions, rules and the files they write change.
- **Bundle contents:** `bundles/base/process/REVIEW_CYCLE.md`, `bundles/base/HOWTO.md`, `bundles/base/INSTALL.md`, `bundles/base/hooks/guard.py` (docstring only, F1), `bundles/base/rules/core/`, the PR and plan templates under `docs/templates/`, a slash command and its script, `bundles/base/tests/`, and the built outputs for the `claude` and `copilot` flavors.
- **Repository:** `.github/workflows/`, and the GitHub ruleset on `main` (a setting held on GitHub, not in a file).
- **Repositories that install the bundle**, which receive the changed process documents.

## Constraints
- **A human keeps the final say.** The coordinator still never approves, never moves a PR out of draft and never merges; only a human fills in **Approved by**, accepts an intent and decides to merge (`AGENTS.md` "Plan approval" and the Coordinator's definition; INT-22 constraint "A human decides"). Ticking a checkbox in the PR is a human act, never an agent's.
- **Ready still means reviewed.** A review of the final change, with findings repaired, deferred or rejected, and a human-confirmed CI result for the exact commit remain required before ready (INT-22 S2, S10; `REVIEW_CYCLE.md` "The ready check"). Streamlining changes where and how often these are recorded, not whether they are met.
- **Approval follows the review policy.** The approval rule in `AGENTS.md` "Review process" and INT-23 stays the rule; a solo repository may be lighter, a team is not weakened (INT-23 "Must never": require an approver who is not in the repository).
- **Independent review stays.** The reviewer still writes only `REVIEW_PLAN_N.md` and never reviews its own change; held-out scenarios stay with the quality side (`AGENTS.md`).
- **Both flavors.** Agent and template changes apply to `claude` and `copilot` from one canonical source (INT-22 constraint "Both flavors").
- **Deterministic build, standard library only** for any script and for `build.py` (INT-22 constraint).
- **Shipped text stays generic.** Text installed into other repositories carries no history or names specific to this repository (REVIEW_PLAN_2 F5).
- **Concise.** Documents follow the "Plan length" rule; this intent adds no new document where an existing one can be edited.
- **No outward action without the owner.** Changing the GitHub ruleset or the CI workflow, pushing and merging need the owner's go-ahead (INT-22 constraint).
- **Release scope.** v0.2.0 ships with F1, F4 and F5 as known issues; this intent does not hold that release.

## Scenario seeds

### S1 — The PR says what is left for me
**Who:** The owner opening a pull request at the end of a phase.
**Wants:** One place that states what remains for approval, and per file what to review and which steps complete it.
**So that:** Finishing takes one pass, with no hunting across plan, review file and chat.
**We will know when:** The PR description lists the remaining human steps, and for each changed file says what to check and what ticking it means; after the steps are done the list is empty.
**Must never:** List a step as open that is done, or as done that is open, or ask the owner to look in a file the PR does not link.

### S2 — A definition of done with levels
**Who:** The owner or the coordinator asking whether a phase is finished.
**Wants:** Distinct levels: mergeable, releasable, done.
**So that:** "Ready to merge" is never mistaken for "ready to release".
**We will know when:** The definition exists in one named place, each level lists its conditions, and the coordinator's closing report says which level has been reached and what is missing for the next.
**Must never:** Report a phase as done on the strength of mergeable, or let the coordinator or any agent declare done on its own (`human-confirms-closure`).

### S3 — A phase status I can trust
**Who:** The owner typing `/phase-status <N>`.
**Wants:** A structured list of what is open for that phase's plan files.
**So that:** The answer comes from the files, not from an agent's memory.
**We will know when:** The command prints the same list on repeated runs over unchanged files, names each open item with its file, and a read of the script shows it only reads.
**Must never:** Change any file, or report an item closed that the files show open.

### S4 — Each fact is recorded once
**Who:** The owner checking where a CI confirmation, a finding decision or an approval is recorded.
**Wants:** One home per kind of fact, with links from anywhere else.
**So that:** Copies cannot drift and no agent reports a filled approval as blank.
**We will know when:** The process document names the home of each kind of fact; after a phase, a search for the same decision finds one record and links.
**Must never:** Keep a second copy of a decision that can be edited separately from the first.

### S5 — Confirming CI is done once per code state
**Who:** The owner confirming CI before ready.
**Wants:** To confirm CI once for the code that will merge.
**So that:** Recording the confirmation does not create the need to confirm again.
**We will know when:** After CI is confirmed, no repository commit is needed to record that fact, and a later commit that does not change code needs no second confirmation; a commit that does change code does.
**Must never:** Mark a PR ready on a CI result from a different commit, or on a local pass alone (INT-22 S10).

### S6 — Decisions come in one batch, in plain words
**Who:** The owner asked to decide on review findings.
**Wants:** One list, each item saying what, why, the consequence and a default, answerable with "accept all" or named exceptions.
**So that:** Decisions take minutes and need no decoding.
**We will know when:** The list uses descriptions, not bare IDs, each has a recommendation, and a single reply settles the lot; each answer is recorded once.
**Must never:** Ask the owner to decide on an item known only by an internal ID, or apply a default the owner has not been shown.

### S7 — A small text fix to shipped docs is light
**Who:** The solo owner with a text-only fix to a shipped document (such as REVIEW_PLAN_2 F4, F5, F1).
**Wants:** A lighter path than a full amendment round.
**So that:** Such fixes are made instead of shipped as known issues.
**We will know when:** The three deferred findings are fixed by this path, each with a visible diff and a human tick, and the process document states which kinds of change may use it.
**Must never:** Let the light path cover code, rules or agent permissions, or apply in a team repository; or let it skip the human's approval.

### S8 — The branch rules are written and checked
**Who:** The coordinator before a phase ends, and a maintainer reading the process.
**Wants:** The branch and merge rules written down and compared with the workflows.
**So that:** A required check that no longer runs is found before it blocks a PR.
**We will know when:** A process document lists required checks, squash only, linear history, review count, bypass and how to stack PRs; the coordinator's report compares required checks with the job names in `.github/workflows/` and flags a mismatch.
**Must never:** Change the ruleset itself, or state a rule it has not read from the repository's settings.

### S9 — Every ask from an agent stands alone
**Who:** The owner reading any agent's question.
**Wants:** What is asked, why, the consequence and a default, in plain words.
**So that:** The answer is a yes or no, not a research task.
**We will know when:** A sample of asks from a phase run shows each with those four parts and no unexplained ID.
**Must never:** Present a list of bare IDs, or hide a consequence.

## Out of scope
- Merging, releasing and deploying, and choosing a version number.
- Changing review severity or the passes of the `reviewer` (INT-21, INT-23).
- Any weakening of approval for a team repository.
- Changing the GitHub ruleset or CI workflow themselves; this intent documents and checks them. Doing so is the owner's act.
- The cross-worktree edit hook (cause 8): noted, not changed here unless the owner decides (see Open questions).
- The UX for review and answer (INT-24).
- Re-reviewing Phase 2 beyond the three deferred findings.

## Open questions
- **Where does CI status live after confirmation?** The idea is the PR (a comment or checklist item) rather than a repository file, so recording it does not move the head commit. Recommendation: the PR checklist, with the coordinator reading the CI result and the human ticking it. Who: the owner.
- **Can CI be skipped for docs-only changes?** Unverified: confirm with the GitHub documentation on path filters and on how required checks behave when a workflow is skipped (a skipped required check can block a merge). Recommendation: investigate first, do not change `.github/workflows/` until the answer is known. Who: the planner, then the owner.
- **Which changes may use the light path?** Recommendation: only text in documents and agent instructions that changes no behavior, in a solo repository, with a human tick on the diff. Who: the owner.
- **Where does the definition of done live: in each phase plan or as one coordinator-owned checklist?** Recommendation: one checklist in `docs/process/`, referenced by the plan template, so it is not copied per phase. Who: the owner.
- **Does the PR checkbox count as the approval the plan's Approved by line records?** Recommendation: the checkbox approves the PR; the **Approved by** line of a plan stays a human-written line, since `AGENTS.md` "Plan approval" reads it. Who: the owner.
- **Should `REVIEW_PLAN_N.md` stay the home of finding state, or should decisions be recorded in the PR?** Recommendation: keep the reviewer's file as the record of what was found and the PR as the record of what was decided, with a link, so only the reviewer edits the first. Who: the owner.
- **Is the cross-worktree edit block (cause 8) deliberate?** A hook blocks it; the rule "Deliberate workarounds" says to read why before changing it. Recommendation: leave it and document the delegation route. Who: the owner, after the planner reads the hook.
- **Stacked PRs under squash-only:** document the rebase step, or ask the owner to allow rebase-merge? Recommendation: document only; the ruleset is the owner's to change. Who: the owner.
- **Bring this intent under the same plan as the v0.2.0 release or separately?** Recommendation: a separate phase, after v0.2.0 ships. Who: the owner.
