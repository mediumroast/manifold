# SPDX-License-Identifier: Apache-2.0
"""Component registration operations."""

from pathlib import Path
from datetime import date
from typing import Optional
import json
import re
from .models import WikiRegisterRequest, WikiRegisterResponse
from .read import wiki_read
from .write import wiki_write_page, WikiWriteRequest
from .git import git_commit
from .config import (
    Component, ConfigError, add_component, load_config, sync_schema_slugs, update_component, valid_slug,
)


def wiki_update_component(wiki_root: Path, slug: str, description: Optional[str] = None,
                          repo: Optional[str] = None, owner: Optional[str] = None) -> dict:
    """
    Change a registered component's description, repository or owner, on its page and in the registry.

    Only the fields given (not None) change.  Authorization is the caller's job (the repository and
    owner are for a human registrar only); this function does not check who is asking.
    Returns ``{"status": "updated", "changed": [...]}`` or ``{"error": ...}``.
    """
    if not valid_slug(slug):
        return {"error": "%r is not a valid component name." % slug}
    try:
        config = load_config(wiki_root)
    except ConfigError as exc:
        return {"error": str(exc)}
    if slug not in config.slugs():
        return {"error": "%s is not a registered component." % slug}
    if description is not None and (not description.strip() or len(description) > 200):
        return {"error": "The description must be non-empty and under 200 characters."}
    if repo is not None and not repo.strip():
        return {"error": "The repository URL may not be empty."}
    if owner is not None and not owner.strip():
        return {"error": "The owner may not be empty."}

    changed = [name for name, value in (("description", description), ("repository", repo), ("owner", owner))
               if value is not None]
    component_path = f"wiki/components/{slug}.md"
    if (wiki_root / component_path).is_file():
        page = wiki_read(wiki_root, component_path)
        text = (wiki_root / component_path).read_text(encoding="utf-8")
        if description is not None:
            text = re.sub(r"^summary:.*$", lambda m: "summary: %s" % json.dumps(description, ensure_ascii=False),
                          text, count=1, flags=re.MULTILINE)
        if owner is not None:
            text = re.sub(r"^owner:.*$", lambda m: "owner: %s" % json.dumps(owner, ensure_ascii=False),
                          text, count=1, flags=re.MULTILINE)
        if repo is not None:
            text = re.sub(r"^\*\*Repository:\*\*.*$", lambda m: "**Repository:** %s" % repo, text, count=1,
                          flags=re.MULTILINE)
        if text != (wiki_root / component_path).read_text(encoding="utf-8"):
            response = wiki_write_page(
                wiki_root, WikiWriteRequest(path=component_path, content=text, etag=page.etag,
                                            message=f"Update component: {slug} ({', '.join(changed)})"))
            if response.status != "updated":
                return {"error": response.error or "Write failed with status: %s" % response.status}
    try:
        if update_component(wiki_root, slug, description=description, repo=repo, owner=owner):
            git_commit(wiki_root, [wiki_root / "manifold.yaml"], f"wiki: update {slug} in manifold.yaml")
    except ConfigError as exc:
        return {"error": str(exc)}
    return {"status": "updated", "name": slug, "changed": changed}


def remove_from_sidebar(wiki_root: Path, slug: str) -> Optional[Path]:
    """
    Remove a component's links (its page and its agent guide) from wiki/_sidebar.md.

    The counterpart of the sidebar adders, used by the purge; it does not commit (the caller makes
    one commit for the whole purge).  Handoff entries stay: they are history.  Returns the path if it changed.
    """
    sidebar = wiki_root / "wiki" / "_sidebar.md"
    if not sidebar.exists():
        return None
    lines = sidebar.read_text(encoding="utf-8").splitlines(keepends=True)
    markers = ("(/components/%s.md)" % slug, "(/guides/agents/%s.md)" % slug)
    kept = [line for line in lines if not any(m in line for m in markers)]
    if kept == lines:
        return None
    sidebar.write_text("".join(kept), encoding="utf-8")
    return sidebar


def remove_from_index(wiki_root: Path, slug: str) -> Optional[Path]:
    """Remove a component's row from the Components table in wiki/index.md (no commit). Returns the path if it changed."""
    index = wiki_root / "wiki" / "index.md"
    if not index.exists():
        return None
    lines = index.read_text(encoding="utf-8").splitlines(keepends=True)
    kept = [line for line in lines if not line.startswith("| %s |" % slug)]
    if kept == lines:
        return None
    index.write_text("".join(kept), encoding="utf-8")
    return index


