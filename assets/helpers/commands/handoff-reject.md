Reject a handoff implementation and send it back for rework.

Call wiki_handoff_tool(action="list", source="$COMPONENT", status_filter="needs-review")
to find the handoff. Show the current implementation notes. Ask the user to describe
specifically what is wrong or insufficient. Then call
wiki_handoff_tool(action="reject", path="...", notes="<feedback>").
Confirm to the user: the handoff is back in-progress with feedback in ## Blockers.
The target should run /handoff-update again when ready.
