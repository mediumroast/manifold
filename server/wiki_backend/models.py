# SPDX-License-Identifier: Apache-2.0
"""Data models for wiki MCP service using Pydantic."""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel
from datetime import datetime


class WikiPageResponse(BaseModel):
    """Response structure for wiki_read operations."""
    path: str
    body: str
    frontmatter: Dict[str, Any]
    etag: str
    links: List[str] = []


class WikiWriteRequest(BaseModel):
    """Request structure for wiki_write_page operations."""
    path: str
    content: str
    etag: Optional[str] = None  # None for create, value for update
    message: str


class WikiWriteResponse(BaseModel):
    """Response structure for wiki_write_page operations."""
    path: str
    status: str  # "created", "updated", "conflict"
    etag: Optional[str] = None
    error: Optional[str] = None


class WikiLogEntry(BaseModel):
    """Structure for a single log entry."""
    timestamp: datetime
    action: str
    component: Optional[str] = None
    message: str


class WikiLogRequest(BaseModel):
    """Request structure for wiki_log_append operations."""
    action: str
    message: str
    component: Optional[str] = None


class InventoryComponent(BaseModel):
    """Component entry in wiki inventory."""
    name: str
    path: str
    description: str
    owner: Optional[str] = None
    repo: Optional[str] = None
    status: str = "active"  # "archived" for a component a registrar has archived


class InventoryHandoff(BaseModel):
    """Handoff entry in wiki inventory."""
    from_component: str
    to_component: str
    path: str
    status: str  # "pending", "in-progress", "completed", "blocked"


class WikiInventoryResponse(BaseModel):
    """Response structure for wiki_inventory operations."""
    components: List[InventoryComponent]
    handoffs: List[InventoryHandoff]
    all_files: List[str]


class WikiRegisterRequest(BaseModel):
    """Request structure for wiki_register_component operations."""
    name: str                          # slug, e.g. "acme-api"
    description: str                   # one-sentence summary
    repo: str                          # full repo URL
    owner: str                         # team or person name
    source_docs: List[str] = []        # paths to raw docs (relative to wiki_root) to embed
    inline_docs: Dict[str, Any] = {}   # {"readme": "...", "architecture": "..."} — content passed directly
    skip_source_docs: bool = False     # register with stubs if True
    reconcile: bool = False            # if True and page exists, update from source docs instead of blocking


class WikiRegisterResponse(BaseModel):
    """Response structure for wiki_register_component operations.

    Valid status values: "created", "reconciled", "already_registered", "error"
    """
    name: str
    path: str
    status: str  # "created", "reconciled", "already_registered", "error"
    message: str
    etag: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Response structure for health check."""
    status: str  # "healthy", "unhealthy"
    wiki_root: str
    message: str


class FreshnessStaleEntry(BaseModel):
    """A component whose wiki page is older than one or more raw docs."""
    component: str
    wiki_page: str
    last_wiki_update: str
    newer_raw_docs: List[str]


class FreshnessUnknownEntry(BaseModel):
    """A component that could not be checked (missing page or frontmatter)."""
    component: str
    reason: str


class WikiFreshnessResponse(BaseModel):
    """Response structure for wiki_freshness_tool."""
    stale: List[FreshnessStaleEntry] = []
    fresh: List[str] = []
    unknown: List[FreshnessUnknownEntry] = []
