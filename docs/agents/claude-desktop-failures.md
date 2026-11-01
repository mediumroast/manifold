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
