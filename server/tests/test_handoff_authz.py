# SPDX-License-Identifier: Apache-2.0
"""Who may do what on a handoff: the source creates, confirms, rejects and closes; the target claims and
requests review (PHASE_1_PLAN T14)."""

import pytest

pytest.importorskip("fastmcp")

CREATE = {"action": "create", "source": "acme-api", "target": "acme-web", "type": "feature", "priority": "low",
          "title": "Order status", "summary": "s", "what_needs_to_happen": "w"}


@pytest.fixture()
def world(tool_world):
    tool_world.who("src", roles=["contributor"], grants=["acme-api"])
    tool_world.who("tgt", roles=["contributor"], grants=["acme-web"])
    tool_world.who("other", roles=["contributor"], grants=["acme-cli"])
    tool_world.who("rita", roles=["reader"])
    return tool_world


def handoff(world, who, **arguments):
    return world.call(who, "wiki_handoff_tool", **arguments)


def page(world, path):
    return (world.root / path).read_text()


@pytest.fixture()
def created(world):
    result = handoff(world, "src", **CREATE)
    assert result["status"] == "created", result
    return result["path"]


@pytest.mark.parametrize("who", ["tgt", "other", "rita"])
def test_only_a_source_grant_creates_a_handoff(world, who):
    before = world.git_log()
    result = handoff(world, who, **CREATE)
    assert result["refused"] is True and "acme-api" in result["error"]
    assert world.git_log() == before


def test_the_target_claims_and_others_cannot(world, created):
    for who in ("src", "other", "rita"):
        assert handoff(world, who, action="claim", path=created)["refused"] is True
    assert "status: open" in page(world, created)
    assert handoff(world, "tgt", action="claim", path=created)["status"] == "claimed"


def test_the_full_cycle_with_the_source_confirming(world, created):
    handoff(world, "tgt", action="claim", path=created)
    assert handoff(world, "src", action="request-review", path=created, notes="done")["refused"] is True
    assert handoff(world, "tgt", action="request-review", path=created, notes="done")["status"] == "needs-review"
    assert handoff(world, "tgt", action="confirm", path=created)["refused"] is True
    assert handoff(world, "other", action="confirm", path=created)["refused"] is True
    assert handoff(world, "src", action="confirm", path=created)["status"] == "confirmed"
    assert "status: completed" in page(world, created)


def test_the_target_cannot_close_and_nothing_is_written(world, created):
    handoff(world, "tgt", action="claim", path=created)
    before, log = page(world, created), world.git_log()
    result = handoff(world, "tgt", action="close", path=created, resolution="all done")
    assert result["refused"] is True and "acme-api" in result["error"]
    assert page(world, created) == before and world.git_log() == log


def test_the_source_closes(world, created):
    handoff(world, "tgt", action="claim", path=created)
    assert handoff(world, "other", action="close", path=created, resolution="x")["refused"] is True
    assert handoff(world, "src", action="close", path=created, resolution="Verified.")["status"] == "completed"


@pytest.mark.parametrize("who", ["tgt", "other", "rita"])
def test_only_the_source_rejects(world, created, who):
    handoff(world, "tgt", action="claim", path=created)
    handoff(world, "tgt", action="request-review", path=created, notes="done")
    before = page(world, created)
    assert handoff(world, who, action="reject", path=created, notes="no")["refused"] is True
    assert page(world, created) == before
    assert handoff(world, "src", action="reject", path=created, notes="redo")["status"] == "rejected"


def test_listing_needs_only_read(world, created):
    assert "handoffs" in handoff(world, "rita", action="list") or "count" in handoff(world, "rita", action="list")
    world.who("root", roles=["admin"])
    assert handoff(world, "root", action="list")["refused"] is True


def test_a_page_that_is_not_a_handoff_is_not_a_target_of_the_actions(world):
    result = handoff(world, "src", action="close", path="wiki/CLAUDE.md", resolution="x")
    assert result.get("refused") is not True and "not a handoff page" in result["error"]


def test_the_tool_text_gives_the_source_the_close(world):
    import asyncio
    tool = next(t for t in asyncio.run(world.server.app.list_tools()) if t.name == "wiki_handoff_tool")
    assert "target closes" not in tool.description.lower()
    assert "Only the SOURCE" in tool.description
