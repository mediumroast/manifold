# Breach procedure

How a rule breach by an agent is found, recorded and fed back into the rules. It applies to every agent, including the `coordinator` and the main session. A breach is any command or edit that broke a rule in `AGENTS.md`, whether the guard refused it or it went through. This file ships in every install (at `docs/process/BREACH_PROCEDURE.md`).

## Who and when

- **Who:** the `coordinator` records breaches. Where there is none, the owner (the person who approves plans here) does.
- **When:** after every run of an agent that changes files, and whenever the `reviewer` finds a breach the agent did not report.
- **A breach by the coordinator** is recorded the same way, by the owner or by the `reviewer`, never left out because the coordinator is the one recording.

## How to record

1. **Find the record.** It is `docs/agents/<harness>-failures.md`, named for the client the agents ran in (for example `claude-desktop`, `vscode-copilot`). If it does not exist, create it from `docs/templates/AGENT_FAILURES_TEMPLATE.md` and fill in the header, including the enforcement statement: whether a hook runs in that harness.
2. **Compare.** Put the agent's "Rule exceptions" line next to four sources and note every difference:
   - the diff and the commit log of the run;
   - `.manifold/guard-log.jsonl` (one line per refusal by the guard: time, rule, tool, agent type, the first 80 characters of the command);
   - where the client keeps them, the agent's transcript (Claude Code keeps a subagent's at `~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl`; whether a given agent may read it is a permission matter, so say "not compared" when it cannot);
   - the agent's own report.
3. **Append an entry.** Add one entry per rule per run with the template's fields: Rule, What happened, Evidence, Count, Agent, Disclosed by the agent, Suggested change, Status, Intent raised. Append only: never rewrite or delete an earlier entry; a later change of status is a new line under that entry.
4. **Evidence.** Cite a transcript by its location; do not copy it. Put no secret or personal data in an entry. Mark a cause you did not prove as "inference".
5. **Count.** Count per agent and per rule: each separate command or edit that broke the rule is one. A breach the agent reported is counted as disclosed; one the `reviewer` or the coordinator found afterwards is marked concealed and counted separately.
6. **Say so in the review.** The `reviewer` lists what it compared under "Rule exceptions compared" in `docs/plans/REVIEW_PLAN_<N>.md`.

## Exceptions

Only a human grants an exception, by adding an entry to `.manifold/guard-allow.json` with `pattern`, `reason`, `granted_by` and `date`. An agent that is blocked does not work around the block: it stops, says what it tried and what it needs, and asks. An exception that is granted is also recorded as an entry in the failures record, with Status `open` until the rule or the guard is changed so the exception is no longer needed. No agent writes `.manifold/guard-allow.json` or the guard itself; the guard refuses it. The guard also refuses the agent definitions and hook setup (`.claude/agents/*.md`, `.claude/settings.json`, `.claude/settings.local.json`, the skill files, `.github/agents/*.agent.md`, `.github/hooks/manifold-guard.json`) unless a human grants a path exception: an entry with `"scope": "path"`, a `pattern` that matches the whole project-relative path, and a required `"expires": "YYYY-MM-DD"` (it grants nothing after that date). The owner edits the file by hand, and removes the entry when the work is done. An entry still present at the next run, expired or not, is listed by the coordinator with its `granted_by` and `reason`. `.manifold/guard-log.jsonl` shows each use as rule `exception-used`.

## From a record to a rule change

A breach that repeats, or that the guard missed, does not end as a chat message. The coordinator hands the entry to the `planner`, which drafts an intent (status `draft`, never `accepted`) from `docs/templates/INTENT_TEMPLATE.md`; the owner decides. The entry's Status moves to `rule changed` or `enforced` only when the rule or the guard has changed and a test shows it, and its **Intent raised** field names the intent.

## Returning the result to Manifold

When the owner wants the result to reach the Manifold source repository, the coordinator drafts a GitHub issue body: harness and client version, the entry ids, the counts per agent and rule (disclosed and concealed apart), the suggested changes, and no transcripts. The owner names the repository to post to (ask; do not guess) and posts it. The coordinator does not post it.
