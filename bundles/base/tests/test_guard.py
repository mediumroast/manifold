# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Tests for hooks/guard.py: the tool-boundary guard (shell-write rule and per-agent write allowlist)."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("manifold_guard", ROOT / "hooks" / "guard.py")
guard = importlib.util.module_from_spec(_spec)
sys.modules["manifold_guard"] = guard
_spec.loader.exec_module(guard)


# ------------------------------------------------------------------ classify_bash

REFUSED = [
    # heredocs
    "cat > f <<'EOF'\nx\nEOF",
    "cat >> f <<EOF\nx\nEOF",
    "python - <<'EOF'\nprint(1)\nEOF",
    "python3 - <<EOF\nprint(1)\nEOF",
    # in-process writes
    "python3 -c \"open('f','w').write('x')\"",
    "python3 -c \"from pathlib import Path; Path('f').write_text('x')\"",
    # redirects into a file
    "printf x >> f",
    "echo x > f",
    "echo x >f",
    "echo x &> f",
    "ls >| f",
    # in-place editors and tee
    "sed -i s/a/b/ f",
    "sed -i.bak s/a/b/ f",
    "sed -ni s/a/b/p f",
    "sed --in-place s/a/b/ f",
    "tee f",
    "echo x | tee f",
    "echo x | tee -a f",
    "perl -pi -e s/a/b/ f",
    "perl -i.bak -pe s/a/b/ f",
    # /tmp and /private/tmp
    "echo x > /tmp/a",
    "echo x >> /private/tmp/a",
    "cp a /tmp/b",
    "touch /tmp/c",
    "mkdir /private/tmp/d",
    "mv a /tmp/e",
    "dd if=a of=/tmp/f",
    # the same after a separator, in a subshell, or inside bash -c
    "ls && echo x > f",
    "ls; echo x > f",
    "ls || echo x > f",
    "ls | sed -i s/a/b/ f",
    "ls\necho x > f",
    "(echo x > f)",
    "echo $(echo x > f)",
    "git status && cat > f <<'EOF'\nx\nEOF",
    "bash -c \"echo x > f\"",
    "sh -c 'echo x > f'",
    "bash -lc 'ls; sed -i s/a/b/ f'",
    "zsh -c \"cat > f <<EOF\nx\nEOF\"",
    "bash -c \"bash -c 'echo x > f'\"",
    "eval \"echo x > f\"",
    "env FOO=1 sed -i s/a/b/ f",
    "FOO=1 tee f",
    "/usr/bin/sed -i s/a/b/ f",
    "xargs sed -i s/a/b/",
    "sudo tee f",
]

ALLOWED = [
    "git diff > /dev/null",
    "pytest -q 2>&1",
    "pytest -q 2>&1 | tail -5",
    "ls >/dev/null 2>&1",
    "echo \"a > b\"",
    "echo 'a >> b'",
    "echo \"a << b\"",
    "grep -n '>' f",
    "grep -n \"=>\" f",
    "git commit -m \"x\"",
    "git commit -m \"fix > and <<EOF handling\"",
    "python3 .manifold/scratch/probe.py",
    "python3 -c \"print(1 > 0)\"",
    "python3 -c \"print(open('f').read())\"",
    "ls",
    "ls -la docs",
    "sed -n 's/a/b/p' f",
    "sed -e 's/a/b/' f",
    "sed s/a/b/ f",
    "perl -ne 'print' f",
    "perl -Mstrict -e 'print 1'",
    "tee",
    "echo x | tee /dev/null",
    "cp /tmp/a b",
    "ls /tmp",
    "cat /private/tmp/a",
    "bash -c \"echo x\"",
    "bash script.sh",
    "cat <<< word",
    "wc -l < f",
    "git log --format='%h > %s'",
    "cd server && ../.venv/bin/python -m pytest -q",
    "echo 2>&1",
    "ls 1>&2",
]


