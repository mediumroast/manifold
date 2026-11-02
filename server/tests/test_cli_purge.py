# SPDX-License-Identifier: Apache-2.0
"""admin registry purge (PHASE_1_PLAN T26)."""

import getpass
import subprocess

import pytest
from starlette.testclient import TestClient

pytest.importorskip("fastmcp")

from manifold_security import principals, settings  # noqa: E402
from tests.conftest import CliRunner  # noqa: E402
from wiki_backend.config import load_config  # noqa: E402


def git(world, *args):
    return subprocess.run(["git", *args], cwd=world.root, capture_output=True, text=True, check=True).stdout


@pytest.fixture()
def world(tool_world):
    root = tool_world.root
    (root / "wiki" / "_sidebar.md").write_text("- **Components**\n  - [acme-api](/components/acme-api.md)\n")
    (root / "wiki" / "index.md").write_text("| Component | Status | Wiki page | Summary |\n|---|---|---|---|\n")
    git(tool_world, "add", "-A")
    git(tool_world, "commit", "-q", "-m", "sidebar and index")
    tool_world.who("reg", roles=["registrar"])
    tool_world.who("ann", roles=["contributor"], grants=["doomed", "acme-api"])
    settings.set_value(tool_world.conn, "purge_hold_days", 0)
    return tool_world


def make_archived(world, slug="doomed", archive=True):
    result = world.call("reg", "wiki_register_component_tool", name=slug, description="Goes away.",
                        repo="https://example.test/" + slug, owner="team", skip_source_docs=True)
    assert result["status"] == "created", result
    client = TestClient(world.server.asgi_app, base_url="http://127.0.0.1:8686")
    assert client.post("/ingest", json={"component": slug, "content": "# raw\n"},
                       headers={"Authorization": "Bearer " + world.tokens["ann"]}).status_code == 200
    guide = world.call("ann", "wiki_write_page_tool", path="wiki/guides/agents/%s.md" % slug, content="# guide\n")
    assert guide["status"] == "created", guide
    if archive:
        assert world.call("reg", "wiki_component_manage_tool", action="archive", name=slug,
                          reason="retired")["status"] == "archived"


def purge(world, *args):
    return CliRunner(world.data_dir, world.root)("registry", "purge", *args)


def clean(world):
    return git(world, "status", "--porcelain") == ""


def exists(world, relative):
    return (world.root / relative).exists()


def test_a_valid_purge_removes_everything_leaves_git_clean_and_makes_one_commit(world):
    make_archived(world)
    before = git(world, "rev-list", "--count", "HEAD").strip()
    assert clean(world)
    code, out, err = purge(world, "doomed", "--confirm-slug", "doomed")
    assert code == 0, err
    assert not exists(world, "wiki/components/doomed.md") and not exists(world, "raw/doomed")
    assert not exists(world, "wiki/guides/agents/doomed.md")
    assert "doomed" not in load_config(world.root).slugs()
    assert "doomed" not in (world.root / "wiki" / "_sidebar.md").read_text()
    assert "doomed" not in (world.root / "wiki" / "index.md").read_text()
    assert "`doomed`" not in (world.root / "wiki" / "CLAUDE.md").read_text()
    assert "acme-api" in load_config(world.root).slugs()  # the others are untouched
    assert clean(world)
    assert int(git(world, "rev-list", "--count", "HEAD").strip()) == int(before) + 1
    head = git(world, "log", "-1", "--format=%an|%B")
    assert head.startswith("host:%s|wiki: purge archived component doomed" % getpass.getuser())
    assert "Manifold-Principal: host-%s (host)" % getpass.getuser() in head
    # the history keeps everything
    assert "Goes away." in git(world, "show", "HEAD~1:wiki/components/doomed.md")


def test_a_purge_removes_the_components_grants_denies_and_state_but_not_the_others(world):
    make_archived(world)
    principals.add_deny(world.conn, "ann", "doomed")
    assert purge(world, "doomed", "--confirm-slug", "doomed")[0] == 0
    ann = principals.get_principal(world.conn, "ann")
    assert principals.grants_of(world.conn, ann.id) == ["acme-api"] and principals.denies_of(world.conn, ann.id) == []
    assert principals.get_component_state(world.conn, "doomed").state == "active"  # the row is gone
    events = [r["detail"] for r in world.conn.execute("SELECT detail FROM audit WHERE event = 'component.lifecycle'")]
    assert any(d.startswith("purged:") for d in events)


