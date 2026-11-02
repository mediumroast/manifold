# SPDX-License-Identifier: Apache-2.0
"""Tests for wiki_ping_tool."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from wiki_backend.ping import wiki_ping
from wiki_backend.onboarding import wiki_onboarding_protocol


def test_ping_returns_connected_status():
    result = wiki_ping()
    assert result["status"] == "connected"


def test_ping_reports_the_calling_principal_when_given_one():
    who = {"id": "p1", "name": "alice", "kind": "human", "roles": ["reader"]}
    assert wiki_ping(principal=who)["principal"] == who
    assert wiki_ping()["principal"] is None


def test_ping_returns_the_default_server_name_without_an_instance():
    assert wiki_ping()["server"] == "manifold"


def test_ping_returns_the_server_name_from_manifold_yaml(tmp_path):
    (tmp_path / "manifold.yaml").write_text("version: 1\nserver_name: acme-wiki\n")
    assert wiki_ping(tmp_path)["server"] == "acme-wiki"


def test_ping_falls_back_to_the_default_when_manifold_yaml_is_missing(tmp_path):
    assert wiki_ping(tmp_path)["server"] == "manifold"


def test_ping_returns_tool_list():
    result = wiki_ping()
    assert isinstance(result["tools"], list)
    assert len(result["tools"]) > 0


def test_ping_tool_count_matches_list():
    result = wiki_ping()
    assert result["tool_count"] == len(result["tools"])


def test_ping_lists_itself():
    result = wiki_ping()
    assert "wiki_ping_tool" in result["tools"]


def test_ping_lists_core_tools():
    result = wiki_ping()
    for name in ("wiki_inventory_tool", "wiki_read_tool", "wiki_write_page_tool"):
        assert name in result["tools"], f"Expected {name} in ping tool list"


def test_ping_returns_next_step():
    result = wiki_ping()
    assert "next_step" in result
    assert len(result["next_step"]) > 0


def test_onboarding_protocol_includes_ping():
    protocol = wiki_onboarding_protocol()
    tool_names = {t["name"] for t in protocol["tools"]}
    assert "wiki_ping_tool" in tool_names
