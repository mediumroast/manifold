# SPDX-License-Identifier: Apache-2.0
"""Principals, roles, grants, denies, per-component authority and component state.

Every mutation runs in ``BEGIN IMMEDIATE`` and has committed when the function
returns, so another connection (or process) sees it on its next read.
"""

import datetime
import re
import secrets
import sqlite3
from dataclasses import dataclass
from typing import List, Optional

from .store import now_iso, transaction

KINDS = ("human", "agent", "service")
ROLES = ("reader", "contributor", "registrar", "admin")
AUTHORITIES = ("grants", "repo-write", "either")
DEFAULT_AUTHORITY = "either"
SHARED_SCOPE = "_shared"  # the page scope that belongs to no component; no valid slug can equal it

# Same rule as wiki_backend.config (a test keeps the two in step); duplicated because this
# package must not import the server.
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
_MAX_SLUG = 64
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._@ -]{0,63}$")


class PrincipalError(ValueError):
    """A principal operation is not allowed.  The message says why."""


@dataclass(frozen=True)
class Principal:
    id: str
    name: str
    kind: str
    active: bool
    may_self_grant_on_register: bool
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Principal":
        return cls(row["id"], row["name"], row["kind"], bool(row["active"]),
                   bool(row["may_self_grant_on_register"]), row["created_at"])


def is_slug(value: object) -> bool:
    return isinstance(value, str) and len(value) <= _MAX_SLUG and bool(_SLUG_RE.match(value))


def check_scope(scope: str, allow_shared: bool = True) -> str:
    if scope == SHARED_SCOPE and allow_shared:
        return scope
    if scope == SHARED_SCOPE:
        raise PrincipalError("%s is reserved and is not a component slug." % SHARED_SCOPE)
    if not is_slug(scope):
        raise PrincipalError(
            "%r is not a component slug (lowercase letters and digits with single . _ - between; "
            "at most %d characters) or %s." % (scope, _MAX_SLUG, SHARED_SCOPE))
    return scope


