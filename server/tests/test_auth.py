# SPDX-License-Identifier: Apache-2.0
"""Tests for the shared-token authentication: the rules, the middleware, and the server routes."""

import asyncio
import base64

import pytest

from wiki_backend.auth import (
    AuthConfigError,
    TokenAuthMiddleware,
    check_startup,
    configured_token,
    is_authorized,
    is_loopback,
)

TOKEN = "t" * 32


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    monkeypatch.delenv("MANIFOLD_TOKEN", raising=False)
    monkeypatch.delenv("MANIFOLD_TOKEN_FILE", raising=False)


def basic(user, password):
    return "Basic " + base64.b64encode(("%s:%s" % (user, password)).encode()).decode()


# ── reading the token ────────────────────────────────────────────────────────

def test_no_token_means_authentication_is_off():
    assert configured_token() is None


def test_token_comes_from_the_environment_and_is_stripped(monkeypatch):
    monkeypatch.setenv("MANIFOLD_TOKEN", "  " + TOKEN + "\n")
    assert configured_token() == TOKEN


def test_token_can_come_from_a_file(monkeypatch, tmp_path):
    secret = tmp_path / "token"
    secret.write_text(TOKEN + "\n")
    monkeypatch.setenv("MANIFOLD_TOKEN_FILE", str(secret))
    assert configured_token() == TOKEN


def test_the_environment_wins_over_the_file(monkeypatch, tmp_path):
    secret = tmp_path / "token"
    secret.write_text("f" * 32)
    monkeypatch.setenv("MANIFOLD_TOKEN_FILE", str(secret))
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)
    assert configured_token() == TOKEN


def test_unreadable_token_file_is_an_error(monkeypatch, tmp_path):
    monkeypatch.setenv("MANIFOLD_TOKEN_FILE", str(tmp_path / "missing"))
    with pytest.raises(AuthConfigError, match="could not be read"):
        configured_token()


# ── loopback ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("host", ["127.0.0.1", "127.1.2.3", "::1", "[::1]", "localhost", "LOCALHOST"])
def test_loopback_hosts(host):
    assert is_loopback(host)


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.5", "10.0.0.1", "example.test", "", "my-laptop.local"])
def test_other_hosts_are_not_loopback(host):
    assert not is_loopback(host)


# ── startup rules ────────────────────────────────────────────────────────────

def test_loopback_without_a_token_starts_with_a_warning():
    assert "Authentication is off" in check_startup("127.0.0.1")


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.5"])
def test_non_loopback_without_a_token_is_refused(host):
    with pytest.raises(AuthConfigError, match="Refusing to listen"):
        check_startup(host)


def test_non_loopback_with_a_token_starts(monkeypatch):
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)
    assert check_startup("0.0.0.0") is None


def test_a_short_token_is_refused_even_on_loopback(monkeypatch):
    monkeypatch.setenv("MANIFOLD_TOKEN", "x" * 23)
    with pytest.raises(AuthConfigError, match="too short"):
        check_startup("127.0.0.1")
    monkeypatch.setenv("MANIFOLD_TOKEN", "x" * 24)
    assert check_startup("127.0.0.1") is None


# ── deciding on a header ─────────────────────────────────────────────────────

@pytest.mark.parametrize("header", [
    "Bearer " + TOKEN, "bearer " + TOKEN, "BEARER   " + TOKEN,
    basic("anyone", TOKEN), basic("", TOKEN), "basic " + base64.b64encode((":" + TOKEN).encode()).decode(),
])
def test_accepted_headers(header):
    assert is_authorized(header, TOKEN)


@pytest.mark.parametrize("header", [
    None, "", "Bearer", "Bearer ", "Bearer wrong", "Bearer " + TOKEN + "x", "Bearer " + TOKEN[:-1],
    TOKEN, "Token " + TOKEN, basic("user", "wrong"), basic(TOKEN, "wrong"), "Basic !!!notbase64!!!",
    "Basic " + base64.b64encode(TOKEN.encode()).decode(),  # no colon: not user:password
    "Basic " + base64.b64encode(b"\xff\xfe:x").decode(),
])
def test_rejected_headers(header):
    assert not is_authorized(header, TOKEN)


def test_everything_is_allowed_when_authentication_is_off():
    assert is_authorized(None, None) and is_authorized("Bearer anything", None)


# ── the middleware ───────────────────────────────────────────────────────────

def call(path, authorization=None, scope_type="http", token=None, monkeypatch=None):
    """Run a request through the middleware; return (status or None, reached_app, response headers)."""
    seen = {"reached": False, "messages": []}

    async def app(scope, receive, send):
        seen["reached"] = True
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    async def send(message):
        seen["messages"].append(message)

    scope = {"type": scope_type, "path": path,
             "headers": [(b"authorization", authorization.encode())] if authorization else []}
    asyncio.run(TokenAuthMiddleware(app)(scope, None, send))
    start = next((m for m in seen["messages"] if m["type"] in ("http.response.start", "websocket.close")), {})
    return start.get("status", start.get("code")), seen["reached"], start.get("headers", [])


