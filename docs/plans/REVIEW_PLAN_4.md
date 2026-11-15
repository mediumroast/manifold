# REVIEW_PLAN_4.md

**Phase:** `docs/plans/PHASE_4_PLAN.md`, checkpoint 1 only (Tasks 1 to 13, "Clear instructions in the pull request") and its owner-approved "Review amendment (round 1)" (Tasks 41 to 56). Checkpoints 2 to 6 are not part of this change and are not reported as missing.
**Intent:** INT-27, `intent/INT-27-clear-human-instructions-in-the-pr.md` (it has scenario seeds S1 to S7; there is no S8)
**Commit reviewed:** `1bf3836550ffd37ea0bae9f4aff3e33898327361` on branch `claude/phase-4-cp1` (pull request 35; base `claude/phase-4-plan` at `c6b059e92a8a5e4b725ec5f651e233b60b93ee86`; full change `c6b059e..1bf3836`, 36 files; repairs since revision 1 `3724f88..1bf3836`, 11 commits, 24 files). The head came from `git rev-parse HEAD` after `git log -3`.
**Plan version:** `PHASE_4_PLAN.md`; the plan is approved by Michael Hay on Nov 14, 2026, and the review amendment (round 1) is approved by him (`**Amendment approved by:** Michael Hay on Nov 14, 2026`, commit `da496ef`, the owner's edit). Task 55 is owner-gated (see F4) and was deliberately not run.
**Policy used:** `REVIEW.md` (passes, Important and Nit meaning, nit cap of 5 per report). The `Review process` approval rule in `AGENTS.md` (solo repository, owner Michael Hay, no second approver) applies: no second person is required, and the owner's approval is his own. GitHub's own Approve review is a separate act and is not something this file can show.
**Revision:** 4, 2026-11-15 14:55 (checkpoint 2 and its repair; the header fields above this line describe checkpoint 1 as of revision 2 and are kept as history; the checkpoint 2 header is the next block, then the revision 4 header)

**Checkpoint 2 header (revision 3).**
- **Phase:** `docs/plans/PHASE_4_PLAN.md`, checkpoint 2 only (Tasks 14 to 22, "Contract tests and hardening for the server"). Checkpoints 3 to 6 are not part of this change.
- **Intent:** INT-2, `intent/INT-2-test-hardening-and-contracts.md` (scenario seeds S1 to S4; the owner's inline answers to the three open questions are "survey the repository", and the plan did).
- **Commit reviewed:** `d3411a39c4def8d4fc660bc1788d9879600c9e32` on branch `claude/phase-4-cp2` (`git log` head; commits `84f42c7` and `d3411a3`; diff `origin/main..HEAD`, 44 files, 1988 insertions, 9 deletions; the one modified file is `docs/plans/PHASE_4_PLAN.md`, the other 43 are created).
- **Plan version:** `**Approved by:** Michael Hay on Nov 14, 2026` (`PHASE_4_PLAN.md:3`).
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo repository, owner Michael Hay, no second approver) applies, and nothing in this change needs a second person.

**Revision 4 header.**
- **Commit reviewed:** `9a28de75eead69b45f4de34a49bced3f3b9883ea` (`git log` head, "Phase 4 plan: the owner signs the round 2 (checkpoint 2) amendment"), branch `claude/phase-4-cp2`; diff `origin/main..HEAD` is 49 files, 2356 insertions, 14 deletions. Since revision 3 (`d3411a3`) the branch has 7 commits: `4e0776c` (REVIEW_PLAN_4 revision 3), `7a6982e` (the repair, 9 files), `961c7e1` (failure entry F21), `e02f595` (INT-2, INT-19 and Task 22 notes, Provenance line), `e8455bd` (failure entry F22), `9675d67` (the planner's format pass on the amendment), `9a28de7` (the owner's signature).
- **Plan version:** `PHASE_4_PLAN.md`, "Review amendment (round 2, checkpoint 2)", Tasks 57 to 62, `**Amendment approved by:** Michael Hay on Nov 15, 2026` (line 1014, commit `9a28de7`). The amendment was drafted by the coder, then put into the planner's format, and the repair ran before the signature; the owner accepted that after the fact (see "Process record").
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Intent:** INT-2 (S2 note) and INT-19 (note); INT-2 is `status: accepted`.

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-14 11:30 | `9895935fd181510832d889c9353a3391266aea71` | First review (checkpoint 1): F1 to F9 |
| 2 | 2026-11-14 12:12 | `1bf3836550ffd37ea0bae9f4aff3e33898327361` | Re-review of the repairs of the amendment (Tasks 41 to 56): State of F1 to F9 set from evidence; new findings F10 and F11 |
| 3 | 2026-11-15 14:40 | `d3411a39c4def8d4fc660bc1788d9879600c9e32` | First review of checkpoint 2 (Tasks 14 to 22): new findings F12 to F17; the checkpoint 1 findings are not re-reviewed and keep their revision 2 State |
| 4 | 2026-11-15 14:55 | `9a28de75eead69b45f4de34a49bced3f3b9883ea` | Re-review of checkpoint 2 and its repair (Tasks 57 to 62): F12 to F17 all repaired (evidence below); new findings F18 and F19 (nits, process record); the failure entries F21 and F22 checked against the guard log; CP1 findings F4, F9, F10, F11 not re-reviewed, state unchanged |

## Counts by severity

| Severity | Open | Repaired |
|---|---|---|
| Important | 1 (F4, owner-gated, checkpoint 1) | 4 (F1, F2, F3; F12 repaired in revision 4) |
| Nit | 5 (F9, F10, F11 from checkpoint 1; F18, F19 new in revision 4) | 9 (F5, F6, F7, F8; F13 to F17 repaired in revision 4) |

No finding is shown as deferred or rejected: that is a human's decision, recorded in the pull request, and none was recorded in anything I read. The nit cap (5) applies per review: revision 3 reported five new nits and left none out; revision 4 reports two new nits and left none out.

The sections headed "CP2: ..." further down are the revision 3 text, kept; their State lines for F12 to F17 are updated in place with the revision 4 evidence. Revision 4's own sections come first, under "CP2 revision 4".

## CP2 revision 4: repair, process record and gates

### Findings F12 to F17 (revision 3): repaired or open

All six are **repaired**. I ran each myself on 2026-11-15 on the head `9a28de7`; the detail is in each finding's State line below.

| Finding | Revision 4 State | Short evidence |
|---|---|---|
| F12 (Important) | repaired | `pytest tests/contracts -q`: `44 passed` on the real clock (the 15th; the recording is from the 14th); with the freeze switched off (inline `python -c`, no file written) the register recording fails again with the same `b505db1e...` etag as in revision 3, and the new test fails too |
| F13 | repaired | the self-test now runs every recording with `wiki_inventory_tool`'s answer renamed and asserts that exactly its recordings differ, each message naming the tool and `result.components` |
| F14 | repaired | `mask_product_versions` touches `bundles[].version` only; `test_only_the_product_version_fields_are_masked` passes; the `127.0.0.1` text is restored in the two helper recordings |
| F15 | repaired | `wiki_agent_catalog_tool.with_agents.json` exists; `-k wiki_agent_catalog_tool`: `2 passed` |
| F16 | repaired | `--runxfail` fails with the stated reason; the plain run is `6 passed, 5 xfailed` |
| F17 | repaired | the Task 62 note holds a CP2 Rule exceptions line (`none`) and a CP8 line; both are consistent with the guard log (see below) |

### The repair itself (commit `7a6982e`, 9 files)

What I read in full: `harness.py`, the diff of `cases.py`, `record.py`, `test_harness.py`, `test_write_failures.py`, the new recording, and the diff of the two re-recorded files. Nothing under `server/` other than `server/tests/` changed (`git diff 7a6982e~1 7a6982e --name-status`: 8 `M` or `A` in `server/tests/` and the plan), so no server code was changed.

- **The date freeze (`harness.py`, `_FrozenDate`, `FROZEN_DAY`, `run_case`).** `run_case` wraps the setup calls and the call under test in `mock.patch("wiki_backend.register.date", _FrozenDate)`; `register.py:5` imports `date` by name, so the patch takes effect, and `register.py:585` is the only use of `date` in that module. The frozen day is 2026-11-14, the day the recordings were made, so no recording changed. Cause and effect, run by me with an inline `python -c` (no file written): (a) with the freeze switched off, `1 failed` for the register recording with `got 'b505db1e...'`, the same etag that failed on the 15th in revision 3, and `3 failed, 41 passed` across `test_tool_contracts.py` and `test_harness.py` (the register recording, the F13 self-test, and the new day test); (b) with the frozen day set to 2031-05-05, `1 failed` with a different etag (`0b9428c3...`); (c) on the real clock, the 15th, with the freeze in place, the same case passes. So the etag follows the frozen day and nothing else, and today's date no longer matters. I could not do the coder's "moved day" run, because the guard refused my write of a scratch plugin (see Rule exceptions compared); the three runs above are the substitute. The other tools that call `date.today()` (`handoff.py`, `agent_guide.py`, `ingest.py`, `log.py`) are not frozen; the only recordings with a 64-character hash are `wiki_read_tool.ok`, `wiki_write_page_tool.create`, `.update`, `.stale_etag` and `wiki_register_component_tool.ok`, and the first four have no date in the page, so no other recording depends on the day. Dates in the other results are the `<date>` and `<timestamp>` tokens. A midnight rollover between two calls inside one case cannot matter for the register case (the freeze is constant).
- **`test_the_register_recording_does_not_depend_on_the_day`.** It patches `register.date` to 2031-05-05 and then calls `run_case`, which patches it again to the frozen day, so the day it "moves" to is replaced inside the call. It is still a real check (it fails when the freeze is removed: shown in (a)), but the coder's scratch-plugin evidence in the Task 57 note ("moving the registrar's day to 2026-11-13, 2031-05-05 and 2028-02-29 -> `41 passed` each") would show the same result for any day if the plugin patched the same name, since `run_case` overrides it. I cannot see the plugin (scratchpad), so I make no claim about it; the evidence I rely on is (a) to (c).
- **`mask_product_versions`.** Masks `bundles[].version` only, applied after `normalise`, on `wiki_bundle_info_tool`. `wiki_bundle_info_tool.ok.json` holds one version value (`"version": "<version>"`, line 14) and no other dotted number. A dotted number anywhere else is compared. It is keyed on the field name, so a second tool that returned a `bundles` list with a `version` would be masked too; no such tool exists today.
- **The `files` entry in `cases/record`.** `case(..., files=...)` and `harness._place_files` write the fictional files into the private copy of the Acme example and commit them with the test-local git identity; `record.py` writes the same `files` into the recording; `harness.py`'s module docstring documents the key. The Acme example in `examples/` is not changed (`git status --short` is empty and `git diff --name-status` shows nothing under `examples/`). The recording is loaded by the same path as the others (`run_case` reads `case.get("files", {})`).
- **The new `with_agents` recording.** Fictional data only: `acme-planner` and `acme-coder`, "the fictional Acme API", `make check`, `make test`. `grep -iE "mediumroast|mihay|michael|megaroast|/Users/|/private/|ghp_|sk-|secret|password|@"` over the recording and `cases.py` printed no personal or real data (the only hit is the `@etag:` argument marker in `cases.py:63`). The order of `agents_found` (`acme-planner`, `acme-coder`) comes from `agents_sorted` (`agent_guide.py:139`, stable sort by role order, roles differ), not from the folder order, so the recording does not depend on the file system. Test: `-k wiki_agent_catalog_tool` `2 passed`. 34 recordings now, 16 tools.
- **The two edited tests (F13, F16): the only existing tests edited.** F13: the body of `test_a_renamed_field_in_one_tool_leaves_the_other_recordings_alone` was rewritten, and `broken` is no longer there; it now renames `wiki_inventory_tool`'s answer through a wrapper on `world.call` for every recording and asserts that exactly the `wiki_inventory_tool.*` recordings fail, each message with the tool and `result.components`. I checked that no other case calls `wiki_inventory_tool` as a setup step or etag look-up (`grep` in `cases.py` and the recordings: only its own case; the ping recording names it in a list, not as a call). F16: `test_git_refusing_the_commit_is_reported_to_the_caller` keeps `xfail(strict=True)` and its reason, and now requires `result.get("committed") is False` or an `error`, `warning` or `message` text matching a "not committed" regex. Both edits are the findings themselves (each finding was about that test), the plan says so, and neither weakens a test that was working: F13's old version could not fail, and F16's is stricter. `pytest tests/test_write_failures.py --runxfail -q`: `5 failed, 6 passed`, each of the five for the stated reason (the fifth: `{'path': ..., 'status': 'created', 'etag': ..., 'error': None}`); plain run `6 passed, 5 xfailed`.
- **The two re-recorded recordings.** `git diff` of `wiki_export_helper_tool.ok.json` and `wiki_export_component_helpers_tool.ok.json`: one line each (the helper text), `<version>.1` back to `127.0.0.1` in two places inside that line; nothing else. The other 31 recordings of revision 3 are not in the commit's file list (`git diff --name-status`), so they are byte-identical.
- **Plan claims versus what I reproduced.** The plan's `1123 passed, 5 xfailed, 14 warnings`, `24 passed`, `2108 passed, 1 skipped`, `lint ok` and the vendored-files line all reproduce exactly (gates below). Task 59's acceptance ("exactly two changed existing recordings") holds; Task 60's holds; Task 61's holds; Task 57 and Task 58 commands pass; `phase_status.py 4` shows no unticked task in CP8 (CP8's six tasks are `[x]`).

### Process record

- **Order of events (from the commit log, local times of 2026-11-15, one author for all commits, so who wrote which text is not shown by git).** 06:09 `d3411a3`; 06:21 review revision 3; 06:30 `7a6982e` (the repair with the amendment section in the plan, signature still a slug); 06:31 F21; 06:32 `e02f595` (INT-2, INT-19, Task 22 note, Provenance line); 06:38 F22; 06:39 `9675d67` (Source and Acceptance lines, findings table, open questions, after-the-fact paragraph); 06:46 `9a28de7` (the signature). The repair therefore ran before the signature, as the plan's "After-the-fact review" paragraph and F22 both say. The text accepts this and the owner signed after reading; the plan says so in its own words, and the signature is a name and date as the template wants.
- **The signature commit (`9a28de7`).** 11 lines: the signature line, a `>` blank line and a two-space indent on the "Conclusion" line of the Task 14 note (so the conclusion belongs to the list item above it), and the findings-not-repaired table re-spaced (pipes aligned). Noted, not raised: these are the MarkText re-spacing the commit message names (one quote line and one table), the counts add up (6 insertions, 5 deletions), and they change layout only; the Task 14 note's words are unchanged.
- **Failure entry F22 (coordinator) against the log, the commits and the plan.** What I could check holds: the dates and times fit the commits (the repair at 06:30, the entry at 06:38, the format pass after it, the signature last); the plan holds the Provenance and "After-the-fact review" paragraphs the entry names; the entry's Remedy matches what the plan and the log show (the planner format pass, then the owner's signature). The guard log cannot show who wrote what, as the entry itself says, and the entry's own evidence is the session transcript and the coordinator's brief, which I cannot read: those parts are "not compared". The entry's statement that `e02f595` is "the planner's later Provenance paragraph" and that the planner reviewed Tasks 57 to 62 cannot be checked from git (one author). One statement is not consistent with the process text, see F18.
- **Failure entry F21 (coder) against `.manifold/guard-log.jsonl`.** The log has 8 lines as the task expected, before my own work; lines 7 and 8 are the entry's two refusals exactly: line 7 `2026-11-15T14:24:44Z`, rule `no-heredocs`, tool `Bash`, agent_type `coder`; line 8 `2026-11-15T14:27:19Z`, rule `protected-file`, tool `Bash`, agent_type `coder` (the log cuts the command at 80 characters, so "empty heredoc" and "`cut` of the guard log" come from the coder's disclosure, not from the log; the rule names fit). "6 lines before the repair and 8 after" matches: lines 1 to 6 are all 2026-11-14. Both refusals fall before the repair commit (14:24Z and 14:27Z are 06:24 and 06:27 local; the commit is 06:30). The coder's plan line (CP8) and the entry agree on both. Count (2 attempted, 2 refused, 0 through) matches. The entry's `cp` question is not in the log and not settled by me: the commit holds only the three intended recording files (two one-line changes and one new file), which fits the coder's statement that three recordings were copied back; what was copied in the scratchpad and whether `cp` into the repository counts under the rule is the owner's call, as the entry says.
- **Difference between the log and the two entries.** None for lines 1 to 8. The only difference is after: the log now has two more lines (9 and 10), written by me (two refused scratch-file writes by the reviewer at 14:50:10Z and 14:50:12Z, rule `write-allowlist`). The guard allows the reviewer to write only `docs/plans/REVIEW_PLAN_<N>.md`, while the environment names a scratchpad for temporary files; that conflict is the same one as in entry F19 of the failures file for round 1. I did not retry or work around it.
- **Guard exceptions.** `.manifold/guard-allow.json` does not exist, so no exception was granted and none used.
- **INT-2 "Status of S2" note, INT-19 note, Task 22 note.** Accurate where I checked: the package name and version `0.1.16`, "no option to send a header or token", "answers 401 to every unauthenticated `/mcp` request" and "run only for `--help`" all match the Task 14 note; "Phase 4 plan, Concern 6 and Open question 19" exist (`PHASE_4_PLAN.md:112` and `:758`, both about the server jobs not being required); Task 22 is `[~]` and `server.yml` is unchanged (`git diff origin/main..HEAD --stat -- .github` prints nothing); the INT-19 note and the Task 22 note point at INT-2 S2 and each other, and the unverified part ("whether the suite has sign-in scenarios") is marked "Unverified". Both notes are labelled "drafted for the owner's review". I did not re-run `npx` (network). The notes were added by an agent to INT-2, which is `status: accepted`; they are additive (nothing of the accepted text changed: `git diff e02f595~1 e02f595 -- intent/` shows only added lines) and the owner's signature on the plan is not a signature on them, so the owner's approval of that text is still his to give (rule (g)).
- **INT-2 "Release rule while open" placeholder.** `intent/INT-2-test-hardening-and-contracts.md:63` still holds `<Insert the owner's decision: whether a release may go out with this gap open, or S2's wording changes>`. Noted, not raised: it is the owner's to fill. It is not read by `phase_status.py` (intents are not read) and no gate fails on it.
- **Other consequence for the owner (not new).** The Completion checklist line "No [~] blocked items outstanding" (`PHASE_4_PLAN.md:706`) cannot be ticked while Task 22 stays `[~]`; `phase_status.py 4` also lists Task 55 `[~]`.

