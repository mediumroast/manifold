# SPDX-License-Identifier: Apache-2.0
"""Handoff lifecycle operations — create, claim, close, list."""

from __future__ import annotations

import re
import yaml
from datetime import date
from pathlib import Path
from typing import Optional

from .models import WikiWriteRequest, WikiLogRequest
from .read import wiki_read
from .write import write_page_of_kinds
from .log import wiki_log_append
from .register import update_sidebar_handoff, update_sidebar_handoff_status
from .config import ConfigError, registered_slugs
from manifold_security import scopes


def wiki_write_handoff_page(wiki_root: Path, request: WikiWriteRequest):
    """
    Create or update a handoff page (``wiki/handoffs/<pair>/<file>.md``): the only writer of handoff pages.

    Same etag rules, frontmatter validation and git commit as :func:`wiki_write_page`, with
    the same path confinement; it accepts handoff pages and nothing else.
    """
    return write_page_of_kinds(wiki_root, request, (scopes.HANDOFF_ONLY,))


_VALID_TYPES = {"feature", "bug", "breaking-change", "integration-spec"}

_PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _make_id(title: str) -> str:
    """Convert a title to a kebab-case slug, max 40 chars."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:40].rstrip("-")


def _extract_section(content: str, header: str) -> str:
    """Extract the body of a markdown section (## Header). Returns empty string if not found."""
    pattern = rf"^##\s+{re.escape(header)}\s*$(.*?)(?=^##\s|\Z)"
    m = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def _update_frontmatter_field(content: str, field: str, value: str) -> str:
    """Replace a frontmatter field value in place."""
    return re.sub(
        rf"^({re.escape(field)}:\s*).*$",
        rf"\g<1>{value}",
        content,
        count=1,
        flags=re.MULTILINE,
    )


def _fill_section(content: str, header: str, body: str) -> str:
    """Replace the content of a ## Section with body text."""
    pattern = rf"(^##\s+{re.escape(header)}\s*\n)(.*?)(?=^##\s|\Z)"
    replacement = rf"\1{body}\n\n"
    return re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE | re.DOTALL)


def _append_to_section(content: str, header: str, text: str) -> str:
    """Append text to an existing ## Section without replacing its content."""
    pattern = rf"(^##\s+{re.escape(header)}\s*\n)(.*?)(?=^##\s|\Z)"
    def replacer(m: re.Match) -> str:
        existing = m.group(2).rstrip()
        divider = "\n\n" if existing and not existing.endswith("\n\n") else "\n"
        return f"{m.group(1)}{existing}{divider}{text}\n\n"
    return re.sub(pattern, replacer, content, count=1, flags=re.MULTILINE | re.DOTALL)


