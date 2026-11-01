# SPDX-License-Identifier: Apache-2.0
"""The tool policy: every tool is guarded, and the guard refuses the wrong principal (PHASE_1_PLAN T12)."""

import asyncio

import pytest

pytest.importorskip("fastmcp")

import server  # noqa: E402
from manifold_security import authorizer  # noqa: E402
from wiki_backend.guard import Guard  # noqa: E402

READ_TOOLS = {
    "wiki_read_tool": {"path": "wiki/CLAUDE.md"},
    "wiki_inventory_tool": {},
    "wiki_freshness_tool": {},
    "wiki_onboarding_tool": {},
    "wiki_reconcile_plan_tool": {"component": "acme-api"},
    "wiki_bundle_info_tool": {},
    "wiki_list_helpers_tool": {},
    "wiki_export_helper_tool": {"name": "ingest_doc"},
    "wiki_export_component_helpers_tool": {},
}
WRITE_TOOLS = {
    "wiki_write_page_tool": {"path": "wiki/components/acme-api.md", "content": "# x\n"},
    "wiki_log_append_tool": {"action": "lint", "message": "m", "component": "acme-api"},
    "wiki_agent_catalog_tool": {"component": "acme-api"},
    "wiki_handoff_tool": {"action": "create", "source": "acme-api", "target": "acme-web", "type": "feature",
                          "priority": "low", "title": "T", "summary": "s", "what_needs_to_happen": "w"},
    "wiki_register_component_tool": {"name": "newone", "description": "d", "repo": "https://x.test/r", "owner": "o"},
    "wiki_component_manage_tool": {"action": "archive", "name": "acme-api", "reason": "r"},
}


def _tools():
    async def listing():
        return {t.name: t for t in await server.app.list_tools()}
    return asyncio.run(listing())


def test_every_registered_tool_has_a_policy_and_the_policy_names_only_registered_tools():
    assert set(_tools()) == set(authorizer.TOOL_POLICY)


def test_every_registered_tool_function_is_guarded():
    names = list(_tools())

    async def functions():
        return {name: (await server.app.get_tool(name)).fn for name in names}
    unguarded = [n for n, fn in asyncio.run(functions()).items() if not getattr(fn, "__manifold_guarded__", False)]
    assert unguarded == []


def test_the_test_lists_cover_every_tool_except_ping():
    assert set(READ_TOOLS) | set(WRITE_TOOLS) | {"wiki_ping_tool"} == set(authorizer.TOOL_POLICY)


def test_a_tool_with_no_policy_is_refused():
    guard = Guard(server._store_access, lambda: None)

    def wiki_unlisted_tool():
        return {"ran": True}
    assert guard.guarded(wiki_unlisted_tool)().get("reason") == "no_policy"


def test_a_call_with_no_signed_in_principal_is_refused():
    guard = Guard(server._store_access, lambda: None)

    @guard.guarded
    def wiki_ping_tool():
        return {"ran": True}
    assert wiki_ping_tool()["reason"] == "unauthenticated"


@pytest.mark.parametrize("tool", sorted(READ_TOOLS) + sorted(WRITE_TOOLS))
def test_an_admin_only_principal_is_refused_every_read_and_write_tool(tool_world, tool):
    tool_world.who("root", "human", roles=["admin"])
    before = tool_world.git_log()
    result = tool_world.call("root", tool, **{**READ_TOOLS, **WRITE_TOOLS}[tool])
    assert result.get("refused") is True, result
    assert tool_world.git_log() == before


@pytest.mark.parametrize("tool", sorted(READ_TOOLS))
def test_a_reader_reads(tool_world, tool):
    tool_world.who("rita", "human", roles=["reader"])
    result = tool_world.call("rita", tool, **READ_TOOLS[tool])
    assert result.get("refused") is not True, result


@pytest.mark.parametrize("tool", sorted(WRITE_TOOLS))
def test_a_reader_cannot_write(tool_world, tool):
    tool_world.who("rita", "human", roles=["reader"])
    result = tool_world.call("rita", tool, **WRITE_TOOLS[tool])
    assert result.get("refused") is True, result


def test_ping_needs_only_a_signed_in_principal(tool_world):
    tool_world.who("root", "human", roles=["admin"])
    result = tool_world.call("root", "wiki_ping_tool")
    assert result["status"] == "connected" and result["principal"]["name"] == "root"


def test_no_tool_or_route_name_creates_credentials_roles_or_grants():
    forbidden = ("credential", "role", "grant", "deny", "admin", "setting", "principal", "token", "purge")
    names = list(authorizer.TOOL_POLICY) + list(authorizer.ROUTE_POLICY)
    assert [n for n in names if any(word in n for word in forbidden)] == []
    actions = [a for policy in authorizer.TOOL_POLICY.values() if isinstance(policy, dict) for a in policy]
    assert [a for a in actions if any(word in a for word in forbidden)] == []


def test_the_wiki_browser_needs_the_read_capability(tool_world, wiki_root, monkeypatch):
    from starlette.testclient import TestClient
    (wiki_root / "wiki" / "index.md").write_text("# hi\n")
    tool_world.who("root", "human", roles=["admin"])
    tool_world.who("rita", "human", roles=["reader"])
    client = TestClient(server.asgi_app, base_url="http://127.0.0.1:8686")
    admin = client.get("/docs/log.md", headers={"Authorization": "Bearer " + tool_world.tokens["root"]})
    reader = client.get("/docs/log.md", headers={"Authorization": "Bearer " + tool_world.tokens["rita"]})
    assert admin.status_code == 403
    assert reader.status_code != 403 and reader.status_code != 401
