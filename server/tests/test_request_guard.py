# SPDX-License-Identifier: Apache-2.0
"""The Host and Origin guard (PHASE_1_PLAN T19)."""

import asyncio

import pytest

from manifold_security import settings
from manifold_security.request_guard import (
    RequestGuardMiddleware, allowed_host_values, allowed_origin_values,
)


def call(host=None, method="GET", origin=None, path="/mcp", extra_hosts=(), extra_origins=(), scope_type="http"):
    """Run one request through the guard; return (status or None, reached the app)."""
    seen = {"reached": False, "messages": []}

    async def app(scope, receive, send):
        seen["reached"] = True
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    async def send(message):
        seen["messages"].append(message)

    headers = []
    if host is not None:
        headers.append((b"host", host.encode()))
    if origin is not None:
        headers.append((b"origin", origin.encode()))
    scope = {"type": scope_type, "method": method, "path": path, "headers": headers}
    guard = RequestGuardMiddleware(app, lambda: (extra_hosts, extra_origins), port=8686)
    asyncio.run(guard(scope, None, send))
    first = next((m for m in seen["messages"] if m["type"] in ("http.response.start", "websocket.close")), {})
    return first.get("status", first.get("code")), seen["reached"]


# ── Host ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("host", ["127.0.0.1:8686", "localhost:8686", "[::1]:8686", "LOCALHOST:8686"])
def test_the_served_addresses_are_accepted(host):
    assert call(host) == (200, True)


@pytest.mark.parametrize("host", ["evil.test", "evil.test:8686", "127.0.0.1:9999", "127.0.0.1", "localhost.evil.test:8686",
                                  "", None])
def test_any_other_host_is_refused_with_421_and_never_reaches_the_app(host):
    assert call(host) == (421, False)


def test_a_configured_public_host_is_accepted_with_or_without_the_port():
    assert call("wiki.example.test", extra_hosts=["wiki.example.test"]) == (200, True)
    assert call("wiki.example.test:8686", extra_hosts=["wiki.example.test"]) == (200, True)
    assert call("wiki.example.test:8443", extra_hosts=["wiki.example.test:8443"]) == (200, True)
    assert call("wiki.example.test:8443", extra_hosts=["wiki.example.test"]) == (421, False)
    assert call("other.example.test", extra_hosts=["wiki.example.test"]) == (421, False)


def test_health_accepts_a_loopback_name_on_any_port_for_the_container_probe_and_nothing_else():
    assert call("127.0.0.1:12345", path="/health") == (200, True)
    assert call("localhost", path="/health") == (200, True)
    assert call("evil.test", path="/health") == (421, False)
    assert call("127.0.0.1:12345", path="/mcp") == (421, False)


def test_a_websocket_with_the_wrong_host_is_closed():
    assert call("evil.test", scope_type="websocket") == (1008, False)


def test_the_guard_ignores_other_scope_types():
    reached = []

    async def app(scope, receive, send):
        reached.append(scope["type"])
    asyncio.run(RequestGuardMiddleware(app, lambda: ((), ()))({"type": "lifespan"}, None, None))
    assert reached == ["lifespan"]


# ── Origin ───────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_a_foreign_origin_on_a_changing_request_is_refused_with_403(method):
    assert call("127.0.0.1:8686", method=method, origin="https://evil.test") == (403, False)
    assert call("127.0.0.1:8686", method=method, origin="null") == (403, False)


def test_a_served_origin_is_accepted():
    for origin in ("http://127.0.0.1:8686", "https://localhost:8686", "http://[::1]:8686"):
        assert call("127.0.0.1:8686", method="POST", origin=origin) == (200, True)


def test_no_origin_passes_so_mcp_clients_and_scripts_work():
    assert call("127.0.0.1:8686", method="POST") == (200, True)


def test_a_foreign_origin_on_a_read_only_request_is_not_checked_here():
    assert call("127.0.0.1:8686", method="GET", origin="https://evil.test") == (200, True)


def test_a_configured_origin_and_the_public_hosts_origins_are_accepted():
    assert call("127.0.0.1:8686", method="POST", origin="https://app.example.test",
                extra_origins=["https://app.example.test"]) == (200, True)
    assert call("wiki.example.test", method="POST", origin="https://wiki.example.test",
                extra_hosts=["wiki.example.test"]) == (200, True)
    assert call("wiki.example.test", method="POST", origin="https://evil.test",
                extra_hosts=["wiki.example.test"]) == (403, False)


def test_the_value_helpers():
    assert "127.0.0.1:8686" in allowed_host_values(8686)
    assert "wiki.test:8686" in allowed_host_values(8686, ["wiki.test"])
    assert "https://wiki.test" in allowed_origin_values(["wiki.test"])


# ── the real server ──────────────────────────────────────────────────────────

def _client(monkeypatch, root, host="127.0.0.1:8686"):
    pytest.importorskip("fastmcp")
    from starlette.testclient import TestClient
    import server
    monkeypatch.setattr(server, "WIKI_ROOT", root)
    return TestClient(server.asgi_app, base_url="http://" + host)


def test_the_server_refuses_a_wrong_host_before_asking_for_a_credential(monkeypatch, wiki_root, auth_world):
    headers = {"Authorization": "Bearer " + auth_world.human_token}
    assert _client(monkeypatch, wiki_root, "evil.test").get("/health", headers=headers).status_code == 421
    assert _client(monkeypatch, wiki_root).get("/health", headers=headers).status_code == 200


def test_the_server_refuses_a_foreign_origin_even_with_a_good_credential(monkeypatch, wiki_root, auth_world):
    client = _client(monkeypatch, wiki_root)
    good = {"Authorization": "Bearer " + auth_world.human_token}
    body = {"component": "acme-api", "content": "# hi"}
    assert client.post("/ingest", json=body, headers={**good, "Origin": "https://evil.test"}).status_code == 403
    assert not (wiki_root / "raw").exists()


def test_a_host_added_by_the_setting_applies_at_once(monkeypatch, wiki_root, auth_world):
    client = _client(monkeypatch, wiki_root, "wiki.example.test")
    assert client.get("/health").status_code == 421
    settings.set_value(auth_world.conn, "allowed_hosts", "wiki.example.test")
    assert client.get("/health").status_code == 200
    settings.unset(auth_world.conn, "allowed_hosts")
    assert client.get("/health").status_code == 421
