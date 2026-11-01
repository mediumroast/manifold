# SPDX-License-Identifier: Apache-2.0
"""Wiki MCP server using FastMCP with HTTP/SSE transport."""

import json
import os
from pathlib import Path
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.http import RequestContextMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.responses import RedirectResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from wiki_backend.models import (
    WikiWriteRequest,
    WikiLogRequest,
    WikiRegisterRequest,
)
from wiki_backend.read import wiki_read
from wiki_backend.write import wiki_write_page, protected_field_change
from wiki_backend.log import wiki_log_append
from wiki_backend.inventory import wiki_inventory
from wiki_backend.register import (
    wiki_register_component, wiki_update_component, update_sidebar_handoff, update_sidebar_handoff_status,
)
from wiki_backend.freshness import wiki_freshness
from wiki_backend.onboarding import wiki_onboarding_protocol, wiki_onboarding_preflight, wiki_reconcile_plan
from wiki_backend.ping import wiki_ping
from wiki_backend.config import ConfigError, DEFAULT_SERVER_NAME, load_config, registered_slugs, valid_slug
from wiki_backend.actor import acting_var
from wiki_backend.health import wiki_health
from wiki_backend.web import VENDOR_URL, instance_shell, render_shell, vendor_dir
from wiki_backend.auth import PrincipalAuthMiddleware, StoreAccess
from wiki_backend.guard import Guard, Refused, RoutePolicyMiddleware
from manifold_security import audit, authorizer, limits, principals, scopes, settings as security_settings
from manifold_security.context import caller_from_scope, current_caller_var
from manifold_security.store import StoreError
from wiki_backend.bundles import wiki_bundle_info
from wiki_backend.ingest import (
    wiki_ingest_doc, classify_doc_type, read_body_capped, max_ingest_bytes, BodyTooLarge,
)
from wiki_backend.helpers import wiki_export_helper, wiki_list_helpers, wiki_export_all_helpers
from wiki_backend.agent_guide import wiki_agent_guide
from wiki_backend.handoff import (
    handoff_create, handoff_claim, handoff_close, handoff_list,
    handoff_request_review, handoff_confirm, handoff_reject, handoff_parties, open_handoffs_of,
)


# Repo root — wiki pages live at WIKI_ROOT/wiki/...
WIKI_ROOT = Path(os.getenv("CONTAINER_WIKI_ROOT", "/workspace"))


@asynccontextmanager
async def lifespan(app):
    """Startup and shutdown lifecycle."""
    # Startup
    if not WIKI_ROOT.exists():
        raise RuntimeError(f"Wiki root does not exist: {WIKI_ROOT}")
    yield
    # Shutdown


# Create FastMCP app
def _server_name() -> str:
    """The MCP server name from manifold.yaml, or the default if the file is missing or invalid."""
    try:
        return load_config(WIKI_ROOT).server_name
    except ConfigError:
        return DEFAULT_SERVER_NAME


app = FastMCP(_server_name(), lifespan=lifespan)

_store_access = StoreAccess()


def current_caller():
    """
    The authenticated caller of the tool call being served, or None.

    Reads the scope of the HTTP request that carried the call (``get_http_request``), which is
    the POST for both /mcp and /messages/ (SSE); falls back to the context variable the
    middleware sets.
    """
    try:
        from fastmcp.server.dependencies import get_http_request
        caller = caller_from_scope(get_http_request().scope)
        if caller is not None:
            return caller
    except RuntimeError:
        pass
    return current_caller_var.get()


# Every tool is wrapped by guard.guarded (under @app.tool()); a tool with no entry in
# authorizer.TOOL_POLICY is refused.  Tools that depend on a page, component or handoff call
# guard.require(capability, scope) themselves before they change anything.
guard = Guard(_store_access, current_caller)


@app.tool()
@guard.guarded
def wiki_ping_tool() -> dict:
    """
    Verify connectivity to the wiki MCP server and return the list of available
    tools. Call this as the first step of any session — especially when working
    from a component repo — to confirm the native MCP connection is live before
    performing any wiki operations.

    Calling this tool successfully proves that native MCP wrappers are working.
    No curl or protocol-level diagnostics are needed.
    """
    caller = current_caller()
    return wiki_ping(WIKI_ROOT, principal=caller.as_dict() if caller else None)


def _slug_scope(value: str) -> str:
    """A component slug as a scope, or a ValueError saying what is wrong with it."""
    try:
        return principals.check_scope((value or "").strip().lower(), allow_shared=False)
    except principals.PrincipalError as exc:
        raise ValueError(str(exc))


