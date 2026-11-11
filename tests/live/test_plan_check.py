"""Tests for plan_check.py, the checker for reflected test plans (INT-25 S1, S4; plan T45, T46).

Run: .venv/bin/python -m pytest tests/live -q
(ci.yml runs bundles/base only; wiring this folder into CI is the owner's call.)
"""
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import plan_check  # noqa: E402  (imported from this folder)

FIXTURES = HERE / "fixtures" / "test_plans"

NAMES = ["no-intent-cited", "all-automated-cases-pre-ticked", "case-without-source",
         "no-gap-statement", "no-questions-section"]


def _names(text):
    return sorted(name for name, _detail in plan_check.check(text))


GOOD = """# PHASE_9_TEST_PLAN.md
**Approved by:**

## Source intents
- `INT-99` Export a wiki (accepted). Seeds S1, S2.

## Gaps found
- A1 covers S2.

## Manual test cases

### M1 — A manual check
**Derived from:** Unconfirmed: owner to confirm
**Existing or new:** new

## Automated test cases

### A1 — A gap check
**Derived from:** INT-99 S2
**Existing or new:** new
**Todo:** [ ]

## Questions for the human

### Q1 — Which pages may a denied caller see?
**Blocking:** yes
**Answer:**

## Quality gates
- [ ] No blocking question is open
"""


def test_the_good_text_used_below_has_no_finding():
    assert _names(GOOD) == []


@pytest.mark.parametrize("fixture", ["reflected-copilot.md", "reflected-claude.md"])
def test_a_reflected_before_plan_shows_every_sign(fixture):
    text = (FIXTURES / fixture).read_text()
    assert _names(text) == sorted(NAMES)


def test_a_skeptical_plan_has_no_finding_and_a_blank_approved_by_is_not_one():
    text = (FIXTURES / "skeptical.md").read_text()
    assert "**Approved by:**\n" in text
    assert plan_check.check(text) == []


def test_the_template_example_blocks_show_no_finding_once_an_intent_is_named():
    """T49: the template's own placeholders are enough to pass the checker, except the intent a person must name."""
    template = HERE.parent.parent / "bundles" / "base" / "templates" / "PHASE_TEST_PLAN_TEMPLATE.md"
    text = template.read_text()
    assert _names(text) == ["no-intent-cited"]
    assert plan_check.check(text.replace("`INT-<n>`", "`INT-99`")) == []


def test_findings_are_name_and_detail_pairs():
    findings = plan_check.check((FIXTURES / "reflected-claude.md").read_text())
    for item in findings:
        name, detail = item
        assert name in NAMES and isinstance(detail, str) and detail


def test_no_intent_cited_when_the_section_has_no_intent_id():
    text = GOOD.replace("- `INT-99` Export a wiki (accepted). Seeds S1, S2.", "- an intent, not named")
    assert _names(text) == ["no-intent-cited"]


def test_no_intent_cited_when_the_id_is_only_outside_the_section():
    text = GOOD.replace("- `INT-99` Export a wiki (accepted). Seeds S1, S2.", "- none").replace(
        "A1 covers S2.", "A1 covers INT-99 S2.")
    assert _names(text) == ["no-intent-cited"]


def test_no_intent_cited_when_the_section_is_missing():
    text = GOOD.replace("## Source intents", "## Something else")
    assert _names(text) == ["no-intent-cited"]


def test_all_automated_cases_pre_ticked():
    text = GOOD.replace("**Todo:** [ ]", "**Todo:** [x]")
    assert _names(text) == ["all-automated-cases-pre-ticked"]


def test_one_open_automated_case_is_enough_to_clear_the_pre_ticked_sign():
    extra = "\n### A2 — Another\n**Derived from:** INT-99 S1\n**Existing or new:** new\n**Todo:** [x]\n"
    text = GOOD.replace("\n## Questions for the human", extra + "\n## Questions for the human")
    assert _names(text) == []


def test_case_without_source_when_derived_from_is_empty():
    text = GOOD.replace("**Derived from:** INT-99 S2", "**Derived from:**")
    assert _names(text) == ["case-without-source"]


def test_case_without_source_when_the_line_is_missing():
    text = GOOD.replace("**Derived from:** INT-99 S2\n", "")
    assert _names(text) == ["case-without-source"]


def test_a_manual_case_may_say_unconfirmed_instead_of_a_source():
    text = GOOD.replace("**Derived from:** Unconfirmed: owner to confirm", "**Derived from:**\n**Notes:** Unconfirmed: owner to confirm")
    assert _names(text) == []


def test_an_automated_case_may_not_say_unconfirmed_instead_of_a_source():
    text = GOOD.replace("**Derived from:** INT-99 S2", "**Derived from:**\nUnconfirmed: owner to confirm")
    assert _names(text) == ["case-without-source"]


def test_no_gap_statement_when_the_section_holds_nothing():
    text = GOOD.replace("- A1 covers S2.", "- nothing")
    assert _names(text) == ["no-gap-statement"]


def test_no_gap_statement_when_the_section_is_missing():
    text = GOOD.replace("## Gaps found", "## Elsewhere")
    assert _names(text) == ["no-gap-statement"]


def test_no_gap_found_without_evidence_is_still_no_gap_statement():
    text = GOOD.replace("- A1 covers S2.", "no gap found")
    assert _names(text) == ["no-gap-statement"]


def test_no_gap_found_with_evidence_is_a_gap_statement():
    text = GOOD.replace("- A1 covers S2.", "no gap found\nRead the intent and tests/test_export.py; S1 and S2 are adequate.")
    assert _names(text) == []


def test_no_questions_section_when_the_heading_is_missing():
    text = GOOD.replace("## Questions for the human", "## Notes")
    assert _names(text) == ["no-questions-section"]


def test_no_questions_section_when_it_holds_no_question_and_no_reason():
    text = GOOD.replace("### Q1 — Which pages may a denied caller see?\n**Blocking:** yes\n**Answer:**\n", "none\n")
    assert _names(text) == ["no-questions-section"]


def test_a_stated_reason_stands_for_a_question():
    text = GOOD.replace("### Q1 — Which pages may a denied caller see?\n**Blocking:** yes\n**Answer:**\n",
                        "No questions because every expected result has a source.\n")
    assert _names(text) == []


def test_template_comments_do_not_count():
    text = GOOD.replace("## Questions for the human", "<!-- Q1 — example -->\n## Questions for the human").replace(
        "### Q1 — Which pages may a denied caller see?\n**Blocking:** yes\n**Answer:**\n", "<!-- Q2 — example -->\n")
    assert _names(text) == ["no-questions-section"]


def test_the_command_line_exits_1_with_findings_and_0_without():
    script = str(HERE / "plan_check.py")
    bad = subprocess.run([sys.executable, script, str(FIXTURES / "reflected-claude.md")],
                         stdout=subprocess.PIPE, universal_newlines=True)
    assert bad.returncode == 1
    for name in NAMES:
        assert name in bad.stdout
    ok = subprocess.run([sys.executable, script, str(FIXTURES / "skeptical.md")],
                        stdout=subprocess.PIPE, universal_newlines=True)
    assert ok.returncode == 0 and ok.stdout == ""