### New findings in revision 4

**F18 (Nit) — Failure entry F22 says the coder broke no rule of its own, but the review cycle names the coder**
- **Pass:** Compliance (consistency of the record with the process text).
- **Location:** `docs/agents/claude-desktop-failures.md:353` (F22, "Count": "The coder did not break a rule of its own: it was told to write the amendment.") and the entry's "Suggested change"; `docs/process/REVIEW_CYCLE.md:18` ("the `coder` does not start a repair checkpoint before a human has approved the amendment").
- **Evidence:** `REVIEW_CYCLE.md:18` puts the duty on the coder as well as on the coordinator, and the entry's suggested change ("the coder starts only after **Amendment approved by** is written") restates a rule that is already written. The coder did start a repair checkpoint (Tasks 57 to 62 are in `7a6982e`) while the line was still a slug. The entry says the coder followed a brief; that explains why it happened, and the coder reported everything, but it does not change what the process text says. Under `BREACH_PROCEDURE.md` a breach is counted per agent and per rule, so the count may be 1 for the coordinator and 1 for the coder (disclosed).
- **Direction:** append (do not rewrite) a line under F22 saying whether the owner counts a coder entry, and drop or reword the suggested change, since the rule exists and what is missing is a stop in the coder's own definition (a chat instruction does not replace the signature). I did not read the coder's definition for that stop; the owner or coordinator decides. The failures file is not edited by me.
- **State:** open