def _parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from a markdown string. Returns {} on failure."""
    if not content.startswith("---"):
        return {}
    rest = content[3:]
    close = rest.find("\n---")
    if close < 0:
        return {}
    try:
        return yaml.safe_load(rest[:close]) or {}
    except yaml.YAMLError:
        return {}


# ── Public API ────────────────────────────────────────────────────────────────


def handoff_create(
    wiki_root: Path,
    source: str,
    target: str,
    type: str,
    priority: str,
    title: str,
    summary: str,
    what_needs_to_happen: str,
    technical_details: str = "",
) -> dict:
    """
    Create a new handoff document and update the sidebar.

    Returns {"status": "created", "path": ..., "id": ..., "next": ...}
    or {"error": ...} on validation failure.
    """
    try:
        valid_slugs = registered_slugs(wiki_root)
    except ConfigError as exc:
        return {"error": str(exc)}
    for role, slug in (("source", source), ("target", target)):
        if slug not in valid_slugs:
            return {
                "error": (
                    f"Unknown {role} component slug '{slug}'. "
                    f"Registered components: {sorted(valid_slugs)}. "
                    "Register it with wiki_register_component_tool."
                )
            }
    if type not in _VALID_TYPES:
        return {
            "error": (
                f"Unknown handoff type '{type}'. "
                f"Valid types: {sorted(_VALID_TYPES)}"
            )
        }

    handoff_id = _make_id(title)
    path = f"wiki/handoffs/{source}-to-{target}/{type}-{handoff_id}.md"

    if (wiki_root / path).exists():
        return {
            "error": (
                f"Handoff already exists at {path}. "
                f"Use action='claim' to pick it up."
            )
        }

    today = date.today().isoformat()
    content = (
        f"---\n"
        f'title: "{title}"\n'
        f"type: {type}\n"
        f"source_component: {source}\n"
        f"target_component: {target}\n"
        f"status: open\n"
        f"priority: {priority}\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        f"blocking: []\n"
        f"blocked_by: []\n"
        f"---\n\n"
        f"## Summary\n\n{summary}\n\n"
        f"## What needs to happen\n\n{what_needs_to_happen}\n\n"
        f"## Technical details\n\n{technical_details or '_(None provided.)_'}\n\n"
        f"## Implementation notes\n\n_(Target fills this in while working.)_\n\n"
        f"## Blockers\n\n_(None.)_\n\n"
        f"## Related handoffs\n\n_(None.)_\n"
    )

    request = WikiWriteRequest(
        path=path,
        content=content,
        etag=None,
        message=f"handoff: create {type} from {source} to {target} — {title}",
    )
    response = wiki_write_handoff_page(wiki_root, request)
    if response.status not in ("created",):
        return {"error": response.error or f"Write failed with status: {response.status}"}

    # Update sidebar
    update_sidebar_handoff(
        wiki_root, source, target,
        handoff_path=path,
        handoff_title=title,
    )

    # Log
    wiki_log_append(
        wiki_root,
        WikiLogRequest(
            action="create-handoff",
            component=target,
            message=f"Created {type} handoff from {source}: {title}",
        ),
    )

    return {
        "status": "created",
        "path": path,
        "id": handoff_id,
        "next": (
            f"Target component can now call "
            f"wiki_handoff_tool(action='claim', path='{path}') to pick this up."
        ),
    }


def handoff_claim(wiki_root: Path, path: str) -> dict:
    """
    Claim an open handoff and mark it in-progress.

    Returns {"status": "claimed", "path": ..., "summary": ..., "what_needs_to_happen": ...}
    or {"error": ...}.
    """
    try:
        page = wiki_read(wiki_root, path)
    except FileNotFoundError:
        return {"error": f"Handoff not found: {path}"}

    fm = page.frontmatter
    current_status = fm.get("status", "open")
    if current_status in ("in-progress", "completed"):
        return {
            "error": (
                f"Handoff is already {current_status}. "
                f"Use action='close' to complete it."
            )
        }

    today = date.today().isoformat()
    content = (wiki_root / path).read_text(encoding="utf-8")
    content = _update_frontmatter_field(content, "status", "in-progress")
    content = _update_frontmatter_field(content, "updated", today)

    request = WikiWriteRequest(
        path=path,
        content=content,
        etag=page.etag,
        message=f"handoff: claim — {fm.get('title', path)}",
    )
    response = wiki_write_handoff_page(wiki_root, request)
    if response.status not in ("updated",):
        return {"error": response.error or f"Write failed with status: {response.status}"}

    # Update sidebar symbol
    update_sidebar_handoff_status(wiki_root, path, "in-progress")

    target = fm.get("target_component", "")
    wiki_log_append(
        wiki_root,
        WikiLogRequest(
            action="update-handoff",
            component=target or None,
            message=f"Claimed handoff: {fm.get('title', path)} — status: in-progress",
        ),
    )

    # Extract summary sections from the original body
    summary_text = _extract_section(page.body, "Summary")
    what_text = _extract_section(page.body, "What needs to happen")

    return {
        "status": "claimed",
        "path": path,
        "summary": summary_text,
        "what_needs_to_happen": what_text,
    }


def handoff_close(wiki_root: Path, path: str, resolution: str) -> dict:
    """
    Mark a handoff completed and record the resolution.

    Returns {"status": "completed", "path": ..., "next": ...}
    or {"error": ...}.
    """
    try:
        page = wiki_read(wiki_root, path)
    except FileNotFoundError:
        return {"error": f"Handoff not found: {path}"}

    fm = page.frontmatter
    current_status = fm.get("status", "open")
    if current_status == "completed":
        return {"error": "Handoff is already completed."}

    today = date.today().isoformat()
    content = (wiki_root / path).read_text(encoding="utf-8")
    content = _update_frontmatter_field(content, "status", "completed")
    content = _update_frontmatter_field(content, "updated", today)
    content = _fill_section(content, "Implementation notes", resolution)

    request = WikiWriteRequest(
        path=path,
        content=content,
        etag=page.etag,
        message=f"handoff: close — {fm.get('title', path)}",
    )
    response = wiki_write_handoff_page(wiki_root, request)
    if response.status not in ("updated",):
        return {"error": response.error or f"Write failed with status: {response.status}"}

    # Update sidebar symbol
    update_sidebar_handoff_status(wiki_root, path, "completed")

    target_component = fm.get("target_component", "")
    wiki_log_append(
        wiki_root,
        WikiLogRequest(
            action="complete-handoff",
            component=target_component or None,
            message=f"Completed handoff: {fm.get('title', path)}",
        ),
    )

    return {
        "status": "completed",
        "path": path,
        "next": (
            f"Update the {target_component} component page "
            f"(wiki/components/{target_component}.md) "
            f"to reflect this change in ## Changelog."
        ),
    }


def handoff_request_review(wiki_root: Path, path: str, notes: str) -> dict:
    """
    Mark a handoff as needing source review and append implementation notes.

    Called by the target after completing their implementation. Sets status →
    needs-review and updates the sidebar symbol to ◑.

    Returns {"status": "needs-review", "path": ..., "next": ...} or {"error": ...}.
    """
    try:
        page = wiki_read(wiki_root, path)
    except FileNotFoundError:
        return {"error": f"Handoff not found: {path}"}

    fm = page.frontmatter
    current_status = fm.get("status", "open")
    if current_status != "in-progress":
        return {
            "error": (
                f"Handoff status is '{current_status}' — only in-progress handoffs "
                "can be submitted for review. Use action='claim' first."
            )
        }

    today = date.today().isoformat()
    content = (wiki_root / path).read_text(encoding="utf-8")
    content = _update_frontmatter_field(content, "status", "needs-review")
    content = _update_frontmatter_field(content, "updated", today)
    content = _append_to_section(content, "Implementation notes", notes)

    request = WikiWriteRequest(
        path=path,
        content=content,
        etag=page.etag,
        message=f"handoff: request-review — {fm.get('title', path)}",
    )
    response = wiki_write_handoff_page(wiki_root, request)
    if response.status not in ("updated",):
        return {"error": response.error or f"Write failed with status: {response.status}"}

    update_sidebar_handoff_status(wiki_root, path, "needs-review")

    source_component = fm.get("source_component", "")
    wiki_log_append(
        wiki_root,
        WikiLogRequest(
            action="update-handoff",
            component=source_component or None,
            message=f"Review requested on handoff: {fm.get('title', path)}",
        ),
    )

    return {
        "status": "needs-review",
        "path": path,
        "next": (
            f"Notify {source_component} that this handoff is awaiting their review. "
            f"They should run /handoff-confirm or "
            f"wiki_handoff_tool(action='confirm', path='{path}') to approve, "
            f"or action='reject' to send it back with feedback."
        ),
    }


def handoff_confirm(wiki_root: Path, path: str, notes: str = "") -> dict:
    """
    Confirm a handoff from the source component's perspective.

    Called by the source after reviewing the target's implementation. Sets
    status → completed and updates the sidebar symbol to ✓.

    Returns {"status": "confirmed", "path": ..., "next": ...} or {"error": ...}.
    """
    try:
        page = wiki_read(wiki_root, path)
    except FileNotFoundError:
        return {"error": f"Handoff not found: {path}"}

    fm = page.frontmatter
    current_status = fm.get("status", "open")
    if current_status != "needs-review":
        return {
            "error": (
                f"Handoff status is '{current_status}' — only needs-review handoffs "
                "can be confirmed. Use action='request-review' first."
            )
        }

    today = date.today().isoformat()
    content = (wiki_root / path).read_text(encoding="utf-8")
    content = _update_frontmatter_field(content, "status", "completed")
    content = _update_frontmatter_field(content, "updated", today)
    if notes:
        content = _append_to_section(
            content, "Implementation notes", f"**Confirmed by source:** {notes}"
        )

    request = WikiWriteRequest(
        path=path,
        content=content,
        etag=page.etag,
        message=f"handoff: confirm — {fm.get('title', path)}",
    )
    response = wiki_write_handoff_page(wiki_root, request)
    if response.status not in ("updated",):
        return {"error": response.error or f"Write failed with status: {response.status}"}

    update_sidebar_handoff_status(wiki_root, path, "completed")

    source_component = fm.get("source_component", "")
    target_component = fm.get("target_component", "")
    wiki_log_append(
        wiki_root,
        WikiLogRequest(
            action="complete-handoff",
            component=source_component or None,
            message=f"Confirmed and completed handoff: {fm.get('title', path)}",
        ),
    )

    return {
        "status": "confirmed",
        "path": path,
        "next": (
            f"Handoff confirmed and marked completed. "
            f"Update wiki/components/{target_component}.md ## Changelog to reflect this. "
            f"Then close any related handoffs in the opposite direction with /handoff-close."
        ),
    }


def handoff_reject(wiki_root: Path, path: str, feedback: str) -> dict:
    """
    Reject a handoff from the source component's perspective and send it back.

    Called by the source when the target's implementation is insufficient.
    Appends feedback to ## Blockers and sets status → in-progress.

    Returns {"status": "rejected", "path": ..., "next": ...} or {"error": ...}.
    """
    try:
        page = wiki_read(wiki_root, path)
    except FileNotFoundError:
        return {"error": f"Handoff not found: {path}"}

    fm = page.frontmatter
    current_status = fm.get("status", "open")
    if current_status != "needs-review":
        return {
            "error": (
                f"Handoff status is '{current_status}' — only needs-review handoffs "
                "can be rejected."
            )
        }

    today = date.today().isoformat()
    content = (wiki_root / path).read_text(encoding="utf-8")
    content = _update_frontmatter_field(content, "status", "in-progress")
    content = _update_frontmatter_field(content, "updated", today)
    content = _append_to_section(
        content, "Blockers", f"**{today} — Rejected by source:** {feedback}"
    )

    request = WikiWriteRequest(
        path=path,
        content=content,
        etag=page.etag,
        message=f"handoff: reject — {fm.get('title', path)}",
    )
    response = wiki_write_handoff_page(wiki_root, request)
    if response.status not in ("updated",):
        return {"error": response.error or f"Write failed with status: {response.status}"}

    update_sidebar_handoff_status(wiki_root, path, "in-progress")

    target_component = fm.get("target_component", "")
    wiki_log_append(
        wiki_root,
        WikiLogRequest(
            action="update-handoff",
            component=target_component or None,
            message=f"Rejected (needs rework): {fm.get('title', path)}",
        ),
    )

    return {
        "status": "rejected",
        "path": path,
        "next": (
            f"Feedback added to ## Blockers. Handoff is back in-progress. "
            f"Notify {target_component} to review the feedback and re-implement. "
            f"They can re-submit with action='request-review' when ready."
        ),
    }


def handoff_list(
    wiki_root: Path,
    target: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """
    List handoff documents, optionally filtered by target component and/or status.

    Returns {"handoffs": [...]} sorted by priority then updated date (desc).
    """
    handoffs_dir = wiki_root / "wiki" / "handoffs"
    if not handoffs_dir.exists():
        return {"handoffs": []}

    results = []
    for md_file in handoffs_dir.rglob("*.md"):
        if md_file.name == ".gitkeep":
            continue
        content = md_file.read_text(encoding="utf-8")
        fm = _parse_frontmatter(content)
        if not fm:
            continue

        file_status = fm.get("status", "")
        file_target = fm.get("target_component", "")

        if target and file_target != target:
            continue
        if status and file_status != status:
            continue

        rel_path = str(md_file.relative_to(wiki_root))
        results.append({
            "path": rel_path,
            "title": fm.get("title", md_file.stem),
            "source_component": fm.get("source_component", ""),
            "target_component": file_target,
            "status": file_status,
            "priority": fm.get("priority", "medium"),
            "updated": fm.get("updated", ""),
        })

    results.sort(
        key=lambda h: (
            _PRIORITY_ORDER.get(h["priority"], 99),
            # Sort by updated descending (negate by reversing string comparison)
            h["updated"],
        )
    )

    return {"handoffs": results}
