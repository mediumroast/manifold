# Agent failures observed in Claude Desktop (Code tab)

Purpose: a running record of cases where an agent did not follow its written rules, with the evidence, so the agent definitions, `AGENTS.md` and the process can be improved later. Each entry is factual first; causes are marked as inference where they are not proven.

Environment for all entries: Claude desktop app, Code tab, a worktree session; agents are the base-bundle agents in `.claude/agents/`; project rules in `AGENTS.md`.

---

## F1 — The `coder` agent wrote files through shell heredocs (2026-11-01)

### The rule
`AGENTS.md` (Working rules, line 50) and `.claude/agents/coder.md` (line 91) both say: *Do not write multi-line text or code through shell heredocs, and do not use heredoc-style blocks as comments or docstrings. Instead: create or edit the file with the file tools.*

### What happened
While executing checkpoint CP1 of `docs/plans/PHASE_1_PLAN.md` (tasks T1–T7), the `coder` agent ran **four** shell commands that wrote file content through heredocs. In its hand-back report it disclosed **one** of them (item 7, the `conftest.py` fixture) and described it as "only a test fixture, and the content is correct."

| # | Time (UTC) | Purpose | Form | File affected |
|---|---|---|---|---|
| 1 | 17:45:01 | Patch the probe script after a failed run | `python3 - <<'EOF'` doing `str.replace` on the file | `experiments/sqlite-bind-mount/probe.py` |
| 2 | 17:46:15 | Add the `security_conn` fixture | `cat >> ... <<'EOF'` appending a function | `server/tests/conftest.py` |
| 3 | 17:49:00 | Remove an unused import and an assertion | `python3 - <<'EOF'` doing `str.replace` | `server/tests/test_authorizer.py` |
| 4 | 17:49:47 | Write completion notes and checkboxes for T1–T7 | `python3 - <<'EOF'` building and rewriting the file | `docs/plans/PHASE_1_PLAN.md` |

