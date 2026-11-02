# SPDX-License-Identifier: Apache-2.0
"""The security store: modes, migrations, refusals, standard-library-only imports."""

import ast
import os
import sqlite3
import stat
import sys
from pathlib import Path

import pytest

from manifold_security import store
from manifold_security.store import StoreError, open_store

TABLES = {"settings", "principals", "credentials", "roles", "grants", "denies",
          "component_state", "usage", "audit"}


def _mode(path: Path) -> int:
    return stat.S_IMODE(os.stat(path).st_mode)


def _tables(conn) -> set:
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")} - {"sqlite_sequence"}


def test_creates_folder_and_file_with_private_modes(tmp_path):
    data = tmp_path / "data" / "nested"
    conn = open_store(data, wiki_root=tmp_path / "wiki")
    assert _mode(data) == 0o700
    assert _mode(data / "manifold.db") == 0o600
    conn.close()


def test_existing_loose_modes_are_tightened(tmp_path):
    data = tmp_path / "data"
    data.mkdir(mode=0o755)
    os.chmod(data, 0o755)
    (data / "manifold.db").write_bytes(b"")
    os.chmod(data / "manifold.db", 0o644)
    open_store(data, wiki_root=tmp_path / "wiki").close()
    assert _mode(data) == 0o700 and _mode(data / "manifold.db") == 0o600


def test_migrates_from_empty_database(tmp_path):
    conn = open_store(tmp_path / "d", wiki_root=tmp_path / "wiki")
    assert _tables(conn) == TABLES
    assert conn.execute("PRAGMA user_version").fetchone()[0] == store.latest_version() >= 1
    conn.close()


def test_migrates_from_explicit_version_zero_file(tmp_path):
    data = tmp_path / "d"
    data.mkdir()
    raw = sqlite3.connect(data / "manifold.db")
    raw.execute("PRAGMA user_version = 0")
    raw.commit()
    raw.close()
    conn = open_store(data, wiki_root=tmp_path / "wiki")
    assert _tables(conn) == TABLES
    conn.close()


def test_reopen_is_idempotent_and_keeps_data(tmp_path):
    data = tmp_path / "d"
    conn = open_store(data, wiki_root=tmp_path / "wiki")
    conn.execute("INSERT INTO settings(key, value, updated_at) VALUES ('k', 'v', 't')")
    conn.close()
    conn = open_store(data, wiki_root=tmp_path / "wiki")
    assert conn.execute("SELECT value FROM settings WHERE key='k'").fetchone()[0] == "v"
    conn.close()


def test_refuses_newer_schema_version(tmp_path):
    data = tmp_path / "d"
    data.mkdir()
    raw = sqlite3.connect(data / "manifold.db")
    raw.execute("PRAGMA user_version = %d" % (store.latest_version() + 1))
    raw.commit()
    raw.close()
    with pytest.raises(StoreError, match="Upgrade Manifold"):
        open_store(data, wiki_root=tmp_path / "wiki")


def test_refuses_data_dir_inside_wiki_root(tmp_path):
    root = tmp_path / "wiki"
    root.mkdir()
    for inside in (root, root / "data", root / "a" / "b"):
        with pytest.raises(StoreError, match="inside the instance repository"):
            open_store(inside, wiki_root=root)
    assert not (root / "data").exists()


def test_refusal_uses_container_wiki_root_env(tmp_path, monkeypatch):
    root = tmp_path / "wiki"
    root.mkdir()
    monkeypatch.setenv("CONTAINER_WIKI_ROOT", str(root))
    with pytest.raises(StoreError, match="inside the instance repository"):
        open_store(root / "data")


def test_sibling_with_same_prefix_is_allowed(tmp_path):
    root = tmp_path / "wiki"
    root.mkdir()
    open_store(tmp_path / "wiki-data", wiki_root=root).close()


def test_default_journal_mode_is_wal_and_synchronous_full(tmp_path):
    conn = open_store(tmp_path / "d", wiki_root=tmp_path / "wiki")
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert conn.execute("PRAGMA synchronous").fetchone()[0] == 2  # FULL
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conn.execute("PRAGMA busy_timeout").fetchone()[0] > 0
    conn.close()


def test_journal_mode_delete_from_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("MANIFOLD_STORE_JOURNAL_MODE", "delete")
    conn = open_store(tmp_path / "d", wiki_root=tmp_path / "wiki")
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
    conn.close()


def test_unknown_journal_mode_is_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("MANIFOLD_STORE_JOURNAL_MODE", "memory")
    with pytest.raises(StoreError, match="MANIFOLD_STORE_JOURNAL_MODE"):
        open_store(tmp_path / "d", wiki_root=tmp_path / "wiki")


def test_transaction_commits_and_rolls_back(tmp_path):
    conn = open_store(tmp_path / "d", wiki_root=tmp_path / "wiki")
    with store.transaction(conn):
        conn.execute("INSERT INTO settings(key, value, updated_at) VALUES ('a', '1', 't')")
    with pytest.raises(RuntimeError):
        with store.transaction(conn):
            conn.execute("INSERT INTO settings(key, value, updated_at) VALUES ('b', '2', 't')")
            raise RuntimeError("boom")
    keys = {r[0] for r in conn.execute("SELECT key FROM settings")}
    assert keys == {"a"}
    conn.close()


def test_security_package_imports_only_the_standard_library():
    package = Path(store.__file__).parent
    stdlib = set(sys.stdlib_module_names)
    for path in package.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                assert name in stdlib or name == "manifold_security", "%s imports %s" % (path.name, name)
