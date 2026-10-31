# SPDX-License-Identifier: Apache-2.0
"""The starter instance is a valid empty instance, and the first registrations fill in its navigation."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from wiki_backend.config import load_config, sync_schema_slugs
from wiki_backend.handoff import handoff_create
from wiki_backend.health import wiki_health
from wiki_backend.models import WikiRegisterRequest
from wiki_backend.register import wiki_register_component

STARTER = Path(__file__).resolve().parents[2] / "examples" / "starter"

pytestmark = pytest.mark.skipif(not STARTER.is_dir(), reason="no examples/starter beside the server")


@pytest.fixture()
def mine(tmp_path):
    root = tmp_path / "my-wiki"
    shutil.copytree(STARTER, root)
    for args in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t.test"],
                 ["add", "-A"], ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    return root


def register(root, name):
    return wiki_register_component(root, WikiRegisterRequest(
        name=name, description="The %s component" % name, repo="https://example.test/%s" % name,
        owner="Team", skip_source_docs=True))


def test_the_starter_is_healthy_with_no_components(mine):
    healthy, payload = wiki_health(mine)
    assert healthy, payload["message"]
    assert payload["checks"]["manifold.yaml"] == "ok (0 components)"
    assert load_config(mine).name == "My Team Wiki"


def test_the_schema_slug_list_starts_empty(mine):
    assert sync_schema_slugs(mine) is None
    text = (mine / "wiki" / "CLAUDE.md").read_text()
    assert "Valid component slugs:\n\nThe list above" in text and "acme" not in text.lower()


def test_the_first_component_appears_in_the_registry_sidebar_and_index(mine):
    assert register(mine, "billing").status == "created"
    assert load_config(mine).slugs() == ["billing"]
    sidebar = (mine / "wiki" / "_sidebar.md").read_text()
    assert sidebar.index("- **Components**") < sidebar.index("[billing](/components/billing.md)") < sidebar.index("- **Handoffs**")
    index = (mine / "wiki" / "index.md").read_text()
    assert "| billing | active | [wiki/components/billing.md](components/billing.md) |" in index
    assert "- `billing`" in (mine / "wiki" / "CLAUDE.md").read_text()


def test_later_components_follow_the_first_in_every_list(mine):
    for name in ("billing", "catalog", "checkout"):
        assert register(mine, name).status == "created"
    sidebar = (mine / "wiki" / "_sidebar.md").read_text()
    positions = [sidebar.index("[%s](/components/%s.md)" % (n, n)) for n in ("billing", "catalog", "checkout")]
    assert positions == sorted(positions)
    rows = [l for l in (mine / "wiki" / "index.md").read_text().splitlines() if l.startswith("| ") and "/components/" in l]
    assert [r.split("|")[1].strip() for r in rows] == ["billing", "catalog", "checkout"]


def test_a_handoff_between_new_components_works_and_is_listed(mine):
    register(mine, "billing")
    register(mine, "catalog")
    created = handoff_create(mine, "catalog", "billing", "feature", "low", "Price export", "s", "w")
    assert created["status"] == "created"
    sidebar = (mine / "wiki" / "_sidebar.md").read_text()
    assert "  - catalog → billing" in sidebar and "Price export" in sidebar


def test_registering_twice_does_not_duplicate_anything(mine):
    register(mine, "billing")
    assert register(mine, "billing").status == "already_registered"
    assert (mine / "wiki" / "_sidebar.md").read_text().count("[billing]") == 1
    assert (mine / "manifold.yaml").read_text().count("slug: billing") == 1


def test_every_relative_link_in_the_starter_resolves():
    broken = []
    for page in sorted(STARTER.rglob("*.md")):
        text = re.sub(r"```.*?```|`[^`\n]*`", "", page.read_text(encoding="utf-8"), flags=re.S)
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#")[0]
            resolved = (STARTER / "wiki" / path.lstrip("/")) if path.startswith("/") else page.parent / path
            if path == "/":
                resolved = STARTER / "wiki" / "index.md"
            if not resolved.exists():
                broken.append("%s -> %s" % (page.relative_to(STARTER), target))
    assert broken == []
