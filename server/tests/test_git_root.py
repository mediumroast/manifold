# SPDX-License-Identifier: Apache-2.0
"""git_commit commits only in a repository whose top level is the wiki root."""

import subprocess

from wiki_backend.git import git_commit


def _git(path, *args):
    return subprocess.run(["git", *args], cwd=path, capture_output=True, text=True, check=True).stdout.strip()


def test_commits_in_the_wiki_root_repository(wiki_root):
    (wiki_root / "note.md").write_text("x")
    assert git_commit(wiki_root, ["note.md"], "wiki: note")["committed"]


def test_refuses_to_commit_into_a_parent_repository(wiki_root):
    inner = wiki_root / "examples" / "inner"
    inner.mkdir(parents=True)
    (inner / "note.md").write_text("x")
    before = _git(wiki_root, "rev-list", "--count", "HEAD")
    result = git_commit(inner, ["note.md"], "wiki: note")
    assert result["committed"] is False and "inside another git repository" in result["reason"]
    assert _git(wiki_root, "rev-list", "--count", "HEAD") == before
    assert "note.md" not in _git(wiki_root, "diff", "--cached", "--name-only")


def test_refuses_outside_any_repository(tmp_path):
    (tmp_path / "note.md").write_text("x")
    result = git_commit(tmp_path, ["note.md"], "wiki: note")
    assert result["committed"] is False and "not a git repository" in result["reason"]
