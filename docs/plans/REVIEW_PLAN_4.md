# REVIEW_PLAN_4.md

**Phase:** `docs/plans/PHASE_4_PLAN.md`, checkpoint 1 only (Tasks 1 to 13, "Clear instructions in the pull request"). Checkpoints 2 to 6 are not part of this change and are not reported as missing.
**Intent:** INT-27, `intent/INT-27-clear-human-instructions-in-the-pr.md` (it has scenario seeds S1 to S7; there is no S8)
**Commit reviewed:** `9895935fd181510832d889c9353a3391266aea71` on branch `claude/phase-4-cp1` (pull request 35; base `claude/phase-4-plan` at `c6b059e92a8a5e4b725ec5f651e233b60b93ee86`; diff `c6b059e..9895935`, 6 commits, 28 files)
**Plan version:** `PHASE_4_PLAN.md` **Approved by:** Michael Hay on Nov 14, 2026; no amendment exists. Plan last commit on the branch: `9895935` (the coder's notes and the owner's answer to Open question 3 were added in this range).
**Policy used:** `REVIEW.md` (passes, Important and Nit meaning, nit cap of 5). The `Review process` approval rule in `AGENTS.md` (solo repository, owner Michael Hay, no second approver) applies: no second person is required, and the owner's approval is his own. GitHub's own Approve review is a separate act and is not something this file can show.
**Revision:** 1, 2026-11-14 11:30

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-14 11:30 | `9895935fd181510832d889c9353a3391266aea71` | First review |

## Counts by severity

| Severity | Open | Repaired |
|---|---|---|
| Important | 4 | 0 |
| Nit | 5 | 0 |

No nit was left out of this file (the cap is 5). Deferred and rejected findings are a human's decision and are counted in the pull request, not here.

## Findings

Order by pass, then by severity. Plan-conformance results that hold are listed after the findings, under "What was checked and holds".

### Bugs

