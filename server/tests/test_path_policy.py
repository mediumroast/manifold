# SPDX-License-Identifier: Apache-2.0
"""The page tools write and read only where they should (PHASE_1_PLAN T8, T9; INT-1 S16).

Everything runs against the temporary ``wiki_root`` fixture; no real data is touched.
``wiki_write_page`` accepts only component and shared pages; handoff pages have their own
writer, ``wiki_write_handoff_page`` (owner decision on T9, "strict everywhere").
"""

import os
import subprocess

import pytest

from manifold_security import scopes
from wiki_backend.handoff import wiki_write_handoff_page
from wiki_backend.models import WikiWriteRequest
from wiki_backend.read import wiki_read
from wiki_backend.write import wiki_write_page

CONTENT = "# Planted\n\nThis must not land.\n"

# Paths a tool may never write: system files, the log, handoffs, and anything that leaves the root.
TOOL_WRITE_REFUSED = [
    "manifold.yaml",
    "wiki/_sidebar.md",
    "wiki/CLAUDE.md",
    "wiki/log.md",
    "wiki/handoffs/acme-api-to-acme-web/x.md",
]
# Paths nothing may write, tool or not.
ESCAPING = ["../outside.md", "wiki/../../outside.md", "wiki/a\x00b.md"]


def _tree(root):
    """Every file under root (outside .git) with its bytes, to prove nothing changed."""
    seen = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            full = os.path.join(base, name)
            if os.path.islink(full):
                seen[full] = os.readlink(full)
            else:
                with open(full, "rb") as handle:
                    seen[full] = handle.read()
    return seen


def _write(root, path, **kwargs):
    return wiki_write_page(root, WikiWriteRequest(path=path, content=CONTENT, message="test"), **kwargs)


@pytest.mark.parametrize("path", TOOL_WRITE_REFUSED)
def test_a_tool_write_to_a_protected_path_is_refused(wiki_root, path):
    before = _tree(wiki_root)
    response = _write(wiki_root, path)
    assert response.status == "error", response
    assert _tree(wiki_root) == before


@pytest.mark.parametrize("path", ESCAPING)
def test_a_write_that_leaves_the_root_is_refused(wiki_root, path):
    before = _tree(wiki_root)
    response = _write(wiki_root, path)
    assert response.status == "error", response
    assert _tree(wiki_root) == before
    assert not (wiki_root.parent / "outside.md").exists()


def test_a_write_by_absolute_path_is_refused(wiki_root, tmp_path_factory):
    elsewhere = tmp_path_factory.mktemp("elsewhere") / "x.md"
    before = _tree(wiki_root)
    response = _write(wiki_root, str(elsewhere))
    assert response.status == "error", response
    assert not elsewhere.exists()
    assert _tree(wiki_root) == before


def test_a_write_through_a_symlink_that_leaves_the_root_is_refused(wiki_root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside-dir")
    (wiki_root / "wiki" / "link").symlink_to(outside, target_is_directory=True)
    response = _write(wiki_root, "wiki/link/x.md")
    assert response.status == "error", response
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("path", ["../outside.md", "wiki/../../outside.md", "manifold.yaml",
                                  ".git/config", "wiki/../.git/config"])
def test_a_read_outside_wiki_and_raw_is_refused(wiki_root, path):
    (wiki_root.parent / "outside.md").write_text("secret\n")
    with pytest.raises((ValueError, FileNotFoundError)):
        wiki_read(wiki_root, path)


def test_a_read_by_absolute_path_is_refused(wiki_root, tmp_path_factory):
    target = tmp_path_factory.mktemp("elsewhere") / "x.md"
    target.write_text("secret\n")
    with pytest.raises((ValueError, FileNotFoundError)):
        wiki_read(wiki_root, str(target))


def test_a_read_through_a_symlink_that_leaves_the_root_is_refused(wiki_root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside-file") / "secret.md"
    outside.write_text("secret\n")
    (wiki_root / "wiki" / "leak.md").symlink_to(outside)
    with pytest.raises((ValueError, FileNotFoundError)):
        wiki_read(wiki_root, "wiki/leak.md")


# ── the policy itself ────────────────────────────────────────────────────────

@pytest.mark.parametrize("path,kind,scope", [
    ("wiki/components/acme-api.md", "component", "acme-api"),
    ("wiki/guides/agents/acme-api.md", "component", "acme-api"),
    ("wiki/handoffs/acme-api-to-acme-web/x.md", "handoff-only", None),
    ("wiki/log.md", "log-only", None),
    ("wiki/_sidebar.md", "system", None),
    ("wiki/CLAUDE.md", "system", None),
    ("manifold.yaml", "system", None),
    ("wiki/decisions/2026-01-01-x.md", "shared", "_shared"),
    ("wiki/index.md", "shared", "_shared"),
    ("wiki/guides/notes.md", "shared", "_shared"),
])
def test_classify_gives_kind_and_scope(wiki_root, path, kind, scope):
    assert scopes.classify(wiki_root, path) == (kind, scope)


@pytest.mark.parametrize("path", ["src/app.py", "raw/acme-api/x.md", "wiki/notes.txt", "README.md", "",
                                  "wiki/components/Bad Name.md"])
def test_classify_refuses_everything_else(wiki_root, path):
    with pytest.raises(scopes.PathRefused):
        scopes.classify(wiki_root, path)


def test_component_and_shared_pages_are_still_writable(wiki_root):
    assert _write(wiki_root, "wiki/components/acme-api.md").status == "created"
    assert _write(wiki_root, "wiki/decisions/2026-01-01-x.md").status == "created"


def test_the_handoff_writer_accepts_only_handoff_pages(wiki_root):
    before = _tree(wiki_root)
    for path in ("wiki/components/acme-api.md", "wiki/log.md", "manifold.yaml", "../outside.md"):
        response = wiki_write_handoff_page(
            wiki_root, WikiWriteRequest(path=path, content=CONTENT, message="test"))
        assert response.status == "error", path
    assert _tree(wiki_root) == before


def test_wiki_and_raw_pages_are_readable(wiki_root):
    (wiki_root / "raw" / "acme-api").mkdir(parents=True)
    (wiki_root / "raw" / "acme-api" / "r.md").write_text("raw\n")
    assert wiki_read(wiki_root, "wiki/CLAUDE.md").body.startswith("# Wiki Schema")
    assert wiki_read(wiki_root, "raw/acme-api/r.md").body.strip() == "raw"


def test_git_status_stays_clean_after_refusals(wiki_root):
    for path in TOOL_WRITE_REFUSED:
        _write(wiki_root, path)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=wiki_root, capture_output=True, text=True)
    assert status.stdout == ""