def _authorize_handoff(action: str, source: str, target: str, path: str):
    """
    Authorize a handoff action on the right component: the source for create, confirm,
    reject and close; the target for claim and request-review; ``read`` for list.

    Returns None when allowed, or an error dict (a refusal, or a problem with the arguments).
    An unknown action is left to the tool, which names the valid ones.
    """
    capability = authorizer.TOOL_POLICY["wiki_handoff_tool"].get(action)
    if capability is None:
        return None
    try:
        if capability == authorizer.READ:
            guard.require(capability)
        elif action == "create":
            source_slug, target_slug = _slug_scope(source), _slug_scope(target)
            guard.require(capability, source_slug)
            guard.require_active(source_slug)
            guard.require_active(target_slug)
        else:
            if not path:
                return {"error": "action=%r requires path." % action}
            source_slug, target_slug = handoff_parties(WIKI_ROOT, path)
            side = target_slug if action in ("claim", "request-review") else source_slug
            guard.require(capability, side)
    except ValueError as exc:
        return {"error": str(exc)}
    except Refused as exc:
        return exc.as_dict()
    return None


@app.tool()
@guard.guarded
def wiki_handoff_tool(
    action: str,
    source: str = "",
    target: str = "",
    type: str = "",
    priority: str = "medium",
    title: str = "",
    summary: str = "",
    what_needs_to_happen: str = "",
    technical_details: str = "",
    path: str = "",
    resolution: str = "",
    notes: str = "",
    status_filter: str = "",
) -> dict:
    """
    Manage the full handoff lifecycle in one tool.

    action="create"         — Post a new handoff from source to target component.
                              Required: source, target, type, priority, title, summary,
                              what_needs_to_happen. Optional: technical_details.
                              Returns: path, id, next step.

    action="claim"          — Claim an open handoff and mark it in-progress.
                              Required: path. Returns: summary and what_needs_to_happen.

    action="close"          — Mark a handoff completed. Only the SOURCE component (the one that
                              asked for the work) can close; the target never does. With
                              no review step, the target calls request-review and the
                              source then confirms.
                              Required: path, resolution.
                              Returns: confirmation and prompt to update component page.

    action="request-review" — Submit implementation for source review (target calls this).
                              Required: path, notes (what was implemented).
                              Sets status → needs-review (◑).

    action="confirm"        — Confirm the target's implementation (source calls this).
                              Required: path. Optional: notes (confirmation message).
                              Sets status → completed (✓).

    action="reject"         — Reject the implementation and send it back (source calls this).
                              Required: path, notes (feedback describing what needs to change).
                              Sets status → in-progress (◉), appends feedback to ## Blockers.

    action="list"           — List handoffs. Optional: target (slug), source (slug),
                              status_filter (open | in-progress | needs-review |
                              completed | blocked).

    Valid types: feature | bug | breaking-change | integration-spec
    Valid priorities: critical | high | medium | low
    """
    refusal = _authorize_handoff(action, source, target, path)
    if refusal is not None:
        return refusal
    if action == "create":
        return handoff_create(
            WIKI_ROOT, source, target, type, priority,
            title, summary, what_needs_to_happen, technical_details,
        )
    elif action == "claim":
        return handoff_claim(WIKI_ROOT, path)
    elif action == "close":
        return handoff_close(WIKI_ROOT, path, resolution)
    elif action == "request-review":
        if not path:
            return {"error": "action='request-review' requires path."}
        if not notes:
            return {"error": "action='request-review' requires notes describing what was implemented."}
        return handoff_request_review(WIKI_ROOT, path, notes)
    elif action == "confirm":
        if not path:
            return {"error": "action='confirm' requires path."}
        return handoff_confirm(WIKI_ROOT, path, notes)
    elif action == "reject":
        if not path:
            return {"error": "action='reject' requires path."}
        if not notes:
            return {"error": "action='reject' requires notes (feedback for the target)."}
        return handoff_reject(WIKI_ROOT, path, notes)
    elif action == "list":
        return handoff_list(WIKI_ROOT, target or None, status_filter or None)
    else:
        return {"error": f"Unknown action '{action}'. Valid: create | claim | close | request-review | confirm | reject | list"}