@pytest.mark.parametrize("command", REFUSED)
def test_classify_bash_refuses_shell_writes(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is False, command
    assert "Write" in message and "Edit" in message, message
    assert ".manifold/scratch/" in message, message


@pytest.mark.parametrize("command", ALLOWED)
def test_classify_bash_allows_read_only_and_quoted_use(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is True, (command, message)


def test_a_refusal_message_says_not_to_work_around_it():
    allowed, message = guard.classify_bash("echo x > f")
    assert not allowed
    assert "exception" in message and ".manifold/guard-allow.json" in message
    assert "replace_all" in message


def test_an_unparsable_command_is_judged_on_what_can_be_read():
    # an unclosed quote must not crash the guard; the write in it is still refused
    allowed, _ = guard.classify_bash("echo 'unclosed > f")
    assert allowed is True  # the redirect is inside the open quote
    allowed, _ = guard.classify_bash("echo x > f 'unclosed")
    assert allowed is False


ENTRY = {"pattern": "sed -i s/a/b/ notes.txt", "reason": "one-off rename", "granted_by": "Michael Hay", "date": "2026-11-06"}


def test_a_human_exception_allows_a_matching_command_only():
    assert guard.classify_bash("sed -i s/a/b/ notes.txt", allow=[ENTRY])[0] is True
    assert guard.classify_bash("sed -i s/a/b/ other.txt", allow=[ENTRY])[0] is False


@pytest.mark.parametrize("missing", ["pattern", "reason", "granted_by", "date"])
def test_an_exception_without_all_four_fields_is_ignored(missing):
    entry = {k: v for k, v in ENTRY.items() if k != missing}
    assert guard.classify_bash("sed -i s/a/b/ notes.txt", allow=[entry])[0] is False


def test_an_exception_with_an_empty_field_is_ignored():
    entry = dict(ENTRY, granted_by=" ")
    assert guard.classify_bash("sed -i s/a/b/ notes.txt", allow=[entry])[0] is False


def test_an_exception_does_not_cover_a_compound_command():
    # the pattern matches the whole command, so a second write appended to it is still judged
    allowed, _ = guard.classify_bash("sed -i s/a/b/ notes.txt && echo x > f", allow=[ENTRY])
    assert allowed is False


# ----------------------------------------------------------------- classify_write

REVIEW_FILES = ["docs/plans/REVIEW_PLAN_1.md", "docs/plans/REVIEW_PLAN_12.md"]


@pytest.mark.parametrize("path", REVIEW_FILES)
@pytest.mark.parametrize("exists", [True, False])
def test_reviewer_may_write_its_review_file(path, exists):
    assert guard.classify_write("reviewer", path, exists)[0] is True


@pytest.mark.parametrize("path", [
    "docs/plans/PHASE_1_PLAN.md",
    "docs/plans/REVIEW_PLAN_.md",
    "docs/plans/REVIEW_PLAN_x.md",
    "docs/plans/REVIEW_PLAN_1.md.bak",
    "docs/plans/sub/REVIEW_PLAN_1.md",
    "docs/plans/../../server/app.py",
    "docs/plans/REVIEW_PLAN_1.md/../../PHASE_1_PLAN.md",
    "REVIEW.md",
    "server/app.py",
    "bundles/base/tests/test_x.py",
])
def test_reviewer_may_write_nothing_else(path):
    allowed, message = guard.classify_write("reviewer", path, True)
    assert allowed is False
    assert "REVIEW_PLAN_" in message


@pytest.mark.parametrize("path,exists", [
    ("docs/agents/claude-desktop-failures.md", True),
    ("docs/agents/vscode-copilot-failures.md", False),
    ("intent/INT-24-something.md", False),
])
def test_coordinator_may_write_failure_records_and_new_drafts(path, exists):
    assert guard.classify_write("coordinator", path, exists)[0] is True


def test_coordinator_may_not_overwrite_an_existing_intent():
    allowed, message = guard.classify_write("coordinator", "intent/INT-20-agent-guardrails-hold.md", True)
    assert allowed is False
    assert "INT-" in message


@pytest.mark.parametrize("agent", [None, "", "planner", "coder", "bug-coder", "test-planner", "test-coder",
                                   "scenario-writer", "reviewer", "coordinator", "general-purpose"])
@pytest.mark.parametrize("path", [".manifold/guard-allow.json", ".manifold/hooks/guard.py", ".manifold/guard-log.jsonl",
                                  "./.manifold/guard-allow.json", "docs/../.manifold/guard-allow.json"])
def test_guard_files_are_refused_for_every_agent(agent, path):
    allowed, message = guard.classify_write(agent, path, True)
    assert allowed is False
    assert "human" in message


@pytest.mark.parametrize("agent", [None, "", "planner", "coder", "bug-coder", "test-planner", "test-coder",
                                   "scenario-writer", "general-purpose"])
@pytest.mark.parametrize("path", ["server/app.py", "docs/plans/PHASE_2_PLAN.md", "intent/INT-20-x.md",
                                  ".manifold/scratch/probe.py"])
def test_other_agents_are_unrestricted(agent, path):
    assert guard.classify_write(agent, path, True)[0] is True


# ------------------------------------------------------------------------- main

def run_hook(tmp_path, payload, client="claude", raw=None):
    env = {"PATH": "/usr/bin:/bin", "CLAUDE_PROJECT_DIR": str(tmp_path)}
    stdin = raw if raw is not None else json.dumps(payload)
    return subprocess.run([sys.executable, str(ROOT / "hooks" / "guard.py"), "--client", client],
                          input=stdin, capture_output=True, text=True, env=env, cwd=str(tmp_path))


def log_lines(tmp_path):
    path = tmp_path / ".manifold" / "guard-log.jsonl"
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []


def test_claude_refusal_exits_2_and_logs_the_refusal(tmp_path):
    command = "cat > notes.txt <<'EOF'\n" + "x" * 200 + "\nEOF"
    p = run_hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": command}, "agent_type": "coder"})
    assert p.returncode == 2
    assert "Write" in p.stderr and "Edit" in p.stderr
    (entry,) = log_lines(tmp_path)
    assert set(entry) == {"time", "rule", "tool", "agent_type", "command"}
    assert entry["tool"] == "Bash" and entry["agent_type"] == "coder" and entry["rule"] == "no-heredocs"
    assert entry["command"] == command[:80] and len(entry["command"]) == 80


def test_claude_allowed_call_exits_0_silently_and_logs_nothing(tmp_path):
    p = run_hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": "pytest -q 2>&1"}})
    assert (p.returncode, p.stdout, p.stderr) == (0, "", "")
    assert log_lines(tmp_path) == []


def test_claude_write_refusal_uses_the_agent_type_and_an_absolute_path(tmp_path):
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "server" / "app.py"), "content": "x"},
               "agent_type": "reviewer"}
    p = run_hook(tmp_path, payload)
    assert p.returncode == 2 and "REVIEW_PLAN_" in p.stderr
    ok = dict(payload, tool_input={"file_path": str(tmp_path / "docs/plans/REVIEW_PLAN_1.md"), "content": "x"})
    assert run_hook(tmp_path, ok).returncode == 0


