# SPDX-License-Identifier: Apache-2.0
"""Credentials: ``mf_<credential_id>_<secret>``.

Only ``sha256(secret)`` is stored.  The full credential is returned once, by
``issue_credential``, and is never stored, logged or exported.
"""

import hashlib
import hmac
import secrets
import sqlite3
from dataclasses import dataclass, field
from typing import Optional

from .store import now_iso, transaction

PREFIX = "mf_"

VALID = "valid"
UNKNOWN = "unknown"
EXPIRED = "expired"
REVOKED = "revoked"


@dataclass(frozen=True)
class IssuedCredential:
    """What ``issue_credential`` returns.  ``secret`` and ``token`` are hidden from ``repr``."""

    credential_id: str
    principal_id: str
    label: str
    expires_at: Optional[str]
    secret: str = field(repr=False)

    @property
    def token(self) -> str:
        """The full credential a client presents.  Show it once."""
        return "%s%s_%s" % (PREFIX, self.credential_id, self.secret)

    def __repr__(self) -> str:
        return "IssuedCredential(credential_id=%r, principal_id=%r, label=%r, expires_at=%r, secret=<hidden>)" % (
            self.credential_id, self.principal_id, self.label, self.expires_at)


@dataclass(frozen=True)
class Verification:
    status: str
    credential_id: Optional[str] = None
    principal_id: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.status == VALID


def _hash(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def parse(presented: str):
    """Split a presented credential into ``(credential_id, secret)``, or ``None`` if malformed."""
    if not isinstance(presented, str) or not presented.startswith(PREFIX):
        return None
    credential_id, sep, secret = presented[len(PREFIX):].partition("_")
    if not sep or not credential_id or not secret:
        return None
    return credential_id, secret


def issue_credential(conn: sqlite3.Connection, principal_id: str, label: str = "",
                     expires_at: Optional[str] = None) -> IssuedCredential:
    """Create a credential for ``principal_id``.  No expiry unless ``expires_at`` (UTC ISO) is given."""
    secret = secrets.token_urlsafe(32)
    credential_id = secrets.token_hex(6)  # hex: contains no underscore, so parsing is unambiguous
    with transaction(conn):
        if conn.execute("SELECT 1 FROM principals WHERE id = ?", (principal_id,)).fetchone() is None:
            raise ValueError("No principal with id %s." % principal_id)
        conn.execute(
            "INSERT INTO credentials(credential_id, principal_id, secret_hash, label, created_at, expires_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (credential_id, principal_id, _hash(secret), label, now_iso(), expires_at),
        )
    return IssuedCredential(credential_id, principal_id, label, expires_at, secret)


def verify(conn: sqlite3.Connection, presented: str, now: Optional[str] = None) -> Verification:
    """Check a presented credential against the store on this call (no cache)."""
    parsed = parse(presented)
    if parsed is None:
        return Verification(UNKNOWN)
    credential_id, secret = parsed
    row = conn.execute(
        "SELECT principal_id, secret_hash, expires_at, revoked_at FROM credentials WHERE credential_id = ?",
        (credential_id,),
    ).fetchone()
    stored = row["secret_hash"] if row is not None else _hash("")
    matches = hmac.compare_digest(stored, _hash(secret))
    if row is None or not matches:
        return Verification(UNKNOWN)
    if row["revoked_at"] is not None:
        return Verification(REVOKED, credential_id, row["principal_id"])
    if row["expires_at"] is not None and row["expires_at"] <= (now or now_iso()):
        return Verification(EXPIRED, credential_id, row["principal_id"])
    return Verification(VALID, credential_id, row["principal_id"])


def revoke_credential(conn: sqlite3.Connection, credential_id: str) -> bool:
    """Revoke one credential.  Returns False when it does not exist or was already revoked."""
    with transaction(conn):
        cur = conn.execute(
            "UPDATE credentials SET revoked_at = ? WHERE credential_id = ? AND revoked_at IS NULL",
            (now_iso(), credential_id),
        )
    return cur.rowcount == 1
