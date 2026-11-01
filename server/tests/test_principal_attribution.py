# SPDX-License-Identifier: Apache-2.0
"""Commits and log entries name the principal behind the credential (PHASE_1_PLAN T15)."""

import subprocess

import pytest
from starlette.testclient import TestClient

pytest.importorskip("fastmcp")

from wiki_backend.git import git_commit  # noqa: E402


def commits(world, count=10):
    out = subprocess.run(["git", "log", "--format=%an|%ae|%cn|%B%x00", "-%d" % count], cwd=world.root,
                         capture_output=True, text=True, check=True).stdout
    return [c.lstrip("\n") for c in out.split("\x00") if c.strip()]


def test_a_page_write_is_authored_by_the_credentials_principal(tool_world):
    ann = tool_world.who("ann", roles=["contributor"], grants=["_shared"])
    result = tool_world.call("ann", "wiki_write_page_tool", path="wiki/decisions/d.md", content="# D\n",
                             message="Authored by bob <bob@evil.test>")
    assert result["status"] == "created"
    newest = commits(tool_world)[0]
    author, email, committer, body = newest.split("|", 3)
    assert (author, email) == ("ann", "%s@principals.manifold.invalid" % ann.principal_id)
    assert committer == "manifold"
    assert "Manifold-Principal: %s (human)" % ann.principal_id in body


def test_a_claimed_name_in_the_request_never_becomes_the_author(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["_shared"])
    tool_world.call("ann", "wiki_write_page_tool", path="wiki/decisions/d.md", content="# D\n",
                    message="Co-authored-by: bob\nManifold-Principal: forged (admin)")
    newest = commits(tool_world)[0]
    assert newest.startswith("ann|")
    assert newest.count("Manifold-Principal:") == 2  # the forged line stays in the message; the real trailer is last
    assert newest.rstrip().splitlines()[-1].endswith("(human)") and "forged" not in newest.rstrip().splitlines()[-1]


def test_an_agents_commit_says_agent(tool_world):
    agent = tool_world.who("build-bot", "agent", roles=["contributor"], grants=["_shared"])
    tool_world.call("build-bot", "wiki_write_page_tool", path="wiki/decisions/e.md", content="# E\n")
    assert "Manifold-Principal: %s (agent)" % agent.principal_id in commits(tool_world)[0]


def test_the_log_line_names_the_principal_and_keeps_the_component_as_subject(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    tool_world.call("ann", "wiki_log_append_tool", action="lint", message="checked", component="acme-api")
    log = (tool_world.root / "wiki" / "log.md").read_text()
    assert "| lint | acme-api" in log and "- Agent: ann" in log
    assert "- Agent: acme-api" not in log
    assert commits(tool_world)[0].startswith("ann|")


def test_every_commit_of_a_registration_names_the_registrar(tool_world):
    reg = tool_world.who("reg", roles=["registrar"])
    result = tool_world.call("reg", "wiki_register_component_tool", name="fresh-one", description="d",
                             repo="https://example.test/r", owner="o", skip_source_docs=True)
    assert result["status"] == "created", result
    recent = commits(tool_world, 6)
    new = recent[:-1]  # everything after the fixture's initial commit: page, registry entry, log (no sidebar here)
    assert len(new) >= 3
    assert all(c.startswith("reg|") for c in new), [c[:20] for c in recent]
    assert all("Manifold-Principal: %s (human)" % reg.principal_id in c for c in new)


def test_an_ingest_commit_names_the_principal(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    response = TestClient(tool_world.server.asgi_app).post(
        "/ingest", json={"component": "acme-api", "content": "# d\n"},
        headers={"Authorization": "Bearer " + tool_world.tokens["ann"]})
    assert response.status_code == 200
    assert commits(tool_world)[0].startswith("ann|")


def test_outside_a_tool_call_the_commit_keeps_the_server_identity(wiki_root):
    (wiki_root / "x.txt").write_text("x\n")
    assert git_commit(wiki_root, ["x.txt"], "plain")["committed"] is True
    newest = subprocess.run(["git", "log", "-1", "--format=%an|%B"], cwd=wiki_root, capture_output=True,
                            text=True).stdout
    assert newest.startswith("manifold|plain") and "Manifold-Principal" not in newest