**F19 (Nit) — The signed amendment still says the slug is unsigned and that a chat instruction authorizes the repair**
- **Pass:** Bugs (consistency of the plan text).
- **Location:** `docs/plans/PHASE_4_PLAN.md:1019` ("The owner's chat instruction (2026-11-15: repair F12 and all five nits) authorizes this repair; the slug above is left for the owner's own name."); `:1021` ("Before signing, the owner reads: ..."); against `REVIEW_CYCLE.md:12-13` and `:18` (approval is the name and date on **Amendment approved by**, a human's, before the repair).
- **Evidence:** the line is signed (`:1014`, `Michael Hay on Nov 15, 2026`), so "the slug above is left for the owner's own name" is no longer true, and "authorizes this repair" asserts that a chat message does what the process text gives to the signature. The same section's "After-the-fact review" paragraph says the opposite (the repair ran ahead of the signature and the owner accepted it), so the section contradicts itself. A coder or reviewer reading the plan later could take the first sentence as a precedent. (The `Instructions` line at `:1015` is left after signing, as in round 1 at `:769`; that is the template's habit and I do not raise it.)
- **Direction:** the owner may reword the two sentences to say what happened (the owner instructed the repair in chat, the repair ran before the signature, the owner signed on Nov 15 after reading) and leave out "authorizes". It is the owner's text; the planner and the coder do not edit the signed line.
- **State:** open

### Tests, Security, Context files (revision 4)

- **Tests.** The tests for the repair are listed above. A bug fix is not in this change; F16's change is to a deferred-defect marker, not a fix. No existing test was edited other than the two named in the finding (F13 and F16); `git diff origin/main..HEAD --name-status` shows no `M` on a test file other than `test_harness.py` and `test_write_failures.py`, and both are new in this branch (they are `A` in `origin/main..HEAD`), so against the base nothing existing was edited. Real-use evidence for the contract workflow (a person changing a field and seeing only that tool fail): still **no evidence yet**.
- **Test plan check.** No `PHASE_<N>_TEST_PLAN.md` in this change.
- **Security.** `git diff 4e0776c..HEAD` read for credentials and personal data: none added. The notes in INT-2 and INT-19 and the plan carry no secret; the new recording is fictional.
- **Context files.** `AGENTS.md`, `CLAUDE.md` and `REVIEW.md` are not made out of date by the repair; INT-2 and INT-19 carry the new notes only.

### Rule exceptions compared (revision 4)

- **Coder, repair (plan CP8 line):** two refused commands (`no-heredocs`, `protected-file`), `cp -R` into the scratchpad, `cp` of three recordings into the repository, `git checkout` of two wrong recordings, nothing else. Compared with `.manifold/guard-log.jsonl` (8 lines when I started; 10 now): the two refusals match lines 7 and 8 in time (14:24:44Z, 14:27:19Z), rule, tool and agent type. The `cp`, `cp -R` and `git checkout` are not in the guard log (it logs refusals only); the commit holds only the three intended recordings besides the code and plan changes, so the repository side matches the line. Commit `7a6982e`: explicit file list, attribution line, no hook bypass visible.
- **Coder, CP2 line (Task 62 note, `none`):** matches the log (no CP2-time lines; the first line of 2026-11-15 is 14:24:44Z, during the repair).
- **Coordinator (F22):** compared above; matches the commits and the plan; transcript not compared; see F18 for the one inconsistency.
- **Mine:** I wrote this file, ran read-only `git` and `grep`, the project's gate commands, and three inline `python -c` runs that import the harness and call pytest (no file written, nothing in `/tmp`, the harness's temporary folders only). I tried twice to write a scratch plugin in the session scratchpad with `Write`; the guard refused both (rule `write-allowlist`, log lines 9 and 10), and I did not retry by another route. No other refusal.

### Gates run (revision 4, 2026-11-15, head `9a28de7`)

