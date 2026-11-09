<!-- SPDX-License-Identifier: Apache-2.0 -->
# Results: Claude Code (terminal), Phase 1 test set

| Run | |
|---|---|
| Bundle | v0.2.0 build, scratch clone at commit `f2120f4`, zip sha256 `3b2dca431c085561f3aad22fbb143678f9443a434633576908f7a811eb3dd066` |
| Client and version | Claude Code, version not recorded |
| Model | Not recorded (see `summary.md`) |
| Tester | the coordinating session ran the scripts; the owner decides the row marked "Not decided" |

Result is **Pass**, **Fail** or **Not decided**. The scripts decided Pass and Fail from the saved evidence of the run (`testplan` and `testset` labels). Written by Claude. Findings are in `findings.md`.

**Totals (testset only):** 9 Pass, 0 Fail, 1 Not decided, of 10 checks.

| Id | Check | Result | What happened |
|---|---|---|---|
| P.1 | The plan cites an intent. | Pass | Auto: the plan cites `INT-1` and `INT-6`. |
| P.2 | No automated case is pre-ticked. | Pass | Auto: none ticked before the test-coder ran. |
| P.3 | Every case has a source. | Pass | Auto. |
| P.4 | Gaps are judged, or `no gap found` has evidence. | Pass | Auto: three thin and one absent row in the coverage table. |
| P.5 | A question is asked, or a reason for none is stated. | Pass | Auto: "No questions because" with four reasons. |
| P.6 | **Approved by** is still blank when the plan is written. | Pass | Auto, read before the plan was approved in the scratch clone. |
| P.7 | The first reply asks a question or says `no gap found`. | Not decided | Auto: no test-planner chat found in the window (the planner ran as a subagent). Owner to read the first reply. |
| T.1 | Changed files are only under `server/tests/` and `docs/plans/`. | Pass | Auto: `server/tests/test_revocation_smoke.py` and `docs/plans/PHASE_1_TEST_PLAN.md`. |
| T.2 | The server suite result line is clean. | Pass | Auto: 1015 passed, 2 warnings. |
| T.3 | New test functions were added. | Pass | Auto: 1 new function. |

## Observations

- Manual cases in the plan: 3 (TLS client walkthrough, Linux `manifold init` with Docker, a SQLite bind-mount probe). Automated: 2 (A1 new test, A2 gate).
- No client denial was recorded in the window (0 denied).
