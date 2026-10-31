# SPDX-License-Identifier: Apache-2.0
"""Onboarding protocol and pre-flight checks for component registration."""

from pathlib import Path
from typing import Optional

try:
    import frontmatter as _frontmatter_lib
    _HAS_FRONTMATTER = True
except ImportError:
    _HAS_FRONTMATTER = False


# Keywords used to classify raw docs by type
_README_KEYWORDS = {"readme", "overview", "intro", "introduction"}
_ARCH_KEYWORDS = {"architecture", "arch", "design", "structure", "internals"}
_API_KEYWORDS = {"api", "contract", "spec", "endpoint", "schema", "openapi"}


def _classify_doc(filename: str) -> str:
    """Return 'readme' | 'architecture' | 'api' | 'other' for a filename."""
    stem = filename.lower()
    if any(k in stem for k in _README_KEYWORDS):
        return "readme"
    if any(k in stem for k in _ARCH_KEYWORDS):
        return "architecture"
    if any(k in stem for k in _API_KEYWORDS):
        return "api"
    return "other"


def wiki_onboarding_preflight(wiki_root: Path, component: str) -> dict:
    """
    Pre-flight check for a component that is about to be registered.

    Scans raw/{component}/ for existing docs, determines what is missing,
    and returns options the agent should present to the human.
    """
    slug = component.strip().lower()
    raw_dir = wiki_root / "raw" / slug
    component_page = wiki_root / "wiki" / "components" / f"{slug}.md"

    already_registered = component_page.exists()

    # Scan raw dir for source docs
    docs_found: list[dict] = []
    if raw_dir.exists():
        for f in sorted(raw_dir.glob("*.md")):
            docs_found.append({
                "path": str(f.relative_to(wiki_root)),
                "filename": f.name,
                "type": _classify_doc(f.name),
            })

    found_types = {d["type"] for d in docs_found}

    # README is the only truly required doc — architecture and api can always be stubs.
    # We flag them as "recommended" but they don't block registration.
    missing_required = [t for t in ("readme",) if t not in found_types]
    missing_recommended = [t for t in ("architecture", "api") if t not in found_types]
    has_any_docs = bool(docs_found)

    # Agents published to the wiki for this component (see wiki_agent_catalog_tool).
    # The agents themselves are installed in the component repository by the agent bundle.
    agents_dir = raw_dir / "agents"
    agents_found: list[str] = []
    if agents_dir.exists():
        for f in sorted(agents_dir.glob("*.agent.md")):
            agents_found.append(str(f.relative_to(wiki_root)))

    # Build options — always show them so the agent knows what's possible
    options = []
    if not already_registered:
        options = [
            {
                "option": "A",
                "label": "Use docs from the current workspace",
                "description": (
                    "If the component repo has a README.md or other docs, read them "
                    "using your file-reading tool and pass the content directly via "
                    "inline_docs. No need to copy files anywhere. "
                    "Architecture and API sections will be stubs if not provided — "
                    "that is fine, they can be filled in later."
                ),
                "action": (
                    "Read README.md (or any available doc) from the workspace, then call: "
                    f"wiki_register_component_tool(name='{slug}', ..., "
                    "inline_docs={'readme': '<content of README.md>', "
                    "'architecture': '<content if available>'})"
                ),
                "recommended": True,
            },
            {
                "option": "B",
                "label": "Write raw docs to the manifold repo first",
                "description": (
                    f"Write dated markdown files to raw/{slug}/ in the manifold repo, "
                    "then call wiki_register_component_tool with source_docs=[...]. "
                    "Only needed if you want the raw docs permanently stored in manifold."
                ),
                "suggested_filenames": [
                    f"{{YYYY-MM-DD}}-{slug}-readme.md",
                    f"{{YYYY-MM-DD}}-{slug}-architecture.md (optional)",
                    f"{{YYYY-MM-DD}}-{slug}-api.md (optional)",
                ],
                "action": f"wiki_register_component_tool(..., source_docs=['raw/{slug}/YYYY-MM-DD-{slug}-readme.md'])",
            },
            {
                "option": "C",
                "label": "Register with stubs now",
                "description": (
                    "Register immediately with placeholder sections. All sections will "
                    "say 'to be completed'. Use wiki_freshness_tool later to detect "
                    "when docs are added and the page needs updating."
                ),
                "action": "wiki_register_component_tool(..., skip_source_docs=True)",
            },
        ]

    if already_registered:
        if docs_found:
            doc_list = ", ".join(f"`{d['path']}`" for d in docs_found)
            agent_summary = (
                f"Agents published in the wiki: {len(agents_found)}."
                if agents_found else
                "No agents are published in the wiki for this component yet."
            )
            message = (
                f"**`{slug}` is already registered**, but raw docs exist that may not "
                f"be reflected in the wiki page yet: {doc_list}.\n\n"
                f"{agent_summary}\n\n"
                "Would you like me to:\n"
                f"- **Reconcile** the wiki page from these docs (Option D — recommended)\n"
                f"- Check freshness first: `wiki_freshness_tool(component='{slug}')`\n"
                f"- Read the current page: `wiki_read_tool(path='wiki/components/{slug}.md')`\n"
                "- Install or update the agent bundle in the component repository: "
                "`wiki_bundle_info_tool()`\n\n"
                "Just let me know which you'd prefer."
            )

            options = [
                {
                    "option": "D",
                    "label": "Reconcile: update wiki page from raw docs only",
                    "description": (
                        "Re-synthesize the Overview, Architecture, API contract, and Sources "
                        "sections from the raw docs found. Hand-edited sections "
                        "(Integration points, Known issues, Deployment, Changelog) are "
                        "preserved. A changelog entry is appended automatically."
                    ),
                    "action": (
                        f"wiki_register_component_tool(name='{slug}', description='...', "
                        f"repo='...', owner='...', reconcile=True, "
                        f"source_docs={[d['path'] for d in docs_found]})"
                    ),
                    "recommended": True,
                },
                {
                    "option": "E",
                    "label": "Check freshness first",
                    "description": (
                        "Run wiki_freshness_tool to compare raw doc timestamps against "
                        "the wiki page's last_updated date before deciding whether to reconcile."
                    ),
                    "action": f"wiki_freshness_tool(component='{slug}')",
                },
            ]

            return {
                "component": slug,
                "status": "reconcile_available",
                "terminal": False,
                "wiki_page": f"wiki/components/{slug}.md",
                "raw_dir": f"raw/{slug}/",
                "docs_found": docs_found,
                "agents_found": agents_found,
                "message_to_user": message,
                "options": options,
            }

        # Already registered, no raw docs — hard stop, nothing to reconcile
        return {
            "component": slug,
            "status": "already_registered",
            "terminal": True,
            "do_not_call_again": True,
            "action_required": (
                "STOP. Do not call any more tools. "
                "Copy message_to_user verbatim to the chat and stop."
            ),
            "message_to_user": (
                f"**`{slug}` is already registered** in the wiki at "
                f"`wiki/components/{slug}.md`.\n\n"
                "Would you like me to:\n"
                f"- Check if the page is stale: `wiki_freshness_tool(component='{slug}')`\n"
                f"- Read the current page: `wiki_read_tool(path='wiki/components/{slug}.md')`\n"
                "- Update the page with new content\n\n"
                "Just let me know which you'd prefer."
            ),
            "do_not_call": [
                "wiki_register_component_tool",
                "wiki_onboarding_tool",
            ],
            "wiki_page": f"wiki/components/{slug}.md",
            "raw_dir": f"raw/{slug}/",
            "docs_found": docs_found,
        }

    return {
        "component": slug,
        "status": "not_registered",
        "already_registered": False,
        "raw_dir": f"raw/{slug}/",
        "raw_dir_exists": raw_dir.exists(),
        "docs_found": docs_found,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "ready_to_register": True,  # always ready — README is preferred but not blocking
        "options": options,
        "next_step": (
            "Docs found in raw/. Call wiki_register_component_tool with "
            f"source_docs=['{docs_found[0]['path']}'] to embed them."
            if has_any_docs
            else
            f"No raw docs found for '{slug}'. "
            "If the component repo has a README.md or similar, use Option A: "
            "read it with your file tool and pass via inline_docs. "
            "Otherwise use Option C to register with stubs now."
        ),
    }


