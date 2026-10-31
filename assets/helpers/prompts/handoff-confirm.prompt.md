---
mode: agent
description: Confirm the target component's implementation satisfies this handoff
tools: ['{{MCP_SERVER}}/*']
---

Review and confirm a handoff implementation from the source component's perspective.

Step 1: Call wiki_handoff_tool(action="list", source="<this-component>", status_filter="needs-review")
        to find handoffs awaiting your review. Show each one's title and implementation notes.
Step 2: Ask the user: is the implementation satisfactory?
Step 3a: If yes — call wiki_handoff_tool(action="confirm", path="<path>", notes="<optional note>")
         Then prompt the user to close any related handoffs in the opposite direction
         with /handoff-close.
Step 3b: If no — use /handoff-reject to send it back with feedback.
