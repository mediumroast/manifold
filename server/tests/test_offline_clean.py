# SPDX-License-Identifier: Apache-2.0
"""The server never makes an outgoing HTTP request (PHASE_1_PLAN T21, INT-1 offline-clean).

A server module that imports an HTTP client library fails this test.  The host command
(`manifold_cli`) is not a server module and is not scanned.
"""

import ast
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
HTTP_CLIENT_MODULES = {
    "requests", "httpx", "aiohttp", "urllib3", "urllib.request", "http.client", "httplib2", "pycurl",
    "treq", "grequests", "websockets", "websocket", "socks",
}


def server_modules():
    files = [SERVER_DIR / "server.py"]
    for package in ("wiki_backend", "manifold_security"):
        files += sorted((SERVER_DIR / package).rglob("*.py"))
    return files


def imported_names(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.module
            for alias in node.names:
                yield node.module + "." + alias.name


def test_there_are_server_modules_to_scan():
    assert len(server_modules()) > 20


@pytest.mark.parametrize("path", server_modules(), ids=lambda p: str(p.relative_to(SERVER_DIR)))
def test_no_server_module_imports_an_http_client_library(path):
    found = {name for name in imported_names(path)
             if name in HTTP_CLIENT_MODULES or name.split(".")[0] in {"requests", "httpx", "aiohttp", "urllib3"}}
    assert not found, "%s imports an HTTP client: %s" % (path.name, sorted(found))


def test_the_scan_catches_a_client_import(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("import urllib.request\nfrom http import client\nfrom requests import get\n")
    names = set(imported_names(bad))
    assert "urllib.request" in names and "requests" in names
