# SPDX-License-Identifier: Apache-2.0
"""Auto-generate and maintain agent guide pages for wiki/guides/agents/."""

import re
from datetime import date
from pathlib import Path
from typing import Optional

import frontmatter

from .git import git_commit


_KNOWN_ROLES = ["scenario-writer", "bug-coder", "test-planner", "test-coder", "reviewer", "planner", "coder"]
_ROLE_ORDER = {
    "planner": 0, "coder": 1, "bug-coder": 2, "reviewer": 3,
    "test-planner": 4, "test-coder": 5, "scenario-writer": 6,
}
# Roles the build profile of the base bundle installs.
_BUILD_ROLES = ["planner", "coder", "bug-coder", "reviewer", "test-planner", "test-coder"]

def _display_name(slug: str) -> str:
    """Return display name: capitalise only pure-alpha slugs, leave others unchanged."""
    if slug.isalpha():
        return slug.capitalize()
    return slug


def _infer_role(name: str) -> str:
    for role in _KNOWN_ROLES:
        if name.endswith(f"-{role}"):
            return role
    return "unknown"


def _extract_stack_facts(body: str) -> str:
    match = re.search(r"## Stack facts\s*\n\s*(.*?)(?=\n## |\Z)", body, re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_verify_command(body: str) -> str:
    match = re.search(r"[Vv]erify[^`\n]*run `([^`]+)`", body)
    return match.group(1).strip() if match else ""


def _extract_test_command(body: str) -> str:
    match = re.search(r"Run `([^`]+)` in full", body)
    return match.group(1).strip() if match else ""


def _extract_plan_prefix(description: str) -> str:
    match = re.search(r"([A-Z][A-Z0-9_]*_PHASE)", description)
    return match.group(1) if match else ""


def _stack_to_bullets(stack_facts: str) -> str:
    if not stack_facts:
        return "- _Stack details not extracted — see raw agent file_"
    if stack_facts.strip().startswith("-"):
        return stack_facts.strip()
    items = [s.strip() for s in re.split(r",|\n", stack_facts) if s.strip()]
    return "\n".join(f"- {item}" for item in items)


def _install_section(slug: str) -> str:
    return f"""## Installing and updating the {slug} agents

The agents are installed in the {slug} repository by the agent bundle, not copied from
this page. Call `wiki_bundle_info_tool()` for the available bundles, their versions and
the install steps. Re-running the installer updates the files it installed and keeps any
file that was edited. After an install or update, copy the agent files into
`raw/{slug}/agents/` and call `wiki_agent_catalog_tool(component="{slug}")` to refresh
this page."""


def _update_agent_guide_sidebar(wiki_root: Path, slug: str) -> bool:
    """Insert agent guide link into the Agents section of _sidebar.md if missing."""
    sidebar = wiki_root / "wiki" / "_sidebar.md"
    if not sidebar.exists():
        return False
    text = sidebar.read_text(encoding="utf-8")
    display = _display_name(slug)
    link = f"    - [{display} agents](/guides/agents/{slug}.md)"
    if link in text:
        return False
    lines = text.splitlines(keepends=True)
    insert_after = -1
    for i, line in enumerate(lines):
        if "/guides/agents/" in line and line.strip().startswith("- ["):
            insert_after = i
    if insert_after < 0:
        return False
    lines.insert(insert_after + 1, link + "\n")
    sidebar.write_text("".join(lines), encoding="utf-8")
    git_commit(wiki_root, [sidebar], f"wiki: add {slug} agents to sidebar")
    return True


def wiki_agent_guide(wiki_root: Path, component: str) -> dict:
    """
    Create or update wiki/guides/agents/{component}.md from the agent files in
    raw/{component}/agents/. Also inserts the guide link into the sidebar if absent.
    """
    slug = component.strip().lower()
    agents_dir = wiki_root / "raw" / slug / "agents"

    if not agents_dir.exists() or not list(agents_dir.glob("*.agent.md")):
        return {
            "status": "no_agents",
            "message": (
                f"No agent files found in raw/{slug}/agents/. "
                "Install the agent bundle in the component repository (wiki_bundle_info_tool), "
                "copy its agent files into that folder, then call this tool again."
            ),
        }

    # Load all agent files
    agent_files = sorted(agents_dir.glob("*.agent.md"))
    agents: list[dict] = []
    for f in agent_files:
        try:
            post = frontmatter.load(str(f))
            meta = post.metadata
            name = meta.get("name") or f.stem.replace(".agent", "")
            desc = " ".join(str(meta.get("description", "")).split())
            agents.append({
                "name": name,
                "role": _infer_role(name),
                "path": str(f.relative_to(wiki_root)),
                "body": post.content,
                "description": desc,
            })
        except Exception:
            continue

    if not agents:
        return {"status": "no_agents", "message": f"Could not parse any agents in raw/{slug}/agents/."}

    agents_sorted = sorted(agents, key=lambda a: _ROLE_ORDER.get(a["role"], 99))

    # Extract stack/command info from coder agent (fall back to first available)
    primary = next((a for a in agents if a["role"] == "coder"), agents[0])
    planner = next((a for a in agents if a["role"] == "planner"), agents[0])

    stack_facts_raw = _extract_stack_facts(primary["body"])
    verify_cmd = _extract_verify_command(primary["body"])
    test_cmd = _extract_test_command(primary["body"])
    plan_prefix = _extract_plan_prefix(planner["description"])

    display = _display_name(slug)
    today = date.today().isoformat()

    # Inventory table
    inventory_rows = "\n".join(
        f'| `{a["name"]}` | {a["role"]} | `{a["path"]}` |'
        for a in agents_sorted
    )

    # Missing roles note
    present_roles = {a["role"] for a in agents}
    missing_roles = [r for r in _BUILD_ROLES if r not in present_roles]
    agent_count_line = (
        f"The {display} component has {len(agents)} agent"
        f"{'s' if len(agents) != 1 else ''} published in `raw/{slug}/agents/`."
    )
    missing_note = (
        f"\nRoles the base bundle provides that are not published here: {', '.join(missing_roles)}.\n"
        if missing_roles else "\n"
    )

    # Stack bullets
    stack_bullets = _stack_to_bullets(stack_facts_raw)

    # Verify/test block
    verify_line = f"{verify_cmd}   # type check" if verify_cmd else "# type check — see agent file"
    test_line = f"{test_cmd}   # run tests" if test_cmd else "# test command — see agent file"

    # Plan convention
    plan_plan = f"`{plan_prefix}_<N>_PLAN.md`" if plan_prefix else "_see agent description_"
    plan_test = f"`{plan_prefix}_<N>_TEST_PLAN.md`" if plan_prefix else "_see agent description_"

    # Typical session
    session_lines = []
    if "planner" in present_roles:
        session_lines.append(
            f"1. Planner reads raw docs in `raw/{slug}/` and produces "
            f"`{plan_prefix or slug.upper()}_<N>_PLAN.md`."
        )
    if "coder" in present_roles:
        session_lines.append("2. Coder reads the plan and implements task by task.")
    if "bug-coder" in present_roles:
        session_lines.append("3. Bug coder handles defect reports found during QA.")
    typical_session = "\n".join(session_lines) if session_lines else "_See agent files for session protocol._"

    exports = _install_section(slug)

    content = f"""---
title: {display} Agent Guide
last_updated: {today}
---

# {display} Agent Guide

{agent_count_line}{missing_note}
## Agent inventory

| Agent name | Role | Source file |
|---|---|---|
{inventory_rows}

## Stack snapshot

{stack_bullets}

## Verify and test commands

```bash
{verify_line}
{test_line}
```

## Plan file convention

Phase plans are named {plan_plan} and test plans are named {plan_test}.

{exports}

## Typical session

{typical_session}

## Raw source docs

{display} raw docs live in `raw/{slug}/`. Run
`wiki_freshness_tool(component="{slug}")` to check whether the wiki page is
stale relative to raw docs.
"""

    guide_path = wiki_root / "wiki" / "guides" / "agents" / f"{slug}.md"
    existed = guide_path.exists()
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide_path.write_text(content, encoding="utf-8")
    git_commit(wiki_root, [guide_path],
               f"wiki: {'update' if existed else 'create'} {slug} agent guide")

    sidebar_updated = _update_agent_guide_sidebar(wiki_root, slug)

    return {
        "status": "updated" if existed else "created",
        "path": str(guide_path.relative_to(wiki_root)),
        "agents_found": [a["name"] for a in agents_sorted],
        "sidebar_updated": sidebar_updated,
    }
