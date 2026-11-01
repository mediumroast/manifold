# SPDX-License-Identifier: Apache-2.0
"""Principal authentication: header parsing, loopback, and the real server's routes (PHASE_1_PLAN T10)."""

import base64

import pytest

from wiki_backend import auth
from wiki_backend.auth import _presented_secret, is_loopback


def basic(user, password):
    return "Basic " + base64.b64encode(("%s:%s" % (user, password)).encode()).decode()


# ── no shared token any more ─────────────────────────────────────────────────

@pytest.mark.parametrize("name", ["TokenAuthMiddleware", "configured_token", "check_startup",
                                  "is_authorized", "AuthConfigError"])
def test_the_shared_token_machinery_is_gone(name):
    assert not hasattr(auth, name)


def test_the_old_environment_variables_are_not_read(monkeypatch, auth_world):
    monkeypatch.setenv("MANIFOLD_TOKEN", "t" * 32)
    monkeypatch.setenv("MANIFOLD_TOKEN_FILE", "/nonexistent")
    assert not auth.StoreAccess().authenticate("t" * 32).caller


# ── loopback ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("host", ["127.0.0.1", "127.1.2.3", "::1", "[::1]", "localhost", "LOCALHOST"])
def test_loopback_hosts(host):
    assert is_loopback(host)


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.5", "10.0.0.1", "example.test", "", "my-laptop.local"])
def test_other_hosts_are_not_loopback(host):
    assert not is_loopback(host)


# ── reading a header ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("header", [
    "Bearer SECRET", "bearer SECRET", "BEARER   SECRET",
    basic("anyone", "SECRET"), basic("", "SECRET"),
    "basic " + base64.b64encode(b":SECRET").decode(),
])
def test_secrets_are_read_from_bearer_and_basic(header):
    assert _presented_secret(header) == "SECRET"


@pytest.mark.parametrize("header", [
    "", "Bearer", "Bearer ", "SECRET", "Token SECRET", "Basic !!!notbase64!!!",
    "Basic " + base64.b64encode(b"SECRET").decode(),  # no colon: not user:password
    "Basic " + base64.b64encode(b"\xff\xfe:x").decode(),
])
def test_other_headers_carry_no_secret(header):
    assert _presented_secret(header) is None


# ── the real server ──────────────────────────────────────────────────────────

def _client(monkeypatch, root):
    pytest.importorskip("fastmcp")
    from starlette.testclient import TestClient
    import server
    monkeypatch.setattr(server, "WIKI_ROOT", root)
    return TestClient(server.asgi_app, base_url="http://127.0.0.1:8686")  # an address the Host guard accepts


@pytest.mark.parametrize("method,path", [
    ("post", "/mcp"), ("get", "/sse"), ("post", "/ingest"), ("get", "/docs/"), ("get", "/docs/raw/"), ("get", "/"),
])
def test_server_routes_refuse_a_request_without_a_credential(monkeypatch, wiki_root, auth_world, method, path):
    response = getattr(_client(monkeypatch, wiki_root), method)(path, follow_redirects=False)
    assert response.status_code == 401


def test_ingest_writes_only_with_a_credential(monkeypatch, wiki_root, auth_world):
    from manifold_security import principals
    principals.add_grant(auth_world.conn, "alice", "acme-api")  # a contributor still needs a grant on the component
    client = _client(monkeypatch, wiki_root)
    body = {"component": "acme-api", "content": "# hi"}
    assert client.post("/ingest", json=body).status_code == 401
    assert not (wiki_root / "raw").exists()
    ok = client.post("/ingest", json=body, headers={"Authorization": "Bearer " + auth_world.human_token})
    assert ok.status_code == 200 and (wiki_root / ok.json()["path"]).read_text() == "# hi"


def test_a_browser_can_use_basic_authentication(monkeypatch, wiki_root, auth_world):
    client = _client(monkeypatch, wiki_root)
    # The wiki browser is mounted when the server is imported, so under test the page itself may not
    # exist (404); what matters is that the request got past authentication.
    assert client.get("/docs/log.md").status_code == 401
    assert client.get("/docs/log.md", headers={"Authorization": basic("anyone", auth_world.human_token)}
                      ).status_code != 401


def test_health_gives_only_the_status_to_an_unauthenticated_caller(monkeypatch, wiki_root, auth_world):
    client = _client(monkeypatch, wiki_root)
    bare = client.get("/health")
    assert bare.status_code == 200 and bare.json() == {"status": "healthy"}
    detailed = client.get("/health", headers={"Authorization": "Bearer " + auth_world.human_token})
    assert "checks" in detailed.json() and "wiki_root" in detailed.json()


def test_health_ignores_a_wrong_credential_instead_of_refusing(monkeypatch, wiki_root, auth_world):
    response = _client(monkeypatch, wiki_root).get("/health", headers={"Authorization": "Bearer mf_nope_nope"})
    assert response.status_code == 200 and response.json() == {"status": "healthy"}


def test_health_failure_is_still_a_500_without_details(monkeypatch, wiki_root, auth_world):
    (wiki_root / "manifold.yaml").unlink()
    bare = _client(monkeypatch, wiki_root).get("/health")
    assert bare.status_code == 500 and bare.json() == {"status": "unhealthy"}


def test_the_server_refuses_to_start_when_the_store_cannot_be_opened(monkeypatch, tmp_path, wiki_root):
    pytest.importorskip("fastmcp")
    import server
    from manifold_security.store import StoreError
    monkeypatch.setenv("CONTAINER_WIKI_ROOT", str(tmp_path / "elsewhere"))
    monkeypatch.setenv("MANIFOLD_DATA_DIR", str(tmp_path / "elsewhere" / "inside"))
    with pytest.raises(StoreError, match="inside the instance repository"):
        server._check_auth_settings()
