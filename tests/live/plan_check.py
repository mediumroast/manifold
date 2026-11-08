#!/usr/bin/env python3
"""Check a test plan for the signs of a plan that only reflects the existing tests (INT-25, plan T46).

Usage: python3 tests/live/plan_check.py <test plan file>
Prints one line per finding ("name: detail") and exits 1 when there is any; prints nothing and exits 0 otherwise.

Standard library only; syntax valid on Python 3.8 (the declared minimum).

The findings (the signs of INT-25 outcome 6 and S1, plus the per-case source of S2):
  no-intent-cited                 no INT-<n> inside the "## Source intents" section
  all-automated-cases-pre-ticked  at least one "### A<n>" case and every one has "**Todo:** [x]"
  case-without-source             an A<n> or M<n> case with an empty or missing "**Derived from:**"
                                  (a manual case that says "Unconfirmed: owner to confirm" is allowed)
  no-gap-statement                "## Gaps found" holds no case id and no "no gap found" with evidence below it
  no-questions-section            no "## Questions for the human" with a Q<n> entry or a "No questions because" line

A blank "**Approved by:**" is not a finding: it is the correct state of a new plan.
HTML comments (the template's own) are ignored.
"""
import re
import sys

COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
H2_RE = re.compile(r"^## +(.*?)\s*$", re.M)
CASE_RE = re.compile(r"^### +([AM])(\d+)\b.*$", re.M)
ANY_HEADING_RE = re.compile(r"^#{1,3} ", re.M)
DERIVED_RE = re.compile(r"^\*\*Derived from:\*\*(.*)$", re.M)
TODO_RE = re.compile(r"^\*\*Todo:\*\*\s*(\[.\])", re.M)
CASE_ID_RE = re.compile(r"\b[AM]\d+\b")
QUESTION_RE = re.compile(r"^\W*Q\d+\b", re.M)
NO_QUESTIONS_RE = re.compile(r"^\W*No questions because\b", re.M | re.I)
INTENT_RE = re.compile(r"\bINT-\d+\b")
UNCONFIRMED = "unconfirmed: owner to confirm"


def _sections(text):
    """Map the lower-cased title of each level-2 section to its body."""
    found = {}
    matches = list(H2_RE.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        found.setdefault(m.group(1).strip().lower(), text[m.end():end])
    return found


def _cases(text):
    """Return (letter, number, block) for each "### A<n>" or "### M<n>" case."""
    cases = []
    matches = list(CASE_RE.finditer(text))
    for m in matches:
        following = ANY_HEADING_RE.search(text, m.end())
        end = following.start() if following else len(text)
        cases.append((m.group(1), m.group(2), text[m.start():end]))
    return cases


def check(text):
    """Return a list of (name, detail) findings; empty when the plan shows none of the signs."""
    text = COMMENT_RE.sub("", text)
    sections = _sections(text)
    findings = []

    intents = sections.get("source intents")
    if intents is None:
        findings.append(("no-intent-cited", "no '## Source intents' section, and so no intent cited"))
    elif not INTENT_RE.search(intents):
        findings.append(("no-intent-cited", "the '## Source intents' section names no INT-<n>"))

    cases = _cases(text)
    automated = [c for c in cases if c[0] == "A"]
    if automated:
        open_cases = [c for c in automated if TODO_RE.search(c[2]) is None or TODO_RE.search(c[2]).group(1) != "[x]"]
        if not open_cases:
            findings.append(("all-automated-cases-pre-ticked",
                             "all %d automated cases are already ticked [x]" % len(automated)))

    unsourced = []
    for letter, number, block in cases:
        derived = DERIVED_RE.search(block)
        has_source = derived is not None and derived.group(1).strip() != ""
        if has_source:
            continue
        if letter == "M" and UNCONFIRMED in block.lower():
            continue
        unsourced.append("%s%s" % (letter, number))
    if unsourced:
        findings.append(("case-without-source", "no 'Derived from' source: %s" % ", ".join(unsourced)))

    gaps = sections.get("gaps found")
    if gaps is None:
        findings.append(("no-gap-statement", "no '## Gaps found' section"))
    else:
        lines = [line for line in gaps.splitlines()]
        has_case = CASE_ID_RE.search(gaps) is not None
        has_evidence = False
        for i, line in enumerate(lines):
            if "no gap found" in line.lower():
                has_evidence = any(rest.strip() for rest in lines[i + 1:])
                break
        if not has_case and not has_evidence:
            findings.append(("no-gap-statement",
                             "'## Gaps found' holds no case id and no 'no gap found' with evidence below it"))

    questions = sections.get("questions for the human")
    if questions is None:
        findings.append(("no-questions-section", "no '## Questions for the human' section"))
    elif QUESTION_RE.search(questions) is None and NO_QUESTIONS_RE.search(questions) is None:
        findings.append(("no-questions-section",
                         "'## Questions for the human' holds no Q<n> entry and no 'No questions because' line"))

    return findings


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: plan_check.py <test plan file>\n")
        return 2
    try:
        with open(argv[1], encoding="utf-8") as handle:
            text = handle.read()
    except OSError as error:
        sys.stderr.write("plan_check: cannot read %s: %s\n" % (argv[1], error))
        return 2
    findings = check(text)
    for name, detail in findings:
        print("%s: %s" % (name, detail))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