**F1 (Important) — The CI confirmation is recorded two ways, and the human is told how to do only one of them**
- **Location:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md:49-54` (instructions and `Confirmed by` slug), `:75` (the tick box "CI of commit ... is green"), `:70` (remaining-steps instruction 2: "follow the Instructions under CI ... There is no second copy here"); `bundles/base/process/REVIEW_CYCLE.md:47` (the CI confirmation is "a tick in the pull request"), `:54` (the same confirmation is listed as a name-and-date field), `:66` (ready-check line 3: "ticked by a human"); `bundles/base/agents/coordinator.agent.md:57-58` (writes both the numbered shape with the slug and a line "for a human to tick").
- **Evidence:** read the lines above. The CI instructions (template lines 49-52) tell the person to write a name and date on `Confirmed by` and never mention the tick box at line 75; the remaining-steps instruction sends the person to those CI instructions, so a person who follows the text exactly writes a name and leaves the box unticked. The ready check and the single-home table in `REVIEW_CYCLE.md` require a tick. The review cycle therefore contradicts itself: the table says the confirmation is a tick, the slug section says it is a name and date. The coder lists "two CI confirmations in the template" as a deviation; this finding is my judgment on it. INT-27 S1's "Must never: leave a human step with no instructions" is the scenario at risk.
- **Direction:** decide whether the human act is the tick, the slug, or both. If both stay (the owner's own worked example in INT-27 has the `Confirmed by` line, and the ready check needs a tick), say so in one place: tell the person to tick the box and write the line, and make the single-home table and the slug section agree on which it is. If only one stays, drop the other. Add a test for whichever wording is chosen.
- **State:** open

**F2 (Important) — Agent and guide text still says "blank" for a field that now starts as a slug**
- **Location:** `bundles/base/agents/coordinator.agent.md:36` ("Amendment approved by blank"), `bundles/base/agents/planner.agent.md:76` ("Amendment approved by: left blank"), `bundles/base/agents/reviewer.agent.md:82` ("A blank Approved by is the right state of a new test plan"), `bundles/base/HOWTO.md:35-36` ("if it is blank"; "Write your name and the date on Approved by", no word about replacing the slug); lesser: `bundles/base/templates/INTENT_TEMPLATE.md:18` (the comment says to fill in `accepted_by`, not to replace the slug).
- **Evidence:** `grep -rnIE "accepted_by|[Bb]lank|Approved by" bundles/base` (run in this review) lists these lines; none was touched by the change. The new template and `REVIEW_CYCLE.md` say a slug is the starting state and counts as blank. A coordinator told to check that the amendment line is "blank" meets a non-blank slug; a planner told to leave it "blank" may delete the slug the template put there; a reviewer told a blank line is correct may report the slug as a finding. The plan's own Task 7 says the reviewer's sentence "now also names a slug", but no task changes that file and it is not in the file inventory.
- **Direction:** word these lines to match the rule in `REVIEW_CYCLE.md` ("blank or still holding a slug"), and add the HOWTO sentence "replace the whole slug". This is outside the current file inventory, so it needs the planner to add it to the plan (an amendment), not a silent edit.
- **State:** open

### Security

No finding. No credential, token, key or personal data was added in the diff (`git diff c6b059e..9895935` read; the only person names are the owner's in plan and branch-rules text that is not shipped, and the neutral placeholder `M. Kusanagi` in shipped text). `phase_status.py` stays read-only: it opens files for reading only, and it has no import beyond `re`, `sys` and `pathlib`.

### Compliance

**F3 (Important) — The coder's "Rule exceptions: none" does not match the guard log**
- **Location:** `.manifold/guard-log.jsonl` (2 lines, both rule `no-heredocs`, agent type `coder`, 2026-11-14T19:05:43Z and 19:06:27Z); the coder's report; `docs/process/BREACH_PROCEDURE.md` ("A breach is any command or edit that broke a rule ... whether the guard refused it or it went through").
- **Evidence:** the log has one refused command that began `grep -c "<Insert " ... ; python3 - <<` and one that began `git add docs/plans/PHASE_4_PLAN.md bundles/base/process/REVIEW_CYCLE.md bundles/...` (the rest is cut at 80 characters, so the heredoc inside it is inferred, not read). The task also mentioned a refused `cp`; that one is not in the guard log (a client-side permission check, not the guard), so I cannot compare it and I do not know what it copied. `docs/agents/claude-desktop-failures.md` holds no entry for 2026-11-14 or Phase 4. Nothing in the diff shows the refused commands took effect (staging and commits are explicit paths), so these were attempts, not completed breaches; the rule asks for them to be listed anyway.
- **Direction:** the coordinator records the two refusals (and the `cp`, once the owner says what it was) in `docs/agents/claude-desktop-failures.md` as disclosed or concealed per the procedure; the coder's line is corrected in the pull request.
- **State:** open

**F4 (Important) — The bare `<Insert ...>` slug may not be visible in GitHub's rendered description, and this is not settled**
- **Location:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md:54` and `:105`; plan Concerns 3, Task 1 note (c), CP1 Verification ("The owner reads the rendered template in a GitHub comment preview").
- **Evidence:** Task 1 found that GitHub's documentation does not say what happens to an unknown tag, and left it "unverified: confirm in a comment preview". Concerns 3 says that if it is hidden the slug goes in a code span and the owner decides at Task 1. No decision is recorded, the template ships the bare form, and no preview result is in the plan or the pull request. If GitHub hides the text, a reader sees an empty `Confirmed by:` line, which is the failure INT-27 S3 exists to remove. The script already accepts a slug in a code span (`phase_status.py:slugs`), so a fix would need no code change there; the test `test_pr_template_has_visible_instructions_and_one_slug_shape` would need its pattern check adjusted if backticks are added. I did not render the template (no preview was available to me).
- **Direction:** the owner previews the template in a comment (not posted) before the release; if the slugs are hidden, wrap them in code spans in the template and the tests in one repair task. Record the result in the plan. Until then this stays open.
- **State:** open

### Tests

