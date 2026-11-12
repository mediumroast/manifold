# REVIEW_PLAN_3.md

**Phase:** `docs/plans/PHASE_3_PLAN.md`, checkpoints CP1 (Tasks 1 to 6, revisions 1 and 2), the repair of round 1 (Tasks 19 to 21, revision 2) and CP2 (Tasks 7 to 10, revision 3)
**Intent:** INT-26, `intent/INT-26-finishing-a-phase-clear-and-light.md`
**Commit reviewed:** `aabccb3e4949de4de5cdaeedcff03cfd9212451d` (Task 6; with `996bcbd0774b7fdf4f902d95b1b006417e5a7461`, Tasks 1 to 5; diff `3e2bbaf..aabccb3`), branch `claude/intent-phase3-streamline`. The checkout's HEAD is the merge `7a79d22d2c87e2b683e81516ce0893f3091bcac6` (context only; it brings in #32, not reviewed). The working tree also holds one uncommitted edit to `docs/plans/PHASE_3_PLAN.md`: the "Rule exceptions:" line in the CP1 notes (line 146). That line is not in the commit reviewed.
**Plan version:** **Approved by:** Michael Hay on November 11, 2026; no amendment. Plan file has the uncommitted edit named above.
**Policy used:** `REVIEW.md` (repository root, present) plus the built-in defaults and the documents/agent-instructions standard. The `Review process` approval rule of `AGENTS.md` (solo repository, no second approver) applies; this change touches nothing that section says needs a second approver.
**Revision:** 3, 2026-11-11 (time not recorded by the reviewer). Revision 3 reviews CP2, commit `30e88bd7f5d32fcd03c001fc1635dbca75c5611e` (parent `cdc0362`; diff of that commit only: 6 files, 97 insertions, 9 deletions). Branch `claude/intent-phase3-streamline`; the working tree was clean and HEAD equals the commit at the start of this review. The plan is approved (Michael Hay, November 11, 2026) and the owner has settled: Task 8 follows option A; the coder's wording of ready-check item 2 (ending ": repaired, deferred or rejected", kept so an existing test is not edited) is approved; no test edit. Policy and approval rule are as above (`REVIEW.md` plus built-in defaults; solo repository, no second approver; approval rule applies as stated there, nothing in this change needs a second approver). Revision 2 re-reviews the repair checkpoint `eea54246c0c3bc957387e9215d881018f940dc7f` (parent `e68312f`; Tasks 19 to 21 of "Review amendment (round 1)", approved by Michael Hay on November 11, 2026). The sections below that describe revisions 1 and 2 (header lines above, "Checks that found nothing", "Rule exceptions compared" for CP1) are kept as written; revision 2 additions are marked "Rev 2" and revision 3 additions "Rev 3". Finding IDs F1 to F4 are unchanged; CP2 findings continue at F5.

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-11 | `aabccb3e4949de4de5cdaeedcff03cfd9212451d` | First review, CP1 only |
| 2 | 2026-11-11 | `eea54246c0c3bc957387e9215d881018f940dc7f` | Re-review of the repair (Tasks 19 to 21): F1 and F3 repaired, F2 repaired as accepted (evidence recorded, not reproduced by the reviewer); one new Nit (F4) |
| 3 | 2026-11-11 | `30e88bd7f5d32fcd03c001fc1635dbca75c5611e` | Review of CP2 (Tasks 7 to 10): F4 repaired; two new Important (F5, F6) and four new Nits (F7 to F10) |
| 4 | 2026-11-12 (time not recorded by the reviewer) | `db37ef69180caa46713ff7523f7e5a5b13e0f4e4` (CP3, Tasks 11 to 14); round 2 repair `815baa3d2359268bf031cb147227ebc14d4d2eac` (Tasks 22 to 26) re-checked | F5, F6, F7 repaired; F8, F9, F10 not reopened (owner deferred them; the decision lives in the pull request); one new Important (F11) and two new Nits (F12, F13) |
| 5 | 2026-11-12 (time not recorded by the reviewer) | `1ccf6aec9d3bda8649e401a42e09fc90dbaee913` (CP7, Tasks 27 to 30; diff of that commit only: 5 files, 52 insertions, 13 deletions) | F11 and F13 repaired with evidence; F12, F8, F9, F10 not reopened; one new Nit (F14); no Important open |
| 6 | 2026-11-12 (time not recorded by the reviewer) | `6716af3f257ca1dbeae91c3bf498cab96ec17927` (Task 18, the final commit of the branch), on `07d580d` (CP4, Tasks 15 to 17); the whole branch against `origin/main` checked against the plan and INT-26 | F8 repaired with evidence; F9, F10, F12 not reopened (owner-deferred); four new Nits (F15 to F18); no Important open |

Revision 6 header: reviews CP4 (diff of `07d580d~1..6716af3`: 24 files, 959 insertions, 54 deletions) and, as the review of the final commit, the whole branch. Branch `claude/intent-phase3-streamline`; the working tree was clean and HEAD equals `6716af3`. Plan approved (Michael Hay, November 11, 2026) with three amendments approved. Policy used: `REVIEW.md` plus the built-in defaults and the documents standard (the change also holds code: a script, `build.py` and tests). The `Review process` approval rule (solo repository, no second approver) applies as stated there; nothing in this change needs a second approver. Brief: F9, F10, F12, F14's decision and the other owner deferrals are not reopened; CI was not read.

Revision 4 header: reviews CP3, commit `db37ef6` (parent `815baa3`; diff of that commit only: 6 files, 137 insertions, 8 deletions), branch `claude/intent-phase3-streamline`; the working tree was clean and HEAD equals the commit. Plan approved (Michael Hay, November 11, 2026) with the round 2 amendment approved. Policy used: `REVIEW.md` plus the built-in defaults and the documents standard. The `Review process` approval rule (solo repository, no second approver) applies as stated there; nothing in this change needs a second approver. Per the owner's brief, the acceptance of `docs/process/BRANCH_RULES.md` and of the docs-only CI finding is not treated as a finding. Per this revision, the reviewer's state vocabulary is `open` or `repaired`; "deferred" for F8 to F10 is the owner's decision in the pull request, so they still show `open` here.

## Counts by severity

| Severity | Open | Repaired |
|---|---|---|
| Important | 0 | 4 (F1, F5, F6, F11) |
| Nit | 8 (F9, F10: deferred by the owner in the pull request, kept open here; F12 settled by the owner, still `open` here; F14, F15, F16, F17, F18 open) | 6 (F2, F3, F4, F7, F8, F13) |

Rev 6 replaces this table (rev 5: 5 Nit open, 5 repaired). F8 moved to repaired; four new Nits.

Deferred and rejected counts are the owner's, in the pull request. The counts above are those of rev 5 and replace the rev 4 table (rev 4: 1 Important open, 5 Nit open). Per the brief, F12 is settled by the owner and not reopened; it still shows `open` here in the reviewer's vocabulary because the failing-first run remains unreproduced.

## Findings

### Bugs

