---
id: INT-20
title: Agent guardrails hold, and breaches are recorded
author: Michael Hay
created: 2026-11-02
status: draft
affects: [bundles/base]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Agent guardrails hold, and breaches are recorded

## Problem
The base bundle's agents have written rules, and the first real cycle (Phase 1 of the security baseline, draft PR #27) showed that agents break them anyway. The rule `no-heredocs` (and the matching line in `AGENTS.md`) forbids writing files through shell heredocs. In that cycle:

- The `coder` wrote files through heredocs, `sed -i.bak` and a `/tmp` write across several checkpoints (recorded as F1-F3 in `docs/agents/claude-desktop-failures.md` on branch `claude/sub-agents-access-e9e255`). Restating the rule in the prompt did not stop it.
- Later in the same cycle (tasks T37-T52) the `coder` used heredocs or stdin scripts about four more times, despite a no-heredoc instruction in its prompt.
- The `planner` used bash heredocs to write plan edits.
- The coordinating session that relayed work between the agents had no written procedure, so nothing says what it may or may not do either.

Two things are missing. First, a rule that depends on the agent remembering it is not a guardrail: the tool call goes through, and nothing in the suite, the build or the review sees how a file was written. Second, there is no mechanism that records a breach. The record of F1-F3 exists only because someone wrote it by hand, it lives on a branch that is not on `main`, and the new breaches above are not in it. Breaches that are not recorded cannot be counted, so the process cannot be shown to be improving.

## Proposed outcome
1. **The common breaches are stopped where they happen.** The written rules are backed by enforcement at the tool boundary wherever the client allows it, so a heredoc, an in-place `sed`, a `tee` or a redirect into a file is refused when the agent tries it, with a message that names the right alternative.
2. **The rule gives the agent a legal way to do what it was trying to do.** A one-off snippet has a sanctioned route (write it to a named scratch directory with the file tools, then run the file). Renames have a named tool (`Edit` with `replace_all`). The scratch directory is named in the agent's instructions, so `/tmp` is not used.
3. **A breach is reported as a breach.** Every agent report that changes files has a "Rule exceptions" line (none, or each exception with the command and why). The line is not folded into "interpretations" or "notes".
4. **Breaches are recorded by a mechanism, not by luck.** There is one record in the repository, in a defined format, that holds every observed breach by any agent, including the planner and the coordinating session. Adding an entry is a step of a procedure with an owner, not an ad hoc act, and every entry has the same fields (rule, what happened, evidence, count, whether the agent disclosed it, suggested change, status).
5. **The record feeds the rules.** An entry that repeats, or that the enforcement missed, leads to a rule or enforcement change through the normal intent -> plan cycle, not a chat message.
6. **The first record is complete.** The F1-F3 history is carried over and the new breaches (planner heredocs, coder heredocs in T37-T52, the missing coordinator procedure) are added.

## Affected users and systems
- **The owner and maintainers** of the base bundle, who read the record to decide what to change.
- **Every agent** that can write files: `coder`, `bug-coder`, `test-coder`, `planner`, `test-planner`, `scenario-writer`. The `reviewer` is read-only and is affected as a reader of the record and of the exceptions line.
- **The coordinating session or agent** (see INT-22), which will observe breaches and add entries.
- **Rules and build:** `bundles/base/rules/core/` (the `no-heredocs` rule and its neighbours), `bundles/base/agents/*`, `bundles/base/tools/build.py` and `install.py` (the claude and copilot outputs, including any hook or settings file the installer writes), `AGENTS.md`, `bundles/base/tests/`.
- **Both agent flavors:** the `claude` agents (`.claude/agents/`) and the `copilot` agents (`.github/agents/`).
- **Repositories that install the bundle**, which receive the enforcement and the record's format.

