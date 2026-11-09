# Agent failures observed in <harness>
<!--
  Template for the record of rule breaches by agents. Copy this file to
  docs/agents/<harness>-failures.md, named for the harness the agents ran in
  (for example claude-desktop or vscode-copilot), fill in the header, and delete
  these comments. Add an entry by following docs/process/BREACH_PROCEDURE.md:
  append, never rewrite an earlier entry. Entries are factual first; a cause that
  is not proven is marked "inference". Cite a transcript by its location, never copy
  it, and put no secrets or personal data in an entry.
-->

**Harness:** <name, for example Claude desktop app (Code tab), VS Code Copilot Chat (Local)>
**Client version:** <version, or "not read">
**Enforcement in this harness:** <"hook: the guard runs before shell and file-write tool calls" or "instructions only: no hook runs here">. Where a hook does not run, the same rule, the same sanctioned route and the same "Rule exceptions" line are in the agent's instructions, and this record is how a breach is found.
**How to add an entry:** `docs/process/BREACH_PROCEDURE.md`.

---

## F<N> — <short title>: <date>

**Rule:** <the rule id and the sentence of it that was broken>
**What happened:** <the facts: what the agent did, in which task, with which files>
**Evidence:** <transcript, commit, guard-log line or report, cited by location; not copied; no secrets>
**Count:** <how many times in this run, and the running total for this agent and rule>
**Agent:** <planner, coder, bug-coder, test-planner, test-coder, scenario-writer, reviewer, coordinator, or the main session>
**Disclosed by the agent:** <yes / no / found by the reviewer after the fact>
<!-- "found by the reviewer after the fact" means the agent concealed it; the entry marks it as concealed and the record counts it separately from the disclosed ones. -->
**Suggested change:** <a rule, an instruction or an enforcement change, or "none">
**Status:** <open / rule changed / enforced / closed>
**Intent raised:** <the intent id, or "none yet">
