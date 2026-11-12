# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Tests for scripts/phase_status.py: the read-only phase status."""
import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "phase_status.py"
_spec = importlib.util.spec_from_file_location("phase_status_under_test", SCRIPT)
ps = importlib.util.module_from_spec(_spec)
sys.modules["phase_status_under_test"] = ps
_spec.loader.exec_module(ps)

PLAN = """# PHASE_7_PLAN.md

**Approved by:** Pat Example on 2026-01-02

## Tasks

<!-- **Todo:** [ ] a hint inside a comment is not a task -->

### Task 1 - done
**Todo:** [x]

### Task 2 - not done
**Todo:** [ ]

### Task 3 - stuck
**Todo:** [~] blocked: needs an answer

## Completion checklist

- [x] All tasks marked
- [ ] Summary note added

## Review amendment (round 1)

**Amendment approved by:**
"""

TEST_PLAN = """# PHASE_7_TEST_PLAN.md

**Approved by:** <!-- left blank until a human approves -->

### A1 - a case
**Todo:** [ ]
"""

REVIEW = """# REVIEW_PLAN_7.md

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | 2026-01-01 | `aaa` | First review |
| 2 | 2026-01-02 | `bbb` | Re-review |

## Findings

**F1 (Important) - one**
- **State:** repaired (rev 2)

**F2 (Nit) - two**
- **State:** open

**F10 (Nit) - ten**
- **State:** open

**F3 (Nit) - no state line yet**
"""


def make_repo(tmp_path, plan=PLAN, test_plan=TEST_PLAN, review=REVIEW):
    plans = tmp_path / "docs" / "plans"
    plans.mkdir(parents=True)
    if plan is not None:
        (plans / "PHASE_7_PLAN.md").write_text(plan, encoding="utf-8")
    if test_plan is not None:
        (plans / "PHASE_7_TEST_PLAN.md").write_text(test_plan, encoding="utf-8")
    if review is not None:
        (plans / "REVIEW_PLAN_7.md").write_text(review, encoding="utf-8")
    return tmp_path


def status(tmp_path, capsys, number="7"):
    code = ps.main([number, "--root", str(tmp_path)])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def snapshot(root):
    return {str(p.relative_to(root)): (p.read_bytes(), p.stat().st_mtime_ns) for p in sorted(root.rglob("*")) if p.is_file()}


def test_lists_open_blocked_checklist_review_and_approvals(tmp_path, capsys):
    make_repo(tmp_path)
    code, out, err = status(tmp_path, capsys)
    assert code == 0 and err == ""
    assert "Unticked tasks ([ ]): 2" in out  # Task 2 and the test plan case A1; the commented hint is not a task
    assert "Task 2 - not done" in out and "A1 - a case" in out
    assert "Blocked tasks ([~]): 1" in out and "Task 3 - stuck" in out
    assert "Task 1 - done" not in out
    assert "Unticked Completion checklist lines: 1" in out and "Summary note added" in out
    assert "latest revision 2, open findings: 2 (F2, F10)" in out
    assert "findings with no State line: F3" in out
    assert "Approved by: filled" in out
    assert "PHASE_7_PLAN.md:25 Amendment approved by: BLANK" in out
    assert "PHASE_7_TEST_PLAN.md:3 Approved by: BLANK" in out
    assert "Level: below mergeable" in out
    assert "cannot tell from files" in out


def test_line_numbers_point_at_the_marker_lines(tmp_path, capsys):
    make_repo(tmp_path)
    _, out, _ = status(tmp_path, capsys)
    lines = PLAN.split("\n")
    for needle, marker in (("Task 2 - not done", "**Todo:** [ ]"), ("Task 3 - stuck", "**Todo:** [~]")):
        number = next(i for i, line in enumerate(lines, 1) if line.startswith(marker))
        assert "docs/plans/PHASE_7_PLAN.md:%d %s" % (number, needle) in out


def test_same_output_twice_and_nothing_changed(tmp_path, capsys):
    make_repo(tmp_path)
    before = snapshot(tmp_path)
    first = status(tmp_path, capsys)
    second = status(tmp_path, capsys)
    assert first == second
    assert snapshot(tmp_path) == before  # contents and mtimes; no file added or removed


