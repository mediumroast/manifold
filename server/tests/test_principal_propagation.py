# SPDX-License-Identifier: Apache-2.0
"""Tools see the caller behind each call, over /mcp and over /sse (PHASE_1_PLAN T11).

Real server process, two principals with their own generated credentials.  The tool used
is ``wiki_ping_tool``, which reports the principal the server attributes the call to.
"""

import asyncio
import json
import threading
import urllib.error
import urllib.request

import pytest

pytest.importorskip("fastmcp")

from tests.realserver import EXAMPLE, running_server  # noqa: E402

pytestmark = pytest.mark.skipif(not EXAMPLE.is_dir(), reason="no examples/acme beside the server")


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    spec = [("alice", "human", ["contributor"]), ("build-bot", "agent", ["reader"])]
    with running_server(tmp_path_factory.mktemp("propagation"), spec) as running:
        yield running


def _headers(server, name):
    return {"Authorization": "Bearer " + server["tokens"][name]}


async def _ping_over(server, transport_cls, path, name, calls=1):
    from fastmcp import Client
    transport = transport_cls(server["base"] + path, headers=_headers(server, name))
    async with Client(transport) as client:
        return [(await client.call_tool("wiki_ping_tool", {})).data["principal"] for _ in range(calls)]


def _streamable():
    from fastmcp.client.transports import StreamableHttpTransport
    return StreamableHttpTransport


def _sse():
    from fastmcp.client.transports import SSETransport
    return SSETransport


def test_each_call_over_mcp_is_attributed_to_its_own_credential(server):
    first = asyncio.run(_ping_over(server, _streamable(), "/mcp", "alice", calls=2))
    second = asyncio.run(_ping_over(server, _streamable(), "/mcp", "build-bot"))
    assert {p["name"] for p in first} == {"alice"} and first[0]["kind"] == "human"
    assert first[0]["roles"] == ["contributor"]
    assert second[0]["name"] == "build-bot" and second[0]["kind"] == "agent" and second[0]["roles"] == ["reader"]


def test_each_call_over_sse_is_attributed_to_its_own_credential(server):
    first = asyncio.run(_ping_over(server, _sse(), "/sse", "alice", calls=2))
    second = asyncio.run(_ping_over(server, _sse(), "/sse", "build-bot"))
    assert {p["name"] for p in first} == {"alice"}
    assert second[0]["name"] == "build-bot" and second[0]["roles"] == ["reader"]


def test_two_sse_sessions_open_at_once_do_not_mix_callers(server):
    async def both():
        return await asyncio.gather(
            _ping_over(server, _sse(), "/sse", "alice", calls=3),
            _ping_over(server, _sse(), "/sse", "build-bot", calls=3),
        )
    alice, bot = asyncio.run(both())
    assert {p["name"] for p in alice} == {"alice"}
    assert {p["name"] for p in bot} == {"build-bot"}


def test_two_mcp_sessions_open_at_once_do_not_mix_callers(server):
    async def both():
        return await asyncio.gather(
            _ping_over(server, _streamable(), "/mcp", "alice", calls=3),
            _ping_over(server, _streamable(), "/mcp", "build-bot", calls=3),
        )
    alice, bot = asyncio.run(both())
    assert {p["name"] for p in alice} == {"alice"}
    assert {p["name"] for p in bot} == {"build-bot"}


# ── a session id is not a credential ─────────────────────────────────────────

def _open_sse_session(server, name):
    """Open GET /sse as ``name`` in a thread; return (session POST path, close function)."""
    request = urllib.request.Request(server["base"] + "/sse", headers=_headers(server, name))
    response = urllib.request.urlopen(request, timeout=10)
    endpoint = None
    event = None
    while endpoint is None:
        line = response.readline().decode().strip()
        if line.startswith("event:"):
            event = line.split(":", 1)[1].strip()
        elif line.startswith("data:") and event == "endpoint":
            endpoint = line.split(":", 1)[1].strip()
    return endpoint, response.close


def _post(server, endpoint, name, body):
    headers = dict(_headers(server, name) if name else {}, **{"Content-Type": "application/json"})
    request = urllib.request.Request(server["base"] + endpoint, data=json.dumps(body).encode(), headers=headers,
                                     method="POST")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def test_a_post_to_someone_elses_sse_session_is_refused(server):
    endpoint, close = _open_sse_session(server, "alice")
    try:
        body = {"jsonrpc": "2.0", "id": 1, "method": "ping"}
        assert _post(server, endpoint, "build-bot", body) == 403
        assert _post(server, endpoint, None, body) == 401
        assert _post(server, endpoint, "alice", body) == 202
    finally:
        close()