def _title(slug: str) -> str:
    """Title-case a slug: 'acme-api' → 'Acme Api'."""
    return slug.replace("-", " ").replace("_", " ").title()


def _update_sidebar(wiki_root: Path, slug: str) -> None:
    """Add a new component link to wiki/_sidebar.md if not already present."""
    sidebar = wiki_root / "wiki" / "_sidebar.md"
    if not sidebar.exists():
        return
    text = sidebar.read_text(encoding="utf-8")
    link = f"  - [{slug}](/components/{slug}.md)"
    if link in text:
        return  # already there
    # Insert after the last existing component line
    lines = text.splitlines(keepends=True)
    insert_after = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("- [") and "/components/" in line:
            insert_after = i
    if insert_after < 0:
        # No component listed yet (a new instance): the list starts under its heading.
        insert_after = next((i for i, line in enumerate(lines) if line.strip() == "- **Components**"), -1)
    if insert_after >= 0:
        lines.insert(insert_after + 1, link + "\n")
        sidebar.write_text("".join(lines), encoding="utf-8")
        git_commit(wiki_root, [sidebar], f"wiki: add {slug} to sidebar")


_STATUS_SYMBOL = {
    "open": "○",
    "in-progress": "◉",
    "needs-review": "◑",
    "blocked": "⊘",
    "completed": "✓",
    "wont-fix": "✓",
}
_ALL_SYMBOLS = set(_STATUS_SYMBOL.values())


def _strip_symbol(title: str) -> str:
    """Remove a leading state symbol and space from a handoff title."""
    for sym in _ALL_SYMBOLS:
        if title.startswith(sym + " "):
            return title[len(sym) + 1:]
    return title


def update_sidebar_handoff_status(wiki_root: Path, handoff_path: str, new_status: str) -> None:
    """
    Update the state-symbol prefix on an existing handoff sidebar entry.

    handoff_path is wiki-root-relative, e.g.
    "wiki/handoffs/acme-web-to-acme-api/bug-session-expired.md".
    """
    sidebar = wiki_root / "wiki" / "_sidebar.md"
    if not sidebar.exists():
        return
    docsify_path = "/" + "/".join(handoff_path.split("/")[1:])
    symbol = _STATUS_SYMBOL.get(new_status, "○")
    text = sidebar.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changed = False
    for i, line in enumerate(lines):
        if docsify_path in line and line.strip().startswith("- ["):
            # Extract current link text
            m = re.match(r'^(\s*- \[)(.+?)(\]\(.+?\).*)', line)
            if m:
                prefix, title_raw, suffix = m.group(1), m.group(2), m.group(3)
                bare_title = _strip_symbol(title_raw)
                new_title = f"{symbol} {bare_title}"
                if title_raw == new_title:
                    return  # already correct, nothing to do
                lines[i] = f"{prefix}{new_title}{suffix}\n"
                changed = True
                break
    if changed:
        # Opportunistically clean up any duplicate group labels left by merges
        parts = docsify_path.split("/")
        if len(parts) >= 3:
            dir_name = parts[2]
            if "-to-" in dir_name:
                src, _, tgt = dir_name.partition("-to-")
                lines = _deduplicate_group_labels(lines, f"  - {src} → {tgt}")
        sidebar.write_text("".join(lines), encoding="utf-8")
        git_commit(wiki_root, [sidebar],
                   f"wiki: handoff status → {new_status} ({docsify_path.split('/')[-1]})")


def _deduplicate_group_labels(lines: list[str], group_label: str) -> list[str]:
    """Remove duplicate occurrences of a group label, keeping the one with children."""
    indices = [i for i, line in enumerate(lines) if line.rstrip() == group_label]
    if len(indices) <= 1:
        return lines
    to_remove = {
        idx for idx in indices
        if not (idx + 1 < len(lines) and lines[idx + 1].startswith("    - "))
    }
    if len(to_remove) == len(indices):
        to_remove.discard(indices[0])
    return [line for i, line in enumerate(lines) if i not in to_remove]


