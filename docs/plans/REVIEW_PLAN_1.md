# REVIEW_PLAN_1.md

**Phase:** `docs/plans/PHASE_1_TEST_PLAN.md` (automated cases A1-A13 and the four product fixes that followed); the phase plan is `PHASE_1_PLAN.md`
**Intent:** `intent/INT-1-security-baseline.md`, `intent/INT-6-installer.md`
**Commit reviewed:** revision 2: `c76f9c1` on `claude/phase1-test-set-f37394` (the fixes `e4479a5`, `e01970c`, `87e66b4`, `42b3109`, and the plan notes `4e1190c`, `3286be3`, `535f44e`, `c76f9c1`). Revision 1 reviewed `33d1884` plus the then-uncommitted tests (committed since as `0644d8c`).
**Plan version:** test plan: Approved by Michael Hay on November 9, 2026. Phase plan: Approved by Michael Hay 2026-11-01 with amendments to 2026-11-02.
**Policy used:** `REVIEW.md`. The `Review process` rule in `AGENTS.md` (solo repository, owner Michael Hay, no second approver): applies in the sense that the owner is the sole approver; no second approver is required.
**Revision:** 2, 2026-11-09 (time not recorded)

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-09 | 33d1884 + working tree | First review: F1-F5 |
| 2 | 2026-11-09 | c76f9c1 | Re-review after the test-coder repairs and the four bug-coder fixes. F1 and F3 repaired (verified in code); F2 rejected by the owner (verified: A1 create cases assert the refusal and now pass); F4 and F5 deferred (recorded in the test plan). Reviewed the four fixes and the one test correction. New findings: F6 (Nit), F7 (Nit), F8 (Nit) |

## Counts by severity

| Severity | Open | Repaired | Deferred | Rejected |
|---|---|---|---|---|
| Important | 0 | 2 (F1, F3) | 0 | 1 (F2) |
| Nit | 3 (F6, F7, F8) | 0 | 2 (F4, F5) | 0 |

## Known and recorded, not findings

- The folder-symlink gap in the A1 fix (`write.py` checks only the last path component, so a symlinked folder such as `wiki/x -> .git` is not covered): deferred by the owner and recorded in `PHASE_1_TEST_PLAN.md` line 400, with the A1 fix note at line 188.
- The audit row the A4 fix writes for each admin-only caller of `/health` (an `authorizer.refusal` row, not throttled): accepted by the owner, recorded at `PHASE_1_TEST_PLAN.md` line 232.

## Findings

### Bugs

**F1 (Important) — A7 flaky leak needle** (revision 1)
- **State: repaired (test-coder), verified.** `server/tests/test_secret_hygiene.py:141` now reads `secret.split("_", 2)[2]`, so the needle is always the full secret part. I ran `pytest -q --no-header -p no:cacheprovider tests/test_secret_hygiene.py -k A7` 35 times in separate processes: 35 passed, 0 failed (revision 1: 5 of 35 failed). The repair was made before the tests were committed (`git log` shows the file changed only in `0644d8c`).

**F6 (Nit) — The A8 line-break check covers `\n` and `\r` only**
- **Location:** `server/wiki_backend/register.py:19-24` (`_multi_line_field`)
- **Evidence:** read from the code: the check tests `"\n" in value or "\r" in value`. Other characters that Python's `str.splitlines()` and YAML 1.1 treat as line breaks (for example U+0085, U+2028, U+2029, and also `\x0b`, `\x0c`) pass through. Whether any of them reaches the index or frontmatter as a second entry is unverified: I did not probe it (I may not write code, and the test does not use them). INT-1 constraint and the A8 outcome say a value is "one entry or refused"; A8 itself uses `\n`, `: `, `## `, so the green result does not cover these.
- **Direction:** the owner may want the helper to refuse any `str.splitlines()` break, or record the narrower scope as a known gap.
- **State:** open

### Security

No Important finding. A3, A5, A6, A7 are green and no leak was found. Fix review, by pass:

