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
from wiki_backend.write import wiki_write_page
from wiki_backend.log import wiki_log_append
from wiki_backend.inventory import wiki_inventory
from wiki_backend.register import wiki_register_component, update_sidebar_handoff, update_sidebar_handoff_status
from wiki_backend.freshness import wiki_freshness
from wiki_backend.onboarding import wiki_onboarding_protocol, wiki_onboarding_preflight, wiki_reconcile_plan
from wiki_backend.ping import wiki_ping
from wiki_backend.config import ConfigError, DEFAULT_SERVER_NAME, load_config
from wiki_backend.health import wiki_health
from wiki_backend.web import VENDOR_URL, instance_shell, render_shell, vendor_dir
from wiki_backend.auth import (
    AuthConfigError, TokenAuthMiddleware, check_startup, configured_token, is_authorized,
)
from wiki_backend.bundles import wiki_bundle_info
from wiki_backend.ingest import (
    wiki_ingest_doc, classify_doc_type, read_body_capped, max_ingest_bytes, BodyTooLarge,
)
from wiki_backend.helpers import wiki_export_helper, wiki_list_helpers, wiki_export_all_helpers
from wiki_backend.agent_guide import wiki_agent_guide
from wiki_backend.handoff import (
    handoff_create, handoff_claim, handoff_close, handoff_list,
    handoff_request_review, handoff_confirm, handoff_reject,
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


@app.tool()
def wiki_ping_tool() -> dict:
    """
    Verify connectivity to the wiki MCP server and return the list of available
    tools. Call this as the first step of any session — especially when working
    from a component repo — to confirm the native MCP connection is live before
    performing any wiki operations.

    Calling this tool successfully proves that native MCP wrappers are working.
    No curl or protocol-level diagnostics are needed.
    """
    return wiki_ping(WIKI_ROOT)


@app.tool()
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

    action="close"          — Mark a handoff completed (target closes after implementing).
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
def wiki_log_append_tool(action: str, message: str, component: str = None) -> dict:
    """
    Append an entry to the operation log (wiki/log.md).
    
    Never truncates or rewrites existing log entries. Always appends.
    
    Args:
        action: Action type (e.g., "register", "handoff_post", "task_complete")
        message: Detailed message describing the action
        component: Optional component name involved in the action
    """
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
def wiki_inventory_tool() -> dict:
    """
    Get a complete inventory of the wiki graph.
    
    Returns components, handoffs, and all files in the wiki.
    """
    try:
        response = wiki_inventory(WIKI_ROOT)
        return {
            "components": [c.dict() for c in response.components],
            "handoffs": [h.dict() for h in response.handoffs],
            "all_files": response.all_files
        }
    except Exception as e:
        return {"error": str(e)}


@app.tool()
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
        if response.status == "reconciled":
            result["next_step"] = (
                f"Call wiki_log_append_tool(action='reconcile-component', "
                f"component='{response.name}', message='Page reconciled from raw docs') "
                "to record this operation."
            )
        return result
    except Exception as e:
        return {"error": str(e)}


@app.tool()
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
                "4. Call wiki_log_append_tool(action='register', message='...', component='your-slug')",
                "5. Call wiki_freshness_tool(component='your-slug')",
                "6. Call wiki_inventory_tool() to confirm registration",
                "7. Call wiki_bundle_info_tool() and install the agent bundle in the component repository",
                "8. Call wiki_export_component_helpers_tool() and write the helper files into the component repository",
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
        return wiki_agent_guide(WIKI_ROOT, component)
    except Exception as e:
        return {"error": str(e)}


@app.tool()
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

    result = wiki_ingest_doc(WIKI_ROOT, component, doc_type, content, filename)
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
    # /health is open so a container health check can call it without the token. When a
    # token is set, an unauthenticated caller learns only whether the service is healthy.
    try:
        token = configured_token()
    except AuthConfigError:
        token = ""
    detailed = token is None or bool(token and is_authorized(request.headers.get("authorization"), token))
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
    """Refuse unsafe authentication settings; warn when authentication is off."""
    import logging
    warning = check_startup(os.getenv("MANIFOLD_HOST", "127.0.0.1"))
    if warning:
        logging.getLogger(__name__).warning(warning)


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
    middleware=[Middleware(RequestContextMiddleware), Middleware(TokenAuthMiddleware)],
    lifespan=_combined_lifespan,
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8686"))
    # Loopback unless MANIFOLD_HOST says otherwise; reload only when asked for (development).
    host = os.getenv("MANIFOLD_HOST", "127.0.0.1")
    try:
        _check_auth_settings()
    except AuthConfigError as exc:
        raise SystemExit("error: %s" % exc)
    reload = os.getenv("MANIFOLD_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run("server:asgi_app", host=host, port=port, reload=reload)
