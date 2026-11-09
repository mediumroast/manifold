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


LOOPBACK_NAMES = {None, "", "localhost", "127.0.0.1", "::1", "0.0.0.0"}


def _is_loopback_target(host):
    import ipaddress
    if host in LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(str(host).strip("[]")).is_loopback
    except ValueError:
        return False


def test_A11_no_outside_connection_is_attempted_at_run_time(tool_world, wiki_root, monkeypatch):
    """PHASE_1_TEST_PLAN A11 (INT-1 S13): connect and name lookups for anything but loopback are recorded and refused."""
    import socket
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.testclient import TestClient
    import server
    from wiki_backend.auth import PrincipalAuthMiddleware, StoreAccess
    from wiki_backend.guard import RoutePolicyMiddleware

    attempts = []
    real_connect, real_getaddrinfo = socket.socket.connect, socket.getaddrinfo

    def connect(self, address):
        host = address[0] if isinstance(address, tuple) else None  # a unix path or socketpair is local
        if not _is_loopback_target(host):
            attempts.append(("connect", address))
            raise OSError("outside connection refused by the test")
        return real_connect(self, address)

    def getaddrinfo(host, *args, **kwargs):
        if not _is_loopback_target(host if not isinstance(host, bytes) else host.decode()):
            attempts.append(("getaddrinfo", host))
            raise OSError("outside name lookup refused by the test")
        return real_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", connect)
    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)

    (wiki_root / "raw").mkdir()
    tool_world.who("ann", roles=["contributor", "registrar"], grants=["acme-api", "acme-web", "acme-cli", "_shared"])
    token = tool_world.tokens["ann"]
    headers = {"Authorization": "Bearer " + token}
    calls = [
        ("wiki_read_tool", {"path": "wiki/log.md"}),
        ("wiki_write_page_tool", {"path": "wiki/decisions/a11.md", "content": "# A11\n", "message": "m"}),
        ("wiki_handoff_tool", {"action": "create", "source": "acme-api", "target": "acme-web", "type": "feature",
                               "priority": "low", "title": "A11", "summary": "s", "what_needs_to_happen": "w"}),
        ("wiki_register_component_tool", {"name": "a11-new", "description": "d", "repo": "https://example.test/r",
                                          "owner": "o", "skip_source_docs": True}),
        ("wiki_component_manage_tool", {"action": "archive", "name": "acme-cli", "reason": "retired"}),
    ]
    for tool, arguments in calls:
        result = tool_world.call("ann", tool, **arguments)
        assert not result.get("error") and not result.get("refused"), (tool, result)

    docs = Starlette(routes=server._build_docs_routes(wiki_root),
                     middleware=[Middleware(PrincipalAuthMiddleware, store=StoreAccess(tool_world.data_dir)),
                                 Middleware(RoutePolicyMiddleware, store=StoreAccess(tool_world.data_dir))])
    with TestClient(server.asgi_app, base_url="http://127.0.0.1:8686") as client:
        assert client.get("/health").status_code == 200
        ingested = client.post("/ingest", json={"component": "acme-api", "content": "# doc\n"}, headers=headers)
        assert ingested.status_code == 200, ingested.text
    with TestClient(docs, base_url="http://127.0.0.1:8686") as client:
        assert client.get("/docs/", headers=headers).status_code == 200

    assert attempts == []


def test_the_scan_catches_a_client_import(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text("import urllib.request\nfrom http import client\nfrom requests import get\n")
    names = set(imported_names(bad))
    assert "urllib.request" in names and "requests" in names
