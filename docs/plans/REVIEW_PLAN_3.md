# REVIEW_PLAN_3.md

**Phase:** `docs/plans/PHASE_3_PLAN.md`, checkpoint CP1 only (Tasks 1 to 6)
**Intent:** INT-26, `intent/INT-26-finishing-a-phase-clear-and-light.md`
**Commit reviewed:** `aabccb3e4949de4de5cdaeedcff03cfd9212451d` (Task 6; with `996bcbd0774b7fdf4f902d95b1b006417e5a7461`, Tasks 1 to 5; diff `3e2bbaf..aabccb3`), branch `claude/intent-phase3-streamline`. The checkout's HEAD is the merge `7a79d22d2c87e2b683e81516ce0893f3091bcac6` (context only; it brings in #32, not reviewed). The working tree also holds one uncommitted edit to `docs/plans/PHASE_3_PLAN.md`: the "Rule exceptions:" line in the CP1 notes (line 146). That line is not in the commit reviewed.
**Plan version:** **Approved by:** Michael Hay on November 11, 2026; no amendment. Plan file has the uncommitted edit named above.
**Policy used:** `REVIEW.md` (repository root, present) plus the built-in defaults and the documents/agent-instructions standard. The `Review process` approval rule of `AGENTS.md` (solo repository, no second approver) applies; this change touches nothing that section says needs a second approver.
**Revision:** 2, 2026-11-11 (time not recorded by the reviewer). Revision 2 re-reviews the repair checkpoint `eea54246c0c3bc957387e9215d881018f940dc7f` (parent `e68312f`; Tasks 19 to 21 of "Review amendment (round 1)", approved by Michael Hay on November 11, 2026). The sections below that describe revision 1 (header lines above, "Checks that found nothing", "Rule exceptions compared" for CP1) are kept as written; revision 2 additions are marked "Rev 2".

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-11 | `aabccb3e4949de4de5cdaeedcff03cfd9212451d` | First review, CP1 only |
| 2 | 2026-11-11 | `eea54246c0c3bc957387e9215d881018f940dc7f` | Re-review of the repair (Tasks 19 to 21): F1 and F3 repaired, F2 repaired as accepted (evidence recorded, not reproduced by the reviewer); one new Nit (F4) |

## Counts by severity

| Severity | Open | Repaired | Deferred | Rejected |
|---|---|---|---|---|
| Important | 0 | 1 (F1) | 0 | 0 |
| Nit | 1 (F4, new in rev 2) | 2 (F2, F3) | 0 | 0 |

## Findings

### Bugs
(none)

### Security
(none)

### Compliance

**F1 (Important) — The capability record still says nothing was seen in a live client, contradicting the F4 fix**
- **Location:** `docs/agents/harness-capabilities.md:87` (not in Tasks 1 to 6; the shipped `INSTALL.md:78,91` and `HOWTO.md:120` now say the opposite)
- **Evidence:** line 87 ends "Nothing here was seen in a live client: the recorded runs of 2026-11-08 captured no guard log." It says it holds "the same table" as `INSTALL.md`, and `INSTALL.md:89,91` names this file as the source of each row and as "the capability record behind" the new live-refusal sentence. `docs/agents/claude-desktop-failures.md:191` (F9) records one live guard refusal (`no-heredocs`, `test-coder`, 2026-11-09). A repo-wide grep for "not yet seen|no live|live client|captured no guard" outside `docs/plans` finds this line as the only remaining false statement. The plan's F4 task lists only `INSTALL.md`, `HOWTO.md` and the Phase 2 row, and its acceptance grep covers only the two shipped files, so the miss is a plan gap carried through, not a coder deviation.
- **Direction:** Decide whether to bring line 87 into line with the F4 wording (an owner or amendment decision; the file is outside the plan inventory), or record it as a known remaining statement. The plan's objective ("fixed instead of shipped as known issues") is not met for the source record until then.
- **State:** repaired (rev 2)
- **Rev 2 evidence:** `git diff e68312f eea5424 -- docs/agents/harness-capabilities.md` is one line (87), and its new last sentence is the one the plan's Task 19 gives, word for word; no table row changed. The file is not in `.manifold/manifest.json`, so no install refresh was owed. The F9 claim still matches `docs/agents/claude-desktop-failures.md` (test-coder, a subagent, 2026-11-09). The repo-wide grep of Task 19 (`grep -rInE "Nothing here was seen|not yet seen in a live|recorded in a live|None of this has been recorded" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=plans`), run by me, prints two lines: `bundles/base/tests/test_bundle.py:2249` and `:2250`, the absence assertions of the Task 5 test. The owner has accepted this; noted, not a finding. No false statement remains in any document.

