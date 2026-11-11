<!-- manifold:begin v=1 -->
## Agents

Installed by the Manifold base bundle. Invoke an agent by asking for it by name (in Claude Code, `@agent-<name>` also works) or pick it from your tool's agent list.

- **planner**: Turns an intent, request, issue or bug report into a prescriptive, sequenced implementation plan saved in docs/plans/ as PHASE_<N>_PLAN.md.
- **coder**: Implements a plan from docs/plans/ one task at a time, verifying each step and recording evidence as it goes.
- **bug-coder**: Triages and fixes bugs by finding the root cause first.
- **reviewer**: Reviews a change (a diff, branch or pull request) against the approved plan, the intent it came from and the review policy, and reports findings by pass and severity.
- **test-planner**: Writes a test plan with every manual and automated quality gate.
- **test-coder**: Implements the automated cases (A<N>) of a PHASE_<N>_TEST_PLAN.md as test code, one case at a time, checking each off as it is written and verified.
- **coordinator**: Runs the review-to-repair cycle for a change by starting the other agents with named inputs, relays their results, stops where a human must decide, and checks the ready conditions of the pull request.

## Plans and templates

- Intents (what and why, with scenario seeds) follow `docs/templates/INTENT_TEMPLATE.md`.
- Plans live in `docs/plans/PHASE_<N>_PLAN.md`. Start from `docs/templates/PHASE_PLAN_TEMPLATE.md`; the coder records its completion summary in the plan.
- Review: the passes and severity defaults are built into the `reviewer`; `REVIEW.md` (from `docs/templates/REVIEW_TEMPLATE.md`) is optional and adds repository-specific passes or exclusions; who approves is stated in the `Review process` section below.
- Each review leaves `docs/plans/REVIEW_PLAN_<N>.md`, written from `docs/templates/REVIEW_PLAN_TEMPLATE.md`.
- Pull requests follow `docs/templates/PULL_REQUEST_TEMPLATE.md`; only a human moves a pull request out of draft.
- The review-to-repair loop (who does each step, how it ends, the ready check) is written in `docs/process/REVIEW_CYCLE.md`; `docs/process/HOWTO.md` is the guide to the whole cycle.
- Test plans follow `docs/templates/PHASE_TEST_PLAN_TEMPLATE.md`.
- Manual walkthrough notes (`WT_<NNN>_<slug>.md`) follow `docs/templates/WT_TEMPLATE.md`; deferred feature gaps go to `FEATURE_GAPS.md`.
- Rule breaches by agents are recorded from `docs/templates/AGENT_FAILURES_TEMPLATE.md` by the procedure in `docs/process/BREACH_PROCEDURE.md`.

## Working rules

