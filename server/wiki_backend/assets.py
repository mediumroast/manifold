# SPDX-License-Identifier: Apache-2.0
"""Asset overlay: files that ship with the server and that an instance may override.

An asset path is relative to an ``assets/`` root, for example
``helpers/commands/handoff-create.md``.  Two roots are searched, in order:

1. the instance's own ``assets/`` directory (``<wiki_root>/assets``), so an
   instance can replace any file or add new ones;
2. the core ``assets/`` directory that ships with the server.

The core directory is, in order: ``MANIFOLD_ASSETS_DIR`` if set, ``assets/`` at
the repository root (two levels above this package), or ``assets/`` next to the
server code (how the container image lays it out).
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

INSTANCE_DIR = "assets"


def core_assets_dir() -> Path:
    """The core assets directory.  Not required to exist; callers handle a miss."""
    override = os.environ.get("MANIFOLD_ASSETS_DIR", "").strip()
    if override:
        return Path(override)
    here = Path(__file__).resolve()
    for candidate in (here.parents[2] / "assets", here.parents[1] / "assets"):
        if candidate.is_dir():
            return candidate
    return here.parents[2] / "assets"


def _inside(base: Path, rel: str) -> Optional[Path]:
    """``base/rel`` if it stays inside ``base`` after resolving symlinks, else None."""
    if not rel or rel.startswith(("/", "\\")) or "\x00" in rel:
        return None
    try:
        base_resolved = base.resolve()
        target = (base / rel).resolve()
        target.relative_to(base_resolved)
    except (ValueError, OSError):
        return None
    return target


def _roots(wiki_root: Path) -> List:
    return [("instance", Path(wiki_root) / INSTANCE_DIR), ("core", core_assets_dir())]


def find(wiki_root: Path, rel: str) -> Optional[Dict]:
    """Locate an asset file.  Returns ``{"path": Path, "origin": "instance"|"core"}`` or None."""
    for origin, base in _roots(wiki_root):
        target = _inside(base, rel)
        if target is not None and target.is_file():
            return {"path": target, "origin": origin}
    return None


def read_text(wiki_root: Path, rel: str) -> Optional[str]:
    """Contents of the asset, instance copy first, or None if neither layer has it."""
    found = find(wiki_root, rel)
    return found["path"].read_text(encoding="utf-8") if found else None


def list_files(wiki_root: Path, rel_dir: str, pattern: str = "*") -> Dict[str, str]:
    """
    Files directly inside an asset directory, from both layers.

    Returns ``{file name: origin}``; a name present in both layers is reported
    as ``instance``.
    """
    names: Dict[str, str] = {}
    for origin, base in reversed(_roots(wiki_root)):  # core first, so instance overwrites
        directory = _inside(base, rel_dir)
        if directory is None or not directory.is_dir():
            continue
        for item in directory.glob(pattern):
            if item.is_file() and _inside(base, "%s/%s" % (rel_dir, item.name)) is not None:
                names[item.name] = origin
    return dict(sorted(names.items()))
