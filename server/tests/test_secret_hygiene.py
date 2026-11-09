# SPDX-License-Identifier: Apache-2.0
"""A credential never leaves the places meant for it (PHASE_1_TEST_PLAN A3, A7; INT-1 S3, S4).

Presented secrets are made-up strings or credentials generated into a temporary store; nothing here is real.
"""

import base64
import logging
import urllib.error
import urllib.request

import pytest

pytest.importorskip("fastmcp")

from manifold_security import tokens  # noqa: E402

from tests.realserver import EXAMPLE, running_server  # noqa: E402

pytestmark = pytest.mark.skipif(not EXAMPLE.is_dir(), reason="no examples/acme beside the server")

WRONG = "mf_000000000001_" + "WrongSecretWrongSecretWrongSecretWrongSec"[:43].ljust(43, "w")
MALFORMED = "malformed-credential-qzxjvk"
THROTTLED = "mf_000000000002_" + "ThrottledSecretThrottledSecretThrottled"[:43].ljust(43, "t")


def _bearer(secret):
    return "Bearer " + secret


def _basic(secret):
    return "Basic " + base64.b64encode(("anyone:" + secret).encode()).decode()


def _needles(secret):
    """Every form a leaked credential could take: the secret, its Basic encoding, both header values."""
    encoded = base64.b64encode(("anyone:" + secret).encode()).decode()
    return [secret, encoded, _bearer(secret), _basic(secret)]


def _fetch(base, path, authorization):
    """GET a path; return (status, response header text, body text) whatever the status."""
    request = urllib.request.Request(base + path, headers={"Authorization": authorization})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, str(response.headers), response.read().decode(errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, str(exc.headers), exc.read().decode(errors="replace")


def _attempt_order(revoked_secret):
    """Revoked first, so it is judged before the sign-in throttle starts to answer; throttled last."""
    return [revoked_secret, WRONG, MALFORMED] + [THROTTLED] * 8


def _revoke(data_dir, wiki_root, token):
    from manifold_security.store import open_store
    conn = open_store(data_dir, wiki_root=wiki_root)
    try:
        assert tokens.revoke_credential(conn, token.split("_")[1])
    finally:
        conn.close()


def test_A3_a_presented_credential_never_appears_in_the_app_logs_or_responses(
        auth_world, wiki_root, monkeypatch, caplog):
    from starlette.testclient import TestClient
    import server

    monkeypatch.setattr(server, "WIKI_ROOT", wiki_root)
    revoked = tokens.issue_credential(auth_world.conn, auth_world.human.id, "to-revoke").token
    tokens.revoke_credential(auth_world.conn, revoked.split("_")[1])
    client = TestClient(server.asgi_app, base_url="http://127.0.0.1:8686")
    caplog.set_level(logging.DEBUG)
    caplog.set_level(logging.DEBUG, logger="manifold")

    seen, statuses = [], []
    for secret in _attempt_order(revoked):
        for header in (_bearer, _basic):
            response = client.get("/docs/", headers={"Authorization": header(secret)})
            statuses.append(response.status_code)
            seen.append(response.text + str(dict(response.headers)))
    assert 429 in statuses and set(statuses) <= {401, 429}, statuses  # the throttled case really ran

    everything = caplog.text + "\n".join(seen)
    for secret in [revoked, WRONG, MALFORMED, THROTTLED]:
        for needle in _needles(secret):
            assert needle not in everything, "leaked: %s..." % needle[:12]


def test_A7_the_credential_never_reaches_git_history_or_the_wiki(tmp_path):
    import asyncio
    import json
    import subprocess
    from fastmcp import Client
    from fastmcp.client.transports import StreamableHttpTransport

    spec = [("alice", "human", ["contributor"], ["acme-api", "acme-web", "_shared"]),
            ("reg", "human", ["registrar", "contributor"])]
    with running_server(tmp_path, spec) as running:
        secrets = [running["tokens"]["alice"], running["tokens"]["reg"]]

        async def calls():
            async def tool(tool_name, who, **arguments):
                transport = StreamableHttpTransport(
                    running["base"] + "/mcp", headers={"Authorization": "Bearer " + running["tokens"][who]})
                async with Client(transport) as client:
                    return (await client.call_tool(tool_name, arguments, raise_on_error=False)).data

            return [
                await tool("wiki_write_page_tool", "alice", path="wiki/decisions/a7.md", content="# A7\n",
                           message="a page"),
                await tool("wiki_log_append_tool", "alice", action="lint", message="checked", component="acme-api"),
                await tool("wiki_handoff_tool", "alice", action="create", source="acme-api", target="acme-web",
                           type="feature", priority="low", title="A7 handoff", summary="s",
                           what_needs_to_happen="w"),
                await tool("wiki_register_component_tool", "reg", name="a7-fresh", description="d",
                           repo="https://example.test/a7", owner="o", skip_source_docs=True),
            ]

        results = asyncio.run(calls())
        assert [r.get("status", r.get("path")) for r in results], results
        assert not any(r.get("error") or r.get("refused") for r in results), results
        body = json.dumps({"component": "acme-api", "content": "# ingested\n"}).encode()
        request = urllib.request.Request(running["base"] + "/ingest", data=body, method="POST", headers={
            "Authorization": "Bearer " + running["tokens"]["alice"], "Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=10) as response:
            assert response.status == 200

    root = running["root"]
    history = subprocess.run(["git", "log", "--all", "-p", "--format=fuller"], cwd=root,
                             capture_output=True, text=True, check=True).stdout
    authors = subprocess.run(["git", "log", "--all", "--format=%an"], cwd=root,
                             capture_output=True, text=True, check=True).stdout.split()
    files = []
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            files.append(path.read_bytes().decode(errors="replace"))
    everything = history + "\n".join(files)
    for secret in secrets:
        for needle in (secret, secret.split("_", 2)[2]):
            assert needle not in everything, "leaked: %s..." % needle[:12]
    assert {"alice", "reg"} <= set(authors), authors  # commits name the principals
    assert "Manifold-Principal:" in history


def test_A3_a_presented_credential_never_appears_in_the_server_process_log(tmp_path):
    spec = [("alice", "human", ["contributor"])]
    with running_server(tmp_path, spec) as running:
        revoked = running["tokens"]["alice"]
        _revoke(running["data_dir"], running["root"], revoked)
        seen = []
        for secret in _attempt_order(revoked):
            for header in (_bearer, _basic):
                status, headers, body = _fetch(running["base"], "/docs/", header(secret))
                assert status in (401, 429), status
                seen.append(headers + body)
    log = (tmp_path / "server.log").read_text(errors="replace")
    assert log.strip(), "the server wrote no log, so there is nothing to search"

    everything = log + "\n".join(seen)
    for secret in [revoked, WRONG, MALFORMED, THROTTLED]:
        for needle in _needles(secret):
            assert needle not in everything, "leaked: %s..." % needle[:12]
