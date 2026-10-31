# SPDX-License-Identifier: Apache-2.0
"""Tests for wiki_backend.handoff — handoff lifecycle: create, claim, close, list."""

import pytest
from pathlib import Path

from wiki_backend.handoff import (
    handoff_create, handoff_claim, handoff_close, handoff_list,
    handoff_request_review, handoff_confirm, handoff_reject,
)


# ── helpers ────────────────────────────────────────────────────────────────────


def _create_valid(wiki_root: Path, **kwargs) -> dict:
    """Create a valid handoff with default values, overridable via kwargs."""
    defaults = dict(
        source="acme-api",
        target="acme-web",
        type="bug",
        priority="high",
        title="Fix the widget",
        summary="The widget is broken and acme-web needs to fix it.",
        what_needs_to_happen="- [ ] Identify root cause\n- [ ] Apply fix",
        technical_details="Widget endpoint: POST /widget",
    )
    defaults.update(kwargs)
    return handoff_create(wiki_root, **defaults)


# ── create tests ───────────────────────────────────────────────────────────────


def test_create_valid_handoff(wiki_root: Path):
    result = _create_valid(wiki_root)
    assert result.get("status") == "created"
    assert "path" in result
    assert "id" in result
    # File exists
    assert (wiki_root / result["path"]).exists()
    content = (wiki_root / result["path"]).read_text()
    assert "source_component: acme-api" in content
    assert "target_component: acme-web" in content
    assert "status: open" in content
    assert "priority: high" in content


def test_create_unknown_slug_rejected(wiki_root: Path):
    result = handoff_create(
        wiki_root,
        source="unknown-thing",
        target="acme-web",
        type="bug",
        priority="high",
        title="Test",
        summary="Summary",
        what_needs_to_happen="Do something",
    )
    assert "error" in result
    # No file created
    handoffs_dir = wiki_root / "wiki" / "handoffs"
    md_files = list(handoffs_dir.rglob("*.md"))
    assert len(md_files) == 0


def test_create_duplicate_rejected(wiki_root: Path):
    first = _create_valid(wiki_root)
    assert first.get("status") == "created"

    second = _create_valid(wiki_root)  # Same title → same id → same path
    assert "error" in second
    assert "already exists" in second["error"].lower()


def test_create_path_format(wiki_root: Path):
    result = _create_valid(wiki_root, source="acme-api", target="acme-web", type="feature", title="Token refresh v2")
    assert result.get("status") == "created"
    path = result["path"]
    # Must match wiki/handoffs/{source}-to-{target}/{type}-{id}.md
    assert path.startswith("wiki/handoffs/acme-api-to-acme-web/feature-")
    assert path.endswith(".md")


# ── claim tests ────────────────────────────────────────────────────────────────


def test_claim_sets_in_progress(wiki_root: Path):
    created = _create_valid(wiki_root)
    claimed = handoff_claim(wiki_root, created["path"])
    assert claimed.get("status") == "claimed"
    content = (wiki_root / created["path"]).read_text()
    assert "status: in-progress" in content


def test_claim_returns_summary(wiki_root: Path):
    created = _create_valid(wiki_root, summary="My summary text.")
    claimed = handoff_claim(wiki_root, created["path"])
    assert claimed.get("status") == "claimed"
    assert "summary" in claimed
    assert "what_needs_to_happen" in claimed
    assert "My summary text." in claimed["summary"]


def test_claim_already_completed_rejected(wiki_root: Path):
    created = _create_valid(wiki_root)
    handoff_claim(wiki_root, created["path"])
    # Close it
    handoff_close(wiki_root, created["path"], resolution="Done.")
    # Try to claim again
    result = handoff_claim(wiki_root, created["path"])
    assert "error" in result
    assert "completed" in result["error"].lower()


# ── close tests ────────────────────────────────────────────────────────────────


