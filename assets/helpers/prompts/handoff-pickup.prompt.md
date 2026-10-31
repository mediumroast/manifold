---
mode: agent
description: Discover and claim open handoffs for this component
tools: ['{{MCP_SERVER}}/*']
---

Find and claim a handoff for this component from the manifold wiki.

Step 1: Call wiki_handoff_tool(action="list", target="<this-component>", status_filter="open")
Step 2: Show the user the list of open handoffs with title, source, and priority.
Step 3: Ask which one to claim (if more than one).
Step 4: Call wiki_handoff_tool(action="claim", path="<selected path>")
Step 5: Show the summary and what_needs_to_happen from the response.
        This is the work brief — start implementation from here.
