---
mode: agent
description: Close a completed handoff and record the resolution
tools: ['{{MCP_SERVER}}/*']
---

Close a completed handoff in the manifold wiki.

Step 1: Call wiki_handoff_tool(action="list", target="<this-component>", status_filter="in-progress")
        to find the active handoff, or use the path if already known.
Step 2: Ask the user to describe what was done (root cause, fix applied, files changed).
Step 3: Call wiki_handoff_tool(action="close", path="<path>", resolution="<description>")
Step 4: Read wiki/components/<target-component>.md and add a ## Changelog entry
        describing the fix. Update last_updated to today.
Step 5: Confirm completion to the user.
