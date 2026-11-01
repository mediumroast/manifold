---
mode: agent
description: Close a handoff this component raised (source only) and record the resolution
tools: ['{{MCP_SERVER}}/*']
---

Close a handoff that this component raised, in the manifold wiki.

Only the source of a handoff closes it. If this component is the target (it is doing the work),
do not close: request review with /handoff-update, and the source confirms or closes it.

Step 1: Call wiki_handoff_tool(action="list", status_filter="needs-review") (and "in-progress")
        and keep the handoffs whose source_component is this component, or use the path if already known.
Step 2: Ask the user to describe what was checked and accepted (what the target delivered, how it was verified).
Step 3: Call wiki_handoff_tool(action="close", path="<path>", resolution="<description>")
        If the server answers that this component is not the source, stop and tell the user.
Step 4: Read wiki/components/<this-component>.md and add a ## Changelog entry
        describing the result. Update last_updated to today.
Step 5: Confirm completion to the user.
