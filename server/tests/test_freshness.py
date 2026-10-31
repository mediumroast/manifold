# SPDX-License-Identifier: Apache-2.0
"""Tests for wiki_freshness_tool."""

from datetime import date, timedelta
from pathlib import Path

import pytest

from wiki_backend.freshness import wiki_freshness


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_component(wiki_root: Path, slug: str, last_updated: date) -> Path:
    """Create a minimal component wiki page with last_updated frontmatter."""
    components_dir = wiki_root / "wiki" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    page = components_dir / f"{slug}.md"
    page.write_text(
        f"---\n"
        f"title: {slug}\n"
        f"component: {slug}\n"
        f"status: active\n"
        f"last_updated: {last_updated}\n"
        f"owner: test\n"
        f"summary: test component\n"
        f"---\n\n## Overview\nTest.\n"
    )
    return page


def _make_raw_doc(wiki_root: Path, subdir: str, filename: str) -> Path:
    """Create a raw doc file under raw/{subdir}/."""
    raw_dir = wiki_root / "raw" / subdir
    raw_dir.mkdir(parents=True, exist_ok=True)
    f = raw_dir / filename
    f.write_text(f"# {filename}\nContent.\n")
    return f


# ── tests ─────────────────────────────────────────────────────────────────────

def test_fresh_when_no_raw_docs(wiki_root):
    """A component with no raw docs at all is considered fresh (nothing to compare)."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 10))
    result = wiki_freshness(wiki_root)
    assert "acme-api" in result["fresh"]
    assert result["stale"] == []


def test_fresh_when_raw_doc_older_than_wiki(wiki_root):
    """Raw doc dated before last_updated → fresh."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 20))
    _make_raw_doc(wiki_root, "acme-api", "2026-05-10-acme-api-readme.md")
    result = wiki_freshness(wiki_root)
    assert "acme-api" in result["fresh"]
    assert result["stale"] == []


def test_stale_when_raw_doc_newer_than_wiki(wiki_root):
    """Raw doc dated after last_updated → stale."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 10))
    _make_raw_doc(wiki_root, "acme-api", "2026-05-22-acme-api-api.md")
    result = wiki_freshness(wiki_root)
    assert len(result["stale"]) == 1
    entry = result["stale"][0]
    assert entry["component"] == "acme-api"
    assert entry["wiki_page"] == "wiki/components/acme-api.md"
    assert entry["last_wiki_update"] == "2026-05-10"
    assert any("acme-api-api" in p for p in entry["newer_raw_docs"])


def test_stale_lists_multiple_newer_raw_docs(wiki_root):
    """All newer raw docs appear in the stale entry."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 10))
    _make_raw_doc(wiki_root, "acme-api", "2026-05-15-acme-api-api.md")
    _make_raw_doc(wiki_root, "acme-api", "2026-05-20-acme-api-architecture.md")
    result = wiki_freshness(wiki_root)
    assert len(result["stale"]) == 1
    assert len(result["stale"][0]["newer_raw_docs"]) == 2


def test_shared_doc_marks_all_components_stale(wiki_root):
    """A shared raw doc newer than multiple components marks all of them stale."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 10))
    _make_component(wiki_root, "acme-web", date(2026, 5, 10))
    _make_raw_doc(wiki_root, "shared", "2026-05-22-auth-contract.md")
    result = wiki_freshness(wiki_root)
    stale_slugs = {e["component"] for e in result["stale"]}
    assert "acme-api" in stale_slugs
    assert "acme-web" in stale_slugs


def test_shared_doc_only_marks_stale_components(wiki_root):
    """A shared raw doc does not mark a component stale if the component is already current."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 25))
    _make_raw_doc(wiki_root, "shared", "2026-05-22-auth-contract.md")
    result = wiki_freshness(wiki_root)
    assert "acme-api" in result["fresh"]
    assert result["stale"] == []


def test_filter_by_component(wiki_root):
    """Passing component= checks only that component."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 10))
    _make_component(wiki_root, "acme-web", date(2026, 5, 10))
    _make_raw_doc(wiki_root, "acme-api", "2026-05-22-acme-api-api.md")
    _make_raw_doc(wiki_root, "acme-web", "2026-05-22-acme-web-api.md")

    result = wiki_freshness(wiki_root, component="acme-api")
    assert len(result["stale"]) == 1
    assert result["stale"][0]["component"] == "acme-api"
    # acme-web not checked
    assert "acme-web" not in result["fresh"]
    assert not any(e["component"] == "acme-web" for e in result["stale"])


def test_unknown_when_wiki_page_missing(wiki_root):
    """Requesting a component slug with no wiki page returns unknown."""
    result = wiki_freshness(wiki_root, component="nonexistent")
    assert len(result["unknown"]) == 1
    assert result["unknown"][0]["component"] == "nonexistent"


def test_unknown_when_no_last_updated(wiki_root):
    """A component page with no last_updated frontmatter returns unknown."""
    components_dir = wiki_root / "wiki" / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    page = components_dir / "acme-api.md"
    page.write_text("---\ntitle: acme-api\nstatus: active\n---\n\n## Overview\n")
    result = wiki_freshness(wiki_root, component="acme-api")
    assert len(result["unknown"]) == 1
    assert "last_updated" in result["unknown"][0]["reason"]


def test_multiple_components_mixed_results(wiki_root):
    """fresh, stale, and unknown can all appear in a single call."""
    _make_component(wiki_root, "acme-api", date(2026, 5, 10))
    _make_component(wiki_root, "acme-web", date(2026, 5, 25))
    # acme-api has a newer raw doc → stale
    _make_raw_doc(wiki_root, "acme-api", "2026-05-22-acme-api-api.md")
    # acme-web raw doc is older → fresh

    result = wiki_freshness(wiki_root, component=None)
    stale_slugs = {e["component"] for e in result["stale"]}
    assert "acme-api" in stale_slugs
    assert "acme-web" in result["fresh"]
