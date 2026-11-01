# SPDX-License-Identifier: Apache-2.0
"""The authentication and administration audit.

Rows are written synchronously (committed before ``record`` returns).  A
presented credential is never an argument of any function here, and any text
that looks like a Manifold credential is redacted before it is stored.
"""

import json
import re
import sqlite3
from dataclasses import dataclass
from typing import Any, List, Optional

from .store import now_iso, transaction

# Event names (free text is allowed, but these are the planned ones).
CREDENTIAL_ISSUED = "credential.issued"
CREDENTIAL_ROTATED = "credential.rotated"
CREDENTIAL_REVOKED = "credential.revoked"
ROLE_CHANGED = "role.changed"
GRANT_CHANGED = "grant.changed"
DENY_CHANGED = "deny.changed"
SETTING_CHANGED = "setting.changed"
AUTHORIZER_REFUSAL = "authorizer.refusal"
SIGNIN_FAILED = "signin.failed"
SIGNIN_THROTTLED = "signin.throttled"
COMPONENT_LIFECYCLE = "component.lifecycle"
STARTUP_NOTICE = "startup.notice"
PRINCIPAL_CHANGED = "principal.changed"
AUTHORITY_CHANGED = "authority.changed"
STORE_EXPORTED = "store.exported"
STORE_IMPORTED = "store.imported"

GENERIC_FAILURE = "authentication failed"

_CREDENTIAL_LIKE = re.compile(r"mf_[A-Za-z0-9]+_[A-Za-z0-9_\-]+")


def host_actor(os_user: str) -> str:
    """The actor recorded for a command run on the host."""
    return "host:%s" % os_user


def _clean(value: Any) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = json.dumps(value, sort_keys=True, default=str)
    return _CREDENTIAL_LIKE.sub("mf_<redacted>", value)


def record(conn: sqlite3.Connection, event: str, actor: str, subject: str = "", detail: Any = "") -> int:
    """Write one audit row and return its id.  Committed when this returns."""
    with transaction(conn):
        cur = conn.execute(
            "INSERT INTO audit(ts, event, actor, subject, detail) VALUES (?, ?, ?, ?, ?)",
            (now_iso(), _clean(event), _clean(actor), _clean(subject), _clean(detail)))
    return cur.lastrowid


def record_failed_signin(conn: sqlite3.Connection, address: str) -> int:
    """A failed sign-in: the address and a generic reason, never the presented credential."""
    return record(conn, SIGNIN_FAILED, "anonymous", address, GENERIC_FAILURE)


@dataclass(frozen=True)
class AuditRow:
    id: int
    ts: str
    event: str
    actor: str
    subject: str
    detail: str


def show(conn: sqlite3.Connection, since: Optional[str] = None, principal: Optional[str] = None,
         event: Optional[str] = None, limit: int = 200) -> List[AuditRow]:
    """Newest first.  ``principal`` matches the actor or the subject; ``event`` matches exactly or as a
    prefix ending in ``.``  (for example ``credential.``)."""
    clauses, params = [], []
    if since:
        clauses.append("ts >= ?")
        params.append(since)
    if principal:
        clauses.append("(actor = ? OR subject = ?)")
        params += [principal, principal]
    if event:
        if event.endswith("."):
            clauses.append("event LIKE ? ESCAPE '\\'")
            params.append(event.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%")
        else:
            clauses.append("event = ?")
            params.append(event)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = conn.execute("SELECT * FROM audit%s ORDER BY id DESC LIMIT ?" % where, params + [int(limit)])
    return [AuditRow(r["id"], r["ts"], r["event"], r["actor"], r["subject"], r["detail"]) for r in rows]
