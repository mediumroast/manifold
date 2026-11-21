# SPDX-License-Identifier: Apache-2.0
"""A failed write leaves the instance as it was (PHASE_4_PLAN Task 20, INT-2 S3 and Must never).

Each case injects one failure into a write tool and compares the whole tree (relative paths, empty
folders and the sha256 of every file outside `.git`) with a snapshot from before the call, then
checks that `wiki_health` still reports healthy.  The refusals of a stale etag and bad frontmatter
are tested elsewhere (`test_pickup_stale_etag_rejected`, `test_write_validation.py`); here they only
add the unchanged-tree assertion.

A case marked `xfail(strict=True)` is a defect the owner has asked to have listed and fixed by the
`bug-coder` after this phase (PHASE_4_PLAN, Open question 10).  When a defect is fixed its case
starts to pass and strict mode fails the run, which tells the fixer to remove the marker.
"""

import errno
import hashlib
import re
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("fastmcp")

from tests.contracts import harness  # noqa: E402
from wiki_backend.health import wiki_health  # noqa: E402

CALLER = {"kind": "human", "roles": ["contributor", "registrar"]}


@pytest.fixture()
def world(tmp_path, monkeypatch):
    """A tool world over a private copy of the fictional instance `examples/acme`, with one caller `contract`."""
    import server
    monkeypatch.setattr(server, "WIKI_ROOT", server.WIKI_ROOT)  # restored when the test ends
    tool_world, root = harness.open_world(tmp_path, monkeypatch.setenv)
    tool_world.who("contract", CALLER["kind"], roles=CALLER["roles"], grants=harness.GRANTS)
    yield tool_world
    tool_world.conn.close()


def snapshot(root):
    """(files: {relative path: sha256}, folders: {relative path}) of everything outside `.git`."""
    files, folders = {}, set()
    for path in sorted(Path(root).rglob("*")):
        relative = path.relative_to(root)
        if relative.parts[0] == ".git":
            continue
        if path.is_dir():
            folders.add(str(relative))
        else:
            files[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files, folders


def head(root):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True).stdout


def assert_unchanged(world, before, head_before):
    files, folders = snapshot(world.root)
    changed = sorted(p for p in set(files) | set(before[0]) if files.get(p) != before[0].get(p))
    assert changed == [], "files changed: %s" % changed
    assert sorted(folders - before[1]) == [], "stray folders: %s" % sorted(folders - before[1])
    assert sorted(before[1] - folders) == [], "folders removed: %s" % sorted(before[1] - folders)
    for page in ("wiki/_sidebar.md", "wiki/log.md"):
        assert files[page] == before[0][page], page
    assert head(world.root) == head_before, "a commit was made"
    healthy, payload = wiki_health(world.root)
    assert healthy, payload["message"]


def call(world, tool, **arguments):
    return world.call("contract", tool, **arguments)


def out_of_space(monkeypatch, root):
    """Path.write_text refuses (ENOSPC) for every file inside the instance."""
    real = Path.write_text

    def write_text(self, *args, **kwargs):
        if Path(root) in Path(self).parents:
            raise OSError(errno.ENOSPC, "No space left on device", str(self))
        return real(self, *args, **kwargs)
    monkeypatch.setattr(Path, "write_text", write_text)


def run_failure(world, tool, arguments):
    before, head_before = snapshot(world.root), head(world.root)
    result = call(world, tool, **arguments)
    return before, head_before, result


NEW_PAGE = {"path": "wiki/decisions/failure-case.md", "content": "# Failure case\n\nBody.\n", "message": "m"}
NEW_FOLDER_PAGE = {"path": "wiki/newarea/failure-case.md", "content": "# Failure case\n\nBody.\n", "message": "m"}
HANDOFF = {"action": "create", "source": "acme-api", "target": "acme-web", "type": "feature", "priority": "low",
           "title": "Failure case", "summary": "s", "what_needs_to_happen": "w"}


def test_a_stale_etag_leaves_the_tree_unchanged(world):
    arguments = {"path": "wiki/architecture/overview.md", "content": "# New\n", "etag": "0" * 16, "message": "m"}
    before, head_before, result = run_failure(world, "wiki_write_page_tool", arguments)
    assert result["status"] == "conflict"
    assert_unchanged(world, before, head_before)


def test_invalid_frontmatter_in_an_existing_folder_leaves_the_tree_unchanged(world):
    arguments = {**NEW_PAGE, "content": "---\ntitle: [unclosed\n---\n\n# Bad\n"}
    before, head_before, result = run_failure(world, "wiki_write_page_tool", arguments)
    assert result["status"] == "error"
    assert_unchanged(world, before, head_before)


@pytest.mark.xfail(strict=True, reason="defect: a page write with invalid frontmatter into a new folder leaves "
                                       "the empty folder behind (wiki_write creates the folder before it validates)")
def test_invalid_frontmatter_in_a_new_folder_leaves_the_tree_unchanged(world):
    arguments = {**NEW_FOLDER_PAGE, "content": "---\ntitle: [unclosed\n---\n\n# Bad\n"}
    before, head_before, result = run_failure(world, "wiki_write_page_tool", arguments)
    assert result["status"] == "error"
    assert_unchanged(world, before, head_before)


