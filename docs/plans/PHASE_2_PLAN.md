# PHASE_2_PLAN.md

**Approved by:** Michael Hay on November 6, 2026
**Source intent:** [INT-20 Agent guardrails hold][i20], [INT-21 A written review-to-repair loop][i21], [INT-22 A coordinator agent][i22] and [INT-23 Review policy][i23]. All four are `status: accepted`, `accepted_by: Michael Hay on November 3, 2026`, and are planned together as the owner asked ([INT-22 Open questions][i22-oq]).

## Objective
When this phase is complete, the base bundle (version unchanged until the owner decides, Open question 7) enforces its file-writing rules at the tool boundary where the client allows it and states plainly where it does not; every review leaves `docs/plans/REVIEW_PLAN_<N>.md`; the planner amends a plan from it; the coder works checkpoint by checkpoint; a written procedure (`REVIEW_CYCLE.md`) and a `coordinator` agent run that loop and check the ready conditions; breaches are recorded in a templated, harness-named record by a written procedure; review approval is stated once, in an `AGENTS.md` "Review process" section, with no rule that the people in the repository cannot meet; and a `HOWTO.md` explains the whole cycle. All of it exists for the `claude` and `copilot` flavors, built from one source.

## Scope

**In scope:** the guard hook and its install; the widened shell-write rule, the scratch route and the "Rule exceptions" line; the breach record template, its procedure and the first complete record; `REVIEW_PLAN_TEMPLATE.md`, the reviewer writing one file, planner amendment, checkpoints in the plan and test-plan templates and in all agents that execute or plan; `REVIEW_CYCLE.md`; the coordinator agent and PR template; the review-policy decision ([INT-23][i23]); `HOWTO.md`; bundle tests, README, INSTALL, MODELS and live-protocol updates; refreshing this repository's own install; the small adaptation of `tests/live/` (T37a) and the Phase 1 test-set run in Copilot and Claude Code with its results record (T37b to T37d).

**Constraints** (from the intents, in their words):
- INT-20: both flavors, and where a client cannot enforce, "the same rule, the same sanctioned route and the same report line must still be in that flavor's instructions, and the gap is stated plainly in the install guide and the record"; not in PR #27 or on branch `claude/sub-agents-access-e9e255`; no loopholes by wording (`python - <<EOF`, `cat >> f <<'EOF'`, `printf >> f`, `sed -i.bak`, `tee`, `> file`, `/tmp` paths) and no blocking of read-only use (`>` in a quoted argument, `2>&1`, `git` and test commands); a blocked agent does not work around the block, a human may allow an exception and it is recorded; honest records (transcripts cited by location, not copied; no secrets); offline, standard library only; the build stays reproducible.
- INT-21: both flavors from the same sources; the reviewer writes exactly one new file and nothing else; a human approves (the planner never fills in **Approved by**, the reviewer never approves or blocks); review is independent (the writer never reviews; the reviewer does not read held-out scenarios); every repair task names its finding and every finding ends repaired, deferred or rejected; artifacts stay concise; completed tasks keep their notes; plans and reviews written before this change stay valid (a plan with no checkpoints is one checkpoint).
- INT-22: both flavors from one source; a human decides (the coordinator never accepts an intent, fills in **Approved by**, merges, approves a plan or closes a phase); it does not edit code, plans or reviews and does not commit unless asked; it is bound by the rules and its breaches are recorded; no outward action without the owner; independent review; concise.
- INT-23: both flavors; no invented authority; solo repositories complete a cycle with no unmeetable rule; teams can add a second-approver rule; consistent with INT-21 and INT-22; existing installs with a `REVIEW.md` stay valid; concise.
- All four: nothing lands in PR #27 or `claude/sub-agents-access-e9e255`.

**Review standard for this phase (confirmed by the owner, Michael Hay, 2026-11-03).** The change is mostly documents and agent instructions, so a review of it, and of any similar change, means: (a) traceability: every "we will know when" line maps to a named file and section (table under Completion checklist); (b) consistency: no two documents, rules, agent definitions or templates contradict each other, including the rendered `AGENTS.md` against the rule sources; (c) verified claims: every command, flag, path, key or file format a document states was run or read, or is marked "unverified: confirm with <source>", and every link and path resolves; (d) behavior: a document that prescribes behavior is checked in real use on Manifold work, by agents and reviewers that did not write it, and the evidence is recorded (guard log, breach records, review documents, PR summaries, `tests/results/` records); until that use has happened the scenario is reported as "no evidence yet" (reworded 2026-11-06 because the owner replaced the toy walk-throughs with real use; reconfirmed by the owner on 2026-11-06 with the `tests/results/` records added to the evidence list); (e) code gets normal tests plus the bundle build and lint; (f) an independent reviewer, not the author, using the review policy in force; (g) owner approval of any text that changes agent behavior. Severity for prose: **Important** if an agent could behave differently or be misled by it; otherwise Nit. T2 records this in the bundle.

**How each deliverable is checked** (the "Acceptance" lines use these codes):
- **K1** `build.py --check` and the bundle tests pass (structure, rendering, both flavors, determinism).
- **K2** A new bundle test pins the property in both flavors (a phrase, a field, a path, a tool list). Prose is pinned only for the properties that matter, not word for word.
- **K3** Verified-claims list in the task's completion note: each command, flag, path or format the document states, marked ran / read / "unverified: confirm with <source>".
- **K4** Real-use evidence: the walk-throughs W1 to W3 (T40 to T42) were dropped by the owner on 2026-11-06 and replaced by use of the agents on real Manifold work, recorded by the coordinator and the owner after this phase (see T40). Phase 2 acceptance never claims K4; the one early sample is T37c to T37d (Phase 1 test set in Claude Code and Copilot).
- **K5** Owner reads the text at the checkpoint report (agent-behavior text only).

**Out of scope:**
- Editing the intents; PR #27 and its branch; reviewing Phase 1's code (T37c's reviewer reviews only the new Phase 1 test set).
- Automatic transcript analysis beyond the hook's own refusal log ([INT-20 Out of scope][i20-oos]); scheduling or unattended agents; merging, releasing, deployment; choosing models per agent.
- The MCP-tool form of the bundle install (future); only the install-time stub for the review-process section is planned now.
- A version bump of `bundles/base/VERSION` (Open question 7) and changing the default install format (Open question 2).
- Noticed, not touched: `REVIEW.md` at the repository root also carries INT-1 specifics (it stays a repository file); `bundles/base/README.md` has two "What gets installed" tables (T35 merges them because it must edit the table anyway).

**Needs from other repositories:** None. (Returning breach records to Manifold is a GitHub issue the owner posts; the procedure drafts it, T12.)
**Provides to other repositories:** Every repository that installs the bundle gains the guard hook, `coordinator`, `REVIEW_PLAN_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE.md`, `AGENT_FAILURES_TEMPLATE.md`, `docs/process/*` and the `AGENTS.md` "Review process" stub.

## Concerns flagged
Each needs a decision by the owner; the plan follows the stated recommendation and says where.
1. **INT-22 contradicts itself on "ready".** Proposed outcome 2 says the coordinator "refuses to mark it ready otherwise"; the owner's answer says "only a human can move a PR out of draft." The plan follows the answer: the coordinator never moves a PR out of draft; it writes the ready check (what exists, what is missing) in the PR and refuses to state "ready" when something is missing (T33).
2. **The coordinator and the reviewer must write a file but "do not edit".** INT-22 says the coordinator does not edit code, plans or reviews yet must add breach-record entries and draft intents; INT-21 lets the reviewer write one file. Claude Code cannot limit `Edit` to a path in the tool list (see the capability matrix, T1). The plan gives both agents `edit` and limits them with a per-agent write allowlist in the guard hook (T4, T21, T31). In a flavor without a hook the limit is instruction only, and that is stated (T39).
3. **Review passes.** INT-21 and INT-23 put "changing the review passes" out of scope, but the confirmed review standard checks prose. The plan adds no pass: it adds a section to the reviewer telling it how the existing four passes apply to documents (T17).
4. **Coordinator in every profile.** INT-22 answers "All" profiles, but the `quality` profile does not install the `planner`, `coder` or `reviewer`, and `lint` rejects references to roles a profile lacks. The coordinator text uses no `{{ref:...}}` markers and tells the agent to read the installed-agent list in `AGENTS.md` (T33).
5. **PR template location.** The owner chose `docs/templates`; GitHub pre-fills only `.github/pull_request_template.md`, so the coordinator applies the template by reading it (T30). Recorded so nobody expects the pre-fill.
6. **Existing tests pin the old reviewer.** `test_reviewer_is_read_only_and_never_approves`, `test_reviewer_never_edits_and_does_not_offer_to_once_tools_are_enabled` and `test_claude_format_denies_the_tools_an_agent_does_not_declare` assert the reviewer has no edit tool. [INT-21 Open questions][i21-oq] (answer "yes" to allowing a limited edit) changes that on purpose. T21 names them; this plan's approval is the owner's approval to change those assertions, and the coder records that in the task note (rule "Tests under fix").
7. **`REVIEW.md` Human threshold in this repository** names a second person who does not exist. T23 replaces it; that edits a file PR #27 introduced, which [INT-23][i23] allows only on the owner's decision, so T23 needs the owner's explicit yes at approval. **Given by the owner on 2026-11-06 (relayed by the coordinator); the owner's approval of this plan still stands to be written.**

