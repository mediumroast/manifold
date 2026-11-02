# SPDX-License-Identifier: Apache-2.0
"""Who may write pages, append to the log, publish an agent guide and ingest documents (PHASE_1_PLAN T13)."""

import pytest
from starlette.testclient import TestClient

pytest.importorskip("fastmcp")

PAGE = """\
---
title: "Acme Api"
component: "acme-api"
status: active
last_updated: 2026-07-07
owner: "team-a"
summary: "Backend."
---

# Acme Api

## Overview

Text.

**Repository:** https://github.com/acme/acme-api
"""


def write(world, who, path, content, etag=None):
    arguments = {"path": path, "content": content, "message": "test"}
    if etag is not None:
        arguments["etag"] = etag
    return world.call(who, "wiki_write_page_tool", **arguments)


def test_a_contributor_writes_its_own_component_page_and_not_anothers(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    ok = write(tool_world, "ann", "wiki/components/acme-api.md", PAGE)
    assert ok["status"] == "created", ok
    other = write(tool_world, "ann", "wiki/components/acme-web.md", PAGE.replace("acme-api", "acme-web"))
    assert other["refused"] is True and "acme-web" in other["error"]
    assert not (tool_world.root / "wiki" / "components" / "acme-web.md").exists()


def test_only_a_shared_grant_writes_a_decision_page(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    tool_world.who("sam", roles=["contributor"], grants=["_shared"])
    path = "wiki/decisions/2026-01-01-use-rest.md"
    assert write(tool_world, "ann", path, "# Decision\n")["refused"] is True
    assert write(tool_world, "sam", path, "# Decision\n")["status"] == "created"


def test_a_deny_beats_a_grant_on_a_write(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"], denies=["acme-api"])
    assert write(tool_world, "ann", "wiki/components/acme-api.md", PAGE)["refused"] is True


@pytest.mark.parametrize("field,old,new", [
    ("owner", 'owner: "team-a"', 'owner: "someone-else"'),
    ("component", 'component: "acme-api"', 'component: "acme-web"'),
    ("Repository line", "**Repository:** https://github.com/acme/acme-api", "**Repository:** https://evil.test/x"),
])
def test_a_contributor_cannot_change_the_owner_component_or_repository_of_a_component_page(tool_world, field, old, new):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    created = write(tool_world, "ann", "wiki/components/acme-api.md", PAGE)
    changed = write(tool_world, "ann", "wiki/components/acme-api.md", PAGE.replace(old, new), etag=created["etag"])
    assert changed["status"] == "error" and field in changed["error"]
    assert (tool_world.root / "wiki/components/acme-api.md").read_text() == PAGE


def test_other_edits_to_a_component_page_are_allowed(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    created = write(tool_world, "ann", "wiki/components/acme-api.md", PAGE)
    edited = write(tool_world, "ann", "wiki/components/acme-api.md", PAGE.replace("Text.", "More text."),
                   etag=created["etag"])
    assert edited["status"] == "updated"


@pytest.mark.parametrize("path", ["wiki/log.md", "wiki/_sidebar.md", "manifold.yaml",
                                  "wiki/handoffs/acme-api-to-acme-web/x.md", "../outside.md"])
def test_the_write_tool_never_writes_protected_paths_even_with_every_grant(tool_world, path):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api", "_shared"])
    before = tool_world.git_log()
    result = write(tool_world, "ann", path, "x\n")
    assert result.get("status") == "error", result
    assert tool_world.git_log() == before


def test_the_log_append_needs_a_write_grant_on_the_component_or_shared(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    args = {"action": "lint", "message": "checked"}
    assert tool_world.call("ann", "wiki_log_append_tool", component="acme-api", **args)["status"] == "appended"
    assert tool_world.call("ann", "wiki_log_append_tool", component="acme-web", **args)["refused"] is True
    assert tool_world.call("ann", "wiki_log_append_tool", **args)["refused"] is True  # no component: _shared


def test_the_agent_catalog_needs_a_write_grant_on_the_component(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    assert tool_world.call("ann", "wiki_agent_catalog_tool", component="acme-web")["refused"] is True
    assert tool_world.call("ann", "wiki_agent_catalog_tool", component="acme-api").get("refused") is not True


# ── POST /ingest ─────────────────────────────────────────────────────────────

def ingest(world, who, component, content="# doc\n"):
    client = TestClient(world.server.asgi_app, base_url="http://127.0.0.1:8686")
    return client.post("/ingest", json={"component": component, "content": content},
                       headers={"Authorization": "Bearer " + world.tokens[who]})


def test_ingest_needs_a_grant_on_a_registered_component(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    assert ingest(tool_world, "ann", "acme-api").status_code == 200
    refused = ingest(tool_world, "ann", "acme-web")
    assert refused.status_code == 403 and refused.json()["status"] == "error"


def test_ingest_to_shared_needs_the_shared_grant(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    tool_world.who("sam", roles=["contributor"], grants=["_shared"])
    assert ingest(tool_world, "ann", "shared").status_code == 403
    assert ingest(tool_world, "sam", "shared").status_code == 200


def test_only_a_registrar_ingests_to_an_unregistered_slug(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["brand-new"])
    tool_world.who("reg", roles=["registrar"])
    assert ingest(tool_world, "ann", "brand-new").status_code == 403
    assert not (tool_world.root / "raw" / "brand-new").exists()
    accepted = ingest(tool_world, "reg", "brand-new")
    assert accepted.status_code == 200 and (tool_world.root / accepted.json()["path"]).is_file()


def test_a_reader_and_an_admin_cannot_ingest(tool_world):
    tool_world.who("rita", roles=["reader"])
    tool_world.who("root", roles=["admin"])
    assert ingest(tool_world, "rita", "acme-api").status_code == 403
    assert ingest(tool_world, "root", "acme-api").status_code == 403


def test_a_revoked_credential_cannot_ingest(tool_world):
    from manifold_security import tokens
    caller = tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    tokens.revoke_credential(tool_world.conn, caller.credential_id)
    assert ingest(tool_world, "ann", "acme-api").status_code == 401