def test_a_refused_page_write_leaves_the_tree_unchanged(world, monkeypatch):
    out_of_space(monkeypatch, world.root)
    before, head_before, result = run_failure(world, "wiki_write_page_tool", NEW_PAGE)
    assert result.get("error"), result
    assert_unchanged(world, before, head_before)


@pytest.mark.xfail(strict=True, reason="defect: a refused page write into a new folder leaves the empty folder behind")
def test_a_refused_page_write_into_a_new_folder_leaves_the_tree_unchanged(world, monkeypatch):
    out_of_space(monkeypatch, world.root)
    before, head_before, result = run_failure(world, "wiki_write_page_tool", NEW_FOLDER_PAGE)
    assert result.get("error"), result
    assert_unchanged(world, before, head_before)


def test_a_refused_handoff_write_leaves_the_tree_unchanged(world, monkeypatch):
    out_of_space(monkeypatch, world.root)
    before, head_before, result = run_failure(world, "wiki_handoff_tool", HANDOFF)
    assert not result or result.get("status") != "created", result
    assert_unchanged(world, before, head_before)


@pytest.mark.xfail(strict=True, reason="defect: handoff create writes and commits the handoff page first, so a "
                                       "failing sidebar update leaves a handoff page that is not in the sidebar")
def test_a_failing_sidebar_update_part_way_through_handoff_create_leaves_the_tree_unchanged(world, monkeypatch):
    import wiki_backend.handoff as handoff

    def boom(*args, **kwargs):
        raise OSError(errno.EIO, "Input/output error")
    monkeypatch.setattr(handoff, "update_sidebar_handoff", boom)
    before, head_before, result = run_failure(world, "wiki_handoff_tool", HANDOFF)
    assert not result or result.get("status") != "created", result
    assert_unchanged(world, before, head_before)


@pytest.mark.xfail(strict=True, reason="defect: a failing log append after the handoff page and sidebar entry were "
                                       "written leaves both behind with no log line")
def test_a_failing_log_append_part_way_through_handoff_create_leaves_the_tree_unchanged(world, monkeypatch):
    import wiki_backend.handoff as handoff

    def boom(*args, **kwargs):
        raise OSError(errno.EIO, "Input/output error")
    monkeypatch.setattr(handoff, "wiki_log_append", boom)
    before, head_before, result = run_failure(world, "wiki_handoff_tool", HANDOFF)
    assert not result or result.get("status") != "created", result
    assert_unchanged(world, before, head_before)


def refuse_every_commit(monkeypatch):
    """git declines every commit (the documented non-fatal path of git_commit)."""
    import wiki_backend.agent_guide, wiki_backend.ingest, wiki_backend.log, wiki_backend.register, wiki_backend.write
    refused = {"committed": False, "reason": "git refused the commit (injected by the test)"}
    for module in (wiki_backend.agent_guide, wiki_backend.ingest, wiki_backend.log, wiki_backend.register,
                   wiki_backend.write):
        monkeypatch.setattr(module, "git_commit", lambda *a, **k: refused)


def test_git_refusing_the_commit_of_a_page_write_keeps_the_file_and_changes_nothing_else(world, monkeypatch):
    refuse_every_commit(monkeypatch)
    before, head_before = snapshot(world.root), head(world.root)
    result = call(world, "wiki_write_page_tool", **NEW_PAGE)
    assert result["status"] == "created"  # documented: the write succeeded on disk, the commit is non-fatal
    files, folders = snapshot(world.root)
    assert sorted(p for p in files if files[p] != before[0].get(p)) == ["wiki/decisions/failure-case.md"]
    assert folders == before[1]
    assert head(world.root) == head_before
    assert wiki_health(world.root)[0]


def test_git_refusing_the_commits_of_a_handoff_create_changes_only_what_the_code_documents(world, monkeypatch):
    refuse_every_commit(monkeypatch)
    before, head_before = snapshot(world.root), head(world.root)
    result = call(world, "wiki_handoff_tool", **HANDOFF)
    assert result["status"] == "created"
    files, folders = snapshot(world.root)
    changed = sorted(p for p in files if files[p] != before[0].get(p))
    # the handoff page, its sidebar entry and its log entry: nothing else
    assert changed == ["wiki/_sidebar.md", "wiki/handoffs/acme-api-to-acme-web/feature-failure-case.md",
                       "wiki/log.md"]
    assert folders == before[1]
    assert head(world.root) == head_before
    assert wiki_health(world.root)[0]


@pytest.mark.xfail(strict=True, reason="defect: when git refuses the commit, the tool result still looks like a "
                                       "plain success and does not say the change was not committed")
def test_git_refusing_the_commit_is_reported_to_the_caller(world, monkeypatch):
    refuse_every_commit(monkeypatch)
    result = call(world, "wiki_write_page_tool", **NEW_PAGE)
    # The report must be specific: a `committed` flag that is false, or an error or warning text that
    # says the change was not committed.  A field or message that merely contains the word "commit"
    # does not count, and neither does the plain success shape.
    says_not_committed = re.compile(r"not (been )?committed|commit (failed|was refused|did not|was not)|uncommitted",
                                    re.IGNORECASE)
    texts = [str(result.get(key) or "") for key in ("error", "warning", "message")]
    assert result.get("committed") is False or any(says_not_committed.search(t) for t in texts), result
