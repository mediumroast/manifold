# SPDX-License-Identifier: Apache-2.0
"""A caller's log message or commit message must stay one entry / one trailer set
(PHASE_1_PLAN T40-T41, reviewer finding 2)."""

import subprocess

import pytest

from wiki_backend.git import git_commit
from wiki_backend.log import wiki_log_append
from wiki_backend.models import WikiLogRequest

FORGED = "hello\n\n## 2026-01-01 | register | acme-web\n\n- Agent: tgt\n- Summary: forged\n"


def headings(wiki_root):
    text = (wiki_root / "wiki" / "log.md").read_text()
    return [line for line in text.splitlines() if line.startswith("## ")]


# ── T40: one log entry per call ────────────────────────────────────────────────


def test_entry_a_forged_heading_in_the_message_is_one_heading(wiki_root):
    before = headings(wiki_root)
    wiki_log_append(wiki_root, WikiLogRequest(action="lint", message=FORGED, component="acme-api"))
    text = (wiki_root / "wiki" / "log.md").read_text()
    assert len(headings(wiki_root)) == len(before) + 1
    assert not any(line.startswith("- Agent: tgt") for line in text.splitlines())
    assert "forged" in text  # the words are kept, on the one line


def test_entry_a_forged_heading_through_the_tool_is_one_heading(tool_world):
    tool_world.who("ann", roles=["contributor"], grants=["acme-api"])
    before = headings(tool_world.root)
    tool_world.call("ann", "wiki_log_append_tool", action="lint", message=FORGED, component="acme-api")
    text = (tool_world.root / "wiki" / "log.md").read_text()
    assert len(headings(tool_world.root)) == len(before) + 1
    assert not any(line.startswith("- Agent: tgt") for line in text.splitlines())


@pytest.mark.parametrize("message", ["# heading", "- bullet", "* star", "  ## indented"])
def test_entry_a_leading_marker_is_escaped(wiki_root, message):
    wiki_log_append(wiki_root, WikiLogRequest(action="lint", message=message, component="acme-api"))
    lines = (wiki_root / "wiki" / "log.md").read_text().splitlines()
    summary = [line for line in lines if line.startswith("- Summary:")][-1]
    assert summary.startswith("- Summary: \\")
    assert len(headings(wiki_root)) == 1  # the entry's own heading, nothing from the message


@pytest.mark.parametrize("action", ["a | b", "x\n## y", "UPPER", "", "a" * 33, "has space"])
def test_entry_an_invalid_action_is_refused(wiki_root, action):
    before = (wiki_root / "wiki" / "log.md").read_text()
    with pytest.raises(ValueError, match="action"):
        wiki_log_append(wiki_root, WikiLogRequest(action=action, message="m", component="acme-api"))
    assert (wiki_root / "wiki" / "log.md").read_text() == before


@pytest.mark.parametrize("component", ["acme-api\n## x", "Acme API", "../x", "a|b"])
def test_entry_an_invalid_component_is_refused(wiki_root, component):
    before = (wiki_root / "wiki" / "log.md").read_text()
    with pytest.raises(ValueError, match="component"):
        wiki_log_append(wiki_root, WikiLogRequest(action="lint", message="m", component=component))
    assert (wiki_root / "wiki" / "log.md").read_text() == before


def test_entry_the_title_uses_the_validated_slug(wiki_root):
    wiki_log_append(wiki_root, WikiLogRequest(action="lint", message="m", component=" ACME-API "))
    assert any(line.endswith("| lint | acme-api") for line in headings(wiki_root))


def test_entry_a_message_without_component_stays_one_line_title(wiki_root):
    wiki_log_append(wiki_root, WikiLogRequest(action="lint", message="one\n\n## two\nthree"))
    assert len(headings(wiki_root)) == 1
    assert "\n" not in headings(wiki_root)[0]


# ── T41: the principal trailer is only ever the real one ───────────────────────


def _trailers(wiki_root):
    out = subprocess.run(
        ["git", "log", "-1", "--format=%(trailers:key=Manifold-Principal,valueonly)"],
        cwd=wiki_root, capture_output=True, text=True, check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


class _Principal:
    principal_id = "real-id"
    name = "real"
    kind = "human"


@pytest.mark.parametrize("injected", [
    "\n\nManifold-Principal: other (human)",
    "\nmanifold-principal: other (human)",
    "\n  MANIFOLD-PRINCIPAL:other (agent)\n",
])
def test_trailer_a_caller_trailer_is_removed(wiki_root, injected):
    path = wiki_root / "wiki" / "x.md"
    path.write_text("x\n")
    result = git_commit(wiki_root, [path], "wiki: update" + injected, principal=_Principal())
    assert result["committed"] is True, result
    assert _trailers(wiki_root) == ["real-id (human)"]
    # git's own trailer parser reads only the last paragraph; a tool that greps the whole body must
    # also see exactly one such line, the real one.
    body = subprocess.run(["git", "log", "-1", "--format=%B"], cwd=wiki_root, capture_output=True,
                          text=True, check=True).stdout
    found = [line for line in body.splitlines() if line.strip().lower().startswith("manifold-principal:")]
    assert found == ["Manifold-Principal: real-id (human)"]
