# SPDX-License-Identifier: Apache-2.0
"""Tests for document ingestion: path containment, size limits, and the capped body reader."""

import asyncio
import os
import subprocess

import pytest

from wiki_backend.ingest import (
    BodyTooLarge,
    max_ingest_bytes,
    read_body_capped,
    wiki_ingest_doc,
)


def _chunks(*parts):
    async def gen():
        for part in parts:
            yield part
    return gen()


def _read(parts, declared=None, limit=10):
    return asyncio.run(read_body_capped(_chunks(*parts), declared, limit))


# ── happy path ────────────────────────────────────────────────────────────────

def test_ingest_writes_into_the_component_directory_and_commits(wiki_root):
    result = wiki_ingest_doc(wiki_root, "acme-api", "readme", "# Hello\n")
    assert result["status"] == "ok"
    assert result["path"].startswith("raw/acme-api/")
    assert (wiki_root / result["path"]).read_text() == "# Hello\n"
    log = subprocess.run(["git", "log", "--oneline", "-1"], cwd=wiki_root,
                         capture_output=True, text=True).stdout
    assert "ingest" in log


def test_filename_stem_is_slugged(wiki_root):
    result = wiki_ingest_doc(wiki_root, "acme-api", "other", "text", "Extractor_Cookbook.md")
    assert result["path"].endswith("-acme-api-extractor-cookbook.md")


# ── slugs that must not reach the file system ────────────────────────────────

@pytest.mark.parametrize("slug", [
    "..", "../x", "a/b", "a\\b", ".hidden", "-lead", "_lead", "a b", "a..b", "a.",
    "", "   ", "café", "٣٤", "x" * 65, "a\x00b",
])
def test_bad_slugs_are_refused_and_nothing_is_created(wiki_root, slug):
    result = wiki_ingest_doc(wiki_root, slug, "other", "text")
    assert result["status"] == "error"
    assert not (wiki_root / "raw").exists()


def test_dotted_slug_is_accepted(wiki_root):
    assert wiki_ingest_doc(wiki_root, "acme.io", "other", "text")["status"] == "ok"


def test_slug_is_lowercased(wiki_root):
    result = wiki_ingest_doc(wiki_root, "Acme-API", "other", "text")
    assert result["component"] == "acme-api"


# ── symlinks that lead out of raw/ ───────────────────────────────────────────

def test_component_directory_that_is_a_symlink_out_is_refused(wiki_root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    (wiki_root / "raw").mkdir()
    os.symlink(outside, wiki_root / "raw" / "acme-api")
    result = wiki_ingest_doc(wiki_root, "acme-api", "other", "text")
    assert result["status"] == "error"
    assert list(outside.iterdir()) == []


def test_raw_directory_that_is_a_symlink_out_is_refused(wiki_root, tmp_path_factory):
    outside = tmp_path_factory.mktemp("outside")
    os.symlink(outside, wiki_root / "raw")
    result = wiki_ingest_doc(wiki_root, "acme-api", "other", "text")
    assert result["status"] == "error"
    assert list(outside.iterdir()) == []


# ── filename tricks ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("filename", [
    "../../etc/passwd", "/etc/passwd", "..", "...", "a/../../b.md", ".md", "-.md",
    "x" * 500 + ".md",
])
def test_filenames_cannot_escape_or_overflow(wiki_root, filename):
    result = wiki_ingest_doc(wiki_root, "acme-api", "other", "text", filename)
    assert result["status"] == "ok"
    written = wiki_root / result["path"]
    assert written.parent == (wiki_root / "raw" / "acme-api").resolve()
    assert len(written.name) < 140


# ── content limits ───────────────────────────────────────────────────────────

def test_content_over_the_limit_is_refused_with_a_reason(wiki_root, monkeypatch):
    monkeypatch.setenv("MANIFOLD_INGEST_MAX_BYTES", "10")
    result = wiki_ingest_doc(wiki_root, "acme-api", "other", "x" * 11)
    assert result["status"] == "error" and result["reason"] == "too_large"
    assert not (wiki_root / "raw").exists()


def test_limit_counts_bytes_not_characters(wiki_root, monkeypatch):
    monkeypatch.setenv("MANIFOLD_INGEST_MAX_BYTES", "10")
    result = wiki_ingest_doc(wiki_root, "acme-api", "other", "é" * 6)  # 12 bytes
    assert result["reason"] == "too_large"


def test_content_at_the_limit_is_accepted(wiki_root, monkeypatch):
    monkeypatch.setenv("MANIFOLD_INGEST_MAX_BYTES", "10")
    assert wiki_ingest_doc(wiki_root, "acme-api", "other", "x" * 10)["status"] == "ok"


def test_nul_bytes_are_refused(wiki_root):
    assert wiki_ingest_doc(wiki_root, "acme-api", "other", "a\x00b")["status"] == "error"


@pytest.mark.parametrize("value,expected", [
    (None, 1024 * 1024), ("2048", 2048), ("0", 1024 * 1024), ("-5", 1024 * 1024), ("lots", 1024 * 1024),
])
def test_limit_setting(monkeypatch, value, expected):
    if value is None:
        monkeypatch.delenv("MANIFOLD_INGEST_MAX_BYTES", raising=False)
    else:
        monkeypatch.setenv("MANIFOLD_INGEST_MAX_BYTES", value)
    assert max_ingest_bytes() == expected


# ── the capped body reader ───────────────────────────────────────────────────

def test_body_under_the_limit_is_returned_whole():
    assert _read([b"abc", b"def"]) == b"abcdef"


def test_body_at_the_limit_is_accepted():
    assert _read([b"x" * 10], limit=10) == b"x" * 10


def test_declared_length_over_the_limit_is_refused_before_reading():
    consumed = []

    async def gen():
        consumed.append(1)
        yield b"x"

    with pytest.raises(BodyTooLarge):
        asyncio.run(read_body_capped(gen(), "11", 10))
    assert consumed == []


def test_body_that_lies_about_its_length_is_stopped_when_it_passes_the_limit():
    with pytest.raises(BodyTooLarge):
        _read([b"x" * 6, b"x" * 6], declared="3", limit=10)


def test_unparseable_declared_length_falls_back_to_counting():
    assert _read([b"abc"], declared="oops") == b"abc"
    with pytest.raises(BodyTooLarge):
        _read([b"x" * 11], declared="oops")