**F5 (Nit) — `slugs()` finds a leftover slug only on a line that starts with the bare field label**
- **Location:** `bundles/base/scripts/phase_status.py:48-61` (`slugs`, `HUMAN_LABELS`).
- **Evidence:** run in this review against one-line inputs: `**Confirmed by:** <slug>`, `Confirmed by: <slug>`, `Approved by: \`<slug>\`` and `accepted_by: "<slug>"` are reported; `- **Confirmed by:** <slug>`, `> **Confirmed by:** <slug>`, `| **Confirmed by** | <slug> |` and `**Confirmed by** <slug>` (no colon) are not. The error is in the dangerous direction (an unreplaced slug is missed). The shipped template does not use those forms today, and the plan chose a label list on purpose (Task 11) so prose examples are not reported, so this is a Nit. Also, the label `accepted_by` can only match if an intent file is passed with `--pr-body`; the script never reads intent files, so a slug left in an intent's `accepted_by` is not listed by `/phase-status` (the coordinator text does say to treat it as missing).
- **Direction:** for the `--pr-body` input, consider counting every slug (the description is a generated page, not prose with examples), or strip a leading list, quote or table marker before reading the label; add a test for one such form. State in the command text that intent files are not read.
- **State:** open

**F6 (Nit) — Evidence gaps in the tests, and three judgments on the coder's choices**
- **Location:** `bundles/base/tests/test_phase_status.py:178-240`; `bundles/base/tests/test_bundle.py:2332-2430`; plan Task 11 note.
- **Evidence:** (a) Task 6 and Task 10 record a failing-first run; Task 11 records only "27 passed" for the five new phase-status tests, so I cannot reproduce a failing-first result (I did not run the new tests against the old script). The new tests check output for the new feature, so they would fail on the old code ("Unreplaced slugs" does not exist there), but that is inference. (b) The text tests (`test_blank_approval_text_counts_a_slug_as_blank`, `test_coordinator_never_fills_a_slug_and_treats_one_as_missing`) assert that phrases are present; that is the right kind of check for prompt text but does not show an agent behaves differently (see "no evidence yet" below). (c) Existing tests: no existing test was edited or weakened. One existing parametrized test (`test_bad_arguments_exit_2_without_a_traceback`) gained the case `["7", "--pr-body"]`; that is additive. The existing plan-template test (`test_bundle.py:1317`, needle "never fills in") was left as it was.
- **Judgments on the coder's listed deviations:** (1) The trailing comment kept on the **Amendment approved by** line (`PHASE_PLAN_TEMPLATE.md:130`) is acceptable: the visible **Instructions** line sits below it, so no instruction lives only in a comment (INT-27 S1 holds), and keeping it let the pinned test stand unedited. It does mean the template carries wording ("never fills in") chosen to satisfy an old assertion; the owner may prefer to move that wording into the visible line and edit the test with approval. (2) The intent-template test without PyYAML is acceptable: CI installs only pytest and skills-ref, and the test checks the shape that keeps the frontmatter parseable (a quoted string on the `accepted_by` line, with `---` still the first line). The plan's own acceptance command (PyYAML) was reported run once by the coder; I did not re-run it. (3) `.strip("* ")` in `phase_status.py` is acceptable: it is explained in the plan note (an existing test bans `.replace(` in the script) and it works for the template's `**Label:**` form; the limits are in F5. (4) Two CI confirmations: see F1.
- **Direction:** record a failing-first run for the new phase-status tests (run them against the version at `c6b059e`) in the plan note; nothing else to change.
- **State:** open

### Context files

**F7 (Nit) — The two command descriptions still show the old usage, and the Copilot prompt cannot pass the new option**
- **Location:** `bundles/base/commands/phase-status.md:2`, `bundles/base/commands/phase-status.prompt.md:3-9`, `.claude/commands/phase-status.md`.
- **Evidence:** `argument-hint` was changed to `<phase number> [--pr-body <file>]`, but `description` still says "Usage /phase-status <phase number>" and the body says it reads "the plan, test plan and review files". In the Copilot prompt the only input is `${input:phase}`; whether a person can type `4 --pr-body file` into it is unverified (confirm with the VS Code prompt-file documentation). No test covers either file's text for `--pr-body`.
- **Direction:** update the description and body sentence; check or state the Copilot limit.
- **State:** open

