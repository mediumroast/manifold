# SPDX-License-Identifier: Apache-2.0
"""Tests for wiki_onboarding_tool and wiki_agent_guide."""

from pathlib import Path
import pytest
from wiki_backend.onboarding import wiki_onboarding_protocol, wiki_onboarding_preflight, wiki_reconcile_plan
from wiki_backend.agent_guide import wiki_agent_guide


def test_returns_dict():
    result = wiki_onboarding_protocol()
    assert isinstance(result, dict)


def test_has_required_top_level_keys():
    result = wiki_onboarding_protocol()
    for key in ("tools", "initial_registration_steps", "raw_doc_taxonomy",
                "handoff_lifecycle", "ongoing_maintenance"):
        assert key in result, f"missing key: {key}"


def test_tools_list_covers_all_mcp_tools():
    result = wiki_onboarding_protocol()
    tool_names = {t["name"] for t in result["tools"]}
    expected = {
        "wiki_ping_tool",
        "wiki_handoff_tool",
        "wiki_onboarding_tool",
        "wiki_reconcile_plan_tool",
        "wiki_register_component_tool",
        "wiki_read_tool",
        "wiki_write_page_tool",
        "wiki_log_append_tool",
        "wiki_inventory_tool",
        "wiki_freshness_tool",
    }
    assert expected == tool_names


def test_registration_steps_are_ordered():
    result = wiki_onboarding_protocol()
    steps = result["initial_registration_steps"]
    orders = [s["order"] for s in steps]
    assert orders == sorted(orders)
    assert orders[0] == 1


def test_raw_doc_taxonomy_has_rule():
    result = wiki_onboarding_protocol()
    taxonomy = result["raw_doc_taxonomy"]
    assert "rule" in taxonomy
    assert "component_local" in taxonomy
    assert "shared" in taxonomy


def test_handoff_lifecycle_has_post_and_pickup():
    result = wiki_onboarding_protocol()
    lifecycle = result["handoff_lifecycle"]
    assert "post" in lifecycle
    assert "pickup" in lifecycle
    assert isinstance(lifecycle["post"], list)
    assert isinstance(lifecycle["pickup"], list)


def test_no_filesystem_io():
    """Protocol is static — calling it twice returns identical results."""
    r1 = wiki_onboarding_protocol()
    r2 = wiki_onboarding_protocol()
    assert r1 == r2


# ── wiki_onboarding_preflight tests ───────────────────────────────────────────

def _registered_with_docs(wiki_root: Path, slug: str = "acme-api") -> Path:
    components_dir = wiki_root / "wiki" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    (components_dir / f"{slug}.md").write_text(
        f'---\ntitle: {slug}\ncomponent: {slug}\nlast_updated: 2026-01-01\n'
        f'owner: "team"\nsummary: "FastAPI backend"\n---\n\n## Overview\nStub.\n'
    )
    raw_dir = wiki_root / "raw" / slug
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"2026-05-08-{slug}-readme.md").write_text("# Component\nReal content.\n")
    return raw_dir


def test_preflight_registered_with_docs_recommends_reconcile(wiki_root: Path):
    """Registered, docs present, no agents published: reconcile (D) is recommended and the bundle is mentioned."""
    _registered_with_docs(wiki_root)

    result = wiki_onboarding_preflight(wiki_root, "acme-api")

    assert result["status"] == "reconcile_available"
    assert result["terminal"] is False
    assert len(result["docs_found"]) == 1
    assert result["agents_found"] == []
    assert "agents_missing_roles" not in result and "partial_onboarding" not in result
    options = result.get("options", [])
    assert [o["option"] for o in options] == ["D", "E"]
    assert next(o for o in options if o.get("recommended"))["option"] == "D"
    assert "wiki_bundle_info_tool" in result["message_to_user"]
    assert "No agents are published" in result["message_to_user"]


def test_preflight_lists_published_agents(wiki_root: Path):
    raw_dir = _registered_with_docs(wiki_root)
    agents_dir = raw_dir / "agents"
    agents_dir.mkdir()
    for role in ("planner", "coder"):
        (agents_dir / f"acme-api-{role}.agent.md").write_text(f"# {role}\n")

    result = wiki_onboarding_preflight(wiki_root, "acme-api")

    assert result["agents_found"] == ["raw/acme-api/agents/acme-api-coder.agent.md", "raw/acme-api/agents/acme-api-planner.agent.md"]
    assert "Agents published in the wiki: 2" in result["message_to_user"]


