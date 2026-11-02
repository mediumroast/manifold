# SPDX-License-Identifier: Apache-2.0
"""Updating, archiving and restoring components (PHASE_1_PLAN T17)."""

import datetime

import pytest
from starlette.testclient import TestClient

pytest.importorskip("fastmcp")

from manifold_security import principals, settings  # noqa: E402
from wiki_backend.config import load_config  # noqa: E402

HANDOFF = {"action": "create", "source": "acme-api", "target": "acme-web", "type": "feature", "priority": "low",
           "title": "Order status", "summary": "s", "what_needs_to_happen": "w"}


@pytest.fixture()
def world(tool_world):
    tool_world.who("reg", "human", roles=["registrar"])
    tool_world.who("bot", "agent", roles=["registrar"])
    tool_world.who("ann", "human", roles=["contributor"], grants=["acme-api", "acme-web", "_shared"])
    tool_world.who("rita", "human", roles=["reader"])
    return tool_world


def manage(world, who, action, name="acme-cli", **extra):
    return world.call(who, "wiki_component_manage_tool", action=action, name=name, **extra)


def test_the_tool_is_registered_and_pinged(world):
    assert "wiki_component_manage_tool" in world.call("rita", "wiki_ping_tool")["tools"]
    assert world.call("rita", "wiki_ping_tool")["tool_count"] == 16


@pytest.mark.parametrize("who", ["ann", "rita"])
def test_only_a_registrar_manages_components(world, who):
    assert manage(world, who, "archive", reason="r")["refused"] is True
    assert manage(world, who, "restore")["refused"] is True
    assert manage(world, who, "update", description="d")["refused"] is True


def test_archive_needs_a_reason(world):
    assert "reason" in manage(world, "reg", "archive")["error"]
    assert "reason" in manage(world, "reg", "archive", reason="   ")["error"]
    assert principals.get_component_state(world.conn, "acme-cli").archived is False


def test_archive_is_refused_while_a_handoff_is_open_and_names_it(world):
    created = world.call("ann", "wiki_handoff_tool", **HANDOFF)
    for slug in ("acme-api", "acme-web"):  # source and target
        refused = manage(world, "reg", "archive", name=slug, reason="retired")
        assert created["path"] in refused["error"] and refused["open_handoffs"] == [created["path"]]
        assert principals.get_component_state(world.conn, slug).archived is False
    assert manage(world, "reg", "archive", name="acme-cli", reason="retired")["status"] == "archived"  # unrelated


def test_archive_is_allowed_once_the_handoffs_are_completed(world):
    created = world.call("ann", "wiki_handoff_tool", **HANDOFF)
    world.call("ann", "wiki_handoff_tool", action="close", path=created["path"], resolution="done")
    assert manage(world, "reg", "archive", name="acme-api", reason="retired")["status"] == "archived"


def test_archive_records_the_hold_a_log_entry_and_an_audit_row(world):
    result = manage(world, "reg", "archive", reason="No longer used")
    assert result["status"] == "archived"
    hold = settings.get(world.conn, "purge_hold_days")
    expected = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=hold)
    assert result["purge_after"][:10] == expected.strftime("%Y-%m-%d")
    log = (world.root / "wiki" / "log.md").read_text()
    assert "| archive-component | acme-cli" in log and "- Agent: reg" in log
    rows = [dict(r) for r in world.conn.execute("SELECT * FROM audit WHERE event = 'component.lifecycle'")]
    assert rows and rows[-1]["subject"] == "acme-cli" and "No longer used" in rows[-1]["detail"]


def test_an_archived_component_refuses_writes_handoffs_log_and_ingest_and_restore_reenables_them(world):
    manage(world, "reg", "archive", name="acme-api", reason="retired")
    write = {"path": "wiki/components/acme-api.md", "content": "# x\n"}
    assert world.call("ann", "wiki_write_page_tool", **write)["reason"] == "archived"
    assert world.call("ann", "wiki_handoff_tool", **HANDOFF)["reason"] == "archived"  # as source
    reverse = {**HANDOFF, "source": "acme-web", "target": "acme-api"}
    assert world.call("ann", "wiki_handoff_tool", **reverse)["reason"] == "archived"  # as target
    assert world.call("ann", "wiki_log_append_tool", action="a", message="m", component="acme-api")["reason"] == "archived"
    ingest = TestClient(world.server.asgi_app, base_url="http://127.0.0.1:8686").post(
        "/ingest", json={"component": "acme-api", "content": "# d\n"},
        headers={"Authorization": "Bearer " + world.tokens["ann"]})
    assert ingest.status_code == 403 and "archived" in ingest.json()["message"]

    assert manage(world, "reg", "restore", name="acme-api")["status"] == "restored"
    assert world.call("ann", "wiki_write_page_tool", **write)["status"] == "created"
    assert world.call("ann", "wiki_handoff_tool", **HANDOFF)["status"] == "created"


def test_archiving_twice_and_restoring_an_active_component_are_errors(world):
    assert "not archived" in manage(world, "reg", "restore")["error"]
    manage(world, "reg", "archive", reason="r")
    assert "already archived" in manage(world, "reg", "archive", reason="r")["error"]


def test_an_unregistered_component_cannot_be_managed(world):
    assert "not a registered component" in manage(world, "reg", "archive", name="nothing", reason="r")["error"]


def test_the_inventory_marks_each_components_status(world):
    manage(world, "reg", "archive", name="acme-cli", reason="r")
    world.call("reg", "wiki_register_component_tool", name="fresh", description="d", repo="https://x.test/r",
               owner="o", skip_source_docs=True)
    inventory = world.call("rita", "wiki_inventory_tool")
    status = {c["name"]: c["status"] for c in inventory["components"]}
    assert status.get("fresh") == "active"
    # acme-cli has no page in the fixture; archive one with a page too
    manage(world, "reg", "archive", name="fresh", reason="r")
    assert {c["name"]: c["status"] for c in world.call("rita", "wiki_inventory_tool")["components"]}["fresh"] == "archived"


@pytest.mark.parametrize("action", ["purge", "delete", "remove"])
def test_no_mcp_action_purges(world, action):
    assert "Unknown action" in manage(world, "reg", action)["error"]
    assert (world.root / "manifold.yaml").read_text().count("acme-cli") == 1


def test_update_changes_the_description_for_any_registrar_and_the_mapping_only_for_a_human(world):
    world.call("reg", "wiki_register_component_tool", name="fresh", description="Old.", repo="https://x.test/old",
               owner="old-team", skip_source_docs=True)
    assert manage(world, "bot", "update", name="fresh", description="A new description.")["status"] == "updated"
    for extra in ({"repo": "https://x.test/new"}, {"owner": "new-team"}):
        refused = manage(world, "bot", "update", name="fresh", **extra)
        assert refused["refused"] is True and refused["reason"] == "human_required"
    done = manage(world, "reg", "update", name="fresh", repo="https://x.test/new", owner="new-team")
    assert done["changed"] == ["repository", "owner"]
    entry = next(c for c in load_config(world.root).components if c.slug == "fresh")
    assert (entry.description, entry.repo, entry.owner) == ("A new description.", "https://x.test/new", "new-team")
    page = (world.root / "wiki" / "components" / "fresh.md").read_text()
    assert 'owner: "new-team"' in page and "**Repository:** https://x.test/new" in page
    assert 'summary: "A new description."' in page


def test_update_needs_something_to_change_and_valid_values(world):
    assert "at least one" in manage(world, "reg", "update")["error"]
    assert "under 200" in manage(world, "reg", "update", description="x" * 201)["error"]
