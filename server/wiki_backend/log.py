# SPDX-License-Identifier: Apache-2.0
"""Wiki append-only logging operations."""

from pathlib import Path
from datetime import date, datetime
from .models import WikiLogRequest
from .git import git_commit


def _derive_pages(action: str, component: str | None) -> str:
    """Best-effort derivation of pages affected from action + component."""
    if not component:
        return "wiki/log.md"
    slug = component.strip().lower()
    if action in ("register", "update-component"):
        return f"wiki/components/{slug}.md"
    if action == "create-handoff":
        return f"wiki/handoffs/ (new handoff from {slug})"
    if action in ("update-handoff", "complete-handoff"):
        return f"wiki/handoffs/ ({slug})"
    return f"wiki/components/{slug}.md"


def wiki_log_append(wiki_root: Path, request: WikiLogRequest) -> dict:
    """
    Append a properly formatted section to the operation log (wiki/log.md).

    Each call produces a new ## YYYY-MM-DD | action | title section,
    matching the schema defined in wiki/CLAUDE.md. Never truncates or
    rewrites existing entries.

    Args:
        wiki_root: Path to wiki repository root
        request: WikiLogRequest with action, message, and optional component

    Returns:
        Dictionary with confirmation and entry details
    """
    log_path = wiki_root / "wiki" / "log.md"

    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text("# Wiki operation log\n\nAppend-only. Never edit previous entries.\n\n---\n\n", encoding="utf-8")

    today = date.today().isoformat()
    timestamp = datetime.utcnow().isoformat()

    # Section title: component slug if available, else first ~6 words of message
    if request.component:
        title = request.component.strip().lower()
        agent = title
    else:
        words = request.message.split()
        title = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
        agent = "agent"

    pages = _derive_pages(request.action, request.component)

    section = (
        f"\n## {today} | {request.action} | {title}\n\n"
        f"- Agent: {agent}\n"
        f"- Summary: {request.message}\n"
        f"- Pages affected: {pages}\n"
    )

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(section)

    component_tag = f" ({request.component})" if request.component else ""
    git_commit(
        wiki_root,
        [log_path],
        f"log: {request.action}{component_tag}",
    )

    return {
        "status": "appended",
        "timestamp": timestamp,
        "today": today,
        "action": request.action,
        "component": request.component,
        "message": request.message,
        "log_path": str(log_path),
    }
