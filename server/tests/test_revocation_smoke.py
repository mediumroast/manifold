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


def test_a_role_removed_on_the_host_takes_effect_on_the_next_request(world):
    server, host = world
    token, _ = host.issue("alice", "laptop")
    assert ingest(server, token) == 200
    host.admin("role", "unset", "alice", "contributor")
    assert ingest(server, token) == 403
    assert get(server, "/docs/_sidebar.md", token) == 403  # no role left: not even read