def _require(conn: sqlite3.Connection, ref: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM principals WHERE id = ? OR name = ?", (ref, ref)).fetchone()
    if row is None:
        raise PrincipalError("No principal named or numbered %r." % ref)
    return row


def get_principal(conn: sqlite3.Connection, ref: str) -> Optional[Principal]:
    """Look a principal up by id or name; ``None`` if there is none."""
    row = conn.execute("SELECT * FROM principals WHERE id = ? OR name = ?", (ref, ref)).fetchone()
    return Principal.from_row(row) if row else None


def list_principals(conn: sqlite3.Connection) -> List[Principal]:
    return [Principal.from_row(r) for r in conn.execute("SELECT * FROM principals ORDER BY name")]


def count_principals(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM principals").fetchone()[0]


def create_principal(conn: sqlite3.Connection, name: str, kind: str) -> Principal:
    if kind not in KINDS:
        raise PrincipalError("kind must be one of: %s (got %r)." % (", ".join(KINDS), kind))
    if not isinstance(name, str) or not _NAME_RE.match(name):
        raise PrincipalError(
            "name must be 1 to 64 characters: letters, digits, space and . _ @ - , starting with a letter or digit.")
    pid = "p_" + secrets.token_hex(6)
    try:
        with transaction(conn):
            conn.execute("INSERT INTO principals(id, name, kind, created_at) VALUES (?, ?, ?, ?)",
                         (pid, name, kind, now_iso()))
    except sqlite3.IntegrityError:
        raise PrincipalError("A principal named %r already exists." % name) from None
    return get_principal(conn, pid)


def _set_active(conn: sqlite3.Connection, ref: str, active: bool) -> Principal:
    row = _require(conn, ref)
    with transaction(conn):
        conn.execute("UPDATE principals SET active = ?, disabled_at = ? WHERE id = ?",
                     (1 if active else 0, None if active else now_iso(), row["id"]))
    return get_principal(conn, row["id"])


def disable_principal(conn: sqlite3.Connection, ref: str) -> Principal:
    return _set_active(conn, ref, False)


def enable_principal(conn: sqlite3.Connection, ref: str) -> Principal:
    return _set_active(conn, ref, True)


def set_role(conn: sqlite3.Connection, ref: str, role: str) -> None:
    if role not in ROLES:
        raise PrincipalError("role must be one of: %s (got %r)." % (", ".join(ROLES), role))
    row = _require(conn, ref)
    if role == "admin" and row["kind"] != "human":
        raise PrincipalError(
            "The admin role is for people only; %s is a%s %s principal." % (
                row["name"], "n" if row["kind"] == "agent" else "", row["kind"]))
    with transaction(conn):
        conn.execute("INSERT OR IGNORE INTO roles(principal_id, role) VALUES (?, ?)", (row["id"], role))


def unset_role(conn: sqlite3.Connection, ref: str, role: str) -> bool:
    row = _require(conn, ref)
    with transaction(conn):
        cur = conn.execute("DELETE FROM roles WHERE principal_id = ? AND role = ?", (row["id"], role))
    return cur.rowcount == 1


def roles_of(conn: sqlite3.Connection, principal_id: str) -> List[str]:
    return [r[0] for r in conn.execute(
        "SELECT role FROM roles WHERE principal_id = ? ORDER BY role", (principal_id,))]


def _add_scope_row(conn, table: str, ref: str, scope: str) -> None:
    check_scope(scope)
    row = _require(conn, ref)
    with transaction(conn):
        conn.execute("INSERT OR IGNORE INTO %s(principal_id, scope, created_at) VALUES (?, ?, ?)" % table,
                     (row["id"], scope, now_iso()))


def _remove_scope_row(conn, table: str, ref: str, scope: str) -> bool:
    row = _require(conn, ref)
    with transaction(conn):
        cur = conn.execute("DELETE FROM %s WHERE principal_id = ? AND scope = ?" % table, (row["id"], scope))
    return cur.rowcount == 1


def add_grant(conn: sqlite3.Connection, ref: str, scope: str) -> None:
    _add_scope_row(conn, "grants", ref, scope)


def remove_grant(conn: sqlite3.Connection, ref: str, scope: str) -> bool:
    return _remove_scope_row(conn, "grants", ref, scope)


def add_deny(conn: sqlite3.Connection, ref: str, scope: str) -> None:
    _add_scope_row(conn, "denies", ref, scope)


def remove_deny(conn: sqlite3.Connection, ref: str, scope: str) -> bool:
    return _remove_scope_row(conn, "denies", ref, scope)


def grants_of(conn: sqlite3.Connection, principal_id: str) -> List[str]:
    return [r[0] for r in conn.execute(
        "SELECT scope FROM grants WHERE principal_id = ? ORDER BY scope", (principal_id,))]


def denies_of(conn: sqlite3.Connection, principal_id: str) -> List[str]:
    return [r[0] for r in conn.execute(
        "SELECT scope FROM denies WHERE principal_id = ? ORDER BY scope", (principal_id,))]


def set_may_self_grant(conn: sqlite3.Connection, ref: str, enabled: bool) -> None:
    row = _require(conn, ref)
    with transaction(conn):
        conn.execute("UPDATE principals SET may_self_grant_on_register = ? WHERE id = ?",
                     (1 if enabled else 0, row["id"]))


# --- per-component authority and lifecycle state -------------------------------------------

def set_authority(conn: sqlite3.Connection, slug: str, authority: str) -> None:
    check_scope(slug, allow_shared=False)
    if authority not in AUTHORITIES:
        raise PrincipalError("authority must be one of: %s (got %r)." % (", ".join(AUTHORITIES), authority))
    with transaction(conn):
        conn.execute(
            "INSERT INTO component_state(slug, authority) VALUES (?, ?)"
            " ON CONFLICT(slug) DO UPDATE SET authority = excluded.authority", (slug, authority))


def get_authority(conn: sqlite3.Connection, slug: str) -> str:
    row = conn.execute("SELECT authority FROM component_state WHERE slug = ?", (slug,)).fetchone()
    return row["authority"] if row else DEFAULT_AUTHORITY


@dataclass(frozen=True)
class ComponentState:
    slug: str
    authority: str
    state: str
    reason: str
    archived_at: Optional[str]
    purge_after: Optional[str]

    @property
    def archived(self) -> bool:
        return self.state == "archived"


def get_component_state(conn: sqlite3.Connection, slug: str) -> ComponentState:
    row = conn.execute("SELECT * FROM component_state WHERE slug = ?", (slug,)).fetchone()
    if row is None:
        return ComponentState(slug, DEFAULT_AUTHORITY, "active", "", None, None)
    return ComponentState(row["slug"], row["authority"], row["state"], row["reason"],
                          row["archived_at"], row["purge_after"])


def archive_component(conn: sqlite3.Connection, slug: str, reason: str, hold_days: int) -> ComponentState:
    check_scope(slug, allow_shared=False)
    if not isinstance(reason, str) or not reason.strip():
        raise PrincipalError("A reason is required to archive a component.")
    archived_at = datetime.datetime.now(datetime.timezone.utc)
    purge_after = (archived_at + datetime.timedelta(days=hold_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    with transaction(conn):
        conn.execute(
            "INSERT INTO component_state(slug, state, reason, archived_at, purge_after)"
            " VALUES (?, 'archived', ?, ?, ?)"
            " ON CONFLICT(slug) DO UPDATE SET state = 'archived', reason = excluded.reason,"
            " archived_at = excluded.archived_at, purge_after = excluded.purge_after",
            (slug, reason.strip(), archived_at.strftime("%Y-%m-%dT%H:%M:%SZ"), purge_after))
    return get_component_state(conn, slug)


def restore_component(conn: sqlite3.Connection, slug: str) -> ComponentState:
    check_scope(slug, allow_shared=False)
    with transaction(conn):
        conn.execute(
            "UPDATE component_state SET state = 'active', reason = '', archived_at = NULL, purge_after = NULL"
            " WHERE slug = ?", (slug,))
    return get_component_state(conn, slug)
