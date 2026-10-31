# SPDX-License-Identifier: Apache-2.0
"""Smoke test of the real server process: start it, then use it the way a client does.

One server is started against a private copy of examples/acme, with a token, and the tests
share it. This is the check that the pieces fit together: configuration, authentication,
the MCP endpoints, the write path, the HTTP routes and the wiki browser.
"""

import asyncio
import base64
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

pytest.importorskip("fastmcp")

from wiki_backend.ping import _TOOL_NAMES  # noqa: E402

SERVER_DIR = Path(__file__).resolve().parents[1]
EXAMPLE = SERVER_DIR.parent / "examples" / "acme"
TOKEN = "smoke-test-token-0123456789abcdef"

pytestmark = pytest.mark.skipif(not EXAMPLE.is_dir(), reason="no examples/acme beside the server")


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    import shutil
    root = tmp_path_factory.mktemp("smoke") / "acme-wiki"
    shutil.copytree(EXAMPLE, root)
    for args in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t.test"],
                 ["add", "-A"], ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    port = _free_port()
    env = dict(os.environ, CONTAINER_WIKI_ROOT=str(root), PORT=str(port), MANIFOLD_TOKEN=TOKEN,
               MANIFOLD_HOST="127.0.0.1", PYTHONUNBUFFERED="1")
    env.pop("MANIFOLD_RELOAD", None)
    log = root.parent / "server.log"
    with open(log, "w") as out:
        process = subprocess.Popen([sys.executable, "server.py"], cwd=SERVER_DIR, env=env, stdout=out, stderr=out)
        base = "http://127.0.0.1:%d" % port
        try:
            deadline = time.time() + 30
            while time.time() < deadline:
                if process.poll() is not None:
                    pytest.fail("the server exited early:\n" + log.read_text())
                try:
                    urllib.request.urlopen(base + "/health", timeout=1).read()
                    break
                except (urllib.error.URLError, ConnectionError, OSError):
                    time.sleep(0.2)
            else:
                pytest.fail("the server did not start:\n" + log.read_text())
            yield {"base": base, "root": root}
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()


def request(server, path, method="GET", body=None, auth="bearer", read=True):
    headers = {}
    if auth == "bearer":
        headers["Authorization"] = "Bearer " + TOKEN
    elif auth == "basic":
        headers["Authorization"] = "Basic " + base64.b64encode(("anyone:" + TOKEN).encode()).decode()
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(server["base"] + path, data=data, headers=headers, method=method)
    try:
        response = urllib.request.urlopen(req, timeout=10)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read()
    try:
        return response.status, response.headers, response.read() if read else b""
    finally:
        response.close()


def mcp(server, name, arguments=None):
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport

    async def run():
        transport = StreamableHttpTransport(server["base"] + "/mcp", headers={"Authorization": "Bearer " + TOKEN})
        async with Client(transport) as client:
            return await client.call_tool(name, arguments or {})
    return asyncio.run(run()).data


# ── health and authentication ────────────────────────────────────────────────

def test_health_is_open_and_brief_without_the_token(server):
    status, _, body = request(server, "/health", auth=None)
    assert status == 200 and json.loads(body) == {"status": "healthy"}


def test_health_gives_the_checks_with_the_token(server):
    status, _, body = request(server, "/health")
    payload = json.loads(body)
    assert status == 200 and payload["checks"]["manifold.yaml"] == "ok (3 components)"


@pytest.mark.parametrize("method,path", [("POST", "/mcp"), ("GET", "/sse"), ("POST", "/ingest"), ("GET", "/docs/")])
def test_everything_else_needs_the_token(server, method, path):
    assert request(server, path, method=method, body={} if method == "POST" else None, auth=None)[0] == 401


def test_a_wrong_token_is_refused(server):
    req = urllib.request.Request(server["base"] + "/docs/", headers={"Authorization": "Bearer not-the-token-not-the-token"})
    with pytest.raises(urllib.error.HTTPError) as caught:
        urllib.request.urlopen(req, timeout=10)
    assert caught.value.code == 401


# ── the MCP endpoint ─────────────────────────────────────────────────────────

def test_the_server_lists_every_tool_ping_reports(server):
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport

    async def names():
        async with Client(StreamableHttpTransport(server["base"] + "/mcp", headers={"Authorization": "Bearer " + TOKEN})) as c:
            return {t.name for t in await c.list_tools()}
    listed = asyncio.run(names())
    assert listed == set(_TOOL_NAMES) and len(listed) == 15