- **A2 (`scopes.py:97-100`):** addresses the named defect. `check_readable` resolves the real location and refuses unless it also starts with `wiki/` or `raw/`. `confine()` already refuses a link that leaves the root (`scopes.py:57-58`), so the `relative_to(...)` call cannot raise `ValueError` for an outside target; it can only see in-root targets. A2 asserts `ValueError` or `FileNotFoundError` and `PathRefused` is accepted by that (both A2 cases pass). A link from `wiki/` to another readable page stays readable (not tested; not a regression of anything the plan names).
- **A4 (`server.py:931-934`):** addresses the named defect. The detail now needs `authorizer.READ` through `_store_access.authorize(..., READ, None, credential_id)`; `Decision.__bool__` returns `allowed` (`authorizer.py:135`), so `bool(...)` is correct. Anonymous, wrong-credential and disabled callers still get the status only (the earlier A4 cases pass). The refusal audit row is the known item above.
- **A1 (`write.py:138-145`):** addresses the named defect and the label: the check runs before `mkdir` and before the existence check, so the three `create` variants return `status == "error"` instead of `conflict` (the owner's F2 decision), and the three `update-with-etag` variants are refused instead of `updated`. The target is the last path component only (known gap above).
- **A8 (`register.py:47-52`, `555-565`):** refuses a line break in `description`, `repo` or `owner` before anything is written, on both register and update, as the owner chose (option A, Q4). The names of the fields are in the refusal, the values are not. See F6 for the narrow character set.

### Compliance

**F2 (Important) — A1 expectation `error` versus `conflict`** (revision 1)
- **State: rejected by the owner.** Decision (2026-11-09, `PHASE_1_TEST_PLAN.md` line 187): `conflict` is not a refusal; the create variants keep asserting `status == "error"`. Verified in code: `test_path_policy.py:205-228` asserts `result.get("status") == "error"`, a non-empty `error`, an unchanged tree, an unchanged git log and a clean `git status` for every variant, and I ran the file (all six A1 cases are part of the 1060 passing). The refusal is on the symlink: it comes from `write.py:138-145` before the existence check, with the message "is a symbolic link".

**F7 (Nit) — The fix commits carry no "Rule exceptions" line**
- **Location:** `e4479a5`, `e01970c`, `87e66b4`, `42b3109` (commit messages), and the fix notes at `PHASE_1_TEST_PLAN.md` lines 188, 203, 232, 290
- **Evidence:** the working rules require every report from an agent that changed files or ran commands to carry a "Rule exceptions" line. The only such line in the test plan is the test-coder's (line 402). The `**Fixed:**` notes (written by the bug-coder) have none. Compared with the record: `.manifold/guard-log.jsonl` has one entry (the test-coder's `no-heredocs`, 2026-11-09T12:39:26Z, already reported and matched in revision 1) and no bug-coder entry; each fix diff touches only the file the note names (plus the one test line for A8). So nothing contradicts a "none", but the line is absent, not stated.
- **Direction:** add a "Rule exceptions" line to each fix note, or confirm with the coordinator that it was reported elsewhere.
- **State:** open

### Tests

**F3 (Important) — A1 and A2 could not both go green** (revision 1)
- **State: repaired (test-coder), verified.** `test_path_policy.py:219-224` computes the etag as `hashlib.sha256((root / link).read_bytes()).hexdigest()`, with a comment naming `generate_etag`; `wiki_read` is no longer called in A1. Both A1 (6 cases) and A2 (2 cases) are green together after the fixes (full suite below). I did not re-check that the sha256 of the bytes equals `generate_etag` for these files; the A1 update cases are refused before the etag is compared, so a mismatch would not change the result.

**F4 (Nit) — Green cases not seen failing first** (revision 1)
- **State: deferred (owner, 2026-11-09).** Recorded at `PHASE_1_TEST_PLAN.md` line 396, with the reason (no production change allowed) and no new test.

**F5 (Nit) — A10's empty-host case is checked only through `_check_auth_settings()`** (revision 1)
- **State: deferred (owner, 2026-11-09).** Recorded at `PHASE_1_TEST_PLAN.md` line 398; the uvicorn bind for an empty `MANIFOLD_HOST` stays unverified.

**Existing tests and the owner-approved correction.** `git diff 0644d8c HEAD -- server/tests` shows one changed line in one file (`test_register_untrusted_values.py:108`): the assertion `assert result.get("error") or result.get("refused")` became `... or result.get("status") == "error"`. This is minimal: it only adds an accepted refusal shape; the next line (`assert _snapshot(root) == before`) still demands that nothing changed, and the other A8 checks are untouched. The reason is sound on the code: `WikiRegisterResponse` has `status` and `message` and no `error` field (`wiki_backend/models.py:86-`, and the refusal in `register.py:558-565` returns `status="error"`). The approval is recorded in `PHASE_1_TEST_PLAN.md` lines 289 and 290 ("Owner-approved test correction (2026-11-09)") and in the commit subject. The matching rule (AGENTS.md "Tests under fix") asks for the test name, assertion, reason and owner's yes to be recorded; all four are. No other existing test changed in the four fixes. The fixes are not regression-tested by new tests beyond A1, A2, A4 and A8 themselves; those are the failing-first tests.

