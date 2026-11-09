# SPDX-License-Identifier: Apache-2.0
"""A multi-line registration value never becomes more than one entry (PHASE_1_TEST_PLAN A8).

Source: REVIEW.md Security rule (one caller value must never become more than one entry or key);
INT-1 S10, S3.  Either a refusal or a one-line encoding is accepted (owner answer to Q4); what is
not accepted is a value that adds a second entry, key, line or commit.

The "at most one" bound is measured, not assumed: a benign registration and a benign update run
first in the same instance, and the hostile ones may add no more lines, entries or commits than those.
"""

import re
import subprocess

import pytest

pytest.importorskip("fastmcp")

from wiki_backend.config import load_config  # noqa: E402

HOSTILE = "first line\n- slug: injected-entry\n  description: x\n## Injected heading\n- [x](y)\nkey: value"
FIELDS = ["description", "repo", "owner"]
BENIGN = {"description": "A component.", "repo": "https://example.test/org/benign", "owner": "team"}

INDEX = ("# Index\n\n| Component | Status | Wiki page | Description |\n"
         "|---|---|---|---|\n")


def _lines(path):
    return len(path.read_text().splitlines()) if path.is_file() else 0


def _snapshot(root):
    """Line counts of the files a registration touches, and the number of commits."""
    count = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=root, capture_output=True,
                           text=True, check=True).stdout.strip()
    return {
        "yaml_entries": len(re.findall(r"^\s*-\s*slug:", (root / "manifold.yaml").read_text(), re.MULTILINE)),
        "yaml_lines": _lines(root / "manifold.yaml"),
        "sidebar": _lines(root / "wiki" / "_sidebar.md"),
        "index": _lines(root / "wiki" / "index.md"),
        "log": _lines(root / "wiki" / "log.md"),
        "commits": int(count),
    }


def _delta(after, before):
    return {key: after[key] - before[key] for key in after}


def _page(root, slug):
    path = root / "wiki" / "components" / ("%s.md" % slug)
    return path.read_text() if path.is_file() else None


def _frontmatter_keys(text):
    head = text.split("---", 2)[1]
    return [line.split(":", 1)[0] for line in head.splitlines() if re.match(r"^[A-Za-z_]+:", line)]


@pytest.fixture()
def world(tool_world):
    tool_world.who("reg", "human", roles=["registrar"])
    (tool_world.root / "wiki" / "index.md").write_text(INDEX)
    root = tool_world.root

    before = _snapshot(root)
    benign = tool_world.call("reg", "wiki_register_component_tool", name="benign-one", skip_source_docs=True,
                             **BENIGN)
    assert benign.get("status") == "created", benign
    tool_world.register_delta = _delta(_snapshot(root), before)
    tool_world.benign_keys = _frontmatter_keys(_page(root, "benign-one"))

    before = _snapshot(root)
    updated = tool_world.call("reg", "wiki_component_manage_tool", action="update", name="benign-one",
                              description="Changed.", repo="https://example.test/org/changed", owner="team-b")
    assert updated.get("status") == "updated", updated
    tool_world.update_delta = _delta(_snapshot(root), before)
    return tool_world


def _check(world, slug, before, expected_slugs):
    root = world.root
    delta = _delta(_snapshot(root), before)
    bound = world.register_delta if slug == "fresh-one" else world.update_delta
    for key, value in delta.items():
        assert value <= bound[key], "%s grew by %d, a benign change grows it by %d" % (key, value, bound[key])
    assert sorted(load_config(root).slugs()) == sorted(expected_slugs)  # no extra component after a reload
    page = _page(root, slug)
    if page is not None:
        assert len(re.findall(r"^\*\*Repository:\*\*", page, re.MULTILINE)) == 1
        assert _frontmatter_keys(page) == world.benign_keys
        assert not re.search(r"^## Injected heading", page, re.MULTILINE)  # never a heading of its own
        assert not re.search(r"^- \[x\]\(y\)", page, re.MULTILINE)  # nor a list entry


@pytest.mark.parametrize("field", FIELDS)
def test_A8_a_multi_line_value_in_a_registration_is_one_entry_or_refused(world, field):
    root = world.root
    before = _snapshot(root)
    slugs = load_config(root).slugs()
    arguments = dict(BENIGN, **{field: HOSTILE})

    result = world.call("reg", "wiki_register_component_tool", name="fresh-one", skip_source_docs=True, **arguments)

    registered = result.get("status") == "created"
    if not registered:
        assert result.get("error") or result.get("refused") or result.get("status") == "error", result
        assert _snapshot(root) == before  # refused means nothing changed
    _check(world, "fresh-one", before, slugs + (["fresh-one"] if registered else []))


@pytest.mark.parametrize("field", FIELDS)
def test_A8_a_multi_line_value_in_an_update_is_one_entry_or_refused(world, field):
    root = world.root
    before = _snapshot(root)
    slugs = load_config(root).slugs()

    result = world.call("reg", "wiki_component_manage_tool", action="update", name="benign-one",
                        **{field: HOSTILE})

    if result.get("status") != "updated":
        assert result.get("error") or result.get("refused"), result
        assert _snapshot(root) == before
    _check(world, "benign-one", before, slugs)
