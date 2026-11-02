# SPDX-License-Identifier: Apache-2.0
"""Registering components: who may, what a registration grants, the protected mapping, and the daily limits
for agents (PHASE_1_PLAN T16, T18)."""

import pytest

pytest.importorskip("fastmcp")

from manifold_security import audit, limits, principals, settings  # noqa: E402

REPO = "https://example.test/org/%s"


def register(world, who, name, repo=None, owner="team", **extra):
    return world.call(who, "wiki_register_component_tool", name=name, description="A component.",
                      repo=repo or REPO % name, owner=owner, skip_source_docs=True, **extra)


def read_audit(world, event):
    return [dict(r) for r in world.conn.execute("SELECT * FROM audit WHERE event = ?", (event,))]


# ── T16: gating ──────────────────────────────────────────────────────────────

def test_a_reader_and_a_contributor_cannot_register(tool_world):
    tool_world.who("rita", roles=["reader"])
    tool_world.who("ann", roles=["contributor"], grants=["fresh"])
    assert register(tool_world, "rita", "fresh")["refused"] is True
    assert register(tool_world, "ann", "fresh")["refused"] is True
    assert not (tool_world.root / "wiki" / "components" / "fresh.md").exists()


def test_an_agent_registrar_registers_but_has_no_grant_on_the_new_component(tool_world):
    tool_world.who("bot", "agent", roles=["registrar", "contributor"])
    result = register(tool_world, "bot", "fresh-one")
    assert result["status"] == "created" and result["self_granted"] is False
    page = (tool_world.root / "wiki" / "components" / "fresh-one.md").read_text()
    refused = tool_world.call("bot", "wiki_write_page_tool", path="wiki/components/fresh-one.md",
                              content=page + "\nmore\n", etag="x")
    assert refused["refused"] is True


def test_with_the_self_grant_flag_the_registration_adds_one_audited_grant(tool_world):
    bot = tool_world.who("bot", "agent", roles=["registrar", "contributor"], self_grant=True)
    result = register(tool_world, "bot", "fresh-one")
    assert result["self_granted"] is True
    assert principals.grants_of(tool_world.conn, bot.principal_id) == ["fresh-one"]
    rows = read_audit(tool_world, audit.GRANT_CHANGED)
    assert len(rows) == 1 and rows[0]["subject"] == "fresh-one" and rows[0]["actor"] == bot.principal_id
    page = (tool_world.root / "wiki" / "components" / "fresh-one.md").read_text()
    written = tool_world.call("bot", "wiki_write_page_tool", path="wiki/components/fresh-one.md",
                              content=page + "\nmore\n", etag=result["etag"])
    assert written["status"] == "updated"


def test_an_agent_cannot_change_repo_or_owner_of_a_registered_component_but_a_human_registrar_can(tool_world):
    tool_world.who("bot", "agent", roles=["registrar"])
    tool_world.who("reg", "human", roles=["registrar"])
    assert register(tool_world, "reg", "fresh-one")["status"] == "created"
    for changed in ({"repo": "https://evil.test/x"}, {"owner": "someone-else"}):
        refused = register(tool_world, "bot", "fresh-one", **changed)
        assert refused["refused"] is True and refused["reason"] == "human_required"
    same = register(tool_world, "bot", "fresh-one")
    assert same["status"] == "already_registered"  # no change of mapping: not protected, backend says it exists
    human = register(tool_world, "reg", "fresh-one", repo="https://moved.test/x")
    assert human.get("refused") is not True and human["status"] == "already_registered"


def test_reconcile_is_for_a_human_registrar_only(tool_world):
    tool_world.who("bot", "agent", roles=["registrar"])
    tool_world.who("reg", "human", roles=["registrar"])
    register(tool_world, "reg", "fresh-one")
    docs = {"readme": "# Fresh One\n\nDoes things.\n"}
    refused = tool_world.call("bot", "wiki_register_component_tool", name="fresh-one", description="d",
                              repo=REPO % "fresh-one", owner="team", reconcile=True, inline_docs=docs)
    assert refused["refused"] is True
    done = tool_world.call("reg", "wiki_register_component_tool", name="fresh-one", description="d",
                           repo=REPO % "fresh-one", owner="team", reconcile=True, inline_docs=docs)
    assert done["status"] == "reconciled", done


