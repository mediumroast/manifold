# SPDX-License-Identifier: Apache-2.0
"""Wiki read operations."""

from pathlib import Path
from typing import Optional, List
import frontmatter
import hashlib
import re
from .models import WikiPageResponse


def extract_links(content: str) -> List[str]:
    """Extract markdown links from content."""
    # Match [text](path) patterns
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(link_pattern, content)
    return [path for _, path in matches]


def generate_etag(content: str) -> str:
    """Generate an etag from content."""
    return hashlib.sha256(content.encode()).hexdigest()


def wiki_read(wiki_root: Path, path: str) -> WikiPageResponse:
    """
    Read a wiki page and return body, frontmatter, links, and etag.
    
    Args:
        wiki_root: Path to wiki repository root
        path: Path to wiki page relative to wiki_root
        
    Returns:
        WikiPageResponse with page content and metadata
    """
    file_path = wiki_root / path
    
    if not file_path.exists():
        raise FileNotFoundError(f"Page not found: {path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    # Read and parse the file
    with open(file_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    body = post.content
    frontmatter_dict = post.metadata
    
    # Generate full content for etag
    full_content = file_path.read_text(encoding='utf-8')
    etag = generate_etag(full_content)
    
    # Extract links from body
    links = extract_links(body)
    
    return WikiPageResponse(
        path=path,
        body=body,
        frontmatter=frontmatter_dict,
        etag=etag,
        links=links
    )
