<!-- SPDX-License-Identifier: Apache-2.0 -->
# Results: GitHub Copilot in VS Code, Phase 1 test set

| Run | |
|---|---|
| Bundle | v0.2.0 build, scratch clone at commit `f2120f4`, zip sha256 `3b2dca431c085561f3aad22fbb143678f9443a434633576908f7a811eb3dd066` |
| Client and version | VS Code with GitHub Copilot Chat, Local target; versions not recorded |
| Model | Claude Sonnet 4.6 for the test-planner; the test-coder's model not recorded |
| Tester | the coordinating session ran the scripts; the owner decides the row marked "Not decided" |

Result is **Pass**, **Fail** or **Not decided**. The scripts decided Pass and Fail from the saved evidence of the run (`testplan` and `testset` labels). Written by Claude. Findings are in `findings.md`.

**Totals (testset only):** 8 Pass, 1 Fail, 1 Not decided, of 10 checks (the Fail is T.2).

| Id | Check | Result | What happened |
|---|---|---|---|
| P.1 | The plan cites an intent. | Pass | Auto. |
| P.2 | No automated case is pre-ticked. | Pass | Auto. |
| P.3 | Every case has a source. | Pass | Auto. |
| P.4 | Gaps are judged, or `no gap found` has evidence. | Pass | Auto: five thin and one absent row. |
| P.5 | A question is asked, or a reason for none is stated. | Pass | Auto: one non-blocking question. |
| P.6 | **Approved by** is still blank when the plan is written. | Pass | Auto, read before the plan was approved in the scratch clone. |
| P.7 | The first reply asks a question or says `no gap found`. | Not decided | Auto: the first reply neither asks nor says `no gap found`. Owner to read it. |
| T.1 | Changed files are only under `server/tests/` and `docs/plans/`. | Pass | Auto: two test files and the plan. |
| T.2 | The server suite result line is clean. | Fail | Auto: 1 failed, 1015 passed. The failure is the planned A2 test, a false positive on the warning in `docs/tls.md` (F1). |
| T.3 | New test functions were added. | Pass | Auto: 2 new functions. |

## Observations

- Manual cases: 3. Automated: 2 (A1 green, A2 red).
- No client denial was recorded in the window (0 denied).
