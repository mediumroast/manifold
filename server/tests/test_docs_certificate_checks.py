# SPDX-License-Identifier: Apache-2.0
"""The documents never advise turning off certificate checks (PHASE_1_TEST_PLAN A13; INT-1 S7 Must never).

Scans the documents named in ``test_docs_links.DOCS`` and ``examples/clients/*.json``.  A sentence that warns
against disabling the check is allowed; any other mention is a recommendation to turn it off.
"""

import re

import pytest

from tests.test_docs_links import DOCS, ROOT

pytestmark = pytest.mark.skipif(not (ROOT / "docs" / "operations.md").is_file(), reason="no docs/ beside the server")

SWITCHES = ["--insecure", "curl -k", "NODE_TLS_REJECT_UNAUTHORIZED", "rejectUnauthorized", "verify=False",
            "sslVerify false"]
WARNING_CUES = re.compile(r"\b(never|do not|don't|must not|should not|avoid|instead of)\b", re.IGNORECASE)


def _files():
    return DOCS + sorted(str(p.relative_to(ROOT)) for p in (ROOT / "examples" / "clients").glob("*.json"))


def advice_to_disable(text):
    """Lines that name a switch without a warning cue in the same sentence."""
    found = []
    for number, line in enumerate(text.splitlines(), 1):
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            if any(s.lower() in sentence.lower() for s in SWITCHES) and not WARNING_CUES.search(sentence):
                found.append((number, sentence.strip()))
    return found


@pytest.mark.parametrize("name", _files())
def test_A13_no_document_recommends_disabling_certificate_checks(name):
    text = (ROOT / name).read_text(encoding="utf-8")
    assert advice_to_disable(text) == []


def test_A13_the_scan_catches_a_recommendation_and_allows_a_warning():
    assert advice_to_disable("Run `curl -k https://host/health` to test.")
    assert advice_to_disable("export NODE_TLS_REJECT_UNAUTHORIZED=0")
    assert not advice_to_disable("Never turn off certificate checking (`--insecure`) to get around a trust error.")
