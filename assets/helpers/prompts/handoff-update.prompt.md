---
mode: agent
description: Submit your implementation for source review
tools: ['{{MCP_SERVER}}/*']
---

Submit a completed handoff implementation for source review.

Step 1: Call wiki_handoff_tool(action="list", target="<this-component>", status_filter="in-progress")
        to find the active handoff, or use the path if already known.
Step 2: Ask the user to describe what was implemented — what changed, which files,
        how it addresses the handoff requirements.
Step 3: Call wiki_handoff_tool(action="request-review", path="<path>", notes="<description>")
Step 4: Confirm to the user: the handoff is now awaiting source review (status: needs-review).
        Tell them the source component should run /handoff-confirm or /handoff-reject.