| Command | Counts | Result |
|---|---|---|
| `cd server && ../.venv/bin/python -m pytest -q` | `1123 passed, 5 xfailed, 14 warnings in 136.79s`; Python 3.11 | pass (revision 3: `1 failed, 1119 passed, 5 xfailed`) |
| `cd server && ../.venv/bin/python -m pytest tests/contracts -q` | `44 passed` | pass |
| `cd server && ../.venv/bin/python -m pytest tests/test_write_failures.py -q` | `6 passed, 5 xfailed` | pass |
| `cd server && ../.venv/bin/python -m pytest tests/test_write_failures.py --runxfail -q` | `5 failed, 6 passed` | as expected (the five strict xfails, each for its stated reason) |
| `cd server && ../.venv/bin/python -m pytest tests/contracts/test_tool_contracts.py -q -k wiki_agent_catalog_tool` | `2 passed, 33 deselected` | pass |
| `.venv/bin/python -m pytest tests/live -q` | `24 passed in 0.06s` | pass |
| `.venv/bin/python tools/vendor_web.py --check` | `vendored files match a fresh build` | pass |
| `.venv/bin/python -m pytest bundles/base/tests -q` | `2108 passed, 1 skipped in 18.34s` | pass |
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |
| `.venv/bin/python bundles/base/scripts/phase_status.py 4` | Approvals filled (lines 3, 768, 1014); `Unreplaced slugs: 0`; 18 unticked tasks (Tasks 23 to 40, later checkpoints); 2 blocked (Tasks 22 and 55); 7 unticked Completion lines; "Level: below mergeable"; no CP8 task open; it read this review file at revision 3 before I wrote revision 4 (8 open then) | as expected |

Python 3.11 only; CI also runs 3.12 and I did not (as in revision 3).

### Could not check (revision 4)

- The coordinator's brief and transcript (F22's evidence), and who wrote which text (git has one author).
- The coder's scratch plugin for the "moved day" runs, and my own plugin run (refused by the guard); I used inline runs instead.
- Python 3.12, a git config that signs commits, and hosted CI for `9a28de7` and the earlier commits (the coordinator reads them).
- The conformance package facts (needs network), `record.py --write` on a clean tree on a later day, and the owner's by-hand field-rename check.
- The `cp` question of F21 (the guard did not log it).

### A human decides (revision 4)

This review does not approve or block the change. A human approves, informed by the findings. Counts after revision 4: Important 1 open (F4, owner-gated, checkpoint 1); Nit 5 open (F9, F10, F11 from checkpoint 1; F18, F19 new); repaired since revision 3: F12 (Important) and F13 to F17 (Nit). The CP1 findings F4, F9, F10 and F11 were not re-reviewed and keep their revision 2 State.

## CP2: Checkpoint 2 findings (revision 3)

### Tests

**F12 (Important) — The recording of `wiki_register_component_tool.ok` pins a value that changes every day, so the test fails today**
- **Pass:** Tests (flaky or time-dependent test; INT-2 Constraints: "Flaky tests are not tolerated"); also Bugs.
- **Location:** `server/tests/contracts/wiki_register_component_tool.ok.json:19` (`"etag": "5998b7ee..."`); `server/wiki_backend/register.py:585` (`today = date.today().isoformat()`); `server/tests/contracts/harness.py:40-47` (`_VOLATILE` does not cover a 64-character hash).
- **Evidence:** `cd server && ../.venv/bin/python -m pytest -q` run in this review on 2026-11-15: `1 failed, 1119 passed, 5 xfailed, 8 warnings in 140.08s`; the one failure is `tests/contracts/test_tool_contracts.py::test_the_tool_still_matches_its_recording[wiki_register_component_tool.ok]`: `wiki_register_component_tool: result.etag: expected '5998b7ee...', got 'b505db1e...'`. The same single failure came in three more runs of `tests/contracts tests/test_import_rule.py tests/test_write_failures.py tests/test_http_errors.py` (`1 failed, 59 passed, 5 xfailed`), and in a run of that one case alone. The coder's note reports `1120 passed, 5 xfailed` on 2026-11-14. The etag is a hash of the page content, and `register.py:585` writes today's date into the new component page. I did not freeze the clock to prove it, so the cause is inferred from the code, from the pass on the 14th and the fail on the 15th, and from the other four recordings that hold an etag (`wiki_read_tool.ok`, `wiki_write_page_tool.create`, `.update`, `.stale_etag`) still passing: their content has no date.
- **Direction:** make the value stable (normalise the etag of a page that holds a date, leave the etag out of this recording, or fix the date the tool sees in the harness), then re-record by hand with `record.py --write` and review the diff, as the plan says. Then run the contract tests again on a later day or with the clock changed to show they hold. The server tests do not block a merge today (plan Concern 6), but this test will fail in every CI run from now on and it makes the "1120 passed" in the plan note untrue today.
- **State:** repaired (rev 4). `run_case` patches `wiki_backend.register.date` to 2026-11-14 (`harness.py`); `pytest tests/contracts -q` is `44 passed` and the full server run is `1123 passed, 5 xfailed` on the 15th. Cause shown by me (the revision 3 "inferred" is now shown): with the freeze off the case fails again with `b505db1e...`; with the frozen day set to 2031-05-05 it fails with another etag; so the etag follows the frozen day only. Details under "CP2 revision 4".

**F13 (Nit) — A harness self-test compares each recording with itself and proves nothing**
- **Pass:** Tests.
- **Location:** `server/tests/contracts/test_harness.py:36-41` (`test_a_renamed_field_in_one_tool_leaves_the_other_recordings_alone`).
- **Evidence:** the variable `broken` is built and never used; the loop calls `harness.compare(recording["tool"], recording["result"], copy.deepcopy(recording["result"]))`, which can only pass. The plan asked for a check that a rename in one tool involves no other tool's test (Task 19). The real check is the first test in the file, which does name the tool and field; this one adds nothing.
- **Direction:** either drop it, or make it test something: for example run `test_the_tool_still_matches_its_recording` logic for the other tools against the broken tool's rename and show only the one tool differs.
- **State:** repaired (rev 4). `test_harness.py` now runs every recording with `wiki_inventory_tool`'s answer renamed and asserts that exactly its recordings fail, naming the tool and `result.components`; `broken` is gone; passes. It fails when the freeze is off (it runs the register recording too), which is expected.

**F14 (Nit) — Normalisation hides any dotted three-number string in any result, so a changed number in prose is not caught**
- **Pass:** Tests (strength of the contract).
- **Location:** `server/tests/contracts/harness.py:43` (`\b\d+\.\d+\.\d+\b` becomes `<version>`).
- **Evidence:** the pattern is applied to every string of every result. It was added so that the bundle version in `wiki_bundle_info_tool` does not fail every release (Task 17 note), but it also masks, for example, a changed protocol or schema number written in a message. The same token covers the product's own releases URL on purpose.
- **Direction:** limit the replacement to the known version fields (for example under `bundles[].version`) if a wider mask is not wanted. The owner may leave it.
- **State:** repaired (rev 4). The global pattern is gone; `mask_product_versions` masks `bundles[].version` only; `test_only_the_product_version_fields_are_masked` passes; the two helper recordings changed by one line each (`127.0.0.1` restored, which the old pattern had hidden).

