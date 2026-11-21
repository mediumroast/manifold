# SPDX-License-Identifier: Apache-2.0
"""Fixtures for the contract tests."""

import pytest

pytest.importorskip("fastmcp")

from tests.contracts import harness  # noqa: E402


@pytest.fixture()
def contract_world(tmp_path, monkeypatch):
    """A ToolWorld over a private copy of the fictional instance `examples/acme` (see harness.open_world)."""
    import server
    monkeypatch.setattr(server, "WIKI_ROOT", server.WIKI_ROOT)  # restored when the test ends
    world, _root = harness.open_world(tmp_path, monkeypatch.setenv)
    yield world
    world.conn.close()