def test_purge_is_refused_for_a_component_that_is_not_archived_and_changes_nothing(world):
    make_archived(world, archive=False)
    code, _, err = purge(world, "doomed", "--confirm-slug", "doomed")
    assert code == 1 and "not archived" in err
    assert exists(world, "wiki/components/doomed.md") and clean(world)


def test_purge_is_refused_before_the_hold_period_has_passed(world):
    settings.set_value(world.conn, "purge_hold_days", 14)
    make_archived(world)
    code, _, err = purge(world, "doomed", "--confirm-slug", "doomed")
    assert code == 1 and "held until" in err
    assert exists(world, "raw/doomed") and clean(world)


def test_purge_is_refused_with_an_open_handoff_even_if_the_database_says_archived(world):
    make_archived(world, archive=False)
    created = world.call("ann", "wiki_handoff_tool", action="create", source="doomed", target="acme-api",
                         type="feature", priority="low", title="Open one", summary="s", what_needs_to_happen="w")
    assert created["status"] == "created"
    principals.archive_component(world.conn, "doomed", "forced", 0)  # not through the tool, which would refuse
    code, _, err = purge(world, "doomed", "--confirm-slug", "doomed")
    assert code == 1 and created["path"] in err
    assert exists(world, "wiki/components/doomed.md")


@pytest.mark.parametrize("confirm", [[], ["--confirm-slug", "doomed2"], ["--confirm-slug", "DOOMED"], ["--confirm-slug", ""]])
def test_purge_needs_the_slug_typed_exactly_and_shows_what_it_would_remove(world, confirm):
    make_archived(world)
    code, out, err = purge(world, "doomed", *confirm)
    assert code == 1 and "type the slug again" in err and "Nothing was changed" in err
    assert "raw/doomed" in out and "wiki/components/doomed.md" in out
    assert exists(world, "wiki/components/doomed.md") and clean(world)


def test_completed_handoff_pages_are_kept_as_history(world):
    make_archived(world, archive=False)
    created = world.call("ann", "wiki_handoff_tool", action="create", source="doomed", target="acme-api",
                         type="feature", priority="low", title="Done one", summary="s", what_needs_to_happen="w")
    world.call("ann", "wiki_handoff_tool", action="close", path=created["path"], resolution="done")
    assert world.call("reg", "wiki_component_manage_tool", action="archive", name="doomed",
                      reason="retired")["status"] == "archived"
    assert purge(world, "doomed", "--confirm-slug", "doomed")[0] == 0
    assert exists(world, created["path"]) and clean(world)


def test_an_unknown_or_invalid_slug_and_a_wrong_folder_are_refused(world, tmp_path):
    assert purge(world, "Not A Slug", "--confirm-slug", "x")[0] == 1
    assert "not archived" in purge(world, "nothing", "--confirm-slug", "nothing")[2]
    code, _, err = CliRunner(world.data_dir, tmp_path / "wiki-root")("registry", "purge", "x", "--confirm-slug", "x")
    assert code == 1 and "no manifold.yaml" in err


def test_the_file_removal_is_one_replaceable_function(world):
    from manifold_cli import purge as purge_module
    make_archived(world)
    assert purge_module.removable_paths(world.root, "doomed") == [
        "wiki/components/doomed.md", "wiki/guides/agents/doomed.md", "raw/doomed"]
    assert sorted(purge_module.remove_component_files(world.root, "doomed")) == sorted(
        ["wiki/components/doomed.md", "wiki/guides/agents/doomed.md", "raw/doomed"])
    assert purge_module.removable_paths(world.root, "doomed") == []


def test_purge_is_not_offered_over_mcp(world):
    import asyncio
    names = {t.name for t in asyncio.run(world.server.app.list_tools())}
    assert not any("purge" in n for n in names)