def test_the_mcp_endpoint_refuses_a_client_without_the_token(server):
    from fastmcp import Client

    async def connect():
        async with Client(server["base"] + "/mcp") as c:
            await c.list_tools()
    with pytest.raises(Exception):
        asyncio.run(connect())


def test_ping_reports_the_server_name_and_status(server):
    result = mcp(server, "wiki_ping_tool")
    assert result["status"] == "connected" and result["server"] == "manifold" and result["tool_count"] == 15


def test_a_page_can_be_read(server):
    page = mcp(server, "wiki_read_tool", {"path": "wiki/components/acme-api.md"})
    assert "Acme API" in page["body"] and page["etag"]


def test_the_inventory_and_freshness_reflect_the_example(server):
    inventory = mcp(server, "wiki_inventory_tool")
    assert len(inventory["components"]) == 3 and len(inventory["handoffs"]) == 3
    assert [s["component"] for s in mcp(server, "wiki_freshness_tool")["stale"]] == ["acme-cli"]


# ── the write path ───────────────────────────────────────────────────────────

def _git_log(server, count=5):
    return subprocess.run(["git", "log", "--format=%an|%s", "-%d" % count], cwd=server["root"],
                          capture_output=True, text=True, check=True).stdout.splitlines()


def test_a_handoff_is_created_on_disk_and_committed(server):
    created = mcp(server, "wiki_handoff_tool", {
        "action": "create", "source": "acme-web", "target": "acme-cli", "type": "feature", "priority": "low",
        "title": "Smoke test handoff", "summary": "Created by the smoke test.", "what_needs_to_happen": "Nothing."})
    assert created["status"] == "created"
    assert (server["root"] / created["path"]).read_text().startswith("---")
    assert any(line.startswith("manifold|") and "Smoke test handoff" in line for line in _git_log(server))


def test_a_page_is_written_with_its_etag_and_a_stale_etag_is_refused(server):
    page = mcp(server, "wiki_read_tool", {"path": "wiki/decisions/2026-01-14-use-rest-for-orders.md"})
    changed = page["body"] + "\nAdded by the smoke test.\n"
    written = mcp(server, "wiki_write_page_tool", {"path": page["path"], "content": changed, "etag": page["etag"],
                                                   "message": "smoke: edit decision"})
    assert written.get("status") in ("updated", "created", "ok"), written
    assert "Added by the smoke test." in (server["root"] / page["path"]).read_text()
    again = mcp(server, "wiki_write_page_tool", {"path": page["path"], "content": changed + "x", "etag": page["etag"]})
    assert again["status"] == "conflict", again


def test_a_log_entry_is_appended(server):
    before = (server["root"] / "wiki" / "log.md").read_text()
    mcp(server, "wiki_log_append_tool", {"action": "lint", "message": "Smoke test entry", "component": "acme-api"})
    after = (server["root"] / "wiki" / "log.md").read_text()
    assert after.startswith(before) and "Smoke test entry" in after[len(before):]


def test_ingest_writes_a_raw_document(server):
    status, _, body = request(server, "/ingest", method="POST",
                              body={"component": "acme-api", "content": "# Smoke\n", "doc_type": "other"})
    payload = json.loads(body)
    assert status == 200 and payload["path"].startswith("raw/acme-api/")
    assert (server["root"] / payload["path"]).read_text() == "# Smoke\n"


def test_ingest_refuses_a_traversal_slug(server):
    status, _, _ = request(server, "/ingest", method="POST", body={"component": "../x", "content": "no"})
    assert status == 400


# ── the wiki browser ─────────────────────────────────────────────────────────

def test_the_wiki_browser_page_and_its_files_are_served(server):
    status, headers, body = request(server, "/docs/", auth="basic")
    assert status == 200 and b"Acme Engineering Wiki" in body and "text/html" in headers["content-type"]
    assert request(server, "/docs/_manifold/vendor/docsify.min.js", auth="basic")[0] == 200
    assert request(server, "/docs/_sidebar.md", auth="basic")[0] == 200
    assert request(server, "/docs/raw/shared/2026-01-27-order-status-contract.md", auth="basic")[0] == 200


def test_the_sse_endpoint_opens_for_an_authenticated_client(server):
    status, headers, _ = request(server, "/sse", read=False)
    assert status == 200 and "text/event-stream" in headers["content-type"]
