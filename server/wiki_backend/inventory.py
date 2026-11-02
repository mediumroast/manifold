# SPDX-License-Identifier: Apache-2.0
"""Wiki inventory and graph operations."""

from pathlib import Path
from typing import List, Dict, Any, Iterable, Optional
import frontmatter
from .models import WikiInventoryResponse, InventoryComponent, InventoryHandoff


def wiki_inventory(wiki_root: Path, archived: Optional[Iterable[str]] = None) -> WikiInventoryResponse:
    """
    Build a complete inventory of the wiki graph.

    Includes pages, frontmatter, components, handoffs, and backlinks.

    Args:
        wiki_root: Path to wiki repository root
        archived: slugs of archived components (from the security store); each is marked
                  ``status="archived"``, the others ``"active"``

    Returns:
        WikiInventoryResponse with complete wiki graph
    """
    archived_slugs = set(archived or ())
    components = []
    handoffs = []
    all_files = []
    
    wiki_path = wiki_root / "wiki"
    if not wiki_path.exists():
        return WikiInventoryResponse(
            components=[],
            handoffs=[],
            all_files=[]
        )
    
    # Walk through wiki directory
    for md_file in wiki_path.rglob("*.md"):
        relative_path = md_file.relative_to(wiki_root)
        all_files.append(str(relative_path))
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            frontmatter_dict = post.metadata
            
            # Check if this is a component page
            if relative_path.parent.name == "components" and md_file.stem not in ["_index"]:
                if "status" in frontmatter_dict and "component" not in md_file.stem:
                    # This looks like a component page
                    component = InventoryComponent(
                        name=frontmatter_dict.get("name", md_file.stem),
                        path=str(relative_path),
                        description=frontmatter_dict.get("summary", frontmatter_dict.get("description", "")),
                        owner=frontmatter_dict.get("owner"),
                        repo=frontmatter_dict.get("repo"),
                        status="archived" if md_file.stem in archived_slugs else "active",
                    )
                    components.append(component)
            
            # Check if this is a handoff page.
            # Layout: wiki/handoffs/{source}-to-{target}/{type}-{id}.md
            # The from-to pair is in the parent directory name, not the file stem.
            if (
                relative_path.parent.parent.name == "handoffs"
                and md_file.stem != "_index"
            ):
                dir_name = relative_path.parent.name  # e.g. "acme-api-to-acme-web"
                parts = dir_name.split("-to-", 1)
                if len(parts) == 2:
                    handoff = InventoryHandoff(
                        from_component=parts[0],
                        to_component=parts[1],
                        path=str(relative_path),
                        status=frontmatter_dict.get("status", "pending")
                    )
                    handoffs.append(handoff)
        
        except Exception as e:
            # Skip files that can't be parsed
            continue
    
    return WikiInventoryResponse(
        components=components,
        handoffs=handoffs,
        all_files=all_files
    )