@app.tool()
@guard.guarded
def wiki_read_tool(path: str) -> dict:
    """
    Read a wiki page.
    
    Returns body, frontmatter, links, and etag for optimistic concurrency.
    
    Args:
        path: Path to wiki page relative to wiki root (e.g., "wiki/components/acme-web.md")
    """
    try:
        response = wiki_read(WIKI_ROOT, path)
        return {
            "path": response.path,
            "body": response.body,
            "frontmatter": response.frontmatter,
            "etag": response.etag,
            "links": response.links
        }
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_write_page_tool(path: str, content: str, etag: str = None, message: str = "") -> dict:
    """
    Create or update a wiki page with etag-based conflict detection.
    
    For creates: omit etag parameter
    For updates: provide current etag to ensure no concurrent modifications
    
    Args:
        path: Path to wiki page relative to wiki root
        content: Full page content (including frontmatter if updating)
        etag: Current etag for optimistic concurrency (None for create)
        message: Commit message describing the change
    """
    # Authorize on the scope of the page: a component's pages need a write grant on that
    # component, other wiki pages need one on _shared.  Handoff, log and system pages are not
    # writable here at all.
    try:
        kind, scope = scopes.classify(WIKI_ROOT, path)
    except scopes.PathRefused as exc:
        return {"path": path, "status": "error", "error": "Write refused: %s" % exc}
    if kind not in (scopes.COMPONENT, scopes.SHARED):
        return {"path": path, "status": "error",
                "error": "Write refused: %s is a %s page and cannot be written with this tool." % (path, kind)}
    guard.require(authorizer.WRITE, scope)
    if kind == scopes.COMPONENT:
        guard.require_active(scope)
        existing = WIKI_ROOT / path
        if etag is not None and existing.is_file():
            changed = protected_field_change(existing.read_text(encoding="utf-8"), content)
            if changed:
                return {"path": path, "status": "error",
                        "error": "Refused: the %s of a component page changes only through "
                                 "wiki_component_manage_tool (a human registrar)." % changed}
    try:
        request = WikiWriteRequest(
            path=path,
            content=content,
            etag=etag,
            message=message
        )
        response = wiki_write_page(WIKI_ROOT, request)

        return {
            "path": response.path,
            "status": response.status,
            "etag": response.etag,
            "error": response.error
        }
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_log_append_tool(action: str, message: str, component: str = None) -> dict:
    """
    Append an entry to the operation log (wiki/log.md).
    
    Never truncates or rewrites existing log entries. Always appends.
    
    Args:
        action: Action type (e.g., "register", "handoff_post", "task_complete")
        message: Detailed message describing the action
        component: Optional component name involved in the action
    """
    # The entry is a write about one component (or about _shared when none is named).
    try:
        scope = _slug_scope(component) if component else principals.SHARED_SCOPE
    except ValueError as exc:
        return {"error": str(exc)}
    guard.require(authorizer.WRITE, scope)
    if component:
        guard.require_active(scope)
    try:
        request = WikiLogRequest(
            action=action,
            message=message,
            component=component
        )
        response = wiki_log_append(WIKI_ROOT, request)
        return response
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_inventory_tool() -> dict:
    """
    Get a complete inventory of the wiki graph.
    
    Returns components, handoffs, and all files in the wiki.
    """
    try:
        response = wiki_inventory(WIKI_ROOT, _store_access.use(principals.archived_components))
        return {
            "components": [c.dict() for c in response.components],
            "handoffs": [h.dict() for h in response.handoffs],
            "all_files": response.all_files
        }
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_register_component_tool(
    name: str,
    description: str,
    repo: str,
    owner: str,
    source_docs: list = None,
    inline_docs: dict = None,
    skip_source_docs: bool = False,
    reconcile: bool = False,
) -> dict:
    """
    Register a new component in the wiki, or reconcile an existing page from raw docs.

    Creates wiki/components/{slug}.md with the frontmatter and section
    structure required by wiki/CLAUDE.md.

    Call wiki_onboarding_tool(component=name) first to check what already
    exists and get the recommended approach.

    Only name, description, repo, and owner are required. All doc parameters
    are optional — architecture and API sections will be stubs if not provided.

    Args:
        name: Component slug (alphanumeric with hyphens, e.g. "acme-api")
        description: One-sentence description (under 200 chars)
        repo: Full repository URL
        owner: Responsible team or person name
        source_docs: Paths to markdown files already in the manifold repo
                     (relative to repo root). E.g. ["raw/acme-api/readme.md"].
        inline_docs: Content passed directly — use when docs live in the
                     component's own repo. Keys are doc types or filenames:
                       {"readme": "<full content of README.md>",
                        "architecture": "<content if available>"}
                     Valid type keys: "readme", "architecture", "api".
                     The agent should read the file with its file tool, then
                     pass the content here. No file copying needed.
        skip_source_docs: True = register with stub sections immediately.
                          Use when the human wants to fill in docs later.
        reconcile: True = update an already-registered component page from raw docs.
                   Rebuilds Overview, Architecture, API contract, and Sources sections
                   from the provided source_docs or inline_docs. Hand-edited sections
                   (Integration points, Known issues, Deployment, Changelog) are
                   preserved. Requires source_docs or inline_docs to be provided.
                   Use when wiki_onboarding_tool returns status "reconcile_available".
    """
    guard.require(authorizer.COMPONENT_REGISTER)
    caller = guard.caller()
    slug = (name or "").strip().lower()
    try:
        entry = next((c for c in load_config(WIKI_ROOT).components if c.slug == slug), None)
    except ConfigError as exc:
        return {"error": str(exc)}
    page_exists = (WIKI_ROOT / "wiki" / "components" / ("%s.md" % slug)).exists() if valid_slug(slug) else False
    # Reconciling, or naming a repository or owner other than the registry's, changes the mapping
    # from a component to its repository: that is for a human registrar only.
    changes_mapping = bool(entry and ((entry.repo and entry.repo != repo) or (entry.owner and entry.owner != owner)))
    if reconcile or changes_mapping:
        guard.require(authorizer.COMPONENT_PROTECTED_UPDATE)
    counted = valid_slug(slug) and not page_exists and not reconcile
    if counted:
        try:
            _store_access.use(lambda conn: limits.consume(conn, caller.principal_id, caller.kind, limits.REGISTRATIONS))
        except limits.LimitReached as exc:
            return {"error": str(exc), "refused": True, "reason": "limit"}
    registered = False
    try:
        request = WikiRegisterRequest(
            name=name,
            description=description,
            repo=repo,
            owner=owner,
            source_docs=source_docs or [],
            inline_docs=inline_docs or {},
            skip_source_docs=skip_source_docs,
            reconcile=reconcile,
        )
        response = wiki_register_component(WIKI_ROOT, request)
        registered = response.status == "created"
        result = {
            "name": response.name,
            "path": response.path,
            "status": response.status,
            "message": response.message,
            "etag": response.etag,
        }
        if response.status == "already_registered":
            result["do_not_retry"] = True
            result["suggested_next_steps"] = [
                f"wiki_freshness_tool(component='{response.name}') — check if page is stale",
                f"wiki_read_tool(path='{response.path}') — read current content",
                "wiki_write_page_tool(...) + wiki_log_append_tool(...) — update if stale",
            ]
        # Registration and reconcile write their own log entry, attributed to the principal.
        if registered:
            result["self_granted"] = _self_grant(caller.principal_id, response.name)
            wiki_log_append(WIKI_ROOT, WikiLogRequest(
                action="register", component=response.name, message=f"Registered component: {description}"))
        elif response.status == "reconciled":
            wiki_log_append(WIKI_ROOT, WikiLogRequest(
                action="reconcile-component", component=response.name, message="Page reconciled from raw docs"))
        return result
    except Exception as e:
        return {"error": str(e)}
    finally:
        if counted and not registered:
            _store_access.use(lambda conn: limits.refund(conn, caller.principal_id, limits.REGISTRATIONS))


