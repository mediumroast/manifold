Confirm that the target component's implementation satisfies this handoff.

Call wiki_handoff_tool(action="list", source="$COMPONENT", status_filter="needs-review")
to find handoffs awaiting your review. Show the title and implementation notes for each.
Ask the user: is the implementation satisfactory?
If yes: call wiki_handoff_tool(action="confirm", path="...", notes="<optional note>").
  Then prompt the user to close any related handoffs in the opposite direction with /handoff-close.
If no: use /handoff-reject instead to send it back with feedback.
