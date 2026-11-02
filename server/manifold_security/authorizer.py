# SPDX-License-Identifier: Apache-2.0
"""The authorizer: may this principal do this capability on this scope?

``authorize`` reads everything from the database on every call (no cache), so a
revocation, disable, deny or role change committed by any process is seen by the
very next call.  Order of evaluation:

1. the principal exists and is active, and the credential (when given) is valid;
2. a role gives the capability (contributor implies reader; registrar and admin
   imply nothing else; admin holds no data capability);
3. a deny for (principal, scope) refuses;
4. a grant for (principal, scope) allows, when the component's authority allows grants;
5. a ``RepoAuthority`` is asked, when the component's authority allows it (the
   default answers "not available": the repo-write arm belongs to INT-7);
6. refuse.

Capabilities that do not depend on a scope grant (``read``, and the registrar
capabilities) are allowed by the role alone at step 2/3.  Reads ignore denies:
per-component read limits are not part of the first version.
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional

from . import audit, principals as pr
from .store import now_iso

# --- capabilities ---------------------------------------------------------------------

READ = "read"
WRITE = "write"
HANDOFF_CREATE = "handoff.create"
HANDOFF_CONFIRM = "handoff.confirm"
HANDOFF_REJECT = "handoff.reject"
HANDOFF_CLOSE = "handoff.close"
HANDOFF_CLAIM = "handoff.claim"
HANDOFF_REQUEST_REVIEW = "handoff.request_review"
COMPONENT_REGISTER = "component.register"
COMPONENT_UPDATE = "component.update"
COMPONENT_PROTECTED_UPDATE = "component.protected_update"
COMPONENT_ARCHIVE = "component.archive"
COMPONENT_RESTORE = "component.restore"
INGEST = "ingest"

CAPABILITIES = (
    READ, WRITE, HANDOFF_CREATE, HANDOFF_CONFIRM, HANDOFF_REJECT, HANDOFF_CLOSE, HANDOFF_CLAIM,
    HANDOFF_REQUEST_REVIEW, COMPONENT_REGISTER, COMPONENT_UPDATE, COMPONENT_PROTECTED_UPDATE,
    COMPONENT_ARCHIVE, COMPONENT_RESTORE, INGEST,
)

# Capabilities that act on a component's (or _shared) content and so need a grant (or the repo arm).
GRANT_CAPABILITIES = frozenset({
    WRITE, HANDOFF_CREATE, HANDOFF_CONFIRM, HANDOFF_REJECT, HANDOFF_CLOSE, HANDOFF_CLAIM,
    HANDOFF_REQUEST_REVIEW, INGEST,
})
# Capabilities a role gives with no grant (the registrar manages the registry, not the pages).
REGISTRAR_CAPABILITIES = frozenset({
    COMPONENT_REGISTER, COMPONENT_UPDATE, COMPONENT_PROTECTED_UPDATE, COMPONENT_ARCHIVE, COMPONENT_RESTORE,
})

ROLE_CAPABILITIES = {
    "reader": frozenset({READ}),
    "contributor": frozenset({READ}) | GRANT_CAPABILITIES,
    "registrar": REGISTRAR_CAPABILITIES,
    "admin": frozenset(),  # administration happens on the host; admin holds no data capability
}

# --- the tool policy -------------------------------------------------------------------
#
# Every MCP tool (and every ``wiki_handoff_tool`` / ``wiki_component_manage_tool`` action) maps
# to the capability it needs; a tool with no entry is refused.  A plain capability is
# checked by the guard before the tool runs (``read``).  The others depend on the page,
# component or handoff the call names, so the tool asks the guard for that scope itself.
# Nothing here is administrative: credentials, roles, grants and settings are not reachable
# over MCP or HTTP at all (they live in the host command).

AUTHENTICATED = "authenticated"  # any signed-in principal, whatever its roles

TOOL_POLICY = {
    "wiki_ping_tool": AUTHENTICATED,
    "wiki_read_tool": READ,
    "wiki_inventory_tool": READ,
    "wiki_freshness_tool": READ,
    "wiki_onboarding_tool": READ,
    "wiki_reconcile_plan_tool": READ,
    "wiki_bundle_info_tool": READ,
    "wiki_list_helpers_tool": READ,
    "wiki_export_helper_tool": READ,
    "wiki_export_component_helpers_tool": READ,
    "wiki_write_page_tool": WRITE,
    "wiki_log_append_tool": WRITE,
    "wiki_agent_catalog_tool": WRITE,
    "wiki_handoff_tool": {
        "create": HANDOFF_CREATE,
        "confirm": HANDOFF_CONFIRM,
        "reject": HANDOFF_REJECT,
        "close": HANDOFF_CLOSE,
        "claim": HANDOFF_CLAIM,
        "request-review": HANDOFF_REQUEST_REVIEW,
        "list": READ,
    },
    "wiki_register_component_tool": COMPONENT_REGISTER,
    "wiki_component_manage_tool": {
        "update": COMPONENT_UPDATE,
        "archive": COMPONENT_ARCHIVE,
        "restore": COMPONENT_RESTORE,
    },
}

# HTTP routes other than the MCP endpoints.  /health is open (it shows detail to a signed-in caller only).
ROUTE_POLICY = {"/ingest": INGEST, "/docs": READ}

# --- decisions ------------------------------------------------------------------------

VIA_ROLE = "role"
VIA_GRANT = "grant"

NO_PRINCIPAL = "no_such_principal"
PRINCIPAL_INACTIVE = "principal_inactive"
CREDENTIAL_INVALID = "credential_invalid"
UNKNOWN_CAPABILITY = "unknown_capability"
ROLE_MISSING = "role_missing"
HUMAN_REQUIRED = "human_required"
DENIED = "denied"
NO_GRANT = "no_grant"


@dataclass(frozen=True)
class Decision:
    allowed: bool
    via: Optional[str] = None
    reason: Optional[str] = None

    def __bool__(self) -> bool:
        return self.allowed


def allow(via: str) -> Decision:
    return Decision(True, via=via)


def refuse(reason: str) -> Decision:
    return Decision(False, reason=reason)


class RepoAuthority:
    """The repo-write arm of the either-rule.  The default answers "not available"."""

    available = False

    def allows(self, principal: pr.Principal, capability: str, scope: str) -> bool:
        return False


NO_REPO_AUTHORITY = RepoAuthority()


def _credential_ok(conn: sqlite3.Connection, principal_id: str, credential_id: str) -> bool:
    row = conn.execute(
        "SELECT expires_at, revoked_at FROM credentials WHERE credential_id = ? AND principal_id = ?",
        (credential_id, principal_id)).fetchone()
    if row is None or row["revoked_at"] is not None:
        return False
    return row["expires_at"] is None or row["expires_at"] > now_iso()


def _decide(conn, principal_id, capability, scope, credential_id, repo_authority) -> Decision:
    principal = pr.get_principal(conn, principal_id)
    if principal is None or principal.id != principal_id:
        return refuse(NO_PRINCIPAL)
    if not principal.active:
        return refuse(PRINCIPAL_INACTIVE)
    if credential_id is not None and not _credential_ok(conn, principal.id, credential_id):
        return refuse(CREDENTIAL_INVALID)
    if capability not in CAPABILITIES:
        return refuse(UNKNOWN_CAPABILITY)

    roles = set(pr.roles_of(conn, principal.id))
    if not any(capability in ROLE_CAPABILITIES[r] for r in roles):
        return refuse(ROLE_MISSING)
    if capability == COMPONENT_PROTECTED_UPDATE and principal.kind != "human":
        return refuse(HUMAN_REQUIRED)

    if capability == READ:
        return allow(VIA_ROLE)
    if scope in pr.denies_of(conn, principal.id):
        return refuse(DENIED)
    if capability in REGISTRAR_CAPABILITIES:
        return allow(VIA_ROLE)

    authority = pr.get_authority(conn, scope) if scope != pr.SHARED_SCOPE else pr.DEFAULT_AUTHORITY
    if authority in ("grants", "either") and scope in pr.grants_of(conn, principal.id):
        return allow(VIA_GRANT)
    if authority in ("repo-write", "either") and repo_authority.allows(principal, capability, scope):
        return allow("repo-write")
    return refuse(NO_GRANT)


def authorize(conn: sqlite3.Connection, principal_id: str, capability: str, scope: Optional[str] = None,
              credential_id: Optional[str] = None, repo_authority: RepoAuthority = NO_REPO_AUTHORITY,
              record_refusal: bool = True) -> Decision:
    """Decide, from the database as it is now.  A refusal is written to the audit unless told not to."""
    decision = _decide(conn, principal_id, capability, scope, credential_id, repo_authority)
    if not decision.allowed and record_refusal:
        audit.record(conn, audit.AUTHORIZER_REFUSAL, principal_id, scope or "",
                     "%s: %s" % (capability, decision.reason))
    return decision