def test_preflight_already_registered_no_docs_returns_terminal(wiki_root: Path):
    """When the component page exists but raw/ is empty, return the terminal hard stop."""
    slug = "acme-web"

    # Create the component page
    components_dir = wiki_root / "wiki" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    (components_dir / f"{slug}.md").write_text(
        f"---\ntitle: Acme Web\ncomponent: {slug}\nlast_updated: 2026-01-01\n---\n\n## Overview\nStub.\n"
    )

    # raw/{slug}/ exists but has no markdown files
    raw_dir = wiki_root / "raw" / slug
    raw_dir.mkdir(parents=True, exist_ok=True)

    result = wiki_onboarding_preflight(wiki_root, slug)

    assert result["status"] == "already_registered"
    assert result["terminal"] is True
    assert result.get("do_not_call_again") is True
    assert result["docs_found"] == []


# ── wiki_reconcile_plan tests ─────────────────────────────────────────────────

def test_reconcile_plan_asks_only_for_the_repository(wiki_root: Path):
    _registered_with_docs(wiki_root)

    result = wiki_reconcile_plan(wiki_root, "acme-api")

    assert result["status"] == "inputs_required"
    assert {r["name"] for r in result["required_inputs"]} == {"repo"}
    assert result["discovered"] == {"description": "FastAPI backend", "owner": "team"}
    assert len(result["action_plan"]) >= 3  # at minimum: reconcile + log + freshness


def test_reconcile_plan_without_agents_ends_with_the_bundle_steps(wiki_root: Path):
    _registered_with_docs(wiki_root)

    result = wiki_reconcile_plan(wiki_root, "acme-api", repo="https://github.com/acme/acme-api")

    assert result["status"] == "plan_ready"
    assert result.get("required_inputs", []) == []
    calls = [s["tool_call"] for s in result["action_plan"]]
    assert any("wiki_register_component_tool" in c for c in calls)
    assert not any("wiki_log_append_tool" in c for c in calls)  # the server logs the reconcile itself
    assert calls[-3:] == [
        "wiki_bundle_info_tool()",
        "wiki_export_component_helpers_tool()",
        "wiki_agent_catalog_tool(component='acme-api')",
    ]
    assert all(s["ready"] for s in result["action_plan"])
    assert not any("scaffold" in c or "plan_templates" in c for c in calls)


def test_reconcile_plan_with_published_agents_has_no_bundle_steps(wiki_root: Path):
    raw_dir = _registered_with_docs(wiki_root)
    (raw_dir / "agents").mkdir()
    (raw_dir / "agents" / "acme-api-planner.agent.md").write_text("# planner\n")

    result = wiki_reconcile_plan(wiki_root, "acme-api", repo="https://github.com/acme/acme-api")

    assert result["status"] == "plan_ready"
    assert [s["action"] for s in result["action_plan"]] == ["reconcile_wiki_page", "freshness_check"]
    assert result["status_audit"]["agents_published"] == ["raw/acme-api/agents/acme-api-planner.agent.md"]


def test_reconcile_plan_for_an_unregistered_component_points_at_onboarding(wiki_root: Path):
    result = wiki_reconcile_plan(wiki_root, "nobody")
    assert result["status"] == "not_registered"
    assert "wiki_onboarding_tool(component='nobody')" in result["message"]


# ── wiki_agent_guide tests ────────────────────────────────────────────────────

_PLANNER_BODY = """\
---
name: myapp-planner
component: myapp
role: planner
description: "Drive MYAPP_PHASE plans for the myapp component"
---

## Stack facts
Python 3.11+, FastAPI, pytest

Verify by running `mypy app/` before every commit.
Run `pytest tests/ -x` in full after each change.
"""

_CODER_BODY = """\
---
name: myapp-coder
component: myapp
role: coder
description: "Implement tasks from MYAPP_PHASE plans"
---

## Stack facts
Python 3.11+, FastAPI, pytest

Verify by running `mypy app/` before every commit.
Run `pytest tests/ -x` in full after each change.
"""

