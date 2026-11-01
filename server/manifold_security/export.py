# SPDX-License-Identifier: Apache-2.0
"""One portable JSON export of the security store, and the import that reads it back.

The export holds principals (with roles, grants and denies), the per-component authority and the
settings.  It never holds a credential secret.  Credential hashes are written only when asked
for (``with_hashes``), for moving the store to another host without re-issuing credentials; keep
such a file as private as the database itself.  The audit and the usage counters are not exported.

``import_store`` validates everything before it changes anything (the whole import is one
transaction), refuses to overwrite a store that already has principals unless told to merge or
replace, and can run as a dry run.  Standard library only.
"""

import json
import sqlite3
from typing import Any, Dict, List

from . import principals as pr
from . import settings
from .store import now_iso

FORMAT = "manifold-security-export"
VERSION = 1
MERGE = "merge"
REPLACE = "replace"


class ExportError(ValueError):
    """The export file cannot be used.  The message says why."""


def export_store(conn: sqlite3.Connection, with_hashes: bool = False) -> Dict[str, Any]:
    """The store as a JSON-ready dict.  No secret is ever included; hashes only with ``with_hashes``."""
    principal_rows = conn.execute("SELECT * FROM principals ORDER BY name").fetchall()
    result: Dict[str, Any] = {
        "format": FORMAT,
        "version": VERSION,
        "exported_at": now_iso(),
        "includes_hashes": bool(with_hashes),
        "principals": [],
        "component_authority": {},
        "settings": {},
    }
    for row in principal_rows:
        pid = row["id"]
        result["principals"].append({
            "id": pid,
            "name": row["name"],
            "kind": row["kind"],
            "active": bool(row["active"]),
            "may_self_grant_on_register": bool(row["may_self_grant_on_register"]),
            "created_at": row["created_at"],
            "roles": sorted(pr.roles_of(conn, pid)),
            "grants": sorted(pr.grants_of(conn, pid)),
            "denies": sorted(pr.denies_of(conn, pid)),
        })
    for row in conn.execute("SELECT slug, authority FROM component_state ORDER BY slug"):
        result["component_authority"][row["slug"]] = row["authority"]
    for row in conn.execute("SELECT key, value FROM settings ORDER BY key"):
        result["settings"][row["key"]] = row["value"]
    if with_hashes:
        result["credentials"] = [
            {key: row[key] for key in ("credential_id", "principal_id", "secret_hash", "label", "created_at",
                                        "expires_at", "revoked_at")}
            for row in conn.execute("SELECT * FROM credentials ORDER BY credential_id")]
    return result


