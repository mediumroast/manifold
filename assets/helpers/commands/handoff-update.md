Submit your implementation for source review.

Call wiki_handoff_tool(action="list", target="$COMPONENT", status_filter="in-progress")
to find the active handoff. Ask the user to describe what was implemented — what
changed, which files, how it addresses the handoff requirements. Then call
wiki_handoff_tool(action="request-review", path="...", notes="<description>").
Confirm to the user that the handoff is now awaiting source review (status: needs-review)
and that the source component should run /handoff-confirm or /handoff-reject.