def test_claude_edit_of_the_exception_file_is_refused_for_the_main_session(tmp_path):
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(tmp_path / ".manifold" / "guard-allow.json")}}
    p = run_hook(tmp_path, payload)
    assert p.returncode == 2
    assert log_lines(tmp_path)[0]["rule"] == "protected-file"


def test_a_coordinator_may_create_a_new_intent_but_not_replace_one(tmp_path):
    (tmp_path / "intent").mkdir()
    (tmp_path / "intent" / "INT-1-old.md").write_text("old")
    mk = lambda name: {"tool_name": "Write", "agent_type": "coordinator",
                       "tool_input": {"file_path": str(tmp_path / "intent" / name)}}
    assert run_hook(tmp_path, mk("INT-30-new.md")).returncode == 0
    assert run_hook(tmp_path, mk("INT-1-old.md")).returncode == 2


def test_the_exception_file_lets_a_human_allow_one_command(tmp_path):
    (tmp_path / ".manifold").mkdir()
    (tmp_path / ".manifold" / "guard-allow.json").write_text(json.dumps([ENTRY]))
    ok = {"tool_name": "Bash", "tool_input": {"command": "sed -i s/a/b/ notes.txt"}}
    other = {"tool_name": "Bash", "tool_input": {"command": "sed -i s/a/b/ other.txt"}}
    assert run_hook(tmp_path, ok).returncode == 0
    assert run_hook(tmp_path, other).returncode == 2


def test_a_broken_exception_file_grants_nothing_and_says_so(tmp_path):
    (tmp_path / ".manifold").mkdir()
    (tmp_path / ".manifold" / "guard-allow.json").write_text("{not json")
    p = run_hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": "echo x > f"}})
    assert p.returncode == 2
    assert "guard-allow.json" in p.stderr


def test_other_tools_are_not_the_guards_business(tmp_path):
    assert run_hook(tmp_path, {"tool_name": "Read", "tool_input": {"file_path": "x"}}).returncode == 0


def test_unreadable_input_fails_loudly_without_blocking(tmp_path):
    p = run_hook(tmp_path, None, raw="not json")
    assert p.returncode == 1
    assert "guard" in p.stderr


def test_copilot_refusal_prints_deny_json_on_stdout(tmp_path):
    payload = {"tool_name": "Bash", "tool_input": {"command": "echo x > f"}}
    p = run_hook(tmp_path, payload, client="copilot")
    assert p.returncode == 0
    out = json.loads(p.stdout)
    assert out["permissionDecision"] == "deny"
    assert "Write" in out["permissionDecisionReason"]
    assert len(log_lines(tmp_path)) == 1


def test_copilot_camel_case_fields_are_normalised(tmp_path):
    payload = {"toolName": "bash", "toolArgs": json.dumps({"command": "echo x > f"})}
    out = json.loads(run_hook(tmp_path, payload, client="copilot").stdout)
    assert out["permissionDecision"] == "deny"
    ok = {"toolName": "bash", "toolArgs": json.dumps({"command": "ls"})}
    assert run_hook(tmp_path, ok, client="copilot").stdout == ""
