# SPDX-License-Identifier: Apache-2.0
"""A second open_store in a process must not blind the first (PHASE_1_PLAN T2, found in T27).

Closing any file descriptor on the database drops the process's POSIX locks on it. If open_store did that
while another connection was alive, another process would delete the -wal and -shm files and the first
connection would read a dead snapshot: a revoked credential would stay accepted.
"""

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from manifold_security import principals
from manifold_security.store import open_store

SERVER_DIR = Path(__file__).resolve().parents[1]

WRITER = (
    "import sys; sys.path.insert(0, %r)\n"
    "from manifold_security.store import open_store\n"
    "from manifold_security import principals\n"
    "conn = open_store(sys.argv[1], wiki_root=sys.argv[2])\n"
    "principals.create_principal(conn, sys.argv[3], 'human')\n"
    "conn.close()\n" % str(SERVER_DIR)
)


@pytest.fixture(autouse=True)
def default_journal_mode(monkeypatch):
    monkeypatch.delenv("MANIFOLD_STORE_JOURNAL_MODE", raising=False)  # WAL is the case that matters


def write_from_another_process(data_dir, wiki_root, name):
    done = subprocess.run([sys.executable, "-c", WRITER, str(data_dir), str(wiki_root), name],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


def names(conn):
    return [p.name for p in principals.list_principals(conn)]


def test_a_store_opened_twice_in_one_process_sees_what_another_process_writes(tmp_path):
    data, wiki = tmp_path / "data", tmp_path / "wiki"
    first = open_store(data, wiki_root=wiki)
    second = open_store(data, wiki_root=wiki)  # the call that used to drop the first one's locks
    try:
        assert first.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        for number, name in enumerate(("alice", "bob", "carol"), start=1):
            write_from_another_process(data, wiki, name)
            assert len(names(first)) == number and len(names(second)) == number
    finally:
        first.close()
        second.close()


def test_the_wal_and_shm_files_stay_while_a_connection_is_open(tmp_path):
    data, wiki = tmp_path / "data", tmp_path / "wiki"
    first = open_store(data, wiki_root=wiki)
    second = open_store(data, wiki_root=wiki)
    try:
        write_from_another_process(data, wiki, "alice")
        write_from_another_process(data, wiki, "bob")
        assert (data / "manifold.db-wal").exists() and (data / "manifold.db-shm").exists()
    finally:
        first.close()
        second.close()


def test_opening_an_existing_store_does_not_open_or_close_the_database_file(tmp_path, monkeypatch):
    data, wiki = tmp_path / "data", tmp_path / "wiki"
    open_store(data, wiki_root=wiki).close()
    calls = []
    real_open, real_close = os.open, os.close
    monkeypatch.setattr(os, "open", lambda path, *a, **k: calls.append(("open", str(path))) or real_open(path, *a, **k))
    monkeypatch.setattr(os, "close", lambda fd: calls.append(("close", fd)) or real_close(fd))
    open_store(data, wiki_root=wiki).close()
    assert not [c for c in calls if c[0] == "open" and c[1].endswith("manifold.db")]


def test_a_new_store_is_created_private_and_an_existing_one_is_made_private(tmp_path):
    data, wiki = tmp_path / "data", tmp_path / "wiki"
    open_store(data, wiki_root=wiki).close()
    db = data / "manifold.db"
    assert stat.S_IMODE(db.stat().st_mode) == 0o600
    db.chmod(0o644)
    open_store(data, wiki_root=wiki).close()
    assert stat.S_IMODE(db.stat().st_mode) == 0o600


def test_two_processes_creating_the_store_at_once_both_succeed(tmp_path):
    data, wiki = tmp_path / "data", tmp_path / "wiki"
    processes = [subprocess.Popen([sys.executable, "-c", WRITER, str(data), str(wiki), "user%d" % i],
                                  stderr=subprocess.PIPE, text=True) for i in range(4)]
    for process in processes:
        _, err = process.communicate(timeout=60)
        assert process.returncode == 0, err
    conn = open_store(data, wiki_root=wiki)
    assert sorted(names(conn)) == ["user0", "user1", "user2", "user3"]
    conn.close()
