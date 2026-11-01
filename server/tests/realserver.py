# SPDX-License-Identifier: Apache-2.0
"""Start the real server process against a private copy of examples/acme and a private security store.

Used by the smoke test and the principal-propagation test.  The store lives beside the
instance (never inside it) and holds the principals the caller asks for, each with a
generated credential.
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
EXAMPLE = SERVER_DIR.parent / "examples" / "acme"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.contextmanager
def running_server(base_dir: Path, principals_spec):
    """
    Yield ``{"base", "root", "tokens"}`` for a running server.

    ``principals_spec`` is a list of ``(name, kind, roles)`` or ``(name, kind, roles, grant scopes)``;
    ``tokens`` maps each name to the credential generated for it.
    """
    from manifold_security import principals, tokens
    from manifold_security.store import open_store

    root = base_dir / "acme-wiki"
    shutil.copytree(EXAMPLE, root)
    for args in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t.test"],
                 ["add", "-A"], ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

    data_dir = base_dir / "security-data"
    conn = open_store(data_dir, wiki_root=root)
    issued = {}
    for name, kind, roles, *rest in principals_spec:
        principal = principals.create_principal(conn, name, kind)
        for role in roles:
            principals.set_role(conn, name, role)
        for scope in (rest[0] if rest else []):
            principals.add_grant(conn, name, scope)
        issued[name] = tokens.issue_credential(conn, principal.id, "test").token
    conn.close()

    port = free_port()
    env = dict(os.environ, CONTAINER_WIKI_ROOT=str(root), PORT=str(port), MANIFOLD_DATA_DIR=str(data_dir),
               MANIFOLD_HOST="127.0.0.1", PYTHONUNBUFFERED="1")
    for name in ("MANIFOLD_RELOAD", "MANIFOLD_TOKEN", "MANIFOLD_TOKEN_FILE"):
        env.pop(name, None)
    log = base_dir / "server.log"
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
            yield {"base": base, "root": root, "tokens": issued, "data_dir": data_dir}
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
