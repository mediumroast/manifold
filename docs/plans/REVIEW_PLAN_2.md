# REVIEW_PLAN_2.md

**Phase:** whole plan, `docs/plans/PHASE_2_PLAN.md` (CP1 to CP9, CP2a and CP2b, T1 to T58)
**Intent:** INT-20 (`intent/INT-20-agent-guardrails-hold.md`), INT-21 (`intent/INT-21-review-to-repair-loop.md`), INT-22 (`intent/INT-22-coordinator-agent.md`), INT-23 (`intent/INT-23-review-policy.md`), INT-25 (`intent/INT-25-skeptical-test-planner.md`)
**Commit reviewed:** `53df8cff3de2122159ec820fa05e0900644147b1`, branch `claude/intent-agent-process-afd0ed` (PR #28, draft). `git rev-parse HEAD` and `git rev-parse origin/claude/intent-agent-process-afd0ed` both print this hash: they do not differ.
**Plan version:** last commit of `PHASE_2_PLAN.md` is `53df8cff3de2122159ec820fa05e0900644147b1`; **Approved by:** Michael Hay on November 6, 2026; **Amendment approved by:** Michael Hay on November 7, 2026 (CP2a), November 7, 2026 (CP2b), November 8, 2026 (CP8)
**Policy used:** `REVIEW.md` (repository root, present), with the review standard (a) to (g) for documents and agent instructions from `docs/process/REVIEW_CYCLE.md`. The `Review process` section of `AGENTS.md` says solo repository, no companion quality repository, no second approver: the second-approver rule does not apply to this change. The change adds no text that sets an approval rule of its own, and I invented none.
**Revision:** 1, 2026-11-10 19:55

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-11-10 19:55 | 53df8cf | First review |

## Counts by severity

| Severity | Open | Repaired | Deferred | Rejected |
|---|---|---|---|---|
| Important | 2 | 0 | 0 | 0 |
| Nit | 5 | 0 | 0 | 0 |

## Findings

No finding is a hard defect in the guard or the bundle code. The two Important findings are about the plan's own record. I did not write or change any of the reviewed code (independent reviewer, standard (f)).

### Bugs

**F1 (Nit) — write-capable tools that the guard does not refuse are not named in the stated residuals**
- **Location:** `bundles/base/hooks/guard.py:3-80` (docstring), `bundles/base/rules/core/no-heredocs.md`
- **Evidence:** I loaded `classify_bash` and ran my own commands (probe script in the session scratchpad, not in the repository). Allowed although they write file contents: `dd if=/dev/zero of=f bs=1 count=1`, `curl -o out.html http://x`, `wget -O out http://x`, `tar xf a.tar`, `unzip a.zip`, `python3 -m json.tool in.json out.json`, `install -m 644 a b`. About 60 other commands behaved as the plan says (see "Gates run"). The generic residual "other languages, editors and tools than the ones named in the shell rule" covers these, so nothing is misstated, but an agent reading the rule ("no shell command writes or changes file contents") is not told the hook looks at a subset.
- **Direction:** Optional: name two or three of these tools in the residual line, or leave it to real use (the coordinator's listing). Not a repair round: CP2b closed guard repair rounds by the owner's direction.
- **State:** open

### Security

No finding. What I read and ran: the guard's refusal and fail-closed paths through `main` with real hook JSON (exit 2 for a write outside the reviewer's allowlist, exit 2 for unreadable input, exit 0 for the reviewer's own `docs/plans/REVIEW_PLAN_2.md`); about 80 shell probes against `classify_bash` and 13 against `classify_write`, including the CP2a and CP2b named cases (brace expansion, `.github`, code naming a protected path, absolute path to another checkout, case and `..` spellings), all refused as the plan says; the two I expected to pass are the stated residuals (`X=.claude/agents/coder.md; rm $X` and `rm "$(echo .claude/agents/coder.md)"`). I searched the diff added lines for secret-shaped strings and for `/Users/` paths in committed files: none. The scratch-route residual (a script written to `.manifold/scratch/` can reach `.manifold/guard-allow.json`) is stated in the docstring and in "Guard limits and exit codes" with its control; it is a design limit, not a finding.

### Compliance

**F2 (Important) — no coder completion summary, so no "Rule exceptions" line of the Phase 2 coder exists in the repository**
- **Location:** `docs/plans/PHASE_2_PLAN.md:1083-1092` (the checklist item "Summary note added by the coder below this line" is unticked and the template comment is the only content); plan line 101 requires each checkpoint report to carry "Rule exceptions"
- **Evidence:** `grep -n "Rule exceptions" docs/plans/PHASE_2_PLAN.md` finds only plan text, task notes that mention the line, and Phase 1 agents' "none" (lines 981, 985). The per-checkpoint reports of the Phase 2 coder were not committed. What the repository does hold: breach entries F4 to F10 in `docs/agents/claude-desktop-failures.md` (counted from transcripts by the guard's classifier), which say ten breaches went through in the coordinating session and one test-coder heredoc was refused and disclosed.
- **Direction:** The agent that ran the checkpoints (not the reviewer) adds the completion summary with files changed, deviations, gate evidence and a "Rule exceptions" line that agrees with the breach record, or the owner records that the record plus the task notes stand in for it.
- **State:** open

**F3 (Important) — the INT-25 "after" sample departs from T57 and INT-25 on who approves and how the runs were driven**
- **Location:** `docs/plans/PHASE_2_PLAN.md:860-868` (T57 Todo line and the 2026-11-10 note), INT-25 owner decision "A human approves. The test plan carries an **Approved by** line written by a human, never an agent."
- **Evidence:** The note records (a) the Claude Code planner and coder were started by another Claude session, not by a person sending the exact prompt, no model recorded, `verify.md` P.7 is CHECK; (b) both plans carry **Approved by:** Michael Hay "through the coordinator under his limited authority", written by the coordinating session; (c) the planted `INT-1-installer-json-plan.md` was not cited. The owner accepted all of this on 2026-11-10 (T57 Todo line), and the note says one run per client is one sample, not an acceptance of INT-25. I did not read `~/manifold-live-after`; I rely on the note.
- **Direction:** The owner's acceptance is recorded, so nothing to repair. Keep the departure visible when the sample is quoted (the comparison table in T57 does not repeat (a) and (b)); a real-use run should have a person write **Approved by**.
- **State:** open (owner decides whether it is `deferred` with the acceptance as the reason)

**F4 (Nit) — three shipped or traceability statements say the hook has not been seen in a live run, which the plan's own breach record contradicts**
- **Location:** `bundles/base/INSTALL.md:78` and `:91`, `bundles/base/HOWTO.md:120`, plan traceability row "INT-20 S1" ("no live-client evidence yet")
- **Evidence:** `docs/agents/claude-desktop-failures.md:190-198` (F9) and the plan's T37c note record that the live guard refused a `test-coder` heredoc on 2026-11-09 and logged it (`no-heredocs`, `test-coder`); I read the one-line log in the `phase1-test-set-f37394` worktree and it matches. `harness-capabilities.md:86` is accurate for the 2026-11-08 runs only. The error is conservative (it understates enforcement for Claude Code subagents), and standard (b) and (c) ask for no contradiction between documents.
- **Direction:** Say that one live refusal in a Claude Code subagent was recorded on 2026-11-09 (F9), and keep "not seen" for the other rows (Copilot, `--agent`, plugins). The INSTALL text is copied into every install, so change it before a release.
- **State:** open

**F5 (Nit) — the shipped `REVIEW_CYCLE.md` carries this repository's own history and a gendered pronoun**
- **Location:** `bundles/base/process/REVIEW_CYCLE.md:56` ("the owner wrote his name"), section "How the first cycles ran" (lines 52-62)
- **Evidence:** the file is installed to `docs/process/REVIEW_CYCLE.md` in every repository (manifest). The section names Manifold's Phase 2, CP2a and CP2b. The pronoun is used for a person whose pronouns the text does not state.
- **Direction:** Move the history to the plan or the failures record, or say "the owner" without a pronoun.
- **State:** open

### Tests

**F6 (Nit) — a test keeps a name that now says the opposite of what it checks**
- **Location:** `bundles/base/tests/test_bundle.py:1328` (`test_reviewer_is_read_only_and_never_approves`)
- **Evidence:** the reviewer now has an `edit` tool (T21, approved in plan Concern 6); the assertion was changed to `"edit" in tools` with a comment naming the approval.
- **Direction:** Rename it when someone next edits that file; no behavior changes.
- **State:** open

Other Tests-pass checks:
- **Existing tests edited.** Compared with `git diff origin/main...HEAD -- bundles/base/tests/test_bundle.py`: the removed lines are the ones the plan names and approves: the two reviewer tests and the frontmatter-keys tests (T6, T21; plan Concern 6), the 0.1.0 pins (Open question 7, the bump), the `REVIEW_STARTER` tests and the "Human threshold" heading (Open question 6; T20, T22), the `BUILD_ROLES` and `QUALITY_ROLES` constants (T32), the unreadable-input test (T14a, owner decision b) and the Copilot hook assertion (T14a, T14h). Each has a note in the plan. I found no test edited, skipped or weakened without a recorded reason. `server/tests/` is unchanged against `origin/main` (the two flaky-test files in the stale local `main` diff come from merged #30).
- **Failing-first.** Recorded in T3, T9, T14a, T14h, T44, T45 with counts; I did not re-run the failing states (they need the code before each task).
- **Test plan reflection check (INT-25).** The change holds no `PHASE_<N>_TEST_PLAN.md` (the Phase 1 test plan is on another branch). It holds three checker fixtures. `tests/live/plan_check.py` and its 24 tests pass; `skeptical.md` shows none of the five signs and each reflected fixture shows them by design. The reviewer text lists the same five signs as the checker.
- **Real use, standard (d): "no evidence yet" for most scenarios.** One live observation exists: the guard refused a `test-coder` heredoc in Claude Code (F9; see F4). This review is the first real use of the `reviewer` writing its one file; I cannot cite it as evidence for itself. No live Copilot hook refusal was observed (T37b ran the planner only). The `coordinator`, the review-to-repair loop as written, the Copilot hook and the INT-25 text have the one T57 sample (one run per client, deviations in F3) and no more.

### Context files

**F7 (Nit) — "Project commands" in `AGENTS.md` does not list the gates the plan and CI use**
- **Location:** `AGENTS.md:74-77`
- **Evidence:** it lists bundle tests but not `python3 bundles/base/tools/build.py --check` (which prints `lint ok` and which CI runs) or `tests/live`, and says "Lint and type-check: none exist". The plan calls `build.py --check` the "bundle lint" (Prerequisites). The section was confirmed by the owner on 2026-11-01, so changing it is the owner's decision.
- **Direction:** Owner decides whether to add the two commands; the plan states `ci.yml` does not run `tests/live` and leaves wiring it to the owner.
- **State:** open

Otherwise current: the rendered `AGENTS.md` block, `.claude/agents/*`, `docs/process/*`, `docs/templates/*` and `.manifold/hooks/guard.py` match a fresh build of the bundle (see "Gates run"); `REVIEW.md` and the `Review process` section are consistent with each other and with the reviewer text.

## Checklist items that depend on this review

Evidence is the only question I answer; the owner ticks.

- **CP2a** (Completion checklist, line 1078): supported. **Amendment approved by** is filled (line 249); T14a to T14g are `[x]` with notes; the F1 to F10 table is complete; my replay of the named probe classes through `classify_bash`, `classify_write` and `main` agrees with the table; guard tests pass inside the 1954. The "CP2a re-review is in the CP2b table" statement is true (lines 360-384).
- **CP2b** (line 1079): supported. **Amendment approved by** is filled (line 362); T14h to T14m are `[x]`; the R1 to R12 table is complete. "Residuals stated once in the `guard.py` docstring and in Guard limits and exit codes": confirmed. The 17 residual bullets in `docs/agents/harness-capabilities.md:50-` repeat the docstring's (`guard.py:60-79`) with one longer final bullet, and no third list exists: `INSTALL.md:91`, `HOWTO.md:120` and `BREACH_PROCEDURE.md:26` point to the docstring and restate none. This review confirms it, as the checklist item asks. The recount in T14m (121 refused, 65 allowed) matches mine: `ast` over `test_guard.py` gives REFUSED 46 + REFUSED_PROTECTED 15 + REFUSED_VARIATIONS 35 + R_REFUSED_PROTECTED 14 + R_REFUSED_SHELL 11 = 121 and ALLOWED 34 + ALLOWED_AFTER_REPAIR 19 + R_ALLOWED 12 = 65.
- **CP8 and CP9** (line 1075): partly supported. **Amendment approved by** under CP8 is filled (line 685); T44 to T51 and T53 to T56 are `[x]`; T52 `[x]` with Option A; T57 `[x]` by the owner's acceptance of the departures in F3; the build pins the INT-25 text in both flavors. Not evidenced and the owner's: K5 (the owner read the INT-25 text) and "the owner has been told that whether the skeptical test side works is shown only by T57 and real use" (the plan states it at K4, line 29; nothing records that the owner was told).
- **T58** (line 1077): supported. `ci.yml` has `["3.10", "3.12"]` and no 3.8; `grep -rn "3\.8" .github bundles README.md tests/live` prints only the deliberate history listed in T58 step 5 (docstrings at `test_bundle.py:1407,1720`, `lp_verify.py:464,506,507`, `build_protocol.py:671,674`, the generated protocol and results sheets, and the INT-1 fixture); `bundles/base/VERSION` is `0.2.0`; Open question 21 has its answer. Run only on Python 3.11.3 locally (T58 states this).
- **Traceability (T43)** (line 1074): supported. 39 rows (5 + 12 + 10 + 4 + 8), matching the intents' seed headings; every backticked path resolves except `.github/agents/` (a Copilot build output, not installed here) and the `REVIEW_PLAN_<N>.md` pattern; the six coordinator headings the table cites exist.
- **All tasks `[x]`** (line 1070): supported. Every task from T1 to T58 except T40 to T42 is `[x]` with a note (T40 to T42 are `[-]` dropped by the owner, 2026-11-06). T37b, T37d and T57 are `[x]` by recorded owner acceptance, not by the run the task describes.
- **No `[~]` outstanding** (line 1082): supported by the same read: no `[~]` Todo line remains.
- **CP9 review item** (line 1080, "A review of the final commit exists as `REVIEW_PLAN_2.md`"): this file is that review. Each finding is open until the owner repairs, defers or rejects it; the owner's K5 approval of the agent-behavior text is open.
- **Summary note by the coder** (line 1083): not met (F2).
- **K5 — the owner's reading of the agent-behavior text: open, not done.** The owner has not recorded it for T1, T2, T14f, T14l, T15 to T35, T47 to T53 or T58 (the plan's "K5 pending" lines), and I did not and cannot do it.

## Rule exceptions compared

The "Rule exceptions" lines I could find, against the diff, the commit log and `.manifold/guard-log.jsonl`:
- The Phase 2 coder's own line: none exists in the repository (F2). Not compared; the per-checkpoint chat reports were not committed.
- Phase 1 agents' lines in the plan (`bug-coder` and `test-coder`: "Rule exceptions: none", lines 981 and 985): the `test-coder`'s transcript is recorded in F9 as one refused heredoc, disclosed in `PHASE_1_TEST_PLAN.md` (on the other branch, not read here). That agrees with the one line in `/Users/mihay42/dev/manifold/.claude/worktrees/phase1-test-set-f37394/.manifold/guard-log.jsonl` (rule `no-heredocs`, `test-coder`, 2026-11-09 12:39:26Z), which I read; the "none" of line 985 and the disclosed refusal are not the same wording, so I could not tell which line the report meant. This is as the plan states it, unverified here.
- `.manifold/guard-log.jsonl` does not exist in this worktree or in the Phase 2 worktree; the file is git-ignored (`git check-ignore -v` confirms). No refusal of the Phase 2 coding session is therefore visible to compare; the coordinating session's breaches are in `docs/agents/claude-desktop-failures.md` F7 to F10 (7 shell writes and 3 writes to installed files that went through, 5 classifier false positives), which the record states was counted by the guard's classifier over transcripts. I did not recount them.
- The diff: no file outside the plan's inventory that I could see changed in a way the inventory does not list (the inventory lists `tests/live/*`, `tests/results/*`, `.github/workflows/ci.yml`, `.manifold/*`); no `.env`, secret, build output, cache or log file is in the diff (`git diff origin/main...HEAD --name-only` filtered for those types). Commit messages show no `--no-verify` or force-push, but I cannot see hook or signing options in them: not checked. Nothing in the diff touches PR #29 or its branch; I did not check PR #27's branch because it is not among the remote refs here.
- Mine (reviewer's own line): none beyond the following, reported as an exception to be safe: one command used an empty heredoc to python (`python3 -I - <<'EOF'` with no body, the shell write rule names `python - <<`), it wrote no file and was a mistake of mine; I also ran `git fetch origin` and `git fetch origin main` (read from the remote, wrote only under `.git`), built and installed the bundle into the session scratchpad with `build.py --out` and `install.py --target` (outside the repository), and wrote three scratch scripts there with `Write`.

## Gates run

Run by me on commit `53df8cf`, with the read-only virtualenv `/Users/mihay42/dev/manifold/.claude/worktrees/intent-agent-process-afd0ed/.venv/bin/python` (not changed; `-p no:cacheprovider` so nothing was written in this worktree). `git status --short` was empty after the runs.

| Command | Counts | Result |
|---|---|---|
| `<venv python> -m pytest bundles/base/tests -q -p no:cacheprovider` | 1954 passed, 1 skipped, 13.55 s | pass |
| `cd server && <venv python> -m pytest -q -p no:cacheprovider` | 1014 passed, 2 warnings, 105.36 s | pass |
| `<venv python> -m pytest tests/live -q -p no:cacheprovider` | 24 passed, 0.05 s | pass |
| `python3 bundles/base/tools/build.py --check` | `lint ok`, rc 0 | pass |
| `<venv python> tools/vendor_web.py --check` | "vendored files match a fresh build", rc 0 | pass |
| `python3 bundles/base/tools/build.py --out <scratchpad>/dist`, then `install.py --target <scratchpad>/inst --apply` from the unzipped build | built `manifold-base-0.2.0.zip` (331714 bytes, sha256 `99f8b5ca5c477154…`); the fresh install's manifest equals this repository's `.manifold/manifest.json`: same 23 files, no file differs; all 23 hashes match the files on disk | pass (a check I added; the plan did not ask for it) |
| `python3 -I <scratchpad>/trace.py` (rows, paths, headings, list counts) and two guard probe scripts | 39 traceability rows, 121 and 65 guard list counts, probe results as above | informational |

The zip hash differs from the T55/T57 build (`3b2dca43…`) because `bundles/base/INSTALL.md` changed after it (T39, `f2120f4..HEAD`); T57's runs used the earlier build, as its note says. The system Python here is 3.11.3; I ran nothing on 3.10 or on Windows.

## CI on the pushed commit

`gh run list --commit 53df8cff3de2122159ec820fa05e0900644147b1 --json name,status,conclusion,headSha,url`, read at 2026-11-10 about 19:55, after one earlier read in which `server` was still `in_progress`:
- `ci`: completed, success, headSha equals the reviewed hash, https://github.com/mediumroast/manifold/actions/runs/42955158218; jobs `test (3.10)` success and `test (3.12)` success (no 3.8 job).
- `server`: completed, success, headSha equals the reviewed hash, https://github.com/mediumroast/manifold/actions/runs/42955158133; jobs `server tests (3.12)`, `server tests (3.11)`, `server tests (macOS, no Docker)`, `vendored web files` and `image` all success.
- A human reading of CI (the checklist's wording) is the owner's; I read it, I did not confirm it for them.
- PR #28 is still a draft (`gh pr view 28 --json isDraft` gives `true`) with `headRefOid` equal to the reviewed hash.

## Tests run and changed

No bug fix is in this change, so there is no failing-first run for me to reproduce; the plan's recorded failing runs are listed under Tests above and were not re-run. Existing tests changed: those listed under Tests, each with the plan's recorded approval. None changed by me.

## Could not check

- Behavior in a live client (standard (d)): the Copilot hook, `claude --agent`, plugin agents, the `coordinator`, the amendment-and-repair loop as one run, and whether the INT-25 text makes the planner skeptical, beyond the one recorded sample. Nothing was run in a client.
- K5, the owner's reading of the agent-behavior text.
- The "after" runs under `~/manifold-live-after` and the "before" runs: read only through the plan's note (F3).
- The Phase 1 branch's `PHASE_1_TEST_PLAN.md` and `REVIEW_PLAN_1.md`: not read.
- The vendors' documentation behind `harness-capabilities.md` (the plan marks what it did not read); I did not re-fetch any page (this agent has no web tool).
- Python 3.10 and Windows; the hook under any client other than direct invocation of `guard.py`.
- Whether PR #27's branch received any commit: not checked.
- The 10 breaches counted in F7 to F10 of the failures record: not recounted.

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above. The owner alone decides each finding's end state (repaired, deferred or rejected) and K5.

**Rule exceptions:** none that changed a repository file; one empty-bodied heredoc to `python3 -I -` (no file written, my mistake), see "Rule exceptions compared".
