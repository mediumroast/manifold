# SPDX-License-Identifier: Apache-2.0
"""Tests for wiki_write_page frontmatter validation."""

import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from wiki_backend.write import wiki_write_page
from wiki_backend.handoff import wiki_write_handoff_page
from wiki_backend.models import WikiWriteRequest

# wiki_root fixture provided by conftest.py


_VALID_HANDOFF = """\
---
title: "Test handoff"
type: bug
source_component: acme-qa
target_component: acme.io
status: open
priority: high
created: 2026-07-07
updated: 2026-07-07
blocking: []
blocked_by: []
---

## Summary
A test handoff.
"""

_HANDOFF_PATH = "wiki/handoffs/acme-qa-to-acme.io/bug-test.md"


def test_malformed_yaml_rejected(wiki_root):
    content = "---\n: bad: [yaml\n---\nbody\n"
    req = WikiWriteRequest(path=_HANDOFF_PATH, content=content, message="test")
    result = wiki_write_handoff_page(wiki_root, req)
    assert result.status == "error"
    assert "malformed" in result.error.lower()
    assert not (wiki_root / _HANDOFF_PATH).exists()


def test_handoff_missing_source_component_rejected(wiki_root):
    content = """\
---
title: "Test"
type: bug
target_component: acme.io
status: open
priority: high
created: 2026-07-07
updated: 2026-07-07
blocking: []
blocked_by: []
---
body
"""
    req = WikiWriteRequest(path=_HANDOFF_PATH, content=content, message="test")
    result = wiki_write_handoff_page(wiki_root, req)
    assert result.status == "error"
    assert "source_component" in result.error
    assert not (wiki_root / _HANDOFF_PATH).exists()


def test_handoff_legacy_source_field_rejected(wiki_root):
    content = """\
---
title: "Test"
type: bug
source: acme-qa
target_component: acme.io
status: open
priority: high
created: 2026-07-07
updated: 2026-07-07
blocking: []
blocked_by: []
---
body
"""
    req = WikiWriteRequest(path=_HANDOFF_PATH, content=content, message="test")
    result = wiki_write_handoff_page(wiki_root, req)
    assert result.status == "error"
    assert "source" in result.error
    assert not (wiki_root / _HANDOFF_PATH).exists()


def test_valid_handoff_accepted(wiki_root):
    req = WikiWriteRequest(path=_HANDOFF_PATH, content=_VALID_HANDOFF, message="test")
    result = wiki_write_handoff_page(wiki_root, req)
    assert result.status == "created"
    assert (wiki_root / _HANDOFF_PATH).exists()


def test_non_handoff_with_valid_frontmatter_accepted(wiki_root):
    content = """\
---
title: Acme API
component: acme-api
status: active
last_updated: 2026-07-07
owner: team
summary: Backend service.
---

## Overview
Content.
"""
    path = "wiki/components/acme-api.md"
    req = WikiWriteRequest(path=path, content=content, message="test")
    result = wiki_write_page(wiki_root, req)
    assert result.status == "created"
    assert (wiki_root / path).exists()


def test_no_frontmatter_accepted(wiki_root):
    content = "# Simple page\n\nNo frontmatter here.\n"
    path = "wiki/guides/notes.md"
    req = WikiWriteRequest(path=path, content=content, message="test")
    result = wiki_write_page(wiki_root, req)
    assert result.status == "created"
    assert (wiki_root / path).exists()
