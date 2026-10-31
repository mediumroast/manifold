# SPDX-License-Identifier: Apache-2.0
"""Agent bundles that ship with the server, and how to install them.

The agents, rules and document templates are authored once, in ``bundles/``,
and installed into a component repository by the bundle's own installer.  The
server does not render or scaffold agents; it only says what is available and
how to install it, so that a component repository has one deterministic path
and nothing depends on a model comparing files.

The bundles directory is, in order: ``MANIFOLD_BUNDLES_DIR`` if set,
``bundles/`` at the repository root, or ``bundles/`` next to the server code.
"""

import hashlib
import os
from pathlib import Path
from typing import List

RELEASES_URL = "https://github.com/mediumroast/manifold/releases"


def bundles_dir() -> Path:
    override = os.environ.get("MANIFOLD_BUNDLES_DIR", "").strip()
    if override:
        return Path(override)
    here = Path(__file__).resolve()
    for candidate in (here.parents[2] / "bundles", here.parents[1] / "bundles"):
        if candidate.is_dir():
            return candidate
    return here.parents[2] / "bundles"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _bundle_entries(directory: Path) -> List[dict]:
    entries = []
    if not directory.is_dir():
        return entries
    for bundle in sorted(p for p in directory.iterdir() if p.is_dir()):
        version_file = bundle / "VERSION"
        if not version_file.is_file():
            continue
        version = version_file.read_text(encoding="utf-8").strip()
        entry = {"name": bundle.name, "version": version}
        archive = bundle / "dist" / ("manifold-%s-%s.zip" % (bundle.name, version))
        if archive.is_file():
            entry["archive"] = str(archive.relative_to(directory))
            entry["sha256"] = _sha256(archive)
            entry["bytes"] = archive.stat().st_size
        entries.append(entry)
    return entries


def wiki_bundle_info() -> dict:
    """What bundles this server carries, and the steps to install one into a component repository."""
    bundles = _bundle_entries(bundles_dir())
    steps = [
        "Get the bundle ZIP (the server's own copy if 'archive' is listed, else from the release page) "
        "and check its SHA-256 against the value shown here or in the release's SHA256SUMS.",
        "Unzip it, then from inside the unzipped folder run: ./install.sh --target <component repo>   "
        "(this prints a plan and writes nothing).",
        "Read the plan, then add --apply. Use --profile build (default), quality or single, and "
        "--format claude, copilot or skills.",
        "Review and commit the result in the component repository. Later updates are the same command; "
        "files you changed are kept unless you pass --force.",
    ]
    result = {
        "bundles": bundles,
        "install_steps": steps,
        "releases": RELEASES_URL,
        "next": (
            "Install the handoff helpers too with wiki_export_component_helpers_tool(); "
            "after agents are in the component repository, publish them to this wiki with "
            "wiki_agent_catalog_tool(component)."
        ),
    }
    if not bundles:
        result["message"] = (
            "This server carries no bundle files. Download the base bundle from the release page "
            "(%s) and follow install_steps." % RELEASES_URL
        )
    return result
