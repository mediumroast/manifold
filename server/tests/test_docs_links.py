# SPDX-License-Identifier: Apache-2.0
"""Every relative link in the security-work documents resolves, and the stale wording is gone (PHASE_1_PLAN T34, T35)."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ["README.md", "server/README.md", "docs/README.md", "docs/operations.md", "docs/tls.md", "docs/quickstart.md",
        "docs/concepts.md", "examples/starter/README.md"]

pytestmark = pytest.mark.skipif(not (ROOT / "docs" / "operations.md").is_file(), reason="no docs/ beside the server")

LINK = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    text = re.sub(r"[`*_]", "", heading.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path: Path):
    found = set()
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code and line.startswith("#"):
            found.add(slug(line.lstrip("#")))
    return found


@pytest.mark.parametrize("name", DOCS)
def test_every_relative_link_resolves(name):
    page = ROOT / name
    text = page.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.S)  # links inside code blocks are examples
    bad = []
    for target in LINK.findall(text):
        if re.match(r"^[a-z]+:", target) or target.startswith("#") and False:
            continue
        path_part, _, fragment = target.partition("#")
        resolved = (page.parent / path_part).resolve() if path_part else page
        if not resolved.exists():
            bad.append(target)
        elif fragment and resolved.suffix == ".md" and fragment not in anchors(resolved):
            bad.append(target + " (no such heading)")
    assert bad == [], "%s: %s" % (name, bad)


def test_the_old_target_close_wording_is_gone():
    hits = []
    for folder in ("docs", "assets", "examples"):
        for path in (ROOT / folder).rglob("*"):
            if path.is_file() and "plans" not in path.parts and path.suffix in (".md", ".py", ".json"):
                if "target may also: close" in path.read_text(encoding="utf-8", errors="ignore"):
                    hits.append(str(path))
    assert hits == []


def test_no_document_says_authentication_is_optional_or_off():
    for name in DOCS:
        text = (ROOT / name).read_text(encoding="utf-8").lower()
        for phrase in ("token is optional", "authentication is off", "no token means", "shared token and nothing else",
                       "one secret for everyone", "no tls.", "15 tools"):
            assert phrase not in text, (name, phrase)


def test_the_handoff_close_helpers_give_the_close_to_the_source_only():
    for relative in ("assets/helpers/commands/handoff-close.md", "assets/helpers/prompts/handoff-close.prompt.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Only the source" in text and "request review" in text.lower() or "update to request review" in text
        assert "completed handoff" not in text and "target" in text.lower()