def dumps(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _list_of_str(value: Any, what: str) -> List[str]:
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ExportError("%s must be a list of text values." % what)
    return value


def validate(data: Any) -> None:
    """Check the shape and every value; raises :class:`ExportError`.  Does not touch the store."""
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        raise ExportError("This is not a Manifold security export (format %r expected)." % FORMAT)
    if data.get("version") != VERSION:
        raise ExportError("Export version %r is not supported; this Manifold reads version %d."
                          % (data.get("version"), VERSION))
    seen_names, seen_ids = set(), set()
    entries = data.get("principals")
    if not isinstance(entries, list):
        raise ExportError("principals must be a list.")
    for entry in entries:
        if not isinstance(entry, dict):
            raise ExportError("Each principal must be an object.")
        name, pid, kind = entry.get("name"), entry.get("id"), entry.get("kind")
        if not isinstance(name, str) or not name or not isinstance(pid, str) or not pid:
            raise ExportError("Each principal needs an id and a name.")
        if name in seen_names or pid in seen_ids:
            raise ExportError("Principal %r appears twice." % name)
        seen_names.add(name)
        seen_ids.add(pid)
        if kind not in pr.KINDS:
            raise ExportError("Principal %r has kind %r; use one of: %s." % (name, kind, ", ".join(pr.KINDS)))
        for role in _list_of_str(entry.get("roles", []), "roles of %s" % name):
            if role not in pr.ROLES:
                raise ExportError("Principal %r has unknown role %r." % (name, role))
            if role == "admin" and kind != "human":
                raise ExportError("Principal %r is %s and cannot hold the admin role." % (name, kind))
        for key in ("grants", "denies"):
            for scope in _list_of_str(entry.get(key, []), "%s of %s" % (key, name)):
                try:
                    pr.check_scope(scope)
                except pr.PrincipalError as exc:
                    raise ExportError("Principal %r: %s" % (name, exc))
    authority = data.get("component_authority", {})
    if not isinstance(authority, dict):
        raise ExportError("component_authority must be an object.")
    for slug, value in authority.items():
        if not pr.is_slug(slug) or value not in pr.AUTHORITIES:
            raise ExportError("component_authority %r: %r is not valid." % (slug, value))
    values = data.get("settings", {})
    if not isinstance(values, dict):
        raise ExportError("settings must be an object.")
    for key, raw in values.items():
        try:
            settings.parse(key, raw)
        except settings.SettingError as exc:
            raise ExportError(str(exc))
    for credential in data.get("credentials", []) or []:
        if not isinstance(credential, dict) or credential.get("principal_id") not in seen_ids \
                or not all(isinstance(credential.get(k), str) and credential.get(k)
                           for k in ("credential_id", "secret_hash")):
            raise ExportError("A credential entry is malformed or names an unknown principal.")


def import_store(conn: sqlite3.Connection, data: Any, mode: str = "", dry_run: bool = False) -> Dict[str, int]:
    """
    Load an export.  ``mode`` is ``"merge"`` or ``"replace"``; without one the store must hold no
    principal yet.  Returns counts of what was (or, in a dry run, would be) changed.
    """
    validate(data)
    if mode not in ("", MERGE, REPLACE):
        raise ExportError("mode must be merge or replace.")
    counts = {"principals_added": 0, "principals_existing": 0, "roles": 0, "grants": 0, "denies": 0,
              "authority": 0, "settings": 0, "credentials": 0}
    conn.execute("BEGIN IMMEDIATE")
    try:
        existing = pr.count_principals(conn)
        if existing and not mode:
            raise ExportError("The store already holds %d principal(s). Use --merge to add to it or --replace to "
                              "replace it (add --dry-run to see the effect first)." % existing)
        if mode == REPLACE:
            for table in ("credentials", "roles", "grants", "denies", "principals", "settings"):
                conn.execute("DELETE FROM %s" % table)
            conn.execute("UPDATE component_state SET authority = ?", (pr.DEFAULT_AUTHORITY,))
        ids: Dict[str, str] = {}  # id in the file -> id in the store
        for entry in data["principals"]:
            row = conn.execute("SELECT id, kind FROM principals WHERE name = ?", (entry["name"],)).fetchone()
            if row is not None:
                if row["kind"] != entry["kind"]:
                    raise ExportError("Principal %r exists as %s but the file says %s."
                                      % (entry["name"], row["kind"], entry["kind"]))
                ids[entry["id"]] = row["id"]
                counts["principals_existing"] += 1
            else:
                if conn.execute("SELECT 1 FROM principals WHERE id = ?", (entry["id"],)).fetchone():
                    raise ExportError("Id %r is used by a different principal in the store." % entry["id"])
                conn.execute(
                    "INSERT INTO principals(id, name, kind, active, may_self_grant_on_register, created_at, disabled_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (entry["id"], entry["name"], entry["kind"], int(bool(entry.get("active", True))),
                     int(bool(entry.get("may_self_grant_on_register", False))),
                     entry.get("created_at") or now_iso(), None if entry.get("active", True) else now_iso()))
                ids[entry["id"]] = entry["id"]
                counts["principals_added"] += 1
            target = ids[entry["id"]]
            for role in entry.get("roles", []):
                counts["roles"] += conn.execute(
                    "INSERT OR IGNORE INTO roles(principal_id, role) VALUES (?, ?)", (target, role)).rowcount
            for table, key in (("grants", "grants"), ("denies", "denies")):
                for scope in entry.get(key, []):
                    counts[key] += conn.execute(
                        "INSERT OR IGNORE INTO %s(principal_id, scope, created_at) VALUES (?, ?, ?)" % table,
                        (target, scope, now_iso())).rowcount
        for slug, value in data.get("component_authority", {}).items():
            conn.execute("INSERT INTO component_state(slug, authority) VALUES (?, ?)"
                         " ON CONFLICT(slug) DO UPDATE SET authority = excluded.authority", (slug, value))
            counts["authority"] += 1
        for key, raw in data.get("settings", {}).items():
            conn.execute("INSERT INTO settings(key, value, updated_at) VALUES (?, ?, ?)"
                         " ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                         (key, raw if isinstance(raw, str) else ",".join(raw), now_iso()))
            counts["settings"] += 1
        for credential in data.get("credentials", []) or []:
            counts["credentials"] += conn.execute(
                "INSERT OR IGNORE INTO credentials(credential_id, principal_id, secret_hash, label, created_at,"
                " expires_at, revoked_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (credential["credential_id"], ids[credential["principal_id"]], credential["secret_hash"],
                 credential.get("label") or "", credential.get("created_at") or now_iso(),
                 credential.get("expires_at"), credential.get("revoked_at"))).rowcount
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    conn.execute("ROLLBACK" if dry_run else "COMMIT")
    return counts
