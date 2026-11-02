# SPDX-License-Identifier: Apache-2.0
"""The principal authentication middleware, run on its own against a temporary store (PHASE_1_PLAN T10)."""

import asyncio
import base64
import json

import pytest

from manifold_security import principals, tokens
from manifold_security.context import SCOPE_KEY
from wiki_backend.auth import PrincipalAuthMiddleware, StoreAccess


def call(world, path, authorization=None, scope_type="http", store=None):
    """Run a request through the middleware; return (status, reached_app, headers, body, scope)."""
    seen = {"reached": False, "messages": []}

    async def app(scope, receive, send):
        seen["reached"] = True
        seen["scope"] = scope
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    async def send(message):
        seen["messages"].append(message)

    scope = {"type": scope_type, "path": path,
             "headers": [(b"authorization", authorization.encode())] if authorization else []}
    middleware = PrincipalAuthMiddleware(app, store=store or StoreAccess(world.data_dir))
    asyncio.run(middleware(scope, None, send))
    start = next((m for m in seen["messages"] if m["type"] in ("http.response.start", "websocket.close")), {})
    body = next((m.get("body", b"") for m in seen["messages"] if m["type"] == "http.response.body"), b"")
    return start.get("status", start.get("code")), seen["reached"], start.get("headers", []), body, seen.get("scope")


def bearer(token):
    return "Bearer " + token


def basic(token):
    return "Basic " + base64.b64encode(("anyone:" + token).encode()).decode()


@pytest.mark.parametrize("header", [bearer, basic])
def test_bearer_and_basic_both_work(auth_world, header):
    status, reached, _, _, scope = call(auth_world, "/mcp", header(auth_world.human_token))
    assert (status, reached) == (200, True)
    caller = scope[SCOPE_KEY]
    assert (caller.name, caller.kind, caller.roles) == ("alice", "human", ("contributor",))


@pytest.mark.parametrize("path", ["/mcp", "/sse", "/messages/", "/ingest", "/docs/", "/docs/raw/x.md", "/",
                                  "/health/../docs", "/healthz", "/HEALTH"])
def test_protected_paths_need_a_credential(auth_world, path):
    status, reached, headers, _, _ = call(auth_world, path)
    assert (status, reached) == (401, False)
    challenges = [v for k, v in headers if k == b"www-authenticate"]
    assert any(c.startswith(b"Bearer") for c in challenges) and any(c.startswith(b"Basic") for c in challenges)


def test_a_wrong_and_a_missing_credential_get_the_same_answer(auth_world):
    wrong = call(auth_world, "/mcp", bearer(auth_world.human_credential.token + "x"))
    unknown = call(auth_world, "/mcp", bearer("mf_000000000000_" + "a" * 43))
    malformed = call(auth_world, "/mcp", bearer("not-a-credential"))
    missing = call(auth_world, "/mcp")
    assert {r[0] for r in (wrong, unknown, malformed, missing)} == {401}
    assert {r[3] for r in (wrong, unknown, malformed, missing)} == {missing[3]}
    assert json.loads(missing[3])["message"] == "authentication required"


def test_a_revoked_credential_is_refused_on_the_very_next_request(auth_world):
    store = StoreAccess(auth_world.data_dir)
    assert call(auth_world, "/mcp", bearer(auth_world.human_token), store=store)[:2] == (200, True)
    tokens.revoke_credential(auth_world.conn, auth_world.human_credential.credential_id)
    status, reached, _, body, _ = call(auth_world, "/mcp", bearer(auth_world.human_token), store=store)
    assert (status, reached) == (401, False)
    assert json.loads(body)["message"] == "your access was removed or has expired"


def test_revoking_one_credential_leaves_the_other_working(auth_world):
    tokens.revoke_credential(auth_world.conn, auth_world.human_credential.credential_id)
    assert call(auth_world, "/mcp", bearer(auth_world.agent_token))[:2] == (200, True)


def test_a_disabled_principal_is_refused_and_told_why(auth_world):
    principals.disable_principal(auth_world.conn, "build-bot")
    status, reached, _, body, _ = call(auth_world, "/mcp", bearer(auth_world.agent_token))
    assert (status, reached) == (401, False)
    assert json.loads(body)["message"] == "your access was removed or has expired"
    principals.enable_principal(auth_world.conn, "build-bot")
    assert call(auth_world, "/mcp", bearer(auth_world.agent_token))[:2] == (200, True)


def test_an_expired_credential_is_refused_and_told_why(auth_world):
    expired = tokens.issue_credential(auth_world.conn, auth_world.human.id, "old", expires_at="2000-01-01T00:00:00Z")
    status, _, _, body, _ = call(auth_world, "/mcp", bearer(expired.token))
    assert status == 401 and json.loads(body)["message"] == "your access was removed or has expired"


def test_a_revoked_credential_with_a_wrong_secret_is_not_told_anything(auth_world):
    tokens.revoke_credential(auth_world.conn, auth_world.human_credential.credential_id)
    guess = "mf_%s_%s" % (auth_world.human_credential.credential_id, "z" * 43)
    body = call(auth_world, "/mcp", bearer(guess))[3]
    assert json.loads(body)["message"] == "authentication required"


def test_health_is_open_and_marks_the_caller_only_when_the_credential_is_good(auth_world):
    status, reached, _, _, scope = call(auth_world, "/health")
    assert (status, reached) == (200, True) and SCOPE_KEY not in scope
    scope = call(auth_world, "/health", bearer(auth_world.human_token))[4]
    assert scope[SCOPE_KEY].name == "alice"
    assert call(auth_world, "/health", bearer("wrong"))[:2] == (200, True)


def test_an_empty_store_refuses_everything_but_health(tmp_path):
    from manifold_security.store import open_store
    conn = open_store(tmp_path / "empty", wiki_root=tmp_path / "wiki-root")
    world = type("World", (), {"data_dir": tmp_path / "empty"})
    assert call(world, "/mcp", bearer("mf_000000000000_" + "a" * 43))[:2] == (401, False)
    assert call(world, "/mcp")[:2] == (401, False)
    assert call(world, "/health")[:2] == (200, True)
    conn.close()


def test_an_unusable_store_fails_closed(tmp_path, monkeypatch):
    world = type("World", (), {"data_dir": tmp_path / "wiki-root" / "inside"})
    monkeypatch.setenv("CONTAINER_WIKI_ROOT", str(tmp_path / "wiki-root"))
    status, reached, _, body, _ = call(world, "/mcp", bearer("anything"))
    assert (status, reached) == (503, False)
    assert call(world, "/health")[:2] == (200, True)


def test_lifespan_scopes_pass_through(auth_world):
    reached = []

    async def app(scope, receive, send):
        reached.append(scope["type"])

    asyncio.run(PrincipalAuthMiddleware(app, store=StoreAccess(auth_world.data_dir))({"type": "lifespan"}, None, None))
    assert reached == ["lifespan"]


def test_websockets_are_closed_without_a_credential(auth_world):
    assert call(auth_world, "/mcp", scope_type="websocket")[:2] == (1008, False)
