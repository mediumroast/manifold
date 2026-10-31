# SPDX-License-Identifier: Apache-2.0
"""Connection ping — MCP-native server discovery."""

from pathlib import Path
from typing import Optional

from .config import ConfigError, DEFAULT_SERVER_NAME, load_config

_TOOL_NAMES = [
    "wiki_ping_tool",
    "wiki_handoff_tool",
    "wiki_read_tool",
    "wiki_write_page_tool",
    "wiki_log_append_tool",
    "wiki_inventory_tool",
    "wiki_register_component_tool",
    "wiki_freshness_tool",
    "wiki_onboarding_tool",
    "wiki_reconcile_plan_tool",
    "wiki_agent_catalog_tool",
    "wiki_bundle_info_tool",
    "wiki_list_helpers_tool",
    "wiki_export_helper_tool",
    "wiki_export_component_helpers_tool",
]


def _server_name(wiki_root: Optional[Path]) -> str:
    if wiki_root is None:
        return DEFAULT_SERVER_NAME
    try:
        return load_config(wiki_root).server_name
    except ConfigError:
        return DEFAULT_SERVER_NAME


def wiki_ping(wiki_root: Optional[Path] = None) -> dict:
    """
    Return server status and the canonical list of available MCP tool names.
    Called by wiki_ping_tool in server.py.  The server name comes from
    manifold.yaml when ``wiki_root`` has one, else the default.
    """
    return {
        "status": "connected",
        "server": _server_name(wiki_root),
        "tool_count": len(_TOOL_NAMES),
        "tools": list(_TOOL_NAMES),
        "next_step": (
            "Native MCP connection confirmed. "
            "Call wiki_onboarding_tool() for the full protocol, or "
            "wiki_inventory_tool() to see components and open handoffs."
        ),
    }
