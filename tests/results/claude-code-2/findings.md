<!-- SPDX-License-Identifier: Apache-2.0 -->
# Findings: Claude Code, Phase 1 test set

Each row is something the run showed that is not a plain pass or fail of a check. One sample; not a ranking.

| # | Seen at | What happened | Cause | Fix | Status |
|---|---|---|---|---|---|
| F1 | plan | The plan cites intents, judges coverage per seed and plans a new case. It found one real thin spot: grant removal was tested through CLI output only. | INT-25 changes working as written. | None. | Closed |
| F2 | plan | The plan maps cases to intent seeds, not to the tasks of `PHASE_1_PLAN.md`. The "before" plans mapped to tasks. Per-task coverage cannot be read from it. | The new template asks for sources and seeds, not task traceability. | Consider a per-task column in the template. | Open (template) |
| F3 | plan | Only one new automated case was planned for a phase of 58 tasks. The gate case (A2) re-runs existing suites. | Coverage was judged adequate for 29 of 33 rows. Unverified whether that judgement is right. | The owner reads the coverage table. | Open |
| F4 | code | The `test-coder` ran the full server suite for A2, though its text says to leave the full suite to a human. | The plan's A2 asked for it; the plan and the agent text conflict. | Decide which wins: the planner stops planning suite-running gate cases, or the coder text allows a run the plan asks for. | Open (agent text) |
| F5 | code | The coder wrote one green test and did not report trying to make it fail first. | Not observed either way. | Ask for the failing-first evidence in the coder's report. | Open |
| F6 | evidence | `lp_verify.py` does not read subagent sessions in full: the model was not recorded and P.7 could not be judged. | Subagent transcripts are stored apart from the main session. | Read subagent transcripts in `lp_verify.py`. | Open (tooling) |
| F7 | evidence | There is no guard log in the evidence, so this run cannot say whether the hook ran. | Evidence capture does not copy the guard log. | Capture the guard log with the evidence. | Open (tooling) |