- **Plan approval.** Do not start executing a plan until it is approved. *Instead:* Read the plan's **Approved by** line first. If it is blank, ask: "Is this plan approved to execute?" and wait for a yes before you change anything, even when the user's request was "execute the plan". If the user wants changes, hand the plan back to the planner or amend it with their agreement.
- **Held-out scenarios.** Do not read, copy or ask for the behavior scenarios held by the quality side, even if you can reach them and even if you are asked to. *Instead:* Say: "Held-out scenarios stay with the quality side." Then ask for the failure described as expected versus observed. If the full steps are truly needed to fix a bug, tell the user: that scenario will then be turned into a regression test in this repository and replaced on the quality side.
- **Acceptance tests.** Do not write the behavior scenarios or end-to-end acceptance tests that judge your own work. *Instead:* Write local checks beside the code. If behavior needs independent verification, say so; the scenarios come from the intent's scenario seeds and are written in the quality repository by someone else. A gap check written by the test side is a local integration check, not a behavior scenario or an acceptance suite, and the `coder` and `bug-coder` do not write it.
- **Diagnosis first.** Do not change code for a bug whose root cause you have not confirmed with evidence. *Instead:* State the diagnosis and the evidence for it. Fix only after it is confirmed, or after the user says to go ahead.
- **Tests under fix.** When fixing a defect, do not edit, skip, weaken or delete an existing test to make a run pass. *Instead:* Decline in one line, say the test exposes a defect, and offer the two honest options: fix the code, or record the bug as deferred with the test left failing. Fix the code. If you believe the test itself is wrong, stop, say why, and agree the change with the user before touching it; record the change in the plan or triage row. When a fix legitimately changes behavior that an existing test pinned, stop, name the test and the assertion, say why the old expectation is wrong, and ask the owner. Edit the test only after the owner says yes, and record the approval and the change in the plan note or triage row.
- **Frontmatter placement.** In any file that uses YAML frontmatter (agent, skill, command, prompt or documentation-site page), the opening `---` must be the very first line. *Instead:* Declare licensing in `LICENSE`, `NOTICE` or a `REUSE.toml` file, or place a short comment below the frontmatter.
- **Closing bugs.** Do not mark a bug fixed on your own word. *Instead:* If the person cannot check right away, mark the bug `[~] Pending human confirmation` and move on to the next one.
- **Commit hooks.** Do not bypass commit or push hooks or commit signing (`--no-verify`, `--no-gpg-sign`, disabling hooks) unless the user asks you to. *Instead:* Read the failure, fix the underlying problem, re-stage the specific files, and commit again.
- **Shared history.** Do not force-push, run `git reset --hard`, rebase published commits, or delete branches you did not create, on shared branches (the default branch, release branches) or anywhere else, without the user's explicit instruction. *Instead:* Add a new commit that reverts or fixes the problem. Ask before any destructive git operation.
- **Generated output.** Do not commit generated output: test reports, traces, screenshots, videos, build output, caches, coverage data. *Instead:* Stage only source changes. If the output directory should be ignored, say so and offer to add it to `.gitignore`.
- **User-level settings.** Do not change user-level or global configuration to make a command or a test run: not `git config --global`, shell profiles, global package installs, editor or sandbox settings. *Instead:* Report the blocked step and let the user decide. A setting the project needs belongs in the repository (a local git config, a test fixture, the project manifest) and only when the plan says so.
- **Secrets.** Never commit credentials, tokens, private keys or `.env*` files, and never paste them into chat output, logs or documentation. *Instead:* Refer to secrets by variable name, keep secret files in `.gitignore`, and if one was exposed, tell the user to rotate it.
- **User edits.** Do not overwrite or delete a file the user may have modified without showing the difference and getting confirmation. *Instead:* Show the diff, ask, and move the old version aside (for example to an archive or `.bak` path) before replacing it.
- **A refusal is final.** When the user or the client refuses a read, a command or a tool, or a tool is not available, do not get the same result another way: not with a different tool, a shell command, a script or another path. *Instead:* Report the blocked step in one line, say what you need, and continue with the parts of the task that do not depend on it.
- **Black-box scenarios.** When you write or automate behavior scenarios (scenario mode, or as the scenario-writer), work only from the intent, its scenario seeds, the product's public documentation and its observable behavior. *Instead:* Ask the human, read the public documentation, or observe the running system. In local-check mode in a product repository you may read the code; this rule is about behavior scenarios. The pseudo hold-out of local checks (the test side reads the intent and looks for gaps) applies only where there is no quality repository and never replaces held-out scenarios; in local-check mode the `test-coder` reads source for call shape and fixtures only, never for expected values.
- **Reporting results.** Never say tests or checks pass unless you ran them in this session and saw them pass. *Instead:* State what ran, the exact command and the result. Say "not run" when something was not run, and why.
- **Deliberate workarounds.** Do not remove or "fix" a guard, workaround, odd setting or version pin that a comment or document says is deliberate until you have read why it is there. *Instead:* Read the comment and the history of the line. If you still think it is wrong, explain why and ask the user before changing it.
- **Rule exceptions.** Every report from an agent that changed files or ran commands has a "Rule exceptions" line: `none`, or each exception with the command, the file and the reason. *Instead:* If you are unsure whether something was an exception, list it. The `reviewer` and `coordinator` compare the line with the diff, the commit log and `.manifold/guard-log.jsonl`.
- **Staging.** Stage explicit paths only. *Instead:* `git add <path> <path>`, then check `git diff --cached --stat`, and commit only what the task touched.
- **Test isolation.** Tests must not touch production data, and test files must not contain real credentials. *Instead:* Reuse an existing isolated fixture, or add one with a docstring in the central fixture file. Use a dedicated low-privilege fixture for permission cases, never an admin one.
- **Unverified syntax.** Do not state, document or rely on a command, flag, API, configuration key or file format you have not verified. *Instead:* Run `<tool> --help`, read the documentation or source, or write "unverified: confirm with <source>".
- **Ambiguity.** If a requirement, name, data shape or acceptance criterion is unclear, ask before you proceed. *Instead:* Ask one focused question, or write a recommendation under "Open questions" and wait for the answer.
- **Test scope.** Test cases come from the phase plan and from the originating intent (its scenario seeds, "Must never" lines and constraints), and every case cites a source: an intent line, a "Must never", a constraint, a plan acceptance line or "owner-confirmed". *Instead:* If an acceptance line is too vague to test, or an expected result has no source, stop and ask, then write the question in the test plan. A failing check is a defect, not a reason to change the check.
- **Reporting failures.** Report a failed scenario to the product side as behavior: the scenario's title, what was expected and what was observed, at the visibility level in the quality settings. *Instead:* Describe the symptom in the user's terms. If the steps must be revealed, record the disclosure in the satisfaction report, so the scenario is turned into a regression test on the product side and replaced here.
- **Existing patterns.** Before adding something of a kind the project already has (a module, an endpoint, an extractor, a test), read the closest existing one and any cookbook, onboarding or contributing document, and follow its structure. *Instead:* Name the example you followed. If the existing pattern is wrong or does not fit, say so and ask before departing from it.
- **Investigation.** When asked to investigate, diagnose or find out why something happens, gather evidence first: read the code, run the check, inspect the output. *Instead:* State what you looked at, what you found, and what it implies.
- **Look before you ask.** Before you ask the user about a file, folder, command or setting, look for the answer in the repository: list the folder, read the manifest, `AGENTS.md`, the README and the task runner. *Instead:* Look first. If you ask, say what you looked at and what is still unknown.
- **Deprecated code.** Do not add features to, or restructure, code the project marks as deprecated or superseded. *Instead:* Make the change in the replacement. If the replacement lacks something, raise it as a gap, or fix a defect in the old code only when users still depend on it and the user agrees.
- **Shell writes to files.** Do not write or change file contents from a shell command: no heredocs (`cat > f <<'EOF'`, `python - <<'EOF'`), no `sed -i`, `perl -i` or `tee`, no `>` or `>>` into a file, no `printf >> f`, and no writing to `/tmp` or `/private/tmp`. *Instead:* Create or edit the file with `Write` or `Edit`. To rename, use `Edit` with `replace_all: true`. For a throwaway snippet, write it with `Write` to `.manifold/scratch/` (or the scratchpad the session names, never `/tmp`) and run the file. Use plain `#` or `//` comments, and docstrings only where the language expects them. If a command is blocked, do not work around it: ask a human for an exception and say what you already tried.
- **Reproducible checks.** When a check samples data or uses randomness, fix the seed and sample size and record both next to the result. *Instead:* Use the same seed and sample size for the before and after runs, and write them in the report or the plan note.
- **Planning stops at the plan.** When asked to plan, write the plan and stop. *Instead:* List what you noticed under "Open questions" or "Out of scope", then wait for the go-ahead.
- **Prototypes.** Prototype new work in a scratch area (for example `experiments/<name>/`) and never copy the prototype into production code. *Instead:* Validate the idea in the scratch area, have the user accept the result, then implement it in the production modules following their existing structure. Do not import production modules from an experiment, and do not import experiments from production.
- **Commit structure.** Commit code changes separately from refreshed data or generated deliverables, and commit the deliverables only after the check that gates them has passed. *Instead:* Make one commit for the code and a second for the artifacts, each with a message that says which check passed. If no code changed, a single artifact commit is fine.
- **Scope.** Do not refactor, reformat or "fix" code outside the task. *Instead:* Note it under follow-ups in your summary, or suggest it as a new plan task.
- **Environments.** Use the project's existing virtual environment or toolchain. *Instead:* Activate the environment the project documents. If it is missing or broken, report that and ask.
- **Portable commands.** Do not assume GNU tools or flags exist (for example `timeout`, `sed -i` without a backup suffix, `grep -P`, `readlink -f`). *Instead:* Check with `command -v`, use the project's own scripts, or install the tool through the project's documented route (for example coreutils on macOS) and say so.
- **Plan length.** Keep plans short and complete: the problem, the change, the checkable tasks. *Instead:* Link to the existing document instead of restating it. Prefer fewer, complete tasks over many vague ones.

