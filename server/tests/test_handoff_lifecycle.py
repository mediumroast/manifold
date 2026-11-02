# SPDX-License-Identifier: Apache-2.0
"""
Handoff post-and-pickup lifecycle tests.

Simulates two component agents collaborating through the wiki:
  - acme-api agent   : posts a feature handoff for acme.io
  - mr.io agent   : discovers it via inventory, reads it, claims it,
                    works on it, and marks it completed

Each test step is independent but they share a single wiki_root fixture
so the state accumulated across steps reflects real agent behaviour.
"""

import subprocess
from pathlib import Path

import pytest

from wiki_backend.inventory import wiki_inventory
from wiki_backend.log import wiki_log_append
from wiki_backend.models import WikiLogRequest, WikiWriteRequest
from wiki_backend.read import wiki_read
from wiki_backend.handoff import wiki_write_handoff_page

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

HANDOFF_PATH = "wiki/handoffs/acme-api-to-acme.io/feature-jwt-refresh-v2.md"

OPEN_CONTENT = """\
---
title: "JWT refresh token endpoint — v2 response shape"
type: feature
source_component: acme-api
target_component: acme.io
status: open
priority: high
created: 2026-05-22
updated: 2026-05-22
blocking: []
blocked_by: []
---

## Summary
Acme API's /auth/refresh response shape is changing in v2.
acme.io BFF must update its token-refresh logic.

## Context
The v1 flat response is being replaced with a nested `tokens` object.

## What needs to happen
- [ ] Update lib/auth/refresh.ts to read tokens.access_token
- [ ] Schedule proactive refresh from expires_in field

## Technical details
v2 adds: {"tokens": {"access_token": "...", "refresh_token": "..."}, "expires_in": 3600}

## Integration spec
Endpoint URL and HTTP method unchanged.

## Implementation notes
_(empty)_

## Blockers
_(none)_

## Related handoffs
- None
"""


def _git_log(wiki_root: Path) -> list[str]:
    """Return one-line git log messages, newest first."""
    result = subprocess.run(
        ["git", f"-c", f"safe.directory={wiki_root}", "log", "--oneline"],
        cwd=wiki_root,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().splitlines()


def _read_log_md(wiki_root: Path) -> str:
    return (wiki_root / "wiki" / "log.md").read_text()


# ---------------------------------------------------------------------------
# Post phase — acme-api agent
# ---------------------------------------------------------------------------


def test_post_creates_handoff(wiki_root):
    """acme-api agent posts a new handoff; response shows created + etag."""
    req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=OPEN_CONTENT,
        etag=None,
        message="acme-api agent: post JWT refresh v2 handoff for acme.io",
    )
    resp = wiki_write_handoff_page(wiki_root,req)

    assert resp.status == "created"
    assert resp.etag is not None
    assert resp.error is None
    assert (wiki_root / HANDOFF_PATH).exists()


def test_post_duplicate_blocked(wiki_root):
    """A second create attempt (no etag) is rejected as a conflict."""
    # Ensure file exists first
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="setup")
    wiki_write_handoff_page(wiki_root,req)

    # Second create without etag → conflict
    req2 = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="dupe")
    resp = wiki_write_handoff_page(wiki_root,req2)

    assert resp.status == "conflict"
    assert "already exists" in resp.error


def test_post_appends_to_log(wiki_root):
    """wiki_log_append after posting writes an entry to wiki/log.md."""
    log_req = WikiLogRequest(
        action="create-handoff",
        message="acme-api agent posted feature-jwt-refresh-v2 for acme.io",
        component="acme-api",
    )
    result = wiki_log_append(wiki_root, log_req)

    assert result["status"] == "appended"
    assert "create-handoff" in _read_log_md(wiki_root)
    assert "acme-api" in _read_log_md(wiki_root)


def test_post_creates_git_commit(wiki_root):
    """wiki_write_page auto-commits; the commit message matches the agent message."""
    msg = "acme-api agent: post JWT refresh v2 handoff for acme.io"
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message=msg)
    wiki_write_handoff_page(wiki_root,req)

    log = _git_log(wiki_root)
    assert any(msg in line for line in log), f"Expected commit not found in:\n{chr(10).join(log)}"


# ---------------------------------------------------------------------------
# Pickup phase — acme.io agent
# ---------------------------------------------------------------------------


def test_pickup_inventory_shows_open_handoff(wiki_root):
    """
    After acme-api posts, wiki_inventory returns the handoff with status=open
    and correct from/to components.
    """
    # Post the handoff first
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="setup")
    wiki_write_handoff_page(wiki_root,req)

    inv = wiki_inventory(wiki_root)
    handoffs = inv.handoffs

    assert len(handoffs) == 1
    h = handoffs[0]
    assert h.from_component == "acme-api"
    assert h.to_component == "acme.io"
    assert h.status == "open"
    assert h.path == HANDOFF_PATH


