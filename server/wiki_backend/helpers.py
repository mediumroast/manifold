# SPDX-License-Identifier: Apache-2.0
"""Exportable helper scripts for installation into component repos.

The MCP server returns script content and the target output_path.  The agent writes the file into the component repo.
"""

from pathlib import Path

from . import assets
from .config import ConfigError, DEFAULT_SERVER_NAME, load_config

# Registry of exportable helper scripts.
# source: asset path (see assets.py): the instance's assets/ directory first, then the core assets/.
# output_path: where the file should land in the component repo.
_HELPERS: dict[str, dict] = {
    "ingest_doc": {
        "source": "helpers/tools/ingest_doc.py",
        "output_path": "tools/ingest_doc.py",
        "description": (
            "Push local doc files into the manifold wiki via POST /ingest. "
            "Install this in a component repo so doc updates can be run "
            "without referencing the manifold repo path."
        ),
        "usage": "python3 tools/ingest_doc.py <component> <file_path> [doc_type]",
    },
    "handoff-create-prompt": {
        "source": "helpers/prompts/handoff-create.prompt.md",
        "output_path": ".github/prompts/handoff-create.prompt.md",
        "description": "Copilot slash command: /handoff-create — post a new handoff",
        "usage": "Install in component repo. Use as /handoff-create in Copilot Chat.",
    },
    "handoff-pickup-prompt": {
        "source": "helpers/prompts/handoff-pickup.prompt.md",
        "output_path": ".github/prompts/handoff-pickup.prompt.md",
        "description": "Copilot slash command: /handoff-pickup — find and claim open handoffs",
        "usage": "Install in component repo. Use as /handoff-pickup in Copilot Chat.",
    },
    "handoff-close-prompt": {
        "source": "helpers/prompts/handoff-close.prompt.md",
        "output_path": ".github/prompts/handoff-close.prompt.md",
        "description": "Copilot slash command: /handoff-close — close a handoff this component raised (source only)",
        "usage": "Install in component repo. Use as /handoff-close in Copilot Chat.",
    },
    "handoff-create-command": {
        "source": "helpers/commands/handoff-create.md",
        "output_path": ".claude/commands/handoff-create.md",
        "description": "Claude Code slash command: /handoff-create — post a new handoff",
        "usage": "Install in component repo. Use as /handoff-create in Claude Code.",
    },
    "handoff-pickup-command": {
        "source": "helpers/commands/handoff-pickup.md",
        "output_path": ".claude/commands/handoff-pickup.md",
        "description": "Claude Code slash command: /handoff-pickup — find and claim open handoffs",
        "usage": "Install in component repo. Use as /handoff-pickup in Claude Code.",
    },
    "handoff-close-command": {
        "source": "helpers/commands/handoff-close.md",
        "output_path": ".claude/commands/handoff-close.md",
        "description": "Claude Code slash command: /handoff-close — close a handoff this component raised (source only)",
        "usage": "Install in component repo. Use as /handoff-close in Claude Code.",
    },
    "manifold-update-prompt": {
        "source": "helpers/prompts/manifold-update.prompt.md",
        "output_path": ".github/prompts/manifold-update.prompt.md",
        "description": "Copilot slash command: /manifold-update — check and install manifold helper updates",
        "usage": "Install in component repo. Use as /manifold-update in Copilot Chat.",
    },
    "manifold-update-command": {
        "source": "helpers/commands/manifold-update.md",
        "output_path": ".claude/commands/manifold-update.md",
        "description": "Claude Code slash command: /manifold-update — check and install manifold helper updates",
        "usage": "Install in component repo. Use as /manifold-update in Claude Code.",
    },
    "handoff-update-prompt": {
        "source": "helpers/prompts/handoff-update.prompt.md",
        "output_path": ".github/prompts/handoff-update.prompt.md",
        "description": "Copilot slash command: /handoff-update — submit implementation for source review",
        "usage": "Install in component repo. Use as /handoff-update in Copilot Chat.",
    },
    "handoff-confirm-prompt": {
        "source": "helpers/prompts/handoff-confirm.prompt.md",
        "output_path": ".github/prompts/handoff-confirm.prompt.md",
        "description": "Copilot slash command: /handoff-confirm — confirm target's implementation",
        "usage": "Install in component repo. Use as /handoff-confirm in Copilot Chat.",
    },
    "handoff-reject-prompt": {
        "source": "helpers/prompts/handoff-reject.prompt.md",
        "output_path": ".github/prompts/handoff-reject.prompt.md",
        "description": "Copilot slash command: /handoff-reject — reject implementation and request rework",
        "usage": "Install in component repo. Use as /handoff-reject in Copilot Chat.",
    },
    "handoff-update-command": {
        "source": "helpers/commands/handoff-update.md",
        "output_path": ".claude/commands/handoff-update.md",
        "description": "Claude Code slash command: /handoff-update — submit implementation for source review",
        "usage": "Install in component repo. Use as /handoff-update in Claude Code.",
    },
    "handoff-confirm-command": {
        "source": "helpers/commands/handoff-confirm.md",
        "output_path": ".claude/commands/handoff-confirm.md",
        "description": "Claude Code slash command: /handoff-confirm — confirm target's implementation",
        "usage": "Install in component repo. Use as /handoff-confirm in Claude Code.",
    },
    "handoff-reject-command": {
        "source": "helpers/commands/handoff-reject.md",
        "output_path": ".claude/commands/handoff-reject.md",
        "description": "Claude Code slash command: /handoff-reject — reject implementation and request rework",
        "usage": "Install in component repo. Use as /handoff-reject in Claude Code.",
    },
}

