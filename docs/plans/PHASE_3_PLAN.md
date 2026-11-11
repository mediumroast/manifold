# PHASE_3_PLAN.md

**Approved by:**
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

| Path | Action | Reason |
|------|--------|--------|
| `bundles/base/INSTALL.md` | MODIFY | F4 (lines 78, 91) |
| `bundles/base/HOWTO.md` | MODIFY | F4 (line 120) |
| `docs/plans/PHASE_2_PLAN.md` | MODIFY | F4: last cell of the "INT-20 S1" traceability row (line 1146) only |
| `bundles/base/process/REVIEW_CYCLE.md` | MODIFY | F5; homes of facts, definition of done, light path, ready check |
| `bundles/base/hooks/guard.py`, `docs/agents/harness-capabilities.md` | MODIFY | F1 (docstring and its mirror, one line each) |
| `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `bundles/base/templates/PHASE_PLAN_TEMPLATE.md` | MODIFY | remaining-steps checklist; link to the definition of done |
| `bundles/base/agents/coordinator.agent.md`, `bundles/base/rules/core/ask-on-ambiguity.md` | MODIFY | ready check, levels, batched decisions, self-contained asks |
| `docs/process/BRANCH_RULES.md` | CREATE | branch and merge rules, stacked PRs, CI for docs-only changes (not shipped) |
| `bundles/base/scripts/phase_status.py` | CREATE | read-only phase status |
| `bundles/base/commands/phase-status.md` (claude) and the copilot equivalent | CREATE | the slash command |
| `bundles/base/tools/build.py`, `bundles/base/install.py` | MODIFY | payload, lint and install of the script and command |
| `bundles/base/tests/test_bundle.py`, `bundles/base/tests/test_phase_status.py` | MODIFY / CREATE | tests next to each change |
| `.claude/agents/*`, `.manifold/*`, `docs/process/*`, `docs/templates/*` | MODIFY | refresh of this repository's own install (generated, from the build) |

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
**Todo:** [ ]

---

### Task 2 — Correct the INT-20 S1 traceability row (F4)
**Files:** `docs/plans/PHASE_2_PLAN.md` (line 1146, last cell only)
**Action:** MODIFY
**Change:** Replace "no live-client evidence yet" with "one live refusal in a Claude Code subagent, 2026-11-09 (`docs/agents/claude-desktop-failures.md` F9); none yet for Copilot, `--agent`, plugins". No other line of the file changes.
**Acceptance:** `git diff -U0 docs/plans/PHASE_2_PLAN.md` shows one changed line.
**Todo:** [ ]

---

### Task 3 — Remove repository history and the pronoun from the shipped review cycle (F5)
**Files:** `bundles/base/process/REVIEW_CYCLE.md` (lines 52 to 62)
**Action:** MODIFY
**Change:** Delete the section "How the first cycles ran" and its table (the record already exists in `docs/plans/PHASE_2_PLAN.md`, CP2a and CP2b). Keep the lessons paragraph under the new heading "What earlier cycles taught", with no mention of Manifold, Phase 2, CP2a, CP2b or any person's pronoun ("the owner", not "his"). Check that nothing links to the deleted heading: `grep -rn "first cycles" bundles docs README.md`.
**Acceptance:** `grep -n "Phase 2\|CP2\| his \|first cycles ran" bundles/base/process/REVIEW_CYCLE.md` prints nothing.
**Todo:** [ ]

---

### Task 4 — Name the allowed write-capable tools in the guard's stated limits (F1)
**Files:** `bundles/base/hooks/guard.py` (docstring line 77), `docs/agents/harness-capabilities.md` (line 75)
**Action:** MODIFY
**Change:** Replace the line "other languages, editors and tools than the ones named in the shell rule;" with "other languages, editors and tools than the ones named in the shell rule (for example `dd of=`, `curl -o`, `wget -O`, `tar x`, `unzip`, `install`, `python3 -m json.tool in out` are allowed although they write files);" in both files, in the same words. Change no line outside the docstring.
**Acceptance:** `git diff -U0 bundles/base/hooks/guard.py` shows one changed line, inside the docstring (it ends before `from __future__`); the existing parity test between the docstring and `harness-capabilities.md` (if any) passes in Task 6.
**Todo:** [ ]

---

### Task 5 — Add a test that pins the three fixes
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_deferred_text_fixes_f1_f4_f5`: the shipped `REVIEW_CYCLE.md` contains none of `Phase 2`, `CP2a`, `CP2b`, ` his `; `INSTALL.md` and `HOWTO.md` do not contain "not yet seen in a live run"; the `guard.py` docstring names `curl -o`. Follow the style of `test_t35_user_documents_link_nothing_outside_the_zip_and_name_no_bundle_version` (line 2230).
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` shows 1 passed. Failing-first: the note records the failing run of this test on the unchanged files, made by writing the test before applying Tasks 1 to 4 locally (the order in the plan is the order of the commits, not of the first run).
**Todo:** [ ]

---

### Task 6 — Refresh this repository's own install from the build
**Files:** `.manifold/hooks/guard.py`, `.manifold/manifest.json`, `docs/process/REVIEW_CYCLE.md`, `docs/process/HOWTO.md`
**Action:** MODIFY
**Change:** Build into the scratchpad (`python3 bundles/base/tools/build.py --out <scratchpad>/dist`) and install over this repository with the command and flags recorded in the Phase 2 T38 note (`docs/plans/PHASE_2_PLAN.md`); read `install.py --help` first, do not guess flags. `INSTALL.md` is not installed (not in the manifest). Stage explicit paths only.
**Acceptance:** `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes with no failures; `.manifold/hooks/guard.py` equals `bundles/base/hooks/guard.py` (`cmp`); `install.py --status` reports no modified file.
**Todo:** [ ]

---

**Verification:** `.venv/bin/python -m pytest bundles/base/tests -q` and `python3 bundles/base/tools/build.py --check` pass with counts reported; `git diff origin/main --stat` lists only the files in Tasks 1 to 6. The owner reads the diff of Tasks 1 to 4 in the PR and ticks it (the pilot of the light path; see Concerns 1).

### CP2 — One home per fact, definition of done, light path (documents)

### Task 7 — Add the table of homes of facts to the review cycle
**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** MODIFY
**Change:** Add a section "Where each fact is recorded" with one row per kind of fact and its single home; every other document links to it and never copies it: what was found (`docs/plans/REVIEW_PLAN_<N>.md`, only the `reviewer` edits it); what was decided about a finding (a comment or checklist in the pull request, linking the finding; a plan's amendment still carries the repair tasks); the CI confirmation (a tick in the pull request, never a commit); approval of a plan (its **Approved by** line, written by a human; unchanged); approval of the pull request (the checkbox in the pull request). In the section "The ready check" change item 2 to "each finding has a decision recorded in the pull request (the reviewer's file keeps it `open`)" and item 3 to "CI of that exact commit has been read by the `coordinator` and ticked by a human in the pull request; a commit that changes no code needs no second confirmation, a commit that changes code does". Do not remove "a run for an older commit is not the result".
**Acceptance:** `grep -n "Where each fact is recorded" bundles/base/process/REVIEW_CYCLE.md` finds the heading; the file's table has five rows; `grep -c "never a commit" bundles/base/process/REVIEW_CYCLE.md` prints 1 or more.
**Todo:** [ ]

---

### Task 8 — Add the definition of done and the light path
**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** MODIFY
**Change:** (Written for option A; follow the owner's choice under "Definition of done: approach".) Add "Definition of done" with three levels and their conditions: **mergeable** (the four ready-check lines met and a human ticked the pull request); **releasable** (mergeable, merged, the gates of `AGENTS.md` "Project commands" green on the merge commit, and the owner chose a version); **done** (releasable, the plan's completion summary written, a human wrote the closure; `human-confirms-closure`). Add "Light path for text fixes": only in a repository whose `Review process` says solo; only text in documents and agent instructions that changes no behavior (a comment or docstring qualifies only when the diff shows no other changed line); never code, rules, agent permissions, hooks or tests; the diff is shown in the pull request and a human ticks it; a team repository uses the full amendment round. State that the coordinator's closing report names the level reached and what the next level lacks.
**Acceptance:** `grep -n "mergeable\|releasable\|Light path" bundles/base/process/REVIEW_CYCLE.md` finds each; reading the section shows each level with a list of conditions and the sentence "never code, rules, agent permissions, hooks or tests".
**Todo:** [ ]

---

### Task 9 — Add the remaining-steps list to the pull request template
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `bundles/base/templates/PHASE_PLAN_TEMPLATE.md`
**Action:** MODIFY
**Change:** In the PR template add a section "What remains for you" of checkboxes: one line per changed file, saying what to check and what the tick means; one line "CI of commit <full hash> is green (read by the coordinator)"; one line "Findings: decisions below"; and a "Decisions for you" table whose columns are: what, why, consequence, default (no bare IDs; the reply "accept all" settles every default). Replace the template comment text so the Ready check lines link to "Where each fact is recorded" instead of restating it. In the plan template's Completion checklist add one line linking to "Definition of done" in `docs/process/REVIEW_CYCLE.md` and naming the level the plan aims at.
**Acceptance:** `grep -n "What remains for you\|Decisions for you" bundles/base/templates/PULL_REQUEST_TEMPLATE.md` finds both; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 10 — Add tests for Tasks 7 to 9
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_review_cycle_names_homes_levels_and_light_path` (the three headings exist; the light-path section contains "solo" and "never code"; item 3 of the ready check contains "never a commit" or the equivalent sentence) and `test_pr_template_has_remaining_steps_and_decisions_table`. Failing first: run both before Tasks 7 to 9 are applied to the source, record the counts.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "review_cycle_names or pr_template_has"` shows 2 passed.
**Todo:** [ ]

---

**Verification:** `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported); `python3 bundles/base/tools/build.py --check` prints `lint ok`; the built `claude` and `copilot` outputs both contain the new PR template text (`build.py --out` twice, `cmp` equal; deterministic).

### CP3 — Coordinator, plain asks, branch rules

### Task 11 — Read the ruleset and write `docs/process/BRANCH_RULES.md`
**Files:** `docs/process/BRANCH_RULES.md` (CREATE)
**Action:** CREATE
**Change:** With the owner's go-ahead, read the ruleset on `main` with `gh` (read only). Verify the command first: `gh api --help` and the GitHub rulesets API page; mark anything not verified "unverified: confirm with <source>". Record only what was read: required checks (by job name), squash only, linear history, review count, bypass actors. Add the stacked-PR steps under squash-only (the rebase of the dependent branch onto `main` after the base PR is squashed; verify the exact `git rebase` form with `git rebase --help`), and the route for editing agent definitions from another worktree (delegate to a session in that worktree; the guard's protection of definitions is deliberate). Add a section "CI for docs-only changes" holding the investigated answer (path filters, how a required check behaves when its workflow is skipped), with the source for each statement; recommend, do not change `.github/workflows/`.
**Acceptance:** each rule in the file shows the command or page it came from; `git diff --stat -- .github` is empty.
**Todo:** [ ]

---

### Task 12 — Add the level report, the PR-tick CI flow and the branch-rules comparison to the coordinator
**Files:** `bundles/base/agents/coordinator.agent.md`
**Action:** MODIFY
**Change:** In "CI of the exact commit" and "Ready check": the coordinator writes the CI result for the exact commit into the pull request's remaining-steps list for the human to tick, and records no commit for it; the closing report names the level reached (mergeable, releasable, done) and what the next level lacks, and never declares done; decisions are presented as one batch (what, why, consequence, default; "accept all" or named exceptions) with no bare IDs. Add a step "Branch rules": if the repository has a branch-rules document, compare its required check names with the job names in `.github/workflows/` and report a mismatch; never change the ruleset.
**Acceptance:** `grep -n "Branch rules\|mergeable\|accept all" bundles/base/agents/coordinator.agent.md` finds each; both builds (`--out`) render the text for `claude` and `copilot`.
**Todo:** [ ]

---

### Task 13 — Require self-contained asks in every agent
**Files:** `bundles/base/rules/core/ask-on-ambiguity.md`
**Action:** MODIFY
**Change:** Under "Instead" add: every ask states what is asked, why, the consequence and the default, in plain words, and never names an item only by an internal ID (task, checkpoint, finding or open-question number) without saying what it is. Add `coordinator` to `applies_to`.
**Acceptance:** `python3 bundles/base/tools/build.py --check` prints `lint ok`; the rendered `coordinator` agent contains the rule (`grep -n "internal ID"` on the built file).
**Todo:** [ ]

---

### Task 14 — Add tests for Tasks 12 and 13
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_coordinator_reports_level_and_compares_branch_rules` and `test_ask_rule_requires_self_contained_asks_for_coordinator`. Failing first, counts recorded. If an existing test pins the managed rules block or a rule's `applies_to`, stop, name the test and assertion, and ask the owner before editing it.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "coordinator_reports_level or self_contained_asks"` shows 2 passed.
**Todo:** [ ]

---

**Verification:** full bundle tests pass with counts; `docs/process/BRANCH_RULES.md` read by the owner (the only first-hand statement of the ruleset); the owner confirms the docs-only CI finding before any workflow change is planned.

### CP4 — `/phase-status`

### Task 15 — Verify the command formats of both flavors
**Files:** none changed; note in this task
**Action:** none (read)
**Change:** Read the Claude Code documentation for a project slash command file (location, frontmatter, how a command runs a shell command) and the GitHub Copilot equivalent (prompt files). Record each fact with its source, or "unverified: confirm with <source>". Settle whether `claude` and `copilot` get a command and `skills` gets an instruction only.
**Acceptance:** the note lists, per flavor, the file path and the source read.
**Todo:** [ ]

---

### Task 16 — Create the read-only phase status script with tests
**Files:** `bundles/base/scripts/phase_status.py` (CREATE), `bundles/base/tests/test_phase_status.py` (CREATE)
**Action:** CREATE
**Change:** Standard library only, Python 3.10. `main(argv)` takes the phase number and optional `--root`; it reads `docs/plans/PHASE_<N>_PLAN.md`, `PHASE_<N>_TEST_PLAN.md` and `REVIEW_PLAN_<N>.md` and prints, sorted and identical on repeated runs: unticked (`[ ]`) and blocked (`[~]`) task lines with file and line number; blank **Approved by** and **Amendment approved by**; unticked Completion checklist lines; the open count of the latest review revision; the highest level of the definition of done the files support, or "cannot tell from files" for the CI tick, which lives in the PR. It opens files only for reading. Tests: fixture plans in `tmp_path`; same output twice; file contents and mtimes unchanged after a run; an AST check that no call opens a file for writing; a filled approval is never reported blank; exit 2 and a plain message for a missing plan.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` passes (counts reported); `.venv/bin/python bundles/base/scripts/phase_status.py 2` runs against this repository's Phase 2 files and prints the open items.
**Todo:** [ ]

---

### Task 17 — Ship the script and the command in the build and the install
**Files:** `bundles/base/tools/build.py` (`build_payload`, `lint`), `bundles/base/install.py`, `bundles/base/commands/phase-status.md` (CREATE) and the copilot file named by Task 15 (CREATE), `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add the script to the payload as `.manifold/phase_status.py` (every profile, like `.manifold/hooks/guard.py`), lint it as standard library only (reuse `is_stdlib` and `lint_hook`'s check), add the command file per flavor so it runs `python3 .manifold/phase_status.py $ARGUMENTS` (exact syntax from Task 15), list both in the manifest, and let `--uninstall` remove them. Tests: installed and uninstalled in each profile and flavor, two builds byte-equal, the script is in the manifest.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q` passes; `python3 bundles/base/tools/build.py --check` prints `lint ok`; two `--out` builds compare equal with `cmp`.
**Todo:** [ ]

---

### Task 18 — Refresh the install and run every gate
**Files:** this repository's own install (as Task 6)
**Action:** MODIFY
**Change:** Rebuild and install as in Task 6; add one line to `bundles/base/HOWTO.md` naming `/phase-status <N>`.
**Acceptance:** `python3 bundles/base/tools/build.py --check` → `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q`; `cd server && ../.venv/bin/python -m pytest -q`; `.venv/bin/python -m pytest tests/live -q`; `.venv/bin/python tools/vendor_web.py --check`; all with real counts. In a client, `/phase-status 3` prints this plan's open items (observed, or "not run" with the reason).
**Todo:** [ ]

---

**Verification:** `/phase-status 3` (or the script) run twice prints the same list; the gates above are reported with counts.

## Completion checklist
- [ ] All tasks marked [x] by the coder
- [ ] `python3 bundles/base/tools/build.py --check` passes clean
- [ ] `.venv/bin/python -m pytest bundles/base/tests -q` and `cd server && ../.venv/bin/python -m pytest -q` pass clean (no regressions)
- [ ] No [~] blocked items outstanding
- [ ] Level aimed at: mergeable (see "Definition of done" in `docs/process/REVIEW_CYCLE.md`, added by Task 8)
- [ ] Summary note added by the coder below this line

## Open questions
The intent's own open questions are answered in the accepted intent (agree with the recommendations, except the definition of done, presented above, and the release, v0.3.0). Still open, each with a default the plan applies unless the owner says otherwise:

1. **Which definition-of-done approach (A, B or C above)?** Default: A. Confirmed at plan approval.
2. **Does a task set `bundles/base/VERSION` to 0.3.0 and update the places that quote the version?** The intent puts choosing the version out of scope, the owner said the work is v0.3.0. Consequence: without a task, the release step does it. Default: no task here; the owner bumps at release.
3. **Does the `/phase-status` command also need a `copilot` and `skills` form, or `claude` only?** The constraint "both flavors" says both; the Copilot prompt-file format is unverified until Task 15. Default: `claude` and `copilot` get a command, `skills` an instruction line.
4. **May Task 2 edit one cell of the completed Phase 2 plan's traceability table?** It is a record, not a task note. Default: yes, that cell only.