def test_pickup_read_returns_content_and_etag(wiki_root):
    """wiki_read returns the full page body, parsed frontmatter, and etag."""
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="setup")
    write_resp = wiki_write_handoff_page(wiki_root,req)

    page = wiki_read(wiki_root, HANDOFF_PATH)

    assert page.path == HANDOFF_PATH
    assert page.etag == write_resp.etag
    assert page.frontmatter["status"] == "open"
    assert page.frontmatter["source_component"] == "acme-api"
    assert page.frontmatter["target_component"] == "acme.io"
    assert "Summary" in page.body


def test_pickup_claim_sets_in_progress(wiki_root):
    """acme.io agent claims the handoff; status transitions to in-progress."""
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="setup")
    create_resp = wiki_write_handoff_page(wiki_root,req)

    in_progress_content = OPEN_CONTENT.replace("status: open", "status: in-progress")
    update_req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=in_progress_content,
        etag=create_resp.etag,
        message="acme.io agent: claim handoff, status → in-progress",
    )
    update_resp = wiki_write_handoff_page(wiki_root,update_req)

    assert update_resp.status == "updated"
    assert update_resp.etag != create_resp.etag  # new etag after change

    page = wiki_read(wiki_root, HANDOFF_PATH)
    assert page.frontmatter["status"] == "in-progress"


def test_pickup_stale_etag_rejected(wiki_root):
    """Writing with a stale etag returns status=conflict and reports both etags."""
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="setup")
    create_resp = wiki_write_handoff_page(wiki_root,req)

    # First update — advances the etag
    update_req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=OPEN_CONTENT.replace("status: open", "status: in-progress"),
        etag=create_resp.etag,
        message="claim",
    )
    wiki_write_handoff_page(wiki_root,update_req)

    # Second update with the original (now stale) etag
    stale_req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=OPEN_CONTENT.replace("status: open", "status: completed"),
        etag=create_resp.etag,  # stale
        message="should be rejected",
    )
    conflict_resp = wiki_write_handoff_page(wiki_root,stale_req)

    assert conflict_resp.status == "conflict"
    assert "Etag mismatch" in conflict_resp.error


def test_pickup_complete_handoff(wiki_root):
    """Full open→in-progress→completed transition; final inventory shows completed."""
    # Create
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="setup")
    create_resp = wiki_write_handoff_page(wiki_root,req)

    # Claim
    claimed_content = OPEN_CONTENT.replace("status: open", "status: in-progress")
    claim_req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=claimed_content,
        etag=create_resp.etag,
        message="claim",
    )
    claim_resp = wiki_write_handoff_page(wiki_root,claim_req)

    # Complete
    completed_content = claimed_content.replace("status: in-progress", "status: completed")
    complete_req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=completed_content,
        etag=claim_resp.etag,
        message="acme.io agent: mark completed",
    )
    complete_resp = wiki_write_handoff_page(wiki_root,complete_req)

    assert complete_resp.status == "updated"
    assert complete_resp.error is None

    # Inventory reflects final state
    inv = wiki_inventory(wiki_root)
    assert inv.handoffs[0].status == "completed"


def test_pickup_completion_logged(wiki_root):
    """Log append after completion writes a complete-handoff entry."""
    log_req = WikiLogRequest(
        action="complete-handoff",
        message="acme.io completed feature-jwt-refresh-v2",
        component="acme.io",
    )
    wiki_log_append(wiki_root, log_req)

    log_content = _read_log_md(wiki_root)
    assert "complete-handoff" in log_content
    assert "acme.io" in log_content


def test_pickup_git_commits_each_transition(wiki_root):
    """Every write (post, claim, complete, log) creates its own git commit."""
    initial_count = len(_git_log(wiki_root))

    # Post
    req = WikiWriteRequest(path=HANDOFF_PATH, content=OPEN_CONTENT, etag=None, message="post")
    create_resp = wiki_write_handoff_page(wiki_root,req)

    # Log the post
    wiki_log_append(wiki_root, WikiLogRequest(action="create-handoff", message="posted", component="acme-api"))

    # Claim
    claim_req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=OPEN_CONTENT.replace("status: open", "status: in-progress"),
        etag=create_resp.etag,
        message="claim",
    )
    claim_resp = wiki_write_handoff_page(wiki_root,claim_req)

    # Complete
    complete_req = WikiWriteRequest(
        path=HANDOFF_PATH,
        content=OPEN_CONTENT.replace("status: open", "status: completed"),
        etag=claim_resp.etag,
        message="complete",
    )
    wiki_write_handoff_page(wiki_root,complete_req)

    # Log the completion
    wiki_log_append(wiki_root, WikiLogRequest(action="complete-handoff", message="done", component="acme.io"))

    final_count = len(_git_log(wiki_root))
    # 5 operations: post, log-post, claim, complete, log-complete
    assert final_count == initial_count + 5, (
        f"Expected {initial_count + 5} commits, got {final_count}:\n"
        + "\n".join(_git_log(wiki_root))
    )