def test_close_sets_completed(wiki_root: Path):
    created = _create_valid(wiki_root)
    handoff_claim(wiki_root, created["path"])
    closed = handoff_close(wiki_root, created["path"], resolution="Fixed the widget by patching the handler.")
    assert closed.get("status") == "completed"
    content = (wiki_root / created["path"]).read_text()
    assert "status: completed" in content


def test_close_fills_implementation_notes(wiki_root: Path):
    created = _create_valid(wiki_root)
    handoff_claim(wiki_root, created["path"])
    handoff_close(wiki_root, created["path"], resolution="Patched the handler in widget.py line 42.")
    content = (wiki_root / created["path"]).read_text()
    assert "Patched the handler in widget.py line 42." in content


def test_close_returns_next_step(wiki_root: Path):
    created = _create_valid(wiki_root)
    handoff_claim(wiki_root, created["path"])
    result = handoff_close(wiki_root, created["path"], resolution="Done.")
    assert "next" in result
    assert "acme-web" in result["next"]


# ── list tests ─────────────────────────────────────────────────────────────────


def test_list_filters_by_target(wiki_root: Path):
    # Create two handoffs to different targets
    _create_valid(wiki_root, target="acme-web", title="First handoff")
    _create_valid(wiki_root, source="acme-web", target="acme-api", title="Second handoff")

    result = handoff_list(wiki_root, target="acme-web")
    assert "handoffs" in result
    for h in result["handoffs"]:
        assert h["target_component"] == "acme-web"


def test_list_filters_by_status(wiki_root: Path):
    created1 = _create_valid(wiki_root, title="Open handoff")
    created2 = _create_valid(wiki_root, title="Claimed handoff")
    handoff_claim(wiki_root, created2["path"])

    open_result = handoff_list(wiki_root, status="open")
    for h in open_result["handoffs"]:
        assert h["status"] == "open"

    in_progress_result = handoff_list(wiki_root, status="in-progress")
    for h in in_progress_result["handoffs"]:
        assert h["status"] == "in-progress"


# ── sidebar placement tests ────────────────────────────────────────────────────


def _sidebar_with_existing_group(wiki_root: Path) -> None:
    """Write a _sidebar.md that already has one handoff group (A → B)."""
    sidebar = wiki_root / "wiki" / "_sidebar.md"
    sidebar.write_text(
        "- **Handoffs**\n"
        "  - acme-api → acme-web\n"
        "    - [○ Existing handoff](/handoffs/acme-api-to-acme-web/bug-existing.md)\n"
        "\n"
        "- **Log**\n"
        "  - [Operation Log](/log.md)\n",
        encoding="utf-8",
    )
    import subprocess
    subprocess.run(["git", "add", "-A"], cwd=wiki_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "test: add sidebar with existing group"],
        cwd=wiki_root, check=True, capture_output=True,
    )


def test_sidebar_new_group_appended_before_log(wiki_root: Path):
    """A handoff for a brand-new source→target pair creates its group inside Handoffs."""
    _sidebar_with_existing_group(wiki_root)
    _create_valid(wiki_root, source="acme-api", target="acme-web", title="Second handoff")
    sidebar = (wiki_root / "wiki" / "_sidebar.md").read_text()
    assert "acme-api → acme-web" in sidebar
    log_pos = sidebar.index("**Log**")
    group_pos = sidebar.index("acme-api → acme-web")
    assert group_pos < log_pos