**F8 (Nit) — A4 does not pin the new behavior for a reader-only or contributor principal, and `/health` now reads the store before its own try block**
- **Location:** `server/server.py:931-934`
- **Evidence:** read from the code: `_store_access.authorize(...)` runs before the `try:` that turns a health failure into `unhealthy`. If the store raises for an authenticated caller, the route would raise instead of returning an `unhealthy` payload. An anonymous container health check never reaches that call (`caller` is `None`), so the container check is unaffected. Not reproduced.
- **Direction:** consider whether the authorization call should sit inside the same guarded block, or accept and record the behavior.
- **State:** open

### Context files

No finding. No change makes `AGENTS.md`, `CLAUDE.md` or `REVIEW.md` out of date.

## Scope check on the fixes

Each fix commit changes one production file and nothing else (`git show --stat`): `server.py` (6 lines), `scopes.py` (5), `write.py` (9), `register.py` (20, plus the one test line). The only change outside the named defect is whitespace: `write.py` line 140 loses trailing spaces on a blank line (inside the A1 fix commit). That is trivial and is not reported as a finding. No new dependency, no change to other modules. The case-by-case table of revision 1 still holds for A3, A5-A7, A9-A13 (unchanged, green).

| Case | State on `c76f9c1` |
|---|---|
| A1 | green (6 of 6), red before `87e66b4` |
| A2 | green (2 of 2), red before `e01970c` |
| A4 | green, red before `e4479a5` |
| A8 | green (6 of 6), 4 were red before `42b3109` |
| A3, A5-A7, A9-A13 | green; not seen failing (F4, deferred) |

I did not read the held-out scenarios; none are in this repository. I did not run the fixes against the reverted code (the failing-first state is taken from the coder's notes and my revision 1 runs on `33d1884`).

## Rule exceptions compared

The test-coder's line (`PHASE_1_TEST_PLAN.md` line 402): "one attempted heredoc in a Bash command, refused by the guard hook before it ran (no file written); otherwise none." `.manifold/guard-log.jsonl` still has exactly one entry (`no-heredocs`, `test-coder`, 2026-11-09T12:39:26Z): matches. The bug-coder fixes state no line (F7). The diffs between `0644d8c` and `c76f9c1` touch only the four production files, one test line and `PHASE_1_TEST_PLAN.md`; the commit log shows eight commits since `a7047e7`, all with the co-author trailer and nothing that looks like a hook bypass. Matched where a line exists; not comparable where there is none.

## Gates run

| Command | Counts | Result |
|---|---|---|
| `cd server && ../.venv/bin/python -m pytest -q` (on `c76f9c1`) | 1060 passed, 2 warnings, 136.40 s | matches the coordinator's 1060 passed; no failures |
| `cd server && ../.venv/bin/python -m pytest -q --no-header -p no:cacheprovider tests/test_secret_hygiene.py -k A7`, 35 separate processes | 35 passed, 0 failed | A7 stable (revision 1: 5 of 35 failed) |
| `.venv/bin/python -m pytest bundles/base/tests -q` | not run | the four fixes change only `server/`; not run in this revision |
| `.venv/bin/python tools/vendor_web.py --check` | not run | same reason |

## CI on the pushed commit

Not checked (no pull request or remote run was named).

## Could not check

- The manual cases M1-M4 (real clients, real Docker): not implemented and outside the reviewer's tools.
- Whether characters other than `\n` and `\r` get through A8 (F6), and what uvicorn binds for an empty `MANIFOLD_HOST` (F5, deferred).
- A write through a symlinked folder (known, deferred).
- Whether the fixes fail the tests when reverted (taken from the notes and revision 1).

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above.

Rule exceptions: none by the reviewer. I wrote only `docs/plans/REVIEW_PLAN_1.md`, ran read-only `git` commands and `pytest` (the runs create temporary directories under pytest's temp area), and no guard blocked any of my commands.