def _read_page_meta(page_path: Path) -> dict:
    """Extract frontmatter metadata from a wiki component page. Returns {} on failure."""
    if not _HAS_FRONTMATTER:
        return {}
    try:
        post = _frontmatter_lib.load(str(page_path))
        return dict(post.metadata)
    except Exception:
        return {}


def wiki_reconcile_plan(wiki_root: Path, component: str, repo: Optional[str] = None) -> dict:
    """
    Inspect the current state of a registered component and return a ready-to-execute action plan.

    Runs the onboarding preflight, reads the existing component page to discover what is
    already recorded, then returns:
    - A status audit (what is present vs. missing)
    - Values discovered from the page (description, owner)
    - Any inputs still required from the caller (only the repository URL)
    - Concrete tool calls with all discovered values pre-filled
    """
    slug = component.strip().lower()
    component_page = wiki_root / "wiki" / "components" / f"{slug}.md"

    # 1. Run preflight to get docs and agent status
    preflight = wiki_onboarding_preflight(wiki_root, slug)

    if preflight.get("terminal"):
        return {
            "component": slug,
            "status": "nothing_to_do",
            "message": (
                "Component is already registered and no raw docs require reconciliation. "
                + preflight.get("message_to_user", "")
            ),
            "preflight": preflight,
        }

    if preflight.get("status") == "not_registered":
        return {
            "component": slug,
            "status": "not_registered",
            "message": (
                f"'{slug}' is not yet registered in the wiki. "
                f"Run wiki_onboarding_tool(component='{slug}') to start first-time registration."
            ),
            "preflight": preflight,
        }

    # 2. Read existing component page frontmatter
    page_meta = _read_page_meta(component_page) if component_page.exists() else {}
    discovered_description = page_meta.get("summary") or page_meta.get("description")
    discovered_owner = page_meta.get("owner")

    # 3. Build status audit
    docs_found = preflight.get("docs_found", [])
    agents_found = preflight.get("agents_found", [])

    status_audit = {
        "wiki_page": "present",
        "raw_docs": [d["path"] for d in docs_found],
        "agents_published": agents_found,
    }

    discovered: dict = {}
    if discovered_description:
        discovered["description"] = discovered_description
    if discovered_owner:
        discovered["owner"] = discovered_owner

    # 4. Determine what the caller must still supply
    required_inputs = []
    if not repo:
        required_inputs.append({
            "name": "repo",
            "description": "Repository URL, e.g. 'https://github.com/acme/acme-api'",
        })
    ready_to_execute = not required_inputs

    # 5. Build concrete action plan
    desc_val = discovered_description or "<description>"
    owner_val = discovered_owner or "<owner>"
    repo_val = repo or "<repo>"
    source_doc_paths = [d["path"] for d in docs_found]
    doc_summary = ", ".join(source_doc_paths[:2]) + ("..." if len(source_doc_paths) > 2 else "")

    action_plan = [
        {
            "step": 1,
            "action": "reconcile_wiki_page",
            "ready": ready_to_execute,
            "tool_call": (
                f"wiki_register_component_tool(\n"
                f"  name={slug!r},\n"
                f"  description={desc_val!r},\n"
                f"  repo={repo_val!r},\n"
                f"  owner={owner_val!r},\n"
                f"  reconcile=True,\n"
                f"  source_docs={source_doc_paths!r}\n"
                f")"
            ),
        },
        {
            "step": 2,
            "action": "log_reconcile",
            "ready": True,
            "tool_call": (
                f"wiki_log_append_tool(\n"
                f"  action='reconcile-component',\n"
                f"  component={slug!r},\n"
                f"  message='Page reconciled from raw docs: {doc_summary}'\n"
                f")"
            ),
        },
        {
            "step": 3,
            "action": "freshness_check",
            "ready": True,
            "tool_call": f"wiki_freshness_tool(component={slug!r})",
        },
    ]

    if not agents_found:
        action_plan.append({
            "step": 4,
            "type": "mcp_tool",
            "action": "install_agent_bundle",
            "ready": True,
            "tool_call": "wiki_bundle_info_tool()",
            "note": (
                "No agents are published for this component. The response lists the bundle "
                "and the install steps; run the installer in the component repository."
            ),
        })
        action_plan.append({
            "step": 5,
            "type": "mcp_tool",
            "action": "install_handoff_helpers",
            "ready": True,
            "tool_call": "wiki_export_component_helpers_tool()",
            "note": "Returns a 'files' list; write each file's content to its output_path in the component repository.",
        })
        action_plan.append({
            "step": 6,
            "type": "mcp_tool",
            "action": "publish_agent_catalog",
            "depends_on_step": 4,
            "ready": True,
            "tool_call": f"wiki_agent_catalog_tool(component={slug!r})",
            "note": (
                f"After the bundle is installed, copy the agent files into raw/{slug}/agents/ "
                "and run this to create the agent guide page and its sidebar entry."
            ),
        })

    result: dict = {
        "component": slug,
        "status": "plan_ready" if ready_to_execute else "inputs_required",
        "execution_note": (
            "Execute every step in order. A step with a tool_call calls that tool; "
            "a step that returns files means write those files into the component repository."
        ),
        "status_audit": status_audit,
        "discovered": discovered,
        "action_plan": action_plan,
    }

    if required_inputs:
        result["required_inputs"] = required_inputs
        result["message"] = (
            f"{len(required_inputs)} input(s) still needed to complete the plan. "
            "Re-call wiki_reconcile_plan_tool with the values listed in required_inputs "
            "and the plan will be fully ready to execute."
        )
    else:
        result["message"] = (
            f"{len(action_plan)}-step plan generated. All values discovered automatically. "
            "Execute every step in order."
        )

    return result


