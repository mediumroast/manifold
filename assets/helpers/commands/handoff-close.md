Close the current handoff and record the resolution.

Call wiki_handoff_tool(action="list", target="$COMPONENT", status_filter="in-progress")
to confirm the active handoff. Ask the user for the resolution description,
then call wiki_handoff_tool(action="close", path="...", resolution="...").
Then update wiki/components/$COMPONENT.md Changelog.
