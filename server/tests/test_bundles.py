# SPDX-License-Identifier: Apache-2.0
"""Tests for wiki_bundle_info, and the guard that assets/ never duplicates a bundle file."""

import hashlib
import zipfile
from pathlib import Path

import pytest

from wiki_backend import assets, bundles
from wiki_backend.bundles import RELEASES_URL, wiki_bundle_info


def _make_bundle(root: Path, name="base", version="0.1.0", archive=True) -> Path:
    bundle = root / name
    bundle.mkdir(parents=True)
    (bundle / "VERSION").write_text(version + "\n")
    if archive:
        (bundle / "dist").mkdir()
        with zipfile.ZipFile(bundle / "dist" / ("manifold-%s-%s.zip" % (name, version)), "w") as z:
            z.writestr("install.sh", "#!/bin/sh\n")
    return bundle


@pytest.fixture()
def bundle_dir(tmp_path, monkeypatch):
    directory = tmp_path / "bundles"
    directory.mkdir()
    monkeypatch.setenv("MANIFOLD_BUNDLES_DIR", str(directory))
    return directory


def test_lists_a_bundle_with_its_archive_and_hash(bundle_dir):
    bundle = _make_bundle(bundle_dir)
    archive = bundle / "dist" / "manifold-base-0.1.0.zip"
    info = wiki_bundle_info()
    assert info["bundles"] == [{
        "name": "base", "version": "0.1.0",
        "archive": "base/dist/manifold-base-0.1.0.zip",
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "bytes": archive.stat().st_size,
    }]
    assert "message" not in info
    assert any("install.sh --target" in step for step in info["install_steps"])


def test_a_bundle_without_a_built_archive_lists_version_only(bundle_dir):
    _make_bundle(bundle_dir, archive=False)
    assert wiki_bundle_info()["bundles"] == [{"name": "base", "version": "0.1.0"}]


def test_directories_without_a_version_file_are_ignored(bundle_dir):
    (bundle_dir / "notes").mkdir()
    _make_bundle(bundle_dir, name="wiki", version="0.2.0", archive=False)
    assert [b["name"] for b in wiki_bundle_info()["bundles"]] == ["wiki"]


def test_no_bundles_points_at_the_release_page(bundle_dir):
    info = wiki_bundle_info()
    assert info["bundles"] == [] and RELEASES_URL in info["message"] and info["releases"] == RELEASES_URL


def test_missing_directory_is_not_an_error(tmp_path, monkeypatch):
    monkeypatch.setenv("MANIFOLD_BUNDLES_DIR", str(tmp_path / "nope"))
    assert wiki_bundle_info()["bundles"] == []


def test_install_steps_mention_the_dry_run_and_the_checksum(bundle_dir):
    steps = " ".join(wiki_bundle_info()["install_steps"])
    assert "SHA-256" in steps and "writes nothing" in steps and "--apply" in steps


# ── assets/ and bundles/ must not hold the same file ─────────────────────────

def duplicates(assets_root: Path, bundles_root: Path):
    """Pairs (asset, bundle file) whose contents are identical."""
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    seen = {}
    for path in sorted(bundles_root.rglob("*")):
        if path.is_file() and "dist" not in path.relative_to(bundles_root).parts:
            seen.setdefault(digest(path), path)
    return [(a, seen[digest(a)]) for a in sorted(assets_root.rglob("*"))
            if a.is_file() and digest(a) in seen]


def test_the_guard_finds_a_planted_duplicate(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "bundles" / "base" / "agents").mkdir(parents=True)
    (tmp_path / "bundles" / "base" / "agents" / "planner.md").write_text("same text")
    (tmp_path / "assets" / "copy.md").write_text("same text")
    (tmp_path / "assets" / "other.md").write_text("different")
    assert duplicates(tmp_path / "assets", tmp_path / "bundles") == [
        (tmp_path / "assets" / "copy.md", tmp_path / "bundles" / "base" / "agents" / "planner.md")
    ]


def test_no_core_asset_duplicates_a_bundle_file(monkeypatch):
    monkeypatch.delenv("MANIFOLD_ASSETS_DIR", raising=False)
    monkeypatch.delenv("MANIFOLD_BUNDLES_DIR", raising=False)
    bundles_root = bundles.bundles_dir()
    if not bundles_root.is_dir():
        pytest.skip("no bundles/ directory beside this server (it is checked where the bundles live)")
    assert duplicates(assets.core_assets_dir(), bundles_root) == []