def _self_grant(principal_id: str, slug: str) -> bool:
    """A new registration gives its registrar no grant, unless an administrator set the self-grant flag."""
    def grant(conn):
        principal = principals.get_principal(conn, principal_id)
        if principal is None or not principal.may_self_grant_on_register:
            return False
        principals.add_grant(conn, principal_id, slug)
        audit.record(conn, audit.GRANT_CHANGED, principal_id, slug, "grant added on registration (self-grant flag)")
        return True
    return _store_access.use(grant)


@app.tool()
@guard.guarded
def wiki_component_manage_tool(
    action: str,
    name: str,
    reason: str = "",
    description: str = "",
    repo: str = "",
    owner: str = "",
) -> dict:
    """
    Update, archive or restore a registered component. For registrars.

    action="update"  — Change the description (any registrar) and/or the repository and
                       owner (a human registrar only; an agent registrar cannot).
                       Required: name, and at least one of description, repo, owner.

    action="archive" — Take a component out of use. An archived component refuses page
                       writes, new handoffs and document ingest until it is restored, and
                       is held for the purge period before the host can remove it for good
                       (there is no purge over MCP).
                       Required: name, reason. Refused while a handoff that involves the
                       component is not completed; the refusal names the handoffs.

    action="restore" — Bring an archived component back into use. Required: name.
    """
    capability = authorizer.TOOL_POLICY["wiki_component_manage_tool"].get(action)
    if capability is None:
        return {"error": "Unknown action %r. Valid: update | archive | restore" % action}
    try:
        slug = _slug_scope(name)
        if slug not in registered_slugs(WIKI_ROOT):
            return {"error": "%s is not a registered component." % slug}
    except (ValueError, ConfigError) as exc:
        return {"error": str(exc)}
    guard.require(capability, slug)
    caller = guard.caller()

    if action == "update":
        if not (description or repo or owner):
            return {"error": "action='update' needs at least one of description, repo, owner."}
        if repo or owner:
            guard.require(authorizer.COMPONENT_PROTECTED_UPDATE, slug)
        result = wiki_update_component(WIKI_ROOT, slug, description=description or None,
                                       repo=repo or None, owner=owner or None)
        if result.get("status") == "updated":
            _store_access.use(lambda conn: audit.record(
                conn, audit.COMPONENT_LIFECYCLE, caller.principal_id, slug, "update: " + ", ".join(result["changed"])))
            wiki_log_append(WIKI_ROOT, WikiLogRequest(
                action="update-component", component=slug, message="Updated " + ", ".join(result["changed"])))
        return result

    state = _store_access.use(lambda conn: principals.get_component_state(conn, slug))
    if action == "restore":
        if not state.archived:
            return {"error": "%s is not archived." % slug}
        _store_access.use(lambda conn: principals.restore_component(conn, slug))
        _store_access.use(lambda conn: audit.record(conn, audit.COMPONENT_LIFECYCLE, caller.principal_id, slug, "restore"))
        wiki_log_append(WIKI_ROOT, WikiLogRequest(action="restore-component", component=slug,
                                                  message="Component restored"))
        return {"status": "restored", "name": slug}

    # archive
    if not reason.strip():
        return {"error": "action='archive' needs a reason."}
    if state.archived:
        return {"error": "%s is already archived (reason: %s)." % (slug, state.reason)}
    open_pages = open_handoffs_of(WIKI_ROOT, slug)
    if open_pages:
        return {"error": "Cannot archive %s while handoffs involving it are not completed. Complete or "
                         "reject them first: %s" % (slug, ", ".join(open_pages)),
                "open_handoffs": open_pages}
    try:
        _store_access.use(lambda conn: limits.consume(conn, caller.principal_id, caller.kind, limits.ARCHIVES))
    except limits.LimitReached as exc:
        return {"error": str(exc), "refused": True, "reason": "limit"}
    try:
        hold_days = _store_access.use(lambda conn: security_settings.get(conn, "purge_hold_days"))
        archived = _store_access.use(lambda conn: principals.archive_component(conn, slug, reason, hold_days))
    except Exception:
        _store_access.use(lambda conn: limits.refund(conn, caller.principal_id, limits.ARCHIVES))
        raise
    _store_access.use(lambda conn: audit.record(
        conn, audit.COMPONENT_LIFECYCLE, caller.principal_id, slug, "archive: " + reason.strip()))
    wiki_log_append(WIKI_ROOT, WikiLogRequest(action="archive-component", component=slug,
                                              message="Component archived: " + reason.strip()))
    return {"status": "archived", "name": slug, "purge_after": archived.purge_after}