def update_sidebar_handoff(
    wiki_root: Path,
    source: str,
    target: str,
    handoff_path: Optional[str] = None,
    handoff_title: Optional[str] = None,
) -> None:
    """
    Add a handoff link to wiki/_sidebar.md.

    If handoff_path and handoff_title are provided, inserts a clickable link
    nested under the source → target group label. Creates the group label first
    if it is not already present.

    handoff_path must be a wiki-root-relative path, e.g.
    "wiki/handoffs/acme-web-to-acme-api/bug-session-expired.md".
    The sidebar link is written as the Docsify-absolute form
    "/handoffs/{dir}/{file}.md".
    """
    sidebar = wiki_root / "wiki" / "_sidebar.md"
    if not sidebar.exists():
        return

    text = sidebar.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    group_label = f"  - {source} → {target}"
    in_handoffs = False
    group_line = -1
    last_child_line = -1  # last line that belongs to this group's children

    for i, line in enumerate(lines):
        if "**Handoffs**" in line:
            in_handoffs = True
        if not in_handoffs:
            continue
        stripped = line.rstrip()
        if stripped == group_label:
            group_line = i
        # Children of this group are indented 4 spaces (2 more than the group).
        # Stop scanning when a sibling group label is encountered — otherwise
        # last_child_line bleeds into the next group and inserts the link there.
        if group_line >= 0 and i > group_line:
            if stripped.startswith("  - ") and not stripped.startswith("    - "):
                break
            if stripped.startswith("    - ["):
                last_child_line = i

    # Build the file link if we have one
    file_link: Optional[str] = None
    if handoff_path and handoff_title:
        # handoff_path: "wiki/handoffs/{dir}/{file}.md" → "/handoffs/{dir}/{file}.md"
        docsify_path = "/" + "/".join(handoff_path.split("/")[1:])
        bare_title = _strip_symbol(handoff_title)
        labeled_title = f"{_STATUS_SYMBOL['open']} {bare_title}"
        file_link = f"    - [{labeled_title}]({docsify_path})"
        if docsify_path in text:
            return  # already present (any status), nothing to do

    changed = False

    if group_line < 0:
        # Group label not yet in sidebar — append at end of Handoffs section.
        # Walk through lines to find the last line that belongs to Handoffs
        # (everything before the next top-level "- **...**" section or EOF).
        in_handoffs = False
        end_of_handoffs = len(lines) - 1
        for i, line in enumerate(lines):
            if "**Handoffs**" in line:
                in_handoffs = True
                continue
            if in_handoffs:
                if line.strip().startswith("- **") and "Handoffs" not in line:
                    end_of_handoffs = i - 1
                    break
                end_of_handoffs = i
        new_lines = [group_label + "\n"]
        if file_link:
            new_lines.append(file_link + "\n")
        for line in reversed(new_lines):
            lines.insert(end_of_handoffs + 1, line)
        changed = True
    elif file_link:
        # Group exists — insert the file link after the last existing child (or right after the label)
        insert_at = last_child_line if last_child_line >= 0 else group_line
        lines.insert(insert_at + 1, file_link + "\n")
        changed = True

    if changed:
        lines = _deduplicate_group_labels(lines, group_label)
        sidebar.write_text("".join(lines), encoding="utf-8")
        label = handoff_title or f"{source} → {target}"
        git_commit(wiki_root, [sidebar], f"wiki: add {source} → {target} handoff to sidebar ({label})")


def _update_index(wiki_root: Path, slug: str, description: str) -> None:
    """Add a new row to the Components table in wiki/index.md if not already present."""
    index = wiki_root / "wiki" / "index.md"
    if not index.exists():
        return
    text = index.read_text(encoding="utf-8")
    row = f"| {slug} | active | [wiki/components/{slug}.md](components/{slug}.md) | {description} |"
    if f"| {slug} |" in text:
        return  # already there
    lines = text.splitlines(keepends=True)
    # Insert after the last existing component table row
    insert_after = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("|") and "/components/" in line and "Wiki page" not in line:
            insert_after = i
    if insert_after < 0:
        # No component row yet (a new instance): the first row goes under the table's separator line.
        for i, line in enumerate(lines):
            if line.strip().startswith("|") and "Wiki page" in line and i + 1 < len(lines) \
                    and set(lines[i + 1].strip()) <= set("|-: "):
                insert_after = i + 1
                break
    if insert_after >= 0:
        lines.insert(insert_after + 1, row + "\n")
        index.write_text("".join(lines), encoding="utf-8")
        git_commit(wiki_root, [index], f"wiki: add {slug} to index")