### Tests

**F2 (Nit) — Failing-first run of Task 5 not reproduced by the reviewer**
- **Location:** `docs/plans/PHASE_3_PLAN.md` Task 5 note; `bundles/base/tests/test_bundle.py` `test_deferred_text_fixes_f1_f4_f5`
- **Evidence:** the test passes now (`1 passed, 2033 deselected`). The note's "1 failed" on the unchanged files could not be reproduced here: my attempt to stage the old tree used a shell redirect and the guard refused it (see Rule exceptions compared). The commit order also cannot show it, because the test and the text fixes are in the same commit `996bcbd`. The test's assertions are the ones the plan names, and the old text does contain every needle (`Phase 2`, `CP2a`, `not yet seen in a live run`, `recorded in a live`; the `curl -o` line is new in the diff), so a failure on the old files is plausible.
- **Direction:** None required; reproduce with a clean checkout of `3e2bbaf` plus the new test file if the owner wants first-hand evidence.
- **State:** repaired as accepted (rev 2): the owner accepted F2 on the condition that the evidence is recorded if it can be produced. Task 21's note records `git worktree add --detach ... 3e2bbaf`, the test added there with `Edit`, and "1 failed, 1955 deselected" on the old text, with no guard refusal and the worktree removed.
- **Rev 2 evidence:** I did not reproduce the run (I did not rebuild a `3e2bbaf` worktree); the count rests on the coder's note. It is consistent with round 1: 1955 is the Task 6 count of the whole bundle tests at that time, and 1 failed plus 1955 deselected equals the old tree's 1956 tests. `git worktree list` shows no leftover worktree under the scratchpad, and `git status --short` in this checkout was clean at the start of this review. `git diff --stat e68312f eea5424 -- bundles/base/tests` is empty: no test edited by the repair.

### Context files

**F3 (Nit) — The lessons paragraph keeps a pointer to history that no longer exists**
- **Location:** `bundles/base/process/REVIEW_CYCLE.md:52` (also the installed copy `docs/process/REVIEW_CYCLE.md`)
- **Evidence:** the paragraph now reads "the review must be a file (the points were numbered by hand)". With the table deleted, "the points" has no antecedent for a reader of a shipped document. Task 3's acceptance grep passes (nothing for `Phase 2|CP2| his |first cycles`); `grep -rIn "first cycles"` finds no link to the removed heading outside historical plan records.
- **Direction:** Consider dropping or rewording the parenthesis so it needs no history. Style only.
- **State:** repaired (rev 2)
- **Rev 2 evidence:** `bundles/base/process/REVIEW_CYCLE.md` and `docs/process/REVIEW_CYCLE.md` each change one line, the exact replacement the plan's Task 20 names ("the review must be a file, not a chat message;"), and the rest of the paragraph is unchanged. `grep -rn "numbered by hand" bundles docs/process .manifold` prints nothing; `cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md` is equal; `shasum -a 256 docs/process/REVIEW_CYCLE.md` is `824929931473835b0cf352b244ebd01d3018c6bba761a30d83757da527b73c0d`, equal to its entry at `.manifold/manifest.json:27`. The manifest diff is only that hash and `installed_at`, as an install refresh produces.