**F15 (Nit) — `wiki_agent_catalog_tool` has a contract for its "no agents" answer only**
- **Pass:** Tests / Compliance (INT-2 S1: "for every tool, a recorded request and response").
- **Location:** `server/tests/contracts/wiki_agent_catalog_tool.ok.json`; `cases.py` (the `wiki_agent_catalog_tool` case).
- **Evidence:** the recording holds `"status": "no_agents"` and the message, because `examples/acme` has no `raw/acme-api/agents/`. The coder said so in the Task 18 note. `test_every_registered_tool_has_a_contract` is satisfied by name, and it is (16 tools, 33 recordings, matches `tool_count: 16` in the ping recording), but the listing a caller gets when agents exist has no recording.
- **Direction:** a case with an agent file placed by a `setup` step (or a fixture added to the private copy) so the success shape is pinned; or record in the plan that this is a known gap.
- **State:** repaired (rev 4). `wiki_agent_catalog_tool.with_agents.json` (fictional `acme-planner` and `acme-coder`, placed by the case's `files` entry) pins `status`, `path`, `agents_found` and `sidebar_updated`; `-k wiki_agent_catalog_tool` gives `2 passed`; 34 recordings, 16 tools.

**F16 (Nit) — The fifth xfail asserts only that the word "commit" appears somewhere in the result**
- **Pass:** Tests.
- **Location:** `server/tests/test_write_failures.py:208-213` (`test_git_refusing_the_commit_is_reported_to_the_caller`: `assert "commit" in str(result).lower()`).
- **Evidence:** `--runxfail` shows it fails for the stated reason (the result is `{'path': ..., 'status': 'created', 'etag': ..., 'error': None}`, with nothing about git). Once a fixer adds a field, any field or message that happens to contain "commit" turns it green, and so the strict marker will pass for a fix that does not report the failure to the caller in a useful way.
- **Direction:** when `bug-coder` fixes it, assert the named field and the value (for example a `committed` flag false). Leave as it is until then.
- **State:** repaired (rev 4). The test now needs `committed` to be false or an error, warning or message text saying the change was not committed; `strict=True` and the reason are kept. `--runxfail` still fails for the stated reason; plain run `6 passed, 5 xfailed`.

### Compliance

**F17 (Nit) — The coder's "Rule exceptions" line for checkpoint 2 is not in the plan note or the commit messages**
- **Pass:** Compliance (AGENTS.md "Rule exceptions").
- **Location:** `PHASE_4_PLAN.md` CP2 notes (Tasks 14 to 22) and the two commit messages (`84f42c7`, `d3411a3`).
- **Evidence:** `git diff origin/main..HEAD -- docs/plans/PHASE_4_PLAN.md | grep -i "rule exceptions"` printed nothing, and the commit bodies do not carry the line. Your task text gives the coder's line as `none` (reported in the chat, which I cannot read). The comparison I could make is in "CP2: Rule exceptions compared" below, and it matches `none`.
- **Direction:** the coder writes the line into the CP2 note so it travels with the pull request, as it did for checkpoint 1 (`PHASE_4_PLAN.md:961`).
- **State:** repaired (rev 4). The Task 62 note (CP8) holds "Rule exceptions for checkpoint 2 (Tasks 14 to 22): none", naming the guard-log comparison, and a separate line for the repair; both agree with the guard log (see "Rule exceptions compared (revision 4)").

### Bugs, Security, Context files

No finding. Security: `git diff origin/main..HEAD` read for credentials and personal data: none added (see "CP2: What was checked and holds"). Context files: the change adds test files and plan notes only; `AGENTS.md`, `CLAUDE.md` and `REVIEW.md` are not made out of date.

## CP2: What was checked and holds

- **Every registered tool has a contract.** `test_every_registered_tool_has_a_contract` (`test_harness.py:44-48`) compares the set of `server.app.list_tools()` names with the set of `tool` fields of the recordings, both directions; it passes. 16 tools, 33 recordings (15 for the ten read tools, 18 for the write, handoff and component tools; all seven `TOOL_POLICY` handoff actions present: create, claim, request_review, confirm, reject, close, list). Failing-first run reported in the Task 19 note (one recording moved away, 1 failed) was not repeated by me.
- **A rename names the tool and the field.** `test_a_renamed_field_names_the_tool_and_the_field` passes; the message form is `wiki_read_tool: result.etag: expected str, got missing`. Pinned in both directions (a field present on one side only is a difference) and by type.
- **No real data in the recordings.** `grep -rIniE "mediumroast|mihay|michael|megaroast|/Users/|/private/|/var/|ghp_|sk-|secret|password|bearer"` on `server/tests/contracts/*.json` printed nothing real. I also searched for `token`, `https?://` and `@host` shapes: the only URL hits are `https://example.test/contract-new` (the fictional repo), `https://github.com/acme/acme-api` in a schema description and the word "http" inside the helper scripts' text; no token, no email address. Principal ids are `<principal-id>`, names are `contract`, dates and hashes are tokens, the releases URL is `<releases-url>`. Everything else comes from `examples/acme` or the product's own text (the two helper-script exports pin the product's whole helper source, 123 and 20 lines, which is intended but makes those two recordings change whenever a helper changes).
- **A recording change is never automatic.** `record.py` prints usage and writes nothing without `--write` (read), exits 2 when `CI` or `PYTEST_CURRENT_TEST` is set (read, and run by `test_nothing_regenerates_a_recording_during_a_test_run`, which passes), and no test module imports it (the same test scans for `contracts.record` and `import record`). `test_tool_contracts.py` only loads and compares. Not tested by me: a hand run of `record.py --write` (it writes into the repository; the coder's scratch-copy run is in the Task 16 note).
- **Only the entry module imports the framework.** `test_import_rule.py` (4 tests) scans `server.py`, `wiki_backend/`, `manifold_security/`, `manifold_cli/` (`ast.walk`, so imports inside a function count; absolute imports only), flags a module that imports `fastmcp`, `starlette`, `uvicorn` or `mcp`, holds `ENTRY_MODULES` to one member, and includes a self-check on a temporary file. `server/` has no other top-level module than `server.py`. The one-member check can be changed together with the set in one edit; that is what the plan prescribed, and the next reviewer sees the diff.
- **No network, no real git remote.** Contracts and write-failure tests run on a copy of `examples/acme` in `tmp_path` with a local `git init` and a local identity (`harness.make_acme_copy`), a temporary security store and `TestClient` (in-process). `test_offline_clean.py` still passes (full run). Not tested by me: behavior when the user's global git config signs commits (the copy uses `git commit -q` with only a local user).
- **Speed and flakiness (apart from F12).** The contract and new test files together: 8.7 to 10.1 seconds for 65 tests over three runs; the slowest case is 0.36 s. The same 59 passed and 5 xfailed each time. The 6 MiB bodies of `test_http_errors.py` are in memory, no sockets.
- **Defects not hidden.** `git diff origin/main..HEAD --name-status` shows nothing outside `docs/plans/PHASE_4_PLAN.md` modified and 43 files added: no file under `server/` other than `server/tests/` changed, so no code was changed to hide a defect. Task 20's five strict xfails each fail for the stated reason: `pytest tests/test_write_failures.py --runxfail -q` gave `5 failed, 6 passed`: (1) and (2) `stray folders: ['wiki/newarea']`; (3) `files changed: ['wiki/handoffs/acme-api-to-acme-web/feature-failure-case.md']` (page stays, no sidebar entry); (4) `files changed: ['wiki/_sidebar.md', 'wiki/handoffs/...feature-failure-case.md']` (page and sidebar entry stay, no log line); (5) the result is a plain `created` with `error: None` and no mention of the commit. All five are strict (`xfail(strict=True, reason="defect: ...")`), so a fix makes the run fail until the marker is removed.
- **The fifth is outside the plan's defect list, and the coder said so.** The Change text of Task 20 lists the stray folder, partial file, sidebar entry and log line; item 5 (git refusing the commit is not reported to the caller) is a different kind of defect. The Task 20 note says "Item 5 is outside the stray-folder/partial-file/sidebar/log list of the Change text ... flagged for the owner." That is flagged as asked. The owner's answer to Open question 10 covers defects found by these tests; whether a fifth kind falls under it is the owner's call.
- **Plan and note accuracy.** The counts in the Task 15, 16, 19, 20 and 21 notes that I could reproduce hold (Task 15: 4 tests; Task 20: `6 passed, 5 xfailed`; Task 21: 9 tests; contracts: 33 recordings, 7 harness tests, 1 count test, 41 in the folder). The CP2 gates note counts of `24 passed` (live), the vendored check, `2108 passed, 1 skipped` (bundle) and `lint ok` hold; the `1120 passed, 5 xfailed` server count does not hold today (F12).
- **Task 22 and INT-2 S2.** Not raised as a finding, as agreed. The notes are accurate where I checked them: the Task 14 note and the Task 22 note agree (the package has no bearer-token option; `server --help` lists `--url`, `--scenario`, `--suite`, `--expected-failures`, `-o/--output-dir`, `--spec-version`, `--verbose`), `.github/workflows/server.yml` is unchanged (`git diff origin/main..HEAD --stat -- .github` printed nothing), the Task 22 line is `[~]`, and the note says in words "INT-2 S2 (conformance run) stays an open gap". Nothing in the notes claims S2 done. I did not re-run `npx` (it needs network; not done) or read the package, so the package facts are the coder's statements. Two things for the owner to see next to the deferral: the Completion checklist line "No [~] blocked items outstanding" (`PHASE_4_PLAN.md:704`) cannot be ticked while Task 22 stays `[~]`, and INT-2 S2 says a conformance failure blocks the merge, which today no server job does (plan Concern 6). Both are the owner's to settle.
- **No existing test edited.** All 43 other files are new (`A` in `--name-status`); no existing test file appears with an `M`.
- **Tests for a bug fix.** Not applicable: no bug fix; the five xfails are the failing tests of deferred defects.
- **Test plan check.** No `PHASE_<N>_TEST_PLAN.md` in this change.
- **Held-out scenarios.** I did not read any.

## CP2: Rule exceptions compared

The coder's CP2 line (as given in the task, `none`; not recorded in the plan, see F17) compared with the diff, the commit log and `.manifold/guard-log.jsonl`: the guard log has 6 lines, all from 2026-11-14 (19:05:43Z to 20:05:49Z, checkpoint 1 work and its review), and none for 2026-11-15, so the guard refused nothing in CP2 and my own runs added no line (6 lines before and after). The diff holds only test files, recordings and plan notes; the two commits carry the attribution line, name no hook bypass, and the paths are explicit. The plan notes mention `env -u CI -u PYTEST_CURRENT_TEST ... record.py --write` (a run of a script that writes recordings, which the recorder permits by design) and a run of `record.py` copies in the scratchpad. Not compared: the coder's transcript, and anything the guard does not log (it logs refusals only).

My own: one write (this file); read-only `git`, `grep`, `cat`, and the project's test commands. No heredoc, no file written by a shell command, nothing in `/tmp`. I ran the xfail tests with `--runxfail` (read-only, writes only pytest's temporary folders).

## CP2: Gates run

| Command | Counts | Result |
|---|---|---|
| `cd server && ../.venv/bin/python -m pytest -q` | `1 failed, 1119 passed, 5 xfailed, 8 warnings in 140.08s`; Python 3.11.3 | **fail** (F12: `wiki_register_component_tool.ok`); the plan note says 1120 passed |
| `cd server && ../.venv/bin/python -m pytest tests/test_write_failures.py --runxfail -q` | `5 failed, 6 passed` | as expected: the five failures are the strict xfails, each for its stated reason |
| `cd server && ../.venv/bin/python -m pytest tests/contracts tests/test_import_rule.py tests/test_write_failures.py tests/test_http_errors.py -q` (3 runs) | each `1 failed, 59 passed, 5 xfailed`; 8.7 to 10.1 s | fail (F12) |
| `.venv/bin/python -m pytest tests/live -q` | `24 passed in 0.06s` | pass |
| `.venv/bin/python tools/vendor_web.py --check` | `vendored files match a fresh build` | pass |
| `.venv/bin/python -m pytest bundles/base/tests -q` | `2108 passed, 1 skipped in 22.32s` | pass |
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |

The server tests ran on Python 3.11.3 only; CI also runs 3.12 and I did not (no 3.12 interpreter with the project requirements here).

## CP2: CI on the pushed commit

Not checked: I did not read the hosted runs for `d3411a3` (the coordinator reads them). Given F12, `server tests (3.11)` and `server tests (3.12)` in `server.yml` can be expected to fail on this commit from 2026-11-15; this is an inference, not a reading.

## CP2: Tests run and changed

No existing test changed (see above). Failing-first evidence: Task 15 (`test_the_scan_flags_a_module_that_imports_the_framework`), Task 19 (a recording moved away, `1 failed, 39 passed`) and the Task 20 `--runxfail` runs are the coder's; I reproduced the Task 20 one. Real-use evidence for the contract workflow (a human changing a field and seeing exactly that tool fail, the `Verification` line of the CP2 section) is **no evidence yet**: the plan marks it as the owner's by-hand check, and the coder did not do it. The harness self-test does show the message form.

## CP2: Could not check

- Whether `record.py --write` on a clean tree reproduces the committed recordings byte for byte on a later day (it would not for F12); I did not run it because it writes into the repository.
- Python 3.12 (CI matrix) and a global git configuration that signs commits.
- Hosted CI for `d3411a3`.
- The conformance package facts (needs network; not run), and the owner's by-hand field-rename check.
- The coder's transcript and its chat-reported Rule exceptions line.

## CP2: A human decides

This review does not approve or block the change. A human approves, informed by the findings. Counts at revision 3 for checkpoint 2: Important 1 open (F12), Nit 5 open (F13 to F17).

---

# Checkpoint 1 record (revisions 1 and 2), kept as history

The sections below are the revision 2 text for checkpoint 1, unchanged. Their "Gates run", "Rule exceptions compared" and "Counts" describe checkpoint 1 only.

## Findings

Order by pass, then by severity. Plan-conformance results that hold are listed after the findings, under "What was checked and holds". Findings F1 to F9 keep their revision 1 text, shortened, with the new State and its evidence.

### Bugs

**F1 (Important) — The CI confirmation is recorded two ways, and the human is told how to do only one of them**
- **Location (revision 1):** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` CI instructions, `Confirmed by` line and tick box; `bundles/base/process/REVIEW_CYCLE.md` single-home table, slug section and ready check; `bundles/base/agents/coordinator.agent.md`.
- **Evidence in revision 2:** the template's CI **Instructions** step 2 (`PULL_REQUEST_TEMPLATE.md:51`) now says to write name and date on **Confirmed by**, replacing the whole slug, "and then tick the box ... under 'What remains for you'. Both acts are yours: the line and the tick."; step 3 (`:52`) says "do not write your name and do not tick"; the remaining-steps instruction 2 (`:70`) points to those instructions with "(two acts: the line and the tick)" and keeps "There is no second copy here". The heading "What remains for you" exists (`:65`). `REVIEW_CYCLE.md:47` (single-home row: "the **Confirmed by** line and the tick of the CI line"), `:54` (slug section names the line and says ticking is the second act, described in the template's CI instructions) and `:66` (ready-check line 3: "ticked by a human, with the **Confirmed by** line holding a name and date and no slug") agree. `coordinator.agent.md:57` says the human writes the line (replacing the whole slug) and then ticks, and the coordinator does neither. The test `test_ci_confirmation_is_the_line_and_the_tick_in_every_place` (`test_bundle.py`) passes (run in this review, with 17 other new tests: 18 passed); the plan note for Task 45 records 1 failed at `a68f92e` before the repair. Bundle and installed copies of the template and `REVIEW_CYCLE.md` are byte-equal (`cmp`).
- **State:** repaired (rev 2). The two acts are named in one place (the template's CI instructions) and the other places point to it, as the amendment prescribed.

**F2 (Important) — Agent and guide text still says "blank" for a field that now starts as a slug**
- **Evidence in revision 2:** `coordinator.agent.md:36` ("blank or still holding a slug (it is a human's to fill in)"); `planner.agent.md:54` and `:76` ("left as the template has it, blank or still holding a slug; you never delete or fill it"); `reviewer.agent.md:82` ("A blank **Approved by**, or one still holding a slug, is the right state of a new test plan"); `HOWTO.md:35-36` ("blank or still holds a slug"; "replace the whole slug"); `INTENT_TEMPLATE.md:18` ("replace the whole slug on `accepted_by`"). `grep -rnIiE "blank|accepted_by" bundles/base docs/templates docs/process` (markdown, tests excluded) shows no remaining "blank" wording for these fields that omits the slug; `coder.agent.md:24`, `test-coder.agent.md:33` and the rule file already said "blank or still holds a slug". The installed copies (`.claude/agents/*.md`, `docs/process/HOWTO.md`, `docs/templates/INTENT_TEMPLATE.md`) match the manifest. Test `test_agent_and_guide_text_counts_a_slug_as_blank` passes; Task 48 records 1 failed before.
- **State:** repaired (rev 2).

### Security

No finding. `git diff 3724f88..HEAD` and `c6b059e..HEAD` read: no credential, token, key or personal data added; the added lines of shipped files hold none of "Michael Hay", "mediumroast", "mihay42", "Megaroast", "Phase 4", "INT-27" (the `grep` printed nothing; the forbidden-terms lint prints `lint ok`). The new shipped URLs are GitHub's and Visual Studio Code's public documentation pages. `phase_status.py` still opens files for reading only and imports only `re`, `sys` and `pathlib` (plus `__future__`), and contains no `.replace(`.

### Compliance

**F3 (Important) — The coder's "Rule exceptions: none" does not match the guard log**
- **Evidence in revision 2:** `docs/agents/claude-desktop-failures.md` now holds F18 (the coder's two refused `no-heredocs` commands of Phase 4 checkpoint 1, 19:05:43Z and 19:06:27Z; says the coder's line did not list them, and that the `cp` is not in the guard log and what it copied is unknown), F19 (the reviewer's three refusals of round 1: `no-heredocs` 19:29:07Z and 19:30:20Z, `write-allowlist` 19:29:10Z), and F20 (the coder's one `no-heredocs` refusal at 20:05:49Z). I compared them with `.manifold/guard-log.jsonl` (6 lines): every line has an entry, with the same times, rule names and agent types, and the counts (2, 3, 1 attempted; 0 went through) match. The coder's new line in the plan (`PHASE_4_PLAN.md:961`, "Rule exceptions (Tasks 41 to 54 and 56; Task 55 not run)") lists the one refusal at 20:05:49Z, which matches the log (the log cuts the command at 80 characters, so the heredoc is inferred from the rule name and the coder's disclosure). F18 and F20 are closed and F19 is left open for the owner (the reviewer's read-only snippet question): those statuses are the coordinator's and owner's.
- **Residual:** the refused `cp` of round 1 remains unidentified (it was not in the guard log); the record says so plainly.
- **State:** repaired (rev 2) for everything the guard logged. See F11 for one item on the coder's new line.

**F4 (Important) — The bare `<Insert ...>` slug may not be visible in GitHub's rendered description, and this is not settled**
- **Location:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md:54` and `:105`; plan Concerns 3, Task 55 and Open question 3 (`PHASE_4_PLAN.md:976-977`).
- **Evidence in revision 2:** the template still ships the bare form and no code span; Task 55 is `[ ]` (not run) by design, because it waits for the owner's preview of the rendered template in a GitHub comment; Open question 3 has an empty `Answer:`. The owner has not yet reported whether GitHub renders the slug, so this is open and owner-gated, not a coder omission. The plan's default stands: Task 55 stays unrun and F4 stays open, and the release goes out with the risk. `phase_status.py` already reads a slug in a code span, and the amendment keeps Task 55 ready to run on a "hidden" answer. I did not render the template.
- **Direction (unchanged):** the owner previews the template in a comment (not posted) before the release and answers Open question 3; if the slug is hidden, Task 55 runs (code spans in the template, with the matching test change, and a re-install).
- **State:** still open (owner-gated).

### Tests

**F5 (Nit) — `slugs()` finds a leftover slug only on a line that starts with the bare field label**
- **Evidence in revision 2:** `phase_status.py` now has `MARKER_RE`, `LABEL_RE`, `human_label` and `slugs(lines, every=False)`. I ran it (a read-only `python -I -c` import, no file written) on one-line inputs: `- **Confirmed by:** <slug>`, `> **Confirmed by:** <slug>`, `| **Confirmed by** | <slug> |`, `**Confirmed by** <slug>` (no colon), `1. Approved by: <slug>`, a code span, and `accepted_by: "<slug>"` are all reported under the right label; a task line starting `Change:` is not reported by default, and is reported under "(description)" with `every=True`. The `--pr-body` path calls `slugs(..., every=True)`, so any slug anywhere in the description counts. Run on `docs/templates/PULL_REQUEST_TEMPLATE.md` it lists exactly lines 54 and 105. It is read-only, standard library only, and has no `.replace(` (the `grep` printed nothing). The command text now says intent files are not read (see F7). The new tests pass (3 test functions, 12 cases).
- **State:** repaired (rev 2). One side effect is F10.

**F6 (Nit) — Evidence gaps in the tests, and three judgments on the coder's choices**
- **Evidence in revision 2:** (a) Task 41's note records the failing-first run: a detached worktree at `c6b059e` with the five new tests copied in gave **5 failed, 21 passed**, then the worktree was removed (`git worktree list` no longer shows it; `git status --short` is empty here). Later tasks (45, 48, 50, 52, 54) each record their failing-first count (1, 1, 6 across the new slug cases, 2, 1). I did not re-run these against the old trees. (b) Prompt-text tests still check that phrases are present, not that an agent behaves differently: see "Tests run and changed" (no evidence yet). (c) No existing test was edited or weakened: `git diff c6b059e..HEAD -- bundles/base/tests` removes one line only, the `@pytest.mark.parametrize` list of `test_bad_arguments_exit_2_without_a_traceback`, which gained the case `["7", "--pr-body"]` (additive). The three judgments of revision 1 (kept trailing comment on the amendment line, intent-template test without PyYAML, `.strip("* ")`) stand; the `.strip("* ")` has since been replaced by `human_label`.
- **State:** repaired (rev 2) for the failing-first record. The "no evidence yet" status for agent behavior is a standing report, not a finding.

### Context files

**F7 (Nit) — The two command descriptions still show the old usage, and the Copilot prompt cannot pass the new option**
- **Evidence in revision 2:** `bundles/base/commands/phase-status.md:2` and `phase-status.prompt.md:3` have `description` "... Usage /phase-status <phase number> [--pr-body <file>]"; the body sentences name the pull request description with `--pr-body <file>` and say intent files are not read (`phase-status.md:6`, `phase-status.prompt.md:10`). The Copilot `Limit:` paragraph says whether `${input:phase}` can carry `4 --pr-body <file>` is "unverified" and names the VS Code prompt-file documentation URL as the source to confirm with, with the fallback "run the script by hand". Test `test_command_files_describe_pr_body_and_the_intent_limit` (2 cases) passes; Task 52 records 2 failed before. `.claude/commands/phase-status.md` equals the bundle source (`cmp`). I did not re-read the VS Code page, so what the note says that page contains is the coder's statement, not mine.
- **State:** repaired (rev 2).

**F8 (Nit) — The Approve review step states the click path as fact and does not link it**
- **Evidence in revision 2:** `PULL_REQUEST_TEMPLATE.md:72` and `REVIEW_CYCLE.md:50` now carry the link to GitHub's documentation page on reviewing proposed changes. The Task 53 note says the page was read with a summarizing tool (so its words, not a raw read) and that it confirmed Files changed, "Review changes", Approve, "Submit review"; it states that what the control shows to an author is not claimed. I did not re-read the page. The template makes no self-approval claim (the test `test_approve_review_step_is_linked_or_marked_unverified` forbids it and passes; Task 54 records 1 failed before), and the shipped files carry no repository, owner or bypass text (the `grep` for "bypass", "Michael", "mediumroast" in shipped added lines printed nothing; the two hits the note mentions are in the test's own words). "Ask the owner" for a missing or disabled control remains generic by design.
- **State:** repaired (rev 2). The link lets a reader check the path; the click path itself rests on a summarized read, as the note says.

**F9 (Nit) — Bookkeeping: an inaccurate commit message, an out-of-order task, and an unanswered question**
- **Evidence in revision 2:** unchanged and not part of the repairs (no repair was asked; history is not rewritten). Open question 6 of the plan still has no written answer (the default, option a, was built). The amendment's open question 4 repeats this for the owner (`PHASE_4_PLAN.md:978`).
- **State:** still open (nothing to repair; the owner may write the answer, or record it as deferred or rejected in the pull request).

### New findings in revision 2

**F10 (Nit) — A prose line that starts with a field's words is reported as an unreplaced slug**
- **Pass:** Tests (a false positive in a tool the person relies on).
- **Location:** `bundles/base/scripts/phase_status.py:33-35` (`LABEL_RE` accepts a space after the label) and `:51-61` (`human_label`, `slugs`).
- **Evidence:** run in this review (read-only import): the lines `Approved by the owner: <slug>` and `Approved by is a field; e.g. <slug>` are both reported under `Approved by` in the default (plan) mode. The error is in the safe direction (an extra report, never a missed slug). The plan files in this repository report `0`, so nothing is wrong today. Task 49 chose to accept a space after the label so that the no-colon form `**Confirmed by** <slug>` is found, and this is the cost.
- **Direction:** none needed now; if a plan or review ever quotes a slug in a sentence that begins with a field name, either reword it or require the label to be followed by a colon, a border or the end of the label (not a word). The owner may leave it.
- **State:** open

**F11 (Nit) — The coder removed two scratchpad folders it did not create in that run, with `rm -rf`**
- **Pass:** Compliance (the AGENTS.md rule "User edits": prefer archiving over deleting; confirm before deleting what the user may have modified).
- **Location:** `PHASE_4_PLAN.md:961` (the coder's Rule exceptions line: "I removed the two scratchpad folders `dist` and `x` (not created in this run) with `rm -rf`; both were in the session scratchpad"); `docs/agents/claude-desktop-failures.md` F20 (the coordinator judged it not a guard-rule breach on this evidence and says the folders' origin is not known).
- **Evidence:** the line is the coder's own, disclosed, and it is not in the guard log (the guard logs refusals only), so I cannot compare it with anything. The folders were in the session scratchpad, not in the repository, and `git status --short` is empty, so the repository is untouched. Whether the folders held anything another run wanted is unknown to me.
- **Direction:** the coder should not delete a folder it did not create in its run without saying whose it was; here it did say so. Nothing to repair in the repository. The owner may note it with F20.
- **State:** open

## What was checked and holds

- **Both flavors from one source, generated files not hand-edited (Task 56).** Every installed file listed in `.manifold/manifest.json` that exists has the recorded SHA-256 (25 files, 0 mismatches, a read-only `python -I -c` run). `cmp` printed nothing for the bundle-against-installed pairs: `PULL_REQUEST_TEMPLATE.md`, `INTENT_TEMPLATE.md`, `REVIEW_CYCLE.md`, `HOWTO.md` (against `docs/process/HOWTO.md`), `scripts/phase_status.py` (against `.manifold/phase_status.py`) and `commands/phase-status.md` (against `.claude/commands/phase-status.md`). The plan note for Task 56 records `install.py` run from a fresh build without `--force` (10 installed files); I did not re-run the installer. Task 55 is correctly not in this refresh.
- **Shipped text is generic** (see Security): no owner, repository, bypass or phase wording in shipped files; `build.py --check` prints `lint ok`.
- **Intent seeds and Must never lines.** S1: every tickable line, name field and table has visible **Instructions**, and the two CI acts are now said (F1). S2: numbered runs and the full hash are kept. S3: both name fields in the PR template hold one slug of one shape (the script found 2: lines 54 and 105). S4: State cells and instructions unchanged from revision 1. S5: the Approve step is separate, linked, and claims nothing about self-approval (F8). S6: `/phase-status 4 --pr-body docs/templates/PULL_REQUEST_TEMPLATE.md` lists the two slugs by field name; a slug counts as blank in coordinator, planner, reviewer, coder, test-coder, rule text, HOWTO and the intent template (F2). S7: the coordinator text forbids replacing a slug, writing a name or date, ticking, or writing "approved". No ready-check line was dropped or loosened: the four lines are kept, line 3 was tightened (a name and date, no slug).
- **Scope.** The 24 files changed since revision 1 are all in the amendment's inventory (the amendment lists the added agent, HOWTO, intent-template, command and test files as MODIFY, with installed copies refreshed by Task 56). Nothing under `server/`, `.github/` or `bundles/base/VERSION` changed since revision 1 (`git diff --stat 3724f88..HEAD -- server .github bundles/base/VERSION` prints nothing).
- **Tests.** No existing test was edited or weakened (see F6). The changed `phase-status` script keeps the existing ban on `.replace(` satisfied.

## Rule exceptions compared

The coder's CP7 line (`PHASE_4_PLAN.md:961`) says: one `no-heredocs` refusal (a `python` call with a heredoc while checking the Task 48 test, nothing written), one plan-note edit that did not apply and was corrected in a later commit (not a rule matter), `rm -rf` of two scratchpad folders (F11), nothing else refused. Compared with `.manifold/guard-log.jsonl` (6 lines now): the one new coder line, `no-heredocs` at 2026-11-14T20:05:49Z, matches the refusal in the coder's line; there is no other new coder line. The guard log holds the revision 1 lines already recorded: coder 19:05:43Z and 19:06:27Z, reviewer 19:29:07Z, 19:29:10Z and 19:30:20Z; all five are in `claude-desktop-failures.md` F18 and F19. Commit log (11 commits since revision 1): explicit staging in the messages I could read, no `--no-verify`, no force push visible, attribution lines present on commits I read; the commit `bc5a674` message says it holds Tasks 53 and 54 and the plan note was added in `02fc745`, and the message of `02fc745` says so. The coordinator's record (F18 to F20) matches the guard log in time, rule, agent and count. Not compared: the refused `cp` (not in the guard log), the coder's transcript, and the `rm -rf` of F11 (the guard does not log it).

My own run: no command of mine was refused by the guard in this revision (the guard log was 6 lines before and after my runs). My one write is this file. I ran two read-only `python -I -c` imports (no heredoc, no file written), `git`, `grep`, `cmp` and the project's verify and test commands.

## Gates run

| Command | Counts | Result |
|---|---|---|
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |
| `.venv/bin/python -m pytest bundles/base/tests -q` | 2108 passed, 1 skipped, 18.41 s | pass (revision 1: 2092 passed, 1 skipped; the 16 added tests are the CP7 tests) |
| `.venv/bin/python -m pytest bundles/base/tests -q -k "ci_confirmation or agent_and_guide or approve_review or command_files or slugs_are_found or pr_body_reports or prose_slug"` | 18 passed, 2091 deselected | pass |
| `.venv/bin/python tools/vendor_web.py --check` | "vendored files match a fresh build" | pass |
| `.venv/bin/python bundles/base/scripts/phase_status.py 4 --pr-body docs/templates/PULL_REQUEST_TEMPLATE.md` | `Unreplaced slugs: 2` (lines 54 `Confirmed by` and 105 `Human confirmation`); 28 unticked tasks; 7 unticked Completion checklist lines; "Level: below mergeable" | as expected; it also read the review file at revision 1 (9 open) before I wrote this revision |
| `cd server && ../.venv/bin/python -m pytest -q` | not run | CP1 and its amendment change no server file |
| `.venv/bin/python -m pytest tests/live -q` | not run | CI does not run it and the change does not touch it |
| The intent-template acceptance command with PyYAML | not run | the coder reported it once; I did not repeat it |

## CI on the pushed commit

Not checked. I did not read the hosted runs for `1bf3836` (the coordinator reads them and a human ticks the pull request; a run for an older commit is not the result). This is the head named above; every new commit needs its own read and tick.

## Tests run and changed

No bug fix is in this change, so there is no failing-first requirement for a regression test; the amendment still recorded failing-first counts for each new test (see F6), which I did not reproduce against the old trees. Existing tests changed: none edited or weakened; one parametrized list gained a case. For the text that prescribes agent behavior (the coordinator's two-acts CI shape, "never fill a slug", "a slug is blank") the status remains **no evidence yet**: it needs a real coordinator and reviewer run on a pull request that uses the new template; this repository's own pull request 35 is the first place that could show it. The test plan check does not apply (no `PHASE_<N>_TEST_PLAN.md` in this change).

## Could not check

- How GitHub renders `<Insert ...>` in a description (F4, owner-gated), and whether the "Review changes" control behaves as the template says for an author; I had no preview and did not re-read GitHub's or VS Code's documentation.
- The refused `cp` (not in the guard log), the coder's transcript, and what was in the two scratchpad folders that were deleted (F11).
- The hosted CI result for `1bf3836`.
- The command text cut at 80 characters in the guard log beyond its first characters.
- The failing-first runs recorded in the plan notes (not reproduced), and the installer run of Task 56 (only its results were checked: hashes and `cmp`).
- Whether a first-time reader can act on the rendered template (the owner's verification step is still his to do).
- The ruleset and bypass facts in `BRANCH_RULES.md` (not re-read with `gh`; the file has not changed in the repairs).

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above. Counts at revision 2: Important 1 open (F4, owner-gated) and 3 repaired; Nit 3 open (F9, F10, F11) and 4 repaired.