def _register_in_config(wiki_root: Path, component: Component) -> None:
    """Add the component to manifold.yaml and refresh the generated slug list in the schema page."""
    changed = []
    if add_component(wiki_root, component):
        changed.append(wiki_root / "manifold.yaml")
    schema = sync_schema_slugs(wiki_root)
    if schema is not None:
        changed.append(schema)
    if changed:
        git_commit(wiki_root, changed, f"wiki: register {component.slug} in manifold.yaml")


def _read_source_doc(wiki_root: Path, doc_path: str) -> Optional[str]:
    """Read a raw doc by path relative to wiki_root. Returns content or None."""
    full = wiki_root / doc_path
    if full.exists() and full.is_file():
        return full.read_text(encoding="utf-8")
    return None


def _classify_doc(path: str) -> str:
    """Return 'readme' | 'architecture' | 'api' | 'other' based on filename."""
    name = Path(path).name.lower()
    if any(k in name for k in ("readme", "overview", "intro")):
        return "readme"
    if any(k in name for k in ("architecture", "arch", "design", "structure")):
        return "architecture"
    if any(k in name for k in ("api", "contract", "spec", "endpoint", "schema")):
        return "api"
    return "other"


def _section_from_docs(doc_type: str, source_docs: list[dict], stub: str) -> str:
    """
    Return section content for a given doc type.
    Uses the first matching source doc if available, otherwise returns stub.
    """
    matches = [d for d in source_docs if d["type"] == doc_type]
    if not matches:
        return stub
    doc = matches[0]
    return (
        f"_Sourced from `{doc['path']}`"
        f"{' (and ' + str(len(matches)-1) + ' more)' if len(matches) > 1 else ''}. "
        f"Synthesise and rewrite this section as needed._\n\n"
        f"{doc['content']}"
    )


def _extract_section(body: str, heading: str) -> Optional[str]:
    """
    Extract the content of a markdown section by its ## heading.
    Returns the section body (excluding the heading line) or None if not found.
    """
    pattern = rf"^## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, body, re.DOTALL | re.MULTILINE)
    return match.group(1).rstrip() if match else None


def _replace_section(body: str, heading: str, new_content: str) -> str:
    """Replace the content of a markdown section, preserving the heading line."""
    pattern = rf"(^## {re.escape(heading)}\s*\n)(.*?)(?=\n## |\Z)"
    replacement = rf"\g<1>{new_content}\n"
    result = re.sub(pattern, replacement, body, flags=re.DOTALL | re.MULTILINE)
    return result


def _reconcile_component(
    wiki_root: Path,
    slug: str,
    request: WikiRegisterRequest,
    loaded_docs: list[dict],
    today: str,
) -> WikiRegisterResponse:
    """
    Update an already-registered component page from newly provided source docs.

    Preserves hand-edited sections (Integration points, Known issues, Deployment,
    Changelog) and rebuilds only the doc-sourced sections (Overview, Architecture,
    API contract, Sources).
    """
    component_path = f"wiki/components/{slug}.md"

    # Read current page to get etag and existing content
    existing = wiki_read(wiki_root, component_path)
    existing_body = existing.body
    existing_fm = existing.frontmatter

    # Rebuild doc-sourced sections
    _stub_overview = request.description or existing_fm.get("summary", "")
    _stub_arch = (
        f"_To be completed. Update from `raw/{slug}/` source documents._"
    )
    _stub_api = (
        f"_To be completed. Update from `raw/{slug}/` source documents._"
    )

    new_overview = _section_from_docs("readme", loaded_docs, _stub_overview)
    new_arch = _section_from_docs("architecture", loaded_docs, _stub_arch)
    new_api = _section_from_docs("api", loaded_docs, _stub_api)

    sources_lines = "\n".join(
        f"- [`{d['path']}`](../../{d['path']}) — {d['type']} document"
        for d in loaded_docs
    )

    # Append a changelog entry to the existing Changelog section
    existing_changelog = _extract_section(existing_body, "Changelog") or ""
    doc_names = ", ".join(f"`{d['path']}`" for d in loaded_docs)
    new_changelog_entry = f"- **{today}** — Page reconciled from raw docs: {doc_names}"
    updated_changelog = f"{new_changelog_entry}\n\n{existing_changelog}".strip()

    # Apply updates to body
    updated_body = existing_body
    updated_body = _replace_section(updated_body, "Overview", new_overview)
    updated_body = _replace_section(updated_body, "Architecture", new_arch)
    updated_body = _replace_section(updated_body, "API contract", new_api)
    updated_body = _replace_section(updated_body, "Sources", sources_lines)
    updated_body = _replace_section(updated_body, "Changelog", updated_changelog)

    # Rebuild frontmatter with updated last_updated
    fm_lines = ["---"]
    for key, value in existing_fm.items():
        if key == "last_updated":
            fm_lines.append(f"last_updated: {today}")
        else:
            fm_lines.append(f'{key}: "{value}"' if isinstance(value, str) else f"{key}: {value}")
    fm_lines.append("---")
    new_frontmatter = "\n".join(fm_lines)

    full_content = f"{new_frontmatter}\n\n{updated_body.lstrip()}"

    write_request = WikiWriteRequest(
        path=component_path,
        content=full_content,
        etag=existing.etag,
        message=f"Reconcile component from raw docs: {slug}",
    )
    write_response = wiki_write_page(wiki_root, write_request)

    if write_response.status in ("updated", "created"):
        return WikiRegisterResponse(
            name=slug,
            path=component_path,
            status="reconciled",
            message=f"Component page reconciled from {len(loaded_docs)} source doc(s): {slug}",
            etag=write_response.etag,
        )
    elif write_response.status == "conflict":
        return WikiRegisterResponse(
            name=slug,
            path=component_path,
            status="error",
            message=(
                "Reconcile failed: etag conflict — the page was modified concurrently. "
                "Re-run wiki_onboarding_tool to get a fresh etag and retry."
            ),
        )
    else:
        return WikiRegisterResponse(
            name=slug,
            path=component_path,
            status="error",
            message=f"Reconcile failed: {write_response.error}",
        )