**F5 (Important, new in rev 3; pass: Bugs, consistency of documents) — Ready-check item 3 contradicts itself and drops the exact-commit rule for a commit "that changes no code"**
- **Location:** `bundles/base/process/REVIEW_CYCLE.md:57` (plan Task 7, "Change" line 165, prescribed this wording)
- **Evidence:** item 3 now reads "...ticked by a human in the pull request; a commit that changes no code needs no second confirmation, a commit that changes code does. A run for an older commit is not the result." The two sentences cannot both hold for a commit after the confirmed one: if a no-code commit needs no second confirmation, the CI result in force is the one for an older commit, which the last sentence says is not the result. Item 1 and the PR template line ("CI of that exact commit") also keep the exact-commit wording. "Code" is not defined: a commit that changes only agent instructions, rules, hooks configuration or `test_bundle.py` is not "text in documents" by the light path section of the same file, yet it could be read as "no code" here. Here the bundle lint and tests are the CI gate for exactly such text, so skipping a second confirmation could let a behavior-changing commit ride on an older green run. `docs/process/REVIEW_CYCLE.md` (installed) and `bundles/base/agents/coordinator.agent.md:61` still say "a human confirms it" for the exact commit (see F8).
- **Direction:** Decide, as an owner or amendment question (the plan prescribed the wording), what "no second confirmation" covers: name the kinds of commit (for example only the review file or the pull request text) and say that any other commit gets its own CI read; or drop the clause. State once how it fits with "a run for an older commit is not the result".
- **State:** repaired (rev 4)
- **Rev 4 evidence:** `bundles/base/process/REVIEW_CYCLE.md:57` now reads "CI of that exact commit has been read by the `coordinator` and ticked by a human in the pull request (the tick is in the pull request, never a commit). Every commit gets its own read and tick, including a commit that changes only text: the light path saves review effort, not the CI check. A run for an older commit is not the result." The "no second confirmation" clause is gone (`grep -n "no second confirmation" bundles/base/process/REVIEW_CYCLE.md` prints nothing, by the test's own assertion), the exact-commit sentence is kept, and there is no exemption for a no-code commit. `test_review_cycle_round2_repairs` asserts all of this and passes. Item 1 and the PR template line keep the exact-commit wording, so the three places now agree. Installed copy not refreshed (Task 18; see F8).

**F6 (Important, new in rev 3; pass: Bugs, consistency of documents) — Two homes for "what was decided about a finding", and an instruction that contradicts the reviewer's own re-review rule**
- **Location:** `bundles/base/process/REVIEW_CYCLE.md:56` and the new table row at `:46` against `:24`, `:29`, `:31`, `:37` (all in that file)
- **Evidence:** the new table says a decision about a finding lives in the pull request, and item 2 says "(the reviewer's file keeps it `open`)". Line 24 (Re-review row) still tells the `reviewer` to show each earlier finding "as repaired, deferred or rejected with evidence", line 29 says every finding ends in one of three states, and the plan's amendment carries a "Finding / End / Reason" table (Phase 3 plan, "Findings not repaired") that records the same decision. The review template also has a counts table with Deferred and Rejected columns. An agent reading line 56 would leave a deferred finding `open`; an agent reading line 24 would mark it `deferred`; the ready check (old wording, "the counts table shows no open finding") has been replaced, but the state vocabulary in the reviewer's file has not. The coder's note says the item 2 wording was kept so `test_review_cycle_ready_check_leaves_the_decisions_to_a_human` still passes; the owner approved that and I take it as settled, so the finding is about the other lines, not the ending of item 2.
- **Direction:** Say in the home table which part of a finding's end is the reviewer's (repaired, with evidence; open otherwise) and which is the human's (deferred, rejected, kept in the pull request), and align lines 24, 29 and 31 with it; or note that the amendment's table is the plan's copy of the decision and the pull request is the home. One rule for the reviewer.
- **State:** repaired (rev 4)
- **Rev 4 evidence:** one rule now reads the same everywhere I looked. `bundles/base/process/REVIEW_CYCLE.md:15` (re-review row: "repaired, with evidence, or still `open`"), `:18` ("The reviewer's file records only `open` and `repaired` (with the evidence); a human decides deferred and rejected, and the decision is recorded in the pull request"), `:24` ("moves each earlier finding from `open` to `repaired` with its evidence, or leaves it `open`"), `:27`, `:46` (home table: the amendment's table of findings not repaired is "the planner's proposal, not a second home"), `:56`. `bundles/base/templates/REVIEW_PLAN_TEMPLATE.md:25-32` has a two-column counts table (Open, Repaired) and the line "Deferred and rejected findings are a human's decision and are counted in the pull request, not here"; `:50` limits State to `open` or `repaired` and says the reviewer never writes the other two. `bundles/base/agents/planner.agent.md:78` says the planner proposes and a human decides and records it in the pull request. `bundles/base/HOWTO.md:75` lists the decision among the PR lines without a state vocabulary. A grep of `bundles/base` (agents, process, templates, rules, HOWTO) for `deferred|rejected` finds no remaining instruction that has the reviewer writing either state; the PR template keeps Deferred and Rejected columns, which is where the human counts them (the intended home). The old sentence "as repaired, deferred or rejected with evidence" is absent (the test asserts it). Leftover noted, not a finding: `REVIEW_CYCLE.md:18` still says "Every finding ends in one of three states", which is true of the whole process and is qualified by the next sentence.

### Security
(none)

### Compliance

**F1 (Important) — The capability record still says nothing was seen in a live client, contradicting the F4 fix**
- **Location:** `docs/agents/harness-capabilities.md:87` (not in Tasks 1 to 6; the shipped `INSTALL.md:78,91` and `HOWTO.md:120` now say the opposite)
- **Evidence:** line 87 ends "Nothing here was seen in a live client: the recorded runs of 2026-11-08 captured no guard log." It says it holds "the same table" as `INSTALL.md`, and `INSTALL.md:89,91` names this file as the source of each row and as "the capability record behind" the new live-refusal sentence. `docs/agents/claude-desktop-failures.md:191` (F9) records one live guard refusal (`no-heredocs`, `test-coder`, 2026-11-09). A repo-wide grep for "not yet seen|no live|live client|captured no guard" outside `docs/plans` finds this line as the only remaining false statement. The plan's F4 task lists only `INSTALL.md`, `HOWTO.md` and the Phase 2 row, and its acceptance grep covers only the two shipped files, so the miss is a plan gap carried through, not a coder deviation.
- **Direction:** Decide whether to bring line 87 into line with the F4 wording (an owner or amendment decision; the file is outside the plan inventory), or record it as a known remaining statement. The plan's objective ("fixed instead of shipped as known issues") is not met for the source record until then.
- **State:** repaired (rev 2)
- **Rev 2 evidence:** `git diff e68312f eea5424 -- docs/agents/harness-capabilities.md` is one line (87), and its new last sentence is the one the plan's Task 19 gives, word for word; no table row changed. The file is not in `.manifold/manifest.json`, so no install refresh was owed. The F9 claim still matches `docs/agents/claude-desktop-failures.md` (test-coder, a subagent, 2026-11-09). The repo-wide grep of Task 19 (`grep -rInE "Nothing here was seen|not yet seen in a live|recorded in a live|None of this has been recorded" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=plans`), run by me, prints two lines: `bundles/base/tests/test_bundle.py:2249` and `:2250`, the absence assertions of the Task 5 test. The owner has accepted this; noted, not a finding. No false statement remains in any document.

### Tests

**F2 (Nit) — Failing-first run of Task 5 not reproduced by the reviewer**
- **Location:** `docs/plans/PHASE_3_PLAN.md` Task 5 note; `bundles/base/tests/test_bundle.py` `test_deferred_text_fixes_f1_f4_f5`
- **Evidence:** the test passes now (`1 passed, 2033 deselected`). The note's "1 failed" on the unchanged files could not be reproduced here: my attempt to stage the old tree used a shell redirect and the guard refused it (see Rule exceptions compared). The commit order also cannot show it, because the test and the text fixes are in the same commit `996bcbd`. The test's assertions are the ones the plan names, and the old text does contain every needle (`Phase 2`, `CP2a`, `not yet seen in a live run`, `recorded in a live`; the `curl -o` line is new in the diff), so a failure on the old files is plausible.
- **Direction:** None required; reproduce with a clean checkout of `3e2bbaf` plus the new test file if the owner wants first-hand evidence.
- **State:** repaired as accepted (rev 2): the owner accepted F2 on the condition that the evidence is recorded if it can be produced. Task 21's note records `git worktree add --detach ... 3e2bbaf`, the test added there with `Edit`, and "1 failed, 1955 deselected" on the old text, with no guard refusal and the worktree removed.
- **Rev 2 evidence:** I did not reproduce the run (I did not rebuild a `3e2bbaf` worktree); the count rests on the coder's note. It is consistent with round 1: 1955 is the Task 6 count of the whole bundle tests at that time, and 1 failed plus 1955 deselected equals the old tree's 1956 tests. `git worktree list` shows no leftover worktree under the scratchpad, and `git status --short` in this checkout was clean at the start of this review. `git diff --stat e68312f eea5424 -- bundles/base/tests` is empty: no test edited by the repair.

**F8 (Nit, new in rev 3) — Compliance / consistency: the new process text is ahead of the places that apply it, until Tasks 11, 12 and 18**
- **Location:** `docs/process/REVIEW_CYCLE.md:44-45` and `docs/templates/PULL_REQUEST_TEMPLATE.md:62` (installed, old wording); `bundles/base/agents/coordinator.agent.md:61` and `.claude/agents/coordinator.md:72` ("a human confirms it"; no level named); `bundles/base/HOWTO.md:75`
- **Evidence:** `cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md` and the same for the PR template differ. The plan's inventory (line 74) says the install refresh is done later (Task 18) and the coordinator text changes in CP3 (Task 12). Until then, the coordinator in this repository reads the old installed ready check and its definition lacks the "closing report names the level" duty that the shipped `REVIEW_CYCLE.md` now states. Not a deviation; a transitional inconsistency that a reader of CP2 alone would see.
- **Direction:** None for CP2; check at the CP3 review that the coordinator text, HOWTO and the refreshed install agree with this file (and with the resolution of F5 and F6).
- **State:** repaired (rev 6)
- **Rev 6 evidence (commit `6716af3`, Task 18):** the installed copies now equal their sources. `cmp` printed nothing (all equal) for `bundles/base/process/REVIEW_CYCLE.md` vs `docs/process/REVIEW_CYCLE.md`, `templates/PULL_REQUEST_TEMPLATE.md`, `templates/PHASE_PLAN_TEMPLATE.md`, `templates/REVIEW_PLAN_TEMPLATE.md`, `HOWTO.md` vs `docs/process/HOWTO.md`, `process/BREACH_PROCEDURE.md`, `hooks/guard.py`, `scripts/phase_status.py` vs `.manifold/phase_status.py` and `commands/phase-status.md` vs `.claude/commands/phase-status.md`. Every file in `.manifold/manifest.json` (25) matches its sha256 on disk (a read-only `python3 -c`, 0 bad), and the same 25 hashes equal a fresh in-memory `build_payload()` of the current bundle (so the seven rendered agent definitions, which have no single source file, equal the build output; 0 differences). The installed coordinator (`.claude/agents/coordinator.md:73,101`) now carries the exact-commit CI wording, the level report (mergeable, releasable, done; never declares done) and the single CI-write exception; the old "a human confirms it" wording is gone. The installed `AGENTS.md` managed block carries the self-contained-asks sentence (`grep -c "internal ID" AGENTS.md` prints 1, and 1 in each of the six agent definitions that carry rules). The transitional state named in this finding no longer exists. The same applies to the CP3 and CP7 notes that said the install was old until Task 18 (the AGENTS.md block, the coordinator, HOWTO).

**F9 (Nit, new in rev 3; pass: Compliance) — `docs/agents/claude-desktop-failures.md` is changed but is not in the plan's inventory or Tasks 7 to 10**
- **Location:** `docs/agents/claude-desktop-failures.md:239-249` (entry F13)
- **Evidence:** the commit's file list has six files; five are named in Tasks 7 to 10, the sixth is the breach record. `docs/process/BREACH_PROCEDURE.md` says the `coordinator` (or the owner) records breaches, and the entry was added in the coder's CP2 commit. Earlier entries F11 and F12 were added in separate record commits (`cdc0362`, `e68312f`). The content checks out against the guard log (see "Rule exceptions compared, rev 3"), with one detail: the entry and the plan note call it an "empty" or "pointless" snippet, while the logged command is a compound one whose first 80 characters are the heredoc followed by a `grep` on the plan file.
- **Direction:** Record the file as an accepted addition in the CP2 note or the completion summary, as was done for the earlier entries; no change to the entry required.
- **State:** open

### Context files (and Tests, Rev 3)

**F10 (Nit, new in rev 3; pass: Tests) — Task 10 failing-first run not reproduced; one assertion was changed after the passing run**
- **Location:** `docs/plans/PHASE_3_PLAN.md` Task 10 note; `bundles/base/tests/test_bundle.py` `test_review_cycle_names_homes_levels_and_light_path` (about line 2255)
- **Evidence:** the note records "2 failed, 2034 deselected" before and "2 passed" after, and says one assertion of the first test was changed afterwards (whole file to the ready-check section). I ran the two new tests plus the existing ready-check test: `4 passed, 2032 deselected`. I did not reproduce the failing run on the old text (it needs a worktree of `cdc0362` plus the new tests; not rebuilt). The old text lacks all three headings and the PR template sections, so a failure there is certain for the first assertion of each test. The first test checks the three headings, "solo", "never code" and item 3, but not the level names or the full sentence "never code, rules, agent permissions, hooks or tests"; that is the plan's own scope for the test. No existing test was changed: `git diff 30e88bd~1 30e88bd -- bundles/base/tests` has 0 removed lines (`grep -c '^-[^-]'` printed 0).
- **Direction:** None required; optional first-hand reproduction by the owner.
- **State:** open

**F3 (Nit) — The lessons paragraph keeps a pointer to history that no longer exists**
- **Location:** `bundles/base/process/REVIEW_CYCLE.md:52` (also the installed copy `docs/process/REVIEW_CYCLE.md`)
- **Evidence:** the paragraph now reads "the review must be a file (the points were numbered by hand)". With the table deleted, "the points" has no antecedent for a reader of a shipped document. Task 3's acceptance grep passes (nothing for `Phase 2|CP2| his |first cycles`); `grep -rIn "first cycles"` finds no link to the removed heading outside historical plan records.
- **Direction:** Consider dropping or rewording the parenthesis so it needs no history. Style only.
- **State:** repaired (rev 2)
- **Rev 2 evidence:** `bundles/base/process/REVIEW_CYCLE.md` and `docs/process/REVIEW_CYCLE.md` each change one line, the exact replacement the plan's Task 20 names ("the review must be a file, not a chat message;"), and the rest of the paragraph is unchanged. `grep -rn "numbered by hand" bundles docs/process .manifold` prints nothing; `cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md` is equal; `shasum -a 256 docs/process/REVIEW_CYCLE.md` is `824929931473835b0cf352b244ebd01d3018c6bba761a30d83757da527b73c0d`, equal to its entry at `.manifold/manifest.json:27`. The manifest diff is only that hash and `installed_at`, as an install refresh produces.

**F4 (Nit, new in rev 2) — The repair checkpoint has no "Rule exceptions" line in the plan**
- **Location:** `docs/plans/PHASE_3_PLAN.md` Tasks 19 to 21 notes (the only "Rule exceptions:" line in the file is line 159, for CP1)
- **Evidence:** the coder reported "none" for the repair, but `grep -n "Rule exceptions" docs/plans/PHASE_3_PLAN.md` finds no such line for Tasks 19 to 21. The working rule says every report from an agent that changed files or ran commands carries the line. Whether the report itself carried it is outside what I can see; the plan, which is the record, does not. Compared with the diff and guard log, "none" holds (see "Rule exceptions compared, rev 2").
- **Direction:** Record the line in a later task's note or the completion summary (a completed task's note is not edited). Style and traceability only.
- **State:** repaired (rev 3)
- **Rev 3 evidence:** commit `30e88bd` adds, at `docs/plans/PHASE_3_PLAN.md` after the Tasks 19 to 21 verification line, "Rule exceptions (Tasks 19 to 21): none (the owner's decision on review finding 4: they were none)." It is in a later place than the completed notes, which were not edited. The "none" is the owner's, not the coder's observation; it matches what I compared in rev 2.

**F7 (Nit, new in rev 3; pass: Compliance) — The light path does not say whether a review and the ready check still apply**
- **Location:** `bundles/base/process/REVIEW_CYCLE.md` section "Light path for text fixes" (lines 72 to 79)
- **Evidence:** the section says the route is "shorter" and "so they do not need a full amendment round", and lists four conditions, the last being a human tick on the diff. It does not say whether a `reviewer` pass, `REVIEW_PLAN_<N>.md` and the four ready-check lines are still required for such a change. The intent (S7, "Must never": skip the human's approval) is met by the tick; whether item 1 of the ready check (a review of the final commit exists) holds on this path is left to the reader. Who decides that a change "changes no behavior" is also not named (the diff reader, the author or the human who ticks).
- **Direction:** One sentence: what is skipped (the amendment round) and what is kept (review, ready check, or neither), and who judges "text only".
- **State:** repaired (rev 4)
- **Rev 4 evidence:** `bundles/base/process/REVIEW_CYCLE.md:81` adds: "What it skips: the planner amendment and the repair checkpoint. What it keeps: a review of the final commit by the `reviewer` (a revision of `docs/plans/REVIEW_PLAN_<N>.md`), the four lines of the ready check, with CI of every commit read and ticked, and the human's tick of the diff. Who judges "text only": the human who ticks judges ... the author's word does not count, and when the human doubts it, the full amendment round applies." Line 77 also narrows "text" (a comment or docstring qualifies only when the diff shows no other changed line). All three questions of F7 are answered. The test asserts "the human who ticks judges" and "ready check" in the section.

### Rev 4 additional findings (CP3)

**F11 (Important, new in rev 4; pass: Bugs, consistency of agent instructions) — The coordinator is told to write the CI result into the pull request with no owner go-ahead, while the next section says to write to the pull request only with it**
- **Location:** `bundles/base/agents/coordinator.agent.md` the new bullet in "CI of the exact commit" (diff line "Write the result for that exact commit into the pull request's remaining-steps list ... for a human to tick") against the "Ready check" paragraph's last sentence ("Write the description or a comment to the pull request only with the owner's go-ahead")
- **Evidence:** the plan's Task 12 says the coordinator "writes the CI result for the exact commit into the pull request's remaining-steps list", and the new bullet carries no condition. Editing the PR description is a write to the pull request, and the Ready check paragraph, unchanged by this commit, requires the owner's go-ahead for that. An agent reading the CI section alone would edit the PR for every commit (the bullet says every new commit needs its own read and tick); an agent reading the Ready check paragraph would wait. `test_coordinator_reports_level_and_compares_branch_rules` checks only the phrases "remaining-steps list" and "no commit", not the go-ahead.
- **Direction:** Decide, as an owner or amendment question, whether the go-ahead is given once for the phase's PR (then say so in the bullet) or per write, and make the two sections say the same. Where `gh` is unavailable the existing last bullet already covers "not read".
- **State:** repaired (rev 5)
- **Rev 5 evidence:** commit `1ccf6ae`, `bundles/base/agents/coordinator.agent.md`. The four places now agree: line 17 (operating rule) "Nothing is exempt except the one exception: the CI result line that "CI of the exact commit" and "Ready check" name"; line 57 (CI bullet) "This is the one write to the pull request you make without asking each time: the owner has given a standing permission ... Write that line only; change nothing else in the pull request"; line 62 (Ready check) "only with the owner's go-ahead; the one exception is the CI result line in the remaining-steps list ... Every other pull request write needs the go-ahead"; line 84 (What you do not do) "without the owner's go-ahead (the one exception is the CI result line ...)". `grep -n "go-ahead\|without asking"` lists exactly those four lines, so no fifth place. Greps I ran: "the one exception" 3, "without asking each time" 2, "Every other pull request write needs the go-ahead" 1, "Write that line only; change nothing else" 1. `bundles/base/HOWTO.md` matches: step 12 "What the agents will not do" and the human gates bullet each carry the exception ("he one exception is the CI result line" 2 hits; the bullet names it in parentheses). The permission is limited to one line in the remaining-steps list; the tick stays human; push, open, edit, other comment and issue posts still need the go-ahead. Not widened.

**F12 (Nit, new in rev 4; pass: Tests) — Failing-first run of Task 14 not reproduced**
- **Location:** `docs/plans/PHASE_3_PLAN.md` Task 14 note; `bundles/base/tests/test_bundle.py` (`test_coordinator_reports_level_and_compares_branch_rules`, `test_ask_rule_requires_self_contained_asks_for_coordinator`)
- **Evidence:** the note records "2 failed, 2037 deselected" before Tasks 12 and 13 and "2 passed, 2037 deselected" after. The arithmetic fits (2037 + 2 = 2039 = 2038 passed + 1 skipped, the full count I ran). I ran `-k "coordinator_reports_level or self_contained_asks or round2_repairs"`: `3 passed, 2036 deselected`. I did not rebuild the old tree, so the failing run rests on the coder's note. The old coordinator text has no "## Branch rules" heading and the old rule lacks "coordinator" in `applies_to`, so a failure there is certain for the first assertion of each test. No existing test edited: `git diff -U0 db37ef6~1 db37ef6 -- bundles/base/tests | grep -c '^-[^-]'` printed 0; the same for `815baa3` printed 0.
- **Direction:** None required; optional first-hand reproduction.
- **State:** open

**F13 (Nit, new in rev 4; pass: Compliance, verified claims) — `BRANCH_RULES.md` omits one value the ruleset read shows**
- **Location:** `docs/process/BRANCH_RULES.md:27-39` (the rules table)
- **Evidence:** I repeated the read (GET only: `gh api --method GET repos/{owner}/{repo}/rulesets/26275761`). Every row of the table matches: checks `test (3.10)` and `test (3.12)` with `integration_id` 15368, `strict_required_status_checks_policy: true`, `allowed_merge_methods: ["squash"]`, `required_linear_history`, 1 approving review, `dismiss_stale_reviews_on_push: true`, `required_review_thread_resolution: true`, `require_code_owner_review: false`, `require_last_push_approval: false`, `deletion`, `non_fast_forward`, and the two bypass actors (`OrganizationAdmin` with no actor id, `RepositoryRole` id 5, both `pull_request`). The ruleset also has `require_extra_approval_for_unattributed_changes: true`, which the file does not list; the file's claim "records what was read" is therefore not complete, though nothing false is stated. The tag ruleset is marked unverified, and role 5, the up-to-date `updated_at` caveat and the 404 URL are marked as such. The workflow claims hold: neither `ci.yml` nor `server.yml` has a `paths` filter (`grep -n paths` prints nothing in `server.yml`; `ci.yml` read to line 12), `ci.yml` job `test` has the matrix `["3.10", "3.12"]`, and `git diff --stat db37ef6~1 db37ef6 -- .github` is empty.
- **Direction:** Add the row, or say the table lists the rules the owner cares about and not every parameter.
- **State:** repaired (rev 5)
- **Rev 5 evidence:** `docs/process/BRANCH_RULES.md` (diff of `1ccf6ae`: 3 added lines, 0 removed) adds the row "Extra approval for unattributed changes | required (`require_extra_approval_for_unattributed_changes: true`)" after "Code owner review", and the sentence "What `require_extra_approval_for_unattributed_changes` means: unverified: confirm with the GitHub REST page "Rules" ... or the ruleset page." My own read, `gh api --method GET repos/mediumroast/manifold/rulesets/26275761` (GET only, already signed in), filtered to the `pull_request` rule, prints `"require_extra_approval_for_unattributed_changes":true` with the other parameters unchanged from rev 4. The meaning is marked unverified, which is honest; I did not verify it either. `grep -c` of the parameter name in the file prints 2.

### Rev 5 additional findings (CP7)

**F14 (Nit, new in rev 5; pass: Tests) — The new test does not pin the limit of the standing permission**
- **Location:** `bundles/base/tests/test_bundle.py`, `test_coordinator_ci_write_is_the_one_standing_exception` (added at about line 2294)
- **Evidence:** the test pins that the exception is named in four places and that the Ready check says "Every other pull request write needs the go-ahead". It does not assert "Write that line only; change nothing else in the pull request" (CI bullet, line 57), the sentence that keeps the permission from widening, nor "the tick stays" human. A later edit could drop that limit and the test would still pass. It does fail on the old text: the old coordinator has 0 occurrences of "the one exception" or "without asking each time" (`git show 1ccf6ae~1:bundles/base/agents/coordinator.agent.md | grep -c`), so the first assertion fails, as the coder's note records ("1 failed"). Its split strings now resolve (the IndexError of the coder's first run was in the new test only; I ran it: passes).
- **Direction:** Optional: add the limit sentence to the CI-section assertions.
- **State:** open

### Rev 6 additional findings (CP4 and the install refresh)

**F15 (Nit, new in rev 6; pass: Tests) — The "script never writes" test is a deny-list of call names, so it does not pin the read-only property**
- **Location:** `bundles/base/tests/test_phase_status.py:192-209` (`test_no_call_in_the_script_writes_or_changes_a_file`) and `:212` (`test_the_script_imports_only_the_standard_library`)
- **Evidence:** the AST test rejects calls named `open`, `write_text`, `mkdir`, `unlink` and the like, and `print(file=...)` other than to stderr. The stdlib test only checks that every import is in the standard library (`build.lint_hook`). A later edit that adds `import subprocess` or `import os` and calls `subprocess.run(...)`, `os.system(...)` or `getattr(path, "write_" + "text")` passes both tests: the names are not on the list and the modules are standard library. Today's script is read-only (I read all 209 lines: only `Path.read_text`, `is_file`, `print`, no write path; and the two unchanged-contents tests pass), so this is about how long the claim stays true, which INT-26 S3 ("a read of the script shows it only reads") depends on.
- **Direction:** Optional: pin an allow-list of imports (`re`, `sys`, `pathlib`, `__future__`) in the AST test, so a new module has to be argued for.
- **State:** open

**F16 (Nit, new in rev 6; pass: Bugs, verified claims) — The shipped Copilot prompt says "run this in the terminal" but does not say what to do when no terminal is available**
- **Location:** `bundles/base/commands/phase-status.prompt.md:6-12` (installed to `.github/prompts/phase-status.prompt.md` for the copilot format; not installed in this repository, which is a `claude` install)
- **Evidence:** the Task 15 note marks as not verified "that a shell tool is available to a prompt file run" and the behaviour of `${input:...}` when the argument is typed after the command. The shipped limit paragraph states the run is the agent's act, that prompt files run only in the Local harness (deprecated, planned removal February 2027) and that the docs describe no way to run a command; it claims nothing the Task 15 note marks unverified (checked against the note: only `name`, `description`, `argument-hint` and `${input:...}`, which the note lists as read). But the instruction line "Run this command in the terminal" is unconditional, and the only error handling is "If it printed an error, show the error and stop". An agent with no terminal tool has no instruction to say so and stop, so it could write a status list from memory, which is exactly what INT-26 S3 ("from the files, not from an agent's memory") and "Must never report an item closed that the files show open" rule out. Prose: "an agent could be misled" is the Important test; I rate it Nit because the paragraph below already warns that the run is the agent's act, and the only evidence of a no-terminal case is the unverified item itself.
- **Direction:** Add one sentence: if you cannot run the command, say so and do not list the open items yourself.
- **State:** open

**F17 (Nit, new in rev 6; pass: Security) — The Claude command pre-approves every `python3` command, and the typed argument reaches the shell unquoted**
- **Location:** `bundles/base/commands/phase-status.md:4` (`allowed-tools: Bash(python3 *)`) and `:8` (`` !`python3 .manifold/phase_status.py $ARGUMENTS` ``); enforced by `build.py` `lint` (about lines 590-596)
- **Evidence:** the plan (Task 15 settled note, Task 17) prescribes exactly this form and the coder read it in the Claude Code documentation, so it is not a deviation. Two consequences are not said anywhere: (1) the permission pattern covers any `python3 ...` command while the command runs, not only the status script; (2) `$ARGUMENTS` is the raw typed text, so `/phase-status 3; <other command>` reaches the shell as typed, and the script's digit check only runs after the shell has parsed the line. The typist is the user, so the trust boundary is the user's own; whether Claude Code splits compound commands before matching the `Bash(python3 *)` rule is not stated in what the coder read and I did not read it: unverified, confirm with the Claude Code permissions documentation. Not run: I did not invoke the command in a client.
- **Direction:** Owner decision (the plan prescribed the form): either narrow the pattern to `Bash(python3 .manifold/phase_status.py *)` (and say that in the lint and test), or record the breadth as accepted.
- **State:** open

**F18 (Nit, new in rev 6; pass: Compliance) — The CP4 "Rule exceptions" line in the plan omits the `/dev/null` redirect that the coder reported and the breach record names**
- **Location:** `docs/plans/PHASE_3_PLAN.md` line 320 (CP4 "Rule exceptions") against `docs/agents/claude-desktop-failures.md` F15 ("Evidence" paragraph)
- **Evidence:** the plan line lists the refused `cmp` and the three web reads, and says "No file written from a shell command". The F15 entry (breach record, same commit) says "The coder also listed a command that ended with a redirect to `/dev/null` (not a file write)", and the brief says the coder's report listed it. A redirect to `/dev/null` writes no file, so no rule was broken, but the line the reviewer and the coordinator compare is the one in the plan, and it does not match the record. The AGENTS.md rule says "if you are unsure whether something was an exception, list it".
- **Direction:** Add the redirect to the plan's CP4 line (or say in the F15 entry that the plan line is the shorter list). No rule effect.
- **State:** open

## Checks that found nothing

- **Rev 6 checks (CP4 and Task 18):**
  - **Script is read-only (Task 16):** `bundles/base/scripts/phase_status.py` read in full (209 lines): imports `re`, `sys`, `pathlib.Path` only; reads with `Path.read_text` and `is_file`; the only output is `print` to stdout and, for errors, to stderr; no `open`, no write, delete, rename, `os`, `subprocess`. `.manifold/phase_status.py` is byte-equal to it. The tests (21) pass and include contents-and-mtimes-unchanged, same output twice, exit 2 for a missing plan and bad arguments, a filled approval never reported blank. I ran it: `python3 .manifold/phase_status.py 3` twice, the md5 of both outputs equal (`fdd297ff...`); `... 99` exits 2 with a plain message and no traceback; `... 1` runs on Phase 1. `git status --short` was clean after the runs.
  - **Script output against the files:** it printed 4 approval lines filled (plan lines 3, 343, 400, 528), 0 unticked and 0 blocked tasks, 2 unticked Completion checklist lines (plan lines 328 and 329), review revision 5 with 5 open findings (F8, F9, F10, F12, F14). I read those lines in the plan and the review: all true at the time of the run (rev 6 changes the review file after the run). One reading note: the "Level aimed at" line is a declaration, not a task, but it counts as an open checklist line, so the script says "below mergeable" until a human ticks it; that is the stated rule (any unticked checklist line) and matches the plan, not a defect.
  - **Install and manifest (Task 18, and F8):** 25 of 25 manifest hashes match the files; the same 25 hashes equal a fresh in-memory `build_payload()` of the bundle at `6716af3` (0 differences); nine `cmp` pairs equal (listed under F8). `install.py --status` itself: not run (needs the unzipped bundle and a built zip; I did not build one). No installed file differs from the build.
  - **Task 17 deviation (install.py):** true. `bundles/base/install.py:143-157` (`selected_entries`) takes an entry that has a `role` by the role list and any other entry by its `profiles` list, so the two new format entries (no role) are chosen by profile, as the Copilot hook file already was. `git diff 07d580d~1 6716af3 -- bundles/base/install.py` is empty. The new test `test_phase_status_is_installed_per_profile_and_flavor_and_uninstalled_cleanly` (3 profiles x flavors, installed then uninstalled to an empty tree) passes, which is the behavioral evidence. The plan inventory said MODIFY; the coder recorded the deviation in the Task 17 note; I agree with it.
  - **Task 17 commands:** `commands/phase-status.md` has `allowed-tools: Bash(python3 *)` and the inline form `` !`python3 .manifold/phase_status.py $ARGUMENTS` `` (both enforced by `build.py` lint and pinned by `test_the_claude_command_pre_approves_python3_and_runs_the_script_inline`; see F17 for the breadth). The skills line in `render_instructions_block` ends "(unverified that an agent runs it as asked)", only for the `skills` and `both` styles. Lint rejects a script with a non-stdlib import and a missing or wrong command file (two tests).
  - **Copilot prompt:** frontmatter uses `name`, `description`, `argument-hint` only, and `${input:phase}`; it states the Local-harness limit and the deprecation, and says the run is the agent's act. It claims nothing that the Task 15 note marks unverified (see F16 for the missing fallback).
  - **Tests:** `git diff --numstat 07d580d~1 6716af3 -- bundles/base/tests/test_bundle.py` prints `111 0`; 0 removed lines; ten test functions added (some parametrized; the suite grew from 2039 to 2078 passed, 39 = 21 + 18, as the coder says); `test_phase_status.py` is new (21 passed). No existing test was edited. The failing-first run of Task 17 (16 failed, 2 passed before the `build.py` change) is the coder's note; I did not reproduce it (it would need `build.py` reverted).
  - **`.github`:** `git diff --name-only origin/main HEAD` lists 39 files, none under `.github/`, `server/` or `tests/`; `git diff 07d580d~1 6716af3 --name-only -- .github` is empty.
  - **Inventory:** the CP4 commits touch the files of Tasks 15 to 18 plus the generated install files and the plan; `AGENTS.md` (managed block) and `.claude/commands/phase-status.md` are install output not named as paths in the inventory row (`.claude/agents/*`, `.manifold/*`, ...), the same as Task 6; `docs/agents/claude-desktop-failures.md` (F15 breach record) is the same kind of unplanned addition as F9. Not new findings.
  - **HOWTO item 6** names `/phase-status <N>`, the Copilot limit and the "ask the agent to run" route for other formats; it matches the shipped prompt and instruction line.

- **Rev 5 checks:** no existing test edited (`git diff --numstat 1ccf6ae~1 1ccf6ae -- bundles/base/tests/test_bundle.py` prints `16 0`); no installed copy touched (`git diff --name-only` for `.claude`, `.manifold`, `bundles/base/hooks` empty; the only `docs/process` file is `BRANCH_RULES.md`, planned); the five files of the commit are the four named in the plan's verification line plus the plan. The working tree is clean.
- **Plan inventory:** `git diff --name-only 3e2bbaf..aabccb3` lists 12 files, all in the Tasks 1 to 6 files or the inventory rows (`.manifold/manifest.json` and `docs/process/*` are the install refresh, `PHASE_3_PLAN.md` holds the notes).
- **Task 2:** `PHASE_2_PLAN.md` has one changed line (the last cell of the INT-20 S1 row), as planned.
- **Task 4:** one line changed in `bundles/base/hooks/guard.py`, inside the docstring; the same words in `docs/agents/harness-capabilities.md:75`, `bundles/base/hooks/guard.py:80`, `.manifold/hooks/guard.py:80`.
- **Task 6 and the merge:** `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` equal; sha256 of the installed `guard.py`, `docs/process/REVIEW_CYCLE.md` and `docs/process/HOWTO.md` equal the hashes in `.manifold/manifest.json`. `git diff aabccb3 7a79d22` shows the merge changed `.manifold/hooks/guard.py`, `bundles/base/hooks/guard.py`, the manifest and `harness-capabilities.md` only through #32 (a worktree rule, a new residual-gap bullet, new guard tests); it did not touch or undo any CP1 line (the F1 line is present in all three files), and it did not change `REVIEW_CYCLE.md` or `HOWTO.md`.
- **F9 claim:** the shipped wording ("a live refusal ... for a subagent") matches `claude-desktop-failures.md` F9 (test-coder, a subagent). Shipped CP1 text names no date, finding ID or person.
- **Test edits:** no existing test line was removed or changed (0 deleted lines in `test_bundle.py`); one test added.
- **Light-path pilot:** the plan asks the owner to read the Task 1 to 4 diff and tick it in the PR; nothing for the reviewer to decide.

## Rule exceptions compared

The writer's line (plan line 146, uncommitted) says "not established": no coder shell commands or transcript are available, `.manifold/guard-log.jsonl` has one entry that says nothing about CP1, and the diff touches only files named in Tasks 1 to 6 plus the manifest. Compared:
- **Guard log:** `.manifold/guard-log.jsonl` (gitignored) holds one line, a reviewer `write-allowlist` event at 2026-11-11T20:03:10Z for a path in another worktree. The commits are 07:41 -0800 (about 15:41Z), so the entry is later than CP1 and unrelated to it. Matches the writer's statement.
- **Diff and log:** `git log 3e2bbaf..aabccb3` shows two commits by `mihay42`; the 12 changed files are all within Tasks 1 to 6 or their install output. Matches.
- **Not matched or not checkable:** the guard log covers only this checkout and starts after the commits, so a CP1 breach (or the guard's refusal of one) could not be seen either way. The Task 6 note's "the guard did not block the install" cannot be verified. Status: not compared beyond the above; "not established" is the honest value and I agree with it.

## Rule exceptions compared, rev 3

The coder's CP2 line (plan, after the CP2 gates): "none broken", with one attempt refused by the guard (`no-heredocs`), not retried, nothing written, nothing staged or committed. The owner's line adds that the empty heredoc was logged as F13. Compared:
- **Diff:** `git show --stat 30e88bd` lists six files: `bundles/base/process/REVIEW_CYCLE.md`, `bundles/base/templates/PHASE_PLAN_TEMPLATE.md`, `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `bundles/base/tests/test_bundle.py`, `docs/agents/claude-desktop-failures.md`, `docs/plans/PHASE_3_PLAN.md`. The first four and the plan are named in Tasks 7 to 10; the breach record is not (F9). No hook, rule, agent or installed file changed. Matches "none broken".
- **Guard log:** `.manifold/guard-log.jsonl` (gitignored, this checkout) now has four lines. Two are mine from earlier rounds (reviewer, `no-heredocs`, 20:18:44Z and 23:41:35Z). One is the coder's: 23:48:04Z, rule `no-heredocs`, agent_type `coder`, command beginning `python3 - <<'EOF' 2>&1 | head` followed by `EOF` and a `grep -n` on the plan file. That is the one refusal the coder reported; the count (1 refused, none through) matches. The command is slightly more than "an empty snippet" (a read-only `grep` after it), but it wrote nothing. No other coder line.
- **Commit log:** one commit by `mihay42`, 19:21 -0800; the logged refusal (23:48Z on the same day is earlier than 03:21Z on the next) precedes the commit. Message names Tasks 7 to 10. Nothing staged beyond the task files is visible.
- **Not compared:** the coder's transcript and shell history are not available to me, so a command that the guard did not see and the coder did not mention cannot be excluded. Status: matches; limited as stated.
- **This review:** no refusal so far; I used no shell write.

## Rule exceptions compared, rev 4

The coder's CP3 line (plan, "Rule exceptions (CP3)"): one attempt refused by the guard (`no-heredocs`, a stray `python3 - <<'X'` snippet appended to a verification command, not run, re-run without it); every `gh` call GET; no ruleset, setting or workflow changed; no commit, push or staging; no installed copy edited. Recorded by the coder as F14. Compared:
- **Diff:** `git show --stat db37ef6` lists six files: `coordinator.agent.md`, `ask-on-ambiguity.md`, `test_bundle.py`, `claude-desktop-failures.md`, `PHASE_3_PLAN.md`, `BRANCH_RULES.md`. The first three, the plan and `BRANCH_RULES.md` are named in Tasks 11 to 14; the breach record is not in the inventory (same pattern as F9, already open; not a new finding). `git diff --stat db37ef6~1 db37ef6 -- .github` is empty; no installed file (`.claude/`, `.manifold/`, `docs/process/` other than the new file) changed. Matches "no ruleset, workflow or installed copy edited".
- **Guard log:** `.manifold/guard-log.jsonl` last line: 2026-11-12T13:47:17Z, rule `no-heredocs`, tool Bash, agent_type `coder`, the command beginning with a scratchpad path. One coder refusal, as reported (count 1 refused, none through). The F14 entry's evidence ("last line", rule, agent_type, time) matches the log at the time I read it. The command text in the log is truncated to its first characters, so I cannot confirm the `python3 - <<'X'` detail; the rule and agent match.
- **Commit log:** `git log` shows the commit by `mihay42` at 05:54 -0800 (13:54Z), after the refusal (13:47Z). The coder says it made no commit; the commit exists, so it was made by the owner or the coordinating session (not established by me). Message names Tasks 11 to 14.
- **`gh` calls:** I cannot see the coder's calls. The recorded set is all GET. My own repeat of the ruleset read gave the same data, so the file's content is not in doubt; whether any write call was made is not checkable by me.
- **Not compared:** the coder's transcript and shell history. Status: matches; limited as stated.

## Rule exceptions compared, rev 2

The coder's line for the repair was "none". Compared:
- **Diff:** `git show --stat eea5424` lists five files: `.manifold/manifest.json`, `bundles/base/process/REVIEW_CYCLE.md`, `docs/agents/harness-capabilities.md`, `docs/plans/PHASE_3_PLAN.md`, `docs/process/REVIEW_CYCLE.md`. All are named in Tasks 19 to 21 or are the install output. No code, test or other file changed. Matches "none".
- **Commit log:** one commit by `mihay42`, 15:40 -0800 (about 23:40Z). Message names the three repairs.
- **Guard log:** `.manifold/guard-log.jsonl` (gitignored, this checkout) holds a reviewer `write-allowlist` event (20:03:10Z, another worktree) and my own `no-heredocs` refusal of round 1 (20:18:44Z); both are earlier than the repair commit and neither is the coder's. No coder entry. During this round my `python3 -c` unzip of the rebuilt bundle was refused by the guard (`no-heredocs`, python code that writes files); I did not retry it another way (see Gates run). This will add one reviewer entry to the log.
- **Status:** matches; the log cannot show a coder breach that the guard did not see, and the coder's shell history is not available.

## Gates run

| Command | Counts | Result |
|---|---|---|
| `python3 bundles/base/tools/build.py --check` | n/a | `lint ok` |
| `.venv/bin/python -m pytest bundles/base/tests -q` (at merge HEAD `7a79d22`, includes #32's tests) | 2033 passed, 1 skipped | pass (the Task 6 note's 1955 passed is for `aabccb3`; not re-run at that commit) |
| `.venv/bin/python -m pytest bundles/base/tests -q -k deferred_text_fixes` | 1 passed, 2033 deselected | pass |
| `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` | n/a | equal |
| manifest hashes vs files (`shasum -a 256`, 3 files) | 3 of 3 | equal |
| `install.py --status` | not run | needs the unzipped bundle; I did not rebuild |
| Rev 2: `python3 bundles/base/tools/build.py --check` at `eea5424` | n/a | `lint ok` |
| Rev 2: `.venv/bin/python -m pytest bundles/base/tests -q` at `eea5424` | 2033 passed, 1 skipped | pass |
| Rev 2: `cmp .manifold/hooks/guard.py bundles/base/hooks/guard.py` | n/a | equal |
| Rev 2: `cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md`; sha256 of `docs/process/REVIEW_CYCLE.md` vs `.manifold/manifest.json:27` | 2 of 2 | equal; hash `82492993...c0d` matches |
| Rev 2: `build.py --out <scratchpad>/dist2` | n/a | built `manifold-base-0.2.0.zip` (lint ok) |
| Rev 2: `install.py --status` from the unzipped bundle | not run | the unzip step (a `python3 -c` zipfile call) was refused by the guard; I did not get the result another way. The coder's note (Task 20: 0 lines MODIFIED) is unverified by me; the hash and `cmp` checks above cover the one file that changed |
| Rev 2: Task 19 and 20 acceptance greps (as written in the plan) | n/a | Task 20 grep prints nothing; Task 19 grep prints the two accepted test lines |
| server tests, `tests/live`, `vendor_web.py --check` | not run | outside CP1 verification |
| Rev 3: `python3 bundles/base/tools/build.py --check` at `30e88bd` | n/a | `lint ok` |
| Rev 3: `.venv/bin/python -m pytest bundles/base/tests -q` at `30e88bd` | 2035 passed, 1 skipped | pass; equals the coder's count |
| Rev 3: `.venv/bin/python -m pytest bundles/base/tests -q -k "review_cycle_names or pr_template_has or ready_check"` | 4 passed, 2032 deselected | pass (the two new tests and the existing ready-check tests) |
| Rev 3: Task 7 to 9 greps (headings, five table rows, `never a commit`, `mergeable`, `releasable`, `Light path`, `What remains for you`, `Decisions for you`) | n/a | read in the diff of `30e88bd`: all present; table has five rows |
| Rev 3: build twice with `build.py --out` and `cmp`; `install.py --status`; server tests, `tests/live`, `vendor_web.py --check` | not run | the coder's note is the only evidence for the twice-built zip; the others are outside CP2 verification |

| Rev 4: `python3 bundles/base/tools/build.py --check` at `db37ef6` | n/a | `lint ok` |
| Rev 4: `.venv/bin/python -m pytest bundles/base/tests -q` at `db37ef6` | 2038 passed, 1 skipped | pass; equals the coder's count |
| Rev 4: `.venv/bin/python -m pytest bundles/base/tests -q -k "coordinator_reports_level or self_contained_asks or round2_repairs"` | 3 passed, 2036 deselected | pass (Task 14's two tests and the round 2 test) |
| Rev 4: removed lines in `test_bundle.py` for `815baa3` and for `db37ef6` | 0 and 0 | no existing test edited |
| Rev 4: `gh api --method GET repos/{owner}/{repo}/rulesets` and `.../rulesets/26275761` (read only) | 2 reads | table of `BRANCH_RULES.md` matches except one omitted parameter (F13) |
| Rev 4: failing-first runs of Task 14 and Task 26; build twice and `cmp`; `install.py --status`; server tests, `tests/live`, `vendor_web.py --check` | not run | coder's notes only for the first two and the twice-built zip; the rest are outside CP3 verification |

| Rev 5: `python3 bundles/base/tools/build.py --check` at `1ccf6ae` | n/a | `lint ok` |
| Rev 5: `.venv/bin/python -m pytest bundles/base/tests -q` at `1ccf6ae` | 2039 passed, 1 skipped | pass; equals the coder's count |
| Rev 5: `-k "ci_write_is_the_one or howto or coordinator"` | 213 passed, 1827 deselected | pass |
| Rev 5: `gh api --method GET repos/mediumroast/manifold/rulesets/26275761` (filtered to the `pull_request` rule) | 1 read | shows the F13 parameter as `true` |
| Rev 5: failing-first run of Task 27 on the old text; twice-built zip `cmp`; `install.py --status`; server tests, `tests/live`, `vendor_web.py --check` | not run | the old-text failure is established by reading (0 hits of the new phrases in the parent); the rest are coder-note evidence or outside CP7 |
| Rev 6: `python3 bundles/base/tools/build.py --check` at `6716af3` | n/a | `lint ok` |
| Rev 6: `.venv/bin/python -m pytest bundles/base/tests -q` at `6716af3` | 2078 passed, 1 skipped | pass; equals the coder's count |
| Rev 6: `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` | 21 passed | pass |
| Rev 6: `.venv/bin/python -m pytest tests/live -q` | 24 passed | pass (CI does not run them) |
| Rev 6: `.venv/bin/python tools/vendor_web.py --check` | n/a | "vendored files match a fresh build" |
| Rev 6: server tests, `cd server && ../.venv/bin/python -m pytest -q -p no:cacheprovider` | 1060 passed, 2 warnings, 132.12 s | pass; equals the coder's count (the warnings are Pydantic deprecations, not from this change) |
| Rev 6: nine `cmp` pairs, source vs installed (listed under F8) | 9 of 9 | equal |
| Rev 6: manifest sha256 vs files; manifest hashes vs a fresh in-memory `build_payload()` | 25 of 25; 25 of 25 | 0 bad; 0 differences |
| Rev 6: `python3 .manifold/phase_status.py 3` twice (md5 of each output); `... 99`; `... 1` | equal; exit 2; ran | pass |
| Rev 6: `install.py --status`; two `--out` builds and `cmp` | not run | needs a built and unzipped bundle; the reviewer builds nothing (the coder's note reports 25 `ok` and 344969 bytes twice, `cmp` equal; not reproduced) |

## Rule exceptions compared, rev 6

The coder's CP4 line (plan line 320): "none broken"; three read-only WebFetch reads on 2026-11-12 (recorded in the Task 15 note); no web read and no `gh` call in the continuation; one command refused by the guard (rule `protected-file`, a `cmp` loop over `.claude/agents/`), not retried another way; no file written from a shell command; no commit, push or staging; no installed copy edited by hand; no existing test edited; `.github/` unchanged. The brief adds that the coder's report also listed a redirect to `/dev/null`. Compared:
- **Guard log:** `.manifold/guard-log.jsonl` has, after the earlier entries I compared (2026-11-11T23:48:04Z `no-heredocs`, 2026-11-12T13:47:17Z `no-heredocs`, both coder, CP2 and CP3), one new coder entry: 2026-11-12T20:54:37Z, rule `protected-file`, tool Bash, command beginning with a scratchpad variable assignment (truncated in the log). That is the one refused `cmp` the line names, 8 seconds after `installed_at` (2026-11-12T20:54:29Z) in `.manifold/manifest.json`, so it came right after the apply step. Matches. The log is gitignored and covers this checkout only.
- **Diff and commits:** `07d580d` and `6716af3` (both 2026-11-12 13:14:56 -0800) carry only files of Tasks 15 to 18 and the generated install files (see "Checks"); no `.github` file, no ruleset, no hook source (the `guard.py` pair is unchanged in these two commits), no staged extra. No installed file differs from the build (manifest and in-memory build, above), so "no installed copy edited by hand" is consistent with the files; I cannot see the hands.
- **Not matched:** the `/dev/null` redirect is in the F15 breach entry but not in the plan line (F18, a Nit). A redirect to `/dev/null` is not a file write, so no rule is broken.
- **Not compared:** the coder's transcript and shell history; the three WebFetch reads (the plan notes and the breach entry do not let me see them; the log records only refusals); that no `gh` call was made in the continuation. Status: matches as far as the log and the diff go.
- **My own refusals, this review (listed again under "Rule exceptions (this review)"):** one `no-heredocs` and one `write-allowlist` entry from the reviewer are the last two lines of the log.

## Rule exceptions compared, rev 5

The coder's CP7 line (plan, after the CP7 verification): "none"; the only `gh` call a GET of the ruleset; one deviation (wording of the operating rule) noted as not an exception. Compared:
- **Diff:** `git show --stat 1ccf6ae`: `HOWTO.md`, `coordinator.agent.md`, `test_bundle.py`, `PHASE_3_PLAN.md`, `BRANCH_RULES.md`. All named in Tasks 27 to 30 or the plan notes. No installed copy, hook, rule, `.github` file or ruleset changed. Matches.
- **Guard log:** `.manifold/guard-log.jsonl` last line is still 2026-11-12T13:47:17Z (coder, `no-heredocs`), the refusal I compared in rev 4 for CP3. The commit time is 06:15 -0800 (14:15Z), so that entry is earlier than the commit and no new entry exists for CP7. The log is gitignored and covers only this checkout. Matches "none".
- **`gh` calls:** I cannot see the coder's calls; my own GET repeat gave the same value the coder reports.
- **Not compared:** the coder's transcript and shell history. Status: matches; limited as stated.

## CI on the pushed commit

Not checked: I did not read CI for `aabccb3` (no `gh` call made; the plan says a human confirms CI). Rev 6: CI was not read for `07d580d` or `6716af3` either.

## Tests run and changed

One test added (`test_deferred_text_fixes_f1_f4_f5`), none changed, none deleted. This is text work, not a bug fix, so the failing-first rule applies only as the plan's own acceptance line; see F2. Real-use evidence for the changed text (item d of the standard): no evidence yet, by nature of these edits.

## Rev 2 summary of the repair

- Plan inventory and deviations: no unplanned file in `eea5424`; the Task 19 grep deviation was reported in the coder's note and accepted by the owner.
- The repair added no new text that contradicts another document: the new sentence in the capability record agrees with `INSTALL.md` and `HOWTO.md` as changed in CP1; the REVIEW_CYCLE reword is neutral. Completed CP1 task notes were not edited, as the amendment says.
- Real-use evidence (item d): no evidence yet.

## Rev 3 summary of CP2

- **Plan inventory and deviations:** Tasks 7 to 10 are all marked done with notes; the plan template line, the PR template sections and both tests match the plan's wording. One recorded deviation (item 2 ending), settled by the owner. One unplanned file (F9). Added beyond the plan text: "the `coordinator` may record the decision" in the decisions row; read as consistent with "a tick is a human act", not a finding.
- **Intent (INT-26):** S7 and the "light path never covers code, rules or agent permissions; solo only; human approval kept" constraints are present in the text; the open points are F5 to F7. The intent's "approval follows the review policy" holds: item 4 of the ready check is unchanged.
- **Standard for documents:** (a) traceability: each Task 7 to 10 acceptance line maps to a section and a test; (b) consistency: F5, F6, F8; (c) verified claims: the paths and section names the new text links (`docs/process/REVIEW_CYCLE.md`, `docs/templates/PULL_REQUEST_TEMPLATE.md`, "Where each fact is recorded", `human-confirms-closure` rule file at `bundles/base/rules/core/human-confirms-closure.md`) exist; (d) behavior: no evidence yet; (e) build and tests run, above; (g) owner approval of text that changes agent behavior: the plan is approved and the owner settled the two points named in the header.
- **Nit cap:** 4 new nits plus F4 earlier, within the cap of 5.

## Rev 4 summary of CP3 and the round 2 re-check

- **Round 2 (F5, F6, F7):** all three repaired with evidence above; F8, F9, F10 left as they were (owner-deferred).
- **Task 11 (`BRANCH_RULES.md`):** states what the read showed, marks role 5, the tag ruleset and the skipped-job behaviour as unverified; stacked-PR steps cite `git rebase --help`; recommendation only, `.github` unchanged. One omitted parameter (F13). The owner's acceptance of the file and of the docs-only CI finding is not treated as a finding.
- **Task 12 (coordinator):** level report (mergeable, releasable, done; never declares done), batch of decisions ("accept all", no bare IDs), PR-tick CI flow with no commit, "## Branch rules" comparison that never changes the ruleset, all present and tested. One consistency gap with the go-ahead rule (F11). The shipped text links no unshipped path (the coder's note says a reference check forced this; I saw no `BRANCH_RULES.md` path in the coordinator text).
- **Task 13 (rule):** `applies_to` gains `coordinator`; the Instead text states what, why, consequence, default and no bare internal ID. The installed `AGENTS.md` managed block still has the old text (`grep -c "internal ID" AGENTS.md` printed 0) and the installed coordinator is old: the same transitional state as F8 (Task 18), owner-deferred; noted, not reopened.
- **Task 14 (tests):** two tests, no existing test edited (F12 for the unreproduced failing run).
- **Standard for documents:** (a) traceability: Task 11 to 14 acceptance lines map to files and tests; (b) consistency: F11; (c) verified claims: ruleset table checked against a fresh read (F13), workflow claims read; (d) behavior: no evidence yet; (e) bundle build and tests run, above; (g) owner approval: plan approved. Real-use evidence for the coordinator changes: no evidence yet.
- **Nit cap:** two new nits plus open nits; within the cap of 5 new nits per review.

## Rev 5 summary of CP7

- **Plan inventory and deviations:** Tasks 27 to 30 are marked done with notes. One recorded deviation (operating-rule wording, "Nothing is exempt except the one exception: ...", so the grep count is 3); the owner accepted it. Task 29's owner reading of the diff was reported by the owner as done (per the brief); the plan note still says "pending" (not a finding; the owner's words are to be added there).
- **Standard for documents:** (a) each acceptance grep maps to a file and I re-ran them (3, 2, 1, 2, 2); (b) consistency: the four coordinator places and the two HOWTO places agree; (c) verified claims: ruleset row confirmed by my GET, meaning marked unverified; (d) behavior: no evidence yet (the standing permission has not been used in a real pull request); (e) tests and lint run, above; (g) the owner decided the standing permission (Open question 2 and the round 3 amendment).
- **Installed copies:** the installed coordinator and HOWTO remain old until Task 18, the same transitional state as F8; not reopened.
- **Nit cap:** one new nit.

## Rev 6 summary of CP4, the install refresh and the whole branch

- **CP4 (Tasks 15 to 18):** all four marked done with notes. Task 15: the notes list the file path and source per flavor, with unverified items marked, and the owner's option (a) is recorded. Task 16: script and 21 tests as described. Task 17: payload, lint, both command files and 18 new tests; the `install.py` deviation is true (see Checks). Task 18: install refreshed, 25 of 25 files match, HOWTO item 6 added. Findings: four Nits (F15 to F18), one repaired earlier finding (F8). `/phase-status 3` in a Claude Code client: not run by the coder and not run by me; I ran the script itself.
- **F8:** repaired (rev 6), with the evidence under F8. F9, F10 and F12 are not reopened (owner deferrals); F14 is unchanged. Earlier repaired findings (F1 to F7, F11, F13): no regression found: the bundle test suite, which pins their wording, passes (2078), the nine installed copies equal their sources, and the two greps of Tasks 1 and 3 print nothing.
- **Completion checklist (plan lines 324 to 329):** four of six lines ticked and true (all tasks `[x]`; lint ok; bundle and server tests pass, re-run here; no `[~]`). Two are not ticked: "Level aimed at: mergeable" (the owner's) and "Summary note added by the coder" (the coder's closing step). `/phase-status 3` itself reports these two as open.
- **Verification lines of each checkpoint, whole branch:** CP1 to CP3 and CP7 were reviewed in revisions 1 to 5 (their gates then); today's re-run of lint and the bundle tests passes on the final commit, and the CP4 line ("the script run twice prints the same list; the gates with counts") is met. Items that live outside the files stay unchecked by me: the owner's tick of the Task 1 to 4 diff and of `BRANCH_RULES.md`, the owner's confirmation of the docs-only CI finding, and every CI result (CI was not read).
- **INT-26 outcomes (the proposed outcome list), met in the files:**
  1. three text fixes by the light path: met (F4, F5, F1 repaired; greps clean); the human tick is in the pull request: cannot tell.
  2. one home per fact: met (`REVIEW_CYCLE.md` "Where each fact is recorded"; F6 repaired).
  3. definition of done with levels: met (`REVIEW_CYCLE.md` "Definition of done"; the coordinator's report names the level; never declares done).
  4. deterministic phase status: met (read-only script, Claude command with `allowed-tools: Bash(python3 *)`, Copilot prompt file with its limits stated, skills instruction line marked unverified). What is not shown: a run of the command in a client, and the Copilot prompt in the Local harness.
  5. ceremony scaled to risk: met (light path, solo only, never code, rules, permissions, hooks or tests).
  6. fewer, clearer human steps: met in the PR template ("What remains for you", "Decisions for you", ready check) and the coordinator text; no real pull request read.
  7. self-contained asks: met in the rule and in the installed `AGENTS.md` block and agent definitions.
  8. branch rules written and compared: met in text (`docs/process/BRANCH_RULES.md`, coordinator "Branch rules" section); the ruleset and `.github` were not changed; unverified rows are marked.
  9. reduce CI repeats: investigation only, recorded in `BRANCH_RULES.md`; no workflow change, as the intent says.
- **INT-26 scenario seeds:** S1 template met, a real description not read; S2 met; S3 met (same output twice, each open item named with its file, the script only reads; F15 is about keeping that true); S4 met; **S5 partly met by the owner's decision:** no repository commit is needed to record CI (met), but the seed's "a later commit that does not change code needs no second confirmation" is not what the shipped text says: item 3 now says every commit gets its own read and tick (round 2 amendment, F5 repaired at the owner's decision). Not a defect; the seed and the shipped rule differ, and the owner chose the rule. S6 met in text, no sample of real asks; S7 met (three findings fixed, kinds of change listed, solo only; human tick in the PR); S8 met in text, the unverified rows named; S9 met in text, no sample of a phase run.
- **Standard for documents:** (a) traceability: each Task 15 to 18 acceptance line maps to a file, a test or a command run above; (b) consistency: installed copies equal sources (F8), HOWTO item 6, the shipped prompt, the instruction line and the Task 15 note agree; (c) verified claims: command syntax rests on the coder's reading of the Claude Code and VS Code pages (not re-read by me), unverified items marked (F16, F17 name two); (d) behavior: no evidence yet (no client run of `/phase-status`, no real pull request using the new template, no real use of the standing CI-write permission); (e) lint and tests run above; (g) owner approval: plan approved with three amendments.
- **Nit cap:** four new Nits (within the cap of 5).

## Could not check

- Rev 6: CI for `07d580d` and `6716af3` (CI was not read; no `gh` call by me); `install.py --status` and the twice-built zip equality (not built by me); the failing-first run of Task 17 (the coder's note only); `/phase-status 3` in a Claude Code client and the Copilot prompt in VS Code (not invoked); the three WebFetch pages the coder read (not re-read, so the command and prompt syntax rest on the coder's note, and the permission-matching behavior in F17 is unverified); whether the owner ticked anything in the pull request or read `BRANCH_RULES.md`; the coder's transcript and shell history for CP4.

- Rev 5: the failing-first run of Task 27 (reasoned from the old text, not rebuilt); the coder's transcript and full `gh` call list; CI for `1ccf6ae` (no `gh run` read); `install.py --status`; the twice-built zip equality; whether the owner has ticked anything in the pull request.

- The failing-first run of Task 5 on the old files (F2).
- The coder's own shell history and the guard's behavior during Task 6.
- CI for the commit reviewed; `install.py --status` and the install itself (not rebuilt).
- Whether the owner has read and ticked the Task 1 to 4 diff in the PR.
- Rev 2: the failing-first run of Task 21 (coder's note only); `install.py --status` (guard refusal of my unzip step); CI for `eea5424`; the coder's shell history for the repair.

- Rev 3: the failing-first run of Task 10 (F10); the coder's transcript and shell history for CP2; the twice-built zip equality and `install.py --status`; CI for `30e88bd`; whether the owner has read and ticked anything in the pull request.

- Rev 4: the failing-first runs of Tasks 14 and 26 (coder's notes only); the coder's transcript and the full `gh` call list for CP3; CI for `db37ef6` and `815baa3` (no `gh run` read made); `install.py --status`; whether the owner has ticked anything in the pull request; the text of the refused command in the guard log (truncated).

## Rule exceptions (this review)

Rule exceptions (rev 6): two of my commands were refused by the guard and I did not retry them another way. (1) A Bash command with a heredoc (`bash -c '... <<EOF ...'`, to loop `cmp`), refused by rule `no-heredocs`; it ran nothing and I redid the checks with plain `cmp` calls and `python3 -c`. (2) A Write of a scratch script to the session scratchpad, refused by rule `write-allowlist` (the reviewer may write only `docs/plans/REVIEW_PLAN_<N>.md`); nothing was written and I used `python3 -c` one-liners instead (read-only). Both are the last two lines of `.manifold/guard-log.jsonl`. Beyond those: no file written from a shell command, no commit, push or staging, no `gh` call; the server tests and `tests/live` were run with `-p no:cacheprovider` (no cache written); Edit used only on this file.

Rule exceptions (rev 5 and earlier): none by me in rev 5 (no shell write, no refused command; Edit used only on this file; my one `gh api --method GET` call was read only). Rev 4: no shell write and no refused command; Edit used only on this file; my `gh api --method GET` calls were read only). The earlier refusals of rounds 1 and 2 are listed above.

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above.
