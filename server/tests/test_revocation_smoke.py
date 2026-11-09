# SPDX-License-Identifier: Apache-2.0
"""Revocation is immediate and durable, across processes (PHASE_1_PLAN T27).

The real server runs on a temporary instance and data folder.  Everything about principals and
credentials is done with the host command in separate processes while the server keeps running:
the server must see each change on the very next request, without a restart, and must still
honor it after a restart.
"""

import json
import subprocess
import sys
import urllib.error
import urllib.request

import pytest

pytest.importorskip("fastmcp")

from tests.realserver import EXAMPLE, REPO_ROOT, ServerProcess  # noqa: E402

pytestmark = pytest.mark.skipif(not EXAMPLE.is_dir(), reason="no examples/acme beside the server")


class Host:
    """The host command, run as a separate process each time (`./manifold admin ...`)."""

    def __init__(self, server, tmp_path):
        self.server = server
        self.tmp_path = tmp_path
        self.count = 0

    def admin(self, *args):
        command = [sys.executable, str(REPO_ROOT / "manifold"), "admin", "--data-dir", str(self.server.data_dir),
                   "--wiki-root", str(self.server.root), *args]
        done = subprocess.run(command, capture_output=True, text=True)
        assert done.returncode == 0, done.stderr
        return done.stdout

    def issue(self, principal, label):
        self.count += 1
        path = self.tmp_path / ("secret-%d" % self.count)
        out = self.admin("credential", "issue", principal, "--label", label, "--secret-file", str(path))
        credential_id = out.split("Issued credential ")[1].split(" ")[0]
        return path.read_text().strip(), credential_id


def get(server, path, token):
    request = urllib.request.Request(server.base + path, headers={"Authorization": "Bearer " + token})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


