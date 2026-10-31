# SPDX-License-Identifier: Apache-2.0
"""The MCP tool surface: what the server registers is what ping reports, and the retired tools are gone."""

import asyncio
import os

import pytest

pytest.importorskip("fastmcp")

import server  # noqa: E402  (needs fastmcp)
from wiki_backend.ping import _TOOL_NAMES  # noqa: E402

RETIRED = {
    "wiki_agent_list_tool", "wiki_agent_read_tool", "wiki_agent_scaffold_tool", "wiki_agent_export_tool",
    "wiki_agent_guide_tool", "wiki_work_plan_template_tool", "wiki_export_plan_templates_tool",
}


def _registered():
    async def names():
        return {t.name for t in await server.app.list_tools()}
    return asyncio.run(names())


def test_ping_reports_exactly_the_registered_tools():
    assert set(_TOOL_NAMES) == _registered()
    assert len(_TOOL_NAMES) == len(set(_TOOL_NAMES))


def test_retired_tools_are_not_registered():
    assert not RETIRED & _registered()


def test_new_tools_are_registered():
    assert {"wiki_bundle_info_tool", "wiki_agent_catalog_tool"} <= _registered()


def test_reconcile_tool_takes_only_the_component_and_repo():
    async def params():
        tool = next(t for t in await server.app.list_tools() if t.name == "wiki_reconcile_plan_tool")
        return set(tool.parameters["properties"])
    assert asyncio.run(params()) == {"component", "repo"}
