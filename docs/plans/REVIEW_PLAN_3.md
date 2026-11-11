# REVIEW_PLAN_3.md

**Phase:** `docs/plans/PHASE_3_PLAN.md`, checkpoint CP1 only (Tasks 1 to 6)
**Intent:** INT-26, `intent/INT-26-finishing-a-phase-clear-and-light.md`
**Commit reviewed:** `aabccb3e4949de4de5cdaeedcff03cfd9212451d` (Task 6; with `996bcbd0774b7fdf4f902d95b1b006417e5a7461`, Tasks 1 to 5; diff `3e2bbaf..aabccb3`), branch `claude/intent-phase3-streamline`. The checkout's HEAD is the merge `7a79d22d2c87e2b683e81516ce0893f3091bcac6` (context only; it brings in #32, not reviewed). The working tree also holds one uncommitted edit to `docs/plans/PHASE_3_PLAN.md`: the "Rule exceptions:" line in the CP1 notes (line 146). That line is not in the commit reviewed.
**Plan version:** **Approved by:** Michael Hay on November 11, 2026; no amendment. Plan file has the uncommitted edit named above.
**Policy used:** `REVIEW.md` (repository root, present) plus the built-in defaults and the documents/agent-instructions standard. The `Review process` approval rule of `AGENTS.md` (solo repository, no second approver) applies; this change touches nothing that section says needs a second approver.
**Revision:** 1, 2026-11-11 (time not recorded by the reviewer)

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-11 | `aabccb3e4949de4de5cdaeedcff03cfd9212451d` | First review, CP1 only |

## Counts by severity

| Severity | Open | Repaired | Deferred | Rejected |
|---|---|---|---|---|
| Important | 1 | 0 | 0 | 0 |
| Nit | 2 | 0 | 0 | 0 |

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
- **State:** open

### Tests

**F2 (Nit) — Failing-first run of Task 5 not reproduced by the reviewer**
- **Location:** `docs/plans/PHASE_3_PLAN.md` Task 5 note; `bundles/base/tests/test_bundle.py` `test_deferred_text_fixes_f1_f4_f5`
- **Evidence:** the test passes now (`1 passed, 2033 deselected`). The note's "1 failed" on the unchanged files could not be reproduced here: my attempt to stage the old tree used a shell redirect and the guard refused it (see Rule exceptions compared). The commit order also cannot show it, because the test and the text fixes are in the same commit `996bcbd`. The test's assertions are the ones the plan names, and the old text does contain every needle (`Phase 2`, `CP2a`, `not yet seen in a live run`, `recorded in a live`; the `curl -o` line is new in the diff), so a failure on the old files is plausible.
- **Direction:** None required; reproduce with a clean checkout of `3e2bbaf` plus the new test file if the owner wants first-hand evidence.
- **State:** open

### Context files

**F3 (Nit) — The lessons paragraph keeps a pointer to history that no longer exists**
- **Location:** `bundles/base/process/REVIEW_CYCLE.md:52` (also the installed copy `docs/process/REVIEW_CYCLE.md`)
- **Evidence:** the paragraph now reads "the review must be a file (the points were numbered by hand)". With the table deleted, "the points" has no antecedent for a reader of a shipped document. Task 3's acceptance grep passes (nothing for `Phase 2|CP2| his |first cycles`); `grep -rIn "first cycles"` finds no link to the removed heading outside historical plan records.
- **Direction:** Consider dropping or rewording the parenthesis so it needs no history. Style only.
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

## Gates run

| Command | Counts | Result |
|---|---|---|
| `python3 bundles/base/tools/build.py --check` | n/a | `lint ok` |
| `.venv/bin/python -m pytest bundles/base/tests -q` (at merge HEAD `7a79d22`, includes #32's tests) | 2033 passed, 1 skipped | pass (the Task 6 note's 1955 passed is for `aabccb3`; not re-run at that commit) |
| `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` | 1 passed, 2033 deselected | pass |
| `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` | n/a | equal |
| manifest hashes vs files (`shasum -a 256`, 3 files) | 3 of 3 | equal |
| `install.py --status` | not run | needs the unzipped bundle; I did not rebuild |
| server tests, `tests/live`, `vendor_web.py --check` | not run | outside CP1 verification |

## CI on the pushed commit

Not checked: I did not read CI for `aabccb3` (no `gh` call made; the plan says a human confirms CI).

## Tests run and changed

One test added (`test_deferred_text_fixes_f1_f4_f5`), none changed, none deleted. This is text work, not a bug fix, so the failing-first rule applies only as the plan's own acceptance line; see F2. Real-use evidence for the changed text (item d of the standard): no evidence yet, by nature of these edits.

## Could not check

- The failing-first run of Task 5 on the old files (F2).
- The coder's own shell history and the guard's behavior during Task 6.
- CI for the commit reviewed; `install.py --status` and the install itself (not rebuilt).
- Whether the owner has read and ticked the Task 1 to 4 diff in the PR.

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above.
