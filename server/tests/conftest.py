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
