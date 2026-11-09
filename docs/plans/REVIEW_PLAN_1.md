# REVIEW_PLAN_1.md

**Phase:** `docs/plans/PHASE_1_TEST_PLAN.md` (automated cases A1-A13 as implemented in the uncommitted working tree); the phase plan is `PHASE_1_PLAN.md`
**Intent:** `intent/INT-1-security-baseline.md`, `intent/INT-6-installer.md`
**Commit reviewed:** `33d1884ee58f14e37beb565010af7ff3e7996713` on `claude/phase1-test-set-f37394`, plus the uncommitted change (5 modified and 5 new files under `server/tests/`, and the test plan itself)
**Plan version:** test plan: Approved by Michael Hay on November 9, 2026. Phase plan: Approved by Michael Hay 2026-11-01 with amendments to 2026-11-02.
**Policy used:** `REVIEW.md`. The `Review process` rule in `AGENTS.md` (solo repository, owner Michael Hay, no second approver): applies in the sense that the owner is the sole approver; no second approver is required.
**Revision:** 1, 2026-11-09 (time not recorded)

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-09 | 33d1884 + working tree | First review |

## Counts by severity

| Severity | Open | Repaired | Deferred | Rejected |
|---|---|---|---|---|
| Important | 3 | 0 | 0 | 0 |
| Nit | 2 | 0 | 0 | 0 |

## Findings

### Bugs

**F1 (Important) — A7 is flaky: the leak needle is cut short when the token's secret part contains `_`**
- **Location:** `server/tests/test_secret_hygiene.py:141` (`secret.split("_")[2]`)
- **Evidence:** `secrets.token_urlsafe(32)` (`manifold_security/tokens.py:73`) uses an alphabet that includes `_`. The credential is `mf_<id>_<secret>`, so when the secret contains `_`, `split("_")[2]` is only the part before the first `_`: one character, two characters, or the empty string. Such a needle appears by chance in the git history (`'d' not in 'commit bea8...'`) or is the empty string, which is always "in" the text. I ran `pytest tests/test_secret_hygiene.py -k A7` 35 times in separate processes: 5 failed, about 14 percent. Failures seen: `assert 'd' not in ...`, `assert '93' not in ...`, `assert 'J' not in ...`, `assert '' not in ...`, plus one more "leaked: ..." with a short needle. All were the leak loop at line 142.
- **Order or timing:** neither. Run alone, in file order (3 of 3 passed), with A3 and A7 only (passed), and in full-suite order (passed in the 1060-test run). The only variable is the random token. The failure is a flawed test, not a leak.
- **The reported failure:** "authors include alice and reg" (line 143) did not fail in any of my 35 repeated runs or in the full suite. The failure I reproduced is the leak assertion at line 142. If the failure you saw was line 143, I could not reproduce it; it may be a misattribution from truncated output.
- **Direction:** take the secret part with `split("_", 2)[2]` (or slice after the second underscore), so the needle is always the full 43 characters.
- **State:** open

### Security

No finding. A3, A5, A6 and A7 are green and no leak was found; A3's and A7's coverage caveats are stated in the test plan.

### Compliance

**F2 (Important) — The plan's A1 expectation and the implemented A1 disagree on `error` versus `conflict`, and the plan's note records the mismatch without a decision**
- **Location:** `server/tests/test_path_policy.py:221`; `PHASE_1_TEST_PLAN.md` line 183 (Expected outcome `status == "error"`) and line 186 (Todo)
- **Evidence:** Of the 6 red A1 parameter cases, the 3 `create` cases fail with `'conflict' == 'error'` ("File already exists ... Provide current etag for update."). Nothing is written in those cases (the test asserts the tree is unchanged after that line, but the status assert fails first). A regular file would produce the same `conflict`, so those three cases are red for the reply label and not for the symlink defect. Only the 3 `update-with-etag` cases fail with `updated`, which is the real defect. The coder's note mentions the `conflict` result but does not say whether the owner accepts `conflict` as a refusal.
- **Direction:** the owner decides whether `conflict` counts as a refusal for the no-etag path. If yes, the `create` variants should assert "not updated and tree unchanged"; if no, they will stay red after the defect is fixed unless the fix returns `error` before the existence check. Record the decision in the test plan.
- **State:** open

### Tests

**F3 (Important) — A1 and A2 cannot both go green: A1's `update-with-etag` setup reads through the symlink with `wiki_read`**
- **Location:** `server/tests/test_path_policy.py` (A1, the line `arguments["etag"] = wiki_read(root, link).etag`)
- **Evidence:** A2 is red because `wiki_read` returns content through an in-root symlink. The expected fix for A2 makes `wiki_read` raise on those links. A1's `update-with-etag` variant obtains its etag by calling `wiki_read(root, link)` on the same kind of link, so after the A2 fix the A1 setup raises `ValueError` and A1 cannot pass. The pair of checks therefore cannot both be satisfied by a correct fix. Read from the code; I did not apply a fix, so this is an inference, not an observed failure.
- **Direction:** compute the etag without `wiki_read` (for example hash the bytes directly, following the etag definition in the backend), so A1 does not depend on A2's defect.
- **State:** open

