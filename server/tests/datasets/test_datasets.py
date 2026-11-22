# SPDX-License-Identifier: Apache-2.0
"""The curated test instances: they load, they are healthy, and (later tasks) they behave."""

import subprocess

import pytest

from tests.datasets import loader
from wiki_backend.health import wiki_health


@pytest.fixture()
def dataset(tmp_path):
    """``dataset(name)``: a private git-backed copy of the curated set ``name`` (see loader.copy_curated)."""
    return lambda name: loader.copy_curated(tmp_path, name)


def _git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True).stdout


@pytest.mark.parametrize("name", ["messy", "hostile"])
def test_a_curated_copy_is_healthy_and_git_backed(dataset, name):
    root = dataset(name)
    healthy, payload = wiki_health(root)
    assert healthy, payload["message"]
    assert payload["checks"]["git repository"] == "ok"
    assert _git(root, "log", "--format=%an <%ae>").splitlines() == ["datasets <datasets@example.test>"]
    assert _git(root, "status", "--porcelain") == ""


def test_the_curated_names_are_the_two_sets_and_an_unknown_name_is_refused(tmp_path):
    assert loader.curated_names() == ["hostile", "messy"]
    with pytest.raises(ValueError, match="no curated set 'nope'"):
        loader.copy_curated(tmp_path, "nope")
    with pytest.raises(ValueError):
        loader.copy_curated(tmp_path, "../messy")


def test_two_copies_of_a_set_have_the_same_commit(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    first = loader.copy_curated(tmp_path / "a", "messy")
    second = loader.copy_curated(tmp_path / "b", "messy")
    assert _git(first, "rev-parse", "HEAD") == _git(second, "rev-parse", "HEAD")


@pytest.mark.parametrize("chars", [1, 100, 5000, 200000])
def test_long_page_has_the_stated_size_and_is_the_same_every_time(chars):
    text = loader.long_page(chars)
    assert len(text) == chars and text == loader.long_page(chars)
    assert text == text.strip()
