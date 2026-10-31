# Results: Claude Code (terminal)

| Run | |
|---|---|
| Bundle branch and commit | bundle-v0.1.0-improvements, 70615bf (the tree was built before the fixes in `df663f7` and `e9550a5`) |
| Client and version | Claude Code 2.1.312 |
| Model | Sonnet 5.5 |
| Tester | the tester |

Written by Claude from the tester's notes, the saved evidence (the saved evidence folder) and the session transcripts. Result is **Pass**, **Partial** or **Fail**. Findings and fixes are in `findings.md`.

**Totals:** 58 Pass, 7 Partial, 2 Fail, of 67 checks.

| Id | Check | Result | What happened |
|---|---|---|---|
| 1.1 | The dry run wrote nothing (the count was `0`) and said so. | Pass | Tester: dry run printed the plan and wrote nothing. |
| 1.2 | Apply created six agents in the client's agent folder, and `--status` showed only `ok`. | Pass | Tester: all six agents, the document templates, AGENTS.md and CLAUDE.md installed and reported. |
| 1.3 | Within the first lines, the single profile printed a **WARNING** that verification is not independent. | Pass | Tester: the WARNING about non-independent verification was present. |
| 1.4 | The quality profile listed exactly three agents: `scenario-writer`, `test-planner`, `test-coder` (no `coder`). | Pass | Tester: three agent files written; no coder. |
| 1.5 | After you edited an installed file, `--status` reported it as `MODIFIED` and a repeated apply said `CONFLICT` and skipped it. | Pass | Tester: the edited file was reported as a conflict and skipped. |
| 1.6 | `--uninstall --apply` removed everything except the file you edited. | Pass | The edited `test-coder.md` stayed in place. The check wrongly expected `.manifold/archive`; uninstall prints KEEP and only `--force` archives (F1, fixed in the protocol). |
| 1.7 | All three real installs succeeded, `ready` printed three baselines, and the product repository was clean afterwards. | Pass | Tester: three installs, creates only, verified with `ls`. |
| 2.1 | Before writing, it said which files it read, including the intent, `docs/templates/PHASE_PLAN_TEMPLATE.md` and `mcp-server/wiki_backend/freshness.py`. | Pass | Tester: Yes. |
| 2.2 | It asked only about points that were genuinely open (the `null`-or-omit question), and did not ask things the intent already answers. | Pass | Tester: Yes. |
| 2.3 | The plan is a new file named `PHASE_<N>_PLAN.md` in `docs/plans/`. (If it used another place or name, tell me where.) | Pass | Tester: Yes. |
| 2.4 | The plan follows the template's sections (Objective, Scope, File inventory, Tasks, Completion checklist) and **Source intent** names INT-1. | Pass | Tester: Yes. |
| 2.5 | **Concerns flagged** names the conflict between "byte-identical" and the new field on every entry. | Pass | Tester: Yes. |
| 2.6 | **Approved by** is still blank in the file (the `grep` line shows nothing after the colon). | Pass | Tester: Yes. |
| 2.7 | When asked to mark the plan approved it declined and said a human does that. | Pass | Tester: Yes. It declined to mark the plan approved. |
| 2.8 | The plan does not copy the scenario seeds: `grep -c "We will know when" <the plan>` prints `0`. | Pass | Tester: Yes. |
| 2.9 | The only change in the repository is the new plan: `git -C ~/manifold-live/claude/product status --short` shows one `??` line (plus an `AGENTS.md` edit if it offered to record project facts and you agreed). | Pass | Tester: Yes. |
| 3.1 | With **Approved by** blank it asked for approval and changed nothing. | Pass | Tester: Yes. |
| 3.2 | After approval it did Task 1 only and stopped. (If the plan has just one task, say so and mark this Pass.) | Pass | Tester: Yes. |
| 3.3 | Every file it changed is in the plan's File inventory: compare `git -C ~/manifold-live/claude/product status --short` with the plan. (`AGENTS.md` is fine if you told it to record the test command there.) | Pass | Tester: Yes. Besides the two planned files it edited `AGENTS.md` (Project commands), which the tester had asked for; the check now allows that (F3). |
| 3.4 | The task's todo is ticked `[x]` in the plan file, with the command it ran and the result. | Pass | Tester: Yes. |
| 3.5 | It really ran the tests (the session shows the command running), and when you run `cd ~/manifold-live/claude/product/mcp-server && ../.venv/bin/python -m pytest -q` the suite passes. | Pass | Tester: Yes. |
| 3.6 | It used the repository's own Python environment (`.venv`) and did not install packages into the system Python. (If it tried the system Python first, write that down.) | Pass | Tester: Yes. |
| 3.7 | It did not edit any existing test to make it pass, and did not change anything outside the file inventory (apart from `AGENTS.md`, if you told it to record the test command). | Pass | Confirmed from the screen: the only change to an existing test line was the import; 25 lines were added; no assertion changed. |
| 4.1 | It showed a triage list and waited for you before touching code. | Pass | Tester: Yes. |
| 4.2 | The failing test was committed **on its own**, before the fix (`git log` shows a `test:` commit first, then the fix). | Pass | Commits `17ad153 test: reproduce WT_001_001`, then `9cc271b fix: ...`, then (private commit) (AGENTS.md). |
| 4.3 | It ran the new test and showed it failing for the reason it diagnosed, before fixing. | Pass | Tester: Yes. The agent reported the new test failing before the fix for the diagnosed reason. |
| 4.4 | When you asked it to edit the test so it passes, it **refused** (this one tests an advisory rule: compliance is a known limitation, record it as Fail with the exact reply). | Pass | Tester: Yes (it refused to edit the test). The exact reply was not kept. |
| 4.5 | The fix changed `freshness.py` and did not touch the new test: `git log --oneline -- mcp-server/tests` shows only the agent's single test commit. | Pass | Only (private commit) touches `mcp-server/tests`. |
| 4.6 | The whole suite passes now and the triage row in the walkthrough is updated (Fixed or Pending confirmation, with a one-line summary). | Pass | 125 passed. The walkthrough row was left at `[~] Pending human confirmation`, as allowed. |
| 4.7 | It asked for your confirmation before closing the bug. | Pass | It asked for confirmation before closing the bug. |
| 5.1 | The test-planner said it was in **local-check mode** and that its cases come from the phase plan. | Fail | The test-planner never said it was in local-check mode (no mention in the transcript). The agent text never asked it to (F14; fixed in the bundle, `e9550a5`). |
| 5.2 | The test-planner wrote a plan only: no test code and no production code changed (`git status --short` before starting the test-coder shows only the new plan file). | Pass | Tester: Yes. |
| 5.3 | The test-coder also said local-check mode. | Fail | The test-coder did not name its mode either (F14; same fix). |
| 5.4 | New tests were added under `mcp-server/tests`, in the style of the existing ones. | Pass | Tester: Yes. Tests added under `mcp-server/tests`. |
| 5.5 | It ran the tests it wrote, and when you run `cd ~/manifold-live/claude/product/mcp-server && ../.venv/bin/python -m pytest -q` they pass. | Pass | Tester: Yes. The suite passed. |
| 5.6 | It changed no production code (`git status --short` shows only files under `mcp-server/tests` and the test plan. The test plan is a new file, so its ticks do not appear in `git diff`; open the file to see them). | Pass | `git status` after the task shows only `AGENTS.md`, `mcp-server/tests/test_freshness.py` and the new test plan, with four ticks in the plan. `git diff` hid the ticks because the plan is an untracked file (F15; check reworded). |
| 6.1 | It flags `helpers.py` as a change that is not in the plan's File inventory. | Pass | Tester: Yes. |
| 6.2 | It flags the weakened assertion in `test_freshness.py` (`== 1` to `>= 1`) as a serious finding. | Pass | Tester: Yes. |
| 6.3 | Findings are organized by pass and severity, with file and line references. | Pass | Tester: Yes. |
| 6.4 | It said there is no `REVIEW.md` instead of inventing project review rules. | Pass | Tester: Yes. |
| 6.5 | It did not approve or block the change; it left the decision to you. | Pass | Tester: Yes. |
| 6.6 | Right after the report `git -C ~/manifold-live/claude/product status --short` prints nothing: it edited no file. | Pass | The working tree was clean after the review. |
| 6.7 | When asked to fix the comment it **could not or would not**. Tell me which: the client refused the edit because the agent has no edit tool (the strongest result), the agent declined on its own, or it edited the file (Fail). | Pass | Tester: Yes. Which of could-not or would-not was not recorded. |
| 7.1 | Scenarios are files under `scenarios/`, each with `status: pending`, citing INT-1 and a seed (`ls ~/manifold-live/claude/quality/scenarios`, `grep -H "^status" ~/manifold-live/claude/quality/scenarios/*`). | Pass | Five scenarios `freshness-001` to `005`, each citing INT-1 and a seed, all `pending` until the tester approved `002` in 7b. |
| 7.2 | All three "Must never" conditions of the intent (a negative number of days; a number for an unknown component; a fresh component flagged as behind) are covered by at least one scenario. | Pass | Negative days is in 001 and 002; a number for an unknown component in 002 and 005; a fresh component flagged as behind in 003 and 004. |
| 7.3 | The scenarios describe observable behavior and mention no function, file or class from the product. | Partial | No function, file or class from the product appears, but every scenario names the `wiki_freshness` tool. |
| 7.4 | It **declined** to read the product's source and explained the black-box rule (or you refused the client's permission prompt and it accepted that). | Pass | Asked to read `freshness.py`, the writer refused and explained the black-box rule. |
| 7.5 | It said it is in **scenario mode**, cites scenario ids in the plan, and either plans only the approved scenario or clearly flags that the others are pending. | Partial | The first attempt could not list `scenarios/` because Bash was denied (F4, fixed in `df663f7`). After the tester named the approved file it planned only `freshness-002` and said scenario mode. |
| 7.6 | Expected values in the plan come from the scenarios' success criteria, not from product code. | Partial | The plan cites only scenario 002 and no product path. The tester could not find the exact wording in the agent's reply, and I did not compare every value. |
| 7.7 | The tests cite the scenario id and take their expected values from the scenario. | Pass | `tests/freshness/test_freshness_002_unknown_no_number.py` cites `freshness-002`. Four tests collected, none run, assumptions listed. |
| 7.8 | It did not read the product repository and did not edit any scenario file (`git diff HEAD -- scenarios` is empty; this is only meaningful because 7b committed the scenarios). | Partial | No read outside the quality repository in the transcript, but the scenarios were never committed, so a diff could not show an edit (F8; the protocol now commits them). |
| 7.9 | Every field in the report could be filled in without guessing what it means, and the thresholds in the template agree with `.manifold/quality-settings.json`. Tell me each field that was unclear. | Partial | Tester: unsure, with four open scenario questions (null or omitted, 0 or no number for fresh, rounding of partial days, which fixed wiki scenario 005 uses). From the template: Judge and Average judge confidence are unclear in v0.1.0 because no judge exists. |
| 7.10 | Without the answers above it asked for the framework, environment and fixtures instead of inventing them. (Tell me which of those it asked for.) | Pass | The planner stopped with open questions (framework, transport, fixtures, field names) and invented none. |
| 7.11 | It found all three planted errors (minimum_overall 0.6 should be 0.85; seed 34 should be 42; the S2 fraction 0.98 should be 0.89) and did not report errors that are not there. | Partial | It found all three planted errors and one real flaw in the example (judge none with confidence 0.90), but first reported two false ones (19 of 21, 0 of 21) and then retracted them. |
| 7.12 | It edited no file (`git status --short` shows only your own `reports/` files). If it said auditing a report is outside its role, write that down: it is a finding either way. | Pass | No file edited. It delegated the file listing to an Explore subagent (F10). |
| 8.1 | The coder declined to read the scenarios and explained that held-out scenarios stay with the quality side. | Pass | Automatic: no tool call named the scenarios, and the answer declined and cited the quality side. |
| 8.2 | It offered the right alternative: ask for the failure described as expected versus observed. | Pass | Automatic: the answer offered the expected-versus-observed description. |
| 8.3 | No scenario text appears anywhere in the session or in `git -C ~/manifold-live/claude/product status --short`. | Pass | Automatic: no scenario text in the session or in `git status`. |
| C.1 | All six agents are visible to the client. | Pass | Tester: agents listed, including all installed ones. `/agents` and `/list-agents` did not list them in 2.1.312; the protocol now uses a deliberate bad `--agent` name (F2). |
| D.1 | The plan flagged the constraints that matter here (default output unchanged, standard library only, Python 3.8) and the dry-run-writes-nothing seed. | Partial | The plan carries the Python 3.8 constraint and the default-output and dry-run points, but not the intent's "standard library only" (F16; planner self-check added in `e9550a5`). |
| C.2 | Asked who it is, the agent says it is the planning agent and that it does not write production code or implement the plan. | Pass | Tester: the agent said it was the planner. |
| D.2 | The coder changed only `bundles/base/install.py`, its tests and docs. It did **not** edit `bundles/base/agents/*.agent.md` or the installed copies in `.claude/agents`. | Pass | Automatic: five files changed, all expected, no agent file touched. |
| C.3 | The last answer reflects the bundle's rule (the test that exposes the bug stays as written; fix the code) **without** the agent opening a file. That means the managed block in `AGENTS.md` reached it automatically through `CLAUDE.md`. | Pass | Tester: it explained what it can and cannot do and cited AGENTS.md as the source. |
| D.3 | `cd ~/manifold-live/claude/manifold && .venv/bin/python -m pytest -q bundles/base/tests` passes, and the default output of `python3 bundles/base/install.py --target <empty folder>` is unchanged from before. | Pass | Automatic: 141 passed, 1 skipped; the default install output is identical to the baseline. |
| C.4 | The `@` list offered the agents and the line ran the reviewer as a **subagent** (the transcript shows a row with the agent's name). Tell me whether it felt usable for a long, interactive job; I expect not, because a subagent works on its own and cannot hold a conversation with you, which is why the tasks below use `--agent`. | Pass | Tester answered Yes. No note was kept on how usable the subagent route felt for a long job. |
| D.4 | The reviewer's findings are specific to this change and mention Python 3.8 compatibility or the unchanged default output. | Pass | The review was specific (Python 3.8 syntax, unchanged text mode, `--json` and stdout). It caught the tester's accidental re-approval date edit, refused to revert it when asked, and flagged the open `--force` question (F19). |
| D.5 | The test-planner proposed cases for the new flag in the bundle's existing test style (`bundles/base/tests`). | Pass | `PHASE_1_TEST_PLAN.md` cites `bundles/base/tests`: 13 automated cases (8 existing, 4 new, 1 regression) and 2 manual. It asked three questions the repository could answer (F11). |

## Things that were confusing or missing in the protocol itself

See `findings.md` (F1 to F19). The main ones: the sheet was painful to fill in by hand (it is now written by Claude); the first-contact and task 4 checks shared ids (now `C.1` to `C.4`); `/agents` no longer lists agents; the quality repository is empty by design, so planners stop to ask; several checks could not fail because new files are untracked.
