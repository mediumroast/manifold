# SPDX-License-Identifier: Apache-2.0
"""Start the real server process against a private copy of examples/acme and a private security store.

Used by the smoke test, the principal-propagation test and the revocation test.  The store lives
beside the instance (never inside it).  ``running_server`` seeds principals directly in the store
before the server starts; ``ServerProcess`` leaves the store empty so a test can build it with the
host command in another process, and can stop and start the server again.
"""

import contextlib
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SERVER_DIR.parent
EXAMPLE = REPO_ROOT / "examples" / "acme"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ServerProcess:
    """A real server on a temporary copy of the example instance.  ``start``/``stop`` may be repeated."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.root = base_dir / "acme-wiki"
        self.data_dir = base_dir / "security-data"
        self.port = free_port()
        self.base = "http://127.0.0.1:%d" % self.port
        self.process = None
        shutil.copytree(EXAMPLE, self.root)
        for args in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t.test"],
                     ["add", "-A"], ["commit", "-q", "-m", "start"]):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def start(self):
        env = dict(os.environ, CONTAINER_WIKI_ROOT=str(self.root), PORT=str(self.port),
                   MANIFOLD_DATA_DIR=str(self.data_dir), MANIFOLD_HOST="127.0.0.1", PYTHONUNBUFFERED="1")
        for name in ("MANIFOLD_RELOAD", "MANIFOLD_TOKEN", "MANIFOLD_TOKEN_FILE"):
            env.pop(name, None)
        log = self.base_dir / "server.log"
        with open(log, "a") as out:
            self.process = subprocess.Popen([sys.executable, "server.py"], cwd=SERVER_DIR, env=env,
                                            stdout=out, stderr=out)
        deadline = time.time() + 30
        while time.time() < deadline:
            if self.process.poll() is not None:
                pytest.fail("the server exited early:\n" + log.read_text())
            try:
                urllib.request.urlopen(self.base + "/health", timeout=1).read()
                return self
            except (urllib.error.URLError, ConnectionError, OSError):
                time.sleep(0.2)
        pytest.fail("the server did not start:\n" + log.read_text())

    def stop(self):
        if self.process is None:
            return
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
        self.process = None

    def restart(self):
        self.stop()
        return self.start()


@contextlib.contextmanager
def running_server(base_dir: Path, principals_spec):
    """
    Yield ``{"base", "root", "tokens", "data_dir"}`` for a running server.

    ``principals_spec`` is a list of ``(name, kind, roles)`` or ``(name, kind, roles, grant scopes)``;
    ``tokens`` maps each name to the credential generated for it.
    """
    from manifold_security import principals, tokens
    from manifold_security.store import open_store

    server = ServerProcess(base_dir)
    conn = open_store(server.data_dir, wiki_root=server.root)
    issued = {}
    for name, kind, roles, *rest in principals_spec:
        principal = principals.create_principal(conn, name, kind)
        for role in roles:
            principals.set_role(conn, name, role)
        for scope in (rest[0] if rest else []):
            principals.add_grant(conn, name, scope)
        issued[name] = tokens.issue_credential(conn, principal.id, "test").token
    conn.close()
    server.start()
    try:
        yield {"base": server.base, "root": server.root, "tokens": issued, "data_dir": server.data_dir}
    finally:
        server.stop()
