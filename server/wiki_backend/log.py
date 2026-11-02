# SPDX-License-Identifier: Apache-2.0
"""Wiki append-only logging operations."""

import re
from pathlib import Path
from datetime import date, datetime
from .models import WikiLogRequest
from .git import git_commit
from .actor import current_actor
from .config import valid_slug

_ACTION_RE = re.compile(r"[a-z0-9_-]{1,32}")


def _one_line(text: str) -> str:
    """Whitespace runs, newlines included, become one space: a message is one line of one entry."""
    return " ".join((text or "").split())


def _escape_marker(line: str) -> str:
    """Escape a leading ``#``, ``-`` or ``*`` so the text cannot read as a heading or a list item."""
    return "\\" + line if line[:1] in ("#", "-", "*") else line



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

    # Nothing the caller supplies may become a second entry, a second field or a forged heading.
    if not _ACTION_RE.fullmatch(request.action or ""):
        raise ValueError("Invalid log action %r: use 1 to 32 characters from a-z, 0-9, '_' and '-'." % (request.action,))
    component = None
    if request.component:
        component = request.component.strip().lower()
        if not valid_slug(component):
            raise ValueError("Invalid log component %r: it must be a component slug." % (request.component,))
    message = _one_line(request.message)

    today = date.today().isoformat()
    timestamp = datetime.utcnow().isoformat()

    # Section title: component slug if available, else first ~6 words of message
    if component:
        title = component
        agent = title
    else:
        words = message.split()
        title = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
        agent = "agent"

    # The agent line names the principal behind the credential, never a name the caller supplied.
    actor = current_actor()
    if actor is not None:
        agent = actor.name

    pages = _derive_pages(request.action, component)

    section = (
        f"\n## {today} | {request.action} | {title}\n\n"
        f"- Agent: {agent}\n"
        f"- Summary: {_escape_marker(message)}\n"
        f"- Pages affected: {pages}\n"
    )

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(section)

    component_tag = f" ({component})" if component else ""
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
        "component": component,
        "message": message,
        "log_path": str(log_path),
    }