_DEFAULT_SERVER_URL = "http://127.0.0.1:8686"

_SERVER_PLACEHOLDER = "{{MCP_SERVER}}"


def _render(content: str, wiki_root: Path) -> str:
    """Fill {{MCP_SERVER}} with this instance's server name (manifold.yaml, else the default)."""
    if _SERVER_PLACEHOLDER not in content:
        return content
    try:
        server_name = load_config(wiki_root).server_name
    except ConfigError:
        server_name = DEFAULT_SERVER_NAME
    return content.replace(_SERVER_PLACEHOLDER, server_name)


def wiki_list_helpers(wiki_root: Path) -> dict:
    """Return the registry of all exportable helper scripts."""
    return {
        "helpers": [
            {
                "name": name,
                "output_path": meta["output_path"],
                "description": meta["description"],
                "usage": meta["usage"],
            }
            for name, meta in _HELPERS.items()
        ]
    }


def wiki_export_all_helpers(wiki_root: Path) -> dict:
    """
    Return the content and output_path for every registered helper file.
    Used by the /manifold-update command and onboarding step 9.
    """
    files = []
    errors = []
    for name, meta in _HELPERS.items():
        found = assets.find(wiki_root, meta["source"])
        if found:
            files.append({
                "name": name,
                "output_path": meta["output_path"],
                "content": _render(found["path"].read_text(encoding="utf-8"), wiki_root),
                "description": meta["description"],
                "origin": found["origin"],
            })
        else:
            errors.append(f"{name}: source not found at assets/{meta['source']}")
    return {
        "files": files,
        "count": len(files),
        "errors": errors,
        "next": (
            "Write each file's content to its output_path in the component repo, "
            "then commit. These files become slash commands in Copilot Chat and Claude Code."
        ),
    }


def wiki_export_helper(wiki_root: Path, name: str, server_url: str = "") -> dict:
    """
    Return the content of a helper script ready to write into a component repo.

    Args:
        wiki_root:   Instance repository root (mounted volume).
        name:        Helper name, e.g. "ingest_doc".
        server_url:  Override the default server URL embedded in the script.
                     If empty, the default (http://127.0.0.1:8686) is kept.

    Returns:
        {"name", "output_path", "content", "notes"} on success.
        {"error": "..."} on failure.
    """
    if name not in _HELPERS:
        known = sorted(_HELPERS.keys())
        return {"error": f"Unknown helper '{name}'. Known helpers: {known}"}

    meta = _HELPERS[name]
    found = assets.find(wiki_root, meta["source"])

    if not found:
        return {
            "error": (
                f"Helper source not found: assets/{meta['source']}. "
                "It is looked up in the instance's assets/ directory and then in the "
                f"server's own assets ({assets.core_assets_dir()}). "
                "A missing core file means the server installation is incomplete."
            )
        }

    content = _render(found["path"].read_text(encoding="utf-8"), wiki_root)

    # Patch in a custom server URL if provided
    effective_url = server_url.strip().rstrip("/") if server_url.strip() else ""
    if effective_url and effective_url != _DEFAULT_SERVER_URL:
        content = content.replace(
            f'default="{_DEFAULT_SERVER_URL}"',
            f'default="{effective_url}"',
        )

    notes = (
        f"Write to {meta['output_path']} in the component repo. "
        f"Usage: {meta['usage']}"
    )

    return {
        "name": name,
        "output_path": meta["output_path"],
        "content": content,
        "notes": notes,
        "origin": found["origin"],
    }