**F4 (Nit, new in rev 2) — The repair checkpoint has no "Rule exceptions" line in the plan**
- **Location:** `docs/plans/PHASE_3_PLAN.md` Tasks 19 to 21 notes (the only "Rule exceptions:" line in the file is line 159, for CP1)
- **Evidence:** the coder reported "none" for the repair, but `grep -n "Rule exceptions" docs/plans/PHASE_3_PLAN.md` finds no such line for Tasks 19 to 21. The working rule says every report from an agent that changed files or ran commands carries the line. Whether the report itself carried it is outside what I can see; the plan, which is the record, does not. Compared with the diff and guard log, "none" holds (see "Rule exceptions compared, rev 2").
- **Direction:** Record the line in a later task's note or the completion summary (a completed task's note is not edited). Style and traceability only.
- **State:** open

## Checks that found nothing

- **Plan inventory:** `git diff --name-only 3e2bbaf..aabccb3` lists 12 files, all in the Tasks 1 to 6 files or the inventory rows (`.manifold/manifest.json` and `docs/process/*` are the install refresh, `PHASE_3_PLAN.md` holds the notes).
- **Task 2:** `PHASE_2_PLAN.md` has one changed line (the last cell of the INT-20 S1 row), as planned.
- **Task 4:** one line changed in `bundles/base/hooks/guard.py`, inside the docstring; the same words in `docs/agents/harness-capabilities.md:75`, `bundles/base/hooks/guard.py:80`, `.manifold/hooks/guard.py:80`.
- **Task 6 and the merge:** `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` equal; sha256 of the installed `guard.py`, `docs/process/REVIEW_CYCLE.md` and `docs/process/HOWTO.md` equal the hashes in `.manifold/manifest.json`. `git diff aabccb3 7a79d22` shows the merge changed `.manifold/hooks/guard.py`, `bundles/base/hooks/guard.py`, the manifest and `harness-capabilities.md` only through #32 (a worktree rule, a new residual-gap bullet, new guard tests); it did not touch or undo any CP1 line (the F1 line is present in all three files), and it did not change `REVIEW_CYCLE.md` or `HOWTO.md`.
- **F9 claim:** the shipped wording ("a live refusal ... for a subagent") matches `claude-desktop-failures.md` F9 (test-coder, a subagent). Shipped CP1 text names no date, finding ID or person.
- **Test edits:** no existing test line was removed or changed (0 deleted lines in `test_bundle.py`); one test added.
- **Light-path pilot:** the plan asks the owner to read the Task 1 to 4 diff and tick it in the PR; nothing for the reviewer to decide.

## Rule exceptions compared