@app.tool()
@guard.guarded
def wiki_freshness_tool(component: str = None) -> dict:
    """
    Check which component wiki pages are stale relative to their raw source docs.

    Compares the last_updated frontmatter date on each wiki/components/{slug}.md
    against the dates of files in raw/{slug}/ and raw/shared/. Returns three lists:
    - stale: components whose wiki page is older than one or more raw docs
    - fresh: components whose wiki page is up to date
    - unknown: components that could not be checked (missing page or frontmatter)

    Args:
        component: Optional component slug to check only one component.
                   If omitted, all known components are checked.
    """
    try:
        result = wiki_freshness(WIKI_ROOT, component)
        return result
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_onboarding_tool(component: str = None, verbose: bool = False) -> dict:
    """
    Return onboarding instructions for registering a new component.

    Default (no args): returns a short sequential checklist — the minimum
    needed to start. Follow the steps in order; call this tool with
    component= to get the pre-flight scan before registering.

    With component="slug": scans raw/{component}/ and returns what docs
    exist, what is missing, and the options to present to the human.

    With verbose=True: also includes the full protocol reference (handoff
    lifecycle, raw doc taxonomy, agent bundle, maintenance duties). Only
    request this if you need the detail — the default is intentionally brief.

    Args:
        component: Component slug to pre-flight check (e.g. "acme-api").
        verbose: If True, include full protocol reference in the response.
    """
    try:
        # Always return the concise checklist
        result = {
            "steps": [
                "1. Call wiki_onboarding_tool(component='your-slug') to check existing state",
                "2. Review preflight.options and ask the human which option they prefer",
                "3. Call wiki_register_component_tool(name, description, repo, owner, [source_docs or skip_source_docs])",
                "4. Call wiki_freshness_tool(component='your-slug')",
                "5. Call wiki_inventory_tool() to confirm registration",
                "6. Call wiki_bundle_info_tool() and install the agent bundle in the component repository",
                "7. Call wiki_export_component_helpers_tool() and write the helper files into the component repository",
            ],
            "register_args": {
                "required": ["name", "description", "repo", "owner"],
                "optional": {
                    "source_docs": "List of raw doc paths to embed (e.g. ['raw/acme-api/2026-05-24-acme-api-readme.md'])",
                    "skip_source_docs": "True = register with stubs now, add docs later",
                },
            },
            "hint": "Call wiki_onboarding_tool(component='your-slug') first to see what already exists.",
        }

        if component:
            preflight = wiki_onboarding_preflight(WIKI_ROOT, component)
            result["preflight"] = preflight

            if preflight.get("status") == "already_registered":
                # Hard stop — return ONLY the stop signal, nothing else.
                # A minimal response gives the model fewer things to act on.
                return {
                    "status": "already_registered",
                    "terminal": True,
                    "do_not_call_again": True,
                    "action_required": preflight["action_required"],
                    "message_to_user": preflight["message_to_user"],
                    "do_not_call": preflight["do_not_call"],
                    "wiki_page": preflight["wiki_page"],
                }
            else:
                # Override hint with the preflight next_step
                result["hint"] = preflight.get("next_step", result["hint"])

        if verbose:
            result["full_protocol"] = wiki_onboarding_protocol()

        return result
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_reconcile_plan_tool(component: str, repo: str = None) -> dict:
    """
    Inspect what is recorded for a registered component and return a ready-to-execute action plan.

    Runs the onboarding preflight automatically and reads the existing component page,
    then returns:
    - status_audit: what is present vs. missing (wiki page, raw docs, published agents)
    - discovered: values taken from the existing page (description, owner)
    - action_plan: concrete, sequenced tool calls with the discovered values filled in
    - required_inputs: values the caller must still supply (only the repository URL)

    If required_inputs is empty, every tool_call in action_plan is ready to execute
    without further editing. When no agents are published for the component, the plan
    ends with the steps that install the agent bundle in the component repository.

    Args:
        component: Component slug, e.g. "acme-api"
        repo: Repository URL, e.g. "https://github.com/acme/acme-api".
              Required for the reconcile call; if omitted it is listed in required_inputs.
    """
    try:
        return wiki_reconcile_plan(WIKI_ROOT, component=component, repo=repo)
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_agent_catalog_tool(component: str) -> dict:
    """
    Publish a component's agents to the wiki: create or update
    wiki/guides/agents/{component}.md from the agent files in raw/{component}/agents/,
    and add the guide link to the sidebar if absent.

    The agents themselves are installed in the component repository by the agent
    bundle (see wiki_bundle_info_tool). This tool records what is installed so that
    people and other agents can find it in the wiki browser. Copy the component's
    agent files into raw/{component}/agents/ first. It is idempotent: safe to re-run
    after agents are added or updated.

    Args:
        component: Component slug, e.g. "acme-web"
    """
    try:
        scope = _slug_scope(component)
    except ValueError as exc:
        return {"error": str(exc)}
    guard.require(authorizer.WRITE, scope)
    guard.require_active(scope)
    try:
        return wiki_agent_guide(WIKI_ROOT, component)
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_bundle_info_tool() -> dict:
    """
    List the agent bundles this server carries and how to install one in a component repository.

    A bundle is a set of role agents, rules and document templates with a deterministic
    installer. Returns each bundle's name and version (with the archive and its SHA-256
    when the server holds the ZIP) and the install steps. Use this instead of describing
    or copying agent files by hand.
    """
    try:
        return wiki_bundle_info()
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_list_helpers_tool() -> dict:
    """
    List all helper scripts that can be exported into a component repo.

    Returns each helper's name, description, target output_path, and usage
    string. Call this to discover what tools are available before calling
    wiki_export_helper_tool.
    """
    try:
        return wiki_list_helpers(WIKI_ROOT)
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_export_helper_tool(name: str, server_url: str = "") -> dict:
    """
    Export a helper script for installation into a component repo.

    Returns content, output_path and notes. The agent writes content to output_path in the component repo.

    This is Step 0 of component onboarding. Installing ingest_doc in the
    component repo means future doc updates can be pushed to the wiki
    directly from that repo without referencing the manifold repo.

    Available helpers (call wiki_list_helpers_tool to see all):
    - ingest_doc: push local doc files into the manifold wiki via POST /ingest.

    Args:
        name:       Helper name, e.g. "ingest_doc"
        server_url: Override the default MCP server URL baked into the script
                    (default: http://127.0.0.1:8686). Use 127.0.0.1 not
                    localhost — Docker on macOS binds as IPv6 dual-stack and
                    localhost resolves to ::1 in some sandboxed contexts.
    """
    try:
        return wiki_export_helper(WIKI_ROOT, name, server_url)
    except Exception as e:
        return {"error": str(e)}


