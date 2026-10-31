# SPDX-License-Identifier: Apache-2.0
"""The example instance works: it loads, passes the health checks, and its links resolve."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from wiki_backend.config import load_config, sync_schema_slugs
from wiki_backend.freshness import wiki_freshness
from wiki_backend.handoff import handoff_claim, handoff_create, handoff_list
from wiki_backend.health import wiki_health
from wiki_backend.inventory import wiki_inventory

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "acme"

pytestmark = pytest.mark.skipif(not EXAMPLE.is_dir(), reason="no examples/acme beside the server")


@pytest.fixture()
def acme(tmp_path):
    """A private copy of the example, as its README tells a user to make."""
    root = tmp_path / "acme-wiki"
    shutil.copytree(EXAMPLE, root)
    for args in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t.test"],
                 ["add", "-A"], ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    return root


def test_the_registry_lists_three_components():
    config = load_config(EXAMPLE)
    assert config.slugs() == ["acme-api", "acme-web", "acme-cli"]
    assert all(c.owner and c.repo and c.description for c in config.components)


def test_the_schema_slug_list_matches_the_registry():
    assert sync_schema_slugs(EXAMPLE) is None  # nothing to change: already generated from manifold.yaml


def test_a_copy_is_healthy(acme):
    healthy, payload = wiki_health(acme)
    assert healthy, payload["message"]
    assert payload["checks"]["manifold.yaml"] == "ok (3 components)"


def test_the_inventory_sees_three_components_and_three_handoffs(acme):
    inventory = wiki_inventory(acme)
    assert sorted(c.name for c in inventory.components) == ["acme-api", "acme-cli", "acme-web"]
    assert len(inventory.handoffs) == 3


def test_handoffs_are_in_three_different_states(acme):
    states = {h["status"] for h in handoff_list(acme)["handoffs"]}
    assert states == {"open", "in-progress", "completed"}
    assert [h["status"] for h in handoff_list(acme, target="acme-api", status="open")["handoffs"]] == ["open"]


def test_exactly_one_component_page_is_stale(acme):
    result = wiki_freshness(acme)
    assert [entry["component"] for entry in result["stale"]] == ["acme-cli"]
    assert result["stale"][0]["newer_raw_docs"] == ["raw/shared/2026-01-27-order-status-contract.md"]
    assert sorted(result["fresh"]) == ["acme-api", "acme-web"] and result["unknown"] == []


def test_the_example_can_be_worked_on(acme):
    created = handoff_create(acme, "acme-cli", "acme-web", "feature", "low", "Show the cli version", "s", "w")
    assert created["status"] == "created"
    assert handoff_claim(acme, created["path"])["status"] == "claimed"
    log = subprocess.run(["git", "log", "--format=%an", "-1"], cwd=acme, capture_output=True, text=True).stdout.strip()
    assert log == "manifold"


def test_the_example_inside_this_repository_is_never_committed_to():
    """Working in the in-tree folder must not write into the enclosing repository."""
    from wiki_backend.git import git_commit
    inside_a_repository = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=EXAMPLE,
                                         capture_output=True, text=True)
    if inside_a_repository.returncode != 0:
        pytest.skip("the checkout is not a git repository")
    probe = EXAMPLE / ".probe"
    probe.write_text("x")
    try:
        result = git_commit(EXAMPLE, [".probe"], "probe")
    finally:
        probe.unlink()
    assert result["committed"] is False and "inside another git repository" in result["reason"]


_LINK = re.compile(r"\]\(([^)\s]+)\)")


def test_every_relative_link_resolves():
    broken = []
    for page in sorted(EXAMPLE.rglob("*.md")):
        text = re.sub(r"```.*?```|`[^`\n]*`", "", page.read_text(encoding="utf-8"), flags=re.S)  # examples in code are not links
        for target in _LINK.findall(text):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#")[0]
            if path.startswith("/"):  # sidebar links are rooted at wiki/
                resolved = EXAMPLE / "wiki" / path.lstrip("/") if path != "/" else EXAMPLE / "wiki" / "index.md"
            else:
                resolved = (page.parent / path)
            if not resolved.exists():
                broken.append("%s -> %s" % (page.relative_to(EXAMPLE), target))
    assert broken == []


def test_frontmatter_is_complete_on_every_component_and_handoff_page():
    import frontmatter
    for page in (EXAMPLE / "wiki" / "components").glob("*.md"):
        meta = frontmatter.load(page).metadata
        assert {"title", "component", "status", "last_updated", "owner", "summary"} <= set(meta), page.name
    for page in (EXAMPLE / "wiki" / "handoffs").rglob("*.md"):
        meta = frontmatter.load(page).metadata
        assert {"title", "type", "source_component", "target_component", "status", "priority",
                "created", "updated"} <= set(meta), page.name