def ingest(server, token, component="acme-api"):
    body = json.dumps({"component": component, "content": "# from the test\n"}).encode()
    request = urllib.request.Request(server.base + "/ingest", data=body, method="POST", headers={
        "Authorization": "Bearer " + token, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code


@pytest.fixture()
def world(tmp_path):
    server = ServerProcess(tmp_path / "instance")
    (tmp_path / "instance").mkdir(exist_ok=True)
    server.start()
    host = Host(server, tmp_path)
    host.admin("principal", "create", "alice")
    host.admin("role", "set", "alice", "contributor")
    host.admin("grant", "add", "alice", "acme-api")
    yield server, host
    server.stop()


def test_a_revoked_credential_is_refused_on_the_next_request_without_a_restart_and_after_one(world):
    server, host = world
    first, first_id = host.issue("alice", "laptop")
    second, _ = host.issue("alice", "ci")
    assert get(server, "/docs/_sidebar.md", first) == 200 and get(server, "/docs/_sidebar.md", second) == 200

    host.admin("credential", "revoke", first_id)
    # no restart: the very next request
    assert get(server, "/docs/_sidebar.md", first) == 401
    assert get(server, "/docs/_sidebar.md", second) == 200

    server.restart()
    assert get(server, "/docs/_sidebar.md", first) == 401  # durable
    assert get(server, "/docs/_sidebar.md", second) == 200


def test_a_deny_stops_writes_on_the_next_request_and_survives_a_restart(world):
    server, host = world
    token, _ = host.issue("alice", "laptop")
    assert ingest(server, token) == 200

    host.admin("deny", "add", "alice", "acme-api")
    assert ingest(server, token) == 403
    assert get(server, "/docs/_sidebar.md", token) == 200  # reads are not limited per component

    server.restart()
    assert ingest(server, token) == 403

    host.admin("deny", "remove", "alice", "acme-api")
    assert ingest(server, token) == 200  # and lifting it is just as immediate


def test_a_disabled_principal_is_refused_on_the_next_request_and_after_a_restart(world):
    server, host = world
    first, _ = host.issue("alice", "laptop")
    second, _ = host.issue("alice", "ci")
    assert get(server, "/docs/_sidebar.md", first) == 200

    host.admin("principal", "disable", "alice")
    assert get(server, "/docs/_sidebar.md", first) == 401 and get(server, "/docs/_sidebar.md", second) == 401

    server.restart()
    assert get(server, "/docs/_sidebar.md", first) == 401

    host.admin("principal", "enable", "alice")
    assert get(server, "/docs/_sidebar.md", first) == 200


class SseSession:
    """A raw /sse session: opens the stream, learns the message endpoint, collects the JSON-RPC replies."""

    def __init__(self, server, token):
        import queue
        import threading
        self.server = server
        self.token = token
        self.replies = queue.Queue()
        self.endpoint = queue.Queue()
        request = urllib.request.Request(server.base + "/sse", headers={"Authorization": "Bearer " + token})
        self.response = urllib.request.urlopen(request, timeout=30)
        threading.Thread(target=self._read, daemon=True).start()
        self.path = self.endpoint.get(timeout=10)

    def _read(self):
        event = None
        try:
            for raw in self.response:
                line = raw.decode().rstrip("\r\n")
                if line.startswith("event:"):
                    event = line.split(":", 1)[1].strip()
                elif line.startswith("data:"):
                    data = line.split(":", 1)[1].strip()
                    (self.endpoint if event == "endpoint" else self.replies).put(data)
        except (OSError, ValueError, AttributeError):  # the stream was closed under the reader
            pass

    def post(self, payload):
        """POST one JSON-RPC message; return the HTTP status."""
        request = urllib.request.Request(
            self.server.base + self.path, data=json.dumps(payload).encode(), method="POST",
            headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return response.status
        except urllib.error.HTTPError as exc:
            return exc.code

    def call(self, ident, tool, arguments):
        """tools/call; return (HTTP status, the reply's result or None)."""
        status = self.post({"jsonrpc": "2.0", "id": ident, "method": "tools/call",
                            "params": {"name": tool, "arguments": arguments}})
        if status != 202:
            return status, None
        import queue
        while True:
            try:
                reply = json.loads(self.replies.get(timeout=10))
            except queue.Empty:
                return status, None
            if reply.get("id") == ident:
                return status, reply

    def start(self):
        self.post({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "t", "version": "0"}}})
        self.replies.get(timeout=10)
        self.post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return self

    def close(self):
        self.response.close()


def _reply_text(reply):
    return json.dumps(reply)


def test_A12_an_open_sse_session_is_cut_off_by_revocation_and_deny(world):
    import subprocess
    server, host = world
    host.admin("principal", "create", "bob")
    host.admin("role", "set", "bob", "contributor")
    host.admin("grant", "add", "bob", "acme-web")
    a_token, a_id = host.issue("alice", "session-a")
    a2_token, _ = host.issue("alice", "session-a2")
    b_token, _ = host.issue("bob", "session-b")
    page = "wiki/components/acme-api.md"
    original = (server.root / page).read_text()

    def head():
        return subprocess.run(["git", "log", "-1", "--format=%H"], cwd=server.root, capture_output=True,
                              text=True, check=True).stdout

    session_a = SseSession(server, a_token).start()
    session_a2 = SseSession(server, a2_token).start()
    session_b = SseSession(server, b_token).start()
    try:
        ping = session_a.call(2, "wiki_ping_tool", {})
        assert ping[0] == 202 and "alice" in _reply_text(ping[1])

        # revocation: the next POST on the open session is 401 and the tool does not run
        host.admin("credential", "revoke", a_id)
        before = head()
        status, _ = session_a.call(3, "wiki_write_page_tool", {
            "path": page, "content": original + "\nrevoked write\n", "message": "x"})
        assert status == 401
        assert (server.root / page).read_text() == original and head() == before

        # deny: the session stays valid but the tool refuses and writes nothing
        host.admin("deny", "add", "alice", "acme-api")
        status, reply = session_a2.call(4, "wiki_write_page_tool", {
            "path": page, "content": original + "\ndenied write\n", "message": "x"})
        assert status == 202 and "refused" in _reply_text(reply).lower(), reply
        assert (server.root / page).read_text() == original and head() == before

        # the other credential is untouched
        other = session_b.call(5, "wiki_ping_tool", {})
        assert other[0] == 202 and "bob" in _reply_text(other[1])
    finally:
        for session in (session_a, session_a2, session_b):
            session.close()


def test_a_role_removed_on_the_host_takes_effect_on_the_next_request(world):
    server, host = world
    token, _ = host.issue("alice", "laptop")
    assert ingest(server, token) == 200
    host.admin("role", "unset", "alice", "contributor")
    assert ingest(server, token) == 403
    assert get(server, "/docs/_sidebar.md", token) == 403  # no role left: not even read