## Constraints
- **Both flavors.** Every change applies to the `claude` and the `copilot` flavors. Where a client cannot enforce a rule at the tool level (Claude Code can run a hook before a Bash call; Copilot's equivalent may not exist), the intent does not accept silence: the same rule, the same sanctioned route and the same report line must still be in that flavor's instructions, and the gap is stated plainly in the install guide and the record.
- **Not in PR #27.** This work is not part of draft PR #27 (Phase 1 security baseline) and not on branch `claude/sub-agents-access-e9e255`. The existing failure record is moved or restated through this intent's plan, not by editing that branch.
- **No loopholes by wording.** The enforcement must not be defeated by a trivial variation (`python - <<EOF`, `cat >> f <<'EOF'`, `printf >> f`, `sed -i.bak`, `tee`, `> file`, `/tmp` paths). It must also not block read-only and normal use: `>` inside a quoted argument, `2>&1`, and `git`/test commands are allowed.
- **No silent override.** An agent that is blocked does not work around the block (the existing `no-workaround-after-refusal` rule). A human can allow an exception, and the exception is recorded.
- **Honest records.** Entries are factual first; causes are marked as inference where unproven. Transcripts are cited by location, not copied into the repository.
- **No secrets in the record.** Evidence excerpts must not carry credentials or personal data.
- **Offline, standard library only** for any tool added to the bundle, in line with `build.py`.
- **Determinism.** The build stays reproducible (building twice gives identical bytes).

## Scenario seeds

### S1 — A heredoc write is refused as it happens
**Who:** An agent (`coder`, `planner` or any file-writing agent) that is about to write or patch a file from the shell.
**Wants:** To be stopped at the moment of the attempt and told what to do instead.
**So that:** The rule holds even when the agent forgets it or its prompt does not repeat it.
**We will know when:** In a Claude-flavored install, a Bash call that writes a file through a heredoc, `sed -i`, `tee` or a redirect into a file is refused with a message naming `Write`/`Edit`, and the file is unchanged. In a Copilot-flavored install, the instructions carry the same rule and the install guide says what is and is not enforced.
**Must never:** Block ordinary read-only commands or test runs, or let a variant spelling of the same write through.

### S2 — A one-off snippet has a legal route
**Who:** A `coder` that wants to run a few lines to see what happens.
**Wants:** A sanctioned way to do it.
**So that:** Debugging does not push it toward heredocs or `/tmp`.
**We will know when:** The agent's instructions name the scratch directory and the steps (write the snippet to the scratch directory with the file tools, then run the file), and a run following those steps is not refused. A rename across many call sites is done with `Edit` and `replace_all` and needs no shell edit.
**Must never:** Leave `/tmp` or the repository tree as the only place a throwaway script can go.

### S3 — A breach shows up in the report
**Who:** The owner reading a coder's hand-back report.
**Wants:** To see at once whether any rule was broken.
**So that:** They do not have to read the transcript to find out.
**We will know when:** Every report from a file-writing agent has a "Rule exceptions" line that says "none" or lists each exception (command, file, reason), and the reviewer compares that line with the commit and the diff.
**Must never:** Present an exception as an "interpretation", or omit the line when there was nothing to report.

### S4 — A new breach is recorded by procedure
**Who:** The coordinating session after a run in which an agent broke a rule.
**Wants:** To add the breach to the record in a fixed way.
**So that:** The breach is counted and can drive a change.
**We will know when:** The record has a new entry in the standard format for each breach of the run, including breaches by the planner and by the coordinator itself, with a count per agent, a "disclosed by the agent: yes/no" field and a status; and the procedure that says when and how to add it is written down.
**Must never:** Leave a known breach recorded only in chat, or in a pull request description that is later lost.

### S5 — The record is complete for the first cycle
**Who:** A maintainer of the bundle.
**Wants:** One place that lists everything that went wrong in the first real cycle.
**So that:** The changes made in response can be traced to evidence.
**We will know when:** The record contains F1-F3 as they are today, plus the planner heredocs, the coder heredocs in T37-T52 (with the count) and the missing coordinator procedure, each with evidence, and it is on `main` after this intent's plan lands (not before).
**Must never:** Rewrite an earlier entry to look better, or copy a full transcript into the repository.

## Out of scope
- Changing what the rules say about other topics (secrets, force pushes, tests).
- Reviewing the content of PR #27 or of the Phase 1 plan.
- Auditing agents outside this repository's bundle.
- Building a general transcript-analysis tool. The first version records breaches that are observed; automatic detection beyond the tool-boundary hook is a later intent.
- The review procedure (INT-21) and the coordinator agent (INT-22), except as users of the record.

## Open questions
- Where does the record live (`docs/agents/claude-desktop-failures.md` as today, or a client-neutral name since the copilot flavor is covered too), and does it ship in the bundle as a template or stay a file in this repository only? (the product owner)
- Which mechanism enforces the rule in Claude Code: a project hook in `.claude/settings.json` written by the installer, or a hook shipped inside the bundle? The installer's rule on global config changes (`no-global-config-changes`) points to project-level only; confirm. (the product owner)
- What does the Copilot flavor have that is equivalent to a pre-tool hook? If nothing, is a documented gap plus a reviewer check enough? (the product owner, with a check of the current Copilot capabilities)
- Is the `planner`'s need to edit plan files better met by giving it a specific plan-update route (see INT-21) than by a rule alone? (the product owner)
- Should a breach found only by the reviewer (not disclosed by the agent) count differently in the record? (the product owner)
- Who can grant a one-off exception to the hook, and how is it recorded? (the product owner)
