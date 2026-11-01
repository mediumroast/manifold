# SPDX-License-Identifier: Apache-2.0
"""The ``admin`` commands: principals, credentials, roles, grants, denies, settings, audit, export.

Each command is a function ``(context, args)`` registered by ``(group, verb)``.  Every change is
written to the audit with the actor ``host:<os user>``.  A credential secret is shown once, on a
terminal or in a file created with mode 0600, and never appears in any log, audit row or later
output.  Standard library only.
"""

import argparse
import datetime
import json
import os
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, TextIO, Tuple

from manifold_security import audit, export, principals, settings, tokens
from manifold_security.store import now_iso


class CliError(Exception):
    """A command failed in a way the person can fix.  The message says how."""


@dataclass
class Context:
    conn: sqlite3.Connection
    actor: str               # host:<os user>
    out: TextIO
    is_tty: bool
    wiki_root: Path

    def say(self, text: str = "") -> None:
        self.out.write(text + "\n")


COMMANDS: Dict[Tuple[str, str], Callable] = {}


def command(group: str, verb: str):
    def register(func):
        COMMANDS[(group, verb)] = func
        return func
    return register


# ── helpers ──────────────────────────────────────────────────────────────────

_DURATION = re.compile(r"^(\d+)([hdw])$")


def parse_time(text: str, future: bool, now: Optional[datetime.datetime] = None) -> str:
    """A UTC time as ``YYYY-MM-DDTHH:MM:SSZ`` from ``30d``/``12h``/``2w`` or an ISO date or date-time."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    match = _DURATION.match(text.strip().lower())
    if match:
        unit = {"h": "hours", "d": "days", "w": "weeks"}[match.group(2)]
        delta = datetime.timedelta(**{unit: int(match.group(1))})
        moment = now + delta if future else now - delta
    else:
        try:
            moment = datetime.datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
        except ValueError:
            raise CliError("%r is not a time. Use 30d, 12h, 2w, a date (2027-01-31) or a date and time "
                           "(2027-01-31T12:00:00Z)." % text)
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=datetime.timezone.utc)
    if future and moment <= now:
        raise CliError("%s is in the past." % text)
    return moment.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_principal(ctx: Context, ref: str) -> principals.Principal:
    principal = principals.get_principal(ctx.conn, ref)
    if principal is None:
        raise CliError("No principal named or numbered %r. List them with: admin principal list." % ref)
    return principal


def find_credential(ctx: Context, credential_id: str) -> sqlite3.Row:
    row = ctx.conn.execute("SELECT * FROM credentials WHERE credential_id = ?", (credential_id,)).fetchone()
    if row is None:
        raise CliError("No credential %r. Find the id with: admin principal show <name>." % credential_id)
    return row


def record(ctx: Context, event: str, subject: str, detail: str) -> None:
    audit.record(ctx.conn, event, ctx.actor, subject, detail)


def working_credentials(ctx: Context, principal_id: str, excluding: str = "") -> list:
    now = now_iso()
    rows = ctx.conn.execute(
        "SELECT credential_id FROM credentials WHERE principal_id = ? AND revoked_at IS NULL"
        " AND (expires_at IS NULL OR expires_at > ?) AND credential_id != ? ORDER BY created_at",
        (principal_id, now, excluding)).fetchall()
    return [r["credential_id"] for r in rows]


def prepare_delivery(ctx: Context, secret_file: Optional[str]):
    """Decide, before a credential is created, where its secret will be shown.  Refuses if it has nowhere safe to go."""
    if secret_file:
        path = Path(secret_file)
        if path.exists():
            raise CliError("%s already exists; give --secret-file a new file name." % path)
        if not path.resolve().parent.is_dir():
            raise CliError("The folder for --secret-file does not exist: %s" % path.resolve().parent)
        return ("file", path)
    if ctx.is_tty:
        return ("tty", None)
    raise CliError("A credential's secret is shown once, on a terminal or in a file made for it. "
                   "This is not a terminal: add --secret-file FILE (it is created with mode 0600).")


def deliver(ctx: Context, delivery, issued: tokens.IssuedCredential) -> None:
    mode, path = delivery
    if mode == "file":
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(issued.token + "\n")
        ctx.say("The secret was written to %s (mode 0600). Move it where the client reads it, then delete the file." % path)
    else:
        ctx.say("Credential (shown once; it cannot be shown again):")
        ctx.say("  " + issued.token)


# ── principals ───────────────────────────────────────────────────────────────

@command("principal", "create")
def principal_create(ctx, a):
    created = principals.create_principal(ctx.conn, a.name, a.kind)
    record(ctx, audit.PRINCIPAL_CHANGED, created.id, "created %s %s" % (a.kind, a.name))
    ctx.say("Created %s %s (id %s)." % (created.kind, created.name, created.id))
    ctx.say("It has no roles and no credential yet: admin role set %s <role>, admin credential issue %s."
            % (created.name, created.name))


@command("principal", "list")
def principal_list(ctx, a):
    for p in principals.list_principals(ctx.conn):
        roles = ",".join(principals.roles_of(ctx.conn, p.id)) or "-"
        ctx.say("%-24s %-8s %-8s %-10s roles: %s" % (p.name, p.kind, "active" if p.active else "DISABLED", p.id, roles))


@command("principal", "show")
def principal_show(ctx, a):
    p = find_principal(ctx, a.principal)
    ctx.say("%s (%s, id %s) %s" % (p.name, p.kind, p.id, "active" if p.active else "DISABLED"))
    ctx.say("  roles:   %s" % (", ".join(principals.roles_of(ctx.conn, p.id)) or "none"))
    ctx.say("  grants:  %s" % (", ".join(principals.grants_of(ctx.conn, p.id)) or "none"))
    ctx.say("  denies:  %s" % (", ".join(principals.denies_of(ctx.conn, p.id)) or "none"))
    ctx.say("  may self-grant on register: %s" % ("yes" if p.may_self_grant_on_register else "no"))
    rows = ctx.conn.execute("SELECT * FROM credentials WHERE principal_id = ? ORDER BY created_at", (p.id,)).fetchall()
    ctx.say("  credentials: %s" % ("none" if not rows else ""))
    for r in rows:
        state = "revoked %s" % r["revoked_at"] if r["revoked_at"] else (
            "expires %s" % r["expires_at"] if r["expires_at"] else "no expiry")
        ctx.say("    %s  %s  created %s  %s" % (r["credential_id"], r["label"] or "-", r["created_at"], state))


@command("principal", "disable")
def principal_disable(ctx, a):
    p = principals.disable_principal(ctx.conn, a.principal)
    working = working_credentials(ctx, p.id)
    record(ctx, audit.PRINCIPAL_CHANGED, p.id, "disabled %s" % p.name)
    ctx.say("Lever used: principal disabled. %s can no longer sign in, whichever of its %d working credential(s) "
            "it presents; the next request is refused. Nothing was deleted: admin principal enable %s restores it."
            % (p.name, len(working), p.name))


@command("principal", "enable")
def principal_enable(ctx, a):
    p = principals.enable_principal(ctx.conn, a.principal)
    record(ctx, audit.PRINCIPAL_CHANGED, p.id, "enabled %s" % p.name)
    ctx.say("Enabled %s. Its roles, grants and unrevoked credentials apply again." % p.name)


# ── credentials ──────────────────────────────────────────────────────────────

@command("credential", "issue")
def credential_issue(ctx, a):
    p = find_principal(ctx, a.principal)
    expires = parse_time(a.expires, future=True) if a.expires else None
    delivery = prepare_delivery(ctx, a.secret_file)
    issued = tokens.issue_credential(ctx.conn, p.id, a.label or "", expires)
    try:
        deliver(ctx, delivery, issued)
    except OSError as exc:
        tokens.revoke_credential(ctx.conn, issued.credential_id)
        raise CliError("The secret could not be written (%s); the new credential was revoked." % exc)
    record(ctx, audit.CREDENTIAL_ISSUED, p.id, "credential %s%s" % (issued.credential_id,
                                                                      " expires " + expires if expires else ""))
    ctx.say("Issued credential %s to %s (%s)." % (issued.credential_id, p.name, "expires " + expires if expires else "no expiry"))


@command("credential", "rotate")
def credential_rotate(ctx, a):
    old = find_credential(ctx, a.credential_id)
    if old["revoked_at"]:
        raise CliError("Credential %s is already revoked; issue a new one instead." % a.credential_id)
    p = find_principal(ctx, old["principal_id"])
    expires = parse_time(a.expires, future=True) if a.expires else None
    delivery = prepare_delivery(ctx, a.secret_file)
    issued = tokens.issue_credential(ctx.conn, p.id, old["label"], expires)
    try:
        deliver(ctx, delivery, issued)
    except OSError as exc:
        tokens.revoke_credential(ctx.conn, issued.credential_id)
        raise CliError("The secret could not be written (%s); nothing was rotated." % exc)
    tokens.revoke_credential(ctx.conn, old["credential_id"])
    record(ctx, audit.CREDENTIAL_ROTATED, p.id, "credential %s replaced by %s" % (old["credential_id"], issued.credential_id))
    ctx.say("Rotated: %s is revoked and %s replaces it for %s." % (old["credential_id"], issued.credential_id, p.name))


@command("credential", "revoke")
def credential_revoke(ctx, a):
    row = find_credential(ctx, a.credential_id)
    p = find_principal(ctx, row["principal_id"])
    if not tokens.revoke_credential(ctx.conn, row["credential_id"]):
        raise CliError("Credential %s was already revoked." % a.credential_id)
    record(ctx, audit.CREDENTIAL_REVOKED, p.id, "credential %s" % row["credential_id"])
    others = working_credentials(ctx, p.id)
    ctx.say("Lever used: credential revoked. Credential %s of %s is refused from its next request." % (row["credential_id"], p.name))
    if others:
        ctx.say("%s still has %d working credential(s): %s. To end all access: admin principal disable %s."
                % (p.name, len(others), ", ".join(others), p.name))
    else:
        ctx.say("%s has no other working credential." % p.name)


# ── roles ────────────────────────────────────────────────────────────────────

@command("role", "set")
def role_set(ctx, a):
    principals.set_role(ctx.conn, a.principal, a.role)
    p = find_principal(ctx, a.principal)
    record(ctx, audit.ROLE_CHANGED, p.id, "set %s" % a.role)
    ctx.say("%s now has the role %s (roles: %s)." % (p.name, a.role, ", ".join(principals.roles_of(ctx.conn, p.id))))


@command("role", "unset")
def role_unset(ctx, a):
    p = find_principal(ctx, a.principal)
    if not principals.unset_role(ctx.conn, a.principal, a.role):
        raise CliError("%s does not have the role %s." % (p.name, a.role))
    record(ctx, audit.ROLE_CHANGED, p.id, "unset %s" % a.role)
    remaining = principals.roles_of(ctx.conn, p.id)
    ctx.say("Removed the role %s from %s (roles left: %s)." % (a.role, p.name, ", ".join(remaining) or "none"))


# ── grants, denies, authority, flags ─────────────────────────────────────────

@command("grant", "add")
def grant_add(ctx, a):
    principals.add_grant(ctx.conn, a.principal, a.scope)
    p = find_principal(ctx, a.principal)
    record(ctx, audit.GRANT_CHANGED, p.id, "grant added on %s" % a.scope)
    ctx.say("%s may now write to %s (with a contributor role)." % (p.name, a.scope))


@command("grant", "remove")
def grant_remove(ctx, a):
    p = find_principal(ctx, a.principal)
    if not principals.remove_grant(ctx.conn, a.principal, a.scope):
        raise CliError("%s has no grant on %s." % (p.name, a.scope))
    record(ctx, audit.GRANT_CHANGED, p.id, "grant removed on %s" % a.scope)
    roles = principals.roles_of(ctx.conn, p.id)
    authority = principals.get_authority(ctx.conn, a.scope) if a.scope != principals.SHARED_SCOPE else "either"
    ctx.say("Removed the grant on %s from %s. Routes that still give access:" % (a.scope, p.name))
    ctx.say("  - reading: the role(s) %s give read access to every page; reads are not limited per component."
            % (", ".join(r for r in roles if r in ("reader", "contributor")) or "(none: no reader or contributor role)"))
    if authority in ("repo-write", "either"):
        ctx.say("  - writing through the repository (authority %s): not available in this version, so it gives nothing yet." % authority)
    ctx.say("  - writing through a grant: none left on %s." % a.scope)
    ctx.say("To end writing and reading altogether: admin deny add %s %s (writes), or admin principal disable %s (everything)."
            % (p.name, a.scope, p.name))


@command("deny", "add")
def deny_add(ctx, a):
    principals.add_deny(ctx.conn, a.principal, a.scope)
    p = find_principal(ctx, a.principal)
    record(ctx, audit.DENY_CHANGED, p.id, "deny added on %s" % a.scope)
    ctx.say("%s is denied writes to %s whatever grants or roles it holds. Reads are not limited per component; "
            "to stop all access: admin principal disable %s." % (p.name, a.scope, p.name))


@command("deny", "remove")
def deny_remove(ctx, a):
    p = find_principal(ctx, a.principal)
    if not principals.remove_deny(ctx.conn, a.principal, a.scope):
        raise CliError("%s has no deny on %s." % (p.name, a.scope))
    record(ctx, audit.DENY_CHANGED, p.id, "deny removed on %s" % a.scope)
    ctx.say("Removed the deny on %s for %s. Its grants and roles apply there again." % (a.scope, p.name))


@command("authority", "set")
def authority_set(ctx, a):
    principals.set_authority(ctx.conn, a.component, a.authority)
    record(ctx, audit.AUTHORITY_CHANGED, a.component, "authority %s" % a.authority)
    ctx.say("Write authority of %s is now %s." % (a.component, a.authority))


@command("registrar-flag", "set")
def registrar_flag_set(ctx, a):
    p = find_principal(ctx, a.principal)
    principals.set_may_self_grant(ctx.conn, a.principal, a.self_grant == "on")
    record(ctx, audit.PRINCIPAL_CHANGED, p.id, "self-grant on register %s" % a.self_grant)
    ctx.say("%s %s receive a grant on a component it registers." % (p.name, "will" if a.self_grant == "on" else "will not"))


# ── settings ─────────────────────────────────────────────────────────────────

@command("settings", "list")
def settings_list(ctx, a):
    for key, spec in settings.SPECS.items():
        value = settings.get(ctx.conn, key)
        shown = ",".join(value) if isinstance(value, list) else value
        ctx.say("%-30s %-24s %s" % (key, shown if shown != "" else "(empty)", spec.doc))


@command("settings", "get")
def settings_get(ctx, a):
    value = settings.get(ctx.conn, a.key)
    ctx.say(",".join(value) if isinstance(value, list) else str(value))


@command("settings", "set")
def settings_set(ctx, a):
    value = settings.set_value(ctx.conn, a.key, a.value)
    record(ctx, audit.SETTING_CHANGED, a.key, "set to %s" % (",".join(value) if isinstance(value, list) else value))
    ctx.say("%s is now %s." % (a.key, ",".join(value) if isinstance(value, list) else value))


@command("settings", "unset")
def settings_unset(ctx, a):
    settings.unset(ctx.conn, a.key)
    record(ctx, audit.SETTING_CHANGED, a.key, "returned to the default")
    ctx.say("%s is back to its default (%s)." % (a.key, settings.SPECS[a.key].default))


# ── audit, export, import ────────────────────────────────────────────────────

@command("audit", "show")
def audit_show(ctx, a):
    ref = None
    if a.principal:
        found = principals.get_principal(ctx.conn, a.principal)
        ref = found.id if found else a.principal
    since = parse_time(a.since, future=False) if a.since else None
    rows = audit.show(ctx.conn, since=since, principal=ref, event=a.event, limit=a.limit)
    for r in rows:
        ctx.say("%s  %-22s actor=%s subject=%s  %s" % (r.ts, r.event, r.actor, r.subject or "-", r.detail))
    if not rows:
        ctx.say("No audit rows match.")


@command("export", "")
def export_command(ctx, a):
    data = export.export_store(ctx.conn, with_hashes=a.with_hashes)
    path = Path(a.file)
    if path.exists():
        raise CliError("%s already exists; give a new file name." % path)
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.write(export.dumps(data))
    record(ctx, audit.STORE_EXPORTED, str(path), "hashes included" if a.with_hashes else "no credentials")
    ctx.say("Exported %d principal(s) to %s (mode 0600)%s." % (
        len(data["principals"]), path,
        "; credential hashes are included, keep the file as private as the database" if a.with_hashes
        else "; no credentials or hashes are in it"))


@command("import", "")
def import_command(ctx, a):
    try:
        data = json.loads(Path(a.file).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CliError("Cannot read %s as JSON: %s" % (a.file, exc))
    mode = export.REPLACE if a.replace else (export.MERGE if a.merge else "")
    try:
        counts = export.import_store(ctx.conn, data, mode=mode, dry_run=a.dry_run)
    except export.ExportError as exc:
        raise CliError(str(exc))
    summary = ", ".join("%s %d" % (k.replace("_", " "), v) for k, v in counts.items() if v)
    if a.dry_run:
        ctx.say("Dry run, nothing changed. It would apply: %s." % (summary or "nothing"))
    else:
        record(ctx, audit.STORE_IMPORTED, a.file, "%s: %s" % (mode or "into an empty store", summary))
        ctx.say("Imported: %s." % (summary or "nothing"))


# ── the registry purge (see purge.py) ────────────────────────────────────────

@command("registry", "purge")
def registry_purge(ctx, a):
    from . import purge
    purge.run(ctx, a)


# ── the parser ───────────────────────────────────────────────────────────────

def add_parsers(sub: argparse._SubParsersAction) -> None:
    """Add the ``admin`` groups to ``sub`` (the subparsers of the ``admin`` command)."""
    def group(name, help_text):
        parser = sub.add_parser(name, help=help_text)
        return parser.add_subparsers(dest="verb", metavar="VERB", required=True)

    g = group("principal", "people, agents and services")
    p = g.add_parser("create", help="create a principal")
    p.add_argument("name")
    p.add_argument("--kind", choices=principals.KINDS, default="human")
    g.add_parser("list", help="list principals")
    for verb in ("show", "disable", "enable"):
        g.add_parser(verb, help="%s a principal" % verb).add_argument("principal")

    g = group("credential", "issue, rotate and revoke credentials")
    for verb in ("issue", "rotate"):
        p = g.add_parser(verb, help="%s a credential" % verb)
        p.add_argument("principal" if verb == "issue" else "credential_id")
        if verb == "issue":
            p.add_argument("--label", default="")
        p.add_argument("--expires", help="30d, 12h, 2w, a date or a date and time; none by default")
        p.add_argument("--secret-file", help="write the secret to this new file (mode 0600) instead of the terminal")
    g.add_parser("revoke", help="revoke one credential").add_argument("credential_id")

    g = group("role", "roles")
    for verb in ("set", "unset"):
        p = g.add_parser(verb, help="%s a role" % verb)
        p.add_argument("principal")
        p.add_argument("role", choices=principals.ROLES)

    for name in ("grant", "deny"):
        g = group(name, "%ss on a component or _shared" % name)
        for verb in ("add", "remove"):
            p = g.add_parser(verb, help="%s a %s" % (verb, name))
            p.add_argument("principal")
            p.add_argument("scope", help="a component slug or _shared")

    g = group("authority", "who may write to a component")
    p = g.add_parser("set", help="set the write authority of a component")
    p.add_argument("component")
    p.add_argument("authority", choices=principals.AUTHORITIES)

    g = group("registrar-flag", "registrar options")
    p = g.add_parser("set", help="whether a registration gives the registrar a grant on the new component")
    p.add_argument("principal")
    p.add_argument("--self-grant", choices=("on", "off"), required=True)

    g = group("settings", "limits and options, all with defaults")
    g.add_parser("list", help="list settings")
    g.add_parser("get", help="show one setting").add_argument("key")
    p = g.add_parser("set", help="change a setting")
    p.add_argument("key")
    p.add_argument("value")
    g.add_parser("unset", help="return a setting to its default").add_argument("key")

    g = group("audit", "the audit trail")
    p = g.add_parser("show", help="show audit rows, newest first")
    p.add_argument("--since", help="30d, 12h, a date or a date and time")
    p.add_argument("--principal", help="a principal name or id (as actor or subject)")
    p.add_argument("--event", help="an event, or a prefix ending in a dot (credential.)")
    p.add_argument("--limit", type=int, default=50)

    p = sub.add_parser("export", help="write the principals, roles, grants, authority and settings to a JSON file")
    p.add_argument("file")
    p.add_argument("--with-hashes", action="store_true", help="include credential hashes (never secrets)")
    p.set_defaults(verb="")
    p = sub.add_parser("import", help="read an export")
    p.add_argument("file")
    p.add_argument("--dry-run", action="store_true")
    flag = p.add_mutually_exclusive_group()
    flag.add_argument("--merge", action="store_true", help="add to what the store already holds")
    flag.add_argument("--replace", action="store_true", help="replace what the store holds")
    p.set_defaults(verb="")

    g = group("registry", "the component registry")
    p = g.add_parser("purge", help="remove an archived component for good (after its hold period)")
    p.add_argument("slug")
    p.add_argument("--confirm-slug", default="", help="type the slug again to confirm")