_BUG_CODER_BODY = """\
---
name: myapp-bug-coder
component: myapp
role: bug-coder
description: "Fix defects found during QA"
---

## Stack facts
Python 3.11+, FastAPI, pytest
"""


def _make_agents(wiki_root: Path, slug: str = "myapp") -> Path:
    agents_dir = wiki_root / "raw" / slug / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    (agents_dir / f"{slug}-planner.agent.md").write_text(_PLANNER_BODY)
    (agents_dir / f"{slug}-coder.agent.md").write_text(_CODER_BODY)
    (agents_dir / f"{slug}-bug-coder.agent.md").write_text(_BUG_CODER_BODY)
    return agents_dir


def _make_sidebar(wiki_root: Path) -> Path:
    """Create a minimal _sidebar.md with an Agents section."""
    sidebar = wiki_root / "wiki" / "_sidebar.md"
    sidebar.parent.mkdir(parents=True, exist_ok=True)
    sidebar.write_text(
        "- [Home](/)\n"
        "- **Agents**\n"
        "    - [Agent overview](/guides/agents/overview.md)\n"
        "    - [Acme API agents](/guides/agents/acme-api.md)\n"
    )
    return sidebar


def test_agent_guide_creates_guide_file(wiki_root: Path):
    """wiki_agent_guide creates wiki/guides/agents/{slug}.md when agents exist."""
    _make_agents(wiki_root)
    result = wiki_agent_guide(wiki_root, "myapp")

    assert result["status"] == "created"
    assert result["agents_found"] == ["myapp-planner", "myapp-coder", "myapp-bug-coder"]

    guide = wiki_root / "wiki" / "guides" / "agents" / "myapp.md"
    assert guide.exists()
    content = guide.read_text()
    assert "# Myapp Agent Guide" in content
    assert "myapp-planner" in content
    assert "myapp-coder" in content
    assert "Python 3.11+" in content
    assert "MYAPP_PHASE" in content


def test_agent_guide_extracts_commands(wiki_root: Path):
    """wiki_agent_guide extracts verify and test commands from agent body."""
    _make_agents(wiki_root)
    result = wiki_agent_guide(wiki_root, "myapp")
    guide = (wiki_root / "wiki" / "guides" / "agents" / "myapp.md").read_text()

    assert "mypy app/" in guide
    assert "pytest tests/ -x" in guide


def test_agent_guide_updates_sidebar(wiki_root: Path):
    """wiki_agent_guide inserts the guide link in _sidebar.md when not present."""
    _make_agents(wiki_root)
    sidebar = _make_sidebar(wiki_root)

    result = wiki_agent_guide(wiki_root, "myapp")

    assert result["sidebar_updated"] is True
    sidebar_text = sidebar.read_text()
    assert "/guides/agents/myapp.md" in sidebar_text


def test_agent_guide_skips_sidebar_when_link_present(wiki_root: Path):
    """wiki_agent_guide returns sidebar_updated=False when link is already in sidebar."""
    _make_agents(wiki_root)
    sidebar = _make_sidebar(wiki_root)
    # Pre-insert the link
    sidebar.write_text(
        sidebar.read_text()
        + "    - [Myapp agents](/guides/agents/myapp.md)\n"
    )

    result = wiki_agent_guide(wiki_root, "myapp")

    assert result["sidebar_updated"] is False


def test_agent_guide_no_agents_returns_no_agents(wiki_root: Path):
    """wiki_agent_guide returns status 'no_agents' when raw/{slug}/agents/ is absent."""
    result = wiki_agent_guide(wiki_root, "ghost")

    assert result["status"] == "no_agents"
    assert "ghost" in result["message"]


def test_agent_guide_update_status_on_existing_guide(wiki_root: Path):
    """wiki_agent_guide returns status 'updated' when guide already exists."""
    _make_agents(wiki_root)
    guides_dir = wiki_root / "wiki" / "guides" / "agents"
    guides_dir.mkdir(parents=True, exist_ok=True)
    (guides_dir / "myapp.md").write_text("# Old guide\n")

    result = wiki_agent_guide(wiki_root, "myapp")

    assert result["status"] == "updated"
