# SPDX-License-Identifier: Apache-2.0
"""The server's identity comes from configuration: the MCP server name in exported helpers and the git author."""

import subprocess

import pytest

from wiki_backend.git import git_commit
from wiki_backend.helpers import wiki_export_all_helpers, wiki_export_helper

PROMPTS = [n for n in (
    "handoff-create", "handoff-pickup", "handoff-close", "handoff-update",
    "handoff-confirm", "handoff-reject", "manifold-update",
)]


def _set_server_name(root, name):
    (root / "manifold.yaml").write_text("version: 1\nserver_name: %s\n" % name)


@pytest.mark.parametrize("prompt", PROMPTS)
def test_prompts_name_the_configured_server(wiki_root, prompt):
    _set_server_name(wiki_root, "acme-wiki")
    exported = wiki_export_helper(wiki_root, prompt + "-prompt")["content"]
    assert "tools: ['acme-wiki/*']" in exported
    assert "{{MCP_SERVER}}" not in exported


def test_prompts_use_the_default_name_when_none_is_configured(wiki_root):
    (wiki_root / "manifold.yaml").write_text("version: 1\n")
    assert "tools: ['manifold/*']" in wiki_export_helper(wiki_root, "handoff-create-prompt")["content"]


def test_prompts_still_export_when_manifold_yaml_is_missing(wiki_root):
    (wiki_root / "manifold.yaml").unlink()
    assert "tools: ['manifold/*']" in wiki_export_helper(wiki_root, "handoff-create-prompt")["content"]


def test_no_exported_file_keeps_a_placeholder(wiki_root):
    _set_server_name(wiki_root, "acme-wiki")
    result = wiki_export_all_helpers(wiki_root)
    assert result["errors"] == []
    assert all("{{MCP_SERVER}}" not in f["content"] for f in result["files"])


def _author(root):
    return subprocess.run(["git", "log", "-1", "--format=%an <%ae>"], cwd=root,
                          capture_output=True, text=True).stdout.strip()


def _commit_in(root):
    # No identity configured in the repository, so the server's default applies.
    subprocess.run(["git", "config", "--unset", "user.name"], cwd=root)
    subprocess.run(["git", "config", "--unset", "user.email"], cwd=root)
    (root / "note.md").write_text("x")
    return git_commit(root, ["note.md"], "wiki: note")


def test_git_author_defaults_to_manifold(wiki_root, monkeypatch):
    monkeypatch.delenv("MANIFOLD_GIT_NAME", raising=False)
    monkeypatch.delenv("MANIFOLD_GIT_EMAIL", raising=False)
    assert _commit_in(wiki_root)["committed"]
    assert _author(wiki_root) == "manifold <manifold@localhost>"


def test_git_author_can_be_set_by_environment(wiki_root, monkeypatch):
    monkeypatch.setenv("MANIFOLD_GIT_NAME", "Acme Bot")
    monkeypatch.setenv("MANIFOLD_GIT_EMAIL", "bot@acme.test")
    assert _commit_in(wiki_root)["committed"]
    assert _author(wiki_root) == "Acme Bot <bot@acme.test>"
