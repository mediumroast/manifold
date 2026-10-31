# SPDX-License-Identifier: Apache-2.0
"""Health of the mounted instance: the checks behind GET /health and ``svc_ctl.sh health``."""

import os
from pathlib import Path
from typing import Dict, Tuple

from .config import ConfigError, load_config

# Files every instance must have.
_REQUIRED_FILES = ("wiki/CLAUDE.md", "wiki/log.md")


def wiki_health(wiki_root: Path) -> Tuple[bool, Dict]:
    """
    Check that the instance is usable.  Returns ``(healthy, payload)``.

    Failing checks make the service unhealthy: the mount is missing, a required
    page is missing, ``manifold.yaml`` is absent or invalid, or the wiki folder
    cannot be written (every write tool would fail).  A missing ``.git`` folder
    is reported as a warning only, because writes still work; they just are not
    recorded in history.
    """
    root = Path(wiki_root)
    checks: Dict[str, str] = {}
    failures = []

    if not root.is_dir():
        message = "Wiki root does not exist: %s" % root
        return False, {"status": "unhealthy", "wiki_root": str(root), "message": message,
                       "checks": {"wiki_root": "missing"}}
    checks["wiki_root"] = "ok"

    for name in _REQUIRED_FILES:
        if (root / name).is_file():
            checks[name] = "ok"
        else:
            checks[name] = "missing"
            failures.append("Required file missing: %s" % name)

    try:
        config = load_config(root)
        checks["manifold.yaml"] = "ok (%d components)" % len(config.components)
    except ConfigError as exc:
        checks["manifold.yaml"] = "invalid"
        failures.append(str(exc))

    wiki_dir = root / "wiki"
    if wiki_dir.is_dir() and os.access(str(wiki_dir), os.W_OK):
        checks["wiki writable"] = "ok"
    else:
        checks["wiki writable"] = "not writable"
        failures.append("The wiki folder is not writable by the server")

    if (root / ".git").exists():
        checks["git repository"] = "ok"
    else:
        checks["git repository"] = "warning: no .git; changes will not be committed"

    healthy = not failures
    return healthy, {
        "status": "healthy" if healthy else "unhealthy",
        "wiki_root": str(root),
        "message": "Wiki service is healthy" if healthy else "; ".join(failures),
        "checks": checks,
    }