@app.tool()
@guard.guarded
def wiki_export_component_helpers_tool() -> dict:
    """
    Export all manifold helper files in one call for installation into a
    component repo. Returns content and output_path for every registered
    helper: handoff slash commands (create/pickup/close) for both Copilot
    and Claude Code, plus the manifold-update command for future self-updates.

    For each file in the response:
      - Write content to output_path in the component repo
      - Commit all files together

    Use this during onboarding (step 9) and whenever /manifold-update is run.
    """
    try:
        return wiki_export_all_helpers(WIKI_ROOT)
    except Exception as e:
        return {"error": str(e)}


def _ingest_as(caller, component, doc_type, content, filename):
    """Run the ingest attributed to the authenticated caller (the commit names the principal)."""
    token = acting_var.set(caller)
    try:
        return wiki_ingest_doc(WIKI_ROOT, component, doc_type, content, filename)
    finally:
        acting_var.reset(token)


# Doc ingest endpoint — called by tools/ingest_doc.py running on the host.
# Accepts raw document content and writes it into raw/{component}/ inside
# the mounted manifold repo.  The agent never reads or transmits file bytes;
# it just passes the resulting path to wiki_register_component_tool.
@app.custom_route("/ingest", methods=["POST"])
async def ingest_doc(request: Request):
    """
    POST /ingest — write a source doc into raw/{component}/.

    Body (JSON):
        component   str   required  — component slug, e.g. "acme-api"
        doc_type    str   required  — readme | architecture | api | other
                                      (omit to auto-detect from filename)
        content     str   required  — full text of the document
        filename    str   optional  — override auto-generated filename

    Returns:
        200  {"status": "ok",    "path": "raw/...", "bytes": N, ...}
        400  {"status": "error", "message": "..."}
    """
    limit = max_ingest_bytes() + 4096  # JSON framing around the document
    try:
        raw = await read_body_capped(request.stream(), request.headers.get("content-length"), limit)
    except BodyTooLarge:
        return JSONResponse({"status": "error", "message": "request body is too large"}, status_code=413)
    try:
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("body must be a JSON object")
    except Exception:
        return JSONResponse({"status": "error", "message": "invalid JSON body"}, status_code=400)

    component = (body.get("component") or "").strip()
    content   = body.get("content") or ""
    filename  = body.get("filename") or None

    # doc_type: explicit or auto-detected from filename
    doc_type = (body.get("doc_type") or "").strip().lower()
    if not doc_type and filename:
        doc_type = classify_doc_type(filename)
    if not doc_type:
        doc_type = "other"

    if not component:
        return JSONResponse({"status": "error", "message": "component is required"}, status_code=400)
    if not content:
        return JSONResponse({"status": "error", "message": "content is required"}, status_code=400)

    # Authorization: the caller needs a grant on the component (raw/shared maps to _shared). Only a
    # registrar may ingest for a slug that is not registered yet (the first documents of a new
    # component). An archived component takes no documents.
    caller = caller_from_scope(request.scope)
    if caller is None:  # the middleware guarantees a caller; never ingest without one
        return JSONResponse({"status": "error", "message": "authentication required"}, status_code=401)
    slug = component.lower()
    if valid_slug(slug):
        token = acting_var.set(caller)
        try:
            if slug == "shared":
                guard.require(authorizer.INGEST, principals.SHARED_SCOPE)
            elif slug in registered_slugs(WIKI_ROOT):
                guard.require(authorizer.INGEST, slug)
                guard.require_active(slug)
            elif not guard.has_role("registrar"):
                raise Refused("Refused: %s is not a registered component; only a registrar can add documents "
                              "for a new component." % slug, "not_registered")
        except Refused as exc:
            return JSONResponse({"status": "error", "message": exc.message, "reason": exc.reason}, status_code=403)
        except ConfigError as exc:
            return JSONResponse({"status": "error", "message": str(exc)}, status_code=500)
        finally:
            acting_var.reset(token)
    result = _ingest_as(caller, component, doc_type, content, filename)
    if result["status"] == "ok":
        status_code = 200
    elif result.get("reason") == "too_large":
        status_code = 413
    else:
        status_code = 400
    return JSONResponse(result, status_code=status_code)


