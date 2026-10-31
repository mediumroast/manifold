# SPDX-License-Identifier: Apache-2.0
"""Wiki write operations with etag-based conflict detection."""

from pathlib import Path
from typing import Optional
import re
import yaml
from .models import WikiWriteRequest, WikiWriteResponse
from .read import generate_etag
from .git import git_commit


_HANDOFF_REQUIRED_FIELDS = {
    "title", "type", "source_component", "target_component",
    "status", "priority", "created", "updated",
}
_HANDOFF_LEGACY_FIELDS = {"source", "target"}
_HANDOFF_PATH_RE = re.compile(r"^wiki/handoffs/[^/]+/[^/]+\.md$")


def _validate_frontmatter(path: str, content: str) -> Optional[str]:
    """
    Return an error message string if frontmatter is invalid, else None.

    Runs only when content starts with '---'. Checks:
    1. YAML is parseable
    2. For handoff paths: all required fields present, no legacy field names
    """
    if not content.startswith("---"):
        return None

    # Extract text between opening and closing ---
    rest = content[3:]
    close = rest.find("\n---")
    if close < 0:
        return None  # no closing delimiter — not standard frontmatter, skip
    yaml_text = rest[:close]

    try:
        fm = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as exc:
        return f"Frontmatter YAML is malformed: {exc}. Write rejected — fix the frontmatter and retry."

    if not _HANDOFF_PATH_RE.match(path):
        return None  # non-handoff files: YAML validity is enough

    missing = _HANDOFF_REQUIRED_FIELDS - set(fm.keys())
    legacy = _HANDOFF_LEGACY_FIELDS & set(fm.keys())

    errors = []
    if missing:
        errors.append(
            f"Handoff frontmatter is missing required fields: {sorted(missing)}. "
            f"Expected: title, type, source_component, target_component, "
            f"status, priority, created, updated."
        )
    if legacy:
        errors.append(
            f"Found non-canonical field names: {sorted(legacy)}. "
            f"Use source_component and target_component."
        )
    return " ".join(errors) if errors else None


def wiki_write_page(wiki_root: Path, request: WikiWriteRequest) -> WikiWriteResponse:
    """
    Create or update a wiki page with etag-based optimistic concurrency.
    
    For creates: etag must be None
    For updates: etag must match current page's etag
    
    Args:
        wiki_root: Path to wiki repository root
        request: WikiWriteRequest with path, content, etag, message
        
    Returns:
        WikiWriteResponse with status and new etag on success, or conflict error
    """
    file_path = wiki_root / request.path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file exists
    file_exists = file_path.exists()
    
    if request.etag is None and file_exists:
        # Creating new but file already exists
        return WikiWriteResponse(
            path=request.path,
            status="conflict",
            error=f"File already exists: {request.path}. Provide current etag for update."
        )
    
    if request.etag is not None:
        # Updating existing file
        if not file_exists:
            return WikiWriteResponse(
                path=request.path,
                status="conflict",
                error=f"File does not exist: {request.path}. Use etag=None to create."
            )
        
        # Read current content and verify etag
        current_content = file_path.read_text(encoding='utf-8')
        current_etag = generate_etag(current_content)
        
        if current_etag != request.etag:
            return WikiWriteResponse(
                path=request.path,
                status="conflict",
                error=f"Etag mismatch. Current: {current_etag}, Provided: {request.etag}"
            )
    
    # Validate frontmatter before touching disk
    fm_error = _validate_frontmatter(request.path, request.content)
    if fm_error:
        return WikiWriteResponse(path=request.path, status="error", error=fm_error)

    # Write the content
    file_path.write_text(request.content, encoding='utf-8')
    new_content = file_path.read_text(encoding='utf-8')
    new_etag = generate_etag(new_content)

    status = "created" if request.etag is None else "updated"

    # Auto-commit to git.  Non-fatal: write already succeeded if this fails.
    commit_message = request.message or f"wiki: {status} {request.path}"
    git_commit(wiki_root, [file_path], commit_message)

    return WikiWriteResponse(
        path=request.path,
        status=status,
        etag=new_etag
    )