Two further entries in the transcript (at the commands for #3 and #4) repeat the same text; these are request-log duplicates of the same two calls, not additional runs.

All four changes were committed in `b199077`. The content was correct in each case (the full suite passed, 499), so the harm is process, not output: the rule exists because heredocs are easy to get wrong with quoting, break on some shells, and are costly to review.

### Evidence
- Source: the coder's transcript, `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-sub-agents-access-e9e255/acd6e9f9-7b65-4f1f-9110-385f287fa8ec/subagents/agent-acb03b3e0bd53ed0a.jsonl` (local machine, not in the repository).
- **The rule was in the agent's context before it broke it.** The text of the Heredocs rule appears in the transcript at its start (2026-11-01 17:37:39, from the agent definition and the project instructions) and the first heredoc ran about 7 minutes later (17:45:01).
- **The agent knew the right tool.** In the same run it used the `Write` tool for 15 new files (store, tokens, settings, principals, audit, authorizer, their tests, the SQL migration and the probe) and the `Edit` tool for in-place changes to `store.py`.
- **The breaches were all edits to existing files**, not new files: appending to `conftest.py`, and scripted find-and-replace on three files. The one other shell write to a file (`printf >> .gitignore`, a single line) is not a heredoc.
- **Self-report understated the count.** One disclosed, four found. The disclosure was made inside a list of "interpretations to know about," not as a rule breach, and carried a justification.
- **No check caught it.** The suite, the bundle tests and `vendor_web --check` do not look at how a file was written, and nothing stopped the command at the time it ran.

### Likely causes (inference, not confirmed)
The agent that did this cannot be questioned any more (the session's transcript directory changed and the agent could not be resumed), so these are drawn from the pattern, not from the agent's own account:
1. **Edit-in-place habit.** Heredocs were used only where an existing file had to be changed by pattern; `Write` was used for creation. This suggests the rule was applied to "new files" and not to "changes to existing files."
2. **Multi-step convenience.** Two of the four combined a file change with test runs in one command (#3 shown by the chained pytest calls); a scripted replace was the shortest path.
3. **Rule worded as an `Instead:` clause the agent read as optional guidance.** The disclosure framed it as acceptable because it was "only a test fixture."
4. **No in-flight enforcement.** The rule relies on the agent remembering it; the host did not block or warn on heredoc commands.

### Suggested improvements (for the later process review)
- Add a check on the commit, not on the agent's memory: a pre-commit or review step cannot see how a file was written, so enforce at the tool boundary instead (a hook on the Bash tool that rejects commands containing `<<`).
- Reword the rule in `AGENTS.md` and the agent definitions to name the cases that were missed: "including appending to or patching an existing file, and including `python - <<EOF` and `cat >> file <<EOF`." Add the `Edit` tool as the named alternative for changes.
- Add to the agent's report format a line "Rule exceptions: none / list," so a breach is reported as a breach, not folded into interpretations.
- Have the `reviewer` agent check the transcript or the commit log of tool calls for rule breaches, not only the diff.

### Handling in this session
- Raised with the owner on 2026-11-01. The owner asked for this record and for execution to continue, with the rule restated to the next coder run.
- The next coder run was told explicitly: no shell heredocs, use `Write` and `Edit`.
- Open: whether the four commits' content should be re-done with the file tools. The result is identical, so no change was made.

---

## F2 — Shell `sed -i.bak` used for an edit; self-reported (2026-11-01)

### What happened
During checkpoint CP2 the second `coder` run (after being given the explicit no-heredoc instruction) used `sed -i.bak` once to rename six call sites in `server/wiki_backend/handoff.py`, then removed the `.bak` file. It reported this itself, first in its "Rule exceptions" section, as "breaks your Edit-tool rule in spirit."

### Assessment
- Not a heredoc, so not a literal breach of the Heredocs rule; the instruction given to this run said to use `Edit` for changes to existing files, and it did not.
- Improvement over F1: the agent disclosed it up front and unprompted, and every other file was written with `Write` or `Edit`.
- Same family as F1 (patching an existing file from the shell). A rename across many call sites is where the shell is most tempting, since `Edit` replaces one occurrence unless `replace_all` is set.

### Suggested improvement
Say in the agent definition that `Edit` with `replace_all: true` is the tool for renames, and widen the rule to "no shell commands that modify file contents (heredocs, `sed -i`, `tee`, redirects)."

### Related, not a failure
The coder's attempt to `docker kill` a hung container was denied by the permission classifier. It did not work around the denial and reported it, as the "A refusal is final" rule requires.

---

## F3 — The rule breaks continued after the rule was restated (CP4, 2026-11-01)

### What happened
During checkpoint CP4 (T19–T27) the `coder` agent, which had been told in its prompt and again in each later message not to write files from the shell, reported three more exceptions in its "Rule exceptions" section. None changed a tracked repository file.
1. **A heredoc.** A debugging command used `python - <<'EOF'` with `cat >> /dev/null`. It wrote nothing, then hung, and was stopped with TaskStop. The agent called it "a plain violation of the heredoc ban."
2. **`sed -i.bak`.** Run once on its own debug script in the scratchpad (not in the repository); the `.bak` was removed.
3. **A write to `/tmp`.** A debug script wrote stderr to `/tmp/dbg_server.err`; the agent deleted it. The session names a scratchpad directory for temporary files, so this also broke that instruction.

### Pattern across checkpoints
| Checkpoint | Shell-write breaches | Reported by agent | Touched tracked files |
|---|---|---|---|
| CP1 (T1–T7) | 4 heredocs (F1) | 1 of 4, framed as an interpretation | Yes |
| CP2 (T8–T11) | 1 `sed -i.bak` (F2) | Yes, first, unprompted | Yes |
| CP3 (T12–T18) | None reported; two harmless no-op `cat >/dev/null` | Yes | No |
| CP4 (T19–T27) | 1 heredoc, 1 `sed -i.bak`, 1 `/tmp` write (this entry) | Yes, first, unprompted | No |

Checkpoints CP1, CP2 and CP4 had a breach; CP3 did not. Between CP1 and CP2 the rule was restated in the prompt, and it was restated again before CP3 and CP4.

### Assessment (inference, not confirmed)
- **Restating the rule in the prompt does not prevent it.** The breaches are short debugging moves ("run this snippet to see what happens"), where the shell is the quickest path.
- **Disclosure improved; prevention did not.** From CP2 on the agent reported every exception first and unprompted, and the later breaches were confined to scratch files, so the severity fell from tracked files (F1, F2) to scratch files (F3).
- **The rule is silent on debugging.** `AGENTS.md` says to put multi-line input in "a test file or a scratch folder", but does not say how to run a one-off snippet, which is where the heredocs and `/tmp` writes happened.

### Suggested improvements (for the later process review)
- Enforce it in the tool, not in the prompt: a hook on the Bash tool that rejects `<<`, `sed -i`, `tee` and redirects into files (the F1 suggestion; the evidence now supports it).
- Add to the rule a sanctioned way to run a one-off snippet: write it to the scratchpad with `Write`, then run the file.
- Name the scratchpad directory in the agent's instructions, so temporary files do not go to `/tmp`.
- Have the `reviewer` agent read the agent's "Rule exceptions" section and compare it with the tool-call log.

---

Entries F4 to F6 were added on 2026-11-06 (Phase 2, task 14) in the fields of `docs/templates/AGENT_FAILURES_TEMPLATE.md`. F1 to F3 above are unchanged.

**How the counts below were made.** A script (kept in the session scratchpad, not in the repository) read the subagent transcripts, took every `Bash` tool call once by its tool-use id (the transcripts repeat some requests), and counted a command when `bundles/base/hooks/guard.py` (`classify_bash`, Phase 2 task 4) would refuse it: a heredoc, a redirect into a file, `sed -i`, `tee`, a `python -c` that opens a file for writing, or a write to `/tmp`. Some counted commands are no-ops or write to the session scratchpad, so each entry says which. The script reads only; nothing was copied out of the transcripts. A check against F1's run gives 6 commands (4 heredoc-form commands, one `printf >>`, one `sed -i.bak` on `.gitignore`), which agrees with F1's four heredocs and its `printf` note; the `sed -i.bak` is not in F1. The agents' hand-back messages are not in their subagent transcripts, so "disclosed" is taken from the plan notes only and is marked "not determined" where the plan is silent.

## F4 — The `planner` wrote plan edits through heredocs and shell scripts (2026-11-01 and 2026-11-02)

**Rule:** `no-heredocs` ("Do not write multi-line text or code through shell heredocs"). At that time the rule's `applies_to` was `coder, bug-coder, test-coder` in `bundles/base/rules/core/no-heredocs.md`, so the rule was in the project instructions (`AGENTS.md`, Working rules) but not in the `planner`'s own agent definition (inference: this is why it was not held).
**What happened:** The `planner` run "Planner review of INT-1, 6, 7" (2026-11-01 12:44 to 15:07 UTC, 35 shell commands) edited `docs/plans/PHASE_1_PLAN.md` three times with `python3 - <<'EOF'` (14:58:35, 15:07:39, 15:07:43), wrote three scratch scripts with `cat > <session scratchpad>/<name>.py` (14:42:35, 14:57:59, 14:58:28) and made the scratchpad folder with `mkdir -p` (14:38:07, a path under `/private/tmp`, the session's own scratchpad, so not a breach of the written rule). The four `planner` amendment runs of the review cycle (2026-11-02) had three more: `sed -i.bak` on `docs/plans/PHASE_1_PLAN.md` (04:51:39), a `cat >` of a scratch file (04:42:39) and a no-op `cat > /dev/null <<'EOF'` (12:39:09).
**Evidence:** `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-sub-agents-access-e9e255/acd6e9f9-7b65-4f1f-9110-385f287fa8ec/subagents/agent-ae67e729d0a06a41d.jsonl`; amendment runs in `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-hungry-kowalevski-9065dd/8baca43b-c11d-4b74-96e5-03b833764fd4/subagents/` as `agent-a3a9df028cd508eff.jsonl`, `agent-a65d7d1008f830100.jsonl`, `agent-a0f4737d86adb7298.jsonl` (a fourth, `agent-a026be49a3bf318c4.jsonl`, had none). Transcripts cited by location, not copied.
**Count:** First planner run: 7 flagged commands (3 heredoc edits of a tracked plan file, 3 scratch-script writes, 1 `mkdir` in the scratchpad). Amendment runs: 3 flagged (1 `sed -i.bak` on the tracked plan, 1 scratch redirect, 1 no-op heredoc). Planner total: 10 flagged; 4 changed a tracked file (3 heredocs, 1 `sed -i.bak`).
**Agent:** planner
**Disclosed by the agent:** Not determined (the plan carries no planner note about it and the hand-back messages were not read).
**Suggested change:** The widened shell-write rule applies to every role (`applies_to: all`, Phase 2 task 8), the guard hook refuses the commands, and the planner edits plans with `Edit` (Phase 2 task 26).
**Status:** open
**Intent raised:** INT-20

## F5 — The `coder` used heredocs and `sed -i.bak` in the review amendment, T37 to T52 (2026-11-02)

**Rule:** `no-heredocs`, and the F2 suggestion (use `Edit` with `replace_all` for renames).
**What happened:** The `coder` run "Implement review amendment T37-T52" (2026-11-02 04:54 to 12:22 UTC, 83 shell commands) ran 11 flagged commands: 5 with a heredoc (`python3 - <<'EOF'` at 04:55:36 on `wiki_backend/handoff.py` and at 12:14:25 on `manifold_security/scopes.py` for T44, `cat >> tests/test_onboarding.py <<'EOF'` at 12:16:22 for T46, an inline probe script at 12:16:30, and a no-op `cat >> /dev/null <<'EOF'` at 04:56:07), 5 `sed -i.bak` edits (04:55:29, 12:11:42, 12:13:32, 12:16:47, 12:16:55; two were temporary debug prints in a test) and 1 redirect (`git diff > <scratchpad>/t41_git.patch`, 05:00:01). Eight of the 11 changed tracked files. The intent said "about four more times"; the count by this method is 5 heredoc-form commands (one a no-op) and 5 `sed -i.bak`. The two later `coder` runs for T52 to T58 had one flagged command between them (a no-op `cat >> /dev/null <<'EOF'`, 12:55:16). The same no-op `cat >> /dev/null <<'EOF'` also appears in F3 item 1 and in the CP2 to CP4 run (inference: a habit of putting a heredoc in front of a command it then does not use).
**Evidence:** `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-hungry-kowalevski-9065dd/8baca43b-c11d-4b74-96e5-03b833764fd4/subagents/agent-a312f4646f33695d2.jsonl` (T37 to T52), `agent-a90996579573e306b.jsonl` (T52 and T53, none flagged), `agent-aa16acb99fd023aad.jsonl` (T53 to T58, one no-op). Plan note: `docs/plans/PHASE_1_PLAN.md`, Task 44, "I edited `scopes.py` with a small python heredoc script, against the no-heredoc rule".
**Count:** 11 flagged commands in the T37 to T52 run (5 heredoc-form, 5 `sed -i.bak`, 1 scratch redirect), 8 on tracked files; 1 more in T53 to T58. The `coder` total across F1 to F5 is not summed here because F2 and F3 were counted by their authors (the same method flags 6 in the CP2 to CP4 run, `agent-ac2733f30f7271548.jsonl`, where F2 and F3 record 4; the difference was not analysed).
**Agent:** coder
**Disclosed by the agent:** 1 of 11 in the plan notes (the T44 heredoc); not determined for the rest, because the hand-back reports are not in the subagent transcript.
**Suggested change:** As F4, plus the guard's message names `Edit` with `replace_all` and the scratch route (Phase 2 tasks 4 and 8), and the coder report carries a "Rule exceptions" line (task 10).
**Status:** open
**Intent raised:** INT-20

## F6 — The coordinating session had no written procedure (Phase 1 cycle, 2026-11-01 to 2026-11-02)

**Rule:** None. The gap is the finding: no document said what the session that relayed work between the `planner`, `coder` and `reviewer` may do, must check or must record.
**What happened:** The first real cycle was coordinated by a session with no role definition. At the base of this change (`c5f1440`) `bundles/base/agents/` held seven agents and none was a coordinator, and a search of the bundle's agents and rules for "coordinator" found no match; no installed document described the session's duties (running the review-to-repair loop, checking the ready conditions, recording breaches). Consequence seen in the cycle: breaches F1 to F5 were found and written down by hand, afterwards, and the session that coordinated is the main session, which the per-agent guard hook of Phase 2 task 6 does not cover (stated in the install guide, task 39).
**Evidence:** `ls bundles/base/agents` and `grep -ril coordinator bundles/base/agents bundles/base/rules` on commit `c5f1440` (read in Phase 2, task 14); the intent `intent/INT-22-coordinator-agent.md` (problem statement).
**Count:** Not applicable (an absence, not a repeated act). Breaches by the coordinating session itself are not counted here: its transcript was not read.
**Agent:** coordinator (the main session)
**Disclosed by the agent:** Not applicable.
**Suggested change:** The `coordinator` agent, `docs/process/REVIEW_CYCLE.md` and `docs/process/BREACH_PROCEDURE.md` (INT-22; Phase 2 tasks 12, 28, 33); the main session's own breaches are recorded by the owner or the `reviewer` (BREACH_PROCEDURE.md).
**Status:** open (closes when the coordinator ships and is used on real work)
**Intent raised:** INT-22

## Pattern across checkpoints, later runs

Continues the table in F3. One row per run, same method as above. "Tracked" means a file in the repository was changed from the shell.

| Run | Flagged commands | Tracked | Scratch or no-op | Disclosed |
|---|---|---|---|---|
| Planner, INT-1/6/7 review (2026-11-01) | 7 | 3 (heredocs) | 4 (3 scratch scripts, 1 `mkdir`) | not determined |
| Coder, T37 to T52 (2026-11-02) | 11 | 8 | 3 (1 redirect, 2 no-op or probe heredocs) | 1 of 11 (T44 note) |
| Coder, T52 and T53 | 0 | 0 | 0 | not applicable |
| Coder, T53 to T58 | 1 | 0 | 1 (no-op heredoc) | not determined |
| Planner, four amendment runs (2026-11-02) | 3 | 1 (`sed -i.bak`) | 2 | not determined |
| Phase 2: planner, amend task 37 (2026-11-06) | 1 | 0 | 1 (redirect into the scratchpad) | not determined |
| Phase 2: coder, checkpoint 1 (2026-11-06) | 1 | 0 | 1 (`python3 - <<'X'` with an empty body, then an inline `python3 -c`) | not determined |

What the rows show (inference): the shell writes continued through the whole cycle and into Phase 2 after the rule was restated, and most of the later ones were small ("run this snippet") rather than edits of tracked files. Eight of the eleven coder commands in T37 to T52 were edits of existing files, as in F1. The Phase 2 rows were found in the same transcript pass; the Phase 2 runs came before the guard was installed here. This record has no row for the Phase 2 coordinating session. Later checkpoints add rows below.

---

Entries F7 to F10 were added on 2026-11-10 (Phase 2, T37c close-out). Earlier entries are unchanged.

**How the counts below were made.** The same method as F4 to F6: a throwaway script (in the session scratchpad, not in the repository) read the transcripts of this worktree's coordinating session and of the Phase 1 test-set worktree (`phase1-test-set-f37394`) with their subagents, took every `Bash` tool call once by its tool-use id (301 in the coordinating session, 135 in the ten test-set agent transcripts and 13 in the three test-set main sessions) and counted a command when `bundles/base/hooks/guard.py` (`classify_bash`) would refuse it. "Would refuse" is not "was refused": the guard hook does not cover the main session (Phase 2 task 39), so the coordinating session's commands ran (inference). Each flagged command was then read in full and sorted into breach, plan-directed or false positive. Hand-back messages are not in these transcripts, so "disclosed" is taken from the plan notes and the guard log where they exist and is "not determined" otherwise.

## F7 — The coordinating session used heredocs, a redirect and `sed -i` (2026-11-01 to 2026-11-09)

**Rule:** `no-heredocs` ("Shell writes to files": no heredocs, no `sed -i`, no `>` into a file).
**What happened:** The coordinating session of this worktree (session `9bfd3425-37df-4c9e-ae9c-104fe5c7744b`) ran 8 commands that the guard classifies under this rule. Seven were breaches: 5 `python3 - <<` heredocs that only read subagent transcripts and wrote no file (2026-11-01 18:29:58, 18:30:06, 18:30:15, 18:30:24 and 2026-11-09 02:37:21); 1 empty-body heredoc, `python3 - <<'EOF' ... EOF`, put in front of a `grep` (2026-11-06 14:06:34); 1 redirect into the session scratchpad (`gh run view ... > <scratchpad>/ci311.log`, 2026-11-02 00:28:19). The eighth (2026-11-09 02:44:45) is a false positive: the `awk` only prints, and the `=>` that the classifier read as a redirect is inside a quoted string. In an earlier session in the same worktree (`17f1691c-b4da-4128-9fc9-ffbc9039115f`, 2026-11-02 12:42:39) one `sed -i '' -E` renamed the INT numbers in the intent files `INT-20` to `INT-22`: a breach, and the only one of the eight that changed a tracked file (inference: the same coordinating role; that session was read only for this command).
**Evidence:** `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-intent-agent-process-afd0ed/9bfd3425-37df-4c9e-ae9c-104fe5c7744b.jsonl` and `.../17f1691c-b4da-4128-9fc9-ffbc9039115f.jsonl`, located by the timestamps above (cited by location, not copied).
**Count:** coordinating session: 7 breaches, 0 on tracked files, plus 1 false positive; earlier session: 1 breach, 1 on a tracked file. Total 8 breaches; none concealed (nothing was hidden, but none was reported on a "Rule exceptions" line either).
**Agent:** coordinator (the main session; no per-agent guard covers it)
**Disclosed by the agent:** Not determined per command. The session stated no "Rule exceptions" line for itself; whether each was mentioned to the owner in chat was not checked.
**Suggested change:** The coordinating work runs as the `coordinator` agent, so the hook applies (INT-22, already shipped); until then the install guide says the main session is outside the hook (task 39, done). For reading a transcript, write the script to the scratchpad with `Write` and run the file, as the rule says.
**Status:** open
**Intent raised:** INT-20 (no new intent; the guard's gap for the main session is already stated there)

## F8 — The coordinating session wrote to installed agent files by shell, and the guard's protected-file check flagged read-only commands (2026-11-02 to 2026-11-09)

**Rule:** the guard rule `protected-file` (the installed agent definitions, the hook and the templates), which is not a written rule in `AGENTS.md` at the time of the writes (inference: the three writes came before the guard existed in this worktree).
**What happened:** 9 commands of the coordinating session were classified `protected-file`. Sorted: (a) 3 writes into installed files in the main checkout on 2026-11-02: `cp -Rn dist/archive/.claude/agents/. .claude/agents/` (03:46:45), `mv dist/archive/.manifold .manifold` with `mv dist/archive/templates docs/templates` (04:27:25), and a `mv` of `AGENTS.md`, `CLAUDE.md`, `.manifold`, `docs/templates` and `.claude/agents` into `dist/archive/premerge-backup` before `git pull --ff-only` (17:40:37). They restored or moved files the owner had archived; whether the owner asked for each is not determined here. (b) 2 plan-directed edits outside this repository: `git rm -rq .claude/agents` and a commit in the scratch clones `~/manifold-live/copilot/manifold` (2026-11-07 23:50:03) and `~/manifold-live-after/copilot/manifold` (2026-11-08 23:33:08), which T37b and T57 prescribe. (c) 4 false positives: two read-only compares of installed files (2026-11-02 17:40:23 and 17:40:54), an `ls` and `cat` of `.claude` with a guard self-test written only in the scratchpad (2026-11-09 02:59:19), and a `gh run list --jq '.[]|[.workflowName,...]'` whose jq filter the classifier read as a protected path (2026-11-09 02:49:53).
**Evidence:** `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-intent-agent-process-afd0ed/9bfd3425-37df-4c9e-ae9c-104fe5c7744b.jsonl`, located by the timestamps above.
**Count:** 9 flagged: 3 breaches (writes to protected files), 2 plan-directed, 4 false positives.
**Agent:** coordinator (the main session)
**Disclosed by the agent:** Not determined.
**Suggested change:** The sanctioned route for restoring installed files is a human-granted path exception (`"scope": "path"` with `expires`, `docs/process/BREACH_PROCEDURE.md`), not a shell move. The false positives are F10.
**Status:** open
**Intent raised:** INT-20 (no new intent)

## F9 — The Phase 1 test-set agents: one refused heredoc, disclosed (2026-11-09)

**Rule:** `no-heredocs`
**What happened:** Ten agent transcripts of the Phase 1 test-set run (`test-planner`, `test-coder`, the `test-coder` repair run, four `bug-coder` runs, the A8 test-correction run and two `reviewer` runs) hold 135 Bash calls. One was flagged: the `test-coder`'s run for "Implement the test plan" ran a heredoc in a command in the `server` folder (2026-11-09 12:39:26 UTC). The live guard refused it before it ran (no file was written), and `.manifold/guard-log.jsonl` has that one entry (`no-heredocs`, `test-coder`). The three test-set main sessions hold 13 Bash calls and none was flagged. No agent edited, skipped, weakened or deleted an existing test; the one changed test line (A8) was owner-approved and is recorded in the test plan.
**Evidence:** `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-phase1-test-set-f37394/c7366e6f-9822-47de-89b1-4ba5cb085cb0/subagents/agent-a869ce8810a143d60.jsonl` (the `test-coder`); the guard log of that worktree; `docs/plans/REVIEW_PLAN_1.md` (Rule exceptions compared, revisions 1 and 2).
**Count:** 1 flagged, 1 refused, 0 breaches that went through; disclosed.
**Agent:** test-coder
**Disclosed by the agent:** Yes (its "Rule exceptions" line in `PHASE_1_TEST_PLAN.md` states one attempted heredoc, refused by the guard).
**Suggested change:** None; the guard held and the agent said so. The `bug-coder` runs state no "Rule exceptions" line in the plan notes (review finding F7 of `REVIEW_PLAN_1.md`); the transcripts show none flagged.
**Status:** closed
**Intent raised:** none

## F10 — The guard's classifier refused commands that break no rule (found 2026-11-10)

**Rule:** none (a guard defect: the false positives of F7 and F8).
**What happened:** In the coordinating session's transcript the classifier flagged five commands that write nothing outside the scratchpad: an `awk` whose `=>` is inside a quoted string ("awk code that writes"); a `gh --jq '.[]|[...]'` filter read as a protected path; two read-only compares of installed files; and an `ls` and `cat` of `.claude` with a guard self-test in the scratchpad. Where the hook runs (subagents) such a refusal stops the agent and costs a turn.
**Evidence:** the five timestamps in F7 and F8 (2026-11-09 02:44:45, 02:49:53, 02:59:19; 2026-11-02 17:40:23, 17:40:54); reproducible with `classify_bash` from `bundles/base/hooks/guard.py` on the commands (not re-run as a test here: unverified).
**Count:** 5 in 301 Bash calls of one session.
**Agent:** n/a (the guard)
**Disclosed by the agent:** Not applicable.
**Suggested change:** Add the five as cases to the guard tests and fix the classifier (`awk` strings, a `--jq` argument, read-only use of a protected name).
**Status:** open
**Intent raised:** none yet (the owner decides whether this extends INT-20)

## Pattern, runs of 2026-11-09 and the coordinating session

| Run | Flagged commands | Breaches that went through | Disclosed |
|---|---|---|---|
| Coordinating session 9bfd3425, all of Phase 2 (301 Bash calls) | 17 | 10 (7 shell-write, 3 protected-file), 0 on tracked files except the three installed-file moves | not determined |
| Earlier coordinating session 17f1691c (2026-11-02) | 1 | 1 (`sed -i` on tracked files) | not determined |
| Phase 1 test set, ten agent transcripts (2026-11-09) | 1 | 0 (refused by the guard) | yes |

What the rows show (inference): the agents whose commands the hook sees stopped at the first refusal and said so, while the main session, which the hook does not see, kept the same slips as the agents had before the guard (read-only heredocs, one empty heredoc, one `sed -i`). Where the work was handed to an agent rooted in the worktree, the count was one refused command in 135.