@pytest.fixture()
def protected(monkeypatch):
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)


@pytest.mark.parametrize("path", ["/mcp", "/sse", "/messages/", "/ingest", "/docs/", "/docs/raw/x.md", "/", "/health/../docs", "/healthz", "/HEALTH"])
def test_protected_paths_need_the_token(protected, path):
    status, reached, headers = call(path)
    assert (status, reached) == (401, False)
    challenges = [v for k, v in headers if k == b"www-authenticate"]
    assert any(c.startswith(b"Bearer") for c in challenges) and any(c.startswith(b"Basic") for c in challenges)


def test_a_bad_token_is_refused(protected):
    assert call("/mcp", "Bearer nope")[:2] == (401, False)


@pytest.mark.parametrize("header", ["Bearer " + TOKEN, basic("me", TOKEN)])
def test_the_right_token_reaches_the_app(protected, header):
    assert call("/mcp", header)[:2] == (200, True)


def test_health_is_open(protected):
    assert call("/health")[:2] == (200, True)


def test_without_a_token_everything_is_open():
    assert call("/ingest")[:2] == (200, True)


def test_an_unreadable_token_file_denies_everything_instead_of_opening_up(monkeypatch, tmp_path):
    monkeypatch.setenv("MANIFOLD_TOKEN_FILE", str(tmp_path / "missing"))
    assert call("/mcp", "Bearer anything")[:2] == (401, False)
    assert call("/health")[:2] == (200, True)


def test_lifespan_scopes_pass_through(protected):
    reached = []

    async def app(scope, receive, send):
        reached.append(scope["type"])

    asyncio.run(TokenAuthMiddleware(app)({"type": "lifespan"}, None, None))
    assert reached == ["lifespan"]


def test_websockets_are_closed_without_the_token(protected):
    assert call("/mcp", scope_type="websocket")[:2] == (1008, False)


# ── the real server ──────────────────────────────────────────────────────────

def _client(monkeypatch, root):
    pytest.importorskip("fastmcp")
    from starlette.testclient import TestClient
    import server
    monkeypatch.setattr(server, "WIKI_ROOT", root)
    return TestClient(server.asgi_app)


@pytest.mark.parametrize("method,path", [
    ("post", "/mcp"), ("get", "/sse"), ("post", "/ingest"), ("get", "/docs/"), ("get", "/docs/raw/"), ("get", "/"),
])
def test_server_routes_refuse_a_request_without_the_token(monkeypatch, wiki_root, method, path):
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)
    response = getattr(_client(monkeypatch, wiki_root), method)(path, follow_redirects=False)
    assert response.status_code == 401


def test_ingest_writes_only_with_the_token(monkeypatch, wiki_root):
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)
    client = _client(monkeypatch, wiki_root)
    body = {"component": "acme-api", "content": "# hi"}
    assert client.post("/ingest", json=body).status_code == 401
    assert not (wiki_root / "raw").exists()
    ok = client.post("/ingest", json=body, headers={"Authorization": "Bearer " + TOKEN})
    assert ok.status_code == 200 and (wiki_root / ok.json()["path"]).read_text() == "# hi"


def test_a_browser_can_use_basic_authentication(monkeypatch, wiki_root):
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)
    client = _client(monkeypatch, wiki_root)
    # The wiki browser is mounted when the server is imported, so under test the page itself may not
    # exist (404); what matters is that the request got past authentication.
    assert client.get("/docs/log.md").status_code == 401
    assert client.get("/docs/log.md", headers={"Authorization": basic("anyone", TOKEN)}).status_code != 401


def test_health_gives_only_the_status_to_an_unauthenticated_caller(monkeypatch, wiki_root):
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)
    client = _client(monkeypatch, wiki_root)
    bare = client.get("/health")
    assert bare.status_code == 200 and bare.json() == {"status": "healthy"}
    detailed = client.get("/health", headers={"Authorization": "Bearer " + TOKEN})
    assert "checks" in detailed.json() and "wiki_root" in detailed.json()


def test_health_failure_is_still_a_500_without_details(monkeypatch, wiki_root):
    monkeypatch.setenv("MANIFOLD_TOKEN", TOKEN)
    (wiki_root / "manifold.yaml").unlink()
    bare = _client(monkeypatch, wiki_root).get("/health")
    assert bare.status_code == 500 and bare.json() == {"status": "unhealthy"}


def test_health_has_full_detail_when_authentication_is_off(monkeypatch, wiki_root):
    assert "checks" in _client(monkeypatch, wiki_root).get("/health").json()


def test_the_server_refuses_to_start_on_all_interfaces_without_a_token(monkeypatch):
    pytest.importorskip("fastmcp")
    import server
    monkeypatch.setenv("MANIFOLD_HOST", "0.0.0.0")
    with pytest.raises(AuthConfigError):
        server._check_auth_settings()
