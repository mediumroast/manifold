# SPDX-License-Identifier: Apache-2.0
"""Only the entry module imports the web framework (PHASE_4_PLAN Task 15, INT-2 S4).

Everything else (`wiki_backend`, `manifold_security`, `manifold_cli`) stays plain Python, so a
framework change touches one file.
"""

import ast
from pathlib import Path

SERVER_DIR = Path(__file__).resolve().parents[1]
FRAMEWORK = {"fastmcp", "starlette", "uvicorn", "mcp"}
ENTRY_MODULES = {"server.py"}


def scanned_modules():
    files = [SERVER_DIR / "server.py"]
    for package in ("wiki_backend", "manifold_security", "manifold_cli"):
        files += sorted((SERVER_DIR / package).rglob("*.py"))
    return files


def framework_imports(path):
    """Top-level names from FRAMEWORK that the module imports (absolute imports only)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names} & FRAMEWORK
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            if node.module.split(".")[0] in FRAMEWORK:
                found.add(node.module.split(".")[0])
    return found


def test_there_are_modules_to_scan():
    assert len(scanned_modules()) > 20


def test_only_the_entry_module_imports_the_framework():
    offenders = {}
    for path in scanned_modules():
        rel = str(path.relative_to(SERVER_DIR))
        if rel in ENTRY_MODULES:
            continue
        found = framework_imports(path)
        if found:
            offenders[rel] = sorted(found)
    assert offenders == {}, "framework imported outside the entry module: %s" % offenders


def test_the_entry_module_list_has_one_member():
    assert len(ENTRY_MODULES) == 1


def test_the_scan_flags_a_module_that_imports_the_framework(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("import starlette.routing\nfrom fastmcp import FastMCP\nimport os\n")
    assert framework_imports(bad) == {"starlette", "fastmcp"}
