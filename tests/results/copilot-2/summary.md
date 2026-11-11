<!-- SPDX-License-Identifier: Apache-2.0 -->
# Run copilot-2: GitHub Copilot in VS Code, Phase 1 test set (after INT-25)

| | |
|---|---|
| Client | VS Code 1.145.2 (the installed app, read after the run), GitHub Copilot Chat 0.73.0 (from the saved chat), Local target |
| Model | Claude Sonnet 4.6 for the test-planner and the test-coder (read from the saved chats) |
| Bundle | v0.2.0 build, scratch clone at commit `f2120f4`, zip sha256 `3b2dca431c085561f3aad22fbb143678f9443a434633576908f7a811eb3dd066` |
| Scope | Local checks for `PHASE_1_PLAN.md` (task 5 of the live protocol), `testplan` and `testset` evidence only; not the 67-check protocol |
| Result | **9 Pass, 1 Fail, of 10 (testset only)** |

One run is one sample. It is not a ranking of clients or models.

## What happened

1. The `test-planner` was asked: "Plan local tests for docs/plans/PHASE_1_PLAN.md." It wrote `docs/plans/PHASE_1_TEST_PLAN.md`: three manual and two automated cases (A1 import-merge tightening across a restart, A2 a scan of `docs/tls.md` for certificate-bypass advice), a coverage table (26 adequate, 5 thin, 1 absent rows) and one non-blocking question. The planner wrote its own text on the `Answer:` line of that question.
2. The plan was approved in the scratch clone under a limited, stated authority (allowed for throw-away plans only).
3. The `test-coder` wrote two tests (55 lines in `server/tests/test_deploy_files.py` and `server/tests/test_revocation_smoke.py`). A1 is green. A2 is **red**: `docs/tls.md` line 32 is the warning "Never turn off certificate checking (`-k`, `--insecure`, ...)", so a substring scan for those words finds the prohibition itself. The coder reported it, left it red and gave the owner two options (rephrase the warning, or let the test allow the string inside a "never do this" sentence). It labelled the result "defect found" and called the test correct, so it did not see that the planned check itself was flawed (F9). Before writing the test it had searched `docs/tls.md` for `-k ` only and predicted the test would pass. It also used `/docs/_sidebar.md` instead of the plan's `/health` for A1, because `/health` is an open path that returns 200 for a revoked credential (F10), and it answered the planner's Q1 itself by reading `test_startup.py` (no case missing).
4. Decision (owner, throw-away run): the red test stays red and is recorded as a finding about the planned case. Nothing is fixed.

## What it showed

- The "before" defect is gone in this sample: nothing pre-ticked, an intent cited, coverage judged, two new cases, a question asked.
- The red A2 is a flawed planned case (a naive substring check), not a product defect.
- The coder behaved as INT-25 asks about red tests (reported, did not weaken, offered options) but diagnosed the wrong thing: it read a bad planned check as a product defect. It did not try to make either check fail first: the chat shows no step that breaks the code to see the test go red.

## Compared with claude-code-2

Held constant: the prompts and their order; the blob of `PHASE_1_PLAN.md` (`b8358cfb306ffc5a0c035a67107b5d23d821f6ba`); the `server` tree (`ba06febdb87cec49ef5ad9e4ef8b053fcec39fc6`); the build zip checksum above; the agent sources. Differing: client, model, hooks and guard enforcement, who ran each agent, and that both ran in scratch clones.

| Compared | claude-code-2 | copilot-2 |
|---|---|---|
| Files produced | plan, 1 test | plan, 2 tests |
| Cases (automated, manual) | 2, 3 | 2, 3 |
| New cases beyond existing tests | A1 (grant removal) | A1 (import-merge restart), A2 (tls.md scan) |
| Intent cited | `INT-1`, `INT-6` | cited (see its plan; not recounted) |
| Questions asked | none, with four reasons | 1, non-blocking, answered by the planner itself |
| Plan checks P.1 to P.6 | all pass | all pass |
| P.7 (first reply) | pass (owner): the first reply was a mode statement | pass: the first reply opened with a mode statement, then showed its planned coverage, the gaps and a question and asked for confirmation before writing (the script saw only the opening line) |
| Test functions added | 1, green | 2, one green, one red |
| Server suite | 1015 passed | 1 failed, 1015 passed (the red A2 test) |
| Coverage of each `PHASE_1_PLAN.md` task | The cases name Tasks 1, 24, 27, 34, 36 and 58: 6 of 58 (counted from "Related task" and not from the agent's claim); the coverage table is by intent seed, so the other 52 are neither claimed nor ruled out | The cases name Tasks 29, 34, 36 and 47: 4 of 58, same method and same limit |
| Breaches | none found in the diff; no guard log captured; the coder ran the full suite against its own text | none found in the diff; no guard log captured; the coder ran the tests unsandboxed because the VS Code sandbox blocks the git config |
| Time and turns | planner about 6 minutes (2 user messages), coder about 3 minutes (2 user messages), from the subagent session timestamps | planner about 6 minutes of model time over 3 requests, coder about 10 minutes, from the saved chat's elapsed times |
| Other | the coder's A2 ran the full suites | the planner filled the human-only `Answer:` line and asked a question a search could answer |

The "before" runs (both clients) pre-ticked all 45 automated cases, cited no intent and asked no question; those plans are throw-away evidence and are not copied here.

## Files

[`results.md`](results.md) one row per check. [`findings.md`](findings.md) what the run showed.
