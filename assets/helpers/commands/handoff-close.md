Close a handoff that THIS component raised (this component is its source), and record the resolution.

Only the source of a handoff closes it. If this component is the target (it is doing the work),
do not close: use /handoff-update to request review, and the source confirms or closes it.

Call wiki_handoff_tool(action="list", status_filter="needs-review") (and "in-progress") and keep the
handoffs whose source_component is "$COMPONENT". Show the title and implementation notes for each.
Ask the user for the resolution description (what was checked and accepted), then call
wiki_handoff_tool(action="close", path="...", resolution="...").
If the server answers that this component is not the source, stop and tell the user.
Then update wiki/components/$COMPONENT.md Changelog.
