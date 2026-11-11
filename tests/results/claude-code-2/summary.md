<!-- SPDX-License-Identifier: Apache-2.0 -->
# Run claude-code-2: Claude Code, Phase 1 test set (after INT-25)

| | |
|---|---|
| Client | Claude Code 2.1.317 (read from the saved session files) |
| Model | `claude-sonnet-4-6` for the planner and the coder (read from the saved session files; `lp_verify.py` itself printed "not recorded") |
| Bundle | v0.2.0 build, scratch clone at commit `f2120f4`, zip sha256 `3b2dca431c085561f3aad22fbb143678f9443a434633576908f7a811eb3dd066` |
| Scope | Local checks for `PHASE_1_PLAN.md` (task 5 of the live protocol), `testplan` and `testset` evidence only; not the 67-check protocol |
| Result | **10 Pass of 10 (testset only)**; P.7 passed by owner decision, the first reply being a mode statement (see `results.md`) |

One run is one sample. It is not a ranking of clients or models.

## What happened

1. The `test-planner` was asked: "Plan local tests for docs/plans/PHASE_1_PLAN.md." It wrote `docs/plans/PHASE_1_TEST_PLAN.md`: three manual cases and two automated ones (A1 a new test, A2 a gate that re-runs the existing suites), a coverage table (29 adequate, 3 thin, 1 absent rows), and "No questions because" with four reasons.
2. The plan was approved in the scratch clone under a limited, stated authority (allowed for throw-away plans only). Nothing from this run is kept as an approved plan.
3. The `test-coder` was asked: "Implement the test plan docs/plans/PHASE_1_TEST_PLAN.md." It added one test, `test_a_grant_removal_is_refused_on_the_next_request_without_a_restart_and_after_one`, in `server/tests/test_revocation_smoke.py` (+17 lines), green. For A2 it ran the full server suite (1015 passed), the bundle suite (1954 passed, 1 skipped) and the vendored-files check, although the agent's own text says to leave the full suite to a human: the plan's A2 asked for it, so plan and text conflict (F4).

## What it showed

- The "before" defect is gone in this sample: no case was pre-ticked, the plan cites two intents (`INT-1`, `INT-6`), judges coverage per intent seed, and found a real thin spot (grant removal checked only through CLI output, not on a live server).
- The new test is real work, not a mapping of an existing one. It is one test, though.
- The coverage table is by intent seed, not by `PHASE_1_PLAN.md` task (F2); each case does name its related tasks.

## Compared with copilot-2

See "Compared with claude-code-2" in [`../copilot-2/summary.md`](../copilot-2/summary.md).

## Files

[`results.md`](results.md) one row per check. [`findings.md`](findings.md) what the run showed.
