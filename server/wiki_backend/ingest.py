# SPDX-License-Identifier: Apache-2.0
"""Server-side document ingestion into raw/{component}/."""

import os
import re
from pathlib import Path
from datetime import date
from typing import Optional
from .git import git_commit
from .config import valid_slug

_VALID_DOC_TYPES = {"readme", "architecture", "api", "other"}

# The longest file-name stem kept from a caller-supplied filename.
_MAX_STEM = 80

# Upper bound on a document, in bytes.  /ingest writes to disk for any caller
# that can reach the port, so the bound is enforced before the body is parsed.
DEFAULT_MAX_BYTES = 1024 * 1024


def max_ingest_bytes() -> int:
    """Size limit in bytes: MANIFOLD_INGEST_MAX_BYTES, else 1 MiB."""
    try:
        value = int(os.environ.get("MANIFOLD_INGEST_MAX_BYTES", DEFAULT_MAX_BYTES))
    except ValueError:
        return DEFAULT_MAX_BYTES
    return value if value > 0 else DEFAULT_MAX_BYTES


class BodyTooLarge(Exception):
    """The request body is larger than the ingest limit."""


async def read_body_capped(chunks, declared_length: Optional[str], limit: int) -> bytes:
    """
    Collect an async iterator of byte chunks, refusing more than ``limit`` bytes.

    ``declared_length`` is the Content-Length header, if any: a body that
    declares more than ``limit`` is refused before any of it is read, and a
    body that lies about its length is stopped as soon as it passes the limit.
    """
    if declared_length is not None:
        try:
            if int(declared_length) > limit:
                raise BodyTooLarge()
        except ValueError:
            pass
    received = bytearray()
    async for chunk in chunks:
        received.extend(chunk)
        if len(received) > limit:
            raise BodyTooLarge()
    return bytes(received)

# Keyword rules mirror _classify_doc in register.py
_README_KW = ("readme", "overview", "intro")
_ARCH_KW = ("architecture", "arch", "design", "structure", "internals")
_API_KW = ("api", "contract", "spec", "endpoint", "schema", "openapi", "swagger")


def classify_doc_type(filename: str) -> str:
    """Infer doc type from filename using keyword rules."""
    stem = Path(filename).name.lower()
    if any(k in stem for k in _README_KW):
        return "readme"
    if any(k in stem for k in _ARCH_KW):
        return "architecture"
    if any(k in stem for k in _API_KW):
        return "api"
    return "other"


def wiki_ingest_doc(
    wiki_root: Path,
    component: str,
    doc_type: str,
    content: str,
    filename: Optional[str] = None,
) -> dict:
    """
    Write a document into raw/{component}/ inside the mounted wiki repo.

    Called by the POST /ingest route.  The host-side CLI script reads the
    source file and POSTs its content here — the model is never involved
    in the file transfer.

    Args:
        wiki_root:  Absolute path to the manifold repo root (mounted volume).
        component:  Component slug, e.g. "acme-api".
        doc_type:   One of: readme | architecture | api | other.
        content:    Full text of the document.
        filename:   Override the auto-generated filename.  Must end in .md.

    Returns:
        {"status": "ok", "path": "raw/..."} or {"status": "error", "message": ...}
    """
    # --- validate component slug ---
    slug = component.strip().lower()
    if not valid_slug(slug):
        return {
            "status": "error",
            "message": "component must be lowercase ASCII letters and digits with single dots, "
                       "hyphens or underscores between them, at most 64 characters",
        }

    # --- validate doc_type ---
    if doc_type not in _VALID_DOC_TYPES:
        return {
            "status": "error",
            "message": f"doc_type must be one of {sorted(_VALID_DOC_TYPES)}, got: {doc_type!r}",
        }

    # --- validate content ---
    if not content or not content.strip():
        return {"status": "error", "message": "content must not be empty"}
    if "\x00" in content:
        return {"status": "error", "message": "content must be text (it contains a NUL byte)"}
    limit = max_ingest_bytes()
    if len(content.encode("utf-8")) > limit:
        return {
            "status": "error",
            "reason": "too_large",
            "message": "content is larger than the limit of %d bytes" % limit,
        }

    # --- resolve output path ---
    raw_root = (wiki_root / "raw").resolve()
    raw_dir = (wiki_root / "raw" / slug).resolve()
    if raw_root.parent != wiki_root.resolve() or raw_dir.parent != raw_root:
        # raw/ or raw/<slug> is a symlink that leads somewhere else.
        return {"status": "error", "message": "component directory is outside raw/"}
    raw_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    if filename:
        # Derive a dated slug from the source filename's stem so that multiple
        # docs of the same doc_type get unique, descriptive names.
        # e.g. EXTRACTOR_COOKBOOK.md → {date}-{slug}-extractor-cookbook.md
        stem = Path(filename).stem.lower()
        stem_slug = re.sub(r"[^a-z0-9-]+", "-", stem.replace("_", "-"))
        stem_slug = stem_slug.strip("-")[:_MAX_STEM].strip("-") or doc_type
        out_path = raw_dir / f"{today}-{slug}-{stem_slug}.md"
    else:
        out_path = raw_dir / f"{today}-{slug}-{doc_type}.md"

    # --- the file must land directly inside raw/<slug>/ ---
    if out_path.resolve().parent != raw_dir:
        return {"status": "error", "message": "output path is outside the component directory"}

    # --- write and commit ---
    out_path.write_text(content, encoding="utf-8")
    rel_path = str(out_path.relative_to(wiki_root.resolve()))
    git_commit(wiki_root, [out_path], f"wiki: ingest {rel_path}")
    return {
        "status": "ok",
        "path": rel_path,
        "component": slug,
        "doc_type": doc_type,
        "bytes": len(content.encode("utf-8")),
    }