def test_sidebar_reverse_direction_gets_own_group(wiki_root: Path):
    """
    A handoff in the reverse direction (B → A) must appear under its own
    group label, not appended to the existing A → B group.

    Regression test for the bug where last_child_line scanning bled into
    sibling groups, inserting the link under the wrong header.
    """
    _sidebar_with_existing_group(wiki_root)

    # Create a second group in the opposite direction
    _create_valid(wiki_root, source="acme-web", target="acme-api", title="Reverse handoff")

    sidebar = (wiki_root / "wiki" / "_sidebar.md").read_text()

    # Both group labels must be present
    assert "  - acme-api → acme-web\n" in sidebar
    assert "  - acme-web → acme-api\n" in sidebar

    # The reverse-direction link must appear AFTER its own group label,
    # not after the acme-api → acme-web group's children.
    web_to_api_label_pos = sidebar.index("  - acme-web → acme-api\n")
    reverse_link_pos = sidebar.index("/handoffs/acme-web-to-acme-api/")
    api_to_web_last_child_pos = sidebar.index("/handoffs/acme-api-to-acme-web/bug-existing.md")

    assert reverse_link_pos > web_to_api_label_pos, (
        "reverse-direction link must appear after its own group label"
    )
    assert reverse_link_pos > api_to_web_last_child_pos, (
        "reverse-direction link must not be inserted inside the acme-api → acme-web group"
    )


# ── review cycle tests ─────────────────────────────────────────────────────────


def _claimed_handoff(wiki_root: Path) -> str:
    """Create and claim a handoff; return its path."""
    result = _create_valid(wiki_root)
    path = result["path"]
    handoff_claim(wiki_root, path)
    return path


def _needs_review_handoff(wiki_root: Path) -> str:
    """Create, claim, and request-review a handoff; return its path."""
    path = _claimed_handoff(wiki_root)
    handoff_request_review(wiki_root, path, "Implemented the fix in widget.py")
    return path


# request-review

def test_request_review_sets_needs_review(wiki_root: Path):
    path = _claimed_handoff(wiki_root)
    result = handoff_request_review(wiki_root, path, "Done — see widget.py")
    assert result.get("status") == "needs-review"
    content = (wiki_root / path).read_text()
    assert "status: needs-review" in content


def test_request_review_appends_notes(wiki_root: Path):
    path = _claimed_handoff(wiki_root)
    handoff_request_review(wiki_root, path, "Fixed in widget.py line 42")
    content = (wiki_root / path).read_text()
    assert "Fixed in widget.py line 42" in content


def test_request_review_rejects_wrong_status(wiki_root: Path):
    result = _create_valid(wiki_root)
    path = result["path"]
    # open, not in-progress
    result = handoff_request_review(wiki_root, path, "some notes")
    assert "error" in result
    assert "in-progress" in result["error"]


# confirm

def test_confirm_sets_completed(wiki_root: Path):
    path = _needs_review_handoff(wiki_root)
    result = handoff_confirm(wiki_root, path)
    assert result.get("status") == "confirmed"
    content = (wiki_root / path).read_text()
    assert "status: completed" in content


def test_confirm_appends_notes_when_provided(wiki_root: Path):
    path = _needs_review_handoff(wiki_root)
    handoff_confirm(wiki_root, path, notes="Looks good, well done")
    content = (wiki_root / path).read_text()
    assert "Looks good, well done" in content


def test_confirm_rejects_wrong_status(wiki_root: Path):
    path = _claimed_handoff(wiki_root)
    # in-progress, not needs-review
    result = handoff_confirm(wiki_root, path)
    assert "error" in result
    assert "needs-review" in result["error"]


# reject

def test_reject_returns_to_in_progress(wiki_root: Path):
    path = _needs_review_handoff(wiki_root)
    result = handoff_reject(wiki_root, path, "The fix is incomplete")
    assert result.get("status") == "rejected"
    content = (wiki_root / path).read_text()
    assert "status: in-progress" in content


def test_reject_appends_feedback_to_blockers(wiki_root: Path):
    path = _needs_review_handoff(wiki_root)
    handoff_reject(wiki_root, path, "Missing edge case for empty input")
    content = (wiki_root / path).read_text()
    assert "Missing edge case for empty input" in content
    assert "Blockers" in content


def test_reject_rejects_wrong_status(wiki_root: Path):
    result = _create_valid(wiki_root)
    path = result["path"]
    # open, not needs-review
    result = handoff_reject(wiki_root, path, "some feedback")
    assert "error" in result
    assert "needs-review" in result["error"]