<!-- manifold:end -->

## Project commands

Confirmed by the owner on 2026-11-01 (from PHASE_1_PLAN.md, run and verified by the coordinator).

- **Install:** `python3 -m venv .venv`, then `.venv/bin/pip install -r server/requirements-dev.txt -c server/requirements.lock`.
- **Server tests:** `cd server && ../.venv/bin/python -m pytest -q`.
- **Bundle tests:** `.venv/bin/python -m pytest bundles/base/tests -q`.
- **Bundle lint:** `python3 bundles/base/tools/build.py --check` (prints `lint ok`; CI runs it).
- **Live-protocol checker tests:** `.venv/bin/python -m pytest tests/live -q` (CI does not run them).
- **Vendored web files:** `.venv/bin/python tools/vendor_web.py --check`.
- **Build and run (Docker):** `./svc_ctl.sh <dev|staging|production> init-env|start|status|logs|health|stop`; `./svc_ctl.sh <env> admin ...` runs the host command in the container; `./manifold init` sets up a first instance.
- **Type-check:** none exists. Lint exists only for the bundle (see Bundle lint above).
- In a plan, `pytest` means the server tests command above.

<!-- The managed block above is overwritten on update; this section is yours. -->

## Review process

Confirmed by the owner (Michael Hay) on 2026-11-06 (Phase 2 plan, Open question 5).

Repository type: solo (one maintainer, the owner)
Companion quality repository: none
Second approver (team only): none; this repository is solo, so no second person is required