The writer's line (plan line 146, uncommitted) says "not established": no coder shell commands or transcript are available, `.manifold/guard-log.jsonl` has one entry that says nothing about CP1, and the diff touches only files named in Tasks 1 to 6 plus the manifest. Compared:
- **Guard log:** `.manifold/guard-log.jsonl` (gitignored) holds one line, a reviewer `write-allowlist` event at 2026-11-11T20:03:10Z for a path in another worktree. The commits are 07:41 -0800 (about 15:41Z), so the entry is later than CP1 and unrelated to it. Matches the writer's statement.
- **Diff and log:** `git log 3e2bbaf..aabccb3` shows two commits by `mihay42`; the 12 changed files are all within Tasks 1 to 6 or their install output. Matches.
- **Not matched or not checkable:** the guard log covers only this checkout and starts after the commits, so a CP1 breach (or the guard's refusal of one) could not be seen either way. The Task 6 note's "the guard did not block the install" cannot be verified. Status: not compared beyond the above; "not established" is the honest value and I agree with it.

## Rule exceptions compared, rev 2

The coder's line for the repair was "none". Compared:
- **Diff:** `git show --stat eea5424` lists five files: `.manifold/manifest.json`, `bundles/base/process/REVIEW_CYCLE.md`, `docs/agents/harness-capabilities.md`, `docs/plans/PHASE_3_PLAN.md`, `docs/process/REVIEW_CYCLE.md`. All are named in Tasks 19 to 21 or are the install output. No code, test or other file changed. Matches "none".
- **Commit log:** one commit by `mihay42`, 15:40 -0800 (about 23:40Z). Message names the three repairs.
- **Guard log:** `.manifold/guard-log.jsonl` (gitignored, this checkout) holds a reviewer `write-allowlist` event (20:03:10Z, another worktree) and my own `no-heredocs` refusal of round 1 (20:18:44Z); both are earlier than the repair commit and neither is the coder's. No coder entry. During this round my `python3 -c` unzip of the rebuilt bundle was refused by the guard (`no-heredocs`, python code that writes files); I did not retry it another way (see Gates run). This will add one reviewer entry to the log.
- **Status:** matches; the log cannot show a coder breach that the guard did not see, and the coder's shell history is not available.

## Gates run

| Command | Counts | Result |
|---|---|---|
| `python3 bundles/base/tools/build.py --check` | n/a | `lint ok` |
| `.venv/bin/python -m pytest bundles/base/tests -q` (at merge HEAD `7a79d22`, includes #32's tests) | 2033 passed, 1 skipped | pass (the Task 6 note's 1955 passed is for `aabccb3`; not re-run at that commit) |
| `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` | 1 passed, 2033 deselected | pass |
| `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` | n/a | equal |
| manifest hashes vs files (`shasum -a 256`, 3 files) | 3 of 3 | equal |
| `install.py --status` | not run | needs the unzipped bundle; I did not rebuild |
| Rev 2: `python3 bundles/base/tools/build.py --check` at `eea5424` | n/a | `lint ok` |
| Rev 2: `.venv/bin/python -m pytest bundles/base/tests -q` at `eea5424` | 2033 passed, 1 skipped | pass |
| Rev 2: `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` | n/a | equal |
| Rev 2: `cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md`; sha256 of `docs/process/REVIEW_CYCLE.md` vs `.manifold/manifest.json:27` | 2 of 2 | equal; hash `82492993...c0d` matches |
| Rev 2: `build.py --out <scratchpad>/dist2` | n/a | built `manifold-base-0.2.0.zip` (lint ok) |
| Rev 2: `install.py --status` from the unzipped bundle | not run | the unzip step (a `python3 -c` zipfile call) was refused by the guard; I did not get the result another way. The coder's note (Task 20: 0 lines MODIFIED) is unverified by me; the hash and `cmp` checks above cover the one file that changed |
| Rev 2: Task 19 and 20 acceptance greps (as written in the plan) | n/a | Task 20 grep prints nothing; Task 19 grep prints the two accepted test lines |
| server tests, `tests/live`, `vendor_web.py --check` | not run | outside CP1 verification |

## CI on the pushed commit

Not checked: I did not read CI for `aabccb3` (no `gh` call made; the plan says a human confirms CI).

## Tests run and changed

One test added (`test_deferred_text_fixes_f1_f4_f5`), none changed, none deleted. This is text work, not a bug fix, so the failing-first rule applies only as the plan's own acceptance line; see F2. Real-use evidence for the changed text (item d of the standard): no evidence yet, by nature of these edits.

## Rev 2 summary of the repair

- Plan inventory and deviations: no unplanned file in `eea5424`; the Task 19 grep deviation was reported in the coder's note and accepted by the owner.
- The repair added no new text that contradicts another document: the new sentence in the capability record agrees with `INSTALL.md` and `HOWTO.md` as changed in CP1; the REVIEW_CYCLE reword is neutral. Completed CP1 task notes were not edited, as the amendment says.
- Real-use evidence (item d): no evidence yet.

## Could not check

- The failing-first run of Task 5 on the old files (F2).
- The coder's own shell history and the guard's behavior during Task 6.
- CI for the commit reviewed; `install.py --status` and the install itself (not rebuilt).
- Whether the owner has read and ticked the Task 1 to 4 diff in the PR.
- Rev 2: the failing-first run of Task 21 (coder's note only); `install.py --status` (guard refusal of my unzip step); CI for `eea5424`; the coder's shell history for the repair.

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above.
