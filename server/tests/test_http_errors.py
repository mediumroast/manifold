# SPDX-License-Identifier: Apache-2.0
"""The HTTP layer's errors for an authenticated caller (PHASE_4_PLAN Task 21, INT-2 Problem).

The host, origin, 401, 403 and 421 refusals are tested in `test_request_guard.py`, `test_auth.py`
and `test_docs_route_policy.py`; this file covers what an authenticated client gets for a bad
request: the status, and that the body shows no stack trace, file path or secret.
"""

import json
import re

import pytest

pytest.importorskip("fastmcp")

from starlette.testclient import TestClient  # noqa: E402

LEAKS = ("Traceback", 'File "', "/Users/", "/private/", "/var/", "/tmp/", "site-packages")
SOURCE_FILE = re.compile(r"\.py\b")  # a Python file name (not the "pydantic" in a documentation link)
OVERSIZED = 6 * 1024 * 1024


@pytest.fixture()
def http(monkeypatch, wiki_root, auth_world):
    """(client, headers, forbidden strings): an authenticated client of the real ASGI app, no network."""
    import server
    monkeypatch.setattr(server, "WIKI_ROOT", wiki_root)
    headers = {"Authorization": "Bearer " + auth_world.human_token,
               "Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    forbidden = LEAKS + (auth_world.human_token, auth_world.agent_token, str(wiki_root), str(auth_world.data_dir))
    with TestClient(server.asgi_app, base_url="http://127.0.0.1:8686") as client:
        yield client, headers, forbidden


def assert_clean(response, forbidden):
    for text in forbidden:
        assert text not in response.text, "the body of the %s response contains %r" % (response.status_code, text)
    assert not SOURCE_FILE.search(response.text), "the body names a Python file"


def rpc_body(response):
    """The JSON-RPC message of a JSON or server-sent-events response."""
    if "text/event-stream" in response.headers.get("content-type", ""):
        data = [line[len("data:"):].strip() for line in response.text.splitlines() if line.startswith("data:")]
        return json.loads(data[-1])
    return response.json()


@pytest.fixture()
def session(http):
    """The headers of an initialised MCP session."""
    client, headers, _ = http
    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "t", "version": "1"}}}
    opened = client.post("/mcp", json=init, headers=headers)
    assert opened.status_code == 200
    with_session = {**headers, "mcp-session-id": opened.headers["mcp-session-id"]}
    client.post("/mcp", json={"jsonrpc": "2.0", "method": "notifications/initialized"}, headers=with_session)
    return with_session


def call_tool(client, headers, name, arguments):
    message = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    return client.post("/mcp", json=message, headers=headers)


def test_a_malformed_json_body_is_a_400_parse_error(http):
    client, headers, forbidden = http
    response = client.post("/mcp", content=b"{not json", headers=headers)
    assert response.status_code == 400
    assert rpc_body(response)["error"]["code"] == -32700
    assert_clean(response, forbidden)


def test_an_unknown_tool_name_is_a_tool_error_that_names_the_tool(http, session):
    client, _, forbidden = http
    response = call_tool(client, session, "no_such_tool", {})
    result = rpc_body(response)["result"]
    assert response.status_code == 200 and result["isError"] is True
    assert "no_such_tool" in result["content"][0]["text"]
    assert_clean(response, forbidden)


def test_a_missing_required_argument_is_a_tool_error_that_names_the_argument(http, session):
    client, _, forbidden = http
    response = call_tool(client, session, "wiki_read_tool", {})
    result = rpc_body(response)["result"]
    assert result["isError"] is True and "path" in result["content"][0]["text"]
    assert_clean(response, forbidden)


def test_a_wrong_argument_type_is_a_tool_error_that_names_the_argument(http, session):
    client, _, forbidden = http
    response = call_tool(client, session, "wiki_read_tool", {"path": 5})
    result = rpc_body(response)["result"]
    assert result["isError"] is True and "path" in result["content"][0]["text"]
    assert_clean(response, forbidden)


def test_a_get_that_does_not_accept_an_event_stream_is_a_406(http):
    client, headers, forbidden = http
    response = client.get("/mcp", headers={**headers, "Accept": "application/json"})
    assert response.status_code == 406
    assert_clean(response, forbidden)


def test_a_get_without_a_session_is_a_400(http):
    client, headers, forbidden = http
    response = client.get("/mcp", headers={**headers, "Accept": "text/event-stream"})
    assert response.status_code == 400
    assert_clean(response, forbidden)


def test_a_get_for_a_session_that_does_not_exist_is_a_404(http):
    client, headers, forbidden = http
    response = client.get("/mcp", headers={**headers, "Accept": "text/event-stream", "mcp-session-id": "nope"})
    assert response.status_code == 404
    assert_clean(response, forbidden)


def test_an_oversized_mcp_body_is_a_413(http):
    client, headers, forbidden = http
    response = client.post("/mcp", content=b"x" * OVERSIZED, headers=headers)
    assert response.status_code == 413
    assert_clean(response, forbidden)


def test_an_oversized_ingest_body_is_a_413_and_writes_nothing(http, wiki_root):
    client, headers, forbidden = http
    response = client.post("/ingest", json={"component": "acme-api", "content": "x" * OVERSIZED}, headers=headers)
    assert response.status_code == 413
    assert not (wiki_root / "raw").exists()
    assert_clean(response, forbidden)
