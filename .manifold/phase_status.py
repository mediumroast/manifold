#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Print what is still open in one phase. Read-only, standard library only.

    python3 .manifold/phase_status.py <N> [--root <repository>]

Reads docs/plans/PHASE_<N>_PLAN.md (required), PHASE_<N>_TEST_PLAN.md and
REVIEW_PLAN_<N>.md (both optional) under the root (default: the current
directory). It opens files for reading only and writes nothing. The output is
sorted and is the same on every run over the same files.

Exit codes: 0 printed, 2 bad argument or missing plan.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

APPROVAL_RE = re.compile(r"^\*\*(Amendment approved by|Approved by):\*\*(.*)$")
TODO_RE = re.compile(r"^\s*\*\*Todo:\*\*\s*\[( |~)\](.*)$")
TASK_RE = re.compile(r"^###\s+(Task\s+\S+.*|A\d+.*|M\d+.*)$")
CHECK_RE = re.compile(r"^\s*-\s+\[( |~)\]\s*(.*)$")
FINDING_RE = re.compile(r"^\*\*(F\d+)\b")
STATE_RE = re.compile(r"^-\s+\*\*State:\*\*\s*(.*)$")
REVISION_RE = re.compile(r"^\|\s*(\d+)\s*\|")
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def blank_comments(text: str) -> str:
    """Replace HTML comments by blank lines, so line numbers stay true and template hints are not read as content."""
    return COMMENT_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def read_lines(path: Path):
    return blank_comments(path.read_text(encoding="utf-8")).split("\n")


def is_blank_approval(value: str) -> bool:
    value = value.strip()
    return not value or (value.startswith("<") and value.endswith(">"))


def approvals(lines, rel):
    """One (line, label, filled) row per approval line. A filled line is never reported blank."""
    rows = []
    for number, line in enumerate(lines, 1):
        m = APPROVAL_RE.match(line)
        if m:
            rows.append((number, m.group(1), not is_blank_approval(m.group(2))))
    return rows


def open_tasks(lines):
    """(line, marker, title) for each task whose Todo is [ ] or [~]."""
    title, rows = "(before the first task)", []
    for number, line in enumerate(lines, 1):
        m = TASK_RE.match(line)
        if m:
            title = m.group(1).strip()
            continue
        m = TODO_RE.match(line)
        if m and m.group(1) in (" ", "~"):
            rows.append((number, "[ ]" if m.group(1) == " " else "[~]", title))
    return rows


def checklist_open(lines):
    """Unticked lines of the Completion checklist."""
    rows, inside = [], False
    for number, line in enumerate(lines, 1):
        if line.startswith("## "):
            inside = line.strip() == "## Completion checklist"
            continue
        if inside:
            m = CHECK_RE.match(line)
            if m and m.group(1) == " ":
                rows.append((number, m.group(2).strip()))
    return rows


def review_state(lines):
    """(latest revision, sorted open finding ids, sorted finding ids with no State line)."""
    revision, current, states = 0, None, {}
    in_log = False
    for line in lines:
        if line.startswith("## "):
            in_log = line.strip() == "## Revision log"
            current = None
            continue
        if in_log:
            m = REVISION_RE.match(line)
            if m:
                revision = max(revision, int(m.group(1)))
        m = FINDING_RE.match(line)
        if m:
            current = m.group(1)
            states.setdefault(current, None)
            continue
        m = STATE_RE.match(line)
        if m and current is not None and states.get(current) is None:
            states[current] = m.group(1).strip().lower()
    key = lambda fid: int(fid[1:])
    open_ids = sorted((f for f, s in states.items() if s is not None and s.startswith("open")), key=key)
    unknown = sorted((f for f, s in states.items() if s is None), key=key)
    return revision, open_ids, unknown


def report(number: int, root: Path):
    """Return (lines of output, error message or None)."""
    plan_rel = "docs/plans/PHASE_%d_PLAN.md" % number
    test_rel = "docs/plans/PHASE_%d_TEST_PLAN.md" % number
    review_rel = "docs/plans/REVIEW_PLAN_%d.md" % number
    plan_path = root / plan_rel
    if not plan_path.is_file():
        return [], "phase_status: %s not found under %s" % (plan_rel, root)
    out = ["Phase %d status" % number, ""]
    reasons = []

    plan = read_lines(plan_path)
    test_path, review_path = root / test_rel, root / review_rel
    test = read_lines(test_path) if test_path.is_file() else None
    review = read_lines(review_path) if review_path.is_file() else None
    out.append("Files: %s; %s; %s" % (
        plan_rel,
        test_rel if test is not None else "%s (not present)" % test_rel,
        review_rel if review is not None else "%s (not present)" % review_rel))
    out.append("")

    out.append("Approvals")
    rows = [(plan_rel, r) for r in approvals(plan, plan_rel)]
    if test is not None:
        rows += [(test_rel, r) for r in approvals(test, test_rel)]
    for rel, (line, label, filled) in sorted(rows, key=lambda x: (x[0], x[1][0])):
        out.append("  %s:%d %s: %s" % (rel, line, label, "filled" if filled else "BLANK"))
        if not filled:
            reasons.append("%s is blank (%s:%d)" % (label, rel, line))
    if not rows:
        out.append("  no approval line found")
    out.append("")

    sources = [(plan_rel, plan)] + ([(test_rel, test)] if test is not None else [])
    unticked, blocked = [], []
    for rel, lines in sources:
        for line, marker, title in open_tasks(lines):
            (unticked if marker == "[ ]" else blocked).append((rel, line, title))
    out.append("Unticked tasks ([ ]): %d" % len(unticked))
    out += ["  %s:%d %s" % row for row in sorted(unticked)]
    out.append("Blocked tasks ([~]): %d" % len(blocked))
    out += ["  %s:%d %s" % row for row in sorted(blocked)]
    out.append("")
    if unticked:
        reasons.append("%d unticked task(s)" % len(unticked))
    if blocked:
        reasons.append("%d blocked task(s)" % len(blocked))

    checks = []
    for rel, lines in sources:
        checks += [(rel, line, text) for line, text in checklist_open(lines)]
    out.append("Unticked Completion checklist lines: %d" % len(checks))
    out += ["  %s:%d %s" % row for row in sorted(checks)]
    out.append("")
    if checks:
        reasons.append("%d unticked Completion checklist line(s)" % len(checks))

    if review is None:
        out.append("Review: %s not present" % review_rel)
    else:
        revision, open_ids, unknown = review_state(review)
        out.append("Review: latest revision %d, open findings: %d%s" % (
            revision, len(open_ids), " (%s)" % ", ".join(open_ids) if open_ids else ""))
        if unknown:
            out.append("  findings with no State line: %s" % ", ".join(unknown))
        out.append("  A decision to defer or reject a finding is recorded in the pull request, not in this file.")
    out.append("")

    if reasons:
        out.append("Level: below mergeable (%s)" % "; ".join(reasons))
    else:
        out.append("Level: the files support mergeable")
    out.append("  CI of the exact commit and the human tick: cannot tell from files (they live in the pull request)")
    out.append("  releasable and done: cannot tell from files (the merge, the version and the closure are not in them)")
    return out, None


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path.cwd()
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args):
            print("phase_status: --root needs a folder", file=sys.stderr)
            return 2
        root = Path(args[i + 1])
        del args[i:i + 2]
    if len(args) != 1 or not re.fullmatch(r"[0-9]+", args[0]):
        print("usage: phase_status.py <phase number> [--root <repository>]", file=sys.stderr)
        return 2
    lines, error = report(int(args[0]), root)
    if error:
        print(error, file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