def test_registration_and_reconcile_write_their_own_log_entry_naming_the_principal(tool_world):
    tool_world.who("reg", "human", roles=["registrar"])
    register(tool_world, "reg", "fresh-one")
    tool_world.call("reg", "wiki_register_component_tool", name="fresh-one", description="d",
                    repo=REPO % "fresh-one", owner="team", reconcile=True, inline_docs={"readme": "# R\n"})
    log = (tool_world.root / "wiki" / "log.md").read_text()
    assert "| register | fresh-one" in log and "| reconcile-component | fresh-one" in log
    assert log.count("- Agent: reg") == 2


def test_the_guidance_no_longer_tells_the_agent_to_log_the_registration(tool_world):
    tool_world.who("rita", roles=["reader"])
    steps = tool_world.call("rita", "wiki_onboarding_tool")["steps"]
    assert not any("wiki_log_append_tool" in s for s in steps)
    assert [s.split(".")[0] for s in steps] == [str(i) for i in range(1, len(steps) + 1)]


# ── T18: limits ──────────────────────────────────────────────────────────────

def test_limit_the_sixth_registration_in_a_day_is_refused_for_an_agent_until_the_setting_is_raised(tool_world):
    tool_world.who("bot", "agent", roles=["registrar"])
    for number in range(1, 6):
        assert register(tool_world, "bot", "agent-comp-%d" % number)["status"] == "created"
    sixth = register(tool_world, "bot", "agent-comp-6")
    assert sixth["refused"] is True and sixth["reason"] == "limit"
    assert "agent_registrations_per_day" in sixth["error"] and "resets at" in sixth["error"]
    assert not (tool_world.root / "wiki" / "components" / "agent-comp-6.md").exists()
    assert any("limit registrations" in r["detail"] for r in read_audit(tool_world, audit.AUTHORIZER_REFUSAL))
    settings.set_value(tool_world.conn, "agent_registrations_per_day", 6)
    assert register(tool_world, "bot", "agent-comp-6")["status"] == "created"


def test_limit_a_registration_that_did_not_happen_does_not_use_up_the_day(tool_world):
    bot = tool_world.who("bot", "agent", roles=["registrar"])
    assert register(tool_world, "bot", "agent-comp-1")["status"] == "created"
    assert register(tool_world, "bot", "agent-comp-1")["status"] == "already_registered"  # no use counted
    bad = tool_world.call("bot", "wiki_register_component_tool", name="Bad Name", description="d",
                          repo="https://x.test/r", owner="o")
    assert bad["status"] == "error"
    assert limits.used_today(tool_world.conn, bot.principal_id, limits.REGISTRATIONS) == 1


def test_limit_a_human_registers_without_limit(tool_world):
    tool_world.who("reg", "human", roles=["registrar"])
    for number in range(1, 8):
        assert register(tool_world, "reg", "human-comp-%d" % number)["status"] == "created"


def test_limit_the_second_archive_in_a_day_is_refused_for_an_agent_and_not_for_a_human(tool_world):
    tool_world.who("bot", "agent", roles=["registrar"])
    tool_world.who("reg", "human", roles=["registrar"])
    archive = lambda who, name: tool_world.call(who, "wiki_component_manage_tool", action="archive", name=name,
                                                reason="retired")
    assert archive("bot", "acme-cli")["status"] == "archived"
    second = archive("bot", "acme-qa")
    assert second["refused"] is True and second["reason"] == "limit" and "agent_archives_per_day" in second["error"]
    assert principals.get_component_state(tool_world.conn, "acme-qa").archived is False
    settings.set_value(tool_world.conn, "agent_archives_per_day", 2)
    assert archive("bot", "acme-qa")["status"] == "archived"
    assert [archive("reg", n)["status"] for n in ("acme-data", "acme-io", "acme.io")] == ["archived"] * 3


def test_limit_counts_are_per_principal_and_per_day(tool_world):
    import datetime
    first = tool_world.who("bot1", "agent", roles=["registrar"])
    second = tool_world.who("bot2", "agent", roles=["registrar"])
    day = datetime.datetime(2026, 1, 1, 12, tzinfo=datetime.timezone.utc)
    for _ in range(5):
        limits.consume(tool_world.conn, first.principal_id, "agent", limits.REGISTRATIONS, now=day)
    with pytest.raises(limits.LimitReached, match="2026-01-02 00:00 UTC"):
        limits.consume(tool_world.conn, first.principal_id, "agent", limits.REGISTRATIONS, now=day)
    limits.consume(tool_world.conn, second.principal_id, "agent", limits.REGISTRATIONS, now=day)
    next_day = day + datetime.timedelta(days=1)
    limits.consume(tool_world.conn, first.principal_id, "agent", limits.REGISTRATIONS, now=next_day)
