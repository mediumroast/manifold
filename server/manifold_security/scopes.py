# SPDX-License-Identifier: Apache-2.0
"""Path policy: where the page tools may write and read, and whose scope a page belongs to.

``classify`` turns a path relative to the wiki root into ``(kind, scope)``:

* ``component`` with the component slug as scope: ``wiki/components/<slug>.md`` and
  ``wiki/guides/agents/<slug>.md``;
* ``handoff-only`` (no scope): everything under ``wiki/handoffs/``, written only by the
  handoff code;
* ``log-only`` (no scope): ``wiki/log.md``, appended only by the log code;
* ``system`` (no scope): ``wiki/_sidebar.md``, ``wiki/CLAUDE.md`` and ``manifold.yaml``;
* ``shared`` with scope ``_shared``: any other ``wiki/**.md`` page (decisions,
  architecture, index, guides).

Anything else is refused, as are absolute paths, ``..``, NUL bytes and symlinks that
leave the wiki root.  Standard library only (the host command shares this package).
"""

from pathlib import Path, PurePosixPath
from typing import Optional, Tuple

from .principals import SHARED_SCOPE, is_slug

COMPONENT = "component"
HANDOFF_ONLY = "handoff-only"
LOG_ONLY = "log-only"
SYSTEM = "system"
SHARED = "shared"

_SYSTEM_PATHS = {"manifold.yaml", "wiki/_sidebar.md", "wiki/CLAUDE.md"}
READ_PREFIXES = ("wiki/", "raw/")


class PathRefused(ValueError):
    """The path is not one the tools may use.  The message says why."""


def confine(wiki_root, path: str) -> Tuple[Path, str]:
    """
    Resolve ``path`` against ``wiki_root`` and return ``(absolute path, normalised relative path)``.

    Refuses an empty path, a NUL byte, an absolute path, any ``..`` segment, and a path
    whose real location (after following symlinks) is outside the wiki root.
    """
    if not isinstance(path, str) or not path.strip():
        raise PathRefused("The path is empty.")
    if "\x00" in path:
        raise PathRefused("The path contains a NUL byte.")
    if path.startswith(("/", "\\")) or PurePosixPath(path).is_absolute() or (len(path) > 1 and path[1] == ":"):
        raise PathRefused("The path must be relative to the wiki root, not absolute: %s" % path)
    parts = PurePosixPath(path.replace("\\", "/")).parts
    if ".." in parts:
        raise PathRefused("The path may not contain '..': %s" % path)
    relative = "/".join(part for part in parts if part != ".")
    if not relative:
        raise PathRefused("The path is empty.")
    root = Path(wiki_root).resolve()
    target = (root / relative).resolve()
    if target != root and root not in target.parents:
        raise PathRefused("The path leaves the wiki root: %s" % path)
    return root / relative, relative


def classify(wiki_root, path: str) -> Tuple[str, Optional[str]]:
    """The ``(kind, scope)`` of a page path; raises :class:`PathRefused` for anything else."""
    _, relative = confine(wiki_root, path)
    if relative in _SYSTEM_PATHS:
        return SYSTEM, None
    if relative == "wiki/log.md":
        return LOG_ONLY, None
    parts = relative.split("/")
    if parts[0] != "wiki" or not relative.endswith(".md"):
        raise PathRefused("Pages are written only under wiki/ and end in .md: %s" % path)
    if parts[1] == "handoffs" and len(parts) > 2:
        return HANDOFF_ONLY, None
    for prefix in (("wiki", "components"), ("wiki", "guides", "agents")):
        if tuple(parts[:len(prefix)]) == prefix and len(parts) == len(prefix) + 1:
            slug = parts[-1][:-3]
            if not is_slug(slug):
                raise PathRefused("%r is not a valid component name." % slug)
            return COMPONENT, slug
    return SHARED, SHARED_SCOPE


def check_readable(wiki_root, path: str) -> Path:
    """The absolute path of a page the tools may read: confined, and under ``wiki/`` or ``raw/``."""
    absolute, relative = confine(wiki_root, path)
    if not relative.startswith(READ_PREFIXES):
        raise PathRefused("Only wiki/ and raw/ can be read: %s" % path)
    return absolute
