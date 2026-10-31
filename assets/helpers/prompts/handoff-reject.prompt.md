---
mode: agent
description: Reject a handoff implementation and request rework
tools: ['{{MCP_SERVER}}/*']
---

Reject a handoff implementation from the source component's perspective.

Step 1: Call wiki_handoff_tool(action="list", source="<this-component>", status_filter="needs-review")
        to find the handoff. Show the current implementation notes.
Step 2: Ask the user to describe specifically what is wrong or insufficient.
Step 3: Call wiki_handoff_tool(action="reject", path="<path>", notes="<feedback>")
Step 4: Confirm to the user: the handoff is back in-progress with your feedback
        in ## Blockers. The target should run /handoff-update again when ready.