## Prerequisites
- [x] INT-20 to INT-23 are accepted (read: `status: accepted`, `accepted_by: Michael Hay on November 3, 2026`).
- [x] `docs/agents/claude-desktop-failures.md` and root `REVIEW.md` are in this worktree (read).
- [x] Project commands are in `AGENTS.md` "Project commands" (confirmed by the owner 2026-11-01). Used here: bundle tests `.venv/bin/python -m pytest bundles/base/tests -q`; server tests `cd server && ../.venv/bin/python -m pytest -q`; vendored files `.venv/bin/python tools/vendor_web.py --check`; bundle lint `python3 bundles/base/tools/build.py --check` (from `bundles/base/tools/build.py` docstring and `.github/workflows/ci.yml`). No linter or type-checker exists. "`pytest`" below means the bundle tests command.
- [ ] The `.venv` exists in this checkout (not seen here; the main checkout's `.venv` was not checked). If missing, ask; do not create it unprompted.
- [ ] The owner answers the Open questions marked "before CP2" (3, 5, 6) before CP2 starts.
- Scratch space: temporary files go in the session scratchpad named in the session, never `/tmp`; no shell heredocs (AGENTS.md "Heredocs").

## File inventory

| Path (under `bundles/base/` unless rooted) | Action | Reason |
|---|---|---|
| `/docs/agents/harness-capabilities.md` | CREATE | T1 capability matrix with sources |
| `process/REVIEW_CYCLE.md`, `process/BREACH_PROCEDURE.md` | CREATE | procedures (T2, T28, T12) |
| `HOWTO.md` | CREATE | T35; zip root and installed to `docs/process/HOWTO.md` |
| `hooks/guard.py` | CREATE | T4 tool-boundary guard |
| `templates/REVIEW_PLAN_TEMPLATE.md`, `templates/PULL_REQUEST_TEMPLATE.md`, `templates/AGENT_FAILURES_TEMPLATE.md` | CREATE | T11, T19, T30 |
| `templates/REVIEW_TEMPLATE.md`, `templates/PHASE_PLAN_TEMPLATE.md`, `templates/PHASE_TEST_PLAN_TEMPLATE.md` | MODIFY | T20, T24, T27 |
| `templates/REVIEW_STARTER.md` | DELETE (Open question 6) | T22 |
| `agents/coordinator.agent.md` | CREATE | T33 |
| `agents/{planner,coder,bug-coder,reviewer,test-planner,test-coder,scenario-writer}.agent.md` | MODIFY | T10, T15, T17, T21, T25, T26, T27 |
| `rules/core/no-heredocs.md`, `rule-exceptions-line.md` (CREATE), `dont-edit-the-test-to-pass.md`, `approved-plan-before-execution.md` | MODIFY / CREATE | T8, T9, T25 |
| `tools/build.py`, `install.py` | MODIFY | roles, hook and doc payload, stubs (T5, T6, T11, T12, T16, T18, T19, T22, T29, T30, T32) |
| `tests/test_bundle.py`, `tests/test_guard.py` (CREATE), `tests/live-protocol.md` | MODIFY / CREATE | tests beside each change |
| `README.md`, `INSTALL.md`, `MODELS.md` | MODIFY | T35 |
| `/docs/agents/claude-desktop-failures.md` | MODIFY (append only) | T14 |
| `/AGENTS.md`, `/REVIEW.md`, `/.claude/agents/*`, `/docs/templates/*`, `/.manifold/*` | MODIFY / CREATE | T23, T38 (this repository's own install) |
| `/tests/live/{setup.sh,lp.sh,lp_verify.py,README.md,build_protocol.py,PROTOCOL-claude-code.md,PROTOCOL-copilot.md}` | MODIFY | T37a: one-repository job, `LIVE_ROOT` fix, `testset` check, no hard-coded bundle version |
| `/tests/results/claude-code-2/`, `/tests/results/copilot-2/`, `/tests/results/README.md` (two rows) | CREATE / MODIFY | T37d: Phase 1 test-set runs and their comparison (T40 to T42 dropped, no walk-through records) |
| `/docs/plans/PHASE_1_TEST_PLAN.md`, `/server/tests/*` (new files), `/docs/plans/REVIEW_PLAN_1.md` | CREATE | T37c: the real Phase 1 test set, kept, on its own branch (Open question 11). The Copilot output stays in `~/manifold-live/copilot/manifold`, outside the checkout, and is not copied |

## Tasks

> **Instructions for the coder:**
> Work tasks in the order listed, one checkpoint at a time: finish and verify every task in a checkpoint, report (gates with command and real counts, "Rule exceptions", anything not run), and stop until told to continue. For each task: read the named files first, make the change, run the task's acceptance, then change `[ ]` to `[x]` and add a one-line note under the task header: what changed, command run, result. Blocked: mark `[~]`, say so, do not skip ahead. Tasks marked "Run by a human" stay `[~]` until that person records the result. Write failing tests first where a task says so and record the failing run.

### CP1 — Ground truth and standard (documents only; checks K3, K5)

### Task 1 — Record what each client can enforce, with sources
**Files:** `docs/agents/harness-capabilities.md`
**Action:** CREATE
**Change:** One table, rows: Claude Code and VS Code Copilot Chat (Local) and Copilot CLI; columns: pre-tool hook that can deny; where hooks are configured; hook input fields (tool name, command, agent identity); hooks inside subagents; frontmatter hooks per agent; can an agent start subagents (depth limit); can an agent be restricted to one writable path; can the coordinator read another agent's tool calls; agent frontmatter keys for tools and invocable agents. Every cell has a source URL and the date read, or "unverified: confirm with <source>". Start from what the planner read on 2026-11-03: Claude Code subagents may spawn subagents up to three layers by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`), `hooks` is a subagent frontmatter field, `PreToolUse` exit code 2 blocks and sends stderr to the model, `agent_id`/`agent_type` arrive on stdin, transcripts sit under `~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl` (code.claude.com/docs/en/sub-agents and /hooks); VS Code Copilot has `preToolUse` hooks (deny by JSON `permissionDecision`), in Preview, in `.github/hooks/*.json` and agent frontmatter (code.visualstudio.com/docs/copilot/customization/hooks). Re-read each page; do not copy these claims unread. Resolve the unverified items that decide later tasks: the `$CLAUDE_PROJECT_DIR` form for a hook command, the matcher syntax in subagent frontmatter, whether frontmatter hooks apply under `claude --agent`, the Copilot hook file schema and the Copilot agent keys for `agent`/subagent tools.
**Acceptance:** K3: no cell without a source or "unverified"; owner reads it (K5). Tasks T6, T7, T33 cite its rows.
**Todo:** [x]
Note (2026-11-06): created `docs/agents/harness-capabilities.md` from six pages read with WebFetch/WebSearch (URLs and the read date in the file); nothing was run in any client. Unverified and marked as such: hook working directory, Copilot Local deny exit codes, agent identity and subagent hooks for Copilot, Copilot hook frontmatter YAML, transcript access for Copilot. WebFetch returned page summaries and the last 16,722 characters of the sub-agents page were not read (stated in the file). Awaiting K5 (owner reads it).

---

### Task 2 — Create the review procedure with the review standard first
**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** CREATE
**Change:** Create the file with its first section "Reviewing documents and agent instructions": the confirmed standard (a) to (g) and the prose severity rule, stated as the review standard, and a line "Confirmed by the owner (Michael Hay), 2026-11-03". T28 adds the loop sections. Decision on placement: the procedure ships in every install and is read by the reviewer and coordinator, whereas `REVIEW.md` is becoming optional (T20), so the standard cannot live there.
**Acceptance:** K3 (every path it names exists or is marked as created by a later task); K5.
**Todo:** [x]
Note (2026-11-06): created `bundles/base/process/REVIEW_CYCLE.md` with the section "Reviewing documents and agent instructions": (a) to (g), the prose severity rule and the confirmation line. Checked with `python3 -I <scratchpad>/cmp_d.py`: standard (d) is byte-identical to the plan's (True), and (a), (b), (c), (e), (f), (g) each found verbatim in the file (True). `ls -d`: `tests/results`, `docs/templates/REVIEW_TEMPLATE.md` and `bundles/base/templates/REVIEW_TEMPLATE.md` exist; the other paths are marked in the file as created by later tasks. Awaiting K5.

---

### CP2 — Guardrails (INT-20; checks K1, K2, K3, K5). Needs Open questions 3, 5, 6 answered.

### Task 3 — Add failing tests for the guard
**Files:** `bundles/base/tests/test_guard.py`
**Action:** CREATE
**Change:** Load `hooks/guard.py` with `importlib` the way `test_bundle.py` loads `build.py`. Table-driven cases for `classify_bash(command)`: refused with a message naming `Write`/`Edit`: `cat > f <<'EOF'`, `cat >> f <<EOF`, `python - <<'EOF'`, `python3 -c "open('f','w').write('x')"`, `printf x >> f`, `echo x > f`, `sed -i s/a/b/ f`, `sed -i.bak s/a/b/ f`, `tee f`, `perl -pi -e s/a/b/ f`, any write to a `/tmp` or `/private/tmp` path, and each of these after `&&`, `;` or inside `bash -c "..."`. Allowed: `git diff > /dev/null`, `pytest -q 2>&1`, `echo "a > b"`, `grep -n '>' f`, `git commit -m "x"`, `python3 .manifold/scratch/probe.py`, `ls`, a command whose only `>` is inside quotes. Cases for `classify_write(agent_type, path, exists)`: reviewer allowed only `docs/plans/REVIEW_PLAN_<n>.md`; coordinator allowed `docs/agents/*-failures.md` and a new (not yet existing) `intent/INT-*.md`; refused `.manifold/guard-allow.json` for every agent; other agents unrestricted.
**Acceptance:** `pytest bundles/base/tests/test_guard.py -q` fails before T4 (record the output: module missing).
**Todo:** [x]
Note (2026-11-06): created `bundles/base/tests/test_guard.py` (209 cases: 45 refused and 35 allowed shell commands, the human-exception cases, the reviewer and coordinator allowlists, the protected guard files, and `main` through a subprocess for both clients). Failing run before T4, `python3 -m pytest bundles/base/tests/test_guard.py -q`: `ERROR collecting ... FileNotFoundError: [Errno 2] No such file or directory: '.../bundles/base/hooks/guard.py'`, `1 error during collection` (module missing). Command is the system `python3` (3.11.3, pytest 9.0.2) because no `.venv` exists in this worktree or the main checkout (not created). The coordinator-cannot-write-plans-source-tests case is left to T31, as the plan has it.

---

### Task 4 — Create the guard
**Files:** `bundles/base/hooks/guard.py`
**Action:** CREATE
**Change:** Standard library only, Python 3.8 syntax. Functions `classify_bash(command)` and `classify_write(agent_type, path, exists)` returning `(allowed, message)`; `main(argv)` reads the hook JSON on stdin, takes `--client claude|copilot` to normalise field names (per T1), exits 2 with the message on stderr to refuse (Claude) or prints the deny JSON (Copilot, per T1). The message names the sanctioned route: write the snippet with `Write` to `.manifold/scratch/` and run the file; use `Edit` with `replace_all` for renames. Tokenise with `shlex` and track quotes so `>` inside quotes and `2>&1` pass. A human exception is an entry in `.manifold/guard-allow.json` (`pattern`, `reason`, `granted_by`, `date`); the guard refuses every agent write to that file and to `guard.py` itself. Every refusal appends `{time, rule, tool, agent_type, command first 80 characters}` to `.manifold/guard-log.jsonl` (the coordinator's observable, T33; the file is local and git-ignored by T5; the 80-character cap keeps secrets out).
**Acceptance:** `pytest bundles/base/tests/test_guard.py -q` passes; the failing run from T3 is quoted in the note. Residual gap stated in the file docstring: a script that writes files when run from a file is not inspected.
**Todo:** [x]
Note (2026-11-06): created `bundles/base/hooks/guard.py` (stdlib only; `ast.parse(feature_version=(3, 8))` ok). `python3 -m pytest bundles/base/tests/test_guard.py -q`: 209 passed (the T3 run above was the failing one: module missing). Deviations: (1) it tokenises with its own quote-aware scanner, not `shlex`, because `shlex` with punctuation cannot tell a quoted `>` from a real one; (2) `classify_bash(command, allow=None)` takes the human-exception list as an optional second argument, `pattern` is a regular expression that must match the whole command; (3) it also refuses agent writes to `.manifold/guard-log.jsonl` (not in the plan: an agent editing the log would defeat the review); (4) `classify_write` is default-deny for the coordinator, so T31's "coordinator cannot write plans, source or tests" case will pass at once and has no failing-first run. Docstring states the residual gaps (script run from a file; command substitution inside double quotes; tools the guard does not look at; Copilot field and tool names unverified).

---

### Task 5 — Ship the hook and the scratch folder in the payload
**Files:** `bundles/base/tools/build.py`, `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `HOOK_FILES = {"hooks/guard.py": (".manifold/hooks/guard.py", ALL_PROFILES)}` and `.manifold/scratch/.gitignore` (content `*` then `!.gitignore`, from `config/scratch.gitignore`, CREATE) to the `common` list in `build_payload`; make `lint` fail when `hooks/guard.py` does not compile or imports outside the standard library. Add tests: the files are in the zip and `bundle.json`; install and uninstall to an empty repo still leave it empty (extend `test_every_profile_and_format_uninstalls_to_an_empty_repo`); two builds are identical.
**Acceptance:** `pytest bundles/base/tests -q` passes; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [x]
Note (2026-11-06): `build.py` gains `HOOK_FILES`, `SUPPORT_FILES` (`config/scratch.gitignore` -> `.manifold/scratch/.gitignore`, content `*` then `!.gitignore`), a payload loop, and `lint_hook` (must compile; imports only the standard library; no relative imports). `python3 -m pytest bundles/base/tests -q`: 371 passed, 1 skipped at this step; `build.py --check`: `lint ok`. Tests added: files in the zip and `bundle.json` for all profiles, installed byte-identical, lint rejects a broken hook, a third-party or relative import, a missing file; `test_every_profile_and_format_uninstalls_to_an_empty_repo` now also asserts the hook and scratch file were installed (it still ends empty). "Two builds are identical" is covered by the existing `test_build_is_deterministic`, left unchanged. Deviation: a second support file, `config/manifold.gitignore` -> `.manifold/.gitignore` (content `guard-log.jsonl`), because T4 says the log is git-ignored by T5 and the scratch `.gitignore` does not cover `.manifold/guard-log.jsonl`; strike it if the owner prefers another way.

---

### Task 6 — Render the Claude hook into every agent
**Files:** `bundles/base/tools/build.py`, `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** In `render_agent` for `claude`, emit a `hooks:` block (a `PreToolUse` entry with the matcher and command from T1, the command uses `${CLAUDE_PROJECT_DIR}` because T1 leaves the hook's working directory unverified, e.g. `python3 "${CLAUDE_PROJECT_DIR}/.manifold/hooks/guard.py" --client claude`; owner accepted this on 2026-11-06) after `disallowedTools`, built from a constant `GUARD_HOOKS_CLAUDE`, so no canonical agent file repeats it. Test: every rendered `.claude/agents/*.md` carries the block; the frontmatter still starts on line 1; copilot and skills outputs do not carry the Claude block. Decision per [INT-20 Open questions][i20-oq] ("Hook in the bundle for consistent install"): per-agent frontmatter needs no merge into a user-owned `.claude/settings.json`; the cost is that the main session and plugin-run agents are not covered, which T39 states (see Open question 4).
**Acceptance:** `pytest bundles/base/tests -q -k hook` passes (new tests named with `hook`); K3 for the matcher and command form against T1.
**Todo:** [x]
Note (2026-11-06): `build.py` emits `GUARD_HOOKS_CLAUDE` after `disallowedTools` for every Claude agent: `matcher: "Bash|Edit|Write|MultiEdit|NotebookEdit"` (letters and `|` only, so an exact name list per harness-capabilities.md, "Matcher syntax"), command `python3 "${CLAUDE_PROJECT_DIR}/.manifold/hooks/guard.py" --client claude` (shell form, placeholder in double quotes, per the `$CLAUDE_PROJECT_DIR` row; read, not run in a client). `python3 -m pytest bundles/base/tests -q -k hook`: 23 passed at this step (33 at the end of CP2). Two existing tests pinned the exact Claude frontmatter and were adjusted for the new `hooks` key only (`test_claude_format_keeps_only_name_description_and_denied_tools` now expects `hooks` among the top-level keys; `test_claude_format_denies_the_tools_an_agent_does_not_declare` reads the frontmatter up to `hooks:`); their other assertions are unchanged, and T21 still has to change the reviewer assertions it names. Verified-claims list: matcher and command form read in harness-capabilities.md rows S1/S2; whether the hook fires in a real Claude Code session: not run.

---

### Task 7 — Render the Copilot hook file if T1 verified one
**Files:** `bundles/base/hooks/copilot-guard.json`, `bundles/base/tools/build.py`
**Action:** CREATE / MODIFY
**Change:** Owner decision (2026-11-06): ship the file even though T1 leaves enforcement in VS Code Local unverified ("that is what testing is for"); T39 states the gap and T37b observes it. Where T1 marks the Copilot `preToolUse` file schema verified (it does for `.github/hooks/*.json`, `version: 1`), create `hooks/copilot-guard.json` with that schema calling `python3 .manifold/hooks/guard.py --client copilot`, and ship it as `.github/hooks/manifold-guard.json` for the `copilot` format only. If T1 leaves it unverified, change nothing, mark this task `[~] unverified: confirm with the VS Code hooks page` and let T39 state that the Copilot flavor is instructions-only.
**Acceptance:** `json.load` of the file passes in `pytest`; `--format copilot` installs it and `--format claude` does not; or the `[~]` note names the missing source.
**Todo:** [x]
Note (2026-11-06): created `bundles/base/hooks/copilot-guard.json` (`version: 1`, `hooks.preToolUse` with `type: command`, `command: python3 .manifold/hooks/guard.py --client copilot`, `timeoutSec: 10`), shipped as `.github/hooks/manifold-guard.json` in the `copilot` format only (also with `both` and `all`). Per the owner's decision it ships although VS Code Local enforcement is unverified (harness-capabilities.md: file schema read in S3 and S6; Local use of `.github/hooks/*.json`, deny exit codes, agent identity and tool names unverified; nothing run). `install.py` `selected_entries` needed one change (a format entry with no `role` is chosen by profile, not skipped), outside the task's Files. Lint checks the file is JSON with `version` 1 and a `preToolUse` list. `python3 -m pytest bundles/base/tests -q`: 385 passed, 1 skipped at this step; tests cover the schema, install for copilot/both/all and not claude/skills, every profile, and uninstall to an empty repo.

---

### Task 8 — Widen the shell-write rule and give the legal route
**Files:** `bundles/base/rules/core/no-heredocs.md`
**Action:** MODIFY
**Change:** Keep the id (rule ids equal file names); set `title: Shell writes to files`, `applies_to: all`. Rule: no shell command writes or changes file contents (heredocs, `python - <<`, `sed -i`, `perl -i`, `tee`, `>`/`>>` into a file, `printf >>`), and no writing to `/tmp`. Instead: create or edit with `Write`/`Edit`; rename with `Edit` and `replace_all: true`; for a throwaway snippet write it with `Write` to `.manifold/scratch/` (or the scratchpad the session names) and run the file; if blocked, do not work around it, ask a human for an exception and say what you already tried. Enforce: `hook: .manifold/hooks/guard.py` and `review: compare "Rule exceptions" with .manifold/guard-log.jsonl`.
**Acceptance:** K1; K2: `test_rules_reach_only_the_roles_they_apply_to` and a new test that the rule text names `replace_all`, `.manifold/scratch/` and `/tmp` pass; the rendered `AGENTS.md` block line shows it (K3 by reading the rendered block).
**Todo:** [x]
Note (2026-11-06): rewrote `rules/core/no-heredocs.md` (id kept, `title: Shell writes to files`, `applies_to: all`, severity unchanged at medium, source `incident`; Rule, Why, Instead name `replace_all`, `.manifold/scratch/`, `/tmp`, the ask-a-human route; Enforce lists the hook and the "Rule exceptions" comparison). New tests `test_shell_write_rule_applies_to_every_role_and_names_the_sanctioned_routes` and `test_rendered_instructions_block_carries_the_shell_write_rule_for_every_profile`; `test_rules_reach_only_the_roles_they_apply_to` unchanged and passing. `python3 -m pytest bundles/base/tests -q`: 387 passed, 1 skipped at this step. Rendered block read: `- **Shell writes to files.** Do not write or change file contents from a shell command: ...` for the `build` profile (printed with `python3 -I -c`).

---

### Task 9 — Add the rule that a breach is reported as a breach
**Files:** `bundles/base/rules/core/rule-exceptions-line.md` (renamed from `report-rule-exceptions.md` by the owner, Michael Hay, 2026-11-07, because the old file name tripped the Write block; rule id is `rule-exceptions-line`)
**Action:** CREATE
**Change:** `applies_to: all`, severity high. Rule: every report from an agent that changed files or ran commands has a "Rule exceptions" line: `none`, or each exception with command, file and reason; never folded into notes or interpretations; never omitted when empty. Instead: if unsure whether something was an exception, list it. The `reviewer` and `coordinator` compare the line with the diff, the commit log and `.manifold/guard-log.jsonl`.
**Acceptance:** K1; K2: the rule appears in every role's rendered output (extend `test_every_rule_is_rendered_somewhere`).
**Todo:** [x]
Note (2026-11-07): the first attempt at `report-rule-exceptions.md` was refused by the Write tool ("Subagents should return findings as text, not write report files") and was not retried; the rename to `rule-exceptions-line` is the owner's decision (Michael Hay, 2026-11-07). Created `rules/core/rule-exceptions-line.md` (title "Rule exceptions", high, `applies_to: all`, source incident). New test `test_rule_exceptions_line_rule_reaches_every_role_in_every_rendering` (7 roles x claude, copilot, skills = 21 cases, checks the rendered rule line). Failing first: `python3 -m pytest bundles/base/tests -q -k rule_exceptions_line_rule` = 21 failed (rule missing). After: `python3 -m pytest bundles/base/tests -q` = 435 passed, 1 skipped; `python3 bundles/base/tools/build.py --check` = `lint ok`. `test_every_rule_is_rendered_somewhere` unchanged and passing.

---

### Task 10 — Add the "Rule exceptions" line to each agent's report
**Files:** `bundles/base/agents/{planner,coder,bug-coder,test-planner,test-coder,scenario-writer,reviewer}.agent.md`
**Action:** MODIFY
**Change:** In each agent's closing report section ("When you finish", "When all tasks are done", "Report"), add the bullet "**Rule exceptions:** `none` or each exception (command, file, reason)." The `reviewer` reports the comparison it made instead.
**Acceptance:** K2: new `test_every_agent_ends_with_a_rule_exceptions_line` over all roles and the claude and copilot outputs passes.
**Todo:** [x]
Note (2026-11-06): added the bullet `- **Rule exceptions:** `none` or each exception (command, file, reason).` to the closing section of planner, coder, bug-coder, test-planner, test-coder and a new short "When you finish" section in scenario-writer (it had none); the reviewer's bullet reports the comparison it made. `test_every_agent_ends_with_a_rule_exceptions_line` is parametrized over all 7 roles and the claude, copilot and skills outputs (21 cases) and checks the bullet follows the closing heading, once. `python3 -m pytest bundles/base/tests -q`: 408 passed, 1 skipped at this step.

---

### Task 11 — Create the breach record template
**Files:** `bundles/base/templates/AGENT_FAILURES_TEMPLATE.md`, `bundles/base/tools/build.py`
**Action:** CREATE / MODIFY
**Change:** Template for `docs/agents/<harness>-failures.md` (harness-named, e.g. `claude-desktop`, `vscode-copilot`; [INT-20 Open questions][i20-oq]). Header: harness, client version, how to add an entry (link to `docs/process/BREACH_PROCEDURE.md`). Entry fields, same for all: **Rule**, **What happened**, **Evidence** (transcript cited by location, no copy, no secrets), **Count**, **Agent** (planner, coder, coordinator, ...), **Disclosed by the agent** (yes / no / found by the reviewer after the fact, which the entry marks as concealed and counts separately), **Suggested change**, **Status** (open, rule changed, enforced, closed), **Intent** raised. Add to `TEMPLATE_PATHS` for all profiles at `docs/templates/AGENT_FAILURES_TEMPLATE.md`.
**Acceptance:** K1; K2: the template has each field name; K3: the entry fields match [INT-20 Proposed outcome 4][i20-p] item by item.
**Todo:** [x]
Note (2026-11-06): created `templates/AGENT_FAILURES_TEMPLATE.md` (header: Harness, Client version, Enforcement in this harness, How to add an entry; entry fields Rule, What happened, Evidence, Count, Agent, Disclosed by the agent, Suggested change, Status, Intent raised) and added it to `TEMPLATE_PATHS` for all profiles at `docs/templates/AGENT_FAILURES_TEMPLATE.md`. Read against INT-20 outcome 4 (rule, what happened, evidence, count, disclosed, suggested change, status): all seven present, plus Agent and Intent raised as the task says. Test `test_failures_template_has_the_header_and_every_entry_field` (fields in one fixed order). `python3 -m pytest bundles/base/tests -q`: 414 passed, 1 skipped (after T12); `build.py --check`: `lint ok`.

---

### Task 12 — Write the breach procedure
**Files:** `bundles/base/process/BREACH_PROCEDURE.md`, `bundles/base/tools/build.py`
**Action:** CREATE / MODIFY
**Change:** Who (the coordinator; the owner when there is none), when (after every run of an agent that changes files, and when the reviewer finds an undisclosed breach), how (create `docs/agents/<harness>-failures.md` from the template if missing; append, never rewrite an earlier entry; compare the agent's "Rule exceptions" with the diff, the commit log, `.manifold/guard-log.jsonl` and, where the client allows, the transcript; count per agent; a coordinator breach is recorded the same way), the rule for exceptions (only a human grants one in `.manifold/guard-allow.json`; the agent asks and shows what it tried; the exception is also recorded), how a repeat or a missed breach becomes a rule or hook change (a draft intent, not a chat message), and how the result goes back to Manifold: the coordinator drafts a GitHub issue body (entry ids, counts, harness, no transcripts) for the owner to post to `mediumroast/manifold` (from `git remote -v` in this repository; confirm, Open question 8). Ship to `docs/process/BREACH_PROCEDURE.md` for all profiles (add `PROCESS_PATHS` next to `TEMPLATE_PATHS` in `build.py`, same shape).
**Acceptance:** K1; K2: the installed path exists in every profile; K3 for the remote and the template path.
**Todo:** [x]
Note (2026-11-06): created `process/BREACH_PROCEDURE.md` (who and when, how to record, exceptions, from a record to a rule change, returning the result) and `PROCESS_PATHS` in `build.py` (this file only; T29 adds the other two) with a lint check and a payload loop; installed at `docs/process/BREACH_PROCEDURE.md` for all profiles. `test_failures_template_and_breach_procedure_are_installed_in_every_profile` installs and uninstalls each profile to an empty repo; `python3 -m pytest bundles/base/tests -q`: 414 passed, 1 skipped; `lint ok`. K3: the template path `docs/templates/AGENT_FAILURES_TEMPLATE.md` read in `TEMPLATE_PATHS`; the guard log and exception file paths and fields read in `hooks/guard.py` and covered by its tests; the Claude subagent transcript path read in harness-capabilities.md (access by the coordinator unverified, and the text says "not compared" then). Deviation: the procedure does not name the issue target `mediumroast/manifold`; "mediumroast" is in `FORBIDDEN_TERMS` for shipped text (T29 will scan process documents), so it says the owner names the repository. For this repository the target is `mediumroast/manifold` (Open question 8); `git remote -v` was not run here.

---

### Task 13 — Count the breaches of the first cycle from the transcripts
**Files:** none (read-only; counts go into T14)
**Action:** none
**Change:** For the `coder` runs of tasks T37 to T52 and the `planner` amendment runs of `docs/plans/PHASE_1_PLAN.md`, count shell commands that wrote files (`<<`, `sed -i`, `tee`, `>` into a file, `/tmp`) in the subagent transcripts (`~/.claude/projects/.../subagents/agent-<id>.jsonl`, [INT-20 Problem][i20]). Write the counting script with `Write` into the scratchpad, run the file, read only. If the transcripts cannot be found or read, stop and ask the owner for the locations or the counts (a refused read is not retried another way).
**Acceptance:** per agent: transcript location (not copied), number of commands, which disclosed. Numbers recorded in the task note.
**Todo:** [x]
Note (2026-11-06): read-only script `<scratchpad>/count_shell_writes.py` (run as `python3 -I`, with `list_subagents.py` and `show_commands.py` beside it) counted `Bash` tool calls once each by tool-use id and counted those `guard.classify_bash` refuses. Transcripts under `~/.claude/projects/-Users-mihay42-dev-manifold--claude-worktrees-hungry-kowalevski-9065dd/8baca43b-c11d-4b74-96e5-03b833764fd4/subagents/`: coder T37 to T52 `agent-a312f4646f33695d2.jsonl`: 83 commands, 11 flagged (5 heredoc-form, 5 `sed -i.bak`, 1 scratch redirect), 8 on tracked files; coder T52/T53 `agent-a90996579573e306b.jsonl`: 13, 0; coder T53 to T58 `agent-aa16acb99fd023aad.jsonl`: 23, 1 (no-op heredoc); planner amendments `agent-a3a9df028cd508eff.jsonl` 14, 1; `agent-a65d7d1008f830100.jsonl` 4, 1; `agent-a0f4737d86adb7298.jsonl` 9, 1; `agent-a026be49a3bf318c4.jsonl` 15, 0. Earlier planner run `.../sub-agents-access-e9e255/acd6e9f9-7b65-4f1f-9110-385f287fa8ec/subagents/agent-ae67e729d0a06a41d.jsonl`: 35, 7 (3 heredoc edits of the plan). Disclosed: from the plan notes, 1 of the 11 (Task 44 names its `scopes.py` heredoc); the hand-back messages are not in the subagent transcripts, so the rest is "not determined". The same method over F1's run gives 6, agreeing with F1 (4 heredocs plus the `printf`; a `sed -i.bak` on `.gitignore` is also found). Phase 2 runs: coder CP1 1, planner amend 1; this coder run 0 refused as of the count (38 commands).

---

### Task 14 — Append the new breaches to the first record
**Files:** `docs/agents/claude-desktop-failures.md`
**Action:** MODIFY (append only)
**Change:** After F3, append F4 (planner heredocs), F5 (coder heredocs in T37 to T52, with T13's count), F6 (no written coordinator procedure; fact: the role had no definition) and a closing "Pattern across checkpoints" row for the later checkpoints. Use the template's fields. Do not alter F1 to F3.
**Acceptance:** `git diff --numstat docs/agents/claude-desktop-failures.md` shows 0 deleted lines; K5: owner reads F4 to F6 (S5 of [INT-20][i20]).
**Todo:** [x]
Note (2026-11-06): appended F4 (planner), F5 (coder T37 to T52, with T13's count), F6 (no coordinator procedure), a counting-method paragraph and a "Pattern across checkpoints, later runs" table, in the template's fields, using Edit on the last line (F1 to F3 untouched). `git diff --numstat docs/agents/claude-desktop-failures.md`: `58	0` (58 added, 0 deleted). Where the data did not support the plan's wording it says so: F4's planner heredocs are 3 edits of the plan in the first planner run (the four amendment runs had a `sed -i.bak`, a scratch redirect and a no-op heredoc), and the old rule did not apply to the planner's own definition (inference). Awaiting K5 (owner reads F4 to F6).

---

### CP3 — Review policy (INT-23; checks K1, K2, K5). Needs Open questions 5 and 6.

### Task 15 — State the review defaults in the reviewer
**Files:** `bundles/base/agents/reviewer.agent.md`
**Action:** MODIFY
**Change:** Add to Inputs: the policy is `REVIEW.md` if present, otherwise the built-in defaults written in this file (the four passes, Important versus Nit, nit cap 5); the report states which policy it used; the reviewer never stops for lack of a policy and never invents a human threshold; the approval rule comes from `AGENTS.md` "Review process" (T16) and is reported as "applies / does not apply" for the change. Change the description's "and the repository's REVIEW.md" to "and the review policy".
**Acceptance:** K2: test that the reviewer text has the defaults, "states which policy" and no "second person"; K1.
**Todo:** [ ]

---

### Task 16 — Add the "Review process" stub to the installer
**Files:** `bundles/base/install.py`, `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `REVIEW_PROCESS_STUB` beside `COMMANDS_STUB`: heading `## Review process` and three lines for the owner to fill: `Repository type:` (`solo` or `team`), `Companion quality repository:` (`none` or its name), `Second approver (team only):`. `apply_block` adds it outside the managed block when absent, never filled by an agent. Update the uninstall "created and untouched" check (it compares to `COMMANDS_STUB`) to the combined stub. Tests: a fresh install writes the stub; an existing section is left; uninstall of an untouched created file removes it; an edited file is kept.
**Acceptance:** `pytest bundles/base/tests -q -k "created or stub or uninstall"` passes.
**Todo:** [ ]

---

### Task 17 — Say how the four passes apply to documents
**Files:** `bundles/base/agents/reviewer.agent.md`
**Action:** MODIFY
**Change:** Add a section "When the change is mostly documents or agent instructions": consistency and verified claims under **Bugs**; traceability under **Compliance**; the real-use evidence and `build`/test gates under **Tests**; severity rule from T2; link to `docs/process/REVIEW_CYCLE.md`. No new pass.
**Acceptance:** K2: test pins the section heading and the link; K5.
**Todo:** [ ]

---

### Task 18 — Fix the stale review-policy line in the rendered instructions
**Files:** `bundles/base/tools/build.py`
**Action:** MODIFY
**Change:** In `render_instructions_block` replace "Review policy lives in `REVIEW.md`, written from `docs/templates/REVIEW_TEMPLATE.md`." with: "Review: the passes and severity defaults are built into the `reviewer`; `REVIEW.md` (from `docs/templates/REVIEW_TEMPLATE.md`) is optional and adds repository-specific passes or exclusions; who approves is stated in the `Review process` section below." Add lines for `docs/templates/REVIEW_PLAN_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE.md`, `AGENT_FAILURES_TEMPLATE.md` and the `docs/process/` documents (profile-aware like the existing lines).
**Acceptance:** `pytest bundles/base/tests -q -k instruction` passes; K3: every path in the new lines is in `TEMPLATE_PATHS` or `PROCESS_PATHS`.
**Todo:** [ ]

---

### Task 19 — Create the per-phase review template
**Files:** `bundles/base/templates/REVIEW_PLAN_TEMPLATE.md`, `bundles/base/tools/build.py`
**Action:** CREATE / MODIFY
**Change:** Template for `docs/plans/REVIEW_PLAN_<N>.md`: header (phase, intent, commit reviewed, plan version, policy used: file or defaults, **Revision** number and timestamp, revision log table); counts by severity; findings by pass and severity each with id (`F1`...), location, evidence, direction, and **State** (`open`, `repaired`, `deferred`, `rejected`) with reason and evidence; "Rule exceptions compared" (agent line versus diff, log and commit); "Gates run" (command, counts, result; "not run" with reason); "CI on the pushed commit"; "Tests" (failing-first evidence and any changed existing test with its recorded approval); "Could not check"; the reminder that a human decides. Add to `TEMPLATE_PATHS` for `build` and `single`. A revision updates the same file and appends to the revision log ([INT-21 Open questions][i21-oq]).
**Acceptance:** K1; K2: template has each heading; K3: headings match [INT-21 S1][i21-s1] and [S6][i21-s6].
**Todo:** [ ]

---

### Task 20 — Slim the review template and say what it is for
**Files:** `bundles/base/templates/REVIEW_TEMPLATE.md`
**Action:** MODIFY
**Change:** Rewrite the header comment: this file is the optional repository policy `REVIEW.md` (additions and exclusions only; defaults live in the `reviewer`). Delete the "Human threshold" section; point to `AGENTS.md` "Review process". Keep passes, Important, nit cap and "Do not report".
**Acceptance:** K2: updated `test_review_template_has_passes_and_a_nit_cap` still passes and a new test finds no "Human threshold" heading; K1.
**Todo:** [ ]

---

### Task 21 — Let the reviewer write exactly one file
**Files:** `bundles/base/agents/reviewer.agent.md`, `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Set `tools: [read, search, execute, edit, todo]`. Replace "Read-only, by role" with: the reviewer edits only `docs/plans/REVIEW_PLAN_<N>.md` (create it from the template, revise it in place for a re-review), never code or the plan, enforced by `classify_write` where a hook exists. The chat reply is a pointer to the file plus the counts. Change the three tests named in Concerns 6: `test_reviewer_is_read_only_and_never_approves` (no edit tool → only the review file), `test_reviewer_never_edits_and_does_not_offer_to_once_tools_are_enabled` (keep "does not offer to edit code"), `test_claude_format_denies_the_tools_an_agent_does_not_declare` (reviewer no longer denies `Edit`/`Write`). Record in the note: "assertions changed with the owner's approval of this plan, [INT-21 Open questions][i21-oq]".
**Acceptance:** `pytest bundles/base/tests -q -k reviewer` passes; the rendered `.claude/agents/reviewer.md` has no `Edit` in `disallowedTools`.
**Todo:** [ ]

---

### Task 22 — Decide the review starter in the bundle (Open question 6)
**Files:** `bundles/base/templates/REVIEW_STARTER.md`, `bundles/base/tools/build.py`, `bundles/base/tests/test_bundle.py`
**Action:** DELETE / MODIFY
**Change:** Per the recommendation in Open question 6: remove `REVIEW_STARTER.md` and its `TEMPLATE_PATHS` entry; remove or rewrite the four tests that pin it (`test_build_profile_installs_review_md_from_the_starter`, `test_an_existing_different_review_md_is_a_conflict_and_is_left_alone`, `test_the_review_starter_has_the_template_headings_and_no_comments`, and the quality case in `test_quality_profile_does_not_install_review_md`). Existing installs keep their `REVIEW.md` (the installer never removes a file the bundle stopped shipping; verify with a test: install old payload, upgrade, file still present). If the owner chooses to keep it, strike this task.
**Acceptance:** `pytest bundles/base/tests -q` passes including the new upgrade test.
**Rollback:** `git revert` the commit; no installed repository is affected.
**Todo:** [ ]

---

### Task 23 — Fill this repository's review process and drop its unmeetable rule
**Files:** `AGENTS.md`, `REVIEW.md`
**Action:** MODIFY
**Change:** After the managed block add `## Review process` with `Repository type: solo (one maintainer, the owner)` and `Companion quality repository:` set to the owner's answer (Open question 5), and no second approver. In `REVIEW.md` replace the "Human threshold" paragraph with a pointer to that section. Both statements are the owner's: write only what the owner confirms at approval; if the companion repository is not answered, leave the placeholder and say so. Do not touch the managed block (T38 regenerates it).
**Acceptance:** `git diff` touches nothing between the `manifold:begin` and `manifold:end` markers; K5.
**Todo:** [ ]

---

### CP4 — Review-to-repair loop and checkpoints (INT-21; checks K1, K2, K3, K5)

### Task 24 — Add checkpoints and the amendment skeleton to the plan template
**Files:** `bundles/base/templates/PHASE_PLAN_TEMPLATE.md`
**Action:** MODIFY
**Change:** Under `## Tasks` add checkpoint headings `### CP<n> — <name>` with a **Verification** line ending each checkpoint (a demonstrable result, [INT-21 Open questions][i21-oq]); say a plan without checkpoints is one checkpoint. Add a closing `## Review amendment (round <n>)` skeleton: source `REVIEW_PLAN_<N>.md` revision, **Amendment approved by:** (blank, human), a repair checkpoint whose tasks each carry **Source:** `REVIEW_PLAN_<N>.md F<id>`, a table of findings not repaired (deferred or rejected, reason) and open questions. Add "Rule exceptions" and "Gates run" to the completion-summary list. Keep the file concise.
**Acceptance:** K2: updated `test_plan_template_carries_intent_concerns_and_cross_repository_lines` plus new assertions for `CP1`, `Amendment approved by` and `Source:`; K1.
**Todo:** [ ]

---

### Task 25 — Make the coder and the approval rules checkpoint-aware
**Files:** `bundles/base/agents/coder.agent.md`, `bundles/base/rules/core/approved-plan-before-execution.md`, `bundles/base/rules/core/dont-edit-the-test-to-pass.md`
**Action:** MODIFY
**Change:** `coder`: execute one checkpoint, verify, run the project gates and report each with command and real counts ("not run" with reason), update the plan, report, stop until told to continue; no checkpoints means one; repair checkpoints run only after the amendment's own **Amendment approved by** is filled by a human; a bug fix records the failing-first command and both results in the task note. `approved-plan-before-execution`: approval covers the tasks present when it was given; added tasks need their own approval line. `dont-edit-the-test-to-pass`, Instead: when a fix legitimately changes behavior an existing test pinned, stop, name the test and assertion, say why the old expectation is wrong, ask the owner; the coder edits the test only after a yes and records the approval and the change in the plan note ([INT-21 Open questions][i21-oq]: Coder).
**Acceptance:** K2: new tests for "stops after each checkpoint", "Amendment approved by", "failing-first" and the test-change route; the existing `test_a_request_to_edit_the_test_to_fit_the_bug_is_declined` still passes unchanged (record that); K5.
**Todo:** [ ]

---

### Task 26 — Make the planner amend from a review
**Files:** `bundles/base/agents/planner.agent.md`
**Action:** MODIFY
**Change:** Add "Checkpoints" (group tasks into numbered checkpoints each ending in a verification; dependency order holds; no task outside a checkpoint) and "Amending a plan from a review": input `REVIEW_PLAN_<N>.md`; add a repair checkpoint under `## Review amendment (round <n>)` with one task per Important finding, each with **Source:** and an acceptance line; list deferred and rejected findings with a reason; list open questions; do not change completed tasks or original acceptance lines; never fill in an approval line; make every plan edit with `Edit`, never the shell ([INT-20 Open questions][i20-oq]).
**Acceptance:** K2: new test pins "Amending a plan from a review", "Source:" and "never the shell"; K5.
**Todo:** [ ]

---

### Task 27 — Make bug-coder, test-planner and test-coder checkpoint-aware
**Files:** `bundles/base/agents/{bug-coder,test-planner,test-coder}.agent.md`, `bundles/base/templates/PHASE_TEST_PLAN_TEMPLATE.md`
**Action:** MODIFY
**Change:** `bug-coder`: group triage rows into checkpoints, stop after each, record failing-first evidence, same test-change route. `test-planner`: write `PHASE_<N>_TEST_PLAN.md` in checkpoints that mirror the phase plan's (plan template change in the test-plan template). `test-coder`: implement per checkpoint and stop ([INT-21 Open questions][i21-oq]: yes for bug fixes and test-side agents).
**Acceptance:** K2: one test per agent pinning "checkpoint"; K1.
**Todo:** [ ]

---

### Task 28 — Write the review-to-repair loop
**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** MODIFY
**Change:** Add sections: the sequence (review, `REVIEW_PLAN_<N>.md`, planner amendment, human approves the amendment, coder repair checkpoint, re-review in the same file as a new revision) as a table of who, input, output; "How a review is handled" (answers each point in [INT-21 Proposed outcome][i21-p]: separate session, what it reads, where output goes, who consumes it, findings to tasks, what stops a PR from being marked ready, how cycles end: until nothing or only Nits remain; limit 3 runs or until the human says enough; the human may set another limit); "How tests are handled" (all five points); the ready check (final-commit review exists, each finding repaired, deferred or rejected, CI of the exact commit read and a human confirmed it, approval per `AGENTS.md` "Review process"); the compatibility line. Link, do not restate, the templates and agents.
**Acceptance:** K3; K2: test that every step name appears in both flavors' `coordinator` (T33) and `reviewer`; K5.
**Todo:** [ ]

---

### Task 29 — Ship the procedures
**Files:** `bundles/base/tools/build.py`, `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `PROCESS_PATHS = {"process/REVIEW_CYCLE.md": ("docs/process/REVIEW_CYCLE.md", ALL_PROFILES), "process/BREACH_PROCEDURE.md": ("docs/process/BREACH_PROCEDURE.md", ALL_PROFILES), "HOWTO.md": ("docs/process/HOWTO.md", ALL_PROFILES)}`, include them in `common`, lint for their presence and the forbidden-term scan, and add `HOWTO.md` to the zip-root list in `build_zip`. Pointer lines in `reviewer`, `planner`, `coder` and (T33) `coordinator` to `docs/process/REVIEW_CYCLE.md`. New test `test_markdown_links_and_paths_resolve`: every relative link in the shipped Markdown resolves in the source, and every backticked `docs/...` path in an agent, template or process document is an installed path, a path a document creates (`docs/plans/`, `intent/`, `docs/agents/`) or on a short allowlist in the test.
**Acceptance:** `pytest bundles/base/tests -q` passes; the new test fails when a broken path is added (run once with a temporary bad link in a copy under the scratchpad, record it).
**Todo:** [ ]

---

### CP5 — Coordinator (INT-22; checks K1, K2, K3, K5)

### Task 30 — Add the pull request template
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `bundles/base/tools/build.py`
**Action:** CREATE / MODIFY
**Change:** Sections in the order of [INT-22 S3][i22-s3]: what and why; plan and intent; checkpoints done; review state and findings (link to `REVIEW_PLAN_<N>.md`, counts, commit reviewed); gates (command, counts); CI on the pushed commit (commit sha); rule exceptions; could not check; follow-ups; ready check (met / missing, human confirmation). Add to `TEMPLATE_PATHS` for `build` and `single`, installed at `docs/templates/PULL_REQUEST_TEMPLATE.md`.
**Acceptance:** K2: template has each heading; K1.
**Todo:** [ ]

---

### Task 31 — Add the coordinator write allowlist
**Files:** `bundles/base/hooks/guard.py`, `bundles/base/tests/test_guard.py`
**Action:** MODIFY
**Change:** Confirm the `classify_write` table written in T4 covers the coordinator (`docs/agents/*-failures.md` append and edit, `intent/INT-*.md` create-only) and the reviewer; add a case that the coordinator cannot write `docs/plans/PHASE_*_PLAN.md`, source or tests. Test first (failing), then fix.
**Acceptance:** `pytest bundles/base/tests/test_guard.py -q` fails then passes; both runs quoted.
**Todo:** [ ]

---

### Task 32 — Register the coordinator role
**Files:** `bundles/base/tools/build.py`, `bundles/base/install.py`, `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `"coordinator"` to `ROLES`, to every profile in `PROFILES`, to `SKILL_NAMES` (`coordinate-cycle`) and to `KNOWN_ROLES` in `install.py`; make `CLAUDE_DENY` keep the `Agent` tool for roles that declare the `agent` capability (leave it to every other role as is). Update the tests that count roles (`BUILD_ROLES`, `QUALITY_ROLES`, lines near 737 to 783 of `test_bundle.py`) to include it. The agent file comes in T33, so this task and T33 land in one commit; the build fails between them.
**Acceptance:** after T33: `pytest bundles/base/tests -q` passes; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 33 — Write the coordinator
**Files:** `bundles/base/agents/coordinator.agent.md`
**Action:** CREATE
**Change:** Frontmatter `tools: [read, search, execute, edit, agent, todo]` (Copilot names per T1). Body: Role (runs the cycle, does no one's work, speaks for no human); Operating rules; Inputs; the loop (link `docs/process/REVIEW_CYCLE.md`; start each agent with named inputs; the reviewer in its own subagent session, never the coder's; stop for the human where the procedure says); ready check (writes the check into the PR from the template, reads CI of the exact commit with the `gh` command T1/K3 verified, treats red or missing as a finding, never moves a PR out of draft, never merges, never says "ready" with something missing); tests duties as in [INT-22 item 8][i22-p]; guardrails watch (read "Rule exceptions" against the diff, `.manifold/guard-log.jsonl` and, where the client lets it, the transcript; record by `docs/process/BREACH_PROCEDURE.md`; record its own breaches); process-gap list and draft-intent handoff to the planner (status `draft`, never accepted, no agent or template edited); outward actions (push, PR, comments) only with the owner's go-ahead; no held-out scenarios passed to builders; where a client cannot start subagents the text says "ask the human to start the agent" and lists the inputs. No `{{ref:...}}` markers (Concern 4). No commit unless asked.
**Acceptance:** K1; K2: tests that the claude and copilot outputs exist, share one body, name `REVIEW_PLAN_`, `Amendment approved by`, "never moves a PR out of draft", "Rule exceptions" and every INT-22 duty; `--profile quality` and `--format skills` install it; K3 for the `gh` command; K5.
**Todo:** [ ]

---

### CP6 — HOWTO (checks K2, K3, K5; K4 after the phase)

### Task 34 — Write HOWTO.md
**Files:** `bundles/base/HOWTO.md`
**Action:** CREATE
**Change:** Sections: when to use each of the eight agents (table: use it when, do not use it when); the cycle in order (intent, plan, approve, code by checkpoint, review, repair, re-review, ready check, human merge) with, per step, what usually happens, what the human must do, what the agents will not do; the human gates in one list; what a breach looks like and where it is recorded; solo versus team; what differs by client (hook enforced or instruction only, per T1); how to start (link the installed paths). It links to `REVIEW_CYCLE.md` and the agents instead of restating them, and must not contradict them. Installs to `docs/process/HOWTO.md` (decision: yes, because the people and agents in the repository need it at hand and the other process documents install there too; the zip root also carries it like the README).
**Acceptance:** K2: test that HOWTO names every role in `build.ROLES` and every step name in `REVIEW_CYCLE.md`; K3 for each command; K5; K4 (the six questions of T42) after the phase.
**Todo:** [ ]

---

### Task 35 — Update README, INSTALL, MODELS and the live protocol
**Files:** `bundles/base/README.md`, `bundles/base/INSTALL.md`, `bundles/base/MODELS.md`, `bundles/base/tests/live-protocol.md`, `bundles/base/CONTRIBUTING.md`
**Action:** MODIFY
**Change:** README: eight roles (add `coordinator` row and fix "Seven"); the loop table gains review document, amendment and re-review; "Rules are advice, not enforcement" describes the guard hook and its residual gap (a script that writes when run from a file; the main session under per-agent hooks; Copilot per T1); merge the two "What gets installed" tables into the second, adding hook, scratch folder, process documents, new templates, the stub, `HOWTO.md`. INSTALL: new options or files, the Copilot enforcement statement required by [INT-20 Constraints][i20-c], how a human grants an exception. MODELS: one line, "Phase 2 content (guard, coordinator, loop) is not run on any model". `live-protocol.md`: rows for the guard refusal, the sanctioned route, the reviewer file, a checkpoint stop and the coordinator, one column per client. CONTRIBUTING: how the hook is tested.
**Acceptance:** K2: updated `test_readme_*` and `test_models_page_*` pass; link test (T29) passes; K3: every command quoted in INSTALL runs against the built zip in the scratchpad (record the list); K5.
**Todo:** [ ]

---

### CP7 — Refresh this repository, verify behavior and run the gates

### Task 36 — Run the bundle gates
**Files:** none
**Action:** none
**Change:** Run `python3 bundles/base/tools/build.py --check`, `python3 bundles/base/tools/build.py --out <scratchpad>/dist-1` and `--out <scratchpad>/dist-2`, compare the two zips with `cmp`, then the three project gates.
**Acceptance:** record each command with real counts: bundle tests `.venv/bin/python -m pytest bundles/base/tests -q`; `cd server && ../.venv/bin/python -m pytest -q` (unaffected, run to report); `.venv/bin/python tools/vendor_web.py --check`; `cmp` prints nothing.
**Todo:** [ ]

---

### Task 37 — Install check: both flavors from the same build (precondition)
**Files:** none (scratchpad repository)
**Action:** none
**Change:** Unzip the T36 `dist-1` build into `<scratchpad>/install-check/bundle`, run `install.py --format both --profile single` dry run then `--apply` in a new scratch git repository, list `.claude/agents`, `.github/agents` and `.github/hooks`, compare the `coordinator` body in both flavors, run `--status`, then `--uninstall --apply`. Record `sha256sum` of the zip and `git rev-parse HEAD`; T37b and T37c cite them.
**Acceptance:** both flavors list eight agents; the two coordinator bodies are identical after the frontmatter; the repository is empty after uninstall.
**Todo:** [ ]

---

### Task 37a — Adapt the live-protocol tooling to a one-repository job (only the gaps below)
**Files:** `tests/live/setup.sh`, `tests/live/lp.sh`, `tests/live/lp_verify.py`, `tests/live/README.md`, `tests/live/build_protocol.py`, `tests/live/PROTOCOL-claude-code.md`, `tests/live/PROTOCOL-copilot.md`
**Action:** MODIFY
**Change:** Owner instruction (Michael Hay, 2026-11-06, relayed by the coordinator): use the existing live-protocol tooling to compare Copilot and Claude Code on the Phase 1 test set. Read first: `tests/live/README.md`, the three scripts, `tests/live/PROTOCOL-copilot.md` Task 5, `bundles/base/tests/live-protocol.md` (its task 5, "Local checks: test-planner then test-coder cover the plan", is this job), `tests/results/README.md`, `docs/plans/design/testing-protocol.md`. Usage as read: `setup.sh <claude|copilot>` builds `~/manifold-live/<client>/{bundle,product,quality,manifold}` (needs `PRODUCT_SRC`; `PUBLIC_SRC` defaults to this repository; `LIVE_ROOT` moves the parent); `lp.sh <client> ready | reset <repo> | evidence <label> | where`; `lp.sh ... evidence` runs `lp_verify.py <client> <label> [--since "YYYY-MM-DD HH:MM"] [--test]`, which writes `sessions.md`, `verify.md` (with the exact models in the window) and `results-rows.md` from the Claude Code logs in `~/.claude/projects/` and the Copilot Local logs in VS Code `workspaceStorage/<hash>/chatSessions` (macOS path in the script; found through the folder the chat was opened in). What fits: the `manifold` scratch clone, the git snapshot, the session digest for both clients, the model line. What does not fit, and the edit for each (use `Edit` and `Write`; add no heredoc; leave the existing one in `lp.sh` `seed` alone):
1. `setup.sh` requires `PRODUCT_SRC` and a product with `mcp-server/` and plants a patch. Add `LIVE_REPOS` (default `product quality manifold`); with `LIVE_REPOS=manifold`, skip `PRODUCT_SRC` and steps 2 to 4.
2. `lp_verify.py` reads `~/dev/live/<client>` and `~/dev/manifold-public` while `setup.sh` and `lp.sh` use `~/manifold-live` (`LIVE_ROOT`): evidence would be read from the wrong tree. Make `lp_verify.py` use `LIVE_ROOT` (default `~/manifold-live`) and `PUBLIC_SRC` the way the shell scripts do.
3. The clone's venv gets only `pytest`; Phase 1 tests are the server tests. In `setup.sh` step 5 install `server/requirements-dev.txt -c server/requirements.lock` (AGENTS.md "Project commands") and run `cd server && ../.venv/bin/python -m pytest -q`.
4. `lp.sh ready` appends a bundle-test command to `AGENTS.md` "Project commands", next to this repository's own server-test command. Add `LIVE_SEED=none` to skip `seed`.
5. `lp.sh reset` runs `git reset --hard` and `git clean -fd`, and `ready` commits and tags. Add `MANIFOLD_DIR` (default `$ROOT/manifold`) so `evidence` can read the real checkout, and make `ready` and `reset` exit with an error when `MANIFOLD_DIR` is set. Honor `LIVE_REPOS` in the three `for r in product quality manifold` loops, and create `$ROOT` in `evidence` when `MANIFOLD_DIR` is set (the evidence folder is outside the repository).
6. `lp_verify.py` has no check for a phase test set (`task5` checks `mcp-server/tests` in the product). Add a check `testset` (register it in `CHECKS` and in the `expected` map as `{"test-planner", "test-coder"}`): every changed or new file is under `server/tests/` or `docs/plans/`, and the result line of `cd server && ../.venv/bin/python -m pytest -q`. The test files and the plan file count are read from `git`, not from the agent's claim.
7. `tests/live/README.md`: one line each for `LIVE_REPOS`, `LIVE_SEED`, `MANIFOLD_DIR`, `LIVE_ROOT` for `lp_verify.py`. `PROTOCOL-*.md` are generated and are not edited by hand.
8. No hard-coded bundle version (owner, 2026-11-06: "we need to not hard code things like the bundle version"). `setup.sh` line 32 unzips `manifold-base-0.1.0.zip`, and `build_protocol.py` writes `0.1.0` into the protocol text (lines 338, 389, 572, 760). Read the version once from `bundles/base/VERSION` in `$PUBLIC_SRC` (the file `release.yml` already compares with the tag) and use it in the zip name and in the generated text; look for any other literal version the same way (`grep -nE '0\.1\.0|manifold-base-'` over `tests/live/`) and replace each one. Regenerate the protocols with `python3 build_protocol.py` (without `--results`, so no filled results sheet is reset) and list the regenerated files in the diff. Add `tests/live/build_protocol.py`, `PROTOCOL-claude-code.md` and `PROTOCOL-copilot.md` to **Files**.
**Acceptance:** `bash -n tests/live/setup.sh tests/live/lp.sh` and `python3 -m py_compile tests/live/lp_verify.py` print nothing; `grep -nE '0\.1\.0|manifold-base-0' tests/live/*.sh tests/live/*.py` finds no literal version (a run of the grep with the real output is recorded); after changing `bundles/base/VERSION` in a scratch copy, `setup.sh` still finds the zip; `LIVE_REPOS=manifold` `setup.sh copilot` builds only `manifold` (T37b); `git diff --stat` lists only the seven files above. The scripts have no CI test (the README says the protocol does not run in CI), so the first real use is T37b; a failure there is a finding.
**Todo:** [ ]

---

### Task 37b — Copilot run in a scratch repository (a person drives the chat; the coordinating session captures)
**Files:** none in this repository (scratch tree `~/manifold-live/copilot/manifold`, outside the checkout, owner-confirmed)
**Action:** none
**Change:**
1. Coordinating session: `LIVE_REPOS=manifold tests/live/setup.sh copilot` (a clone of this branch, no remote), then in that clone `git rm -r .claude/agents` and commit, so VS Code sees one set of agents (whether VS Code also reads `.claude/agents` is unverified, Open question 2), then `install.py --format copilot --apply` from the clone's `bundle/` and `LIVE_SEED=none tests/live/lp.sh copilot ready`. Record: `git rev-parse HEAD:docs/plans/PHASE_1_PLAN.md`, `git rev-parse HEAD:server`, and `cmp` of `bundle`'s zip against the T37 zip (`setup.sh` rebuilds it; builds are reproducible, T36).
2. Human step (the only one): open the clone in VS Code, target Local, choose the Sonnet variant in the model picker before the first message (not Auto), pick `test-planner`, send exactly `Plan local tests for docs/plans/PHASE_1_PLAN.md.` (the wording of protocol Task 5), then write name and date on **Approved by** of the plan it wrote (a person, never an agent), start a new chat with `test-coder`, send exactly `Implement the test plan docs/plans/PHASE_1_TEST_PLAN.md.`, allow the project's pytest command once, and tell the coordinating session "done". Nothing is brought back by hand.
3. Coordinating session, after "done": `tests/live/lp.sh copilot evidence testset`. It reads the chat logs on this machine. If `sessions.md` finds no session, record "not observed" and ask the person for the chat export then, not before. Copilot hooks and subagents are unverified until T1/T7: record "guard: not observed" or the T7 result, not a guess.
**Acceptance:** `~/manifold-live/copilot/evidence/testset/` holds `sessions.md`, `verify.md`, `results-rows.md`; `docs/plans/PHASE_1_TEST_PLAN.md` exists in the scratch clone; `verify.md` names the exact model; `git status --short` in this repository is unchanged by the task. If the person has not done step 2, mark `[~]` with that reason.
**Todo:** [ ]

---

### Task 37c — Claude Code run: the real Phase 1 test set, in this repository (after T38)
**Files:** `docs/plans/PHASE_1_TEST_PLAN.md` (CREATE), test files under `server/tests/` named by that plan (CREATE), `docs/plans/REVIEW_PLAN_1.md` (CREATE by the reviewer). Kept, not thrown away (owner, 2026-11-06: this is real work on Manifold, "eating our own coffee beans"). Branch and PR: Open question 11.
**Action:** CREATE
**Change:** Run after T38, so the agents and guard installed here are the T36 build (`install.py --status` shows no MODIFIED), the same build Copilot got in T37b. Same inputs as T37b: record `git rev-parse HEAD:docs/plans/PHASE_1_PLAN.md` and `HEAD:server`, which must equal T37b's, the zip checksum, the exact Claude Code version and model (not forced equal to Copilot's). Normal rules apply:
1. Start `test-planner` with exactly `Plan local tests for docs/plans/PHASE_1_PLAN.md.`; a human writes name and date on **Approved by**; start `test-coder` in a new session with exactly `Implement the test plan docs/plans/PHASE_1_TEST_PLAN.md.`. The coordinating session runs `cd server && ../.venv/bin/python -m pytest -q` (the agent leaves the full suite to a human) and reports the real count.
2. A `reviewer` session, not one of the two above, reviews the change against the plan and writes `docs/plans/REVIEW_PLAN_1.md`; findings end repaired, deferred or rejected as in the review cycle.
3. Capture after each agent and at the end: `MANIFOLD_DIR=<this checkout> LIVE_REPOS=manifold LIVE_ROOT=<scratchpad>/live tests/live/lp.sh claude evidence testset`. Never run `ready` or `reset` here (T37a makes them refuse). Whether subagent sessions are read completely by `lp_verify.py` is unverified: read `sessions.md` after the first capture and note what is missing.
4. Stage explicit paths, commit only when the owner says so, and put nothing in PR #27 or `claude/sub-agents-access-e9e255`.
5. If a mistake or rule breach shows up (a guard refusal in `.manifold/guard-log.jsonl`, a "Rule exceptions" line, an undisclosed shell write, a test that does not test its case, an edited existing test), do not fix it quietly: record it per `docs/process/BREACH_PROCEDURE.md` (T12) in `docs/agents/claude-desktop-failures.md` (append only) and, where it points at an agent or rule defect, draft an intent. Improving the agents from this is the purpose.
**Acceptance:** `docs/plans/PHASE_1_TEST_PLAN.md` exists with **Approved by** filled by a human; every test file the plan names exists under `server/tests/`; the server suite result is recorded with its real count; `docs/plans/REVIEW_PLAN_1.md` exists; `~/.../live/claude/evidence/testset/` holds `sessions.md`, `verify.md`, `results-rows.md`; the breach record has an entry per breach or the note "none seen"; `git status --short` lists only these paths plus those of other tasks.
**Todo:** [ ]

---

### Task 37d — Record both runs in the existing results shape and compare
**Files:** `tests/results/claude-code-2/{summary,results,findings}.md`, `tests/results/copilot-2/{summary,results,findings}.md`, two rows in `tests/results/README.md`
**Action:** CREATE / MODIFY
**Change:** Follow `tests/results/README.md` "Adding a run": run ids client plus sequence; each `summary.md` in the shape of `copilot-1` (Client and version, exact model, bundle commit, scope "Local checks for `PHASE_1_PLAN.md` (task 5 of the live protocol)", result); `results.md` from each `results-rows.md` with every CHECK row decided by someone other than the agent that produced the output; `findings.md`. Remove local paths, dates and names; raw chat logs and the evidence folders stay out of the repository. What does not fit: the README's result counts assume the full 67-check protocol, so the Result column says "N Pass of N (testset only)"; and there is no comparison layout, so `copilot-2/summary.md` holds a "Compared with claude-code-2" section and `claude-code-2/summary.md` links to it. Held constant (written first): the plan blob and `server` tree hashes, the build zip checksum, the agent sources, the two prompts and their order. Differing, recorded as such: client, exact model for each, hooks and guard, scratch clone versus real repository, who approved. Compared, each filled or "not observed": files produced; cases (A and M cases in each test plan, test functions in the code); coverage of each `PHASE_1_PLAN.md` task per tool (Covered, Partly, Not covered, from each plan's case-to-task mapping, not the agent's claim); breaches (guard log, agent report, found in the diff); time and turns if the digest shows them; other differences (questions asked, stops, scope kept). One run each is one sample: say so, and that it is not a ranking. The Copilot test code is not copied anywhere; the Claude Code test set stays on its branch (T37c).
**Acceptance:** both results folders have the three files and no field is empty; `grep -rn "/Users" tests/results/claude-code-2 tests/results/copilot-2` prints nothing; the README table has both rows; `git status --short` lists only these results paths plus those of the other tasks.
**Todo:** [ ]

---

### Task 38 — Refresh this repository's own install
**Files:** `.claude/agents/*`, `docs/templates/*`, `docs/process/*`, `.manifold/*`, `AGENTS.md`
**Action:** MODIFY / CREATE
**Change:** From the extracted build, run `install.py --target <this repository> --status`, then a dry run, then `--apply` (no `--force`); a modified file is reported, not replaced. Re-read `AGENTS.md`: the managed block changed, T23's section is untouched, "Project commands" untouched.
**Acceptance:** `--status` reports no MODIFIED after the apply; `git status --short` lists only the paths in the inventory.
**Todo:** [ ]

---

### Task 39 — State the enforcement gap in the guides
**Files:** `bundles/base/INSTALL.md`, `docs/agents/harness-capabilities.md`
**Action:** MODIFY
**Change:** One table, one row per client and per agent type, column "enforced by hook" or "instructions only", from T1, T6, T7: the main session under per-agent hooks, plugin agents, Copilot where T7 is `[~]`. Same statement as the record's header in the template.
**Acceptance:** K3: each row cites a T1 row; K5.
**Todo:** [ ]

---

### Task 40 — DROPPED by the owner (was W1, the guard in a toy repository); replaced by real use
**Files:** none
**Action:** none
**Change:** Dropped by the owner, Michael Hay, 2026-11-06 (relayed by the coordinator): no toy walk-through. The improved agents, the guard hook, `REVIEW_CYCLE.md` and the `coordinator` are used on the next real Manifold work in this repository, and the evidence that they work comes from that use. This changes the following, and the coder writes nothing for this task beyond the handoff note below:
- **When.** After this phase's own gates (T36), T37 to T37d and T38 (the install refreshed in this repository) and the owner's approval of the agent-behavior text, not inside Phase 2. Phase 2 can be closed before the evidence exists. The one earlier sample is T37c (real work in this repository with the refreshed agents and guard).
- **Evidence, by source.** Guard refusals and sanctioned routes: `.manifold/guard-log.jsonl` and the agents' "Rule exceptions" lines (replaces W1; INT-20 S1 to S3). The loop: `docs/plans/REVIEW_PLAN_<N>.md` with its revisions, the amendment section, the checkpoint reports and the coordinator's PR text with its ready check (replaces W2; INT-21 S1, S2, S3, S5, S6; INT-22 S1, S2, S3, S8). Breaches: entries in `docs/agents/<harness>-failures.md` (INT-20 S4; INT-22 S4 to S6).
- **Who records it.** The coordinator records breaches and the PR summaries as the procedures (T12, T33) say; the owner, who is the only approver here, reads them and writes the verdict per scenario in the next phase plan's Completion checklist, or in a `tests/results/` run if one is made. A missing record is reported as "no evidence yet", never as a pass.
- **What Phase 2 can still check before then.** K1 and K2 (guard classification tests including the loophole table, rendering of rules and agents in both flavors, tool lists, determinism); K3 (every command, path and format a document states); K5 (the owner reads the agent text); the T37 install check and the T37b to T37d Phase 1 test-set runs, which use the installed agents in both tools. These show that the text and code are present and consistent; they do not show that an agent obeys the text.
- **Scenarios left without a live check inside Phase 2:** INT-20 S1, S2, S3; INT-21 S1, S2, S3, S5, S6; INT-22 S1, S2, S3, S8 (the mapping of W1 and W2 to scenarios is this plan's reading; T43 confirms it). Pinned by K2 text and tests only until real use.
**Acceptance:** this task is marked dropped, not done: `Todo: [-] dropped by the owner`; T43's rows for the scenarios above say "real use, after Phase 2 (T40)" in place of a walk-through; no `tests/results/` run exists for W1.
**Todo:** [-] dropped by the owner, 2026-11-06

---

### Task 41 — DROPPED by the owner (was W2, the whole loop on a toy task); replaced by real use
**Files:** none
**Action:** none
**Change:** Dropped by the owner, 2026-11-06, with T40; see T40 for when the evidence arrives, who records it and what is left unchecked. Whole-loop evidence is the next real run through intent, plan with checkpoints, approval, coder checkpoint, `REVIEW_PLAN_<N>.md`, amendment, repair, re-review as revision 2 and the coordinator's PR text. The independence rule still holds in real use: no agent reviews or approves its own text.
**Acceptance:** marked dropped, as T40.
**Todo:** [-] dropped by the owner, 2026-11-06

---

### Task 42 — DROPPED by the owner (was W3, HOWTO read cold by an agent); moves to real use
**Files:** none
**Action:** none
**Change:** Moved to real use by the owner's answer of 2026-11-06, like T40 and T41. When the HOWTO is first used on real work (by a person or an agent asked what to do next), the coordinator notes whether it answered these six questions correctly against `REVIEW_CYCLE.md` and the agents: which agent to start for a bug, what to do when the review finds an Important item, who moves a PR out of draft, what happens when a hook refuses, what a solo repository needs, what is not enforced in Copilot. A wrong answer is a finding against `HOWTO.md`. No intent scenario cites `HOWTO.md` (read: none of INT-20 to INT-23 names it), so no scenario loses its check; the HOWTO is checked in Phase 2 by K2, K3 and K5 only.
**Acceptance:** marked dropped, as T40.
**Todo:** [-] dropped by the owner, 2026-11-06

---

### Task 43 — Fill the traceability table
**Files:** `docs/plans/PHASE_2_PLAN.md`
**Action:** MODIFY
**Change:** Under the Completion checklist, add one row per "We will know when" line of the four intents (INT-20 S1 to S5, INT-21 S1 to S12, INT-22 S1 to S10, INT-23 S1 to S4) giving the file and section and the task, as Phase 1 did. A line with no home is reported, not dropped. A row whose only live check was W1 or W2 (listed in T40) names "real use, after Phase 2 (T40)" as its check.
**Acceptance:** K3: 31 rows; every path in it exists (`ls`); a reviewer can check it (S3 of [INT-22][i22-s3]).
**Todo:** [ ]

---

## Completion checklist
- [ ] All tasks marked [x] by the coder (T37b may stay `[~]` until the person who drove the Copilot chat has done it; T40 to T42 are `[-]` dropped by the owner and are not counted)
- [ ] The owner has been told which scenarios have only K2 text checks until real use (list in T40) and where the real-use evidence will be recorded
- [ ] `python3 bundles/base/tools/build.py --check` prints `lint ok`
- [ ] `.venv/bin/python -m pytest bundles/base/tests -q` passes, `cd server && ../.venv/bin/python -m pytest -q` passes (no regression), `.venv/bin/python tools/vendor_web.py --check` passes
- [ ] The traceability table (T43) is filled and every row resolves
- [ ] A review of the final commit exists as `docs/plans/REVIEW_PLAN_2.md`, written by the `reviewer` in its own session using the standard above; each finding is repaired, deferred or rejected with a reason; the owner has approved the agent-behavior text (K5)
- [ ] CI on the pushed commit is green and read by a human
- [ ] No [~] blocked items outstanding except those waiting on a human run
- [ ] Summary note added by the coder below this line

<!--
  coder: add your completion summary here:
  - Files changed
  - Deviations from the plan, and why ("None." if none)
  - Verification evidence: command and result for each check; anything not run, and why
  - Rule exceptions: none, or each (command, file, reason)
  - Deferred items and follow-ups
-->

## Open questions
Each has the planner's recommendation; the owner decides. **Answered by the owner (Michael Hay) on 2026-11-06, relayed by the coordinator:** 2 (both flavors, default stays `claude`), 3 (client scratchpad, else `.manifold/scratch/`), 4 (per-agent frontmatter), 5 (no quality repository, solo), 6 (remove `REVIEW_STARTER.md`), 7 (bump to `0.2.0` in a separate commit after the review), 8 (`mediumroast/manifold`), 9 (`HOWTO.md` installs into `docs/process/` and the zip root), 10 (not now), 11 (recommendation (i) agreed, with this change: the T37c evidence and the minor agent adjustments come back into this PR, see below). Also answered: **T23 may edit the root `REVIEW.md`** (yes), **T21 may change the three reviewer tests that pin it read-only** (approved, with the allowlist), **INT-22 "ready": a human moves a pull request out of draft, the coordinator never does**. 12 (standard (d), reconfirmed with the `tests/results/` records added to its evidence list). No open question remains. The owner approved this plan on 2026-11-06 (see **Approved by**).

1. ~~Review definition for document-heavy work.~~ **Resolved:** confirmed by the owner (Michael Hay) on 2026-11-03, relayed by the coordinator; recorded under Scope and in T2.
2. **Pre-release formats.** Evidence: `build_payload` already renders `claude`, `copilot` and `skills` into every zip; `install.py` defaults to `--format claude` (`main`, `--format` help); `README.md` and `INSTALL.md` document `--format copilot|both|all`; `MODELS.md` and `tests/results/copilot-1` hold Copilot results; this repository's `.manifold/manifest.json` records `formats: ["claude"]`; `test_bundle.py` tests formats (`test_format_selection`). So Copilot output is shipped and tested for structure; what is claude-only is the default and this repository's own install. Possible meanings: (i) default install becomes `both`; (ii) the pre-release must be run live in Copilot before release; (iii) Phase 2 content must exist in Copilot form. Recommendation: do (iii) (this plan does: every task renders both flavors and tests pin both) and (ii) as a manual gate (the T37b Copilot run is the first sample; W1 to W3 are dropped, T40 to T42, and become real use, repeated in VS Code Copilot Chat before release, recorded; today's `copilot-1` run predates Phase 2); keep the default at `claude`, because installing both could give one editor two entry points per role (whether VS Code also reads `.claude/agents` is unverified: confirm with the VS Code custom-agents page) and the installer already warns on overlap. What differs: Copilot has `preToolUse` hooks in Preview (T1); hook file schema, subagent tools and the `agents` restriction key are unverified until T1. The safe part planned: instructions, tests and docs for both flavors; the Copilot hook only if T1 verifies it (T7).
3. **Scratch directory name** (before CP2). Recommendation: the scratchpad the client names, else `.manifold/scratch/`, installed with a `.gitignore` of `*` so no root `.gitignore` edit is needed. Alternative: `experiments/` (already named in the old rule but meant for prototypes).
4. **Hook placement for Claude Code** (before CP2). Recommendation: per-agent frontmatter (T6): consistent install, no merge into `.claude/settings.json`; it leaves the main session and a `--agent` session uncovered unless T1 shows frontmatter hooks apply there. Alternative: the installer merges one hook entry into `.claude/settings.json` (project level, so within `no-global-config-changes`), covering all sessions, at the cost of a JSON merge and a conflict path. If the owner wants the coordinating session covered, choose the alternative and add one installer task.
5. **Companion quality repository for this repository?** (before CP2, for T23.) Unknown from the files; the owner answers `none` or the name. Also confirm `solo` for this repository (stated in [INT-23 Problem][i23]).
6. **Keep or remove `REVIEW_STARTER.md`?** (before CP3.) Keep: pro, new installs get a ready `REVIEW.md`, no extra step; con, it is a file whose content nobody owns, it invited the invented second-approver rule, and it duplicates the reviewer's defaults. Remove: pro, one source for defaults (the reviewer), `REVIEW.md` becomes optional and per-repository, fewer files and tests; con, a repository wanting a policy file copies `REVIEW_TEMPLATE.md` by hand. Recommendation: remove (T22; the owner leans the same way, [INT-23 Open questions][i23-oq]).
7. **Version bump?** The Phase 1 question is still unanswered. Recommendation: bump `bundles/base/VERSION` to `0.2.0` in a separate commit after the review, because installed files change and `release.yml` requires the tag to equal `VERSION`; this plan does not edit it.
8. **GitHub issue target for returned breach records.** Recommendation: `mediumroast/manifold` (from `git remote -v`), drafted by the coordinator, posted by the owner.
9. **Does an installed `HOWTO.md` belong in `docs/process/`?** Recommendation: yes (T29, T34). Alternative: zip root only.
10. **Install-time flags** for repository type and quality repository (`--repo-type`, `--quality-repo`). Recommendation: not now; the stub (T16) covers the current form, and flags belong with the MCP install form ([INT-23 Open questions][i23-oq]).
11. **Where does the Claude Code work of T37c land?** It is real work: `docs/plans/PHASE_1_TEST_PLAN.md`, tests under `server/tests/` and `docs/plans/REVIEW_PLAN_1.md`, kept. This branch (`claude/intent-agent-process-afd0ed`) carries the Phase 2 plan and intents, and the agents and guard it needs only after T38. Options: (i) its own branch cut from this branch after T38, its own PR, stacked on the Phase 2 PR; (ii) its own branch cut from `main` (which has `PHASE_1_PLAN.md`, read: `a44152f` is on `main`) with the T36 build installed in it first, its own PR; (iii) this branch and PR. Recommendation: (i); it keeps the agents identical to the Phase 2 build and keeps Phase 1 test work out of the Phase 2 review. Either way nothing goes to PR #27 or `claude/sub-agents-access-e9e255`. The Copilot scratch repository is outside the checkout (owner, 2026-11-06). **Owner answer (2026-11-06):** agreed with (i), and the reason is that this PR needs test evidence and artifacts of the improved agents from a real task, not a scratch one (the way the owner will run a QA pass of the agents). For safety the T37c work runs on a branch cut from this branch; the owner looks at the results and makes minor adjustments to the agents until satisfied, and those adjustments, the evidence and the T37c artifacts are brought back into this PR. Which merge or cherry-pick brings them back is decided when the results are in.
12. ~~**Reconfirm the reworded review standard (d)**~~ **Resolved:** reconfirmed by the owner on 2026-11-06, with the `tests/results/` records added to the evidence list (Scope). Original question: (Scope). The owner's confirmed wording of 2026-11-03 said behavior is tested "by a dry-run walk-through on a toy task". Because the owner moved W1, W2 and W3 (T40 to T42) to real use on 2026-11-06, the plan reworded (d) to real use with recorded evidence and "no evidence yet" until it exists. Please reconfirm or replace the wording; T2 copies it into `REVIEW_CYCLE.md` and the reviewer's document section (T20).

[i20]: ../../intent/INT-20-agent-guardrails-hold.md
[i20-p]: ../../intent/INT-20-agent-guardrails-hold.md#proposed-outcome
[i20-c]: ../../intent/INT-20-agent-guardrails-hold.md#constraints
[i20-oq]: ../../intent/INT-20-agent-guardrails-hold.md#open-questions
[i20-oos]: ../../intent/INT-20-agent-guardrails-hold.md#out-of-scope
[i21]: ../../intent/INT-21-review-to-repair-loop.md
[i21-p]: ../../intent/INT-21-review-to-repair-loop.md#proposed-outcome
[i21-oq]: ../../intent/INT-21-review-to-repair-loop.md#open-questions
[i21-s1]: ../../intent/INT-21-review-to-repair-loop.md#s1--a-review-leaves-a-document-behind
[i21-s6]: ../../intent/INT-21-review-to-repair-loop.md#s6--the-re-review-checks-the-repairs
[i22]: ../../intent/INT-22-coordinator-agent.md
[i22-p]: ../../intent/INT-22-coordinator-agent.md#proposed-outcome
[i22-oq]: ../../intent/INT-22-coordinator-agent.md#open-questions
[i22-s3]: ../../intent/INT-22-coordinator-agent.md#s3--every-pr-reads-the-same-way
[i23]: ../../intent/INT-23-review-policy.md
[i23-oq]: ../../intent/INT-23-review-policy.md#open-questions
