# SPDX-License-Identifier: Apache-2.0
"""Tests for wiki_backend.helpers — list helpers and batch export."""

import pytest
from pathlib import Path

from wiki_backend.helpers import wiki_list_helpers, wiki_export_helper, wiki_export_all_helpers


def _seed_helpers(wiki_root: Path) -> None:
    """The helper sources come from the core assets that ship with the server; nothing to seed."""


def test_list_helpers_returns_all(wiki_root: Path):
    result = wiki_list_helpers(wiki_root)
    assert "helpers" in result
    # 1 (ingest_doc) + 8 handoff/manifold + 6 review-cycle = 15
    assert len(result["helpers"]) == 15


def test_export_all_returns_files_list(wiki_root: Path):
    _seed_helpers(wiki_root)
    result = wiki_export_all_helpers(wiki_root)
    assert "files" in result
    assert isinstance(result["files"], list)
    assert result["count"] == len(result["files"])


def test_export_all_file_has_required_keys(wiki_root: Path):
    _seed_helpers(wiki_root)
    result = wiki_export_all_helpers(wiki_root)
    assert len(result["files"]) > 0
    for f in result["files"]:
        assert "name" in f
        assert "output_path" in f
        assert "content" in f


def test_export_all_includes_update_commands(wiki_root: Path):
    _seed_helpers(wiki_root)
    result = wiki_export_all_helpers(wiki_root)
    names = {f["name"] for f in result["files"]}
    assert "manifold-update-prompt" in names
    assert "manifold-update-command" in names


def test_export_single_still_works(wiki_root: Path):
    _seed_helpers(wiki_root)
    result = wiki_export_helper(wiki_root, "ingest_doc")
    assert "error" not in result
    assert result["name"] == "ingest_doc"
    assert "content" in result
    assert "output_path" in result
