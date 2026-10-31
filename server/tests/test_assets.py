# SPDX-License-Identifier: Apache-2.0
"""Tests for the asset overlay: instance files over core files, and path containment."""

import os

import pytest

from wiki_backend import assets
from wiki_backend.helpers import _HELPERS, wiki_export_all_helpers, wiki_export_helper


@pytest.fixture()
def core(tmp_path, monkeypatch):
    """A throwaway core assets directory, selected through MANIFOLD_ASSETS_DIR."""
    directory = tmp_path / "core-assets"
    (directory / "helpers" / "commands").mkdir(parents=True)
    (directory / "helpers" / "commands" / "one.md").write_text("core one")
    (directory / "helpers" / "commands" / "two.md").write_text("core two")
    monkeypatch.setenv("MANIFOLD_ASSETS_DIR", str(directory))
    return directory


def _instance_file(wiki_root, rel, text):
    path = wiki_root / "assets" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


# ── resolution order ─────────────────────────────────────────────────────────

def test_core_file_is_found_when_the_instance_has_none(wiki_root, core):
    found = assets.find(wiki_root, "helpers/commands/one.md")
    assert found["origin"] == "core" and found["path"].read_text() == "core one"


def test_instance_file_wins_over_core(wiki_root, core):
    _instance_file(wiki_root, "helpers/commands/one.md", "instance one")
    assert assets.find(wiki_root, "helpers/commands/one.md")["origin"] == "instance"
    assert assets.read_text(wiki_root, "helpers/commands/one.md") == "instance one"
    assert assets.read_text(wiki_root, "helpers/commands/two.md") == "core two"


def test_instance_can_add_a_new_file(wiki_root, core):
    _instance_file(wiki_root, "helpers/commands/three.md", "instance three")
    assert assets.read_text(wiki_root, "helpers/commands/three.md") == "instance three"


def test_missing_asset_is_none(wiki_root, core):
    assert assets.find(wiki_root, "helpers/commands/nope.md") is None
    assert assets.read_text(wiki_root, "nope/nope.md") is None


def test_list_merges_both_layers_and_reports_the_origin(wiki_root, core):
    _instance_file(wiki_root, "helpers/commands/two.md", "instance two")
    _instance_file(wiki_root, "helpers/commands/three.md", "instance three")
    assert assets.list_files(wiki_root, "helpers/commands", "*.md") == {
        "one.md": "core", "three.md": "instance", "two.md": "instance",
    }


def test_list_of_a_missing_directory_is_empty(wiki_root, core):
    assert assets.list_files(wiki_root, "nope") == {}


# ── containment ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("rel", [
    "../secret.md", "helpers/../../secret.md", "/etc/passwd", "\\windows", "", "a\x00b",
    "helpers/commands/../../../secret.md",
])
def test_paths_that_leave_the_assets_directory_are_not_found(wiki_root, core, rel):
    (core.parent / "secret.md").write_text("secret")
    assert assets.find(wiki_root, rel) is None


def test_symlink_that_leaves_the_assets_directory_is_not_followed(wiki_root, core, tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("outside")
    os.symlink(outside, core / "helpers" / "commands" / "link.md")
    assert assets.find(wiki_root, "helpers/commands/link.md") is None
    assert "link.md" not in assets.list_files(wiki_root, "helpers/commands")


def test_instance_symlink_out_is_not_followed_and_core_is_used(wiki_root, core, tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("outside")
    (wiki_root / "assets" / "helpers" / "commands").mkdir(parents=True)
    os.symlink(outside, wiki_root / "assets" / "helpers" / "commands" / "one.md")
    assert assets.read_text(wiki_root, "helpers/commands/one.md") == "core one"


# ── core location ────────────────────────────────────────────────────────────

def test_environment_variable_selects_the_core_directory(core):
    assert assets.core_assets_dir() == core


def test_default_core_directory_is_the_repository_assets(monkeypatch):
    monkeypatch.delenv("MANIFOLD_ASSETS_DIR", raising=False)
    assert (assets.core_assets_dir() / "helpers").is_dir()


# ── the shipped assets are complete, and an instance does not need copies ────

def test_every_registered_helper_exists_in_the_core_assets(wiki_root, monkeypatch):
    monkeypatch.delenv("MANIFOLD_ASSETS_DIR", raising=False)
    missing = [n for n, m in _HELPERS.items() if assets.find(wiki_root, m["source"]) is None]
    assert missing == []


def test_export_comes_from_core_for_an_instance_with_no_helper_files(wiki_root, monkeypatch):
    monkeypatch.delenv("MANIFOLD_ASSETS_DIR", raising=False)
    result = wiki_export_all_helpers(wiki_root)
    assert result["errors"] == [] and result["count"] == len(_HELPERS)
    assert {f["origin"] for f in result["files"]} == {"core"}
    assert not (wiki_root / "wiki" / "commands").exists()


def test_instance_override_changes_the_exported_content_and_reports_it(wiki_root, monkeypatch):
    monkeypatch.delenv("MANIFOLD_ASSETS_DIR", raising=False)
    source = _HELPERS["handoff-create-command"]["source"]
    _instance_file(wiki_root, source, "# our own handoff-create\n")
    exported = wiki_export_helper(wiki_root, "handoff-create-command")
    assert exported["content"] == "# our own handoff-create\n" and exported["origin"] == "instance"
    others = [f for f in wiki_export_all_helpers(wiki_root)["files"] if f["name"] != "handoff-create-command"]
    assert {f["origin"] for f in others} == {"core"}


def test_missing_helper_source_says_where_it_looked(wiki_root, core):
    result = wiki_export_helper(wiki_root, "ingest_doc")
    assert "helpers/tools/ingest_doc.py" in result["error"] and str(core) in result["error"]
