# SPDX-License-Identifier: Apache-2.0
"""The security store: one SQLite file outside the instance repository.

``open_store(data_dir)`` creates the folder (mode 0700) and ``manifold.db``
(mode 0600), applies the numbered migrations in ``migrations/`` and returns a
connection in autocommit mode, so callers open transactions explicitly with
``transaction()``.  Standard library only: the host command shares this
package with the server.

One connection per process, and no stray descriptors: a process should hold at
most one connection to the store, and nothing in it may ``open()`` or
``os.open()`` and then close the database file while a connection is alive.
Closing any descriptor on a file releases all of the process's POSIX locks on
it; another process then deletes the WAL files and this one reads a stale
snapshot forever (see PHASE_1_PLAN T2).  ``open_store`` itself touches the file
only when it does not exist yet, and a second ``open_store`` in a process is
safe for that reason, but share the connection rather than open more.
"""

import contextlib
import datetime
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Iterator, Optional

DB_NAME = "manifold.db"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"
JOURNAL_MODES = ("wal", "delete")
DEFAULT_WIKI_ROOT = "/workspace"

_MIGRATION_RE = re.compile(r"^(\d{4})_[a-z0-9_]+\.sql$")


def now_iso() -> str:
    """Current UTC time as ``YYYY-MM-DDTHH:MM:SSZ`` (sorts as text)."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class StoreError(Exception):
    """The store cannot be opened.  The message says how to fix it."""


def _migrations() -> list:
    found = []
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        match = _MIGRATION_RE.match(path.name)
        if not match:
            raise StoreError("Migration file %s is not named NNNN_name.sql." % path.name)
        found.append((int(match.group(1)), path))
    return found


def latest_version() -> int:
    """The schema version this code writes."""
    migrations = _migrations()
    return migrations[-1][0] if migrations else 0


def _inside(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def _journal_mode(explicit: Optional[str]) -> str:
    mode = (explicit or os.getenv("MANIFOLD_STORE_JOURNAL_MODE") or "wal").strip().lower()
    if mode not in JOURNAL_MODES:
        raise StoreError(
            "MANIFOLD_STORE_JOURNAL_MODE is %r; use one of: %s." % (mode, ", ".join(JOURNAL_MODES))
        )
    return mode


def _apply_migrations(conn: sqlite3.Connection) -> None:
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    migrations = _migrations()
    newest = migrations[-1][0] if migrations else 0
    if current > newest:
        raise StoreError(
            "The security database is schema version %d but this Manifold only understands up to %d. "
            "Upgrade Manifold; do not open the database with an older version." % (current, newest)
        )
    for version, path in migrations:
        if version <= current:
            continue
        script = path.read_text(encoding="utf-8")
        # executescript() commits first, so the transaction is part of the script.
        try:
            conn.executescript("BEGIN IMMEDIATE;\n%s\nPRAGMA user_version = %d;\nCOMMIT;" % (script, version))
        except sqlite3.Error as exc:
            if conn.in_transaction:
                conn.execute("ROLLBACK")
            # Two processes starting on a new store at once both read version 0; the second then waits for the
            # first and runs the script again. If the other one got there, this migration is simply done.
            if conn.execute("PRAGMA user_version").fetchone()[0] >= version:
                continue
            raise StoreError("Migration %s failed: %s" % (path.name, exc)) from exc


def open_store(data_dir, wiki_root=None, journal_mode: Optional[str] = None,
               check_same_thread: bool = True) -> sqlite3.Connection:
    """Open (creating if needed) the store in ``data_dir`` and return a connection.

    ``wiki_root`` defaults to ``CONTAINER_WIKI_ROOT`` (or ``/workspace``); a
    ``data_dir`` inside it is refused, so the database can never be committed
    to the instance repository.
    """
    mode = _journal_mode(journal_mode)
    folder = Path(data_dir).expanduser().resolve()
    root = Path(wiki_root or os.getenv("CONTAINER_WIKI_ROOT") or DEFAULT_WIKI_ROOT).expanduser().resolve()
    if _inside(folder, root):
        raise StoreError(
            "The data folder %s is inside the instance repository %s. "
            "Set MANIFOLD_DATA_DIR to a folder outside it." % (folder, root)
        )
    try:
        folder.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(folder, 0o700)
        db_path = folder / DB_NAME
        # Create the file with 0600 before SQLite does; the -wal and -shm files copy its mode.
        # Only when it is missing: closing ANY file descriptor on the database drops every POSIX lock this
        # process holds on it, SQLite's included. Another process would then see no other user, delete the
        # -wal and -shm files, and this process would read a dead snapshot for good (revocations unseen).
        # While the file is missing no connection can exist, so this one open and close is safe.
        if not db_path.exists():
            try:
                os.close(os.open(str(db_path), os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600))
            except FileExistsError:
                pass  # another process created it a moment ago
        os.chmod(db_path, 0o600)  # by path: touches no descriptor and no lock
    except OSError as exc:
        raise StoreError("Cannot prepare the data folder %s: %s" % (folder, exc)) from exc
    try:
        conn = sqlite3.connect(str(db_path), timeout=10, isolation_level=None, check_same_thread=check_same_thread)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("PRAGMA foreign_keys = ON")
        actual = conn.execute("PRAGMA journal_mode").fetchone()[0].lower()
        for attempt in range(100):  # switching the mode needs a lock the busy timeout does not wait for
            if actual == mode:
                break
            try:
                actual = conn.execute("PRAGMA journal_mode = %s" % mode).fetchone()[0].lower()
            except sqlite3.OperationalError as exc:
                if "locked" not in str(exc) or attempt == 99:
                    raise
                time.sleep(0.1)
                actual = conn.execute("PRAGMA journal_mode").fetchone()[0].lower()
        if actual != mode:
            raise StoreError(
                "SQLite would not enter %s journal mode in %s (it reported %s). "
                "Try MANIFOLD_STORE_JOURNAL_MODE=delete." % (mode, folder, actual)
            )
        conn.execute("PRAGMA synchronous = FULL")
        _apply_migrations(conn)
    except sqlite3.Error as exc:
        raise StoreError("Cannot open the security database in %s: %s" % (folder, exc)) from exc
    return conn


@contextlib.contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """``BEGIN IMMEDIATE`` ... commit; rolls back and re-raises on any error."""
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")
