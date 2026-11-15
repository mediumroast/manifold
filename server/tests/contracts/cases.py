# SPDX-License-Identifier: Apache-2.0
"""The contract cases the recorder runs (PHASE_4_PLAN Tasks 17 and 18).

Each entry is `(tool, case name, case)`; the recorder writes `<tool>.<case name>.json` from it.
Every case runs against a fresh private copy of `examples/acme` (a fictional instance).  The
caller is a human with the roles listed; it holds a grant on every Acme component and `_shared`.
"""

HUMAN = {"kind": "human", "roles": ["contributor", "registrar"]}
READER = {"kind": "human", "roles": ["reader"]}
AGENT = {"kind": "agent", "roles": ["contributor"]}

OPEN_HANDOFF = "wiki/handoffs/acme-web-to-acme-api/feature-order-history-endpoint.md"
ACTIVE_HANDOFF = "wiki/handoffs/acme-cli-to-acme-api/bug-cancel-returns-500-for-an-order-that-alr.md"
NEW_COMPONENT = {"name": "contract-new", "description": "A new component for a contract case.",
                 "repo": "https://example.test/contract-new", "owner": "Contract team", "skip_source_docs": True}

_REVIEW = {"tool": "wiki_handoff_tool",
           "arguments": {"action": "request-review", "path": ACTIVE_HANDOFF, "notes": "Fixed and tested."}}


def case(tool, name, arguments, caller=HUMAN, setup=None, files=None):
    entry = {"arguments": arguments, "caller": caller}
    if setup:
        entry["setup"] = setup
    if files:
        entry["files"] = files  # {relative path: text} written into the private copy before the case
    return (tool, name, entry)


# Fictional agent files for the agent-catalog listing case; the Acme example has none of its own.
AGENT_FILES = {
    "raw/acme-api/agents/acme-planner.agent.md":
        "---\nname: acme-planner\ndescription: Plans work for the fictional Acme API.\n---\n\n# Acme planner\n\nPlans.\n",
    "raw/acme-api/agents/acme-coder.agent.md":
        "---\nname: acme-coder\ndescription: Builds the fictional Acme API.\n---\n\n# Acme coder\n\n"
        "## Stack facts\n\n- Python 3\n\nTo verify, run `make check`. Run `make test` in full.\n",
}


CASES = [
    # Read tools (Task 17)
    case("wiki_ping_tool", "ok", {}),
    case("wiki_read_tool", "ok", {"path": "wiki/components/acme-api.md"}),
    case("wiki_read_tool", "missing_path", {"path": "wiki/components/no-such-page.md"}),
    case("wiki_read_tool", "outside_the_wiki", {"path": "../../etc/passwd"}),
    case("wiki_inventory_tool", "ok", {}),
    case("wiki_freshness_tool", "ok", {}),
    case("wiki_freshness_tool", "one_component", {"component": "acme-api"}),
    case("wiki_onboarding_tool", "ok", {}),
    case("wiki_reconcile_plan_tool", "ok", {"component": "acme-api"}),
    case("wiki_reconcile_plan_tool", "unknown_component", {"component": "no-such-component"}),
    case("wiki_bundle_info_tool", "ok", {}),
    case("wiki_list_helpers_tool", "ok", {}),
    case("wiki_export_helper_tool", "ok", {"name": "ingest_doc"}),
    case("wiki_export_helper_tool", "unknown_helper", {"name": "no_such_helper"}),
    case("wiki_export_component_helpers_tool", "ok", {}),
    # Write tools (Task 18)
    case("wiki_write_page_tool", "create",
         {"path": "wiki/decisions/contract-case.md", "content": "# Contract case\n\nBody.\n", "message": "contract create"}),
    case("wiki_write_page_tool", "update",
         {"path": "wiki/architecture/overview.md", "content": "# Overview\n\nChanged.\n",
          "etag": "@etag:wiki/architecture/overview.md", "message": "contract update"}),
    case("wiki_write_page_tool", "stale_etag",
         {"path": "wiki/architecture/overview.md", "content": "# Overview\n\nNew.\n",
          "etag": "0000000000000000", "message": "contract stale"}),
    case("wiki_write_page_tool", "protected_field_change",
         {"path": "wiki/components/acme-api.md",
          "content": "---\ncomponent: \"acme-api\"\nowner: \"Somebody else\"\n---\n\n# Acme Api\n",
          "etag": "0000000000000000", "message": "contract protected"}),
    case("wiki_write_page_tool", "invalid_frontmatter",
         {"path": "wiki/decisions/contract-bad.md", "content": "---\ntitle: [unclosed\n  : bad\n---\n\n# Bad\n",
          "message": "contract invalid"}),
    case("wiki_log_append_tool", "ok",
         {"action": "lint", "message": "Contract case entry.", "component": "acme-api"}),
    case("wiki_agent_catalog_tool", "ok", {"component": "acme-api"}),
    case("wiki_agent_catalog_tool", "with_agents", {"component": "acme-api"}, files=AGENT_FILES),
    case("wiki_handoff_tool", "create",
         {"action": "create", "source": "acme-api", "target": "acme-web", "type": "feature", "priority": "low",
          "title": "Contract case handoff", "summary": "A summary.", "what_needs_to_happen": "Do the thing."}),
    case("wiki_handoff_tool", "claim", {"action": "claim", "path": OPEN_HANDOFF}),
    case("wiki_handoff_tool", "request_review", _REVIEW["arguments"]),
    case("wiki_handoff_tool", "confirm", {"action": "confirm", "path": ACTIVE_HANDOFF, "notes": "Looks right."},
         setup=[_REVIEW]),
    case("wiki_handoff_tool", "reject", {"action": "reject", "path": ACTIVE_HANDOFF, "notes": "Needs a test."},
         setup=[_REVIEW]),
    case("wiki_handoff_tool", "close", {"action": "close", "path": ACTIVE_HANDOFF, "resolution": "Done."}),
    case("wiki_handoff_tool", "list", {"action": "list"}),
    case("wiki_register_component_tool", "ok", NEW_COMPONENT),
    case("wiki_component_manage_tool", "update",
         {"action": "update", "name": "acme-api", "description": "A changed description."}),
    case("wiki_component_manage_tool", "archive", {"action": "archive", "name": "contract-new", "reason": "retired"},
         setup=[{"tool": "wiki_register_component_tool", "arguments": NEW_COMPONENT}]),
    case("wiki_component_manage_tool", "restore", {"action": "restore", "name": "contract-new"},
         setup=[{"tool": "wiki_register_component_tool", "arguments": NEW_COMPONENT},
                {"tool": "wiki_component_manage_tool",
                 "arguments": {"action": "archive", "name": "contract-new", "reason": "retired"}}]),
]
