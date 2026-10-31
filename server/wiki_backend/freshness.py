# SPDX-License-Identifier: Apache-2.0
"""Wiki freshness checking — compares raw doc mtimes against wiki page last_updated."""

from datetime import date, datetime
from pathlib import Path
from typing import Optional

import frontmatter


def wiki_freshness(wiki_root: Path, component: Optional[str] = None) -> dict:
    """
    Compare raw doc modification dates against wiki component page last_updated.

    For each component (or a single named component):
      - Reads last_updated from wiki/components/{slug}.md frontmatter
      - Walks raw/{slug}/ for files newer than last_updated
      - Walks raw/shared/ for files newer than last_updated
      - Returns stale / fresh / unknown lists

    Args:
        wiki_root: Repo root (WIKI_ROOT)
        component: Optional slug to check only one component

    Returns:
        dict with keys: stale, fresh, unknown
    """
    wiki_components_dir = wiki_root / "wiki" / "components"
    raw_dir = wiki_root / "raw"

    # Collect component slugs to check
    if component:
        slugs = [component]
    else:
        slugs = [
            p.stem
            for p in wiki_components_dir.glob("*.md")
            if p.stem not in ("_index",)
        ] if wiki_components_dir.exists() else []

    # Collect shared raw docs and their dates once
    shared_raw = _raw_files_with_dates(raw_dir / "shared") if (raw_dir / "shared").exists() else []

    stale = []
    fresh = []
    unknown = []

    for slug in slugs:
        wiki_page = wiki_components_dir / f"{slug}.md"
        if not wiki_page.exists():
            unknown.append({"component": slug, "reason": "wiki page not found"})
            continue

        # Read last_updated from frontmatter
        try:
            post = frontmatter.load(str(wiki_page))
            raw_val = post.metadata.get("last_updated")
            last_updated = _parse_date(raw_val)
        except Exception as e:
            unknown.append({"component": slug, "reason": f"could not read frontmatter: {e}"})
            continue

        if last_updated is None:
            unknown.append({"component": slug, "reason": "missing last_updated frontmatter"})
            continue

        # Collect component-local raw docs
        component_raw = _raw_files_with_dates(raw_dir / slug) if (raw_dir / slug).exists() else []

        # All raw files relevant to this component
        all_raw = component_raw + shared_raw

        # Find files newer than last_updated
        newer = [
            str(path.relative_to(wiki_root))
            for path, file_date in all_raw
            if file_date > last_updated
        ]

        if newer:
            stale.append({
                "component": slug,
                "wiki_page": f"wiki/components/{slug}.md",
                "last_wiki_update": str(last_updated),
                "newer_raw_docs": sorted(newer),
            })
        else:
            fresh.append(slug)

    return {
        "stale": stale,
        "fresh": fresh,
        "unknown": unknown,
    }


def _raw_files_with_dates(directory: Path) -> list[tuple[Path, date]]:
    """Return (path, date) pairs for all .md files in a directory."""
    results = []
    if not directory.exists():
        return results
    for f in directory.glob("*.md"):
        # Prefer date embedded in filename (YYYY-MM-DD-*) for stability;
        # fall back to mtime so freshly created files without date prefix still register.
        file_date = _date_from_filename(f.name) or _mtime_date(f)
        results.append((f, file_date))
    return results


def _date_from_filename(name: str) -> Optional[date]:
    """Extract YYYY-MM-DD from a filename like 2026-05-09-acme-api-readme.md."""
    parts = name.split("-", 3)
    if len(parts) >= 3:
        try:
            return date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, TypeError):
            pass
    return None


def _mtime_date(path: Path) -> date:
    """Return the file's last-modified date."""
    return datetime.fromtimestamp(path.stat().st_mtime).date()


def _parse_date(value) -> Optional[date]:
    """Parse a frontmatter date value (date object, datetime, or YYYY-MM-DD string)."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None
