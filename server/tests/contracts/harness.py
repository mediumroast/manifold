# SPDX-License-Identifier: Apache-2.0
"""The contract harness (PHASE_4_PLAN Task 16, INT-2 S1).

A recording is one JSON file per tool and case, `<tool>.<case>.json`::

    {"tool": ..., "arguments": {...}, "caller": {"kind": ..., "roles": [...]},
     "files": {"relative/path": "text", ...},                # optional: fictional files placed (and committed) first
     "setup": [{"tool": ..., "arguments": {...}}, ...],     # optional: calls run first, same caller
     "result": {...}}                                        # the normalised tool result

Every case runs against a private copy of the fictional instance `examples/acme`, in a temporary
folder, with a temporary security store.  Nothing real is touched and nothing goes out on the
network.  The caller holds a grant on every Acme component and on `_shared`, so a case differs
only by kind and roles.

Recordings are written only by `record.py`, run by hand.  Tests only compare.
"""

import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

SERVER_DIR = Path(__file__).resolve().parents[2]
EXAMPLE = SERVER_DIR.parent / "examples" / "acme"
CONTRACT_DIR = Path(__file__).resolve().parent
GRANTS = ("acme-api", "acme-web", "acme-cli", "_shared")

if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

_VOLATILE = (
    (re.compile(r"\b[0-9a-f]{40}\b"), "<sha>"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?"), "<timestamp>"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "<date>"),
    (re.compile(r"\bp_[0-9a-f]{12}\b"), "<principal-id>"),  # generated when the principal is created
    (re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/releases"), "<releases-url>"),  # the product's own release page
)


def normalise(value, root=None):
    """The value with volatile text (commit hashes, timestamps, dates, the temporary folder) replaced by tokens."""
    if isinstance(value, dict):
        return {k: normalise(v, root) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalise(v, root) for v in value]
    if isinstance(value, str):
        if root:
            value = value.replace(str(root), "<root>")
        for pattern, token in _VOLATILE:
            value = pattern.sub(token, value)
        return value
    return value


def mask_product_versions(result):
    """The result with the product version fields replaced by `<version>` (they change at every release).

    Only `bundles[].version` is masked (the result of `wiki_bundle_info_tool`).  A version-looking
    number anywhere else in a result, such as one in a message, is still compared.
    """
    if isinstance(result, dict) and isinstance(result.get("bundles"), list):
        result = dict(result)
        result["bundles"] = [
            {**b, "version": "<version>"} if isinstance(b, dict) and "version" in b else b for b in result["bundles"]
        ]
    return result


def _kind(value):
    if value is None:
        return "null"
    return {dict: "object", list: "array", str: "str", bool: "bool", int: "int", float: "float"}.get(
        type(value), type(value).__name__)


def _walk(tool, path, expected, actual):
    if _kind(expected) != _kind(actual):
        raise AssertionError("%s: %s: expected %s, got %s" % (tool, path, _kind(expected), _kind(actual)))
    if isinstance(expected, dict):
        for key in expected:
            if key not in actual:
                raise AssertionError("%s: %s.%s: expected %s, got missing" % (tool, path, key, _kind(expected[key])))
        for key in actual:
            if key not in expected:
                raise AssertionError("%s: %s.%s: expected missing, got %s" % (tool, path, key, _kind(actual[key])))
        for key in expected:
            _walk(tool, "%s.%s" % (path, key), expected[key], actual[key])
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise AssertionError("%s: %s: expected %d items, got %d" % (tool, path, len(expected), len(actual)))
        for index, (e, a) in enumerate(zip(expected, actual)):
            _walk(tool, "%s[%d]" % (path, index), e, a)
    elif expected != actual:
        raise AssertionError("%s: %s: expected %r, got %r" % (tool, path, expected, actual))


def compare(tool, recorded, actual):
    """Raise AssertionError naming the tool and the dotted field path of the first difference.

    Both sides must already be normalised.  A field present on one side only, a different type
    and a different value are all differences.
    """
    _walk(tool, "result", recorded, actual)


def recording_files():
    return sorted(CONTRACT_DIR.glob("*.json"))


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def make_acme_copy(parent):
    """A private git-backed copy of the example instance under `parent`."""
    root = Path(parent) / "acme-wiki"
    shutil.copytree(EXAMPLE, root)
    for args in (["init", "-q"], ["config", "user.name", "t"], ["config", "user.email", "t@t.test"],
                 ["add", "-A"], ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
    return root


def open_world(parent, setenv):
    """A ToolWorld over a private copy of the example.

    `setenv(name, value)` sets an environment variable (the pytest monkeypatch in tests, a plain
    `os.environ` setter in the recorder).  Returns (world, root); the caller closes `world.conn`.
    """
    from manifold_security.store import open_store
    from tests.conftest import ToolWorld
    import server

    root = make_acme_copy(parent)
    data_dir = Path(parent) / "store"
    conn = open_store(data_dir, wiki_root=root)
    setenv("MANIFOLD_DATA_DIR", str(data_dir))
    setenv("CONTAINER_WIKI_ROOT", str(root))
    server.WIKI_ROOT = root
    return ToolWorld(conn, data_dir, root, server), root


def _resolve(world, arguments):
    """An argument value `@etag:<path>` becomes the current etag of that page (an etag changes with the content)."""
    resolved = {}
    for key, value in arguments.items():
        if isinstance(value, str) and value.startswith("@etag:"):
            value = world.call("contract", "wiki_read_tool", path=value[len("@etag:"):])["etag"]
        resolved[key] = value
    return resolved


def _place_files(root, files):
    """Write the fictional files of a case (`files`: {relative path: text}) into the private copy and commit them."""
    if not files:
        return
    for rel, text in files.items():
        target = Path(root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "contract case files"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


FROZEN_DAY =datetime.date(2026, 11, 14)  # the day the recordings were made


class _FrozenDate(datetime.date):
    @classmethod
    def today(cls):
        return FROZEN_DAY


def run_case(world, case):
    """Run a case (setup calls, then the call itself) and return the normalised result.

    The date the registrar writes into a new component page is fixed, so the page, and therefore its
    etag (a hash of the page), do not change from day to day.  Only the harness does this; the server
    code is untouched.
    """
    caller = case["caller"]
    world.who("contract", caller["kind"], roles=caller["roles"], grants=GRANTS)
    _place_files(world.root, case.get("files", {}))
    with mock.patch("wiki_backend.register.date", _FrozenDate):
        for step in case.get("setup", []):
            world.call("contract", step["tool"], **_resolve(world, step["arguments"]))
        result = world.call("contract", case["tool"], **_resolve(world, case["arguments"]))
    return mask_product_versions(normalise(result, world.root))
