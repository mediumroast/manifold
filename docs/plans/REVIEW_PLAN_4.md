# REVIEW_PLAN_4.md

**Phase:** `docs/plans/PHASE_4_PLAN.md`, checkpoint 1 only (Tasks 1 to 13, "Clear instructions in the pull request") and its owner-approved "Review amendment (round 1)" (Tasks 41 to 56). Checkpoints 2 to 6 are not part of this change and are not reported as missing.
**Intent:** INT-27, `intent/INT-27-clear-human-instructions-in-the-pr.md` (it has scenario seeds S1 to S7; there is no S8)
**Commit reviewed:** `1bf3836550ffd37ea0bae9f4aff3e33898327361` on branch `claude/phase-4-cp1` (pull request 35; base `claude/phase-4-plan` at `c6b059e92a8a5e4b725ec5f651e233b60b93ee86`; full change `c6b059e..1bf3836`, 36 files; repairs since revision 1 `3724f88..1bf3836`, 11 commits, 24 files). The head came from `git rev-parse HEAD` after `git log -3`.
**Plan version:** `PHASE_4_PLAN.md`; the plan is approved by Michael Hay on Nov 14, 2026, and the review amendment (round 1) is approved by him (`**Amendment approved by:** Michael Hay on Nov 14, 2026`, commit `da496ef`, the owner's edit). Task 55 is owner-gated (see F4) and was deliberately not run.
**Policy used:** `REVIEW.md` (passes, Important and Nit meaning, nit cap of 5 per report). The `Review process` approval rule in `AGENTS.md` (solo repository, owner Michael Hay, no second approver) applies: no second person is required, and the owner's approval is his own. GitHub's own Approve review is a separate act and is not something this file can show.
**Revision:** 11, 2026-11-23 (CP4 Task 31, the coder's note in commit `7a25b93`, and failure entry F30 in commit `aea23c9`, branch `claude/phase-4-cp4c`; revision 11's header is its own section, "CP4 revision 11"). Earlier revision line, kept as history: 10, 2026-11-22 (CP11, Task 75 and the owner's Task 28 row, commits `500ec9b` and `aa5301c`, branch `claude/phase-4-cp4b`, round 7 amendment signed by Michael Hay on Nov 22, 2026; revision 10's header is its own section, "CP11 revision 10"). Earlier still: 9, 2026-11-22 (CP11, Task 74, the Step 0e rewrite of the owner's Megaroast setup guide, commit `1b2833b`, branch `claude/phase-4-cp4`, round 6 amendment signed by Michael Hay on Nov 22, 2026; the header fields above this line describe checkpoint 1 as of revision 2 and are kept as history; the checkpoint 2 header is the next block, then the revision 4, 5, 6, 7 and 8 headers; revision 9's header is its own section, "CP11 revision 9")

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

**Revision 5 header.**
- **Commit reviewed:** `559810201389a7eb763d592598932bde157c47c7` (`git rev-parse HEAD`, "Record F25..."), branch `claude/phase-4-cp2`. Since revision 4 (`9a28de7`, `git diff 9a28de7..HEAD --name-status`): `eec2f60` (the planner's fix of F18 and F19), `36063b4` (revision 4 of this file), `ee9f170` (failure entry F23), `f1084e1` (INT-2 release rule, owner's S2 decision), `789711c` (F24), `d0ac219` and `6b0c57f` (the round 3 amendment and the owner's signature), `f35fb11` (the CP9 repair, 3 files in `server/tests/contracts/` plus the plan), `5598102` (F25).
- **Plan version:** `PHASE_4_PLAN.md`, "Review amendment (round 3, checkpoint 2: CI failure)", Tasks 63 to 65, `**Amendment approved by:** Michael Hay on Nov 15, 2026` (commit `6b0c57f`). Here the signature came before the repair (`6b0c57f` before `f35fb11`), as `REVIEW_CYCLE.md` asks. Task 22 stays `[~]`, by the owner's decision (INT-2 S2 release rule, Nov 15, 2026; `intent/INT-2-test-hardening-and-contracts.md`, "Release rule while open").
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Not my work:** I wrote none of the code or plan text under review (the repair is the bug-coder's).

**Revision 6 header (checkpoint 3).**
- **Phase:** `docs/plans/PHASE_4_PLAN.md`, "CP3 — Curated test data sets (INT-3)", Tasks 23 to 27. Checkpoints 4 to 6 are not part of this change and are not reported as missing.
- **Intent:** INT-3, `intent/INT-3-test-data-sets.md` (`accepted_by: Michael Hay on Nov 14, 2026`). S2 (hostile text) is Tasks 23, 24, 25 and 27; S3 (a real source is scrubbed) is Task 26 (Tasks 28 and 31 are CP4); S1 is deferred by the owner (Open question 17) and is not reported as missing.
- **Commit reviewed:** `85b52a2de1499db4e4003556d59093a975fdda46` ("Record F28 ...", `git rev-parse HEAD`), branch `claude/phase-4-cp3`; diff `origin/main..HEAD` is 6 commits plus the F27 commit (`1325306` failure F27, `1e4255c` Task 23, `1a9b168` Task 24, `aa31901` Task 25, `3e1e898` Task 26, `ff45935` Task 27, `85b52a2` failure F28), 26 files, 755 insertions, 5 deletions; 24 files are created (all under `server/tests/datasets/`) and 2 are modified (`docs/plans/PHASE_4_PLAN.md`, `docs/agents/claude-desktop-failures.md`). The branch is not pushed, so CI has not run.
- **Run reviewed:** this is the coder's second CP3 run. The first run is set aside on `claude/phase-4-cp3-run1`; I did not read it and it is not under review.
- **Plan version:** `**Approved by:** Michael Hay on Nov 14, 2026` (`PHASE_4_PLAN.md:3`); amendments signed.
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Not my work:** I wrote none of the code, data or plan text under review.

**Revision 7 header (checkpoint 3 repair, CP10).**
- **Phase:** `docs/plans/PHASE_4_PLAN.md`, "Review amendment (round 4, checkpoint 3: scan output)", Tasks 66 to 72 (CP10). Checkpoints 4 to 6 are not part of this change.
- **Commit reviewed:** `f9ead7d81128d6ae1fe56f08c6f1fb659f3402c9` (`git rev-parse HEAD`), branch `claude/phase-4-cp3`, draft pull request 37. Since revision 6 (`85b52a2`): `32cde84` (revision 6 and failure F29), `b2bad35` (the planner's round 4 amendment), `0df5d0d` (the owner's answers to Open questions 1 and 2), `7df5d38` (the owner's signature), `7ef9f3d` (the coder's code, test and README changes, Tasks 66 to 70), `f9ead7d` (the coder's plan notes, Tasks 71 and 72). `git diff --stat 85b52a2..HEAD` is 6 files: `server/tests/datasets/README.md`, `scan.py`, `test_datasets.py`, `docs/plans/PHASE_4_PLAN.md`, `docs/plans/REVIEW_PLAN_4.md` and `docs/agents/claude-desktop-failures.md`; nothing under `server/` outside `server/tests/datasets/`.
- **Plan version:** `**Amendment approved by:** Michael Hay on Nov 21, 2026`. Order in git: amendment (`b2bad35`), answers (`0df5d0d`), signature (`7df5d38`), then the code (`7ef9f3d`): the signature came before the repair, as `REVIEW_CYCLE.md` asks. The owner decided F28 (option 2: no matched text for any kind), Open question 1 (yes) and Open question 2 (no) in chat; I cannot read the chat, so I rely on the plan's record of it.
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Not my work:** I wrote none of the code or plan text under review (the repair is the coder's).

**Revision 8 header (CP11, the owner's setup guide).**
- **Phase:** `docs/plans/PHASE_4_PLAN.md`, "Review amendment (round 5, checkpoint 4: owner's setup guide)", Task 73 (CP11), and the Correction, Effect and six answered Open questions of that amendment. Read against INT-3 and Concerns 7 to 9. Tasks 28 to 35 are the content source; they are not themselves under review (CP4 and CP5 are the owner's acts and not run yet).
- **Commit reviewed:** `408e86fb` (`git log` head, "Phase 4 CP11 Task 73 ..."), branch `claude/phase-4-cp4`; diff `origin/main..HEAD` (`7ba6e3b`) is 4 files, 118 insertions, 1 deletion: `docs/megaroast-setup.md` (new, 60 lines), `docs/README.md` (+1 row), `server/tests/test_docs_links.py` (one list entry), `docs/plans/PHASE_4_PLAN.md` (+56). Four commits: `82d5bf2` (first round 5 text), `b76cba4` (rewritten for a from-scratch setup), `1b23c92` (the owner's answers), `756e3b0` (the owner's signature), then `408e86f` (the coder). The signature came before the coder's work, as `REVIEW_CYCLE.md` asks.
- **Plan version:** `**Amendment approved by:** Michael Hay on Nov 22, 2026`. The approved plan itself is Michael Hay, Nov 14, 2026.
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Not my work:** I wrote none of the guide, test or plan text under review (the coder did).

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-14 11:30 | `9895935fd181510832d889c9353a3391266aea71` | First review (checkpoint 1): F1 to F9 |
| 2 | 2026-11-14 12:12 | `1bf3836550ffd37ea0bae9f4aff3e33898327361` | Re-review of the repairs of the amendment (Tasks 41 to 56): State of F1 to F9 set from evidence; new findings F10 and F11 |
| 3 | 2026-11-15 14:40 | `d3411a39c4def8d4fc660bc1788d9879600c9e32` | First review of checkpoint 2 (Tasks 14 to 22): new findings F12 to F17; the checkpoint 1 findings are not re-reviewed and keep their revision 2 State |
| 4 | 2026-11-15 14:55 | `9a28de75eead69b45f4de34a49bced3f3b9883ea` | Re-review of checkpoint 2 and its repair (Tasks 57 to 62): F12 to F17 all repaired (evidence below); new findings F18 and F19 (nits, process record); the failure entries F21 and F22 checked against the guard log; CP1 findings F4, F9, F10, F11 not re-reviewed, state unchanged |
| 5 | 2026-11-15 20:40 | `559810201389a7eb763d592598932bde157c47c7` | Review of the CP9 repair (Tasks 63 to 65, commit `f35fb11`, tests only): no Important finding; new nits F26 and F27; F18 and F19 re-checked and repaired; failure entries F22 to F25 checked against the guard log (13 lines); CP1 findings F4, F9, F10, F11 not re-reviewed, state unchanged |
| 6 | 2026-11-21 | `85b52a2de1499db4e4003556d59093a975fdda46` | First review of checkpoint 3 (Tasks 23 to 27, the coder's second run): one Important (F28) and four nits (F29 to F32); failure entries F27 and F28 checked against the guard log (15 lines when I started); the seven recorded deviations judged; the checkpoint 1 and 2 findings (F4, F9, F10, F11, F26, F27) not re-reviewed and keep their State. Review finding numbers F28 and later are review findings; they are not the failure entries F26 to F28 of `claude-desktop-failures.md` |
| 7 | 2026-11-21 | `f9ead7d81128d6ae1fe56f08c6f1fb659f3402c9` | Review of the checkpoint 3 repair (CP10, Tasks 66 to 72): F28 (Important) and F29 to F32 (nits) all repaired, evidence below; one new nit (F33, date convention in the amendment); failure entry F29 and the coder's CP10 and CP3 Rule exceptions lines checked against the guard log (17 lines before and after my commands); the checkpoint 1 and 2 findings (F4, F9, F10, F11, F26, F27) not re-reviewed. Review finding numbers F28 and later are not the failure entries F26 to F29 of `claude-desktop-failures.md` |
| 8 | 2026-11-22 | `408e86fb` | Review of CP11 (Task 73, the owner's Megaroast setup guide): no Important finding; five new nits (F34 to F38) and three more not itemized; the guide checked point by point against Tasks 28 to 35 (holds); the coder's Rule exceptions `none` compared with the guard log (17 lines before and after); F4, F9, F10, F11, F26, F27, F33 carried forward unchanged. Review finding numbers F34 and later are review findings |
| 9 | 2026-11-22 | `1b2833b4fc54c0284dac7101e02a3e5d848c6994` | Review of CP11 Task 74 (the Step 0e rewrite, round 6 amendment): no Important finding; the nine points of "How Step 0e reads" all present and acceptance (a) to (f) reproduces; three new nits (F39 to F41); F34 to F38, F4, F9, F10, F11, F26, F27, F33 and the 3 not itemized carried forward unchanged; the owner's "missing steps" gap is settled in substance, with two residual gaps (F39); the coder's Rule exceptions `none` compared with the guard log (17 lines before and after). Review finding numbers F34 and later are review findings |
| 10 | 2026-11-22 | `aa5301c43261c48710b0bf3b937f2c0097bae39b` | Review of CP11 Task 75 (the SIGNOFFS table, commit `500ec9b`) and the owner's Task 28 row (commit `aa5301c`): no Important finding; five new nits (F42 to F46); the seven columns, the Instructions line, README line 38 and guide Steps 1 and 2 match the round 7 amendment; all gates re-run; all earlier open findings carried forward unchanged. Review finding numbers F34 and later are review findings |
| 11 | 2026-11-23 | `aea23c9cf7c7b28179c725143de21f10476dba94` | Review of CP4 Task 31 (the coder's note, commit `7a25b93`) and failure entry F30 (commit `aea23c9`): one Important (F47, a real repository name in the plan note) and two nits (F48, F49); the note's facts re-checked against what I could reproduce; F30 matches guard-log line 18; the Todo is unticked; nothing from the scratch clone reached this repository; all gates re-run; all earlier open findings carried forward unchanged. Review finding numbers F34 and later are review findings; F30 here is the failure entry, not a review finding |

## Counts by severity

| Severity | Open | Repaired |
|---|---|---|
| Important | 2 (F4, owner-gated, checkpoint 1; F47 new in revision 11) | 5 (F1, F2, F3; F12 repaired in revision 4; F28 repaired in revision 7) |
| Nit | 21 (F9, F10, F11 from checkpoint 1; F26, F27 from revision 5; F33 from revision 7; F34 to F38 from revision 8; F39 to F41 from revision 9; F42 to F46 from revision 10; F48, F49 new in revision 11) plus 3 not itemized (nit cap, from revision 8) | 15 (F5, F6, F7, F8; F13 to F17 repaired in revision 4; F18, F19 repaired in revision 5; F29 to F32 repaired in revision 7) |

No finding is shown as deferred or rejected by me. The plan's "Findings not repaired" table for round 4 records two parts as deferred (the longer first-name list, and widening the scan to bare hosts); the owner signed the amendment with that table and answered Open question 2 no, so those two parts are the owner's decisions, and F30 and F32 are repaired in the parts the owner approved. The nit cap (5) applies per review: revision 3 reported five new nits and left none out; revision 4 two; revision 5 two; revision 6 four; revision 7 one.

Revision 11's own section comes first, under "CP4 revision 11" (Task 31 and failure entry F30). Revision 10's section follows, under "CP11 revision 10" (Task 75 and the Task 28 row). Revision 9's section follows, under "CP11 revision 9" (Task 74). Revision 8's section follows, under "CP11 revision 8". Revision 7's section follows, under "CP3 revision 7". Revision 6's sections follow, under "CP3 revision 6" (their State lines for F28 to F32 are updated in place with the revision 7 evidence). The sections for revisions 3 to 5 follow, unchanged.

The sections headed "CP2: ..." further down are the revision 3 text, kept; their State lines for F12 to F17 are updated in place with the revision 4 evidence. Revision 4's own sections come under "CP2 revision 4" (F18 and F19 keep their text there, with the State set in revision 5). Revision 5's own sections come first, under "CP2 revision 5".

## CP4 revision 11: the Task 31 note and failure entry F30

**Header (revision 11).**
- **Phase:** `docs/plans/PHASE_4_PLAN.md`, Task 31 "Check the example instance from a scratch clone" (`:589`; Change `:595`, Acceptance `:596`, Todo `:597`, the coder's Note after it). Read against INT-3 (no real content, nothing committed here, the owner's private terms file never read or printed).
- **Commits reviewed:** `7a25b93` (the coder: `docs/plans/PHASE_4_PLAN.md`, 8 insertions) and `aea23c9` (the coordinator: `docs/agents/claude-desktop-failures.md`, 12 insertions, entry F30). Head `aea23c9cf7c7b28179c725143de21f10476dba94` (`git log`), branch `claude/phase-4-cp4c`, working tree clean before and after my commands.
- **Plan version:** `**Approved by:** Michael Hay on Nov 14, 2026` (`PHASE_4_PLAN.md:3`); Task 31 is "unchanged" by the later amendments (`:1239`).
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Not my work:** I wrote none of the note or the failure entry. I did not read `~/.manifold/excluded_terms.json` and read no held-out scenario.

### Verdict (revision 11)

One Important finding (F47) and two nits (F48, F49). The note covers all four parts of the acceptance line (commands, healthy, component count, scan count per kind), the facts I could reproduce hold, the Todo and the task header stay unticked, nothing from the scratch clone is in this repository, and F30 matches guard-log line 18. The Important finding is a real repository name in the committed note, which the plan says not to write until the owner supplies names.

### Checks asked for

| Check | Result | Evidence |
|---|---|---|
| Acceptance: commands recorded | holds | Note bullets: clone, the "Without Docker" route, the four admin steps, the server start with `PORT=8699`, `curl -s http://127.0.0.1:8699/health`, the MCP inventory call, the `scan.py` command with `--terms-file` |
| Acceptance: health healthy | holds, as written | `{"status":"healthy"}` from the `/health` endpoint. I could not reproduce it (server stopped, credential deleted, as the note says). `server/server.py:936` shows `/health` calls `wiki_health(WIKI_ROOT)` and returns `"status"`, so the claim is consistent with the code |
| Acceptance: component count (owner expects two) | holds as written; not reproduced | Note: 2 components (`example-api`, `example-web`), 1 handoff, 7 files. The plan's own provenance (`:1297`) says the example instance has `example-api` and `example-web`, one handoff, and nine tracked files; 7 inventory files plus `README.md` and `manifold.yaml` is nine, so the numbers agree |
| Acceptance: scan count per kind | holds as written | "`scan: no findings`: 0 findings of every kind, including the terms kind", with the terms file passed by path only. I did not re-run it on the clone, because that needs the owner's terms file, which I must not read |
| Acceptance: `git status --short` in this repository unchanged | holds | `git status --short` prints nothing at the head; `git diff 7a25b93~1 aea23c9 --stat` is the two files above |
| Clone untouched | holds | The scratch clone (`<scratchpad>/testbed-clone`): `git status --short` prints no line, 14 commits, 9 tracked files (the same numbers as the Note and as `:1297`) |
| Production containers untouched | holds as far as I can see | `docker ps` now: `manifold-production Up 19 hours (healthy)` and `manifold-caddy-production Up 19 hours 127.0.0.1:8686->8686/tcp`. The note says `Up 19 hours` before and after; I saw only the current state, so "before" is the coder's word |
| Scratch server stopped | holds | `lsof -nP -iTCP:8699 -sTCP:LISTEN` prints nothing |
| Throwaway credential deleted | holds | the scratch data folder holds only `manifold.db`, `manifold.db-shm`, `manifold.db-wal`; no `*.secret` file anywhere in the scratchpad listing |
| Todo and task header unticked (owner's) | holds | `PHASE_4_PLAN.md:597` is `**Todo:** [ ]`; the header at `:589` has no tick |
| No secret, credential, repository content, URL or email-shaped text in the diff | holds, except one name (F47) | Added lines searched for `@host.tld` and `https?://`: the only match is `http://127.0.0.1:8699/health`, a local loopback address, not a repository URL. No credential text, no file content from the clone, no commit hash or author of the clone. The one real name is F47 |
| Nothing from the clone reached this repository | holds | `grep -rIl` for the repository name (not repeated here) over the worktree (without `.git`, `.venv`) finds only `PHASE_4_PLAN.md` (the note) and this file (after my edit); `git diff 7a25b93~1 aea23c9` touches the two files above only |
| Plan wording about `wiki_health` | see F48 | |
| F30 against `.manifold/guard-log.jsonl` line 18 | holds | The log has 18 lines (`wc -l`, before and after my commands). Line 18: `2026-11-23T14:04:42Z`, rule `no-heredocs`, tool `Bash`, agent_type `coder`, the command text beginning with a shell variable assignment (`S=/private/tmp/...`). The commit `7a25b93` is stamped 06:05:24 -0800, which is 14:05:24Z, about 40 seconds after the log line. The entry's date, rule, agent and count ("1 attempted, 1 refused") match. The log is git-ignored (`git check-ignore` prints the path), so the line cannot be checked from the commit alone |
| F30 against the coder's "Rule exceptions: none" wording | partly compared; see F49 | The coder's report was not given to me as text; I compared with what the entry says about it. The plan Note does not hold a "Rule exceptions" line; its last bullet states the refused attempt in plain words, and that matches F30's account (not worked around; started as a background command without a redirect) |

### Gates, run by me (head `aea23c9`, Python 3.11)

| Command | Result |
|---|---|
| `cd server && ../.venv/bin/python -m pytest -q` | `1146 passed, 5 xfailed, 33 warnings in 136.65s` (equals revision 10) |
| `.venv/bin/python -m pytest server/tests/test_docs_links.py -q` | `12 passed in 0.02s` |
| `python3 bundles/base/tools/build.py --check` | `lint ok` |

### New findings in revision 11

**F47 (Important) — The Task 31 note names the real repository (`<ORG>/<repo>` is the plan's rule), and the plan says to write roles until the owner supplies names**
- **Pass:** Compliance (the plan's rule on names) and Security (INT-3: no real content or names committed).
- **Location:** `docs/plans/PHASE_4_PLAN.md` Task 31 Note, the "Clone:" bullet (the first line after the `**Note:**` line, about `:599`): the full `gh repo clone <organization>/<repository name> ...` text with the real organization and the real name of the example instance repository (the note is the only place in the plan that has the repository name; it was 0 matches at `7a25b93~1`).
- **Evidence:** `git show 7a25b93` added line; `git show 7a25b93~1:docs/plans/PHASE_4_PLAN.md | grep -c <the repository name>` prints `0`. The plan says: Task 28's lead paragraph (`:548`): "The owner permits naming the repositories (Open question 18) but has supplied no names; until the owner supplies them, rows and notes use the role names"; the Task 30 acceptance (`:645`) "No names or IDs in the note until the owner supplies repository names (Open question 18)"; the CP4 gate (`:122`) "permission to name the repositories is given, no names are supplied"; the round 7 amendment's Tasks 29 and 30 notes use `<ORG>/<name>`; Task 31's own plan text in the CP4 checklist uses `<ORG>/<repo-name>`. The owner's answer to Open question 18 ("It is ok to name it since the intention is to eventually provide a public demonstration") gives permission, which the plan reads as permission without names. The commit message and Note do not say the owner supplied the name. The name is of a repository the owner made fresh (it holds no company content, `:1238`), which lowers the harm; it does not remove the departure from the plan, and the name now sits in a file that will be public.
- **Direction:** replace the real name in the note with the role text and `<ORG>/<repo-name>` (as Tasks 29 and 30 do), or, if the owner has supplied the name for the record, say so in the note and in Open question 18's answer, so that the departure is the owner's decision. The commit stays as history; a new commit repairs it.
- **State:** open

**F48 (Nit) — The plan's Task 31 Change line still says `wiki_health` is a tool; the coder found it is the `/health` endpoint, and the plan is wrong, not the coder**
- **Pass:** Bugs (consistency; the plan misleads a later reader).
- **Location:** `docs/plans/PHASE_4_PLAN.md:595` ("then call `wiki_health` and `wiki_inventory_tool`") and Acceptance `:596` ("health reports healthy"); the Note's "Health:" bullet.
- **Evidence:** `server/server.py:36` imports `wiki_health` from `wiki_backend.health` and `:936` calls it inside the `/health` handler; it is a Python function, not a registered MCP tool (the Note says an MCP call returned `Unknown tool`; I did not call it, the server being stopped). The same name is used correctly as a function in Task 9 (`:494`, "`wiki_health` reports healthy" in a test) and the guide. So the Task 31 Change line used a tool-style name by mistake; the Acceptance line (health reports healthy) is met through the endpoint. The coder recorded this in the Note and did not edit the Change line, which is right (the plan is the planner's text).
- **Direction:** the planner (not the coder) corrects the Change line by a one-line amendment ("check the `/health` endpoint, then call `wiki_inventory_tool`"), signed by the owner; no change to the note.
- **State:** open

**F49 (Nit) — F30's "Rule exceptions" argument and its Status line**
- **Pass:** Compliance (the Rule exceptions line must say what happened; a refused command is listed, not hidden) and Bugs (consistency of the entry).
- **Location:** `docs/agents/claude-desktop-failures.md` entry F30, "What happened" (last sentence) and "Disclosed by the agent".
- **Evidence:** the entry says the coder's line said `none` and then described the refused attempt in the same line, and says a refused command "is a flagged attempt, not an exception granted". That reading is the entry's own; `AGENTS.md` ("Rule exceptions") says "If you are unsure whether something was an exception, list it", which points to listing the refused attempt, and the coder did list it (in the report) while writing `none`. The two statements are the inconsistency; the entry records it and sets `Status: closed` with "Transcript not compared". I could not compare the coder's report text, and the Note in the plan has no Rule exceptions line to compare.
- **Direction:** nothing to change in the entry's account; the owner decides whether to make the coder's wording rule explicit ("a refused command goes on the line"), as the entry already leaves it open under "Suggested change".
- **State:** open

### Rule exceptions

The coder's line, as given to me for this review, is `none`, with the refused redirect attempt described in the report body. Compared with the diff (`7a25b93`: the plan only, the Task 31 note; `aea23c9`: the failures file only), the commit log (two commits, trailers present, no hook bypass visible) and `.manifold/guard-log.jsonl` (18 lines before and after my commands; line 18 is the coder's refused `no-heredocs` attempt): the diff and the log agree with F30; the word `none` against the one refused attempt is the mismatch recorded in F49. Not compared: the coder's transcript, and the exact report text (I was given its content by the caller, not the report itself). My own commands: read-only `git`, `grep`, `ls`, `lsof`, `docker ps`, `cat` of a task output file, and the three gate commands; none was refused; the only file I wrote is this one.

### What I could not check

The note's health, component-count, handoff and file numbers on the live server (stopped; credential deleted); the scan on the clone with the owner's terms file (I may not read it); that the production containers were `Up 19 hours` before the run (only the current state is visible); the coder's report text and transcript; whether the owner supplied the repository name in chat (F47); real-use evidence of the owner reading the Task 31 note and ticking the Todo ("no evidence yet").

### Summary

One Important finding (F47), two nits (F48, F49); nothing repaired in this revision; all earlier open findings (F4, F9, F10, F11, F26, F27, F33 to F46 and the 3 not itemized) carried forward unchanged. Gates: server tests 1146 passed, 5 xfailed; docs links 12 passed; build lint ok. A human decides; these findings do not approve or block the change.

## CP11 revision 10: the SIGNOFFS table (Task 75) and the owner's Task 28 row

**Header (revision 10).**
- **Phase:** `docs/plans/PHASE_4_PLAN.md`, "Review amendment (round 7, checkpoint 4: the SIGNOFFS table and Task 28)" (`PHASE_4_PLAN.md:1311` onward), Task 75 (CP11), the Task 28 text (`:550`), and the Task 29 and 30 notes. Read against INT-3 (the permission, no-real-content and "nothing committed here" constraints).
- **Commits reviewed:** `500ec9b` (the coder, Task 75: `docs/megaroast-setup.md`, `docs/plans/PHASE_4_PLAN.md`, `server/tests/datasets/README.md`, `server/tests/datasets/SIGNOFFS.md`; 12 insertions, 8 deletions) and `aa5301c` (the Task 28 row; `git show --stat` lists `server/tests/datasets/SIGNOFFS.md` only, 3 insertions, 2 deletions). Head `aa5301c43261c48710b0bf3b937f2c0097bae39b` (`git rev-parse HEAD`), branch `claude/phase-4-cp4b`, working tree clean. Diff from `922549e`: 4 files.
- **Plan version:** `**Amendment approved by:** Michael Hay on Nov 22, 2026` (commit `d1a5a78`, before the coder's `500ec9b`: the signature came first, as `REVIEW_CYCLE.md` asks).
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Not my work:** I wrote none of the table, README, guide or plan text under review.

### Verdict (revision 10)

No Important finding. Five new nits (F42 to F46). The table has seven columns in the amendment's order, the Instructions line says what Task 75 (b) lists, README line 38 and guide Steps 1 and 2 carry the amendment's wording, and no URL, address-shaped text or real repository name is in the diff. The earlier open findings (F4, F9, F10, F11, F26, F27, F33 to F41 and the 3 not itemized) are not touched by these commits and keep their State.

### Checks asked for

| Check | Result | Evidence |
|---|---|---|
| Seven columns, amendment's order | holds | `SIGNOFFS.md:11`: Source, Owner, Permission date, Visibility, Nothing committed here, Scrub checked by, Scan result; equals Provenance (4) of the amendment. The separator at `:12` has seven cells, the row at `:13` has seven cells |
| The row was written by the owner; the coder's commit filled no cell | holds as far as git shows; see F46 | `git show 500ec9b` for `SIGNOFFS.md` adds only header, separator and the Instructions line (the table has no row); `aa5301c` touches `SIGNOFFS.md` only. I cannot see who typed the row; see F46 |
| Row content | holds | Source by role ("Copy with history of the company repository"), owner, date `Nov 22, 2026`, `Private`, "Yes, nothing committed here"; Visibility is private, so Task 28's stop rule does not fire |
| Stale sentence "The table has no rows yet." | present at `SIGNOFFS.md:7`, now false | F43 |
| Task 75 header ticked by the coder | yes, `PHASE_4_PLAN.md:1326` is `- [x]` from `500ec9b` | F42. Convention check: `git log -S'- [x] **Task 73'` finds only `922549e`, the owner's commit (author Michael Hay); Task 74 at `:1294` is `- [ ]`. So the owner ticks the task header |
| Task 29 and 30 notes: roles only, no names; headers and Todos unticked | holds | `PHASE_4_PLAN.md` Task 29 and Task 30 notes use `<ORG>/<name>` and roles; both `**Todo:** [ ]` lines are unchanged; no `###` header is ticked. See F44 for scope |
| No real repository name, URL or email-shaped text in the diff | holds | `git diff 922549e aa5301c`, added lines, searched for URLs, `@host.`, `github.com`, `company_dns`, `mediumroast`, `testbed`: only a match inside the coder's own Note text that quotes the acceptance grep command (it names `company_dns`, `testbed`, a pattern, no repository name); address and URL grep on the guide, README and `SIGNOFFS.md` prints nothing. "Megaroast" is in the Instructions line (`:9`) as the organization word the plan already uses (see F35) |
| README line 38 | holds | `README.md:38` reads "...: source, owner, permission date, visibility, nothing committed here, who checked the scrub," then `scan result.` on line 39; nothing else changed in the file (`git diff` hunk is 2 lines) |
| Guide Step 1 and Step 2 | hold | `megaroast-setup.md:56-57` carry the amendment's wording ("one row, for the copy with history (the other repositories were created fresh and derive nothing; the standalone UI gets a row if company code is added to it)" and "matching the Step 1 row for the copy; record the other repositories' visibility by role in the note"); the diff hunk is those two lines only |

### Gates, run by me (head `aa5301c`, Python 3.11)

| Command | Result |
|---|---|
| `cd server && ../.venv/bin/python -m pytest -q` | `1146 passed, 5 xfailed, 33 warnings in 159.66s` (equals the coder's Note and revision 9) |
| `cd server && ../.venv/bin/python -m pytest tests/datasets tests/test_docs_links.py -q` | `28 passed, 1 warning in 4.42s` (equals the coder's Note) |
| `python3 bundles/base/tools/build.py --check` | `lint ok` |
| `.venv/bin/python server/tests/datasets/scan.py server/tests/datasets/SIGNOFFS.md --terms-file <empty_terms.json fixture in the scratchpad>` | `scan: no findings`, exit 0 |
| same scan on `docs/megaroast-setup.md` | `scan: no findings`, exit 0 |
| guide box counts: `grep -c "^- \[ \]"` and `grep -c "^- \[x\]"` | `13` and `0` |
| Task 75 acceptance (a) to (c), re-run on the head | (b) Instructions grep `1`; (c) README grep matches line 38; (a) now reads header grep `0`, separator grep `0`, `^|` count `3`: not a defect of the coder's commit, because the owner's row and a table formatter changed the file after the coder ran it (the coder's own tree, `500ec9b`, has the unpadded header and separator; see F45) |

The fixture exists and I did not read it; the owner's `~/.manifold/excluded_terms.json` was not used or read. Held-out scenarios: none read.

### New findings in revision 10

**F42 (Nit) — The coder ticked the Task 75 header, which is the owner's tick by the convention of Tasks 73 and 74**
- **Pass:** Compliance (traceability; the owner's gate).
- **Location:** `docs/plans/PHASE_4_PLAN.md:1326` (`- [x] **Task 75 ...`) from commit `500ec9b`.
- **Evidence:** the commit diff changes `- [ ]` to `- [x]` on the header together with the six Todo boxes. For Task 73 the header tick came in `922549e`, the owner's commit; Task 74's header is `- [ ]` (`:1294`), and the Task 74 Note says the coder left it unticked. Task 75's own text says only "the Todo and Note of Task 75" are the coder's. The tick is the owner's statement that the task is done, and the owner has not yet looked at the result (the Verification line says the owner opens the file).
- **Direction:** the coder (or the owner) sets the header back to `- [ ]`; the owner ticks it after reading the table. The six Todo boxes may stay.
- **State:** open

**F43 (Nit) — "The table has no rows yet." is now false**
- **Pass:** Bugs (consistency).
- **Location:** `server/tests/datasets/SIGNOFFS.md:7`, against the row at `:13` and the Instructions line at `:9` ("There is one row").
- **Evidence:** read. The sentence has been in the file since `7ba6e3b`; the amendment said the table would have no row until Task 28, and Task 75's acceptance (a) wanted exactly 2 table lines, so the coder correctly left the sentence. After `aa5301c` the file contradicts itself.
- **Direction:** delete or re-word the sentence (for example "The table has one row so far") as the owner's edit or by a one-line amendment; not for the coder alone, because Task 28 says the diff shows only table rows.
- **State:** open

**F44 (Nit) — The coder wrote the Task 29 and Task 30 notes in the Task 75 commit; Task 75's text allows no other task's Note**
- **Pass:** Compliance (a changed file region outside the task's inventory; deviation not recorded).
- **Location:** `docs/plans/PHASE_4_PLAN.md` Task 29 note (the line after `**Todo:** [ ]`, about `:571`) and Task 30 note (about `:584`), both added in `500ec9b`; Task 75 text (`:1326`: "Edit no test, no other file, no other task's Todo or Note") and its Files line ("this plan (the Todo and Note of Task 75 only)"); the coder's Note (g): "the three files and this plan only".
- **Evidence:** the diff `500ec9b` shows the two added lines. The content fits the amendment's Effect on Task 29 (visibility of the other repositories recorded by role in Task 29's note) and Task 30's acceptance, and both end "The Todo and this task's tick stay the owner's". But the Task 75 Note does not mention them, and the notes state that the owner ran `gh repo view` and confirmed in chat; I cannot read the chat, so those statements are unverified by me. The owner's instruction may have been given in chat; the plan does not record it.
- **Direction:** record in the Task 75 Note (or the amendment) that the owner asked for the two notes, and by whom the statements were entered; otherwise move them out of the Task 75 commit's record.
- **State:** open

**F45 (Nit) — The Task 28 edit reformatted the header and separator lines, and Task 75's acceptance (a) no longer reproduces**
- **Pass:** Compliance (Task 28 acceptance: "`git diff` shows only table rows") and Tests (acceptance commands).
- **Location:** `server/tests/datasets/SIGNOFFS.md:11-12` (`aa5301c`); Task 28 text (`PHASE_4_PLAN.md:550` onward); the Instructions line `:9` ("Scrub checked by and Scan result are the owner's to fill or to mark as not applicable") against the empty cells at `:13`.
- **Evidence:** `git show aa5301c` rewrites both table header lines with column padding (an editor's table formatter) as well as adding the row; they are table rows, so the Task 28 line holds in the plain sense, but the exact-match greps of Task 75 (a) now print `0`, `0` and `3`. Two cells (Scrub checked by, Scan result) are empty, though the Instructions line says the owner fills them or marks them "not applicable"; a blank cell cannot be told from one not yet written.
- **Direction:** the owner writes "not applicable" in the two cells (or says in the Task 28 note why they are blank), and Task 28's note records that the padding is formatter output. Task 75's acceptance was true at `500ec9b` and needs no change.
- **State:** open

**F46 (Nit) — Who wrote the Task 28 row cannot be shown from git**
- **Pass:** Compliance (the owner's cell must be the owner's; INT-3 permission).
- **Location:** commit `aa5301c` (author `mihay42`, the same identity as `500ec9b`; message "the owner writes the SIGNOFFS row for the copy with history"; trailer `Co-Authored-By: Claude Sonnet 5.5`).
- **Evidence:** the commit touches `SIGNOFFS.md` only, and the padded table looks like a Markdown editor's output (the owner edits Markdown in a rendered editor, per the project's notes); both fit "the owner wrote the row". But the commit identity is shared with the coder's, and the Claude co-author trailer on a commit said to hold the owner's own text could be read as the agent having written the permission statement. The permission date and "Yes, nothing committed here" are the owner's statements for INT-3 and need to be the owner's words.
- **Direction:** the owner confirms in the pull request description or the Task 28 note that he typed the row; the coder or coordinator, who made the commit, drops the co-author trailer from a commit of the owner's text next time, or says in the message that the agent only committed it. No change to the row.
- **State:** open

(The nit cap of 5 per report is reached: five nits reported, none left out.)

### Rule exceptions

The coder's Rule exceptions line in the Task 75 Note is `none`. Compared with the diff (`git show --stat 500ec9b`: the four files Task 75 allows, plus the Task 29 and 30 notes inside the plan, see F44), the commit log (two commits, no hook bypass, staged paths in the message scope) and `.manifold/guard-log.jsonl` (17 lines before and after my commands, unchanged): nothing matched an exception. The Task 28 commit carries no Rule exceptions line; it is the owner's.

### What I could not check

The owner's chat statements behind the Task 29 and 30 notes and the typing of the row (F44, F46); real-use evidence of the owner writing a row unaided ("no evidence yet", because the Task 75 Verification line is the owner's reading of the file); the Task 28 box in the guide stays unticked, and the Task 28 header and Todo stay open in the plan, which is right.

### Summary

No Important finding, five new nits (F42 to F46), nothing repaired in this revision, all earlier open findings carried forward. A human decides; these findings do not approve or block the change.

## CP11 revision 9: Step 0e of the setup guide (Task 74)

**Header (revision 9).**
- **Phase:** `docs/plans/PHASE_4_PLAN.md`, "Review amendment (round 6, checkpoint 4: Step 0e of the owner's setup guide)", Task 74 (CP11, the last task). Read against INT-3 and the nine-point "How Step 0e reads after Task 74" (`PHASE_4_PLAN.md:1288`).
- **Commit reviewed:** `1b2833b4fc54c0284dac7101e02a3e5d848c6994` (`git rev-parse HEAD`), branch `claude/phase-4-cp4`; `git diff HEAD~1 HEAD --name-only` lists two files: `docs/megaroast-setup.md` (+9, -1 in the Step 0e block) and `docs/plans/PHASE_4_PLAN.md` (the Todo and Note of Task 74 only, 2 lines each way). Working tree clean (`git status --short` empty).
- **Plan version:** `**Amendment approved by:** Michael Hay on Nov 22, 2026` (the round 6 text, commit `0977fa7`, before the coder's `1b2833b`: the signature came first, as `REVIEW_CYCLE.md` asks).
- **Policy used:** `REVIEW.md`. The `Review process` approval rule in `AGENTS.md` (solo, owner Michael Hay, no second approver) applies; nothing here needs a second person.
- **Not my work:** I wrote none of the guide or plan text under review (the coder did).

### Verdict (revision 9)

No Important finding. Three new nits (F39 to F41). The nine points are all in the guide, the acceptance results reproduce, the diff is only the guide and the plan, and no full URL, address-shaped text, real name or key was found. F34 to F38, F4, F9, F10, F11, F26, F27, F33 and the 3 not itemized nits of revision 8 are not changed by this commit and keep their State.

### The nine points of "How Step 0e reads"

| # | Point | Result | Evidence |
|---|---|---|---|
| 1 | `init` runs once, from a manifold checkout, one instance, not on the other repositories | holds | `megaroast-setup.md:39` (main line: "runs once", "not run on the other repositories; they are component repositories"; "one box is yours to tick") |
| 2 | Clone manifold outside every checkout and the worktree, address in quickstart section 1 | holds | sub-step 1; `docs/quickstart.md:10-13` has the clone line in "1. Get the code"; the guide writes `<manifold-repo-url>` and no address |
| 3 | Needs: Docker running, Python 3.11 or newer, git, a few minutes | holds | sub-step 2; `quickstart.md:6` says "git; Docker with Compose, running; Python 3.11 or newer" |
| 4 | Pick `--instance` path, parent not in a git repository, `rev-parse` message, stray `.git` left to the owner | holds | sub-step 3. I ran `git -C <a folder outside any repository> rev-parse --show-toplevel` and got `fatal: not a git repository (or any of the parent directories): .git`, the guide's text (the guide writes "fatal: not a git repository" as the start of it; the exact message is the amendment's record) |
| 5 | `./manifold init --instance <path>`, name rules, read the plan and say yes only if it matches, what else it creates, undo on failure, do not clone first, clone-then-copy unverified and not a step | holds | sub-step 4. `./manifold init --help` (run by me, read-only) lists `--instance PATH`, `--name NAME`, `--person-secret-file`, `--agent-secret-file` and `--yes`; it says nothing on clone-then-copy, so "unverified: confirm with `./manifold init --help`" is correct and stays |
| 6 | Never paste the two credential files; they live in the clone's `.manifold-data`, not the instance | holds | sub-step 5; `init --help` shows the data folder default `.manifold-data/<env>`; the two secret-file options exist. Where the two files are written is the amendment's record, not checked by me |
| 7 | Pre-push checks, "as the coordinator ran them Nov 22, 2026": `git ls-files` (nine), scan with an empty terms list, branch, `git log` author check | holds as written; see F39 | sub-step 6; no address-shaped text (the address is described as "a `principals.manifold.invalid` address") |
| 8 | Push with `git remote add origin <new url>` then `git push -u origin <branch>`, recorded as run by the owner and worked; README-or-licence case unverified | holds | sub-step 7 |
| 9 | `gh repo view <ORG>/<repo-name> --json visibility` shows private | holds | sub-step 8; the plan Note says `gh repo view --help` lists `--json`; I did not re-run it against a real repository |

It stays one box (`^- \[ \]` count 13, `^- \[x\]` count 0) with eight plain numbered sub-steps; Steps 0a to 0d and Steps 1 to 8 are unchanged (the diff hunk is Step 0e only, `@@ -39,7 +39,15 @@`).

### Task 74 acceptance, run by me (head `1b2833b`, Python 3.11)

| Check | Result |
|---|---|
| (a) `grep -c "^- \[ \]"` and `grep -c "^- \[x\]"` on the guide | `13` and `0` |
| (b) `unverified` on Step 0e: sub-step 4 (clone-then-copy) and sub-step 7 (README or licence) only; `git ls-files`, branch, remote and push lines are not marked | holds (`grep -n unverified` lists lines 23, 32 to 35, 37, 46, 49; lines 32 to 37 are Step 0b, 23 is the intro) |
| (c) `MANIFOLD_APP_KEY_FILE` found (lines 12, 64, 66); URL and address grep prints nothing; `company_dns|testbed|discovery|mediumroast` grep prints nothing; `Step 0a` to `Step 0e` each `1`; `Plan: Task 28` to `Plan: Task 35` each `1` | holds |
| (d) `.venv/bin/python server/tests/datasets/scan.py docs/megaroast-setup.md --terms-file <the empty fixture in the scratchpad>` | `scan: no findings`, exit 0. The fixture is `/private/tmp/claude-501/-Users-mihay42-dev-manifold--claude-worktrees-branch-version-check-7b10f3/6144e1d4-de3c-45bc-b853-1d2d19befa0a/scratchpad/empty_terms.json` (given in the task; it exists; I did not read it). The owner's `~/.manifold/excluded_terms.json` was not used or read |
| (e) `cd server && ../.venv/bin/python -m pytest tests/test_docs_links.py -q` | `12 passed in 0.02s` |
| (e) `python3 bundles/base/tools/build.py --check` | `lint ok` |
| (f) diff files | `docs/megaroast-setup.md` and `docs/plans/PHASE_4_PLAN.md` only |
| Full server tests, `cd server && ../.venv/bin/python -m pytest -q` | `1146 passed, 5 xfailed, 33 warnings in 133.83s`; equals revision 8 (no code changed) |

The coder's Note counts (13, 0, Docker 1, Python 3.11 1, `--instance` 2, `rev-parse` 1, "outside" 2, "once" 2) were not all re-run by me for the Step 0e-only restriction; I re-ran the whole-file counts above and read the block, and the words are present. Also checked for keys and names: `grep -niE "ssh-rsa|BEGIN .*KEY|ghp_|gho_"` finds nothing; the word "Megaroast" appears on lines 2 and 4 (F35, unchanged by this commit), and `~/dev` appears once in sub-step 3 (F41). Held-out scenarios: none read. The coder's plan Note says the Task 74 header is left unticked; `PHASE_4_PLAN.md:1292` is `- [ ]`, so that holds.

### The owner-raised gap: does the rewrite settle "Step 0e lacks steps"?

In substance, yes. The owner's two questions are answered in the first lines: where manifold comes from (sub-step 1, clone it into its own folder, address in the quickstart) and how many repositories `init` runs on (once, one instance, not the others). The steps the old text lacked are all there in order: needs, instance path and the parent-folder check, `init` and its prompts, the credential warning, the pre-push checks, the push, the visibility check. Two residual gaps are in F39 (the scan step has no command, and the guide never says that `init` makes the instance a git repository with its own history, though sub-steps 3 and 6 depend on it). Whether the owner can now run Step 0e top to bottom unaided is real-use evidence that does not exist yet: **no evidence yet**; the box is unticked.

### New findings in revision 9

**F39 (Nit) — Sub-step 6 names no scan command, and sub-step 4 never says the instance is a git repository**
- **Pass:** Bugs (a step the owner cannot follow from the guide alone) and Compliance (traceability to the amendment's point 7).
- **Location:** `docs/megaroast-setup.md:48` (sub-step 6: "the scan with an empty terms list prints `scan: no findings`") and `:46` (sub-step 4: "also creates two credential files, a running server, the two sample components ... and a handoff"); amendment `PHASE_4_PLAN.md:1288`, points (5) and (7).
- **Evidence:** read. The scan is `server/tests/datasets/scan.py` with `--terms-file` (it is on `origin/main`, so the fresh manifold clone has it, `git ls-tree origin/main` finds it); the guide gives neither the path, the file to scan (the instance, or what), nor how to make an empty terms list (the `Write` tool is an agent's way; the owner would need a file holding `[]`). This is the same gap as F36 for Step 4, here in the step the owner raised. Separately, sub-step 6 says `git ls-files`, `git branch --show-current` and `git log` "in the instance" and sub-step 3 checks the parent is not inside a repository, but no line says that `init` itself runs `git init` and commits (the "Manifold" and `first-agent` authors imply it). The amendment's point (5) does not ask for that line, so the coder followed the amendment; it is the amendment that is thin here.
- **Direction:** the planner amends Task 74's text with a line naming the scan file and its usage (README `server/tests/datasets/README.md`), and one sentence saying `init` makes the instance a git repository with its own commits; the coder then applies it. Not for the coder alone.
- **State:** open

**F40 (Nit) — Step 0e uses placeholders the guide never defines, and `<repo-name>` differs from the `<name>` of Steps 0c and 0d**
- **Pass:** Bugs (consistency).
- **Location:** `docs/megaroast-setup.md:6-12` (the placeholder list) against Step 0e (`<manifold-repo-url>`, `<folder>`, `<parent folder>`, `<path>`, `<branch>`, `<repo-name>`) and Steps 0c and 0d (`<ORG>/<name>`).
- **Evidence:** read; the list at lines 6 to 12 defines `<ORG>`, `<source-owner>`, `<source-repo>`, `<repo-role>`, `<new url>`, `<App-name>`, `<INSTALLATION_ID>` and the variable name, and says the guide "is written with placeholders so a later organization can reuse it". The Step 0e placeholders are obvious from context, so no one is misled; but sub-step 8 writes `<ORG>/<repo-name>` where 0c and 0d write `<ORG>/<name>` for the same thing.
- **Direction:** say once in the list that placeholders in angle brackets inside a step are filled by the reader, or use `<name>` in sub-step 8.
- **State:** open

**F41 (Nit) — A real path and a one-time observation are written into a guide that says no real path belongs in it**
- **Pass:** Bugs (consistency) and Security (personal data, low).
- **Location:** `docs/megaroast-setup.md:44` (sub-step 3: "your `~/dev` was an empty one") against `:14` ("No real ... path belongs in this file"); also `:48`, "as the coordinator ran them Nov 22, 2026", with expected counts ("nine files", "Manifold" once).
- **Evidence:** read. `~/dev` is a conventional folder name, not a secret; the amendment's point (4) itself says "(the owner's `~/dev` was an empty one)", so the coder copied it. The "nine files" and author counts are a dated observation of one `init` run; if `init` changes, the guide will be wrong and nothing says how to notice. The guide does date them, which limits the risk.
- **Direction:** the owner decides whether to keep `~/dev` as an example (and amend line 14), or say "a folder such as your development folder"; consider "expected at the time of writing" for the counts. Not for the coder alone, because the amendment dictates the text.
- **State:** open

(The nit cap of 5 per report is not reached: three nits reported, none left out.)

### Carried forward, not re-decided (revision 9)

F34 (Step 8 token discarded then reused), F35 ("Megaroast" in the title), F36 (Step 4 scan not named), F37 (plan text earlier says "fork"), F38 (README or licence as a cause; sub-step 7 repeats the phrase but marks it "unverified: confirm with `git push --help`", so it is now marked in Step 0e as well as asked of in Step 0b), the 3 not itemized nits of revision 8, F4 (Important, owner-gated), F9, F10, F11, F26, F27, F33. This commit changes none of them; their State lines are in the sections below.

### Other checks (revision 9)

- **Security.** The diff read in full for credentials and personal data: none. No full URL (the clone address is `<manifold-repo-url>`), no address-shaped text, no real name or key; the guide's author lines in the commit are the project's own. The `~/dev` mention is F41. The owner's terms file was not opened.
- **Context files.** `AGENTS.md`, `CLAUDE.md` and `REVIEW.md` are not made out of date.
- **Test plan.** No `PHASE_<N>_TEST_PLAN.md` in this change.
- **Real-use evidence (point d).** No evidence yet: no box ticked, the owner has not followed Step 0e from the guide. The owner's later run (he already ran `init` and the push once, as the amendment records) is the evidence that would settle it.
- **Owner approval of agent-behavior text (g).** The round 6 signature of Nov 22, 2026 covers the text; the coder's wording stays within the nine points.
- **CI.** Not read for this head; not checked.

### Gates run (revision 9, 2026-11-22, head `1b2833b`)

| Command | Counts | Result |
|---|---|---|
| `.venv/bin/python server/tests/datasets/scan.py docs/megaroast-setup.md --terms-file <the scratchpad empty_terms.json>` | `scan: no findings`, exit 0 | pass |
| `cd server && ../.venv/bin/python -m pytest tests/test_docs_links.py -q` | `12 passed in 0.02s` | pass |
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |
| `cd server && ../.venv/bin/python -m pytest -q` | `1146 passed, 5 xfailed, 33 warnings in 133.83s` | pass |
| `grep -c "^- \[ \]"` and `"^- \[x\]"` on the guide | `13` and `0` | pass |
| `./manifold init --help`, `git -C <folder> rev-parse --show-toplevel` | help text read; the message shown above | read-only; supports the guide's statements |
| Not run | | `bundles/base/tests`, `tests/live`, `tools/vendor_web.py --check` (nothing they cover changed) |

### Could not check (revision 9)

- The owner's chat statements and the coordinator's checks of Nov 22, 2026 (nine files, branch `main`, author counts, the push, the `~/dev` observation): I rely on the amendment's record; I did not run `init` (it needs Docker and would create a folder) and no network call or `gh` call was made.
- Where `init` writes the two credential files, and that it refuses an existing folder without `manifold.yaml`: the amendment's record; `init --help` does not say.
- The coder's Step 0e-restricted word counts (not re-run one by one).
- The pull request description's matching tick lines, CI, other platforms.

### Rule exceptions compared (revision 9)

- **Coder, Task 74, `none`:** `.manifold/guard-log.jsonl` had 17 lines when I started and 17 after my commands (`wc -l`); the last `coder` line is still line 15 (CP10), so `none` is consistent with the log. The guard logs refusals only. The commit `1b2833b` holds two files and ends with the attribution line; I saw no `--no-verify` or hook bypass; `git status --short` was empty.
- **Mine:** I wrote only this file, with `Edit`. I ran read-only `git` (`rev-parse`, `show`, `diff`, `status`, `ls-tree`), `grep`, `ls`, `wc`, `sed`, `./manifold init --help`, one `git -C` on a path outside any repository, and the gate commands above (the scan with an explicit `--terms-file` argument, the scratchpad fixture). No command of mine was refused or blocked. No heredoc, `sed -i`, redirect or `/tmp` write; the scratchpad was used only as a read path.

### A human decides (revision 9)

This review does not approve or block the change. A human approves, informed by the findings. Counts after revision 9: Important 1 open (F4, owner-gated, checkpoint 1); Nit 14 open (F9, F10, F11, F26, F27, F33, F34 to F38, and F39 to F41 new) plus 3 not itemized; nothing repaired in this revision. The `Review process` approval rule in `AGENTS.md` (solo repository, owner Michael Hay) applies: no second approver is required. F39 and F41 are the planner's or the owner's to decide because the amendment dictates the text; the coder's Step 0e matches the nine points.

## CP11 revision 8: the owner's Megaroast setup guide (Task 73)

### Verdict

No Important finding. Five new nits (F34 to F38) and three more not itemized (nit cap). Task 73's acceptance (a) to (g) reproduces; the guide matches Tasks 28 to 35 in every step I compared; the plan edits by the coder are only Task 73's Todo and Note. Evidence is mine, run on head `408e86f` (Python 3.11). The earlier findings F4, F9, F10, F11, F26, F27 and F33 were not re-decided and keep their State.

### (1) The guide against Task 73, point by point

| Task 73 point | Result | Evidence |
|---|---|---|
| 1. Title, purpose, placeholders | holds | `docs/megaroast-setup.md:2-14`: `<ORG>`, `<source-owner>`, `<source-repo>`, `<repo-role>` (four roles), `<new url>`, `<App-name>`, `<INSTALLATION_ID>`, and `MANIFOLD_APP_KEY_FILE` by name. See F35 for the word "Megaroast" |
| 2. Rules block, four bullets | holds | `:18-21`: no agent reads holdout QA, the key or a token; a ticked box is the owner's act and the coder ticks none; the mirror rule; secrets never in chat, a log, a pull request or any repository file |
| 3. Where a tick is mirrored | holds | `:20`: plan Todo and pull request description; Part 0 mirrored in the pull request description only; Task 29's note says "created in Part 0"; the guide's boxes are the working copy (Open question 2's answer) |
| 4. Part 0, `Step 0a` to `Step 0e`, no `Plan:` line | holds | `:29-42`; `grep -c "Step 0a"` to `"Step 0e"` print `1` each; no `Plan:` on those lines; all private |
| 5. Steps 1 to 8 for Tasks 28 to 35 | holds | `:48-58`; `grep -c "Plan: Task 28"` to `"Plan: Task 35"` print `1` each; the order CP4 (1 to 4) then CP5 (5 to 8) as written |
| 6. "unverified: confirm with <source>" for anything the plan lacks | holds | every Part 0 `git` line (`:32-35`, the force-with-lease flags `:37`) and `./manifold` (`:42`) says "unverified"; the three `gh` forms are marked "verified". I ran `gh repo create --help`: a name plus `--private` is the documented non-interactive form (help line "supply the repository name and one of `--public`, `--private`, or `--internal`"), and `--add-readme`, `--license` and `--gitignore` exist, as the guide says. `git push -h` lists `--[no-]tags` and `--[no-]force-with-lease[=<refname>:<expect>]`, and `git remote -h` lists `add`, `rename` and `remove`, so the guide's "unverified" is conservative and not wrong |
| 7. Last line | holds | `:60` |

Acceptance, run by me: (a) `ls docs/megaroast-setup.md` prints the path. (b) `grep -c "^- \[ \]"` prints `13`, `grep -c "^- \[x\]"` prints `0`. (c) the sixteen counts above are all `1`. (d) `MANIFOLD_APP_KEY_FILE` is on lines 12, 56 and 58; `grep -nE "https?://|[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\."` prints nothing; `grep -niE "company_dns|testbed|discovery|mediumroast"` prints nothing. (d2) as in point 6. (e) `.venv/bin/python server/tests/datasets/scan.py docs/megaroast-setup.md --terms-file .manifold/scratch/empty_terms.json` printed `scan: no findings`, exit 0 (see "Could not check" for the fixture). (f) `python3 bundles/base/tools/build.py --check` printed `lint ok`; `cd server && ../.venv/bin/python -m pytest tests/test_docs_links.py -q` printed `12 passed`. (g) `git diff origin/main..HEAD --stat` lists the four files named in the header and nothing else. No real repository name, organization display name, App ID, installation ID, key, token, address or full URL is in the guide (read in full). Nothing is stated about GitHub or git beyond the plan and the command help except as listed in F38 and the not-itemized nits.

### (2) The facts against Tasks 28 to 35 and Concerns 7 to 9

No step is added or changed in meaning; one inherited contradiction is F34.

- **Step 1 / Task 28:** owner writes the rows, private, stop if not private, "nothing committed here", only table rows in the diff. Matches (`PHASE_4_PLAN.md:556-557`). Minor points in the not-itemized nits.
- **Step 2 / Task 29:** `gh repo view ... --json visibility` once per repository, "3 of 3 exist". Matches (`:568-569`).
- **Step 3 / Task 30:** exists, private, no builder access; "Nothing is read or cloned" is an addition that agrees with Concerns 8 (`:114`) and Task 30's "Builder agents never read, clone"; no change in meaning.
- **Step 4 / Task 31:** private terms file at `~/.manifold/excluded_terms.json`, never printed, stop if missing; clone to a scratch folder outside every checkout; start command not copied from the quickstart; `wiki_health` and `wiki_inventory_tool`; counts per kind, never quoted; no file copied (`:591-593`). Matches. The terms file is named only as a path to the owner's own file; I did not open it. See F36 for the scan command.
- **Step 5 / Task 32:** the five "still to read" facts are exactly those of `:609` (JWT claims and algorithm; Metadata always granted; `GET /installation/repositories` needs only Metadata; lost-key revocation; private App transfer).
- **Step 6 / Task 33:** settings path, name with a fallback said in chat first, "Only on this account", webhook Active unchecked, no callback URL, no user authorization, no device flow, Metadata read-only and no Contents, Pull requests, Issues, Administration or Secrets, one key saved outside every repository at the path held in `MANIFOLD_APP_KEY_FILE`, nothing secret in chat. Matches `:621-622`. The key is held only by the variable name `MANIFOLD_APP_KEY_FILE`; no path is written.
- **Step 7 / Task 34:** "Only select repositories", three repositories, not holdout QA, owner-approval step recorded if it appears, count 3, no App or installation ID in a committed file. Matches `:633-634`.
- **Step 8 / Task 35:** key file by variable name, JWT signing unverified, `POST /app/installations/<INSTALLATION_ID>/access_tokens` with `permissions` limited to Metadata read, one listing request, discard, repeat after one hour and expect a refusal, HTTP status only. Matches `:645-646` (and the contradiction in F34 is Task 35's).
- **Holdout QA never read by builders:** `:18`, `:41`, `:50`. Metadata read only: `:56`. Matches Concerns 8 and 9.

### (3) The push-rejected guidance

`megaroast-setup.md:37`: prefer creating the repository empty; otherwise inspect the remote first; only then "replace `main` with a force-with-lease push (flags unverified: confirm with `git push --help`). You decide this; no agent does it." It does not tell the owner to force-push as the default, puts inspection first, marks the flags unverified and says the decision is the owner's. That meets the instruction. It would be clearer if it said in so many words that the push overwrites the remote `main` and cannot be undone from the copy (see the not-itemized nits); not a finding on its own. The cause it states is the guide's, not the plan's (see the not-itemized nits).

### (4) The index row and the link test

`docs/README.md`: one new table row (`[Megaroast setup](megaroast-setup.md)`), the target resolves. `server/tests/test_docs_links.py`: `git diff` is one list entry, `"docs/megaroast-setup.md"`, added to `DOCS`; no assertion, test function or other line changed (`git diff origin/main..HEAD -- server/tests/test_docs_links.py` is 1 insertion and 1 deletion on the list's second line, a re-wrap). The guide has no relative link (its `docs/quickstart.md` mention is in a code span), so the link test has nothing to check in it today; it will if a link is added. This follows Open question 1's answer (yes).

### (5) The coder's plan edits and Rule exceptions

`git show 408e86f -- docs/plans/PHASE_4_PLAN.md`: two lines removed and two added, the Todo and the Note of Task 73, and nothing else. The Todo has five items ticked, all by the coder as the task says (the plan Todo is the coder's to tick; the guide's boxes are the owner's and none is ticked). The Note's counts reproduce (13 and 0; each `Plan:` and `Step 0` label 1; `MANIFOLD_APP_KEY_FILE` on 3 lines; `scan: no findings`; `lint ok`; `12 passed`; the full server run, below).

Rule exceptions line, coder, `none`: `.manifold/guard-log.jsonl` had 17 lines when I started and 17 after all my commands (`wc -l`). The last `coder` line is line 15 (2026-11-22T00:35:28Z, `no-heredocs`, CP10), the last two are `reviewer` lines (16 and 17, revision 7). So `none` is consistent with the log, and the Note's "still has 17 lines" is accurate. The guard logs refusals only; a command that went through cannot be compared. The commits: `408e86f` holds four files and ends with the attribution line; the others are the planner's and the owner's. I did not see `--no-verify` or a hook bypass in the log. Nothing in `git status --short` is untracked or changed.

### (6) The earlier tasks still read "fork" and "exists": is the Effect paragraph enough?

For the guide's reader, yes: the guide never says "fork" or "already exist", Part 0 says the repositories are created, and its Rules block says where the tick of Task 29 is noted. For a reader of the plan, not completely: see F37. The amendment's Effect covers Tasks 28 to 31 (`:1228`); it does not cover Task 34's "choosing the fork" (`:633`), the CP4 introduction's second sentence "nothing is created" (`:548`), the "Needs from other repositories" line (`:95`), Concerns 7's "The repositories already exist" (`:113`) and Open question 16's parenthesis (`:766`). The Correction names only the first sentence of `:548`, and not "nothing is created". The owner signed "none is edited", so the plan text stays as it is by his decision; the risk is an agent reading CP4 top to bottom. It is reported as a nit because the amendment is signed and names the correction.

### New findings in revision 8

**F34 (Nit) — Step 8 tells the owner to discard the token, then to use the same token an hour later**
- **Pass:** Bugs (consistency) and Compliance (secrets handling).
- **Location:** `docs/megaroast-setup.md:58`, inherited from `PHASE_4_PLAN.md:645-646` (Task 35: "discards the token ... After one hour the owner repeats the one request" and "the same token is refused after one hour").
- **Evidence:** read. A discarded token cannot be re-used; to repeat the request the owner has to keep it somewhere for an hour, and the only rule given is "never write it to a file, chat or log". A reader may save it to a file to keep it, which is what the rule forbids. The guide copies the contradiction faithfully (Task 73 says take the wording from the plan, add no new fact), so the fault is in Task 35.
- **Direction:** the planner amends Task 35 and the guide together (for example, say where the token may be held until the check, and that it is discarded after it); not for the coder to change alone.
- **State:** open

**F35 (Nit) — The guide says no organization name belongs in it, and names "Megaroast" in its title and first sentence**
- **Pass:** Bugs (consistency).
- **Location:** `docs/megaroast-setup.md:2`, `:4`, and `docs/README.md` (new row) against `:14` ("No real repository name, organization name ... belongs in this file") and Task 73 point 1.
- **Evidence:** read; `grep -ni megaroast docs/megaroast-setup.md` prints lines 2 and 4. The amendment calls the organization `MegaRoast`, and the owner chose the file name, so this may be the project's name and not the organization's. It is still against the guide's own rule and against its aim (a later organization reuses it). The acceptance grep (`company_dns|testbed|discovery`) does not look for it, which is why it passed.
- **Direction:** the owner decides: keep "Megaroast" as the name of the project (and say so in line 14), or retitle the guide with the placeholder.
- **State:** open

**F36 (Nit) — Step 4 says "run the scan" but does not name it**
- **Pass:** Compliance (traceability) and Bugs (a step the owner cannot follow from the guide alone).
- **Location:** `docs/megaroast-setup.md:51` against `PHASE_4_PLAN.md:592` ("Run `scan.py` (Task 26)").
- **Evidence:** read. The guide names no command, file or flag for the scan; the file is `server/tests/datasets/scan.py` with a `--terms-file` option (revision 7 ran it). The owner can find it, but the step is the only one with a command that is not given, and the plan names it.
- **Direction:** name `server/tests/datasets/scan.py` and say that its README (`server/tests/datasets/README.md`, step 3) gives the usage, without copying the terms path into any command line that is logged.
- **State:** open

**F37 (Nit) — The plan's earlier text still says "nothing is created", "the fork" and "already exist" in places the Effect paragraph does not name**
- **Pass:** Compliance (consistency between the amendment and the plan it amends).
- **Location:** `PHASE_4_PLAN.md:95`, `:113`, `:548` ("nothing is created"), `:633` (Task 34, "the fork"), `:766`; Effect paragraph `:1228`.
- **Evidence:** read, and `grep -n "fork\|already exist\|nothing is created"` over the plan. The Effect names Tasks 28 to 31; the "nothing is created" half of `:548` contradicts Part 0 (which creates five repositories), and Task 34 is not in the Effect at all. The amendment is signed with "none is edited", so this is the owner's decision; the point is that an agent reading CP4 before the amendment is told the opposite.
- **Direction:** the planner extends the Effect line to Task 34 and to the CP4 introduction, or the owner accepts the reading order. Not for the coder.
- **State:** open

**F38 (Nit) — Step 0b states GitHub's behavior as a cause**
- **Pass:** Bugs (verified claims).
- **Location:** `docs/megaroast-setup.md:37`: "GitHub created the repository with a README or licence, so the histories diverge".
- **Evidence:** the plan's own record (Correction, `:1227`) says "GitHub had created the repository with an initial commit", the owner's observation, with the flags unverified. "README or licence" is the guide's wording; it is a plausible reading, not recorded in the plan or in `gh repo create --help` (which only shows that `--add-readme`, `--license` and `--gitignore` exist). Task 73 point 6 asks that a fact the plan does not record be marked "unverified".
- **Direction:** write "an initial commit (owner's observation)" or mark the cause "unverified".
- **State:** open

**Three more nits, not itemized (nit cap of 5):** (i) Step 1 asks for rows for the standalone UI and the example instance as repositories that "derive from the company repository" (Task 28's wording) while the Effect paragraph says the fresh repositories hold no content from it; the guide does not say what to write for them. (ii) Step 1 says "stop and tell the owner" in a guide that addresses the owner as "you". (iii) Step 0b does not say in so many words that the force-with-lease push overwrites the remote `main` for good (point 3 above).

### Carried forward, not re-decided

F4 (Important, owner-gated, checkpoint 1), F9, F10, F11 (checkpoint 1), F26, F27 (checkpoint 2), F33 (the date convention in the round 4 amendment). Their State lines are unchanged and are in the sections below. Observation only: round 5 uses one date, Nov 22, 2026, for both the owner's answers and his signature, so F33's mismatch does not recur there; `git log` for `1b23c92` and `756e3b0` was not read for the local day.

### Other checks (revision 8)

- **Security.** The diff read in full for credentials and personal data: none. No real repository, organization display name, address, ID, key or token is in the guide. The owner's `~/.manifold/excluded_terms.json` was never opened, read or printed by me, and no run without an explicit `--terms-file` was made. The guide names that path only as the owner's own file. The held-out QA repository was not opened or cloned.
- **Intent.** INT-3's constraint (written permission, a scrub before any real content is public) holds: Part 0b's risk line and Step 1 carry it. INT-7 (App, least privilege, key outside every repository, no long-lived secret) holds in Steps 6 to 8.
- **Context files.** `AGENTS.md`, `CLAUDE.md` and `REVIEW.md` are not made out of date by this change. `AGENTS.md` lists no document index that needs the new file.
- **Test plan check.** No `PHASE_<N>_TEST_PLAN.md` in this change.
- **Real-use evidence (point d of the prose standard).** The owner has not yet followed the guide: no box is ticked, no step has been run from it. **No evidence yet.** The guide changes no agent behavior by itself; the owner's approval of text that changes agent behavior (g) is the signed amendment, which approves Task 73's text.
- **CI.** Not checked for this head: not read (`gh run view` not run); the branch may not be pushed. State: not checked.
- **Held-out scenarios.** I did not read any.

### Gates run (revision 8, 2026-11-22, head `408e86f`, Python 3.11)

| Command | Counts | Result |
|---|---|---|
| `.venv/bin/python server/tests/datasets/scan.py docs/megaroast-setup.md --terms-file .manifold/scratch/empty_terms.json` | `scan: no findings`, exit 0 | pass (fixture: see "Could not check") |
| `cd server && ../.venv/bin/python -m pytest tests/test_docs_links.py -q` | `12 passed in 0.02s` | pass; equals the coder's `12 passed` |
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |
| `cd server && ../.venv/bin/python -m pytest -q` | `1146 passed, 5 xfailed, 33 warnings in 123.61s` | pass; equals the coder's `1146 passed, 5 xfailed` (revision 7 had 1144; I did not trace the two added tests, I compared only with the coder's note) |
| `grep -c` acceptance (b), (c), (d) | `13`, `0`, sixteen counts of `1`, no match for the URL, address and name greps | as in the table above |
| `gh repo create --help`, `git push -h`, `git remote -h` | help text read | supports the guide's statements; no repository was created or changed |
| Not run | | `.venv/bin/python -m pytest bundles/base/tests -q`, `tests/live`, `tools/vendor_web.py --check`: nothing they cover changed; not run by me |

### Could not check (revision 8)

- **The empty-list fixture.** The task asked for an empty `[]` fixture; I cannot write one (my only write is this file). I used `.manifold/scratch/empty_terms.json`, left by the coder's earlier runs (gitignored). I did not read its content; the scan accepted it as a term list (a wrong shape would have printed the constant error), so it is a JSON list, and a clean run means no email, host, token-shaped string or personal-data pattern in the guide with that list. A run with the owner's real term list is the owner's step.
- The owner's chat statements (Correction and answers are read only as the plan records them), the coder's chat report, and any command the guard does not log.
- Every GitHub fact: the guide marks its own unverified items and I did not check GitHub's documentation or run `gh` against a real repository (I made no network call to the organization).
- Whether the pull request description has the matching tick lines (the guide's mirror rule): no pull request was read.
- Linux, Python 3.10 and 3.12 (CI not read).

### Rule exceptions compared (revision 8)

- **Coder, CP11:** compared in (5): `none` against a guard log with no `coder` line after line 15 (17 lines before and after my commands).
- **Mine:** I wrote only this file, with `Edit`. I ran read-only `git` (`log`, `diff`, `show`, `status`), `grep`, `ls`, `wc`, `tail`, the project's gate commands (each alone), `gh repo create --help`, `git push -h`, `git remote -h`, and `scan.py` with an explicit `--terms-file` (the coder's gitignored fixture, as an argument only). **No command of mine was refused or blocked**; the guard log has 17 lines before and after (`wc -l` read before the write). I did not use a heredoc, `sed -i`, a redirect or `/tmp`. `.manifold/guard-allow.json` was not read. If a later check shows a line 18 from me, it is the review file write and not a breach I hid.

### A human decides (revision 8)

This review does not approve or block the change. A human approves, informed by the findings. Counts after revision 8: Important 1 open (F4, owner-gated, checkpoint 1); Nit 11 open (F9, F10, F11, F26, F27, F33 earlier; F34 to F38 new) plus 3 not itemized; nothing repaired in this revision. The `Review process` approval rule in `AGENTS.md` (solo repository, owner Michael Hay) applies: no second approver is required. F34, F35, F36 and F37 are the owner's or the planner's to decide; the coder's CP11 text matches Task 73.

## CP3 revision 7: the scan-output repair (CP10, Tasks 66 to 72)

### Verdict

No Important finding. F28 (Important) and the four nits F29 to F32 of revision 6 are repaired; one new nit (F33). Evidence is mine, run on head `f9ead7d` on Python 3.11. Only `server/tests/datasets/README.md`, `scan.py`, `test_datasets.py` and documents changed since revision 6; no server code changed.

### F28 to F32: set from evidence

| Finding | State | Evidence |
|---|---|---|
| F28 | repaired (rev 7) | `scan.py:43-49`: `Finding` is `(path, line, kind)`, `__str__` is `"%s:%d: %s"`; the `detail` field is gone. `grep -rn "\.detail\|detail="` over `server/tests/datasets/` prints nothing, and the only users of `scan` are `test_datasets.py` and the command line (no other file imports it), so no caller or test depends on the removed field. Output paths, read in full (`scan.py:121-135`): the findings loop prints `Finding.__str__` (file, line, kind); the clean line is a constant; the error line prints `exc` for an `OSError` or `ValueError`. I ran the error paths with the coder's fixtures: a missing terms file prints `[Errno 2] No such file or directory: '.manifold/scratch/nope.json'` (the path I gave, not content); a missing scan path prints `nothing to scan at <path>`; a terms file that is not JSON prints `the term list must be a JSON list of strings; this file is not valid JSON` (`load_terms` raises with `from None`, so no `JSONDecodeError` text, which can quote a line, is shown). A term list of the wrong shape prints a constant message (`:64`). No exception message carries a scanned line, an email, a host, a token or a term. Limits: the file name or relative path is printed (`shown`); it is not matched text, but a file named after a term would show it, and a terms file that is not valid UTF-8 raises `UnicodeDecodeError` (a `ValueError`), whose message names a byte and a position, not text (argued by reading, not run). The scan of the whole `server/tests/datasets/` folder, which I could not run in revision 6, I ran now with the coder's empty-list fixture: 14 lines, each `file:line: kind`, no text (README, `loader.py`, `scan.py`, `test_datasets.py` hold deliberate samples and an author address; the plan's acceptance is over `curated/` only, so this is not a finding). The Task 66 sample with the fixture `["secretco"]` printed exactly `page.md:1: email`, `page.md:1: host`, `page.md:1: term`, exit 1. |
| F29 | repaired (rev 7) | `scan.py:133-134`; I ran `scan.py server/tests/datasets/curated --terms-file .manifold/scratch/empty_terms.json` (path argument only, file not read by me): `scan: no findings`, exit 0. The owner said yes to Open question 1 |
| F30 | repaired (rev 7), widening deferred | README step 3 now says "hosts in URLs (`scheme://host`)" (`README.md:29`), that a bare host name with no scheme is not caught (`:32-33`), that a finding prints only the file, the line and the kind (`:33-34`) and that a clean scan prints `scan: no findings` and exits 0 (`:35`). Each sentence matches `scan.py`. Widening to bare hosts stays deferred: the signed amendment gives the reason (`acme.io` is a deliberate slug) |
| F31 | repaired (rev 7) | see "Task 71 line checked" below |
| F32 | repaired (rev 7), list not extended | message corrected at `test_datasets.py:256`; comment added above `_FIRST_NAMES`; list unchanged (30 names), by the owner's answer to Open question 2 |

### The two existing-test edits (item 2)

`git diff 85b52a2..HEAD -- server/tests/datasets/test_datasets.py` removes three lines: (1) the silence assertion (`out == ""`), (2) the host-text assertion, (3) the old message of the scripts assertion (Task 70, message only, the assertion `>= 3` is unchanged). (1) and (2) are the two the plan names; (3) is named in Task 70 and the owner signed the amendment, so it is planned.

- **Silence assertion.** Approval recorded in the Task 68 note ("Owner's yes: Open question 1, answered Yes by Michael Hay, 2026-11-22", and in the Open question itself). The new assertion `== "scan: no findings\n"` is exact and pins the new behavior; it does not weaken the test. Run by me, inline mutation (`python -c` importing `tests.datasets.scan`, wrapping `scan.main` to drop the `scan: no findings` line from standard output, `pytest.main(['tests/datasets','-q','-k','scan'])`, no file written): `1 failed, 4 passed, 11 deselected`, in `test_scan_flags_real_shaped_text_and_passes_the_committed_sets`. So the assertion fails when the line is missing, as the old silent scan would.
- **Host-text assertion.** Approval recorded in the Task 66 note (the owner's chat decision of Nov 22, 2026, option 2). The old assertion was a substring test that the output contained `sample.md:2: host intranet.big-corp.net`; the new pair is `"%s:2: host" % sample in out.splitlines()` (an exact whole-line match of file, line and kind) and `"intranet.big-corp.net" not in out`. That is stronger on both sides: it fails if the host text is printed (the line would no longer equal the expected line, and the second assertion fails), and it fails if the finding disappears.
- **The recorded deviation (full path, not `sample.md`).** Judged acceptable. `main` passes `args.path` to `scan`, and for a file `scan` prints `str(file)` as given (`scan.py:101`, `shown = str(file if root.is_file() else file.relative_to(root))`), so with `str(sample)` (a `tmp_path` file) the line starts with the full path. The literal `sample.md:2: host` could not match a whole line. The replacement keeps the file, the line and the kind and adds the exact-line form; the deviation is recorded in the task note with its reason. It does not weaken the test.
- **No other existing test touched.** The three removed lines above are the only removals in `test_datasets.py`; the rest of the diff is additions (the new test, a comment). The server suite passes in full (below).

### The new test and its teeth (item 2)

`test_scan_never_shows_matched_text_for_any_kind` (`test_datasets.py:166-180`): a page holding an email and a URL host that both contain the private term, a term list `["secretco"]`, the kinds `{"email", "host", "term"}` on line 1, `"secretco" not in str(findings).lower()` and the printed output exactly the three lines, with no `secretco`. Two strengths: `str(findings)` is the list's `repr`, which shows every field of each `Finding`, so a returned `detail` field would fail it even if `__str__` hid it; and the command-line output is an exact list of lines, not a substring test. Run by me, inline mutation (`python -c` importing `tests.datasets.scan`, setting `Finding.__str__` to a version that appends `secretco intranet.big-corp.net`, `pytest.main(['tests/datasets','-q','-k','scan'])`, no file written): `2 failed, 3 passed, 11 deselected`: `test_scan_flags_real_shaped_text_and_passes_the_committed_sets` and `test_scan_never_shows_matched_text_for_any_kind`, the same count as the coder's run against the old `scan.py`. By reading, against the old `scan.py` the new test fails on the returned `detail` in the `repr` and on the printed `page.md:1: email ops@secretco.com`, which is the coder's `2 failed, 3 passed`. A finding kind the test does not cover is `token` and `pattern`, which never carried text (and are tested in `test_scan_flags_real_shaped_text_and_passes_the_committed_sets` and `test_no_set_contains_personal_data`); every kind is covered by the two tests together. The coder ran the tests failing first against the unchanged `scan.py` (`2 failed, 3 passed, 11 deselected`, Task 66 note); I cannot see the intermediate state (the test and the code are in one commit, `7ef9f3d`), so that order rests on the note and on my own mutation above.

### Task 71 line checked (F31)

`PHASE_4_PLAN.md` "Rule exceptions (CP3, coder)": two refused `Bash` heredocs, rule `no-heredocs`, `agent_type` coder, log line 14 (2026-11-21T14:32:36Z, first run, failure F27) and line 15 (2026-11-22T00:35:28Z, second run, failure F28), neither worked around, no other coder line since the last revision. Checked against `.manifold/guard-log.jsonl`: line 14 and line 15 carry those times, rule `no-heredocs`, tool `Bash`, `agent_type` coder; lines 16 and 17 are `reviewer` (mine, revision 6). It matches the log and failures F27 and F28, and it says it was written from them and not from the coder's own report. The line is accurate. Nothing else in the Task 71 edit changed plan text (`git diff` of the plan shows the one added line under the CP3 gates note).

### Task 72, the CP10 Rule exceptions line, and failure F29

- **Coder, CP10 (`none`).** `.manifold/guard-log.jsonl` had 17 lines when I started, the Task 72 note says 17 at the start and 17 at the end, and there is no `coder` line after line 15 (lines 16 and 17 are `reviewer`). So `none` is consistent with the log. The guard logs refusals only: a command that went through cannot be compared. The commits: `7ef9f3d` (code, Tasks 66 to 70) and `f9ead7d` (plan notes), explicit paths, attribution line present, no `--no-verify` or hook bypass visible; the first holds the three files in `server/tests/datasets/` only (`git show --stat 7ef9f3d`), the second the plan only. I did not see whether a heredoc was typed and the guard let it through: the log has none. The coder's fixtures in `.manifold/scratch/` (`empty_terms.json`, `terms_secretco.json`, a `sample` folder, two `update_pr*.py` helper scripts) are gitignored (`git status --short` is empty); I did not read the fixtures or the scripts.
- **Diff stat (item 3).** The Task 72 acceptance says `git diff --stat origin/main..HEAD` lists only `server/tests/datasets/` and the plan; the coder ran `git diff --stat 7df5d38 HEAD` instead and says why (the branch's earlier checkpoints add files outside that folder, and the plan edits came in the next commit). The reason is right: `origin/main..HEAD` also holds the failures file and the REVIEW_PLAN documents. My own `git diff --stat 85b52a2..HEAD` is the 6 files named in the header. Acceptable; the plan's acceptance line was loose and the deviation is recorded.
- **Task 72 counts reproduce.** `tests/datasets` `16 passed`, the full suite `1144 passed, 5 xfailed`, as the note says (below).
- **Failure entry F29** (`docs/agents/claude-desktop-failures.md`): it claims line 16 (2026-11-22T00:50:34Z, rule `write-allowlist`, tool `Write`, `reviewer`) and line 17 (2026-11-22T00:51:51Z, rule `no-heredocs`, tool `Bash`, `reviewer`). The log lines match in time, rule, tool and agent; count (2 attempted, 2 refused, 0 through) matches. It was committed in `32cde84` with revision 6. Its Status is `open`, the owner's field. It states "fifth time in three runs"; I did not recount earlier entries (not read again beyond the numbers), so that count is the coordinator's.

### New finding in revision 7

**F33 (Nit) — The round 4 amendment dates the owner's signature Nov 21 and his decisions Nov 22**
- **Pass:** Compliance (traceability; a date an agent or a later reader may use to order events) and Bugs (consistency).
- **Location:** `PHASE_4_PLAN.md`, round 4 amendment: `**Amendment approved by:** Michael Hay on Nov 21, 2026`, against the Provenance ("decided F28 in chat on Nov 22, 2026"), Task 66 and 67 Sources ("Nov 22, 2026") and the answers to Open questions 1 and 2 ("2026-11-22").
- **Evidence:** `git log --format='%h %ad' --date=iso` for the commits `b2bad35`, `0df5d0d`, `7df5d38`, `7ef9f3d`, `f9ead7d` shows all five on 2026-11-21 (20:25 to 20:49, -0800). The decisions are dated Nov 22 (that is the UTC day, as the guard log's timestamps), the signature Nov 21 (the local day). Read literally, the signature on Nov 21 comes before the decisions it signs (Nov 22), against the order in git (answers `0df5d0d` before signature `7df5d38`). It does not change the order check, which git settles, but a reader who uses the text would be misled; the same UTC/local gap was noted for the failure entries in revision 6.
- **Direction:** the planner or owner picks one date convention for the amendment (the local day, Nov 21, or the UTC day) and applies it to the signature, the Provenance and the answers. The owner may leave it: the signature is the owner's text, so the reviewer does not suggest editing it silently.
- **State:** open

### Other checks (revision 7)

- **Security.** `git diff 85b52a2..HEAD` read for credentials and personal data: none. The sample strings (`secretco`, `ops@secretco.com`, `intranet.big-corp.net`) are deliberate test samples; `secretco` is not a real organization I can identify (unverified). The owner's private file `~/.manifold/excluded_terms.json` was never opened, read or printed by me; every scan I ran passed an explicit `--terms-file` (the coder's `empty_terms.json` and `terms_secretco.json`, used as arguments only, content not read by me) or no terms file where the scan failed before reading it. A run with no `--terms-file` was not made.
- **README accuracy.** Each of the four sentences in step 3 matches `scan.py` (above). One cosmetic point, not reported as a finding: the sentence is wrapped with a short line (`token-shaped strings and`) at `README.md:30`, and `scan.py:104` keeps an unused loop variable `m` in the email loop; neither changes behavior.
- **Context files.** `AGENTS.md`, `CLAUDE.md` and `REVIEW.md` are not made out of date by this change.
- **Test plan check.** No `PHASE_<N>_TEST_PLAN.md` in this change.
- **Real-use evidence.** The scan on a real source with the owner's term list, and a person following README step 3 with the new output: **no evidence yet**; `SIGNOFFS.md` has no row by design, and the owner's own first run is still his step.
- **CI (the head).** I read both runs with `gh run view`: `ci` 44986843560 `completed`, `success`; `server` 44986843643 `completed`, `success` (status and conclusion only; I did not read the job list or the Linux and Python 3.12 job logs).
- **Held-out scenarios.** I did not read any.

### Gates run (revision 7, 2026-11-21, head `f9ead7d`, Python 3.11)

| Command | Counts | Result |
|---|---|---|
| `cd server && ../.venv/bin/python -m pytest tests/datasets -q` | `16 passed, 1 warning` | pass; equals the coder's `16 passed` (one more than revision 6's 15: the new test) |
| `cd server && ../.venv/bin/python -m pytest -q` | `1144 passed, 5 xfailed, 33 warnings in 122.76s` | pass; equals the coder's `1144 passed, 5 xfailed` (1143 plus the new test) |
| `.venv/bin/python -m pytest tests/live -q` | `24 passed in 0.05s` | pass |
| `.venv/bin/python tools/vendor_web.py --check` | `vendored files match a fresh build` | pass |
| `.venv/bin/python -m pytest bundles/base/tests -q` | `2108 passed, 1 skipped in 19.05s` | pass |
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |
| `scan.py server/tests/datasets/curated --terms-file .manifold/scratch/empty_terms.json` | `scan: no findings`, exit 0 | as intended |
| `scan.py .manifold/scratch/sample --terms-file .manifold/scratch/terms_secretco.json` | `page.md:1: email`, `page.md:1: host`, `page.md:1: term`, exit 1 | as intended |
| `scan.py server/tests/datasets --terms-file .manifold/scratch/empty_terms.json` | 14 lines `file:line: kind`, exit 1 | no text printed |
| inline mutation: `Finding.__str__` appends text, `-k scan` | `2 failed, 3 passed, 11 deselected` | the changed host assertion and the new test fail |
| inline mutation: `main` drops the `scan: no findings` line, `-k scan` | `1 failed, 4 passed, 11 deselected` | the silence assertion's replacement fails |

### Could not check (revision 7)

- Linux, Python 3.12 and Python 3.10 by me (CI for the head is `success` by status only, read above); the owner's real term list (never read, by design).
- The order "tests failing first, then the code" inside `7ef9f3d` (one commit): it rests on the Task 66 note and my own mutations.
- A `UnicodeDecodeError` from a terms file that is not UTF-8 (argued by reading, not run: it would need a fixture I cannot write).
- The owner's chat decisions (read only as the plan records them), the coder's chat report, commands the guard does not log, and the content of the guard's `command` fields past 80 characters.
- The checkpoint 1 and 2 findings (F4, F9, F10, F11, F26, F27) were not re-reviewed and keep their State.

### Rule exceptions compared (revision 7)

- **Coder, CP10:** compared above: `none` against a log with no coder line after line 15 (17 lines before and after the coder's run, per its note, and 17 when I started). The Task 71 line (CP3) matches lines 14 and 15. Failure F29 matches lines 16 and 17.
- **Mine:** I wrote this file with `Edit`. I ran read-only `git`, `grep`, `sed`, `wc`, `cut`, `tail`, `ls`, `gh run view` (status only), the project's gate commands (each alone), `scan.py` with an explicit `--terms-file` pointing at the coder's gitignored fixtures (and for the error paths a missing file and a non-JSON file, `page.md`, as the terms file), and two inline `python -c` mutation runs that patch `tests.datasets.scan` in memory and call `pytest.main` (no file written). The guard log had 17 lines before my commands and 17 after (`wc -l`, `tail -n +18` printed nothing): **none of my commands was refused**, and I did not write or ask for a fixture. `.manifold/guard-allow.json` was not read; I saw no sign an exception was used.

### A human decides (revision 7)

This review does not approve or block the change. A human approves, informed by the findings. Counts after revision 7: Important 1 open (F4, owner-gated, checkpoint 1); Nit 6 open (F9, F10, F11, F26, F27 from earlier revisions; F33 new); repaired since revision 6: F28, F29, F30, F31, F32. The Review process approval rule in `AGENTS.md` (solo repository, owner Michael Hay) applies: no second approver is required.

## CP3 revision 6: curated test data sets (Tasks 23 to 27)

### Verdict

One Important finding (F28, the scan prints matched emails and hosts, which can carry a private term) and four nits (F29 to F32). Everything else asked for holds. Evidence is mine, run on head `85b52a2` on Python 3.11.3. Only test files, test data, a README, a sign-off table and plan and failure notes changed: `git diff --name-status origin/main..HEAD` shows 24 `A` and 2 `M` (the plan and the failures file), so no server code and no existing test was changed.

### What was checked and holds

- **Files, scope and size (Task 23, plan "Files").** All 24 created files are under `server/tests/datasets/`; the plan names `curated/messy/`, `curated/hostile/`, `loader.py`, `README.md`, `SIGNOFFS.md`, `scan.py` and `test_datasets.py`, and the Task 24 Change text names the `dataset` fixture in the datasets test module, so `test_datasets.py` appearing in Task 24 is in the plan. `du -sk server/tests/datasets/curated` prints `76` (under 200). `load_config` loads both sets: `test_the_sets_cover_every_awkward_case` calls `load_config(messy).slugs()`, `tool_world` calls `load_config(root).slugs()` for the hostile set, and both pass. `git status --short` is empty.
- **The curated data is wholly fictional (Task 23, INT-3 "No personal data").** I read all 19 files under `curated/` (messy 12, hostile 7, each including its `manifold.yaml`). Hosts are `example.test` and `hostile.example.test` only (`grep -rnoE "https?://..."` lists five URLs, all `.test`). `grep -rniE "megaroast|mediumroast|mihay|michael|sk-|ghp_|BEGIN .*PRIVATE"` over `curated/` printed nothing. Teams are "Team Dot", "Team Dash", "Team Orders", "Team Harbor"; no person is named, no email address, no key.
- **Awkward cases present (Task 23 Change).** Dotted slug `acme.io` and look-alike `acme-io`; `no-frontmatter.md`; two pages titled "Retry policy"; `orders-core` page dated 2026-01-10 against the raw note of 2026-02-20; a page in seven scripts (Latin, Cyrillic, Greek, Japanese, Arabic, Devanagari and accents). The long page is generated by `loader.long_page`, not committed (`curated/` holds none). Hostile pages: "ignore your previous instructions", "call the tool wiki_write_page_tool", a fake `SYSTEM:` message, a hidden HTML comment and a hostile frontmatter summary. The three tool names the bait uses (`wiki_write_page_tool`, `wiki_handoff_tool`, `wiki_log_append_tool`) exist (`server/server.py:168`, `:280`, `:334`), so the bait is real, not invented. Every hostile line says it is a test string and does nothing, so INT-3 S2 "Must never: harmful beyond a test string" holds.
- **README and SIGNOFFS (Task 26).** `README.md` holds the awkward cases, the real-data rule in five steps (permission in writing, scrub, check, record, original never committed), and a "Megaroast testbed" section with the organization name and four roles only (fork, standalone GUI, holdout QA repository, example instance). No repository name appears. The holdout QA repository is a role only, with "no builder agent reads the holdout QA repository", as the plan's default says. `SIGNOFFS.md` has the five columns (source, owner, permission date, scrub checked by, scan result), no row, and says no real data is committed. The owner's open question (may the holdout QA repository be named) is correctly left open with its default.
- **The owner's private terms file is never opened by a test (Task 26 (3)).** Read, not run: `scan.py:93-97` reads the default only inside `scan()` when `terms_file is None`; `default_terms_file()` is a function (`:53-55`), so nothing is looked up at import. Every `scan(` and `main(` call in `test_datasets.py` (lines 153, 157, 158, 160, 169, 178, 183, 185, 254, 256) passes a fixture file, except line 198, which first replaces `Path.home` with a function that raises (line 189-191) and then replaces `scanner.default_terms_file` with a stand-in inside `tmp_path` (line 195). So no test path reaches `~/.manifold/excluded_terms.json`. I did not open that file, and I ran nothing that reads it (the one command-line run I made was `scan.py --help`).
- **A private term is never shown by `term` findings or a bad list (Task 26 (2)).** `Finding(..., "term")` has an empty `detail` (`scan.py:116`); `load_terms` raises without quoting the content (`:60-66`); `test_scan_finds_private_terms_without_ever_showing_them` and `test_scan_refuses_a_bad_term_list_without_quoting_it` assert it. See F28 for the corner where an email or host finding can still carry one.
- **The hostile test has teeth (Task 25).** The test (`test_datasets.py:116-140`) compares `body` with the page parsed from disk and finds the bait sentence in `body` or `frontmatter`, runs `wiki_inventory_tool` and `wiki_freshness_tool`, and then compares every file of the copy byte for byte (`log.md`, handoffs and pages included), checks the page the bait asks for does not exist, and checks one commit and a clean `git status`. I ran a mutation inline (`python -c`, `pytest.main`, a plugin that wraps `server.wiki_read` so the text comes back altered: `PINEAPPLE` to `PEAR`, `SYSTEM:` to `S:`; no file written): `1 failed`, the assertion on the page body with `the word PINEAPPLE.` against `the word PEAR.` So an altered text fails. I tried a second mutation (a wrapper that creates `wiki/notes/should-never-exist.md` when the bait page is read) and the guard refused the snippet (see "Rule exceptions compared"); I did not retry. By reading, a created or changed file anywhere in the copy fails `_snapshot(root) == before` (it covers every file except `.git`), a file at the bait path fails the `exists()` check, and a new commit fails the count; a call to `wiki_log_append` writes `log.md`, which is in the snapshot. Limits: the test runs three tools (read, inventory, freshness), so it proves those three do not act on the text, not that every tool is safe; an action with no effect on disk (a network call) would not fail it.
- **Task 27 coverage and personal-data tests have teeth.** `test_the_sets_cover_every_awkward_case` has one assertion with a message for each case: a dotted slug (`"." in s`), look-alike slugs (equal once `.`, `-`, `_` are removed), a page with no frontmatter (not `CLAUDE.md` or `log.md`), a duplicate title, the stale page through `wiki_freshness` (exactly `["orders-core"]`), a long page (200 000 characters written into the copy and read back whole through `wiki_read`, health still ok), at least three non-Latin scripts, and AI-aimed text in `hostile`. Removing the case from the data makes the matching assertion fail; I did not edit the data to prove it (I may not), I read each assertion against the data. `test_no_set_contains_personal_data` first shows that the email check and the name patterns fire on a made-up sample (`{"email", "pattern"}`), then scans each committed set. A first name followed by a capitalised word in any page fails it. Limits are in F32.
- **No string-joining to dodge the scanner (item f).** The token, hash and email samples in `test_datasets.py:145-151` and `:253` are plain literals, written as the scanner should catch them. The only join is `"|".join(_FIRST_NAMES)` (`:248`), which builds the name pattern from the list; it hides nothing. No committed file under `curated/` holds a string built to avoid the scan, and the scan over `curated/` is clean (next bullet).
- **The scan over `curated/` is clean.** Proved by the test run, not by a command-line run of mine: `test_scan_flags_real_shaped_text_and_passes_the_committed_sets` asserts `scanner.scan(loader.CURATED, terms_file=no_terms) == []`, and `scanner.main([CURATED, "--terms-file", no_terms]) == 0` with empty output, where `no_terms` is a fixture file holding `[]` made in `tmp_path`. It passes in the full run and in `tests/datasets`. The explicit-file command-line run I planned (an empty list in the session scratchpad) could not be done: the guard refused my write of that file (see "Rule exceptions compared"), and I did not find another way to get the file.
- **No existing test edited, no server code changed (item h).** Only `A` files besides the plan and the failures file; `server/` outside `server/tests/datasets/` is untouched; this is a new test folder, so there is nothing in it to edit. The plan's Verification line ("`git diff --stat` for the checkpoint lists only `server/tests/datasets/`") holds apart from the two documents that carry the notes and failure entries.
- **Commits.** Seven commits, all with the attribution line; the message of each names the task. I cannot see staging commands or `--no-verify` in git, so I report only that I saw nothing that suggests either.

### The seven recorded deviations (item a)

| Deviation (where recorded) | Judgment | Reason |
|---|---|---|
| `body` instead of the plan's "content field" (Task 25 note) | acceptable | the tool returns `body`; the test checks it against the page as parsed from disk, so the plan's meaning is met. The plan text is not amended, which is the planner's housekeeping, not a finding |
| dates returned as text, compared with `str()` (Task 25 note) | acceptable | the tool returns dates as text; the test pins that form exactly, so a changed form fails it |
| `copy_curated(tmp_path, name)` against the acceptance line's `copy_curated("messy")` (Task 24 note) | acceptable | the plan's Change line gives the two-argument signature and the acceptance line a one-argument call; the `dataset(name)` fixture gives the second form. The plan contradicts itself and the coder said so |
| the extra helper `curated_names()` (Task 24 note) | acceptable | used to refuse an unknown or path-like name (`"../messy"`); the test passes and covers it. Small, in scope |
| the extra `scan(..., extra_patterns=())` parameter (Task 26 note, item 4) | acceptable | the plan asks for a first-name-plus-surname list "kept in the test" and run through `scan`; the term list holds literals only, so a pattern argument is the smallest way. The plan's signature still works unchanged |
| hosts taken from URLs only; a bare host with no scheme is not caught (Task 26 note, item 1) | nit (F30) | stated in `scan.py`'s docstring, but README step 3 says the scan reports "hosts" without the limit |
| private-key blocks not scanned until Task 36 (Task 26 note, item 5) | acceptable | Task 36 exists (`PHASE_4_PLAN.md:649`) and is about exactly this; the limit is recorded |

### New findings in revision 6

**F28 (Important) — `scan` prints the matched email address or host in a finding, so a private term can reach the output**
- **Pass:** Security (a private list's content in output) and Compliance (Task 26: "the list is never committed or printed"; `scan.py` docstring: a finding "never carries the matched text for a token or a term").
- **Location:** `server/tests/datasets/scan.py:106` (`Finding(shown, number, "email", m.group(0))`), `:110` (`Finding(shown, number, "host", host)`) and `:49-50` (`__str__` appends the detail); the test that pins the printing: `test_datasets.py:161` (`"sample.md:2: host intranet.big-corp.net"`).
- **Evidence:** by reading, not by a run (a run needs a term file, which I could not write). A line such as `mail ops@secretco.com or see https://www.secretco.com/x` with the private term `secretco` gives three findings: `term` (no text, as designed), `email ops@secretco.com` and `host www.secretco.com` (both print the text). The term is then printed, which the plan and the docstring say it never is, and which the terms file exists to prevent: a private list holds the names an owner must not leak, and those names are exactly what appears in the host and email domain of a real source. Your brief for this review said a finding is `path:line:kind` and never the matched text; the code does not do that for two of its five kinds. The Task 26 note says only that tokens and terms carry no text. Where it is printed: the owner's terminal (README step 3) or whatever logs it; the scan is not in CI. So the exposure is local, which is why I did not weigh it more than Important, and it is a corner (a term inside an email or URL host), not the common case.
- **Direction:** print `path:line: email` and `path:line: host` without the text, like the other kinds (the person reads the line number in the file), or print the text only when no private term appears in it; change the one assertion that pins the host text and add a case where the term sits inside a host and an email and is absent from the output. The owner may decide that an email or host from a scrub candidate may be printed in the owner's own terminal; then the docstring and README should say that the output can hold them, and the finding becomes a nit.
- **State:** repaired (rev 7). Evidence in "CP3 revision 7" (F28 section): `Finding` has no `detail` field (`scan.py:43-49`), every kind prints `path:line: kind`, and the command line shows it on the owner's decided option 2.

**F29 (Nit) — A clean scan prints nothing and exits 0**
- **Pass:** Bugs (usability of the check) and Tests.
- **Location:** `scan.py:132-134` (`main` prints only findings) and `test_datasets.py:159` (`assert capsys.readouterr().out == ""`, which pins the silence).
- **Evidence:** the plan's acceptance says "prints no finding", so this is as specified; the owner has already read a silent success as "nothing happened" (your brief). Exit 0 with no output looks the same as a scan that did not run.
- **Direction:** print one line on success (for example the number of files scanned and "no findings") and change the one assertion; or leave it and say in README step 3 that a clean scan prints nothing. The owner may leave it.
- **State:** repaired (rev 7). `scan.py:133-134` prints `scan: no findings` and exits 0; the assertion at `test_datasets.py:159` is now `== "scan: no findings\n"`; the owner said yes (Open question 1). Run by me: the line and exit 0 on `curated/` with the coder's empty-list fixture.

**F30 (Nit) — README says the scan reports "hosts"; it reports only hosts inside URLs**
- **Pass:** Bugs (consistency) and Compliance (INT-3 S3: a checked scrub).
- **Location:** `server/tests/datasets/README.md`, "The real-data rule", step 3 ("It reports emails, hosts not ending `.test`, `.example` or `.invalid`, ..."); `scan.py:7-9` and `:36` (`_URL_HOST` needs `scheme://`).
- **Evidence:** the docstring and the Task 26 note say a bare host name (`intranet.big-corp.net` with no `https://`, or `db1.corp.net:5432`) is not caught; the README leaves the limit out. A person following README step 3 could take a clean scan as "no real hosts". The README does say the scan "finds what it is shaped to find" and that a person then reads the set, which softens it.
- **Direction:** add "in URLs (`scheme://host`)" to the README sentence, with one sentence that a bare host is for the reader to find; or widen the scan to bare dotted names that end in a known top-level domain (the plan would need the owner's word, since `acme.io` is a deliberate slug). The owner may leave it.
- **State:** repaired (rev 7) for the README wording; the widening of the scan is deferred in the signed amendment. `README.md:29` says "hosts in URLs (`scheme://host`)" and `:32-33` says a bare host name with no scheme (`db1.corp.net:5432`) is not caught, so the reader looks for it. Matches `scan.py` (`_URL_HOST` needs `scheme://`).

**F31 (Nit) — The coder's Rule exceptions line for checkpoint 3 is not in the plan notes or the commit messages**
- **Pass:** Compliance (`AGENTS.md` "Rule exceptions"; the same point as F17 for checkpoint 2, repaired in revision 4).
- **Location:** `PHASE_4_PLAN.md` CP3 notes (Tasks 23 to 27 and the CP3 gates note at line 542) and the seven commit messages.
- **Evidence:** `git diff origin/main..HEAD -- docs/plans/PHASE_4_PLAN.md | grep -ic "rule exception"` prints `0`, and `git log origin/main..HEAD --format=%B | grep -i "rule exception"` prints nothing. The line exists only in the coder's chat report, which I cannot read; failure entry F28 paraphrases it ("its Rule exceptions line listed the refusal"). The comparison I could make is below, and the entries F27 and F28 match the log.
- **Direction:** the coder writes the line into the CP3 gates note so it travels with the pull request, as it did for checkpoint 1 and, after F17, checkpoint 2.
- **State:** repaired (rev 7). `PHASE_4_PLAN.md` now has "Rule exceptions (CP3, coder)" after the CP3 gates note (Task 71); it matches guard log lines 14 and 15 (see "Task 71 line checked" in the revision 7 section). It was written from the log and failures F27 and F28, not from the coder's own report, and says so.

**F32 (Nit) — The personal-data test knows 30 English first names, and one assertion message is wrong**
- **Pass:** Tests (strength) and Bugs.
- **Location:** `test_datasets.py:245-248` (`_FIRST_NAMES`, `_NAME_PATTERNS`: a first name, whitespace, a capitalised word) and `:238` (the message `"text in fewer than two scripts besides Latin"` against the assertion `>= 3`).
- **Evidence:** the pattern catches "Maria Garcia" (the sample proves it fires) and any other name on the list, written with capitals. It does not catch a name not on the list ("Priya Sharma"), a lower-case name, a surname first, or a name in another script, and `Alex` and `Sam` can match ordinary two-word phrases. That is what the plan asked ("a first-name-plus-surname pattern list kept in the test"), so this is a limit, not a departure; the real protection is the owner's term list plus a person reading, as README says. The message at `:238` says "two" and the assertion needs three non-Latin scripts; if it fails, the text misleads.
- **Direction:** correct the message to "three"; note the limit in the test's comment; optionally add the owner's term list through the owner's own run. The owner may leave it.
- **State:** repaired (rev 7) in the parts the owner approved: the message now reads "fewer than three scripts besides Latin" (`test_datasets.py:256`, assertion `>= 3` unchanged) and a three-line comment above `_FIRST_NAMES` states the limit (30 English first names; I counted 30) and the real protection. The list was not extended, by the owner's answer to Open question 2.

### Failure entries F27 and F28 against `.manifold/guard-log.jsonl`

The log had 15 lines when I started (17 now; lines 16 and 17 are mine, see below).

| Entry | Claim | Guard log | Result |
|---|---|---|---|
| F27 (coder, first run, set aside) | 1 refused `Bash` heredoc, 2026-11-21T14:32:36Z, `no-heredocs`, line 14; log had 13 lines before | line 14: 2026-11-21T14:32:36Z, rule `no-heredocs`, tool `Bash`, agent_type `coder`, command starts `cd /Users/.../ser` | matches in time, rule, tool and agent; count (1 attempted, 1 refused, 0 through) matches; 13 lines before is consistent with my revision 5 count (13 lines then). "Heredoc `cat >> /dev/null <<'EOF'`" is the coder's statement: the log cuts the command at 80 characters, so I only see the rule and the first characters. The entry says the "Rule exceptions: none" line was wrong; that line was in the first run's chat report, which I cannot read |
| F28 (coder, second run) | 1 refused `Bash` heredoc, 2026-11-22T00:35:28Z, `no-heredocs`, line 15; line 14 is F27 | line 15: 2026-11-22T00:35:28Z, rule `no-heredocs`, tool `Bash`, agent_type `coder`, command starts `cd /Users/.../ser` | matches; the entry's "one more coder entry than it could account for is F27" fits lines 14 and 15; count matches. The time is UTC, the entry's date is the local day after (2026-11-22 for a 00:35Z line; line 14's 14:32Z is the 21st): consistent |

Both entries have Status `closed` and "Disclosed by the agent: Yes"; those fields are the coordinator's and the owner's. F28 says the same slip twice after an explicit warning "suggests the coder's own text may need a line"; that is the owner's call and I do not raise it as a finding. The two entries carry no secret and no personal data.

### Rule exceptions compared (revision 6)

- **Coder, CP3 (second run):** the plan notes carry no Rule exceptions line (F31). Compared with the guard log: one refusal in this run (line 15, `no-heredocs`), matching F28 and the paraphrase of the line in F28; line 14 belongs to the set-aside first run (F27). No other coder line since the last revision, so I find no refusal that F27 or F28 omit. The guard logs refusals only, so a command that went through cannot be compared. Commit messages: explicit task names and the attribution line on all seven; nothing shows `--no-verify` or a hook bypass; the commits hold the paths of one task each (`git show --stat 1e4255c` is 20 files, the Task 23 data and the plan). The first run's commands and branch were not read.
- **Mine:** I wrote this file with `Edit`. I ran read-only `git`, `grep`, `cat`, `du`, `ls`, `wc`, the project's gate commands (each alone), `scan.py --help`, and one inline `python -c` mutation run that wrapped `server.wiki_read` and called `pytest.main` (no file written). **Two commands of mine were refused by the guard**, and I did not work around either: (1) log line 16, 2026-11-22T00:50:34Z, rule `write-allowlist`, tool `Write`: my write of an empty term list (`[]`) in the session scratchpad, for the explicit `--terms-file` command-line run you asked for; (2) log line 17, rule `no-heredocs`, tool `Bash`: my second inline mutation (a `python -c` that wrapped `server.wiki_read` to create a file, to show that a tool which writes fails the test); the guard read the snippet as code that writes files. Nothing in either ran. I did not ask for an exception: the tests already scan `curated/` with their own empty fixture list, and the by-reading argument covers the second mutation. That leaves two checks not done as asked, listed under "Could not check". `.manifold/guard-allow.json` does not exist, so no exception was granted or used.

### Other checks (revision 6)

- **Security.** `git diff origin/main..HEAD` read for credentials and personal data: none. The sample strings in `test_datasets.py` (`sk-FAKE...`, a made-up session value, a made-up hash, `intranet.big-corp.net`, `maria@mail.example.test`) are deliberate scanner samples, not real; `big-corp.net` is a host that is not under `.test`, in a test sample, not a real company I can identify (unverified). `loader.py:19-20` holds `datasets@example.test` as the git author. By reading, a scan of the whole `server/tests/datasets/` folder (not only `curated/`) is not clean: it would report the email in `loader.py` and the deliberate samples in `test_datasets.py`; the plan's acceptance is over `curated/` only, so this is not a finding. I did not run it (no term file).
- **Context files.** `AGENTS.md`, `CLAUDE.md` and `REVIEW.md` are not made out of date by this change.
- **Test plan check.** No `PHASE_<N>_TEST_PLAN.md` in this change.
- **Real-use evidence.** The curated sets used by a person writing a new test, and the scan applied to a real source with the owner's term list: **no evidence yet**; `SIGNOFFS.md` has no row by design. The coder's own note says the owner should run `scan.py` over `curated/` once with the owner's list; that is the owner's step and I did not do it.
- **Held-out scenarios.** I did not read any.

### Gates run (revision 6, 2026-11-21, head `85b52a2`, Python 3.11.3)

| Command | Counts | Result |
|---|---|---|
| `cd server && ../.venv/bin/python -m pytest -q` | `1143 passed, 5 xfailed, 33 warnings in 126.56s` | pass; equals the coder's `1143 passed, 5 xfailed, 33 warnings` (the five xfails are the CP2 strict ones) |
| `cd server && ../.venv/bin/python -m pytest tests/datasets -q` | `15 passed, 1 warning in 2.06s` | pass (the warning is the pydantic `dict` deprecation in `server.py`, not from this change) |
| `.venv/bin/python -m pytest tests/live -q` | `24 passed in 0.05s` | pass |
| `.venv/bin/python tools/vendor_web.py --check` | `vendored files match a fresh build` | pass |
| `.venv/bin/python -m pytest bundles/base/tests -q` | `2108 passed, 1 skipped in 16.14s` | pass |
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |
| inline mutation: `server.wiki_read` returns the text altered, `-k "hostile and not copy"` | `1 failed, 14 deselected`, on the page body (`PINEAPPLE` against `PEAR`) | as expected: the hostile test fails when the text is altered |

The coder's note says "the other 8 [of the 23 added] were not traced". I did not trace them either: 1143 minus the CP2 count of 1128 (revision 5) is 15, which is exactly `tests/datasets`; the plan's "1120" baseline was the pre-repair CP2 figure, and the 8 are the CP2 repair tests (1123, then 1128). So the difference is explained by the CP2 repairs and nothing else, as far as the counts show; I did not run a count of the base to prove it.

### Could not check (revision 6)

- Linux, Python 3.12 and Python 3.10, and hosted CI (the branch is not pushed; CI has not run).
- The owner's real term list: never read, by me or by any test, as designed. How `scan` behaves with the real list on a real source is the owner's first run.
- The explicit command-line run of `scan.py` over `curated/` and over `server/tests/datasets/` with an empty list in the scratchpad: my write of that file was refused (log line 16). The in-test equivalent over `curated/` passes; the whole-folder scan was not run.
- A second mutation (a tool that writes a file) on the hostile test: refused (log line 17); argued by reading only.
- The coder's chat report and its Rule exceptions line, the commands that the guard does not log, the content of the guard's `command` fields past 80 characters, and the first run (not read, by instruction).
- Whether the `Task 55`-style owner gate or any other owner-gated item changed since revision 5; the checkpoint 1 and 2 findings (F4, F9, F10, F11, F26, F27) were not re-reviewed and keep their State.

### A human decides (revision 6)

This review does not approve or block the change. A human approves, informed by the findings. Counts after revision 6: Important 2 open (F4 owner-gated from checkpoint 1; F28 new); Nit 9 open (F9, F10, F11, F26, F27 from earlier revisions; F29 to F32 new); repaired since revision 5: none (no earlier finding was part of this change). The Review process approval rule in `AGENTS.md` (solo repository, owner Michael Hay) applies: no second approver is required.

## CP2 revision 5: the CP9 repair (Tasks 63 to 65), F18 and F19, failure entries, gates

### Verdict on the repair (no Important finding)

All four checks asked for hold; evidence is mine, run on head `5598102` on 2026-11-15.

- **Only tests changed, and only the three named files among the recordings.** `git diff 9a28de7..HEAD --name-status -- server` prints three lines: `M` `server/tests/contracts/harness.py`, `test_harness.py`, `wiki_inventory_tool.ok.json`. No file under `server/` outside `server/tests/`, nothing in `.github/` (the plan asked for none), no other recording. `wiki_freshness_tool.ok.json` is untouched, as the Task 64 note says (`fresh` was already in sorted order).
- **Sort keys match the plan.** `harness.py` `UNORDERED_LISTS` (lines 74 to 84): `wiki_inventory_tool`: `all_files` by the string (key `None`), `components` and `handoffs` by `path`; `wiki_freshness_tool`: `fresh` by the string, `stale` and `unknown` by `component`. I checked the source of each: `inventory.py:38` (`rglob`, no sort anywhere; the three lists are appended in walk order), `freshness.py:36-38` (`glob`, slug order drives `fresh`, `stale`, `unknown`). Items carry `path` (components, handoffs) and `component` (stale; read from `wiki_freshness_tool.ok.json`), and the recorded `all_files` and `fresh` are strings. `handoff_list` (`handoff.py:674`) is deliberately not sorted, as in Task 63 (its own sort by priority and `updated` decides); I did not re-derive the claim that the three handoff dates differ, I only read the recording.
- **The sort cannot hide a content difference.** The sort is applied to the actual result in `run_case` (the last step, after `normalise` and `mask_product_versions`), and the recording is stored sorted, so both sides are in the same order; `compare` is untouched and still compares both directions. Run by me inline (`python -c`, no file written): an extra item is reported (`wiki_inventory_tool: result.all_files: expected 2 items, got 1`), a changed field inside a sorted list is reported (`result.components[1].name: expected 'x', got 'z'`), and a list not in the table is left in the tool's order (`wiki_agent_catalog_tool` `['b','a']` stays). The sort keeps duplicates, so a repeated or missing entry still differs. I also checked the re-recording: the `git diff` of `wiki_inventory_tool.ok.json` has 21 removed and 21 added lines, and the only lines that differ in count are the first and last items of a list (trailing comma moved), so the file holds the same items in a new order, and nothing else in the recording changed; `tool_count` and the other fields are not in the diff. (A fuller item-by-item comparison of the old and new file was in a command the guard refused, see "Rule exceptions compared"; the evidence above is the `git diff` count and the passing contract run.)
- **The regression test has teeth.** I ran it myself, inline, no file written: `python -c` importing `tests.contracts.harness`, setting `harness.UNORDERED_LISTS = {}` and calling `pytest.main(['tests/contracts','-q','-p','no:cacheprovider'])`: `5 failed, 44 passed`: the four walk tests (`reversed` and `shuffled`, each for `wiki_inventory_tool.ok` and `wiki_freshness_tool.ok`) and `test_the_tool_still_matches_its_recording[wiki_inventory_tool.ok]` (the walk's natural order on this machine already differs from the sorted recording, so the recording is no longer pinned to the macOS order). `test_the_directory_order_test_can_fail` passes in that run, as it should (it removes the sort itself and expects the named `all_files[0]` difference). This is exactly the coder's `5 failed, 44 passed`. With the sort in place: `pytest tests/contracts -q` from `server/` is `49 passed` (44 before plus the 5 new). The walk tests patch `Path.rglob` and `Path.glob` for the whole test, so they cover every tool in the run, but they run only the two recordings named in `WALKING_RECORDINGS`; a third tool that lists a directory walk would need an entry in both `UNORDERED_LISTS` and `WALKING_RECORDINGS` (see F27).
- **The sort key does not cover a renamed field (F26).** See below.
- **No existing test edited.** `git diff f35fb11~1 f35fb11 -- server/tests/contracts/test_harness.py` is additions only (44 lines appended). No existing assertion changed. No bug fix is in this change in the sense of server code; the failing test the repair answers is the CI failure of run 43727526573, and the new tests fail first without the sort (shown above).
- **Plan claims against what I reproduced.** Task 65: `1128 passed, 5 xfailed` (mine: `1128 passed, 5 xfailed, 32 warnings`), `24 passed`, the vendored line, `2108 passed, 1 skipped`, `lint ok`: all reproduce. The coder's scratch-plugin runs (`49 passed` reversed and shuffled) I did not repeat (the plugin is in the scratchpad and unreadable to me); the in-repo walk tests cover the same patch (reversed and shuffled, seed `20261115`), and they pass. Task 63's acceptance (the order differing between two file orders for `wiki_inventory_tool.ok`) is shown by my own `UNORDERED_LISTS = {}` run above, since the shuffled and reversed walk tests fail without the sort.
- **Real-use evidence.** The CI run for the head, which the task gave me as a fact read by the coordinator: `ci` 43731734105 and `server` 43731734111 for `5598102` are completed, success, all 7 checks. I did not read GitHub Actions myself; the second half of the amendment's Verification line (3.11 and 3.12 server jobs pass on Linux, the system that failed) rests on that reading, and the "no flaky tests" behavior across other file systems is shown by that single run plus the walk tests. Contract-workflow real use by a person (a field changed, only that tool fails): still **no evidence yet**.

### F18 and F19: set from evidence

| Finding | State | Evidence |
|---|---|---|
| F18 | repaired (rev 5) | `eec2f60` rewrote the "Count" and "Suggested change" of F22 in `docs/agents/claude-desktop-failures.md` (lines 348 to 360). The Count now says the coder also started the repair before the signature because the brief told it to, that `REVIEW_CYCLE.md` says the coder does not start a repair before approval, and that "the coder's own rule was also not met (it followed the brief and disclosed everything)". The Suggested change now says the rule already exists and that what is new is a hand-off check: the coordinator's brief must name the signed amendment, and the coder stops if the **Amendment approved by** line is blank or a slug, even when told to go ahead. That is what F18 asked for. The numeric "Count: 1" is still given for the coordinator only, and the entry's **Status** is still `open`; both are the owner's. |
| F19 | repaired (rev 5) | `eec2f60` rewrote the sentence at `PHASE_4_PLAN.md` (the signed round 2 amendment): "The owner's chat instruction of 2026-11-15 (repair F12 and all five nits) started this repair; the owner signed the amendment on 2026-11-15 after the fact." `grep -n "authoriz\|left for the owner" docs/plans/PHASE_4_PLAN.md` finds no "authorizes this repair" and no "slug above is left" (the one `authoriz` hit, line 356, is the conformance note on auth, unrelated). "Before signing, the owner reads" is now "read", past tense. The section no longer contradicts its "After-the-fact review" paragraph. |

### Failure entries F22 to F25 against `.manifold/guard-log.jsonl` (13 lines now; 12 when I started)

| Entry | Claim | Guard log | Result |
|---|---|---|---|
| F22 (coordinator) | order breach, round 2 | not a guard event (the entry says so) | rechecked in revision 4; unchanged apart from the F18 fix; its Status is `open` (owner's) |
| F23 (reviewer) | 2 refused `Write` of a scratch file, 2026-11-15T14:50:10Z and 14:50:12Z, `write-allowlist`, lines 9 and 10 | lines 9 and 10: same times, rule `write-allowlist`, tool `Write`, agent_type `reviewer` | matches; count (2 attempted, 2 refused, 0 through) matches; it states "third time in two runs", consistent with F19 of the failures file and F17 of 2026-11-12 (not re-read by me beyond the numbers) |
| F24 (planner) | 1 refused `git apply --cached --recount` at 15:00:14Z, `no-heredocs` ("git apply changes files"), line 11 | line 11: 2026-11-15T15:00:14Z, rule `no-heredocs`, tool `Bash`, agent_type `planner`, command starts `git apply --cached --recount /private/tmp/...` | matches; the entry's "the coordinator committed the whole file" fits `f1084e1`, whose message says the MarkText re-spacing is included (the diff of `intent/INT-2...` shows the re-spaced item-3 text and one blank line besides the planner's one-line release rule) |
| F25 (bug-coder) | 1 refused heredoc at 15:39:26Z, `no-heredocs`, line 12; `cp -R` into the scratchpad is not a rule question | line 12: 2026-11-15T15:39:26Z, rule `no-heredocs`, tool `Bash`, agent_type `bug-coder`, command starts `grep -n "^updated\|^priority" examples/acme/wiki/handoffs/*/*.md; python3 - <<'E` | matches in time, rule and agent; the command text is cut at 80 characters |

Two details I could not match to the log alone: (a) the Task 65 note and F25 call the refused heredoc "a scan of the recordings for lists", while the first 80 characters of the logged command read the `updated` and `priority` lines of the handoff pages (that fits the Task 63 check of the handoff list order; not a contradiction, but the text is cut, so I only say what the log shows); (b) the entries and notes are the agents' own, and the log shows refusals only, so a `cp -R`, the `cmp` and the scratch plugin cannot be checked against it. The recording copied back with `Write`, not `cp`, is consistent with the commit (`git show --stat f35fb11`: three code files in `server/tests/contracts/` plus the plan).

Line 13 of the log is mine (2026-11-15T20:34:44Z, rule `no-heredocs`, agent_type `reviewer`); see "Rule exceptions compared (revision 5)". The F25 entry says "line 12" and that line is the bug-coder's, which holds. `.manifold/guard-allow.json` was not read for this revision; revision 4 found it absent, and I saw no sign that an exception was used.

### Rule exceptions compared (revision 5)

- **Bug-coder, Tasks 63 and 64 notes:** carry no Rule exceptions line. The Task 65 note holds the CP9 line: one `Bash` heredoc refused (`no-heredocs`, not worked around, redone with a file written with `Write`); `cp -R` of `server`, `examples`, `bundles`, `assets` into the scratchpad for the recorder; nothing copied back with `cp`; "otherwise none". Compared with the guard log: one `bug-coder` line (line 12, 15:39:26Z, `no-heredocs`), no other bug-coder line, so the refusal count matches. `cp -R` and `cmp` are not logged (the guard logs refusals only); the commit holds the three files named above and the plan, so the repository side matches "nothing copied back". Commit `f35fb11`: explicit paths (4 files, the plan included), attribution line present, no `--no-verify` visible, no hook bypass. The commit message (CI run 43727526573) names the cause and says "Tests only; no server code changed", which the diff confirms. The rule-exceptions line sits on Task 65 only, which is what the plan's acceptance asks for; it covers all of CP9.
- **Planner (F24) and coordinator (F25, F23 entries):** compared in the table above.
- **Mine:** I wrote this file with `Write` and `Edit`. I ran read-only `git`, `grep`, `sed`, `cat`, `wc`, `ls`, `python3 -c` with small read-only snippets (no file written, nothing in `/tmp` by me), the project's gate commands, and inline `python -c` runs that import `tests.contracts.harness` and call `pytest.main` or the sort function. **One command of mine was refused by the guard**: 2026-11-15T20:34:44Z, rule `no-heredocs`, tool `Bash`, log line 13; it was one compound command that ran the five gates and also held a `python3 -c` that used `subprocess` to read an older version of the recording with `git show` (the guard's message: python code that "writes, copies, moves or deletes files, or runs a command"). Nothing in it ran. I did not rerun that python snippet or get its result another way: I ran the five gates alone (they were not what the guard refused), and for the recording I used the `git diff` line counts and the contract run instead, which is a different and weaker check than the one refused (it cannot show that every item is identical, only that the line counts and the contract pass agree). I did not ask for an exception because the weaker evidence is enough for this finding set. No other refusal. Where an earlier revision of mine hit `write-allowlist` (lines 9 and 10), I did not write a scratch file this time.

### New findings in revision 5

**F26 (Nit) — A tool that renames the field used as a sort key makes the contract test error with a bare `KeyError`, not a named difference**
- **Pass:** Tests (strength of the contract; INT-2 S1: a changed field names the tool and the field; the harness's own first test promises it) and Bugs (error handling).
- **Location:** `server/tests/contracts/harness.py:93` (`sorted(result[field], key=(lambda item: item[key]) if key else None)`) inside `order_unordered_lists`, called from `run_case`.
- **Evidence:** run by me, inline (no file written): `order_unordered_lists('wiki_inventory_tool', {'components': [{'paths': 'b'}, {'paths': 'a'}], 'handoffs': [], 'all_files': []})` raises `KeyError: 'path'`. So if the tool renames or drops `path` in a component or handoff entry, or `component` in a `stale` or `unknown` entry, the contract test for that recording errors inside `run_case` before `compare` runs. The test still goes red (it is not hidden), but the message is `KeyError: 'path'` and a stack trace, not `wiki_inventory_tool: result.components[0].path: expected str, got missing`, which is the form the plan and the F13 self-test describe. The F13 self-test (`test_a_renamed_field_in_one_tool_leaves_the_other_recordings_alone`) renames the top key `components`, which the sort skips (`isinstance(result.get(field), list)`), so it does not meet this case. An item that is not a dict (a string in `components`) would raise `TypeError` the same way.
- **Direction:** make the sort tolerate a missing key (a key function that returns a fixed value for an item without the field, for example by `get`), so `compare` reports the named difference, and add one case to the harness tests (a renamed `path` in `components` names the tool and `result.components[0].path`). The owner may leave it: the test fails loudly either way, and the cost is the readability of the failure.
- **State:** open

**F27 (Nit) — Two small accuracy points: the plan text says 35 recordings, and the walk tests cover only the two named recordings**
- **Pass:** Compliance (accuracy of the plan text) and Tests.
- **Location:** `PHASE_4_PLAN.md` Task 63 (Change text "which of the 35 recordings" and the note "a scan of all 35 for lists of 2 or more items"); `server/tests/contracts/test_harness.py:124` (`WALKING_RECORDINGS = ["wiki_inventory_tool.ok", "wiki_freshness_tool.ok"]`).
- **Evidence:** `ls server/tests/contracts/*.json | wc -l` prints `34` (revision 4 also counted 34 recordings and 16 tools); the plan says 35 in two places, which would be the count before the F15 recording or a miscount, I cannot tell which. The walk tests run only the two named recordings, with `Path.rglob` and `Path.glob` patched for each; a new tool that lists a directory walk, or a new recording of an existing walk tool, is covered only if someone adds it to both `UNORDERED_LISTS` and `WALKING_RECORDINGS`. `test_every_registered_tool_has_a_contract` cannot catch that, and the Task 63 diagnosis is a one-time scan.
- **Direction:** correct "35" to "34" (the owner or planner; the signed amendment is the owner's text, so the reviewer does not suggest editing it silently), and, if wanted, make `WALKING_RECORDINGS` every recording, so a walk-order change in any tool fails by itself rather than relying on the table (the full contract set is about 12 s, so running all 34 under reversed and shuffled walks is cheap). The owner may leave it.
- **State:** open

### Other checks (revision 5)

- **Security.** `git diff 9a28de7..HEAD` read for credentials and personal data: none added; the recording holds fictional Acme paths only; the failure entries carry no secret.
- **Context files.** `AGENTS.md`, `CLAUDE.md` and `REVIEW.md` are not made out of date by the repair. `docs/agents/claude-desktop-failures.md` (F22 to F25) and `intent/INT-2-test-hardening-and-contracts.md` (the release rule, "decided by Michael Hay on Nov 15, 2026, in chat", written by the planner in `f1084e1` with the owner's re-spacing) changed. I did not compare the wording of the release rule with the owner's chat words (not readable); it matches the plan's statement that Task 22 stays deferred, and it fills the placeholder that revision 4 noted (`INT-2:63`). The "Must never: Skip the conformance run for a release" line is read with the exception by the new text; that is the owner's decision as recorded.
- **Process record, signature order.** The amendment was signed (`6b0c57f`) before the repair (`f35fb11`): `git log --oneline` shows `d0ac219`, `6b0c57f`, `f35fb11` in that order, and the bug-coder's note is dated the same day. The coordinator's hand-off check proposed in F22's new Suggested change was in effect here, as far as git shows (the coder started after the signature); whether the coordinator's brief named the signed amendment I cannot read.
- **Test plan check.** No `PHASE_<N>_TEST_PLAN.md` in this change.
- **Held-out scenarios.** I did not read any.

### Gates run (revision 5, 2026-11-15, head `5598102`)

| Command | Counts | Result |
|---|---|---|
| `cd server && ../.venv/bin/python -m pytest -q` | `1128 passed, 5 xfailed, 32 warnings in 129.32s`; Python 3.11 | pass (revision 4: `1123 passed, 5 xfailed`; the 5 added are the CP9 tests) |
| `cd server && ../.venv/bin/python -m pytest tests/contracts -q` | `49 passed` (44 before plus 5) | pass |
| the same with `harness.UNORDERED_LISTS = {}` (inline `python -c`, `pytest.main`, no file written) | `5 failed, 44 passed` | as expected: the four walk tests and `test_the_tool_still_matches_its_recording[wiki_inventory_tool.ok]` fail; the self-check test passes |
| `.venv/bin/python -m pytest tests/live -q` | `24 passed in 0.05s` | pass |
| `.venv/bin/python tools/vendor_web.py --check` | `vendored files match a fresh build` | pass |
| `.venv/bin/python -m pytest bundles/base/tests -q` | `2108 passed, 1 skipped in 17.59s` | pass |
| `python3 bundles/base/tools/build.py --check` | `lint ok` | pass |

I did not run `phase_status.py 4` in this revision. Python 3.11 only on this machine; 3.12 and Linux are covered by the CI facts the coordinator gave me (`ci` 43731734105 and `server` 43731734111, completed, success, all 7 checks, for `5598102`); I did not read them myself, so they are cited as given.

### Could not check (revision 5)

- GitHub Actions itself (the two run ids are the coordinator's reading), Python 3.12 and Linux here.
- The coder's scratch plugin runs (reversed `49 passed`, shuffled `49 passed`): the plugin is in the scratchpad; the in-repo walk tests cover the same patch and pass.
- A full item-by-item comparison of the old and new `wiki_inventory_tool.ok.json` (the command was refused; see above).
- Whether the diagnosis was shown to the owner before any change (Task 63's acceptance wording), which is a chat matter.
- The coordinator's brief and transcripts, the content of the guard's `command` fields past 80 characters, and `.manifold/guard-allow.json` for this revision.
- Task 22 is deferred by the owner's decision and is not reported as missing; its Completion checklist line ("No [~] blocked items outstanding") and Task 55 `[~]` stay the owner's.

### A human decides (revision 5)

This review does not approve or block the change. A human approves, informed by the findings. Counts after revision 5: Important 1 open (F4, owner-gated, checkpoint 1); Nit 5 open (F9, F10, F11 from checkpoint 1; F26, F27 new); repaired since revision 4: F18 and F19. The CP1 findings F4, F9, F10 and F11 were not re-reviewed and keep their revision 2 State. The CP9 repair itself has no Important finding.

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
- **State:** repaired (rev 5): `eec2f60` rewrote the Count and the Suggested change of F22 as asked (see "CP2 revision 5").

**F19 (Nit) — The signed amendment still says the slug is unsigned and that a chat instruction authorizes the repair**
- **Pass:** Bugs (consistency of the plan text).
- **Location:** `docs/plans/PHASE_4_PLAN.md:1019` ("The owner's chat instruction (2026-11-15: repair F12 and all five nits) authorizes this repair; the slug above is left for the owner's own name."); `:1021` ("Before signing, the owner reads: ..."); against `REVIEW_CYCLE.md:12-13` and `:18` (approval is the name and date on **Amendment approved by**, a human's, before the repair).
- **Evidence:** the line is signed (`:1014`, `Michael Hay on Nov 15, 2026`), so "the slug above is left for the owner's own name" is no longer true, and "authorizes this repair" asserts that a chat message does what the process text gives to the signature. The same section's "After-the-fact review" paragraph says the opposite (the repair ran ahead of the signature and the owner accepted it), so the section contradicts itself. A coder or reviewer reading the plan later could take the first sentence as a precedent. (The `Instructions` line at `:1015` is left after signing, as in round 1 at `:769`; that is the template's habit and I do not raise it.)
- **Direction:** the owner may reword the two sentences to say what happened (the owner instructed the repair in chat, the repair ran before the signature, the owner signed on Nov 15 after reading) and leave out "authorizes". It is the owner's text; the planner and the coder do not edit the signed line.
- **State:** repaired (rev 5): `eec2f60` reworded the sentence to the past tense and removed "authorizes" and "the slug above is left" (see "CP2 revision 5").

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