**F8 (Nit) — The Approve review step states the click path as fact and does not link it**
- **Location:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md:72`; `bundles/base/process/REVIEW_CYCLE.md:50`; INT-27 S5 ("links the Review changes place") and its Must never ("no claim about GitHub that was not read").
- **Evidence:** the step says to open the Files changed tab, click "Review changes", choose Approve and submit. The plan note for Task 1 records that what the "Review changes" control shows an author is "unverified", and the plan's Task 5 prescribed this wording, so it conforms to the plan. No claim about self-approval is made (the test forbids "own pull request", "self-approv" and "cannot approve"; none is present). The path itself was not read from GitHub's documentation in Task 1 (it is the usual interface, but not verified here), and there is no link. The step for "control missing or disabled" says "ask the owner", which in this solo repository is the person reading it; `BRANCH_RULES.md` records the owner's route (the repository's bypass) but the shipped, generic text cannot name it. This is allowed by the plan and the intent ("the answer comes from the owner's decision"), so it is a Nit.
- **Direction:** either read the click path from GitHub's documentation and cite it in the plan, or mark it as unverified in the template note; consider adding the link. The pull request this repository writes (not the shipped template) can carry the bypass route in its own text.
- **State:** open

**F9 (Nit) — Bookkeeping: an inaccurate commit message, an out-of-order task, and an unanswered question**
- **Location:** commit `dc9490b` ("Tasks 1-6 ... 5 passed (3 failed before the template change)"); `docs/plans/PHASE_4_PLAN.md` Task 13 note and Open question 6.
- **Evidence:** `dc9490b` changes only `REVIEW_CYCLE.md` and the plan (Tasks 1 and 2); the template and tests it describes arrive in `8cbe46f` five seconds later, so the first commit does not contain what its message says it verified. Task 13 (commit `4015eb6`) was done before Task 12; the note records this and Task 12 does not depend on it, so it is a recorded deviation. Open question 6 (how `/phase-status` reads the description) still has an empty `Answer:`; the coder built option (a), the plan's default, and the plan was approved with the default noted, so this follows the plan; but the owner has not written the answer.
- **Direction:** none needed for the history (do not rewrite it); the owner may write the answer to Open question 6 in the plan.
- **State:** open

## What was checked and holds

- **Both flavors from one source, generated files not hand-edited.** The agent, rule, template, process and command sources under `bundles/base/` changed; the installed copies under `.claude/` and `docs/` are the installer's output. Every installed file's SHA-256 matches `.manifold/manifest.json` (25 files, 0 mismatches, checked with a read-only script run). `cmp` of the five template and process pairs in `bundles/base/` against `docs/` prints nothing (PR template, plan, test-plan and intent templates, `REVIEW_CYCLE.md`); `.manifold/phase_status.py` equals `bundles/base/scripts/phase_status.py`. Two `build.py --out` runs gave zips that `cmp` equal.
- **The two PR template copies are identical** (`cmp`, no output).
- **Shipped text is generic.** `git diff -U0` on `bundles/base/` (added lines) holds no "Michael Hay", "mediumroast", "mihay42", "Megaroast", "Phase 4" or "INT-27" outside test docstrings; `build.py --check` (the forbidden-terms lint) prints `lint ok`.
- **Intent seeds.** S1: each tickable line, name field and table has visible **Instructions** (template lines 49, 68, 88, 100); caveat F1. S2: numbered runs, pass and fail steps, full hash kept, slug left. S3: both name fields hold one slug of one shape (the script found exactly 2 in the PR template, at lines 54 and 105); the plan, amendment, test-plan and intent lines carry the same shape. S4: State cells hold `missing`, the header no longer reads `met / missing`, both words are in the instructions. S5: a separate numbered step exists and nothing claims self-approval (caveat F8). S6: `/phase-status` lists slugs by field name, and a leftover slug counts as blank in the coder, test-coder and rule text and in `is_blank_approval` (caveats F2, F5). S7: the coordinator text forbids replacing a slug, writing a name or date, ticking, or writing "approved". "Must never" lines: no ready-check line was dropped or loosened (`REVIEW_CYCLE.md` ready check keeps its four lines; one sentence was added to line 4).
- **`phase_status.py`.** Read-only (no write call; the script opens files for reading only), standard library only (`re`, `sys`, `pathlib`), sorted output, identical on two runs (also pinned by a test), `from __future__ import annotations` keeps the `Path | None` hint valid on Python 3.10. A missing `--pr-body` file exits 2 with a message; a missing value exits 2. Run in this review: `phase_status.py 4` prints `Unreplaced slugs: 0` and says the description was not read; `phase_status.py 4 --pr-body docs/templates/PULL_REQUEST_TEMPLATE.md` lists exactly lines 54 (`Confirmed by`) and 105 (`Human confirmation`); `git status --short` was empty after the runs.
- **Scope.** All 28 changed files are in the plan's file inventory for CP1 (templates, process, agents, rule, script, commands, tests, `BRANCH_RULES.md`, the install refresh, the plan's own notes). Nothing under `server/`, `.github/` or `bundles/base/VERSION` changed. The `BRANCH_RULES.md` addition records each fact with its source or "unverified" (what `RepositoryRole` 5 means, the bypass effect, what "Review changes" shows an author are all marked unverified); the sentence "Pull request authors cannot approve their own pull requests" is recorded as read through a summarizing tool, which the text says plainly. I did not re-read GitHub's documentation or re-run the ruleset read.

## Rule exceptions compared

The coder's line was "none". Compared with: the commit log (6 commits, explicit staging, no `--no-verify`, no force push visible; commit messages carry the attribution line), the diff (no hand edit of a generated file: manifest hashes match; the install refresh in `4015eb6` was run by `install.py` as Task 13 prescribes, without `--force`), and `.manifold/guard-log.jsonl` (2 refusals, both `no-heredocs`, agent `coder`). The two refusals do not appear in the "none" line: see F3. The refused `cp` is not in the guard log and I could not compare it. The coder's transcript was not read. This reviewer's own run: three commands of mine were refused by the guard (one heredoc, one python snippet with a write-like call, and my attempt to write a scratch script outside `docs/plans/REVIEW_PLAN_<N>.md`); none took effect, and I did not work around them.

## Gates run

| Command | Counts | Result |
|---|---|---|
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |
| `.venv/bin/python -m pytest bundles/base/tests -q` | 2092 passed, 1 skipped, 19.15 s | pass (matches the coder's count) |
| `.venv/bin/python tools/vendor_web.py --check` | "vendored files match a fresh build" | pass |
| `.venv/bin/python bundles/base/scripts/phase_status.py 4` and `... 4 --pr-body docs/templates/PULL_REQUEST_TEMPLATE.md` | `Unreplaced slugs: 0`; then 2 listed | as expected |
| two runs of `python3 bundles/base/tools/build.py --out <scratchpad>/a` and `/b`, then `cmp` of the zips | equal | pass |
| `cd server && ../.venv/bin/python -m pytest -q` | not run | CP1 changes no server file; the plan's CP1 verification does not call for it |
| `.venv/bin/python -m pytest tests/live -q` | not run | CI does not run it and CP1 does not touch it |

## CI on the pushed commit

Not checked. I did not read the hosted runs for `9895935` (the coordinator reads them and a human ticks the pull request; a run for an older commit is not the result).

## Tests run and changed

No bug fix is in this change, so there is no failing-first requirement for a regression test. The coder recorded failing-first runs for Task 6 (3 failed, 2 passed before the template change; 5 passed after) and Task 10 (3 failed, 7 passed before Tasks 7 to 9); I did not reproduce the failing runs (that would need the earlier tree), only the final passing run above. No failing-first run is recorded for the five new phase-status tests (F6). Existing tests changed: none edited or weakened; one parametrized list gained a case (`test_phase_status.py`, `["7", "--pr-body"]`). The existing plan-template test is unedited. No behavior of agents was observed in real use for this change: for the text that prescribes agent behavior (coordinator CI shape, "never fill a slug", "a slug is blank") the status is **no evidence yet**; it needs a real coordinator run on a pull request.

## Could not check

- How GitHub renders `<Insert ...>` in a description (F4), and whether the "Review changes" control behaves as the template says for an author; I had no preview and did not re-read GitHub's documentation.
- The refused `cp` (not in the guard log) and the coder's transcript.
- The hosted CI result for `9895935`.
- The content of the 80-character-cut guard-log commands beyond their first characters.
- The failing-first runs recorded in the plan notes (not reproduced).
- Whether a first-time reader can act on the rendered template (the owner's CP1 verification step is still his to do).
- The ruleset and bypass facts in `BRANCH_RULES.md` (not re-read with `gh`).

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above.
