---
mode: agent
description: Post a cross-component handoff to the manifold wiki
tools: ['{{MCP_SERVER}}/*']
---

Post a new handoff to the manifold wiki using wiki_handoff_tool.

Call wiki_handoff_tool with:
  action: "create"
  source: "<source component slug>"
  target: "<target component slug>"
  type: "<feature | bug | breaking-change | integration-spec>"
  priority: "<critical | high | medium | low>"
  title: "<one-line description of the work>"
  summary: "<one paragraph: what needs to happen and why>"
  what_needs_to_happen: "<bulleted list of specific tasks for the target>"
  technical_details: "<API changes, schemas, data contracts, edge cases>"

If you are not sure of a value, ask before calling the tool.
After the tool returns, confirm the path and tell the user the handoff is live.