def wiki_register_component(wiki_root: Path, request: WikiRegisterRequest) -> WikiRegisterResponse:
    """
    Register a new component in the wiki.

    Creates wiki/components/{slug}.md with the frontmatter and section
    structure required by wiki/CLAUDE.md.

    Source doc options (mutually exclusive; skip_source_docs takes priority):
      skip_source_docs=True  — register with stub sections immediately
      source_docs=[...]      — embed content from existing raw doc paths
      (neither)              — same as skip_source_docs=True (stub sections)
    """
    slug = request.name.strip().lower()

    if not valid_slug(slug):
        return WikiRegisterResponse(
            name=request.name,
            path="",
            status="error",
            message=(
                "Component name must be lowercase letters and digits with single dots, "
                "hyphens or underscores between them, at most 64 characters"
            ),
        )

    try:
        load_config(wiki_root)
    except ConfigError as exc:
        return WikiRegisterResponse(name=slug, path="", status="error", message=str(exc))

    if not request.description or len(request.description) > 200:
        return WikiRegisterResponse(
            name=slug,
            path="",
            status="error",
            message="Description must be non-empty and under 200 characters",
        )

    if not request.repo or not request.owner:
        return WikiRegisterResponse(
            name=slug,
            path="",
            status="error",
            message="Repository URL and owner are required",
        )

    component_path = f"wiki/components/{slug}.md"
    component_file = wiki_root / component_path

    if component_file.exists():
        if not request.reconcile:
            return WikiRegisterResponse(
                name=slug,
                path=component_path,
                status="already_registered",
                message=(
                    f"STOP — component '{slug}' is already registered at {component_path}. "
                    "Do NOT retry this call. "
                    "Tell the user the component exists and offer to run "
                    "wiki_freshness_tool to check if the wiki page is stale."
                ),
            )
        # reconcile=True: fall through to load docs, then call _reconcile_component

    today = date.today().isoformat()
    title = _title(slug)

    # Load source docs if provided
    loaded_docs: list[dict] = []
    missing_source_docs: list[str] = []
    if not request.skip_source_docs:
        # File-path based docs (relative to wiki_root)
        for doc_path in request.source_docs:
            content = _read_source_doc(wiki_root, doc_path)
            if content:
                loaded_docs.append({
                    "path": doc_path,
                    "type": _classify_doc(doc_path),
                    "content": content,
                })
            else:
                missing_source_docs.append(doc_path)

        # Inline docs — content passed directly by the agent (e.g. README from component repo)
        # Keys are doc types: "readme", "architecture", "api", or any filename
        for key, content in (request.inline_docs or {}).items():
            if content and isinstance(content, str):
                doc_type = _classify_doc(key) if "." not in key else _classify_doc(key)
                # Also accept plain type names as keys
                if key in ("readme", "architecture", "api"):
                    doc_type = key
                loaded_docs.append({
                    "path": f"(inline: {key})",
                    "type": doc_type,
                    "content": content,
                })

    using_source_docs = bool(loaded_docs)

    # Reconcile path: page already exists and caller explicitly requested reconcile
    if request.reconcile:
        if not loaded_docs:
            return WikiRegisterResponse(
                name=slug,
                path=component_path,
                status="error",
                message=(
                    "Reconcile requires at least one source doc. "
                    "Provide source_docs=[...] or inline_docs={...}."
                ),
            )
        # A page that predates the registry is added to it here.
        _register_in_config(
            wiki_root,
            Component(slug=slug, repo=request.repo, owner=request.owner, description=request.description),
        )
        return _reconcile_component(wiki_root, slug, request, loaded_docs, today)

    # Build section stubs
    _stub_arch = (
        "_To be completed. Describe the internal design: key modules, patterns, and "
        f"tech stack. Update this section from `raw/{slug}/` source documents._"
    )
    _stub_api = (
        "_To be completed. List endpoints, schemas, and data models. Mark breaking "
        f"changes clearly. Update from `raw/{slug}/` source documents._"
    )
    _stub_overview = request.description
    _stub_integration = (
        "_To be completed. Describe how this component communicates with other "
        "components. Link each component name to its wiki page once known._"
    )

    overview_body = (
        _section_from_docs("readme", loaded_docs, _stub_overview)
        if using_source_docs else _stub_overview
    )
    arch_body = (
        _section_from_docs("architecture", loaded_docs, _stub_arch)
        if using_source_docs else _stub_arch
    )
    api_body = (
        _section_from_docs("api", loaded_docs, _stub_api)
        if using_source_docs else _stub_api
    )

    # Sources section
    if loaded_docs:
        sources_lines = "\n".join(
            f"- [`{d['path']}`](../../{d['path']}) — {d['type']} document"
            for d in loaded_docs
        )
        sources_body = sources_lines
    else:
        sources_body = (
            f"_No raw source documents ingested yet. Add dated docs to `raw/{slug}/` and "
            "update this section with relative links._"
        )

    content = f"""---
title: "{title}"
component: "{slug}"
status: active
last_updated: {today}
owner: "{request.owner}"
summary: "{request.description}"
---

# {title}

## Overview

{overview_body}

**Repository:** {request.repo}

## Architecture

{arch_body}

## API contract

{api_body}

## Integration points

{_stub_integration}

## Implementation status

| Area | Status | Notes |
|---|---|---|
| Initial registration | ✅ Done | {today} |
| Raw source docs | {"✅ Embedded" if using_source_docs else "⬜ Pending"} | {"See Sources section" if using_source_docs else f"Add to `raw/{slug}/`"} |
| Architecture documented | {"⬜ Review embedded content" if using_source_docs else "⬜ Pending"} | |
| API contract documented | {"⬜ Review embedded content" if using_source_docs else "⬜ Pending"} | |

## Changelog

- **{today}** — Component registered.

## Known issues

_None recorded at registration._

## Deployment

_To be completed. Document how the component runs, required environment
variables, dependencies, and health checks._

## Sources

{sources_body}
"""

    write_request = WikiWriteRequest(
        path=component_path,
        content=content,
        etag=None,
        message=f"Register component: {slug}",
    )

    write_response = wiki_write_page(wiki_root, write_request)

    if write_response.status == "created":
        # Keep navigation, home page, and schema registry in sync automatically
        _update_sidebar(wiki_root, slug)
        _update_index(wiki_root, slug, request.description)
        _register_in_config(
            wiki_root,
            Component(slug=slug, repo=request.repo, owner=request.owner, description=request.description),
        )

        msg = f"Component registered successfully: {slug}"
        if missing_source_docs:
            msg += f". Warning: could not read {len(missing_source_docs)} source doc(s): {missing_source_docs}"
        return WikiRegisterResponse(
            name=slug,
            path=component_path,
            status="created",
            message=msg,
            etag=write_response.etag,
        )
    else:
        return WikiRegisterResponse(
            name=slug,
            path=component_path,
            status="error",
            message=f"Failed to register component: {write_response.error}",
        )
