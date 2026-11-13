# PHASE_3_PLAN.md

**Approved by:** Michael Hay on November 11, 2026
**Source intent:** INT-26, `intent/INT-26-finishing-a-phase-clear-and-light.md` (accepted by Michael Hay, 2026-11-11, on branch `claude/intent-phase3-streamline`, commit c1d51c9, PR #31 still draft; the intent file arrives on `main` with that PR's merge, and the owner's answers are in its Open questions)

## Objective

Finishing a phase is a short path with few, plain questions for the owner and a status that can be read at any time. The three text findings deferred in Phase 2 (`REVIEW_PLAN_2.md` F4, F5, F1) are fixed instead of shipped as known issues. Each kind of fact (finding found, finding decision, CI result, approval) has one home. "Mergeable", "releasable" and "done" are defined once. A read-only `/phase-status <N>` lists what is open. The coordinator compares the written branch rules with the workflows. Agent questions are self-contained.

## Scope

**In scope:**

- CP1: F4, F5, F1 as text fixes, with the install refreshed.
- CP2: the process text in `bundles/base/process/REVIEW_CYCLE.md` (homes of facts, definition of done, light path), the PR template, the plan template's checklist.
- CP3: coordinator and rule text; `docs/process/BRANCH_RULES.md`; the docs-only CI investigation (finding only).
- CP4: `/phase-status` command and its read-only script, both flavors.

**Out of scope:**

- Merging, releasing and choosing a version number (intent Out of scope). The owner's answer is that this work ships in a new release, v0.3.0, a separate phase from v0.2.0; the release itself is not a task here.
- Changing the GitHub ruleset or any file in `.github/workflows/`; the plan documents and checks them only.
- The cross-worktree edit block (guard rule `protected-file`, deliberate per the `guard.py` docstring and Phase 2 CP2b R1): left as is, only the delegation route is documented.
- Review severities and passes (INT-21, INT-23); weakening approval for a team repository; the UX of INT-24.
- Noticed, not done: `REVIEW_PLAN_2.md` F6 (rename `test_reviewer_is_read_only_and_never_approves`, `bundles/base/tests/test_bundle.py:1328`), F2, F3, K5 (owner's items); F7 is already met (`AGENTS.md` "Project commands" now lists the bundle lint).

**Needs from other repositories:** None.

**Provides to other repositories:** Repositories that install the bundle receive the changed process documents, templates, agent text and the `/phase-status` command.

**Constraints:** A human keeps the final say: the coordinator never approves, never moves a PR out of draft, never merges; ticking a PR checkbox is a human act. Ready still means reviewed: a review of the final change, findings repaired/deferred/rejected, and a human-confirmed CI result for the exact commit. Approval follows `AGENTS.md` "Review process" and INT-23; a solo repository may be lighter, a team is not weakened. The reviewer still writes only `REVIEW_PLAN_N.md`; held-out scenarios stay with the quality side. Both flavors (`claude`, `copilot`) from one canonical source. Deterministic build, standard library only, for any script and `build.py`. Shipped text stays generic: no history or names specific to this repository. Concise: no new document where an existing one can be edited. No outward action without the owner: ruleset, CI workflow, push and merge need the owner's go-ahead. v0.2.0 ships with F1, F4, F5 as known issues; this plan does not hold that release (the owner's answer: the fixes go into v0.3.0).

## Concerns flagged

1. **The light path is needed by Task 1 but is defined in Task 8.** Owner decides: default is that Tasks 1 to 3 ship under this plan's **Approved by** line and the owner's tick on their diff in the PR, and Task 8 then records that path.
2. **F1 edits the docstring of `bundles/base/hooks/guard.py`, but the intent says the light path never covers code.** Owner decides: default is that the light path covers a comment or docstring only when the diff shows no other changed line, and the rule says so (Task 8).
3. **F4 asks shipped text to say a live refusal was seen, while shipped text must carry no repository history.** The plan words it without date or names ("a live refusal has been recorded for a Claude Code subagent"); the date and F9 go only in the unshipped traceability row (Task 2). Owner confirms.
4. **The intent's Constraints still say "v0.2.0 ships with F1, F4 and F5 as known issues", while the owner now says the fixes go into v0.3.0.** The plan follows the owner's answer; the owner may want the intent line updated (not done here).

## Definition of done: approach (NOT DECIDED; the owner confirms it when approving this plan)

The owner asked whether a DoD template for the coordinator is the way, or something else. Options:

- **A. A section "Definition of done" in `bundles/base/process/REVIEW_CYCLE.md`**, linked from the plan template and the coordinator. No new file; one home; the coordinator quotes the levels in its report. Weakness: it is a description, not a form to tick.
- **B. A coordinator-owned template** (`DONE_CHECKLIST_TEMPLATE.md`, copied into each PR). A tickable form, but a new shipped file, and a copy per phase that can drift (intent cause 1).
- **C. Per-plan text** in each phase plan's Completion checklist. Easy to read, but copied every phase.
- **Recommendation: A for the definition, and the PR's "What remains for you" list (Task 9) as the tickable form for the current phase.** That gives one home for the levels and a per-PR checklist built from them, with no new template. If the owner picks B, Task 8 instead CREATEs the template and the inventory gains one file; if C, Task 8 changes only the plan template.

## Prerequisites

- [x] INT-26 accepted (c1d51c9 on `claude/intent-phase3-streamline`, PR #31 draft); the file reaches this repository's `main` with that PR's merge.
- [x] Phase 2 merged (`b19f54c`); `docs/plans/REVIEW_PLAN_2.md` present.
- [x] Project commands known: `AGENTS.md` "Project commands" (bundle lint `python3 bundles/base/tools/build.py --check`; bundle tests `.venv/bin/python -m pytest bundles/base/tests -q`; `pytest` in this plan means the server tests command).
- [ ] The `.venv` exists (`python3 -m venv .venv`, then the install line in `AGENTS.md`).
- [ ] The owner confirms the definition-of-done approach below (at plan approval).
- [ ] For Task 11 only: the owner's go-ahead to read the GitHub ruleset with `gh`.

## File inventory

| Path                                                                                               | Action          | Reason                                                                      |
| -------------------------------------------------------------------------------------------------- | --------------- | --------------------------------------------------------------------------- |
| `bundles/base/INSTALL.md`                                                                          | MODIFY          | F4 (lines 78, 91)                                                           |
| `bundles/base/HOWTO.md`                                                                            | MODIFY          | F4 (line 120)                                                               |
| `docs/plans/PHASE_2_PLAN.md`                                                                       | MODIFY          | F4: last cell of the "INT-20 S1" traceability row (line 1146) only          |
| `bundles/base/process/REVIEW_CYCLE.md`                                                             | MODIFY          | F5; homes of facts, definition of done, light path, ready check             |
| `bundles/base/hooks/guard.py`, `docs/agents/harness-capabilities.md`                               | MODIFY          | F1 (docstring and its mirror, one line each)                                |
| `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `bundles/base/templates/PHASE_PLAN_TEMPLATE.md` | MODIFY          | remaining-steps checklist; link to the definition of done                   |
| `bundles/base/agents/coordinator.agent.md`, `bundles/base/rules/core/ask-on-ambiguity.md`          | MODIFY          | ready check, levels, batched decisions, self-contained asks                 |
| `docs/process/BRANCH_RULES.md`                                                                     | CREATE          | branch and merge rules, stacked PRs, CI for docs-only changes (not shipped) |
| `bundles/base/scripts/phase_status.py`                                                             | CREATE          | read-only phase status                                                      |
| `bundles/base/commands/phase-status.md` (claude) and the copilot equivalent                        | CREATE          | the slash command                                                           |
| `bundles/base/tools/build.py`, `bundles/base/install.py`                                           | MODIFY          | payload, lint and install of the script and command                         |
| `bundles/base/tests/test_bundle.py`, `bundles/base/tests/test_phase_status.py`                     | MODIFY / CREATE | tests next to each change                                                   |
| `.claude/agents/*`, `.manifold/*`, `docs/process/*`, `docs/templates/*`                            | MODIFY          | refresh of this repository's own install (generated, from the build)        |

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

### CP1 — Ship the three deferred text fixes

### Task 1 — Fix the "never seen live" statements (REVIEW_PLAN_2 F4)

**Files:** `bundles/base/INSTALL.md`, `bundles/base/HOWTO.md`
**Action:** MODIFY
**Change:** In `INSTALL.md` line 78 (table row, Claude Code subagent) replace "Documented, not yet seen in a live run: the recorded runs captured no guard log." with "Documented, and a live refusal has been recorded for a subagent." In `INSTALL.md` line 91 replace "None of this has been recorded in a live client yet;" with "A live refusal has been recorded only for a Claude Code subagent, and for no other row;". In `HOWTO.md` line 120 replace "none of it has been recorded in a live run yet, so treat it as "no evidence yet"" with "the only live evidence recorded is one refusal in a Claude Code subagent; for every other client or mode treat it as "no evidence yet"". Keep "not seen" for Copilot, `--agent` and plugins. No date, no finding ID.
**Acceptance:** `grep -n "not yet seen in a live run\|recorded in a live" bundles/base/INSTALL.md bundles/base/HOWTO.md` prints nothing; `git diff --stat` shows only these two files.
**Todo:** [x]
Note (2026-11-11): INSTALL.md lines 78 and 91 and HOWTO.md line 120 reworded as written; `grep -n "not yet seen in a live run\|recorded in a live" bundles/base/INSTALL.md bundles/base/HOWTO.md` prints nothing. The `git diff --stat` acceptance reads on the whole CP1 diff; the two files here are only the F4 text files (the rest is Tasks 2 to 6).

---

### Task 2 — Correct the INT-20 S1 traceability row (F4)

**Files:** `docs/plans/PHASE_2_PLAN.md` (line 1146, last cell only)
**Action:** MODIFY
**Change:** Replace "no live-client evidence yet" with "one live refusal in a Claude Code subagent, 2026-11-09 (`docs/agents/claude-desktop-failures.md` F9); none yet for Copilot, `--agent`, plugins". No other line of the file changes.
**Acceptance:** `git diff -U0 docs/plans/PHASE_2_PLAN.md` shows one changed line.
**Todo:** [x]
Note (2026-11-11): last cell of the INT-20 S1 row replaced as written (owner's decision: Open question 4, yes, that cell only). `git diff -U0 docs/plans/PHASE_2_PLAN.md` -> one hunk (`@@`), one line removed and one added.

---

### Task 3 — Remove repository history and the pronoun from the shipped review cycle (F5)

**Files:** `bundles/base/process/REVIEW_CYCLE.md` (lines 52 to 62)
**Action:** MODIFY
**Change:** Delete the section "How the first cycles ran" and its table (the record already exists in `docs/plans/PHASE_2_PLAN.md`, CP2a and CP2b). Keep the lessons paragraph under the new heading "What earlier cycles taught", with no mention of Manifold, Phase 2, CP2a, CP2b or any person's pronoun ("the owner", not "his"). Check that nothing links to the deleted heading: `grep -rn "first cycles" bundles docs README.md`.
**Acceptance:** `grep -n "Phase 2\|CP2\| his \|first cycles ran" bundles/base/process/REVIEW_CYCLE.md` prints nothing.
**Todo:** [x]
Note (2026-11-11): section "How the first cycles ran" and its table deleted from `bundles/base/process/REVIEW_CYCLE.md`; the lessons paragraph now sits under "What earlier cycles taught" and starts "These lessons are now part of the steps:". `grep -n "Phase 2\|CP2\| his \|first cycles" bundles/base/process/REVIEW_CYCLE.md` -> nothing; `grep -rn "first cycles" bundles docs README.md` -> only the installed copy `docs/process/REVIEW_CYCLE.md` (refreshed in Task 6) and the historical plan/review records, no link to the heading.

---

### Task 4 — Name the allowed write-capable tools in the guard's stated limits (F1)

**Files:** `bundles/base/hooks/guard.py` (docstring line 77), `docs/agents/harness-capabilities.md` (line 75)
**Action:** MODIFY
**Change:** Replace the line "other languages, editors and tools than the ones named in the shell rule;" with "other languages, editors and tools than the ones named in the shell rule (for example `dd of=`, `curl -o`, `wget -O`, `tar x`, `unzip`, `install`, `python3 -m json.tool in out` are allowed although they write files);" in both files, in the same words. Change no line outside the docstring.
**Acceptance:** `git diff -U0 bundles/base/hooks/guard.py` shows one changed line, inside the docstring (it ends before `from __future__`); the existing parity test between the docstring and `harness-capabilities.md` (if any) passes in Task 6.
**Todo:** [x]
Note (2026-11-11): the "other languages, editors and tools" line in the guard.py docstring (line 77) and in `docs/agents/harness-capabilities.md` (line 75) replaced with the same words. `git diff -U0 bundles/base/hooks/guard.py` -> one hunk, one line, inside the docstring. No parity test exists between the two files (none found by grep); the full bundle suite passes (Task 6).

---

### Task 5 — Add a test that pins the three fixes

**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_deferred_text_fixes_f1_f4_f5`: the shipped `REVIEW_CYCLE.md` contains none of `Phase 2`, `CP2a`, `CP2b`, ` his `; `INSTALL.md` and `HOWTO.md` do not contain "not yet seen in a live run"; the `guard.py` docstring names `curl -o`. Follow the style of `test_t35_user_documents_link_nothing_outside_the_zip_and_name_no_bundle_version` (line 2230).
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` shows 1 passed. Failing-first: the note records the failing run of this test on the unchanged files, made by writing the test before applying Tasks 1 to 4 locally (the order in the plan is the order of the commits, not of the first run).
**Todo:** [x]
Note (2026-11-11): added `test_deferred_text_fixes_f1_f4_f5` (also checks "recorded in a live" is gone, to cover the HOWTO wording). Failing first, on the unchanged files: `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` -> 1 failed, 1955 deselected. After Tasks 1 to 4: same command -> 1 passed, 1955 deselected.

---

### Task 6 — Refresh this repository's own install from the build

**Files:** `.manifold/hooks/guard.py`, `.manifold/manifest.json`, `docs/process/REVIEW_CYCLE.md`, `docs/process/HOWTO.md`
**Action:** MODIFY
**Change:** Build into the scratchpad (`python3 bundles/base/tools/build.py --out <scratchpad>/dist`) and install over this repository with the command and flags recorded in the Phase 2 T38 note (`docs/plans/PHASE_2_PLAN.md`); read `install.py --help` first, do not guess flags. `INSTALL.md` is not installed (not in the manifest). Stage explicit paths only.
**Acceptance:** `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes with no failures; `.manifold/hooks/guard.py` equals `bundles/base/hooks/guard.py` (`cmp`); `install.py --status` reports no modified file.
**Todo:** [x]
Note (2026-11-11): `python3 bundles/base/tools/build.py --out <scratchpad>/dist` -> zip built (sha256 932121eee04c66f4...), unzipped into a fresh scratchpad folder; `install.py --help` read first. From that unzipped bundle: `install.py --target . --format claude --profile build` (dry run: UPDATE only `docs/process/REVIEW_CYCLE.md`, `docs/process/HOWTO.md`, `.manifold/hooks/guard.py`; everything else SKIP), then the same with `--apply` (no `--force`) -> "Installed manifold 0.2.0". `git status --short` shows only those three files plus `.manifold/manifest.json` as installed changes. `build.py --check` -> `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` -> 1955 passed, 1 skipped; `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` -> equal; `install.py --status` (run from the unzipped bundle, because the source folder has no `bundle.json`) -> 23 files `ok`, none MODIFIED. The guard did not block the install.

---

**Verification:** `.venv/bin/python -m pytest bundles/base/tests -q` and `python3 bundles/base/tools/build.py --check` pass with counts reported; `git diff origin/main --stat` lists only the files in Tasks 1 to 6. The owner reads the diff of Tasks 1 to 4 in the PR and ticks it (the pilot of the light path; see Concerns 1).

Rule exceptions: not established: the coder session's shell commands and transcript for CP1 (commits 996bcbd, aabccb3) are not available, and `.manifold/guard-log.jsonl` holds one entry only (a reviewer `write-allowlist` event of 2026-11-11T20:03:10Z in another worktree, after these commits), so it says nothing about the CP1 session. The diff 3e2bbaf..aabccb3 touches only files named in Tasks 1 to 6 (plus `.manifold/manifest.json`, an install output).

### CP2 — One home per fact, definition of done, light path (documents)

### Task 7 — Add the table of homes of facts to the review cycle

**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** MODIFY
**Change:** Add a section "Where each fact is recorded" with one row per kind of fact and its single home; every other document links to it and never copies it: what was found (`docs/plans/REVIEW_PLAN_<N>.md`, only the `reviewer` edits it); what was decided about a finding (a comment or checklist in the pull request, linking the finding; a plan's amendment still carries the repair tasks); the CI confirmation (a tick in the pull request, never a commit); approval of a plan (its **Approved by** line, written by a human; unchanged); approval of the pull request (the checkbox in the pull request). In the section "The ready check" change item 2 to "each finding has a decision recorded in the pull request (the reviewer's file keeps it `open`)" and item 3 to "CI of that exact commit has been read by the `coordinator` and ticked by a human in the pull request; a commit that changes no code needs no second confirmation, a commit that changes code does". Do not remove "a run for an older commit is not the result".
**Acceptance:** `grep -n "Where each fact is recorded" bundles/base/process/REVIEW_CYCLE.md` finds the heading; the file's table has five rows; `grep -c "never a commit" bundles/base/process/REVIEW_CYCLE.md` prints 1 or more.
**Todo:** [x]
Note (2026-11-11): section "Where each fact is recorded" (five-row table) added before "The ready check"; ready-check items 2 and 3 reworded as written, "A run for an older commit is not the result" kept. Item 2 also ends with ": repaired, deferred or rejected", because the existing test `test_review_cycle_ready_check_leaves_the_decisions_to_a_human` pins that phrase in the ready check (it failed once without it); no existing test was edited. Checks: `grep -n "Where each fact is recorded"` finds the heading; five table rows; `grep -c "never a commit"` -> 1.

---

### Task 8 — Add the definition of done and the light path

**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** MODIFY
**Change:** (Written for option A; follow the owner's choice under "Definition of done: approach".) Add "Definition of done" with three levels and their conditions: **mergeable** (the four ready-check lines met and a human ticked the pull request); **releasable** (mergeable, merged, the gates of `AGENTS.md` "Project commands" green on the merge commit, and the owner chose a version); **done** (releasable, the plan's completion summary written, a human wrote the closure; `human-confirms-closure`). Add "Light path for text fixes": only in a repository whose `Review process` says solo; only text in documents and agent instructions that changes no behavior (a comment or docstring qualifies only when the diff shows no other changed line); never code, rules, agent permissions, hooks or tests; the diff is shown in the pull request and a human ticks it; a team repository uses the full amendment round. State that the coordinator's closing report names the level reached and what the next level lacks.
**Acceptance:** `grep -n "mergeable\|releasable\|Light path" bundles/base/process/REVIEW_CYCLE.md` finds each; reading the section shows each level with a list of conditions and the sentence "never code, rules, agent permissions, hooks or tests".
**Todo:** [x]
Note (2026-11-11): option A as written. Sections "Definition of done" (mergeable, releasable, done, each with its conditions; the coordinator's closing report names the level and what the next lacks) and "Light path for text fixes" (solo only; text only; docstring/comment only when no other line changed; "never code, rules, agent permissions, hooks or tests"; diff shown in the PR and ticked by a human; team uses the full amendment round) added after "The ready check". `grep -n "mergeable\|releasable\|Light path"` finds each.

---

### Task 9 — Add the remaining-steps list to the pull request template

**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `bundles/base/templates/PHASE_PLAN_TEMPLATE.md`
**Action:** MODIFY
**Change:** In the PR template add a section "What remains for you" of checkboxes: one line per changed file, saying what to check and what the tick means; one line "CI of commit <full hash> is green (read by the coordinator)"; one line "Findings: decisions below"; and a "Decisions for you" table whose columns are: what, why, consequence, default (no bare IDs; the reply "accept all" settles every default). Replace the template comment text so the Ready check lines link to "Where each fact is recorded" instead of restating it. In the plan template's Completion checklist add one line linking to "Definition of done" in `docs/process/REVIEW_CYCLE.md` and naming the level the plan aims at.
**Acceptance:** `grep -n "What remains for you\|Decisions for you" bundles/base/templates/PULL_REQUEST_TEMPLATE.md` finds both; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [x]
Note (2026-11-11): PR template gains "What remains for you" (per-file line, CI-of-commit line, findings line) and "Decisions for you" (columns What, Why, Consequence, Default; "accept all"); the Ready check comment links to "Where each fact is recorded" and its lines 2 and 3 follow the new wording. Plan template Completion checklist gains the "Level aimed at" line linking "Definition of done". `grep -n "What remains for you\|Decisions for you"` finds both; `build.py --check` -> `lint ok`.

---

### Task 10 — Add tests for Tasks 7 to 9

**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_review_cycle_names_homes_levels_and_light_path` (the three headings exist; the light-path section contains "solo" and "never code"; item 3 of the ready check contains "never a commit" or the equivalent sentence) and `test_pr_template_has_remaining_steps_and_decisions_table`. Failing first: run both before Tasks 7 to 9 are applied to the source, record the counts.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "review_cycle_names or pr_template_has"` shows 2 passed.
**Todo:** [x]
Note (2026-11-11): added both tests (after `test_deferred_text_fixes_f1_f4_f5`). Failing first, before Tasks 7 to 9 were applied: `.venv/bin/python -m pytest bundles/base/tests -q -k "review_cycle_names or pr_template_has"` -> 2 failed, 2034 deselected. After Tasks 7 to 9: same command -> 2 passed, 2034 deselected. (After that run I changed one assertion of the first test from the whole file to the ready-check section; both tests failed on their first assertion before, and still do on the old text.)

---

**Verification:** `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported); `python3 bundles/base/tools/build.py --check` prints `lint ok`; the built `claude` and `copilot` outputs both contain the new PR template text (`build.py --out` twice, `cmp` equal; deterministic).

Gates (2026-11-11): `.venv/bin/python -m pytest bundles/base/tests -q` -> 2035 passed, 1 skipped; `python3 bundles/base/tools/build.py --check` -> `lint ok`; `build.py --out <scratchpad>/cp2a` and `--out <scratchpad>/cp2b` -> `manifold-base-0.2.0.zip` in each, same size and sha256, `cmp` equal. `build.py` has no flavor flag (`--help`: `--check`, `--out`): one zip carries both flavors, and the PR template and review cycle are in `payload/common/` for both, containing "What remains for you", "Decisions for you" and "Light path for text fixes" (read from the zip with Python).

Rule exceptions (CP2, coder's own): none broken. One attempt was refused by the guard (rule `no-heredocs`): I started a pointless `python3 - <<EOF` snippet with no purpose and it was blocked before it ran; nothing was written, and I did not retry or work around it. No file was written from a shell command; no commit, push or staging.

### CP3 — Coordinator, plain asks, branch rules

### Task 11 — Read the ruleset and write `docs/process/BRANCH_RULES.md`

**Files:** `docs/process/BRANCH_RULES.md` (CREATE)
**Action:** CREATE
**Change:** With the owner's go-ahead, read the ruleset on `main` with `gh` (read only). Verify the command first: `gh api --help` and the GitHub rulesets API page; mark anything not verified "unverified: confirm with <source>". Record only what was read: required checks (by job name), squash only, linear history, review count, bypass actors. Add the stacked-PR steps under squash-only (the rebase of the dependent branch onto `main` after the base PR is squashed; verify the exact `git rebase` form with `git rebase --help`), and the route for editing agent definitions from another worktree (delegate to a session in that worktree; the guard's protection of definitions is deliberate). Add a section "CI for docs-only changes" holding the investigated answer (path filters, how a required check behaves when its workflow is skipped), with the source for each statement; recommend, do not change `.github/workflows/`.
**Acceptance:** each rule in the file shows the command or page it came from; `git diff --stat -- .github` is empty.
**Todo:** [x]
Note (2026-11-12): read with `gh` 2.86.0 (signed in already, `gh auth status`; `gh api --help` read first), GET only: `gh api --method GET repos/{owner}/{repo}/rulesets`, `.../rulesets/26275761`, `.../rules/branches/main`; the endpoints were checked against https://docs.github.com/en/rest/repos/rules. `docs/process/BRANCH_RULES.md` created: required checks `test (3.10)` and `test (3.12)` (match `ci.yml` job `test` and its matrix), squash only, linear history, 1 approving review, stale reviews dismissed, threads resolved, strict up-to-date, no deletion or force push, bypass for OrganizationAdmin and RepositoryRole 5 via pull request only (what role 5 is: unverified; the tag ruleset `protect-release-tags` listed, not read: unverified). Stacked-PR steps use `git rebase --onto` (read in `git rebase --help`); the delegation route is documented. Docs-only CI finding: neither `ci.yml` nor `server.yml` has a path filter, so nothing is skipped today; a path filter on `ci.yml` would leave the required checks Pending and block the merge (GitHub "Workflow syntax" page, read 2026-11-12); behaviour of a job skipped by `if:` is unverified (the "Troubleshooting required status checks" URL tried gave HTTP 404). Recommendation only. `git diff --stat -- .github` -> empty.

---

### Task 12 — Add the level report, the PR-tick CI flow and the branch-rules comparison to the coordinator

**Files:** `bundles/base/agents/coordinator.agent.md`
**Action:** MODIFY
**Change:** In "CI of the exact commit" and "Ready check": the coordinator writes the CI result for the exact commit into the pull request's remaining-steps list for the human to tick, and records no commit for it; the closing report names the level reached (mergeable, releasable, done) and what the next level lacks, and never declares done; decisions are presented as one batch (what, why, consequence, default; "accept all" or named exceptions) with no bare IDs. Add a step "Branch rules": if the repository has a branch-rules document, compare its required check names with the job names in `.github/workflows/` and report a mismatch; never change the ruleset.
**Acceptance:** `grep -n "Branch rules\|mergeable\|accept all" bundles/base/agents/coordinator.agent.md` finds each; both builds (`--out`) render the text for `claude` and `copilot`.
**Todo:** [x]
Note (2026-11-12): in `coordinator.agent.md`: the "CI of the exact commit" section gains a bullet (result written into the PR's remaining-steps list for a human to tick, no commit, every commit its own read and tick); the "Ready check" paragraph names the decision in the PR and the tick; a batch-of-decisions paragraph (what, why, consequence, default; "accept all"; no bare IDs); new section "Branch rules" (compares required check names with workflow job names, never changes the ruleset); the closing report names the level reached and what the next lacks, never declares done. Two of my first wordings broke existing tests (`test_t33_coordinator_carries_every_intent_duty_and_the_owner_decisions` pins "a human confirms"; the reference check flagged a path to `docs/process/BRANCH_RULES.md`, which is not shipped); I changed my wording, edited no test. Built zip contains both flavor files `coordinator.md` and `coordinator.agent.md` with the text.

---

### Task 13 — Require self-contained asks in every agent

**Files:** `bundles/base/rules/core/ask-on-ambiguity.md`
**Action:** MODIFY
**Change:** Under "Instead" add: every ask states what is asked, why, the consequence and the default, in plain words, and never names an item only by an internal ID (task, checkpoint, finding or open-question number) without saying what it is. Add `coordinator` to `applies_to`.
**Acceptance:** `python3 bundles/base/tools/build.py --check` prints `lint ok`; the rendered `coordinator` agent contains the rule (`grep -n "internal ID"` on the built file).
**Todo:** [x]
Note (2026-11-12): `ask-on-ambiguity.md`: `coordinator` added to `applies_to`; the "Instead" text gains the self-contained-ask sentence (what, why, consequence, default, no bare internal ID). No existing test pins this rule's `applies_to` or text (grep found none). `build.py --check` -> `lint ok`; `unzip -p` of both rendered coordinator files -> "internal ID" 2 hits (one per flavor).

---

### Task 14 — Add tests for Tasks 12 and 13

**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_coordinator_reports_level_and_compares_branch_rules` and `test_ask_rule_requires_self_contained_asks_for_coordinator`. Failing first, counts recorded. If an existing test pins the managed rules block or a rule's `applies_to`, stop, name the test and assertion, and ask the owner before editing it.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "coordinator_reports_level or self_contained_asks"` shows 2 passed.
**Todo:** [x]
Note (2026-11-12): added `test_coordinator_reports_level_and_compares_branch_rules` and `test_ask_rule_requires_self_contained_asks_for_coordinator` (before `test_pr_template_has_remaining_steps_and_decisions_table`). Failing first, before Tasks 12 and 13: `.venv/bin/python -m pytest bundles/base/tests -q -k "coordinator_reports_level or self_contained_asks"` -> 2 failed, 2037 deselected. After: same command -> 2 passed, 2037 deselected. No existing test pinned the rule's `applies_to` or text; `git diff -U0 bundles/base/tests/test_bundle.py` -> 0 removed lines.

---

**Verification:** full bundle tests pass with counts; `docs/process/BRANCH_RULES.md` read by the owner (the only first-hand statement of the ruleset); the owner confirms the docs-only CI finding before any workflow change is planned.

Gates (2026-11-12): `.venv/bin/python -m pytest bundles/base/tests -q` -> 2038 passed, 1 skipped; `python3 bundles/base/tools/build.py --check` -> `lint ok`; `build.py --out <scratchpad>/cp3a` and `--out <scratchpad>/cp3b` -> same size (339016 bytes), `cmp` equal. Server tests, live checker tests and vendor check: not run (CP3 changes no server code). Verification status: the full tests pass; the owner's reading of `docs/process/BRANCH_RULES.md` and confirmation of the docs-only CI finding are pending. Task 18 (installed copy refresh) not run, as planned.

Rule exceptions (CP3): one attempt refused by the guard (rule `no-heredocs`): I appended a stray `python3 - <<'X'` snippet to a verification command; it was blocked before it ran, nothing was written, and I re-ran the command without it. Every `gh` call was GET: `gh --version`, `gh auth status`, `gh api --help`, `gh repo view --json ...`, `gh api --method GET repos/{owner}/{repo}/rulesets`, `gh api --method GET repos/{owner}/{repo}/rulesets/26275761`, `gh api --method GET repos/{owner}/{repo}/rules/branches/main`. No ruleset, setting or workflow changed; no commit, push or staging; no installed copy edited.

### CP4 — `/phase-status`

### Task 15 — Verify the command formats of both flavors

**Files:** none changed; note in this task
**Action:** none (read)
**Change:** Read the Claude Code documentation for a project slash command file (location, frontmatter, how a command runs a shell command) and the GitHub Copilot equivalent (prompt files). Record each fact with its source, or "unverified: confirm with <source>". Settle whether `claude` and `copilot` get a command and `skills` gets an instruction only.
**Acceptance:** the note lists, per flavor, the file path and the source read.
**Todo:** [x]
Settled (2026-11-12): the owner chose option (a) ("A please"). `copilot` ships `.github/prompts/phase-status.prompt.md`, which tells the agent to run `python3 .manifold/phase_status.py <N>` and paste the output unedited, and states the limit in the shipped text: it is the agent's act, not a deterministic read; prompt files run only in the Local harness, which is deprecated with planned removal in February 2027. `claude` ships `.claude/commands/phase-status.md` with `allowed-tools: Bash(python3 *)` and the inline form `` !`python3 .manifold/phase_status.py $ARGUMENTS` ``. `skills` gets an instruction line only (in the generated instructions block, for the `skills` and `both` styles), marked unverified there. The shipped Copilot wording was checked against the facts below: it uses only the frontmatter keys `name`, `description`, `argument-hint` and the variable form `${input:variableName}` that the page lists, claims nothing about a shell tool, and cites the "no documented way to run a command" and the deprecation as read. Not verified (and not claimed in shipped text): that a shell tool is available to a prompt file run, and the behaviour of `${input:...}` when the argument is typed after the command (the page says typed text is passed along).
Original note (2026-11-12), read-only web reads with WebFetch, three pages:
- `claude`: file `.claude/commands/<name>.md` creates `/<name>`; a skill `.claude/skills/<name>/SKILL.md` is equivalent and the page recommends skills for new work; subdirectories namespace the command. Frontmatter (all optional): `description`, `argument-hint`, `allowed-tools`. `$ARGUMENTS` expands to the full argument string. A command file runs a shell command with the inline form `` !`<command>` `` (output replaces the placeholder; `!` at line start or after whitespace) or a fenced block opened with ` ```! `. The command is checked against permission rules; `allowed-tools: Bash(python3 *)` pre-approves it; a failed command aborts the invocation. Source: https://code.claude.com/docs/en/slash-commands (first 100,000 of 119,051 characters read; the rest not read).
- `copilot`: prompt file `.github/prompts/<name>.prompt.md`. Frontmatter: `description`, `name`, `argument-hint`, `agent`, `model`, `tools`. Text typed after the command is passed along; `${input:variableName}` for inputs. The page documents NO way for a prompt file to run a shell command or script itself: the body is prompt text for the agent, and `tools` / `#tool:<name>` only select tools; whether a shell tool is available is not stated. The page says prompt files run only in the Local harness, which is deprecated and to be removed in February 2027, and suggests agent skills instead. Source: https://code.visualstudio.com/docs/copilot/customization/prompt-files. A second page (https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files) answered none of these questions: unverified: confirm with the Copilot Chat documentation for the CLI and Copilot harness.
- `skills`: no slash command read for this flavor; an instruction line is the plan's default (Open question 3), not verified here.
Result: the Copilot prompt file cannot run `python3 .manifold/phase_status.py` itself; it could only ask the agent to run it, which is the agent's act, not a deterministic read. This is the stop condition of the CP4 instructions. Tasks 15 to 18 stopped here pending the owner's decision; nothing else was done.

---

### Task 16 — Create the read-only phase status script with tests

**Files:** `bundles/base/scripts/phase_status.py` (CREATE), `bundles/base/tests/test_phase_status.py` (CREATE)
**Action:** CREATE
**Change:** Standard library only, Python 3.10. `main(argv)` takes the phase number and optional `--root`; it reads `docs/plans/PHASE_<N>_PLAN.md`, `PHASE_<N>_TEST_PLAN.md` and `REVIEW_PLAN_<N>.md` and prints, sorted and identical on repeated runs: unticked (`[ ]`) and blocked (`[~]`) task lines with file and line number; blank **Approved by** and **Amendment approved by**; unticked Completion checklist lines; the open count of the latest review revision; the highest level of the definition of done the files support, or "cannot tell from files" for the CI tick, which lives in the PR. It opens files only for reading. Tests: fixture plans in `tmp_path`; same output twice; file contents and mtimes unchanged after a run; an AST check that no call opens a file for writing; a filled approval is never reported blank; exit 2 and a plain message for a missing plan.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` passes (counts reported); `.venv/bin/python bundles/base/scripts/phase_status.py 2` runs against this repository's Phase 2 files and prints the open items.
**Todo:** [x]
Note (2026-11-12): created `bundles/base/scripts/phase_status.py` (standard library only; `main(argv)`; reads with `Path.read_text` only; HTML comments are blanked first so template hints are not read as tasks, line numbers stay true; default root is the current directory, `--root` overrides; exit 2 with a plain message for a bad argument or a missing plan) and `bundles/base/tests/test_phase_status.py` (21 tests: open, blocked, checklist, review and approval lines; line numbers; same output twice; contents and mtimes unchanged; run as a program; default root; filled approval never blank (3 values) and blank forms (4 values); a clean phase reaches only "the files support mergeable" and says the CI tick, releasable and done cannot be told from files; exit 2 for a missing plan and for 5 bad argument lists; an AST check that no call is `open()` or any write, delete, rename or mkdir call, nor `print(file=...)` other than to `sys.stderr`; `build.lint_hook` finds no non-stdlib import). The plan lists no failing-first run for this task; the tests were written after the script and were not run against a missing script. `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` -> 21 passed. `.venv/bin/python bundles/base/scripts/phase_status.py 2` -> ran on this repository's Phase 2 files: 0 unticked, 0 blocked, 0 unticked checklist lines, 4 approval lines all filled, `REVIEW_PLAN_2.md` revision 1 with 7 open findings (F1 to F7), level "the files support mergeable".

---

### Task 17 — Ship the script and the command in the build and the install

**Files:** `bundles/base/tools/build.py` (`build_payload`, `lint`), `bundles/base/install.py`, `bundles/base/commands/phase-status.md` (CREATE) and the copilot file named by Task 15 (CREATE), `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add the script to the payload as `.manifold/phase_status.py` (every profile, like `.manifold/hooks/guard.py`), lint it as standard library only (reuse `is_stdlib` and `lint_hook`'s check), add the command file per flavor so it runs `python3 .manifold/phase_status.py $ARGUMENTS` (exact syntax from Task 15), list both in the manifest, and let `--uninstall` remove them. Tests: installed and uninstalled in each profile and flavor, two builds byte-equal, the script is in the manifest.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q` passes; `python3 bundles/base/tools/build.py --check` prints `lint ok`; two `--out` builds compare equal with `cmp`.
**Todo:** [x]
Note (2026-11-12): `build.py`: new `SCRIPT_FILES` (`scripts/phase_status.py` -> `.manifold/phase_status.py`, every profile, in the payload next to the guard, linted with `lint_hook`: compiles, standard library only) and `COMMAND_FILES` (claude: `commands/phase-status.md` -> `.claude/commands/phase-status.md`; copilot: `commands/phase-status.prompt.md` -> `.github/prompts/phase-status.prompt.md`; every profile; listed in `bundle.json` `formats`, so the manifest and `--uninstall` carry them); lint checks both exist, have frontmatter, run `python3 .manifold/phase_status.py`, and the claude one has `allowed-tools: Bash(python3 *)` and the inline form; the commands folder is added to the forbidden-term scan. The skills flavor gets one instruction line in the generated block (styles `skills` and `both`), marked unverified. `install.py` needed no change (a format entry without a role is already chosen by profile, as for the Copilot hook file), so that listed file is unchanged. Command files: `bundles/base/commands/phase-status.md` and `phase-status.prompt.md`. 18 new tests at the end of `test_bundle.py` (installed in each of 3 profiles x 3 flavors and uninstalled to an empty tree; both/all; zip and manifest entries; two builds byte-equal; command wording; skills line; 3 lint-rejection tests; installed script runs); no existing test edited. Failing first, before the `build.py` change: `.venv/bin/python -m pytest bundles/base/tests/test_bundle.py -q -k "phase_status or phase_status_files or two_builds_are_byte_equal_and_carry or claude_command_pre_approves or copilot_prompt_states or skills_instruction_names or both_and_all_formats_install_both or installed_script_runs"` (selects the 18 new tests) -> 16 failed, 2 passed (the 2 passes check only the command files, which already existed); after: full suite `.venv/bin/python -m pytest bundles/base/tests -q` -> 2078 passed, 1 skipped (CP7 had 2039 passed, 1 skipped; +21 +18); `python3 bundles/base/tools/build.py --check` -> `lint ok`; two `--out` builds -> 344969 bytes each, `cmp` equal.

---

### Task 18 — Refresh the install and run every gate

**Files:** this repository's own install (as Task 6)
**Action:** MODIFY
**Change:** Rebuild and install as in Task 6; add one line to `bundles/base/HOWTO.md` naming `/phase-status <N>`.
**Acceptance:** `python3 bundles/base/tools/build.py --check` → `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q`; `cd server && ../.venv/bin/python -m pytest -q`; `.venv/bin/python -m pytest tests/live -q`; `.venv/bin/python tools/vendor_web.py --check`; all with real counts. In a client, `/phase-status 3` prints this plan's open items (observed, or "not run" with the reason).
**Todo:** [x]
Note (2026-11-12): `bundles/base/HOWTO.md` "How to start" gains item 6 naming `/phase-status <N>` (and its two limits: Copilot prompt file runs only in the Local harness and is the agent's act; elsewhere ask the agent to run the script). Then, as Task 6: `python3 bundles/base/tools/build.py --out <scratchpad>/dist18` -> 344969 bytes, sha256 33638ca2ade50712, unzipped to `<scratchpad>/unz18`; `install.py --help` read; dry run `--target . --format claude --profile build` -> UPDATE the agent definitions planner, coder, reviewer, test-planner, test-coder and coordinator (not bug-coder), `PHASE_PLAN_TEMPLATE.md`, `REVIEW_PLAN_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE.md`, `docs/process/REVIEW_CYCLE.md`, `docs/process/HOWTO.md`, and the managed block of `AGENTS.md` (one line changed: the rules text); CREATE `.claude/commands/phase-status.md` and `.manifold/phase_status.py`; all else SKIP. Same with `--apply`, no `--force` -> "Installed manifold 0.2.0". `install.py --status` -> 25 files `ok`, 0 MODIFIED. Manifest hash check (a scratchpad script comparing the sha256 of each installed file with `.manifold/manifest.json`) -> 25 checked, 0 mismatches. `cmp` of the bundle sources with the installed copies: `hooks/guard.py`, `scripts/phase_status.py`, `commands/phase-status.md`, `HOWTO.md`, `process/REVIEW_CYCLE.md`, `process/BREACH_PROCEDURE.md` and the three changed templates -> all equal. The seven agent definitions have no single source file (they are rendered); a `cmp` of the rendered build output against `.claude/agents/*.md` was refused by the guard (rule `protected-file`, see CP4 Rule exceptions) and not retried another way; their equality with the build output is shown by the manifest hash check and `--status` (both `ok`). Gates: see the CP4 Gates line. `/phase-status 3` in a Claude Code client: not run (a command in this session's client was not invoked); the script was run twice instead, see the Verification result. No hand edit of any installed copy.

---

**Verification:** `/phase-status 3` (or the script) run twice prints the same list; the gates above are reported with counts.

Gates (2026-11-12): `python3 bundles/base/tools/build.py --check` -> `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` -> 2078 passed, 1 skipped; `cd server && ../.venv/bin/python -m pytest -q` -> 1060 passed, 2 warnings (Pydantic deprecation, not from this change), 136.59 s; `.venv/bin/python -m pytest tests/live -q` -> 24 passed; `.venv/bin/python tools/vendor_web.py --check` -> "vendored files match a fresh build"; `build.py --out <scratchpad>/cp4a` and `--out <scratchpad>/cp4b` -> 344969 bytes each, `cmp` equal. Script run twice: `.venv/bin/python bundles/base/scripts/phase_status.py 3` twice, output identical (compared byte for byte by the coder's report; counts: 0 unticked tasks, 0 blocked, 2 unticked Completion checklist lines (the "Level aimed at" line and the summary note, left for the owner and the closing step), review revision 5 with 5 open findings (F8, F9, F10, F12, F14, the owner's decisions are in the pull request)).

Rule exceptions (CP4): none broken. Web reads (WebFetch, read only, 2026-11-12, recorded in the Task 15 note): `https://code.claude.com/docs/en/slash-commands`, `https://code.visualstudio.com/docs/copilot/customization/prompt-files`, `https://docs.github.com/en/copilot/tutorials/customization-library/prompt-files`; in this continuation no web read and no `gh` call. One command was refused by the guard (rule `protected-file`): a `cmp` loop over the rendered agent definitions in `.claude/agents/`; nothing ran, I did not retry it by another route and recorded the equality by the manifest hash check and `--status` instead. No file written from a shell command, no commit, push or staging, no installed copy edited by hand, no existing test edited (`git diff -U0 bundles/base/tests/test_bundle.py` shows only added lines), `.github/` unchanged.

## Completion checklist

- [x] All tasks marked [x] by the coder
- [x] `python3 bundles/base/tools/build.py --check` passes clean
- [x] `.venv/bin/python -m pytest bundles/base/tests -q` and `cd server && ../.venv/bin/python -m pytest -q` pass clean (no regressions)
- [x] No [~] blocked items outstanding
- [ ] Level aimed at: mergeable (see "Definition of done" in `docs/process/REVIEW_CYCLE.md`, added by Task 8)
- [ ] Summary note added by the coder below this line

## Open questions

The intent's own open questions are answered in the accepted intent (agree with the recommendations, except the definition of done, presented above, and the release, v0.3.0). Still open, each with a default the plan applies unless the owner says otherwise:

1. **Which definition-of-done approach (A, B or C above)?** Default: A. Confirmed at plan approval.
2. **Does a task set `bundles/base/VERSION` to 0.3.0 and update the places that quote the version?** The intent puts choosing the version out of scope, the owner said the work is v0.3.0. Consequence: without a task, the release step does it. Default: no task here; the owner bumps at release.
3. **Does the `/phase-status` command also need a `copilot` and `skills` form, or `claude` only?** The constraint "both flavors" says both; the Copilot prompt-file format is unverified until Task 15. Default: `claude` and `copilot` get a command, `skills` an instruction line.
4. **May Task 2 edit one cell of the completed Phase 2 plan's traceability table?** It is a record, not a task note. Default: yes, that cell only.

## Review amendment (round 1)

**Source:** `docs/plans/REVIEW_PLAN_3.md`, revision 1 (reviewed commit `aabccb3`, CP1 only; one Important, two Nit)
**Amendment approved by:** Michael Hay on November 11, 2026

Owner decisions applied (chat, 2026-11-11: "Accept all recommendations"): F1 repaired (plan amended to cover the capability record); F2 accepted, failing-first evidence recorded if it can be produced; F3 folded into the repair as a reword. The completed CP1 tasks, their notes and acceptance lines are not changed: Task 1's acceptance grep covered only the two shipped files, which is why F1 was missed; Task 19 closes that gap.

### CP5 — Repairs from review round 1

### Task 19 — Correct the "nothing seen in a live client" sentence in the capability record

**Source:** `REVIEW_PLAN_3.md F1`
**Files:** `docs/agents/harness-capabilities.md` (line 87, last sentence only)
**Action:** MODIFY
**Change:** Replace "Nothing here was seen in a live client: the recorded runs of 2026-11-08 captured no guard log." with "One live guard refusal is recorded, for a Claude Code subagent (`test-coder`, 2026-11-09, `docs/agents/claude-desktop-failures.md` F9); no other row of this table was seen in a live client, and the runs of 2026-11-08 captured no guard log." Change no other line, and leave the table rows as they are. This file is not installed (not in `.manifold/manifest.json`), so no refresh is needed.
**Acceptance:** `grep -rInE "Nothing here was seen|not yet seen in a live|recorded in a live|None of this has been recorded" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=plans` prints nothing (run from the repository root); `grep -n "claude-desktop-failures.md" docs/agents/harness-capabilities.md` shows the new sentence on line 87; `git diff -U0 docs/agents/harness-capabilities.md` shows one changed line.
**Todo:** [x]
Note (2026-11-11): line 87 last sentence of `docs/agents/harness-capabilities.md` replaced as written. `grep -n "claude-desktop-failures.md" docs/agents/harness-capabilities.md` -> line 87; `git diff -U0` -> one hunk. The repo-wide acceptance grep prints two lines, both in `bundles/base/tests/test_bundle.py` (2249, 2250): the assertions of `test_deferred_text_fixes_f1_f4_f5` that the phrases are absent. No false statement remains in any document; the grep's exclusions did not anticipate the test file (plan gap, reported, nothing changed for it).

---

### Task 20 — Remove the pointer to deleted history from the lessons paragraph

**Source:** `REVIEW_PLAN_3.md F3`
**Files:** `bundles/base/process/REVIEW_CYCLE.md` (line 52), then the install refresh: `docs/process/REVIEW_CYCLE.md`, `.manifold/manifest.json`
**Action:** MODIFY
**Change:** In the paragraph under "What earlier cycles taught", replace "the review must be a file (the points were numbered by hand);" with "the review must be a file, not a chat message;". Change nothing else in the paragraph. Then refresh this repository's own install exactly as Task 6 did: `python3 bundles/base/tools/build.py --out <scratchpad>/dist`, unzip into a fresh scratchpad folder, read `install.py --help`, run `install.py --target . --format claude --profile build` as a dry run (expect UPDATE for `docs/process/REVIEW_CYCLE.md` only; everything else SKIP), then the same with `--apply` and no `--force`. Stage explicit paths only.
**Acceptance:** `grep -rn "numbered by hand" bundles docs/process .manifold` prints nothing; `cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md` prints nothing; the sha256 of `docs/process/REVIEW_CYCLE.md` (`shasum -a 256`) equals its entry in `.manifold/manifest.json`; `install.py --status` run from the unzipped bundle reports no MODIFIED file.
**Todo:** [x]
Note (2026-11-11): the phrase in `bundles/base/process/REVIEW_CYCLE.md` line 52 reworded as written. `build.py --out <scratchpad>/dist5` -> built, unzipped to `<scratchpad>/unz5`; `install.py --help` read; dry run `--target . --format claude --profile build` -> UPDATE `docs/process/REVIEW_CYCLE.md` only; same with `--apply`, no `--force` -> "Installed manifold 0.2.0". `grep -rn "numbered by hand" bundles docs/process .manifold` -> nothing; `cmp` of the two REVIEW_CYCLE.md files -> equal; sha256 of `docs/process/REVIEW_CYCLE.md` (82492993...c0d) equals its manifest entry; `install.py --status` from the unzipped bundle -> 0 lines with MODIFIED. Nothing staged.

---

### Task 21 — Record a failing-first run of Task 5's test, or say why not

**Source:** `REVIEW_PLAN_3.md F2`
**Files:** none changed in the repository; the result goes in this task's note
**Action:** none (run and record)
**Change:** Try to run `test_deferred_text_fixes_f1_f4_f5` against the old text: `git worktree add --detach <scratchpad>/old 3e2bbaf`, add the one test function (copied from `bundles/base/tests/test_bundle.py` as it is now) to that worktree's `bundles/base/tests/test_bundle.py` with the `Edit` tool, run `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` there, record the counts, then `git worktree remove --force <scratchpad>/old`. Use no shell redirect. If the test cannot be made to run that way (for example it resolves paths from the main checkout), do not work around a guard refusal; write in the note which step failed and why. Edit no test or file in this checkout.
**Acceptance:** this task's note holds either the command and its "1 failed" count on `3e2bbaf` text, or one sentence naming the step that could not be done and why; `git status --short` in this checkout shows no change caused by this task.
**Todo:** [x]
Note (2026-11-11): `git worktree add --detach <scratchpad>/old 3e2bbaf`; the test function (copy of the current one, without its docstring) added at the end of that worktree's `bundles/base/tests/test_bundle.py` with `Edit`; there, `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` -> 1 failed, 1955 deselected (AssertionError on the old text). Worktree removed with `git worktree remove --force`; no guard refusal; `git status --short` in this checkout shows only the changes of Tasks 19 and 20 and this plan.

---

**Verification:** in the repository root, `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported); `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` prints nothing; the grep in Task 19 prints nothing; `git diff --name-only` lists only `docs/agents/harness-capabilities.md`, `bundles/base/process/REVIEW_CYCLE.md`, `docs/process/REVIEW_CYCLE.md`, `.manifold/manifest.json` and this plan.

Rule exceptions (Tasks 19 to 21): none (the owner's decision on review finding 4: they were none).

**Findings not repaired:** none. F2 is accepted and addressed by Task 21 (evidence only, no code change); F1 and F3 are repaired by Tasks 19 and 20.

| Finding | End | Reason |
| ------- | --- | ------ |
| (none)  |     |        |

**Open questions:** None.

## Review amendment (round 2)

**Source:** `docs/plans/REVIEW_PLAN_3.md`, revision 3 (reviewed commit `30e88bd`, CP2, Tasks 7 to 10; findings F5 to F10: two Important, four Nit)
**Amendment approved by:** Michael Hay on November 12, 2026

Owner decisions applied (chat, 2026-11-11: "Accept all recommendations"): F5, F6 and F7 are repaired in one repair checkpoint; F8, F9 and F10 are deferred, each with its reason in the table below. The completed CP2 tasks (7 to 10), their notes and acceptance lines are not changed; Tasks 7 and 8 prescribed the wording that F5 and F7 find faulty, so the repair corrects it in a later task. Edits are to bundle sources only; the installed copy `docs/process/REVIEW_CYCLE.md` and `.manifold/manifest.json` are refreshed by Task 18, which runs after this checkpoint.

Existing tests that pin the wording this checkpoint changes (none may be edited without the owner's yes, in the owner's words, recorded in the task's note; see Open question 1):

- `test_review_cycle_ready_check_leaves_the_decisions_to_a_human`: the ready-check section must keep "A review of the final commit exists", "repaired, deferred or rejected", "CI of that exact commit", "`Review process` section of `AGENTS.md`", "does not move a pull request out of draft", "does not merge".
- `test_review_cycle_names_homes_levels_and_light_path`: the three headings; the light-path section keeps "solo" and "never code"; item 3 of the ready check contains "never a commit" or "no second confirmation"; the ready check keeps "run for an older commit is not the result".
- `test_review_cycle_has_the_sequence_the_handling_and_the_ready_check`: the table columns and the five step rows of "The sequence" (first column unchanged); in "How a review is handled" the seven bold labels, and "three runs", "until the human says enough", "the human may set another limit", "in place", "A finding is never deleted", "nothing open, or only Nits".
- `test_review_cycle_answers_the_five_test_handling_points` (the CI point keeps "exact commit"), and the table-of-steps tests at `bundles/base/tests/test_bundle.py` lines 2072 and 2113 (first column of "The sequence" and the step names in HOWTO).
- `test_deferred_text_fixes_f1_f4_f5` (no "Phase 2", "CP2a", "CP2b", " his " in the file).

The repairs below keep every phrase listed. If a repair cannot keep one, the coder stops and does not edit the test (Open question 1).

### CP6 — Repairs from review round 2

### Task 22 — Add a failing-first test for the three repairs

**Source:** `REVIEW_PLAN_3.md F5, F6, F7`
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY (add one function; edit no existing test)
**Change:** Add `test_review_cycle_round2_repairs` after `test_review_cycle_names_homes_levels_and_light_path`. It reads `bundles/base/process/REVIEW_CYCLE.md` and asserts: (F5) item 3 of "The ready check" contains neither "no second confirmation" nor "changes no code", and still contains "never a commit" and "run for an older commit is not the result"; (F6) the file contains the sentence Task 24 writes, "The reviewer's file records only `open` and `repaired`", and the string "as repaired, deferred or rejected with evidence" is absent from the file; (F7) the "Light path for text fixes" section contains "the human who ticks judges" and "ready check". Use the exact strings of Tasks 23 to 25.
**Acceptance:** failing first: before Tasks 23 to 25, `.venv/bin/python -m pytest bundles/base/tests -q -k round2_repairs` shows 1 failed; after them, 1 passed. Record both counts and the command in the note.
**Todo:** [x]
Note (2026-11-12): added `test_review_cycle_round2_repairs` after `test_review_cycle_names_homes_levels_and_light_path`; no existing test edited. Failing first, before Tasks 23 to 26 touched any source: `.venv/bin/python -m pytest bundles/base/tests -q -k round2_repairs` -> 1 failed, 2036 deselected (first failing assertion: "no second confirmation" still in item 3). After Tasks 23 to 25 (and 26): same command is covered by `-k "round2_repairs or review_cycle or ready_check or t34"` -> 23 passed, 2014 deselected; full suite 2036 passed, 1 skipped (one more than CP2's 2035).

---

### Task 23 — Drop the "no second confirmation" clause from ready-check item 3

**Source:** `REVIEW_PLAN_3.md F5`
**Files:** `bundles/base/process/REVIEW_CYCLE.md` (item 3 of "The ready check")
**Action:** MODIFY
**Change:** Replace item 3 with: "CI of that exact commit has been read by the `coordinator` and ticked by a human in the pull request (the tick is in the pull request, never a commit). Every commit gets its own read and tick, including a commit that changes only text: the light path saves review effort, not the CI check. A run for an older commit is not the result." Change no other item.
**Acceptance:** `grep -n "second confirmation\|changes no code" bundles/base/process/REVIEW_CYCLE.md` prints nothing; `grep -n "never a commit" bundles/base/process/REVIEW_CYCLE.md` finds item 3 and the table row; `.venv/bin/python -m pytest bundles/base/tests -q -k "ready_check or review_cycle_names"` passes with no test edited.
**Todo:** [x]
Note (2026-11-12): item 3 of "The ready check" replaced as written; no other item changed. `grep -n "second confirmation\|changes no code" bundles/base/process/REVIEW_CYCLE.md` -> nothing; `grep -n "never a commit"` -> line 47 (table row) and line 57 (item 3); `-k "ready_check or review_cycle_names"` passed (inside the 23 passed above), no test edited.

---

### Task 24 — Give the reviewer's file only `open` and `repaired`; move the decision to the pull request

**Source:** `REVIEW_PLAN_3.md F6`
**Files:** `bundles/base/process/REVIEW_CYCLE.md` (sequence table rows "Amendment" and "Re-review"; the paragraph after the table; "Where the output goes"; "What stops a pull request from being marked ready"; the row "What was decided about a finding" in "Where each fact is recorded")
**Action:** MODIFY
**Change:** Make these replacements, each limited to the words named, so that the file has one rule: the reviewer's file says what was found and whether it is repaired; the decision to defer or reject is a human's and lives in the pull request.

- "Re-review" row, Output: replace "each earlier finding shown as repaired, deferred or rejected with evidence" with "each earlier finding shown as repaired, with evidence, or still `open`".
- Paragraph after the table: replace "Every finding ends in one of three states: repaired, deferred (with a reason) or rejected (with a reason)." with "Every finding ends in one of three states: repaired, deferred (with a reason) or rejected (with a reason). The reviewer's file records only `open` and `repaired` (with the evidence); a human decides deferred and rejected, and the decision is recorded in the pull request (see \"Where each fact is recorded\")."
- "Where the output goes": replace "changes the state of each earlier finding with its evidence" with "moves each earlier finding from `open` to `repaired` with its evidence, or leaves it `open`".
- "What stops a pull request from being marked ready": replace "each of its findings is repaired, deferred or rejected, and a human has said so" with "each of its findings is repaired or has a decision (deferred or rejected) recorded in the pull request, and a human has said so".
- "Amendment" row, Output: replace "the findings not repaired with a reason" with "the findings not repaired, each with the planner's proposed end and a reason (the planner proposes; the decision is the human's, in the pull request)".
- Row "What was decided about a finding": replace its first cell text so it reads "the decision on each finding that is not repaired (deferred or rejected, with the reason), in a comment or checklist in the pull request that links the finding; the amendment's table of findings not repaired is the planner's proposal, not a second home; the amendment still carries the repair tasks". Keep the "Who writes it" cell.
  Keep "in place", "A finding is never deleted", "nothing open, or only Nits", "three runs" and the first column of the sequence table unchanged. Edit no other file (the review template, `HOWTO.md` and `planner.agent.md` also use the three-state wording; see Open question 2).
  **Acceptance:** `grep -n "as repaired, deferred or rejected with evidence\|changes the state of each earlier finding" bundles/base/process/REVIEW_CYCLE.md` prints nothing; `grep -c "file records only" bundles/base/process/REVIEW_CYCLE.md` prints 1; `.venv/bin/python -m pytest bundles/base/tests -q -k "review_cycle or t34"` passes with no existing test edited.
  **Todo:** [x]
  Note (2026-11-12): the six replacements applied as worded (re-review row, paragraph after the table, "Where the output goes", "What stops a pull request from being marked ready", amendment row, fact-table row). `grep -n "as repaired, deferred or rejected with evidence\|changes the state of each earlier finding"` -> nothing; `grep -c "file records only"` -> 1; `-k "round2_repairs or review_cycle or ready_check or t34"` -> 23 passed, no existing test edited. "in place", "A finding is never deleted", "nothing open, or only Nits", "three runs" untouched.

---

### Task 25 — State in the light path what is skipped, what is kept and who judges "text only"

**Source:** `REVIEW_PLAN_3.md F7`
**Files:** `bundles/base/process/REVIEW_CYCLE.md` (section "Light path for text fixes")
**Action:** MODIFY
**Change:** Keep the section's intro and its four conditions as they are. Add a closing paragraph: "What it skips: the planner amendment and the repair checkpoint. What it keeps: a review of the final commit by the `reviewer` (a revision of `docs/plans/REVIEW_PLAN_<N>.md`), the four lines of the ready check, with CI of every commit read and ticked, and the human's tick of the diff. Who judges \"text only\": the human who ticks judges whether the change is only text and changes no behavior; the author's word does not count, and when the human doubts it, the full amendment round applies." The section must still contain "solo" and "never code".
**Acceptance:** `grep -n "the human who ticks judges" bundles/base/process/REVIEW_CYCLE.md` finds one line in the light-path section; `.venv/bin/python -m pytest bundles/base/tests -q -k "round2_repairs or review_cycle_names"` passes.
**Todo:** [x]
Note (2026-11-12): closing paragraph added to "Light path for text fixes" (intro and four conditions unchanged; "solo" and "never code" still present). `grep -n "the human who ticks judges"` -> line 81, in the light-path section; the round-2 test and `review_cycle_names` pass (in the 23 passed above).

---

### Task 26 — Apply Task 24's rule to the review template, HOWTO and the planner agent

**Source:** `REVIEW_PLAN_3.md F6` (Open question 2, answered "Agree with recommendation")
**Files:** `bundles/base/templates/REVIEW_PLAN_TEMPLATE.md`, `bundles/base/HOWTO.md`, `bundles/base/agents/planner.agent.md`
**Action:** MODIFY
**Change:** Apply the rule of Task 24: the reviewer's file records only `open` and `repaired`; deferred and rejected are a human's decision, recorded in the pull request. Paths and lines were checked and are as the owner named them. The wording is named by content; the line numbers are only a guide.

- `bundles/base/templates/REVIEW_PLAN_TEMPLATE.md`, "Counts by severity" table (about line 27): replace the header and rule rows `| Severity | Open | Repaired | Deferred | Rejected |` and `|---|---|---|---|---|` with `| Severity | Open | Repaired |` and `|---|---|---|`, and the two rows `| Important | | | | |` and `| Nit | | | | |` with `| Important | | |` and `| Nit | | |`. Add one line under the table: "Deferred and rejected findings are a human's decision and are counted in the pull request, not here."
- `bundles/base/templates/REVIEW_PLAN_TEMPLATE.md`, the **State** line inside the findings comment (about line 48): replace "`open`, `repaired`, `deferred` or `rejected`; the reason, and the evidence for it (the repair task and the command that shows it). A finding ends `repaired`, `deferred` or `rejected`; it is never closed without evidence." with "`open` or `repaired`; for `repaired`, the evidence (the repair task and the command that shows it). A finding is never marked `repaired` without evidence. The reviewer never writes `deferred` or `rejected`: a human decides those and records the decision in the pull request." The words `` `deferred` `` and `` `rejected` `` stay in the template (in this sentence), because an existing test needs them. Leave the comment at the top of the file ("change the State of each earlier finding with its evidence") as it is: it still holds.
- `bundles/base/HOWTO.md`, step "9. Re-review", the sentence "each earlier finding is shown as repaired, deferred or rejected with evidence" (line 65): replace with "each earlier finding is shown as repaired, with evidence, or still `open`". Keep the rest of the paragraph.
- `bundles/base/agents/planner.agent.md`, "Amending a plan from a review", step 2, the bullet "a table of the deferred and rejected findings (Nits, and any Important finding not repaired), each with a reason: every finding ends repaired, deferred or rejected, and none is dropped silently;" (line 78): replace with "a table of the deferred and rejected findings (Nits, and any Important finding not repaired), each with the end you propose and a reason: you propose, a human decides and records the decision in the pull request, and none is dropped silently;". Keep "deferred and rejected findings" in the bullet; the test below needs it.

**Not changed:** `bundles/base/HOWTO.md` line 75 (step "Ready check", "each finding repaired, deferred or rejected") describes the ready check, where Task 24 kept all three ends, and `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` keeps its counts table with Deferred and Rejected, which is the pull request's record.

**Existing tests that pin this wording (the coder edits none of them; if one fails, stop and ask):**

- `test_review_plan_template_has_every_section_of_the_review_document` (`bundles/base/tests/test_bundle.py`, about line 1475) asserts the strings `**State:**`, `` `open` ``, `` `repaired` ``, `` `deferred` ``, `` `rejected` `` and `## Counts by severity` in the template. The new State sentence and the heading keep all six. It does not pin the counts table header, so removing the two columns breaks no test.
- the same function's planner checks (about lines 1660 to 1668, run for both flavors) assert "deferred and rejected", "open questions", "one task per Important finding", "completed tasks" and "original acceptance lines" in the planner output. The new bullet keeps all of them.
- `test_pull_request_template_has_every_section_in_the_order_of_the_intent` pins the table header `| Severity | Open | Repaired | Deferred | Rejected |` in the pull request template, not in the review template; do not touch that file.
- `test_t34_howto_names_every_role_and_every_step_of_the_review_cycle`, `test_t34_howto_has_its_sections_and_three_labels_for_every_step` and `test_deferred_text_fixes_f1_f4_f5` read HOWTO headings, the three bold labels per step and forbidden terms; the edit changes none of them. No test pins the step 9 sentence itself (search: `grep -n "with evidence" bundles/base/tests/*.py` prints nothing).

If an existing test fails because of this task, the coder stops and asks the owner; it does not edit, skip or weaken the test (see Open question 1).

**Planner agent: one source.** `bundles/base/agents/planner.agent.md` is the only canonical file. `bundles/base/tools/build.py` (`load_agents`, `render_agent`, `CLAUDE_AGENT_PATH`, `COPILOT_AGENT_PATH`) renders it to the Claude Code flavor (`.claude/agents/planner.md`), the Copilot flavor (`.github/agents/planner.agent.md`) and the skill form, so one edit reaches both flavors. Do not edit `.claude/agents/planner.md` (this repository's installed copy, line 83) by hand; Task 18 refreshes it and the manifest hash. Task 18 also adds a line to `bundles/base/HOWTO.md`: apply Task 18 on top of this edit and do not undo it.

**Acceptance:** `grep -n "repaired, deferred or rejected with evidence\|ends .repaired., .deferred. or .rejected" bundles/base/HOWTO.md bundles/base/templates/REVIEW_PLAN_TEMPLATE.md bundles/base/agents/planner.agent.md` prints nothing; `grep -c "| Deferred | Rejected |" bundles/base/templates/REVIEW_PLAN_TEMPLATE.md` prints 0; `grep -c "never writes .deferred. or .rejected." bundles/base/templates/REVIEW_PLAN_TEMPLATE.md` prints 1; `grep -c "you propose, a human decides" bundles/base/agents/planner.agent.md` prints 1; `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes with no existing test edited (`git diff -U0 bundles/base/tests/test_bundle.py` still shows added lines only).
**Note:** Task 22's test covers `REVIEW_CYCLE.md` only and is not changed. The grep lines above are the check for this task; if the owner wants a test line for these three files, the coder adds it as a new function after `test_review_cycle_round2_repairs` and asks first. Not planned here.
**Todo:** [x]
Note (2026-11-12): review template (counts table now Severity/Open/Repaired plus the one-line note; State sentence replaced), `HOWTO.md` step 9 sentence and the planner bullet replaced as worded; installed copies not touched. Acceptance: the first grep prints nothing; `grep -c "| Deferred | Rejected |"` -> 0; `grep -c "never writes .deferred. or .rejected."` -> 1; `grep -c "you propose, a human decides"` -> 1; `build.py --check` -> `lint ok`; full bundle suite 2036 passed, 1 skipped, no existing test failed or edited; `git diff -U0 bundles/base/tests/test_bundle.py` shows 0 removed lines.

---

**Verification:** `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported, expected one more than before this checkpoint); `git diff --stat` lists only `bundles/base/process/REVIEW_CYCLE.md`, `bundles/base/templates/REVIEW_PLAN_TEMPLATE.md`, `bundles/base/HOWTO.md`, `bundles/base/agents/planner.agent.md`, `bundles/base/tests/test_bundle.py` and this plan; the grep lines of Task 26 give the stated output; `git diff -U0 bundles/base/tests/test_bundle.py` shows added lines only (0 removed). Task 18 then refreshes the installed copy; its acceptance (`cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md`) covers these changes.

Gates (2026-11-12): `.venv/bin/python -m pytest bundles/base/tests -q` -> 2036 passed, 1 skipped; `python3 bundles/base/tools/build.py --check` -> `lint ok`; `build.py --out <scratchpad>/cp6a` and `--out <scratchpad>/cp6b` -> same size (334301 bytes) and sha256 (70a6475447702bd5), `cmp` equal; `git diff --name-only` lists only the five bundle files named in the Verification line and this plan; the Task 26 greps give the stated output; 0 removed lines in `test_bundle.py`. Task 18 (installed copy refresh) not run, as planned.

Rule exceptions (Tasks 22 to 26): none. No file written from a shell command, no commit, push or staging, no installed copy edited, no existing test edited.

**Findings not repaired:**

| Finding   | End      | Reason                                                                                                                                                                                                                                                                                                                   |
| --------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| F8 (Nit)  | deferred | The new process text is ahead of its installed copy, the coordinator definition and `HOWTO.md` until Tasks 11, 12 and 18; those tasks bring them in line. Check at the CP3 review that the coordinator text and `HOWTO.md` agree with `REVIEW_CYCLE.md` as repaired by Tasks 23 to 25.                                   |
| F9 (Nit)  | deferred | A record note with no effect on behavior: `docs/agents/claude-desktop-failures.md` (entry F13) was added in the CP2 commit though it is not in the plan's inventory. Record it as an accepted addition in the completion summary; the entry needs no change.                                                             |
| F10 (Nit) | deferred | A record note with no effect on behavior: the reviewer did not reproduce the Task 10 failing-first run (it rests on the coder's note) and one assertion was changed after the passing run. The test passes now and no existing test was changed. Not reproduced by the reviewer; optional first-hand check by the owner. |

**Open questions:**

1. If a repair needs an edit to an existing test (the ones listed above), the coder stops and asks. Nothing is decided here. None is expected: Task 23 keeps "never a commit" so that `test_review_cycle_names_homes_levels_and_light_path` still passes (its "or no second confirmation" alternative becomes unused but is not edited). Owner: confirm that leaving that alternative in the test is acceptable. Answer: Agree with task 23's approach.
2. Task 24 changes `REVIEW_CYCLE.md` only, as decided. Three other bundle sources still describe all three states as the reviewer's: `bundles/base/templates/REVIEW_PLAN_TEMPLATE.md` (counts table with Deferred and Rejected columns; the **State** line), `bundles/base/HOWTO.md` line 65 ("each earlier finding is shown as repaired, deferred or rejected with evidence") and `bundles/base/agents/planner.agent.md` line 78. Owner: add a task for them to this checkpoint, or leave them and accept the inconsistency until a later phase? Recommended: add a task, because an agent reading the template will still write `deferred` in the reviewer's file. Answer: Agree with recommendation.
3. The owner's instruction cited lines 24, 29 and 31 of `REVIEW_CYCLE.md`; in the current file those lines are "Where the output goes", a blank line and "How tests are handled". Task 24 therefore names the wording by content (the re-review row, the paragraph after the table, "Where the output goes", "What stops a pull request from being marked ready", the amendment row and the fact table row). Owner: confirm these are the places meant. Answer: They are the right places.
4. Task 25 states that the light path keeps a review of the final commit and the full ready check, and that the human who ticks judges "text only". The review asked for a statement; this is the recommended content. Owner: confirm at approval. Answer: Agree task 25's approach and approve

## Review amendment (round 3)

**Source:** `docs/plans/REVIEW_PLAN_3.md`, revision 4 (reviewed commit `db37ef6`, CP3, Tasks 11 to 14, with the round 2 repair `815baa3` re-checked; open findings F8 to F13: one Important (F11), five Nits)
**Amendment approved by:** Michael Hay on November 12, 2026

Owner decisions applied (chat, 2026-11-12: "Accept all recommendations"): F11 and F13 are repaired in one repair checkpoint; F12 is deferred (and F8, F9, F10 stay deferred as in round 2), each with its reason in the table below. The completed tasks, their notes and acceptance lines are not changed. Edits are to bundle sources only (and the unshipped `docs/process/BRANCH_RULES.md` for F13); the installed coordinator `.claude/agents/coordinator.md` and `.manifold/manifest.json` are refreshed by Task 18, which runs after this checkpoint; do not edit them by hand.

F11, the decision: the coordinator gets a standing permission to write the CI result for the exact commit into the pull request's remaining-steps list ("What remains for you" in the pull request template) without asking each time. Reason: this phase exists so the human only ticks; the write is a reversible checklist line; the tick stays the human's. It is the one exception. Every other pull request write (the description, a comment, a push, opening the pull request) still needs the owner's go-ahead.

Existing tests that pin the wording this checkpoint changes (the coder edits none of them; if one fails, it stops and asks the owner, and does not edit, skip or weaken it; see Open question 1):

- `test_t33_coordinator_carries_every_intent_duty_and_the_owner_decisions` (both flavors; `COORDINATOR_DUTIES` in `bundles/base/tests/test_bundle.py`): the whole coordinator text must keep "push", "only with the owner's go-ahead" and "the repository the owner names" (duty "no outward action without the owner"); "never says \"ready\" while a line is missing", "exact commit" and "a human confirms" (duty "ready check"); "gh run list --commit <full hash> --json", "gh pr view <number> --json headRefOid,isDraft", "treat red or missing CI as a finding" and "unverified" (duty "reads CI of the exact commit").
- `test_coordinator_reports_level_and_compares_branch_rules`: the "CI of the exact commit" section keeps "remaining-steps list" and "no commit".
- `test_t33_coordinator_leaves_no_step_of_the_pull_request_to_an_agent`: the text must not contain "mark the pull request ready", "gh pr ready", "gh pr merge" or "git push" (other than after "never ").
- `test_t33_coordinator_is_one_source_for_both_flavors_and_uses_no_role_references` (no `{{` in the source; both flavors have the same body; `build.lint` passes).
- `test_t34_howto_lists_the_human_gates_and_states_enforcement_per_client_as_far_as_verified` pins "go-ahead" in the HOWTO gates section; Task 30 edits `bundles/base/HOWTO.md` and keeps "go-ahead" (see Open question 2).

The repairs keep every phrase listed.

### CP7 — Repairs from review round 3

### Task 27 — Add a failing-first test for the F11 agreement

**Source:** `REVIEW_PLAN_3.md F11`
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY (add one function; edit no existing test)
**Change:** Add `test_coordinator_ci_write_is_the_one_standing_exception` after `test_coordinator_reports_level_and_compares_branch_rules`. It reads `_agent_text("coordinator")` and asserts, with the exact strings Task 28 writes: (a) the "CI of the exact commit" section contains "without asking each time" and "the one write"; (b) the "Ready check" section (from `## Ready check` to the next `\n## `) contains "only with the owner's go-ahead", "the one exception" and "remaining-steps list", and contains "Every other pull request write needs the go-ahead"; (c) the "Operating rules" bullet "No outward action without the owner" (the text from that bold label to the next line starting `- **`) contains "only with the owner's go-ahead" and "the one exception"; (d) the section "What you do not do" contains "the one exception". The test therefore fails while any of the three places lacks the exception and passes only when the CI section, the Ready check paragraph, the operating rule and the "What you do not do" bullet all name it.
**Acceptance:** failing first: before Task 28, `.venv/bin/python -m pytest bundles/base/tests -q -k ci_write_is_the_one_standing` shows 1 failed; after Task 28, 1 passed. Record both counts and the command in the note.
**Todo:** [x]
**Note:** Added `test_coordinator_ci_write_is_the_one_standing_exception` after `test_coordinator_reports_level_and_compares_branch_rules`; no existing test edited. Failing first: `.venv/bin/python -m pytest bundles/base/tests -q -k ci_write_is_the_one_standing` before any source change: `1 failed, 2039 deselected` (AssertionError at the first check, "without asking each time" missing from the CI section). After Tasks 28 to 30 the first run still failed with an IndexError: the test's own split string lacked the full stop inside the bold label (`**No outward action without the owner.**`); I corrected that string in the new test only, and the run then gave `1 passed, 2039 deselected`.

---

### Task 28 — Make the coordinator's four statements about pull request writes agree

**Source:** `REVIEW_PLAN_3.md F11` (owner decision: a standing permission for the one CI-result line)
**Files:** `bundles/base/agents/coordinator.agent.md` (the operating rule "No outward action without the owner"; the last bullet of "CI of the exact commit" that starts "Write the result for that exact commit"; the last sentence of the "Ready check" paragraph; the bullet in "What you do not do" that starts "Push, open or comment on a pull request")
**Action:** MODIFY
**Change:** Make these four replacements, each limited to the words named, and change nothing else (wording is named by content; line numbers are only a guide):

- Operating rule "No outward action without the owner": after "Show the text first." add: " The one exception is the CI result line that "CI of the exact commit" and "Ready check" name."
- "CI of the exact commit", the bullet "Write the result for that exact commit into the pull request's remaining-steps list ...": keep it as it is and add at its end: " This is the one write to the pull request you make without asking each time: the owner has given a standing permission, because the line is a reversible checklist entry and the tick stays a human's. Write that line only; change nothing else in the pull request."
- "Ready check" paragraph, the last sentence "Write the description or a comment to the pull request only with the owner's go-ahead.": replace with "Write the description or a comment to the pull request only with the owner's go-ahead; the one exception is the CI result line in the remaining-steps list, which you may write without asking each time (see "CI of the exact commit"). Every other pull request write needs the go-ahead."
- "What you do not do", the bullet "Push, open or comment on a pull request, or post an issue without the owner's go-ahead.": replace with "Push, open or comment on a pull request, or post an issue without the owner's go-ahead (the one exception is the CI result line, see "CI of the exact commit")."

Do not change "a human confirms it by a tick in the pull request (never a commit)" in the Ready check paragraph, the four lines of the ready check, or the `gh` commands. The checked sections "Operating rules", "CI of the exact commit", "Ready check" and "What you do not do" are the only places in the file that say when the coordinator may write to the pull request (checked by reading the file; `grep -n "go-ahead\|without asking" bundles/base/agents/coordinator.agent.md` lists them).
**Acceptance:** `grep -c "the one exception" bundles/base/agents/coordinator.agent.md` prints 3; `grep -c "without asking each time" bundles/base/agents/coordinator.agent.md` prints 2; `grep -c "Every other pull request write needs the go-ahead" bundles/base/agents/coordinator.agent.md` prints 1; `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q -k "coordinator or ci_write_is_the_one_standing"` passes with no existing test edited (`git diff -U0 bundles/base/tests/test_bundle.py` shows added lines only).
**Todo:** [x]
**Note:** Four replacements in `bundles/base/agents/coordinator.agent.md`. One deviation in wording: the plan's sentence for the operating rule starts "The one exception is ...", which has a capital T, so the grep for "the one exception" would print 2, not the 3 the acceptance line states. I wrote "Nothing is exempt except the one exception: the CI result line that ..." so that the count is 3. Results: greps print 3, 2 and 1; `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q -k "coordinator or ci_write_is_the_one_standing"` gives `202 passed, 1838 deselected`; `git diff -U0 bundles/base/tests/test_bundle.py` has 0 removed lines.

---

### Task 29 — Add the missing parameter to the rules table of `BRANCH_RULES.md`

**Source:** `REVIEW_PLAN_3.md F13`
**Files:** `docs/process/BRANCH_RULES.md` (the table under "Rules on `main`")
**Action:** MODIFY
**Change:** Re-read the ruleset by GET only: `gh api --method GET repos/{owner}/{repo}/rulesets/26275761` (never another method, no `-f`, `-F` or `--input`, which would turn the call into a write; the command form is the one already recorded in the "How this was read" section). Add one row to the table, after the row "Code owner review" and before "Deletion of `main`", in the style of the other rows: `| Extra approval for unattributed changes | required (`require_extra_approval_for_unattributed_changes: true`) |`, only if the re-read shows that value. The meaning of the parameter is not explained in the file; add after the table, next to the existing "role 5" sentence: "What `require_extra_approval_for_unattributed_changes` means: unverified: confirm with the GitHub REST page "Rules" (https://docs.github.com/en/rest/repos/rules) or the ruleset page." Update the date in "How this was read" only if the re-read is repeated on a new day: add "Row added after a repeat read on <date>." and leave the first date. If the re-read cannot be made (`gh` missing or not signed in), do not add the row from memory: stop and ask the owner. `docs/process/BRANCH_RULES.md` is shown to the owner for a read: the coder prints the diff of this file in its report and stops for the owner's reading before the checkpoint is called done. Edit no other file, change no ruleset, setting or workflow.
**Acceptance:** `grep -c "require_extra_approval_for_unattributed_changes" docs/process/BRANCH_RULES.md` prints 2 (the row and the unverified sentence); `git diff --stat docs/process/BRANCH_RULES.md` shows only this file with additions only; `git diff --stat .github` is empty; every `gh` call in the note is listed with its method (GET); the owner has read the diff (recorded in the note by the owner's words).
**Todo:** [x] (all but the owner's reading, which is open)
**Note:** One `gh` call: `gh api --method GET repos/{owner}/{repo}/rulesets/26275761` (method GET; no `-f`, `-F` or `--input`; already signed in, no sign-in). It showed `require_extra_approval_for_unattributed_changes: true`, so the row was added after "Code owner review" and the unverified sentence after the "role 5" sentence. The read was made on 2026-11-12, the same day as the first read, so no "Row added after a repeat read" line was added. `grep -c "require_extra_approval_for_unattributed_changes" docs/process/BRANCH_RULES.md` prints 2; `git diff --stat docs/process/BRANCH_RULES.md` shows 3 insertions, 0 deletions; `git diff --stat .github` is empty. Owner's reading of the diff: the owner read the three added `BRANCH_RULES.md` lines and accepted them on 2026-11-12 (chat: "Accept recommendations").

---

### Task 30 — Name the CI result line as the one exception in `HOWTO.md`

**Source:** Open question 2 (owner: yes, add Task 30), following Task 28
**Files:** `bundles/base/HOWTO.md` (the step "12. Merge", its "What the agents will not do" paragraph; the bullet in "The human gates" that starts "give a go-ahead for anything that leaves the machine")
**Action:** MODIFY
**Change:** Make these two replacements, each limited to the words named, and change nothing else (wording is named by content; line numbers are only a guide). Task 18 also edits `bundles/base/HOWTO.md` (it refreshes the installed copy); apply this task on the bundle source first, and Task 18 then copies the result, so the two do not conflict.

- Step "12. Merge", **What the agents will not do.**: replace "Merge, move a pull request out of draft, or push, open or comment on one without your go-ahead." with "Merge, move a pull request out of draft, or push, open or comment on one without your go-ahead. The one exception is the CI result line the `coordinator` writes into the remaining-steps list of the pull request without asking each time; the tick stays yours."
- "The human gates", the bullet "give a go-ahead for anything that leaves the machine: a push, a pull request or a comment on one, a posted issue;": replace with "give a go-ahead for anything that leaves the machine: a push, a pull request or a comment on one, a posted issue (the one exception is the CI result line the `coordinator` writes into the remaining-steps list of the pull request);".

Keep "go-ahead" in both places (pinned by `test_t34_howto_lists_the_human_gates_and_states_enforcement_per_client_as_far_as_verified`, which needs "go-ahead", "out of draft", "merge" and "CI" in the human gates section). Existing tests that pin the how-to wording, none of which the coder edits (if one fails, it stops and asks the owner, and does not edit, skip or weaken it; see Open question 1): that test; `test_t34_howto_names_every_role_and_every_step_of_the_review_cycle` (roles in backticks, step headings); `test_t34_howto_has_its_sections_and_three_labels_for_every_step` (the three bold labels in every step); `test_t34_howto_links_the_procedures_and_does_not_contradict_them` ("three runs", "never moves a pull request out of draft", the two approval phrases); `test_t34_howto_has_no_forbidden_term_and_no_bundle_version`; `test_t35_user_documents_link_nothing_outside_the_zip_and_name_no_bundle_version`; `test_deferred_text_fixes_f1_f4_f5` (the HOWTO part); the `test_t34_howto_*` install and zip tests (byte equality of the built copies with the source). Do not edit the step "11. The ready check" paragraph or any other line of the file.
**Acceptance:** `grep -c "he one exception is the CI result line" bundles/base/HOWTO.md` prints 2 (one capital "The", one lower-case "the"); `grep -c "remaining-steps list" bundles/base/HOWTO.md` prints 2; `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q -k "howto"` passes with no existing test edited (`git diff -U0 bundles/base/tests/test_bundle.py` shows added lines only).
**Todo:** [x]
**Note:** Two replacements in `bundles/base/HOWTO.md` as written; "go-ahead" kept in both. `grep -c "he one exception is the CI result line" bundles/base/HOWTO.md` prints 2; `grep -c "remaining-steps list" bundles/base/HOWTO.md` prints 2; `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q -k howto` gives `11 passed, 2029 deselected`; no removed line in `test_bundle.py`.

---

**Verification:** `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported, expected one more than before this checkpoint); `git diff --stat` lists only `bundles/base/agents/coordinator.agent.md`, `bundles/base/HOWTO.md`, `bundles/base/tests/test_bundle.py`, `docs/process/BRANCH_RULES.md` and this plan; the greps of Tasks 28, 29 and 30 give the stated output; `git diff -U0 bundles/base/tests/test_bundle.py` shows added lines only (0 removed). Task 18 then refreshes the installed coordinator; its acceptance covers these changes (`cmp` of the installed coordinator with the build output).

Rule exceptions (Tasks 27 to 30): none. The only `gh` call was `gh api --method GET repos/{owner}/{repo}/rulesets/26275761` (GET, read only). Deviation noted (not a rule exception): the operating-rule wording of Task 28 (see its note). Gates: `.venv/bin/python -m pytest bundles/base/tests -q` gives 2039 passed, 1 skipped (before the checkpoint: 2038 passed, 1 skipped); `python3 bundles/base/tools/build.py --check` prints `lint ok`; two builds with `--out` to the scratchpad are `cmp` equal.

**Findings not repaired:**

| Finding   | End      | Reason                                                                                                                                                                                                                                                                                              |
| --------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F12 (Nit) | deferred | The reviewer did not reproduce the failing-first run of Task 14; it rests on the coder's note, and the arithmetic fits the full-suite count (2037 + 2 = 2038 passed + 1 skipped). No existing test was edited (0 removed lines in `test_bundle.py`). Optional first-hand reproduction by the owner. |
| F8 (Nit)  | deferred | Unchanged from round 2: Task 18 refreshes the installed copies; the CP3 review found the same transitional state for the installed coordinator and the `AGENTS.md` managed block.                                                                                                                   |
| F9 (Nit)  | deferred | Unchanged from round 2: a record note with no effect on behavior. The same pattern (a breach-record entry not in the inventory) recurs in the CP3 commit; record both as accepted additions in the completion summary.                                                                              |
| F10 (Nit) | deferred | Unchanged from round 2: the failing-first run of Task 10 was not reproduced; the test passes and no existing test changed.                                                                                                                                                                          |

The deferrals are the planner's proposal following the owner's decision above; the owner's decision is recorded in the pull request, not here.

**Follow-ups (not tasks):** listing `docs/agents/claude-desktop-failures.md` (the breach record that coder commits add without an inventory row) in the plan template's standing inventory is for a later phase; it would stop F9 and its CP3 repeat from recurring.

**Open questions:**

1. If a repair needs an edit to an existing test (the ones listed above), the coder stops and asks. Nothing is decided here. None is expected: Task 28 keeps every phrase those tests pin and Task 27 adds one function only. Owner: confirm.
2. `bundles/base/HOWTO.md` says in two places that the agents do not push, open or comment on a pull request "without your go-ahead" (the paragraph "What the agents will not do" and the list of what you give a go-ahead for). With the standing permission, these describe the general rule and do not name the CI result line. This amendment does not edit them (the instruction named the coordinator only, and Task 18 also edits `HOWTO.md`). Owner: add one task for a clause "except the CI result line the coordinator writes into the remaining-steps list" in both places, or accept the shorter text? Recommended: add the task, so the human reads the same rule everywhere. Answer: Yes, add Task 30 (owner, 2026-11-12).