**F4 (Nit) — A3 and A7 and the green A-cases were not seen failing first**
- **Location:** `PHASE_1_TEST_PLAN.md` lines 214, 242, 256, 270, 298, 312, 326, 340, 354
- **Evidence:** The coder's notes record "Not seen failing" for A5, A6, A7, A9, A10, A11, A12 and A13 (the A13 scanner self-check was seen catching a sample recommendation, not a repository document). A3 records "GREEN" without a failing run. The notes give the reason (no production change allowed), and A5 has a probe showing the check is not vacuous. For these cases the plan expects no defect, so this is a gap in evidence, not a rule breach. Red evidence: A1, A2, A4 and A8 were seen failing and I reproduced all four (below).
- **Direction:** for A3, A7, A9, A11 and A12, consider a one-off negative check (for example a logging statement of the header, a leaked secret written to a file, a second process without the lock) to show the assertion can fail; record it in the plan.
- **State:** open

**F5 (Nit) — A10 is partly outside the plan's wording and carries an unverified observation**
- **Location:** `server/tests/test_startup.py` (A10 tests); `PHASE_1_TEST_PLAN.md` line 312
- **Evidence:** The plan's expected outcome for `MANIFOLD_HOST=""` is "starts with a warning and refuses every request". The test implements that through `server._check_auth_settings()` only, and the plan's note says `check_startup(conn, "")` directly would refuse. The note also records "unverified" what uvicorn binds when `MANIFOLD_HOST` is set empty (`server.py` passes `""` to uvicorn). That is the real question behind S6 ("start on a shared address because a setting was left empty") and it is left open, so A10's empty-host case may pass while the process still binds somewhere unexpected.
- **Direction:** ask the owner whether the uvicorn bind for an empty `MANIFOLD_HOST` should be checked (a small real-process check) or recorded as a gap.
- **State:** open

### Context files

No finding. No change makes `AGENTS.md`, `CLAUDE.md` or `REVIEW.md` out of date.

## Case-by-case check (point 1) and red tests (point 2)

| Case | Implemented as planned | Result I saw | Notes |
|---|---|---|---|
| A1 | Yes, in `test_path_policy.py`; 3 links x create/etag; extra grant on `acme-web` is recorded | 6 red | 3 `update-with-etag` cases red for the named defect (`updated`); 3 `create` cases red on `conflict` label: see F2, F3 |
| A2 | Yes | 2 red (`DID NOT RAISE`) | Red for the named defect: content returned through the link |
| A3 | Yes, two tests, in-process and real process | green | not seen failing, F4 |
| A4 | Yes | red | `assert {...'checks'...} == {'status': 'healthy'}` for "admin-only": the named defect, and the earlier anonymous, wrong and disabled cases passed first |
| A5, A6 | Yes | green | not seen failing, F4 |
| A7 | Yes | green, flaky | F1 |
| A8 | Yes, 3 fields x register and update | 4 of 6 red | hostile `description`: index grew by 6 (bound 1); `repo`/`owner`: injected heading and frontmatter key on register; `repo` on update: injected heading. Red for the named defects; the bound is measured against a benign run in the same instance, which is sound |
| A9 | Yes | green | |
| A10 | Yes (5 tests) | green | F5 |
| A11, A12, A13 | Yes | green | A12 took about 53 s per the coder's note |

No case was skipped, weakened or deleted: `git diff -U0` shows 317 added lines and no removed lines in the 5 modified files, so no existing test was edited. I did not read the held-out scenarios and none are in this repository.

## Rule exceptions compared

The coder's line: "one attempted heredoc in a Bash command, refused by the guard hook before it ran (no file written); otherwise none." `.manifold/guard-log.jsonl` has exactly one entry: rule `no-heredocs`, tool `Bash`, agent `test-coder`, 2026-11-09T12:39:26Z. That matches the line. The diff shows only the 10 test files and the plan; no production code is changed (`git status` lists only `server/tests/` and `docs/plans/PHASE_1_TEST_PLAN.md`). The commit log was not needed because nothing is committed. Matched.

## Gates run

| Command | Counts | Result |
|---|---|---|
| `cd server && ../.venv/bin/python -m pytest -q --no-header` | 13 failed, 1047 passed, 2 warnings, 129.62 s | The 13 failures are exactly the red cases: A4 (1), A1 (6), A2 (2), A8 (4). Nothing else failed in that run (A7 passed that time) |
| `.venv/bin/python -m pytest bundles/base/tests -q` | not run | the change touches only `server/tests/` |
| `.venv/bin/python tools/vendor_web.py --check` | not run | same reason |
| `cd server && ../.venv/bin/python -m pytest -q -x --no-header -p no:cacheprovider` | 1 failed, 91 passed (stopped on A4) | exploration only |
| `... pytest tests/test_secret_hygiene.py -k A7` x 35 | 30 passed, 5 failed | F1 |
| `... pytest tests/test_secret_hygiene.py` x 3 (file order) and A3 + A7 only | all passed | no order dependence |

## CI on the pushed commit

Not checked: the change is uncommitted and nothing is pushed.

## Tests run and changed

Failing-first evidence: A1, A2, A4 and A8 were seen failing by the coder and by me, for the defects the plan names (A1's `create` variants only for a different label: F2). No existing test was changed. No approval for any change to an existing test was needed.

## Could not check

- The manual cases M1-M4 (real clients, real Docker): not implemented and outside the reviewer's tools.
- What uvicorn binds when `MANIFOLD_HOST` is empty (F5).
- Whether A9's processes and A12's SSE behavior would fail against a broken implementation; I did not mutate production code.
- The "authors include alice and reg" intermittent failure as stated: not reproduced (F1).

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above.

Rule exceptions: none by the reviewer. I wrote only `docs/plans/REVIEW_PLAN_1.md`, ran read-only `git` and `pytest` commands (the test runs create temporary directories under pytest's temp area), and no guard blocked any of my commands.
