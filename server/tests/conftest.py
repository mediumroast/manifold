# SPDX-License-Identifier: Apache-2.0
"""Shared pytest fixtures for wiki backend tests."""

import subprocess
import sys
from pathlib import Path

import pytest

# Make wiki_backend importable from server/
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture()
def wiki_root(tmp_path: Path) -> Path:
    """
    Isolated, git-backed wiki repo for testing.

    Layout mirrors production:
        <tmp>/
          wiki/
            CLAUDE.md
            log.md
            handoffs/
              acme-api-to-acme.io/   (with .gitkeep)
              acme-web-to-acme-api/            (with .gitkeep)
              acme-api-to-acme-web/            (with .gitkeep)

    An initial commit is created so git operations inside tests have a
    valid history to append to.
    """
    def git(*args):
        subprocess.run(
            ["git", *args],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )

    git("init")
    git("config", "user.name", "test-runner")
    git("config", "user.email", "test@test.local")

    # Build wiki skeleton
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "CLAUDE.md").write_text("# Wiki Schema\n")
    (wiki / "log.md").write_text("# Wiki Operation Log\n\n")

    for pair in ("acme-api-to-acme.io", "acme-web-to-acme-api", "acme-api-to-acme-web"):
        d = wiki / "handoffs" / pair
        d.mkdir(parents=True)
        (d / ".gitkeep").write_text("")

    (tmp_path / "manifold.yaml").write_text(
        "version: 1\n"
        "name: Test Wiki\n"
        "components:\n"
        + "".join("  - slug: %s\n" % slug for slug in
                  ("acme-api", "acme.io", "acme-web", "acme-cli", "acme-io", "acme-qa", "acme-data"))
    )

    git("add", "-A")
    git("commit", "-m", "test: init wiki skeleton")

    return tmp_path


class AuthWorld:
    """A security store holding two principals with a credential each (generated, never real)."""

    def __init__(self, conn, data_dir):
        from manifold_security import principals, tokens
        self.conn = conn
        self.data_dir = data_dir
        self.human = principals.create_principal(conn, "alice", "human")
        principals.set_role(conn, "alice", "contributor")
        self.agent = principals.create_principal(conn, "build-bot", "agent")
        principals.set_role(conn, "build-bot", "reader")
        self.human_credential = tokens.issue_credential(conn, self.human.id, "test")
        self.agent_credential = tokens.issue_credential(conn, self.agent.id, "test")
        self.human_token = self.human_credential.token
        self.agent_token = self.agent_credential.token


@pytest.fixture()
def auth_world(tmp_path: Path, monkeypatch):
    """
    Isolated store with a human and an agent principal, each with a credential.

    ``MANIFOLD_DATA_DIR`` points at it for the test, so code that opens the store from
    the environment (the server's middleware) uses this one and no real data folder.
    """
    from manifold_security.store import open_store

    data_dir = tmp_path / "auth-data"
    conn = open_store(data_dir, wiki_root=tmp_path / "wiki-root")
    monkeypatch.setenv("MANIFOLD_DATA_DIR", str(data_dir))
    monkeypatch.setenv("CONTAINER_WIKI_ROOT", str(tmp_path / "wiki-root"))
    world = AuthWorld(conn, data_dir)
    yield world
    conn.close()


@pytest.fixture()
def security_conn(tmp_path: Path):
    """
    Isolated security store (a fresh SQLite file in a temporary folder).

    The data folder is ``<tmp>/security-data`` and the wiki root passed to the
    store is ``<tmp>/wiki-root``, so the "not inside the instance repository"
    rule is exercised without touching any real data folder.
    """
    from manifold_security.store import open_store

    conn = open_store(tmp_path / "security-data", wiki_root=tmp_path / "wiki-root")
    yield conn
    conn.close()