# Health check endpoint
@app.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint: the mounted instance is present, configured and writable."""
    # /health is open so a container health check can call it without a credential. An
    # unauthenticated caller learns only whether the service is healthy.
    detailed = caller_from_scope(request.scope) is not None
    try:
        healthy, payload = wiki_health(WIKI_ROOT)
    except Exception as e:
        payload = {
            "status": "unhealthy",
            "wiki_root": str(WIKI_ROOT),
            "message": f"Health check failed: {str(e)}",
        }
        healthy = False
    if not detailed:
        payload = {"status": payload["status"]}
    return JSONResponse(payload, status_code=200 if healthy else 500)


# ── Dual-transport ASGI app ──────────────────────────────────────────────────
# Claude Code's native MCP client speaks Streamable HTTP (POST /mcp).
# mcp-remote (used by Claude Desktop) speaks SSE (GET /sse + POST /messages/).
# We create both from the same FastMCP server and stitch them into one app.
# FastMCP's _lifespan_manager() is ref-counted so entering it twice is safe.

_http_app = app.http_app(transport="http")  # /mcp  – Streamable HTTP
_sse_app = app.http_app(transport="sse")    # /sse + /messages/ – SSE


def _check_auth_settings() -> None:
    """Open the security store (raises StoreError with the fix if it cannot be); warn when no principal exists."""
    import logging
    if _store_access.principal_count() == 0:
        logging.getLogger(__name__).warning(
            "No principals exist: every request is refused until the first administrator is created "
            "(run ./manifold init).")


@asynccontextmanager
async def _combined_lifespan(starlette_app: Starlette):
    _check_auth_settings()
    async with _http_app.lifespan(starlette_app):
        async with _sse_app.lifespan(starlette_app):
            yield


# Merge route tables: HTTP routes first (priority); skip SSE routes whose
# path already exists in the HTTP set (e.g. /health appears in both).
_http_paths = {getattr(r, "path", None) for r in _http_app.routes}
_extra_sse_routes = [
    r for r in _sse_app.routes if getattr(r, "path", None) not in _http_paths
]

# ── Documentation browser ────────────────────────────────────────────────────
# Serves wiki/ as a Docsify SPA at /docs.  The page shell comes from assets/web (or the
# instance's own wiki/index.html); its scripts and styles are served from
# /docs/_manifold/vendor, so the browser needs no other host.
# raw/ is also mounted at /docs/raw so relative links like ../../raw/... resolve.
# Non-fatal: if wiki/ doesn't exist or aiofiles is missing the mounts are skipped.
def _build_docs_routes(root: Path) -> list:
    """Routes for the wiki browser of the instance at ``root``; empty if it has no wiki/ folder."""
    async def docs_shell(request: Request):
        own_page = instance_shell(root)
        if own_page is not None:
            return FileResponse(str(own_page))
        try:
            return HTMLResponse(render_shell(root))
        except FileNotFoundError as exc:
            return JSONResponse({"status": "error", "message": str(exc)}, status_code=500)

    wiki_dir, raw_dir = root / "wiki", root / "raw"
    if not wiki_dir.exists():
        return []
    try:
        routes = [Route("/docs/", docs_shell), Route("/docs/index.html", docs_shell)]
        if vendor_dir().is_dir():
            routes.append(Mount(VENDOR_URL, StaticFiles(directory=str(vendor_dir()))))
        # /docs/raw must come before /docs so Starlette routes it first.
        if raw_dir.exists():
            routes.append(Mount("/docs/raw", StaticFiles(directory=str(raw_dir))))
        routes.append(Mount("/docs", StaticFiles(directory=str(wiki_dir), html=True)))
        return routes
    except Exception as exc:
        import logging
        logging.getLogger(__name__).warning("Wiki browser disabled: %s", exc)
        return []


_docs_routes = _build_docs_routes(WIKI_ROOT)

async def _redirect_root(request: Request) -> RedirectResponse:
    return RedirectResponse(url="/docs/")

asgi_app = Starlette(
    routes=[Route("/", _redirect_root)] + list(_http_app.routes) + _extra_sse_routes + _docs_routes,
    middleware=[Middleware(RequestContextMiddleware), Middleware(PrincipalAuthMiddleware, store=_store_access),
                Middleware(RoutePolicyMiddleware, store=_store_access)],
    lifespan=_combined_lifespan,
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8686"))
    # Loopback unless MANIFOLD_HOST says otherwise; reload only when asked for (development).
    host = os.getenv("MANIFOLD_HOST", "127.0.0.1")
    try:
        _check_auth_settings()
    except StoreError as exc:
        raise SystemExit("error: %s" % exc)
    reload = os.getenv("MANIFOLD_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run("server:asgi_app", host=host, port=port, reload=reload)