def wiki_onboarding_protocol() -> dict:
    """
    Return the full component onboarding protocol as structured data.

    This is intentionally static — the protocol is the contract, not a
    reflection of current wiki state. No filesystem I/O required.
    """
    return {
        "overview": (
            "This protocol defines how a new component agent registers with the "
            "wiki, how to post and pick up handoffs, and how to keep "
            "the wiki current. Call this tool first in any new component session. "
            "To check the current state of a specific component before registering, "
            "call wiki_onboarding_tool(component='your-component') — it will scan "
            "existing raw docs and return options if anything is missing."
        ),
        "tools": [
            {
                "name": "wiki_ping_tool",
                "when": (
                    "First call in any session from a component repo — confirms the "
                    "native MCP connection is live and lists every available tool by "
                    "name. A successful response proves native wrappers are working."
                ),
                "required_args": [],
            },
            {
                "name": "wiki_handoff_tool",
                "when": (
                    "Any handoff lifecycle operation — create, claim, close, or list. "
                    "Use this instead of wiki_write_page_tool for all handoff files. "
                    "One call handles frontmatter, sidebar update, and log entry atomically."
                ),
                "required_args": ["action"],
            },
            {
                "name": "wiki_onboarding_tool",
                "when": "First call in any new component session — loads this protocol",
                "required_args": [],
                "optional_args": ["component — if provided, runs a pre-flight check"],
            },
            {
                "name": "wiki_reconcile_plan_tool",
                "when": (
                    "When a component is already registered and may be out of date or have "
                    "no agents installed. Runs the preflight automatically, reads the existing "
                    "page to discover known values, and returns a ready-to-execute action plan."
                ),
                "required_args": ["component"],
                "optional_args": ["repo — repository URL (required for the reconcile call)"],
            },
            {
                "name": "wiki_register_component_tool",
                "when": "Once, when registering a brand-new component for the first time",
                "required_args": ["name", "description", "repo", "owner"],
                "optional_args": [
                    "source_docs — list of raw doc paths to embed in the wiki page",
                    "skip_source_docs — if True, register with stub sections immediately",
                ],
            },
            {
                "name": "wiki_read_tool",
                "when": "Before any write — fetch current content and etag to avoid conflicts",
                "required_args": ["path"],
            },
            {
                "name": "wiki_write_page_tool",
                "when": "Create or update any wiki page",
                "required_args": ["path", "content"],
                "optional_args": ["etag (required for updates)", "message"],
            },
            {
                "name": "wiki_log_append_tool",
                "when": "After every wiki write — mandatory, never skip",
                "required_args": ["action", "message"],
                "optional_args": ["component"],
            },
            {
                "name": "wiki_inventory_tool",
                "when": "To list all components, find open handoffs, audit the wiki graph",
                "required_args": [],
            },
            {
                "name": "wiki_freshness_tool",
                "when": "Before ending any session — check whether wiki pages are stale",
                "required_args": [],
                "optional_args": ["component"],
            },
        ],
        "initial_registration_steps": [
            {
                "order": 1,
                "action": "preflight_check",
                "tool": "wiki_onboarding_tool",
                "notes": (
                    "Call wiki_onboarding_tool(component='your-component') to see what "
                    "raw docs already exist and what options are available. Do not assume "
                    "docs are missing — check first."
                ),
            },
            {
                "order": 2,
                "action": "resolve_raw_docs",
                "tool": None,
                "notes": (
                    "Based on the preflight result, either: (A) ask the human to write "
                    "missing docs to raw/{component}/, (B) ask for paths to alternative "
                    "docs, or (C) confirm the human wants to register with stubs. "
                    "Do not proceed to step 3 without a clear choice."
                ),
                "options": {
                    "A": "Human writes missing docs → re-run preflight → register",
                    "B": "Use source_docs=[...] in wiki_register_component_tool",
                    "C": "Use skip_source_docs=True in wiki_register_component_tool",
                },
            },
            {
                "order": 3,
                "action": "register_component",
                "tool": "wiki_register_component_tool",
                "notes": "Creates wiki/components/{slug}.md with correct frontmatter and sections.",
            },
            {
                "order": 4,
                "action": "log_registration",
                "tool": "wiki_log_append_tool",
                "notes": "Use action='register'. Always log immediately after register.",
            },
            {
                "order": 5,
                "action": "check_freshness",
                "tool": "wiki_freshness_tool",
                "notes": "Resolve any stale pages before ending the session.",
            },
            {
                "order": 6,
                "action": "verify_inventory",
                "tool": "wiki_inventory_tool",
                "notes": "Confirm the component appears in the inventory with correct metadata.",
            },
        ],
        "raw_doc_taxonomy": {
            "component_local": [
                "API spec and endpoint documentation",
                "Internal architecture and design decisions",
                "README and onboarding guide",
                "Deployment and operations runbook",
                "Component-specific changelog",
            ],
            "shared": [
                "Auth token contracts used by 2+ components",
                "Cross-component event or message schemas",
                "UX design system and style guide",
                "Shared infrastructure documentation (DBs, queues, storage)",
            ],
            "rule": (
                "If only one component owns or reads a document, it is component-local "
                "and goes in raw/{component}/. If two or more components depend on it, "
                "it belongs in raw/shared/. When in doubt, start component-local and "
                "move to shared when a second consumer appears."
            ),
            "naming_convention": "{YYYY-MM-DD}-{slug-description}.md",
        },
        "handoff_lifecycle": {
            "overview": (
                "Handoffs are the inter-component message queue. A source component posts "
                "a handoff document; the target component discovers, claims, executes, and "
                "completes it."
            ),
            "post": [
                "1. Call wiki_inventory_tool to confirm the target component exists",
                "2. Call wiki_write_page_tool to create wiki/handoffs/{source}-to-{target}/{type}-{id}.md "
                   "with status: open",
                "3. Call wiki_log_append_tool with action='create-handoff'",
            ],
            "pickup": [
                "1. Call wiki_inventory_tool to list handoffs where target is your component",
                "2. Call wiki_read_tool on the handoff doc to get content and etag",
                "3. Call wiki_write_page_tool with status: in-progress and the etag from step 2",
                "4. Execute the work described in the handoff",
                "5. Call wiki_read_tool again to get the current etag",
                "6. Call wiki_write_page_tool with status: completed, add implementation notes",
                "7. Call wiki_read_tool on your component page to get its etag",
                "8. Call wiki_write_page_tool to update your component page with the changes made",
                "9. Call wiki_log_append_tool with action='complete-handoff'",
            ],
            "status_transitions": "open → in-progress → completed | open → blocked → in-progress → completed | any → wont-fix",
            "path_pattern": "wiki/handoffs/{source}-to-{target}/{type}-{id}.md",
            "valid_types": ["feature", "bug", "breaking-change", "integration-spec"],
        },
        "ongoing_maintenance": {
            "after_api_or_schema_change": [
                "Update the raw API doc in raw/{component}/",
                "Call wiki_freshness_tool to detect the stale wiki page",
                "Read the current wiki page and update it to reflect the change",
                "Log the update with action='update-component'",
            ],
            "after_completing_a_handoff": [
                "Update your component's wiki page (## Implementation status, ## Changelog)",
                "Set last_updated to today's date in frontmatter",
                "Log with action='complete-handoff'",
            ],
            "before_ending_any_session": [
                "Call wiki_freshness_tool",
                "Resolve all stale components before committing",
            ],
        },
        "templates": {
            "overview": (
                "Plan and report documents have one canonical structure each. The agent "
                "bundle installs the templates in the component repository under "
                "docs/templates/; a planner never invents its own document structure."
            ),
            "templates": [
                {"name": "INTENT_TEMPLATE", "produces": "an intent: the outcome wanted, constraints and scenario seeds"},
                {"name": "PHASE_PLAN_TEMPLATE", "used_by": "planner", "handed_to": "coder"},
                {"name": "PHASE_TEST_PLAN_TEMPLATE", "used_by": "test-planner", "handed_to": "test-coder"},
                {"name": "REVIEW_TEMPLATE", "used_by": "reviewer"},
                {"name": "WT_TEMPLATE", "used_by": "human tester (walkthrough session)", "handed_to": "bug-coder"},
                {"name": "SCENARIO_TEMPLATE", "used_by": "scenario-writer"},
                {"name": "SATISFACTION_REPORT_TEMPLATE", "used_by": "quality run"},
            ],
            "tool": "wiki_bundle_info_tool",
            "rule": (
                "Read the template in docs/templates/ before writing any plan or report. "
                "The section order, task marker syntax ([ ]/[x]/[~]) and checklists must not be altered."
            ),
        },
        "schema_reference": "Read wiki/CLAUDE.md for the complete wiki schema, frontmatter requirements, and linking conventions.",
        "agents": {
            "overview": (
                "Role-based agents give LLM tools a consistent, portable development "
                "protocol across every component repo. They are authored once, in the "
                "agent bundle, and installed into each component repository by the "
                "bundle's installer. The wiki keeps a catalog of what is installed."
            ),
            "roles": [
                "planner", "coder", "bug-coder", "reviewer",
                "test-planner", "test-coder", "scenario-writer",
            ],
            "formats": ["claude", "copilot", "skills"],
            "tools": [
                {
                    "name": "wiki_bundle_info_tool",
                    "when": "To learn which bundles exist, their versions and how to install one",
                    "required_args": [],
                },
                {
                    "name": "wiki_agent_catalog_tool",
                    "when": (
                        "After agents are installed in a component repository and copied into "
                        "raw/{component}/agents/ — creates wiki/guides/agents/{component}.md and "
                        "updates the sidebar. Also call it when the guide is stale."
                    ),
                    "required_args": ["component"],
                },
            ],
            "initial_agent_setup_steps": [
                {
                    "order": 7,
                    "action": "install_agent_bundle",
                    "tool": "wiki_bundle_info_tool",
                    "notes": (
                        "After registering the component, install the agent bundle in the "
                        "component repository with its installer (dry run first, then --apply) "
                        "and commit the result there."
                    ),
                },
                {
                    "order": 8,
                    "action": "install_handoff_helpers",
                    "tool": "wiki_export_component_helpers_tool",
                    "description": (
                        "Call wiki_export_component_helpers_tool() once to get all helper files. "
                        "Write each file to its output_path in the component repo and commit. "
                        "This installs /handoff-create, /handoff-pickup, /handoff-close, and "
                        "/manifold-update as slash commands in both Copilot Chat and Claude Code."
                    ),
                    "notes": (
                        "The response contains a 'files' list. Write each file's 'content' to "
                        "its 'output_path'. After the first install, agents can use /manifold-update "
                        "to check for and install future updates without re-running onboarding."
                    ),
                },
                {
                    "order": 9,
                    "action": "publish_agent_catalog",
                    "tool": "wiki_agent_catalog_tool",
                    "notes": (
                        "Copy the installed agent files into raw/{slug}/agents/, then call "
                        "wiki_agent_catalog_tool(component='your-slug') to create "
                        "wiki/guides/agents/{slug}.md and add the sidebar entry."
                    ),
                },
            ],
            "file_locations": {
                "installed_in_component_repo": ".claude/agents/ or .github/agents/ (set by the bundle installer)",
                "published_to_wiki": "raw/{component}/agents/{component}-{role}.agent.md",
            },
        },
    }