def test_script_runs_as_a_program_and_writes_nothing(tmp_path):
    make_repo(tmp_path)
    before = snapshot(tmp_path)
    runs = [subprocess.run([sys.executable, str(SCRIPT), "7", "--root", str(tmp_path)], capture_output=True, text=True)
            for _ in range(2)]
    assert [r.returncode for r in runs] == [0, 0]
    assert runs[0].stdout == runs[1].stdout and "Phase 7 status" in runs[0].stdout
    assert snapshot(tmp_path) == before


def test_default_root_is_the_current_directory(tmp_path):
    make_repo(tmp_path)
    p = subprocess.run([sys.executable, str(SCRIPT), "7"], capture_output=True, text=True, cwd=tmp_path)
    assert p.returncode == 0 and "Unticked tasks ([ ]): 2" in p.stdout


@pytest.mark.parametrize("value", ["Pat Example on 2026-01-02", "Pat", "yes <!-- a note -->"])
def test_a_filled_approval_is_never_reported_blank(tmp_path, capsys, value):
    make_repo(tmp_path, plan="**Approved by:** %s\n\n**Amendment approved by:** %s\n" % (value, value),
              test_plan=None, review=None)
    code, out, _ = status(tmp_path, capsys)
    assert code == 0 and "BLANK" not in out
    assert out.count(": filled") == 2


@pytest.mark.parametrize("value", ["", "   ", "<!-- left blank -->", "<name and date>"])
def test_a_blank_approval_is_reported_blank(tmp_path, capsys, value):
    make_repo(tmp_path, plan="**Approved by:** %s\n" % value, test_plan=None, review=None)
    code, out, _ = status(tmp_path, capsys)
    assert code == 0 and "Approved by: BLANK" in out and "Level: below mergeable" in out


def test_a_clean_phase_reaches_only_the_level_the_files_support(tmp_path, capsys):
    clean = "**Approved by:** Pat on 2026-01-02\n\n### Task 1 - x\n**Todo:** [x]\n\n## Completion checklist\n\n- [x] done\n"
    make_repo(tmp_path, plan=clean, test_plan=None, review=None)
    code, out, _ = status(tmp_path, capsys)
    assert code == 0 and "Level: the files support mergeable" in out
    assert "CI of the exact commit and the human tick: cannot tell from files" in out
    assert "releasable and done: cannot tell from files" in out
    assert "REVIEW_PLAN_7.md not present" in out


def test_missing_plan_exits_2_with_a_plain_message(tmp_path, capsys):
    make_repo(tmp_path, plan=None)
    code, out, err = status(tmp_path, capsys)
    assert code == 2 and out == ""
    assert err.strip() == "phase_status: docs/plans/PHASE_7_PLAN.md not found under %s" % tmp_path
    assert "Traceback" not in err


@pytest.mark.parametrize("argv", [[], ["x"], ["1", "2"], ["-3"], ["7", "--root"]])
def test_bad_arguments_exit_2_without_a_traceback(capsys, argv):
    assert ps.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "Traceback" not in captured.err and captured.err.strip()


def _calls(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            yield node


def test_no_call_in_the_script_writes_or_changes_a_file():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    banned_attrs = {"write_text", "write_bytes", "write", "writelines", "mkdir", "makedirs", "unlink", "remove", "rmdir",
                    "rename", "replace", "touch", "chmod", "symlink_to", "hardlink_to", "truncate", "copy", "copyfile",
                    "move", "rmtree", "open"}
    for call in _calls(tree):
        name = call.func.attr if isinstance(call.func, ast.Attribute) else getattr(call.func, "id", "")
        assert name != "open", "the script must read with Path.read_text, not open()"
        assert name not in banned_attrs, "call to %s() could write or change a file" % name
        if name == "print":  # printing to a file object is a write too
            assert all(k.arg != "file" or ast.unparse(k.value) == "sys.stderr" for k in call.keywords)


def test_the_script_imports_only_the_standard_library():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location("build_for_phase_status", ROOT / "tools" / "build.py")
        build = importlib.util.module_from_spec(spec)
        sys.modules["build_for_phase_status"] = build
        spec.loader.exec_module(build)
    finally:
        sys.path.remove(str(ROOT / "tools"))
    assert build.lint_hook(SCRIPT, "scripts/phase_status.py") == []
