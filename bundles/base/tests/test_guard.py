# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Tests for hooks/guard.py: the tool-boundary guard (shell-write rule and per-agent write allowlist)."""
import datetime
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("manifold_guard", ROOT / "hooks" / "guard.py")
guard = importlib.util.module_from_spec(_spec)
sys.modules["manifold_guard"] = guard
_spec.loader.exec_module(guard)

_bspec = importlib.util.spec_from_file_location("manifold_build_for_guard", ROOT / "tools" / "build.py")
build = importlib.util.module_from_spec(_bspec)
sys.modules["manifold_build_for_guard"] = build
_bspec.loader.exec_module(build)


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


def test_unreadable_input_fails_loudly_and_blocks(tmp_path):
    # CP2a T14a: replaces test_unreadable_input_fails_loudly_without_blocking, which pinned exit 1.
    # Exit 1 is a non-blocking error in Claude Code (a silent allow); the owner's decision (b) of 2026-11-07
    # reverses it: input the guard cannot read blocks (exit 2) with a message.
    p = run_hook(tmp_path, None, raw="not json")
    assert p.returncode == 2
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


# =====================================================================================
# CP2a (T14a): failing-first cases for the findings F1 to F5 and F9 of the CP2 review.
# Each case is a failure scenario from the reviewer's probes (docs/plans/PHASE_2_PLAN.md, CP2a).
# =====================================================================================

# ---- F1: shell commands that write the protected files (T14d). Message: protected_message.

REFUSED_PROTECTED = [
    "cp a .manifold/guard-allow.json",
    "mv a .manifold/hooks/guard.py",
    "touch .manifold/guard-log.jsonl",
    "dd if=a of=.manifold/guard-allow.json",
    "truncate -s 0 .manifold/guard-log.jsonl",
    "rm .manifold/guard-allow.json",
    "rm -rf .claude/agents",
    "mv .claude/agents /x",
    "cp a .claude/agents/coder.md",
    "rm .claude/settings.json",
    "cp a .github/hooks/manifold-guard.json",
    "cd .manifold && rm guard-allow.json",
    "rm .manifold/*.json",
    "git checkout -- .claude/settings.json",
    "find .claude -delete",
]

# ---- F2: trivial variations of the shell rule (T14e). Message: shell_message.

REFUSED_VARIATIONS = [
    "python3 -Ic \"open('f','w')\"",
    "echo \"open('f','w')\" | python3",
    "python3 - <<< \"open('f','w')\"",
    "bash <<< 'echo x > f'",
    "cat s | bash",
    "python3 -c \"import shutil; shutil.copy('a','b')\"",
    "python3 -c \"import os; os.system('x')\"",
    "python3 -c \"import os; os.rename('a','b')\"",
    "python3 -c \"from pathlib import Path; Path('f').touch()\"",
    "python3 -c \"import subprocess; subprocess.run('x', shell=True)\"",
    "python3 -c \"import zipfile; zipfile.ZipFile('a').extractall()\"",
    "python3 -c \"import sqlite3; sqlite3.connect('f')\"",
    "node -e \"require('fs').writeFile('f','x',()=>0)\"",
    "node --eval \"fs.writeFileSync('f','x')\"",
    "node -p \"fs.writeFileSync('f','x')\"",
    "ruby -e \"File.write('f','x')\"",
    "perl -e 'open(F,\">f\")'",
    "php -r \"file_put_contents('f','x');\"",
    "deno eval \"Deno.writeTextFileSync('f','x')\"",
    "uv run python -c \"open('f','w')\"",
    "awk -i inplace '{print}' f",
    "awk '{print > \"f\"}' g",
    "ed f",
    "patch < p",
    "git apply p",
    "sponge f",
    "find . -exec sed -i s/a/b/ {} +",
    "env -u FOO sed -i s/a/b/ f",
    "env -C /tmp sed -i s/a/b/ f",
    "sudo -u root tee f",
    "nice -n 5 tee f",
    "cp -t /tmp a",
    "mv -t /private/tmp a",
    "cp --target-directory=/tmp a",
    "[ $x > 1 ]",  # F5, rejected as a false positive: in sh and bash this is a real redirect that creates a file named 1
]

ALLOWED_AFTER_REPAIR = [
    # read-only use of the protected files and directories (INT-20: no regression)
    "cat .manifold/guard-log.jsonl",
    "tail -n 5 .manifold/guard-log.jsonl",
    "grep x .claude/agents/coder.md",
    "ls .claude/agents",
    "diff -u a .claude/agents/coder.md",
    "git diff -- .claude/agents",
    "git log -- .claude/settings.json",
    # read-only forms of commands that otherwise write
    "python3 -m json.tool < a",
    "git apply --check p",
    "find . -name '*.py'",
    "env -u FOO ls",
    "nice -n 5 ls",
    "cp -t dir a",
    # arithmetic and tests are not redirects (F5)
    "[[ a > b ]]",
    "echo $((1>0))",
    "(( 2 > 1 ))",
    "if [[ $x > 1 ]]; then echo y; fi",
    # Stated residual gap (T14f): a script that writes when it is run from a file is not inspected.
    # `bash s.sh` and `bash < s.sh` are the scratch-script route that T8 prescribes, so they stay allowed.
    "bash s.sh",
    "bash < s.sh",
]


@pytest.mark.parametrize("command", REFUSED_PROTECTED)
def test_f1_a_shell_command_on_a_protected_file_is_refused(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is False, command
    assert "human" in message, message


@pytest.mark.parametrize("command", REFUSED_VARIATIONS)
def test_f2_trivial_variations_of_the_shell_rule_are_refused(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is False, command
    assert "Write" in message and "Edit" in message and ".manifold/scratch/" in message, message


@pytest.mark.parametrize("command", ALLOWED_AFTER_REPAIR)
def test_f1_f5_read_only_use_and_arithmetic_stay_allowed(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is True, (command, message)


def test_a_pipe_into_an_interpreter_says_to_write_the_program_to_the_scratch_folder():
    allowed, message = guard.classify_bash("cat s | bash")
    assert allowed is False
    assert "pipe" in message and ".manifold/scratch/" in message


def test_a_path_exception_never_lifts_a_shell_command():
    entry = path_entry(r"\.claude/agents/coder\.md", TODAY.isoformat())
    assert guard.classify_bash("cp a .claude/agents/coder.md", allow=[entry])[0] is False
    # only a command entry excepts a shell command on a definition, as before
    command_entry = dict(ENTRY, pattern="cp a .claude/agents/coder.md")
    assert guard.classify_bash("cp a .claude/agents/coder.md", allow=[command_entry])[0] is True


# ---- F3: protected paths, identity, expiry for path exceptions (T14c)

TODAY = datetime.datetime.now(datetime.timezone.utc).date()
YESTERDAY = TODAY - datetime.timedelta(days=1)
TOMORROW = TODAY + datetime.timedelta(days=1)


def path_entry(pattern, expires, **extra):
    entry = {"scope": "path", "pattern": pattern, "reason": "Phase 2 T38", "granted_by": "Michael Hay",
             "date": "2026-11-07"}
    if expires is not None:
        entry["expires"] = expires
    entry.update(extra)
    return entry


AGENTS_ALL = [None, "", "planner", "coder", "bug-coder", "test-planner", "test-coder", "scenario-writer",
              "reviewer", "coordinator", "general-purpose"]
MANIFOLD_FILES = [".manifold/guard-allow.json", ".manifold/guard-log.jsonl", ".manifold/hooks/guard.py"]
DEFINITIONS = [".claude/agents/coder.md", ".claude/agents/some-new-agent.md", ".claude/settings.json",
               ".claude/settings.local.json", ".github/agents/coder.agent.md", ".github/hooks/manifold-guard.json"]
SKILLS = [".claude/skills/%s/SKILL.md" % name for name in sorted(build.SKILL_NAMES.values())]


def variants(path):
    return [path, "./" + path, "docs/../" + path, path.upper(), "./" + path.upper()]


@pytest.mark.parametrize("agent", AGENTS_ALL)
@pytest.mark.parametrize("path", [v for p in MANIFOLD_FILES + DEFINITIONS + SKILLS for v in variants(p)])
def test_f3_every_protected_path_is_refused_for_every_agent_including_no_identity(agent, path):
    allowed, message = guard.classify_write(agent, path, True)
    assert allowed is False, (agent, path)
    assert "human" in message, message


@pytest.mark.parametrize("path", DEFINITIONS + SKILLS)
def test_f3_the_message_for_a_definition_names_the_path_exception_route(path):
    allowed, message = guard.classify_write("coder", path, True)
    assert allowed is False
    assert "path exception" in message and ".manifold/guard-allow.json" in message
    assert "expires" in message and "Do not work around" in message


def test_f3_the_guards_skill_list_equals_the_builds_skill_names():
    # a new role must not be forgotten: the guard cannot import build.py, so this test compares the two lists
    assert set(guard.SKILL_DIRS) == set(build.SKILL_NAMES.values())


@pytest.mark.parametrize("agent", [a for a in AGENTS_ALL if a not in ("reviewer", "coordinator")])
@pytest.mark.parametrize("path", DEFINITIONS + SKILLS)
def test_f3_a_current_path_exception_allows_a_definition(agent, path):
    # a pattern is a regular expression that must match the whole normalised project-relative path
    exact = path_entry(path.replace(".", r"\."), TOMORROW.isoformat())
    assert guard.classify_write(agent, path, True, allow=[exact]) == (True, "")
    assert guard.classify_write(agent, path, True, allow=[path_entry(".*", TODAY.isoformat())]) == (True, "")


@pytest.mark.parametrize("agent", AGENTS_ALL)
@pytest.mark.parametrize("path", MANIFOLD_FILES)
def test_f3_no_exception_ever_allows_the_three_manifold_files(agent, path):
    for entry in (path_entry(".*", TODAY.isoformat()), path_entry(path.replace(".", r"\."), TOMORROW.isoformat()),
                  dict(ENTRY, pattern=".*")):
        assert guard.classify_write(agent, path, True, allow=[entry])[0] is False, (agent, path, entry)


def test_f3_a_path_exception_lasts_through_its_expiry_date_and_not_past_it():
    path = ".claude/agents/coder.md"
    assert guard.classify_write("coder", path, True, allow=[path_entry(r"\.claude/agents/coder\.md", TODAY.isoformat())])[0] is True
    allowed, message = guard.classify_write(
        "coder", path, True, allow=[path_entry(r"\.claude/agents/coder\.md", YESTERDAY.isoformat())])
    assert allowed is False
    assert "expired on %s" % YESTERDAY.isoformat() in message


@pytest.mark.parametrize("expires", [None, "2026-13-01", "soon", "", "2026-1-1", 20261107])
def test_f3_a_path_exception_without_a_valid_expiry_grants_nothing_and_says_so(expires):
    path = ".claude/agents/coder.md"
    allowed, message = guard.classify_write("coder", path, True, allow=[path_entry(r"\.claude/agents/coder\.md", expires)])
    assert allowed is False
    assert "no valid expires date" in message


def test_f3_a_path_exception_must_match_the_whole_path():
    entry = path_entry(r"\.claude/agents/coder", TODAY.isoformat())
    assert guard.classify_write("coder", ".claude/agents/coder.md", True, allow=[entry])[0] is False


def test_f3_a_command_entry_without_expires_keeps_working_unchanged():
    assert "expires" not in ENTRY and "scope" not in ENTRY
    assert guard.classify_bash("sed -i s/a/b/ notes.txt", allow=[ENTRY])[0] is True
    assert guard.classify_bash("sed -i s/a/b/ notes.txt", allow=[dict(ENTRY, scope="command")])[0] is True


def test_f3_a_command_entry_does_not_lift_a_write_to_a_definition():
    entry = dict(ENTRY, pattern=".*")
    assert guard.classify_write("coder", ".claude/agents/coder.md", True, allow=[entry])[0] is False


@pytest.mark.parametrize("path", [".claude/settings.json", ".claude/settings.local.json"])
def test_f3_settings_and_local_settings_are_protected_alike(path):
    assert guard.classify_write("coder", path, False)[0] is False
    assert guard.classify_write("coder", path, False, allow=[path_entry(".*", TODAY.isoformat())])[0] is True


@pytest.mark.parametrize("spelling", ["Reviewer", "reviewer ", "manifold:reviewer", "plugin/reviewer", " REVIEWER"])
def test_f3_a_reviewer_is_restricted_however_its_identity_is_spelled(spelling):
    assert guard.classify_write(spelling, "server/app.py", True)[0] is False
    assert guard.classify_write(spelling, "docs/plans/REVIEW_PLAN_1.md", True)[0] is True


@pytest.mark.parametrize("spelling", ["Coordinator", "coordinator ", "manifold:coordinator"])
def test_f3_a_coordinator_is_restricted_however_its_identity_is_spelled(spelling):
    assert guard.classify_write(spelling, "server/app.py", True)[0] is False
    assert guard.classify_write(spelling, "docs/agents/claude-desktop-failures.md", True)[0] is True


def test_f3_an_empty_identity_is_not_restricted_by_the_allowlist_but_by_the_protected_files():
    assert guard.classify_write("", "server/app.py", True)[0] is True
    assert guard.classify_write(None, "server/app.py", True)[0] is True
    assert guard.classify_write("", ".claude/agents/coder.md", True)[0] is False


def test_f3_an_unrelated_path_exception_does_not_lift_a_reviewer_refusal():
    unrelated = path_entry(r"\.claude/agents/coder\.md", TODAY.isoformat())
    assert guard.classify_write("reviewer", "server/app.py", True, allow=[unrelated])[0] is False
    assert guard.classify_write("reviewer", "docs/plans/REVIEW_PLAN_1.md", True, allow=[unrelated])[0] is True
    related = path_entry(r"server/app\.py", TODAY.isoformat())
    assert guard.classify_write("reviewer", "server/app.py", True, allow=[related])[0] is True


def test_f3_a_path_exception_lifts_a_coordinator_allowlist_refusal():
    entry = path_entry(r"intent/INT-1-old\.md", TODAY.isoformat())
    assert guard.classify_write("coordinator", "intent/INT-1-old.md", True)[0] is False
    assert guard.classify_write("coordinator", "intent/INT-1-old.md", True, allow=[entry])[0] is True


# ---- F3, F4, F9 through main (T14b, T14c)

def hook_env(tmp_path, project_dir=True):
    env = {"PATH": "/usr/bin:/bin"}
    if project_dir:
        env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    return env


def run_main(tmp_path, payload, client="claude", project_dir=True, cwd=None):
    return subprocess.run([sys.executable, str(ROOT / "hooks" / "guard.py"), "--client", client],
                          input=json.dumps(payload), capture_output=True, text=True,
                          env=hook_env(tmp_path, project_dir), cwd=str(cwd or tmp_path))


def test_f3_a_write_through_a_symlinked_directory_to_a_definition_is_refused(tmp_path):
    (tmp_path / ".claude" / "agents").mkdir(parents=True)
    (tmp_path / "docs").symlink_to(tmp_path / ".claude" / "agents", target_is_directory=True)
    for given in (str(tmp_path / "docs" / "x.md"), "docs/x.md"):
        p = run_main(tmp_path, {"tool_name": "Write", "tool_input": {"file_path": given}, "agent_type": "coder"})
        assert p.returncode == 2, given
        assert "human" in p.stderr
    assert log_lines(tmp_path)[-1]["rule"] == "protected-file"


def test_f3_a_write_through_a_symlinked_directory_to_a_manifold_file_is_refused(tmp_path):
    (tmp_path / ".manifold" / "hooks").mkdir(parents=True)
    (tmp_path / "link").symlink_to(tmp_path / ".manifold" / "hooks", target_is_directory=True)
    p = run_main(tmp_path, {"tool_name": "Edit", "tool_input": {"file_path": str(tmp_path / "link" / "guard.py")}})
    assert p.returncode == 2


def test_f3_without_a_project_dir_variable_the_input_cwd_decides_the_log_and_the_exception_file(tmp_path):
    project = tmp_path / "project"
    elsewhere = tmp_path / "elsewhere"
    (project / ".manifold").mkdir(parents=True)
    elsewhere.mkdir()
    refused = {"tool_name": "Bash", "tool_input": {"command": "echo x > f"}, "cwd": str(project)}
    p = run_main(project, refused, project_dir=False, cwd=elsewhere)
    assert p.returncode == 2
    assert len(log_lines(project)) == 1 and not (elsewhere / ".manifold").exists()
    (project / ".manifold" / "guard-allow.json").write_text(json.dumps([dict(ENTRY, pattern="echo x > f")]))
    assert run_main(project, refused, project_dir=False, cwd=elsewhere).returncode == 0


def test_f9_an_unwritable_log_still_refuses_and_warns(tmp_path):
    (tmp_path / ".manifold" / "guard-log.jsonl").mkdir(parents=True)  # a directory: appending to it fails
    p = run_main(tmp_path, {"tool_name": "Bash", "tool_input": {"command": "echo x > f"}})
    assert p.returncode == 2
    assert "Write" in p.stderr and "could not append" in p.stderr


def test_f9_a_refusal_and_an_allowed_exception_use_each_append_one_log_line(tmp_path):
    payload = {"tool_name": "Edit", "tool_input": {"file_path": str(tmp_path / ".claude" / "agents" / "coder.md")},
               "agent_type": "planner"}
    assert run_main(tmp_path, payload).returncode == 2
    (entry,) = log_lines(tmp_path)
    assert entry["rule"] == "protected-file"
    (tmp_path / ".manifold" / "guard-allow.json").write_text(
        json.dumps([path_entry(r"\.claude/agents/coder\.md", TODAY.isoformat())]))
    assert run_main(tmp_path, payload).returncode == 0
    lines = log_lines(tmp_path)
    assert len(lines) == 2 and lines[1]["rule"] == "exception-used"
    assert lines[1]["tool"] == "Edit" and lines[1]["agent_type"] == "planner"


def test_f9_a_command_exception_use_is_logged_too(tmp_path):
    (tmp_path / ".manifold").mkdir()
    (tmp_path / ".manifold" / "guard-allow.json").write_text(json.dumps([ENTRY]))
    ok = {"tool_name": "Bash", "tool_input": {"command": "sed -i s/a/b/ notes.txt"}}
    assert run_main(tmp_path, ok).returncode == 0
    (entry,) = log_lines(tmp_path)
    assert entry["rule"] == "exception-used"


def test_f9_an_expired_path_exception_refuses_through_main_and_the_message_says_when(tmp_path):
    (tmp_path / ".manifold").mkdir()
    (tmp_path / ".manifold" / "guard-allow.json").write_text(
        json.dumps([path_entry(r"\.claude/agents/coder\.md", YESTERDAY.isoformat())]))
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / ".claude" / "agents" / "coder.md")}}
    p = run_main(tmp_path, payload)
    assert p.returncode == 2
    assert "expired on %s" % YESTERDAY.isoformat() in p.stderr


def test_f9_a_reviewer_allowlist_refusal_can_be_excepted_through_main(tmp_path):
    (tmp_path / ".manifold").mkdir()
    (tmp_path / ".manifold" / "guard-allow.json").write_text(
        json.dumps([path_entry(r"server/app\.py", TODAY.isoformat())]))
    payload = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "server" / "app.py")}, "agent_type": "reviewer"}
    assert run_main(tmp_path, payload).returncode == 0


def _call_main_in_process(monkeypatch, tmp_path, client, payload=None, raw=None):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr(sys, "stdin", io.StringIO(raw if raw is not None else json.dumps(payload)))
    return guard.main(["--client", client])


def test_f4_a_guard_that_raises_blocks_with_exit_2_and_names_the_guard_and_the_exception(monkeypatch, tmp_path, capsys):
    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(guard, "classify_bash", boom)
    rc = _call_main_in_process(monkeypatch, tmp_path, "claude", {"tool_name": "Bash", "tool_input": {"command": "ls"}})
    err = capsys.readouterr().err
    assert rc == 2
    assert "Manifold guard failed" in err and "RuntimeError" in err and "boom" in err and "blocked" in err
    assert log_lines(tmp_path)[-1]["rule"] == "guard-error"


def test_f4_a_guard_that_raises_prints_the_deny_json_for_copilot(monkeypatch, tmp_path, capsys):
    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(guard, "classify_bash", boom)
    rc = _call_main_in_process(monkeypatch, tmp_path, "copilot", {"tool_name": "Bash", "tool_input": {"command": "ls"}})
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["permissionDecision"] == "deny"
    assert "Manifold guard failed" in out["permissionDecisionReason"] and "boom" in out["permissionDecisionReason"]


def test_f4_a_guard_that_raises_in_a_write_check_blocks_too(monkeypatch, tmp_path, capsys):
    def boom(*a, **k):
        raise ValueError("bad path")
    monkeypatch.setattr(guard, "classify_write", boom)
    rc = _call_main_in_process(monkeypatch, tmp_path, "claude",
                               {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "x.md")}})
    assert rc == 2 and "ValueError" in capsys.readouterr().err


def test_f4_unreadable_input_blocks_for_copilot_with_the_deny_json(monkeypatch, tmp_path, capsys):
    rc = _call_main_in_process(monkeypatch, tmp_path, "copilot", raw="not json")
    assert rc == 0
    assert json.loads(capsys.readouterr().out)["permissionDecision"] == "deny"


# =====================================================================================
# CP2b (T14h): failing-first cases for the points R1, R2, R4, R5, R6, R8 and R9 of the CP2a re-review
# (docs/plans/PHASE_2_PLAN.md, CP2b). Test names carry the point, as CP2a's carry the finding.
# =====================================================================================

PROTECTED_TEXT = "is a guard file, an agent definition or hook setup"  # the start of protected_message's reason

# ---- R1 (T14i): a definition is recognised by the end of the path, inside or outside the project

R1_REFUSED = [
    "/m/.claude/agents/coder.md",
    "/m/.claude/settings.json",
    "/m/.claude/settings.local.json",
    "../../../.claude/agents/coder.md",
    "/M/.CLAUDE/Agents/coder.md",
    "/m/.claude/skills/fix-bug/SKILL.md",
    "/m/.github/agents/coder.agent.md",
    "/m/.github/hooks/manifold-guard.json",
]
R1_ALLOWED = ["/m/docs/agents/a.md", "/m/not.claude/agents/a.md", "/m/.claude/agents/sub/dir/a.txt"]


@pytest.mark.parametrize("agent", AGENTS_ALL)
@pytest.mark.parametrize("path", R1_REFUSED)
def test_r1_a_definition_outside_the_project_is_refused_for_every_agent(agent, path):
    allowed, message = guard.classify_write(agent, path, True)
    assert allowed is False, (agent, path)
    assert "path exception" in message, message


@pytest.mark.parametrize("agent", AGENTS_ALL)
def test_r1_the_exception_file_outside_the_project_stays_refused_with_and_without_an_exception(agent):
    path = "/m/.manifold/guard-allow.json"
    assert guard.classify_write(agent, path, True)[0] is False
    for entry in (path_entry(".*", TODAY.isoformat()), dict(ENTRY, pattern=".*")):
        assert guard.classify_write(agent, path, True, allow=[entry])[0] is False, (agent, entry)


@pytest.mark.parametrize("path", R1_ALLOWED)
def test_r1_a_path_that_only_looks_like_a_definition_is_not_refused(path):
    assert guard.classify_write("coder", path, True)[0] is True, path


def test_r1_a_path_exception_for_a_path_outside_the_project_must_match_the_whole_path():
    path = "/m/.claude/agents/coder.md"
    whole = path_entry(r".*/\.claude/agents/coder\.md", TOMORROW.isoformat())
    assert guard.classify_write("coder", path, True, allow=[whole]) == (True, "")
    relative = path_entry(r"\.claude/agents/coder\.md", TOMORROW.isoformat())
    assert guard.classify_write("coder", path, True, allow=[relative])[0] is False


def _two_directories(tmp_path):
    project, main_checkout = tmp_path / "project", tmp_path / "main"
    (project / ".manifold").mkdir(parents=True)
    (main_checkout / ".claude" / "agents").mkdir(parents=True)
    return project, main_checkout


def test_r1_through_main_a_write_to_the_main_checkout_beside_the_project_exits_2(tmp_path):
    project, main_checkout = _two_directories(tmp_path)
    cases = [
        {"tool_name": "Write", "tool_input": {"file_path": str(main_checkout / ".claude" / "agents" / "coder.md")}},
        {"tool_name": "Edit", "tool_input": {"file_path": str(main_checkout / ".claude" / "settings.json")}},
        {"tool_name": "Write", "tool_input": {"file_path": "../main/.claude/agents/coder.md"}},
    ]
    for payload in cases:
        p = run_main(project, dict(payload, agent_type="coder"))
        assert p.returncode == 2, payload
        assert "path exception" in p.stderr


def test_r1_through_main_a_symlink_to_the_main_checkouts_agents_is_refused(tmp_path):
    project, main_checkout = _two_directories(tmp_path)
    link = project / "link"
    link.symlink_to(main_checkout / ".claude" / "agents", target_is_directory=True)
    p = run_main(project, {"tool_name": "Write", "tool_input": {"file_path": str(link / "coder.md")}})
    assert p.returncode == 2
    assert "path exception" in p.stderr


def test_r1_through_main_without_a_project_dir_variable_and_a_subdirectory_cwd_an_absolute_definition_is_refused(tmp_path):
    project = tmp_path / "project"
    (project / ".claude" / "agents").mkdir(parents=True)
    (project / "sub").mkdir()
    payload = {"tool_name": "Write", "cwd": str(project / "sub"),
               "tool_input": {"file_path": str(project / ".claude" / "agents" / "coder.md")}}
    p = run_main(project, payload, project_dir=False, cwd=tmp_path)
    assert p.returncode == 2
    assert "path exception" in p.stderr


# ---- R8 (T14i): a broken allow file grants nothing and does not take the guard down; "2026-11-07\n" is not a date

def test_r8_a_deeply_nested_allow_file_is_a_problem_not_an_exception(tmp_path):
    (tmp_path / ".manifold").mkdir()
    (tmp_path / ".manifold" / "guard-allow.json").write_text("[" * 5000)
    entries, problem = guard.load_allow(str(tmp_path))
    assert entries == []
    assert problem and ".manifold/guard-allow.json" in problem and "grants no exception" in problem


def test_r8_through_main_a_deeply_nested_allow_file_does_not_block_an_ordinary_write_but_refuses_a_definition(tmp_path):
    (tmp_path / ".manifold").mkdir()
    (tmp_path / ".manifold" / "guard-allow.json").write_text("[" * 5000)
    ordinary = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / "server" / "app.py")}}
    assert run_main(tmp_path, ordinary).returncode == 0
    definition = {"tool_name": "Write", "tool_input": {"file_path": str(tmp_path / ".claude" / "agents" / "coder.md")}}
    p = run_main(tmp_path, definition)
    assert p.returncode == 2
    assert "could not read .manifold/guard-allow.json" in p.stderr and "Manifold guard failed" not in p.stderr


def test_r8_a_date_with_a_trailing_newline_is_not_a_date():
    assert guard.parse_expires("2026-11-07\n") is None
    assert guard.parse_expires("2026-11-07") == datetime.date(2026, 11, 7)


def test_r8_a_path_exception_whose_expires_has_a_trailing_newline_grants_nothing():
    path = ".claude/agents/coder.md"
    entry = path_entry(r"\.claude/agents/coder\.md", TOMORROW.isoformat() + "\n")
    allowed, message = guard.classify_write("coder", path, True, allow=[entry])
    assert allowed is False
    assert "no valid expires date" in message


# ---- R2, R6, R4 (T14j, T14k): shell lines that are refused

# The protected-file message (a protected name is on the line).
R_REFUSED_PROTECTED = [
    # R2: brace expansion
    "cp a .manifold/guard-allow.js{on,x}",
    "rm .manifold/hooks/gua{rd.py,x}",
    "rm .cla{ude,}/agents/coder.md",
    "rm {.claude,x}/agents/coder.md",
    # R6: .github itself
    "rm -rf .github",
    "rm -rf ./.github/",
    "mv .github /x",
    # R4: a protected name inside code is refused whatever the API (reading goes through cat or the Read tool)
    "python3 -c \"import subprocess; subprocess.run(['rm','.manifold/guard-allow.json'])\"",
    "python3 -c \"print(open('.claude/settings.json').read())\"",
    "python3 - <<< \"print('.manifold/guard-log.jsonl')\"",
    "node -e \"x('.manifold/hooks/guard.py')\"",
    # R9 (kept): a copy or move that writes a protected name, and the copy into a protected directory
    "cp a .claude/agents/coder.md",
    "cp -t .claude/agents a",
    "mv .claude/agents/coder.md ~/x",
]

# The shell-write message (the line writes, copies, moves or runs a command).
R_REFUSED_SHELL = [
    "python3 -c \"__import__('os').system('x')\"",
    "python3 -c \"exec('x')\"",
    "python3 -c \"eval('x')\"",
    "python3 -c \"import os; os.open('f', os.O_WRONLY)\"",
    "python3 -c \"import fileinput; fileinput.input(inplace=True)\"",
    "python3 -c \"import importlib; importlib.import_module('os')\"",
    "python3 -c \"import logging; logging.FileHandler('f')\"",
    "python3 -c \"import pty; pty.spawn(['x'])\"",
    "python3 -c \"from pathlib import Path; Path('f').replace('g')\"",
    "sed -i s/a/b/ .claude/agents/coder.md",
    "jq . a > .claude/settings.json",
]

R_ALLOWED = [
    # R6: the directory itself is protected against the shell, its other contents are not
    "ls .github",
    "git add .github",
    "touch .github/workflows/ci.yml",
    # R2: a brace that is not a comma list
    "cat {a,b}.txt",
    "find . -exec grep x {} +",
    # R9: the read-only look and the copy out
    "sed -n 5p .claude/agents/coder.md",
    "jq . .claude/settings.json",
    "awk 'NR==5' .claude/agents/coder.md",
    "comm a .claude/agents/coder.md",
    "cp .claude/agents/coder.md ~/backup.md",
    "cp -r .claude ~/backup",
    "python3 -c 'print(\"a\".replace(\"a\",\"b\"))'",
]


@pytest.mark.parametrize("command", R_REFUSED_PROTECTED)
def test_r2_r4_r6_a_command_that_names_a_protected_path_is_refused_with_the_protected_message(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is False, command
    assert PROTECTED_TEXT in message, message


@pytest.mark.parametrize("command", R_REFUSED_SHELL)
def test_r4_r9_code_and_write_forms_are_refused_with_the_shell_message(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is False, command
    assert "Write" in message and "Edit" in message and ".manifold/scratch/" in message, message


@pytest.mark.parametrize("command", R_ALLOWED)
def test_r6_r9_the_read_only_look_and_the_copy_out_stay_allowed(command):
    allowed, message = guard.classify_bash(command)
    assert allowed is True, (command, message)


# ---- T31 (INT-22): the coordinator's write allowlist. The coordinator is default-deny in the guard, so the
# refusal cases below were expected to pass at once; the one that fails first is the new skill folder.

COORDINATOR_REFUSED = [
    "docs/plans/PHASE_2_PLAN.md", "docs/plans/PHASE_2_TEST_PLAN.md", "docs/plans/REVIEW_PLAN_2.md",
    "server/app.py", "bundles/base/tests/test_x.py", "bundles/base/agents/coder.agent.md",
    "REVIEW.md", "AGENTS.md", "CLAUDE.md", "docs/templates/PULL_REQUEST_TEMPLATE.md",
    "docs/process/REVIEW_CYCLE.md", "docs/agents/harness-capabilities.md", "docs/agents/sub/x-failures.md",
    ".manifold/scratch/probe.py", "intent/notes.md", "intent/sub/INT-30-x.md",
]


@pytest.mark.parametrize("path", COORDINATOR_REFUSED)
@pytest.mark.parametrize("exists", [True, False])
def test_t31_the_coordinator_cannot_write_plans_reviews_source_tests_or_documents(path, exists):
    allowed, message = guard.classify_write("coordinator", path, exists)
    assert allowed is False, path
    assert "coordinator" in message and "failures" in message and "INT-" in message


@pytest.mark.parametrize("path,exists", [
    ("docs/agents/claude-desktop-failures.md", True), ("docs/agents/claude-desktop-failures.md", False),
    ("docs/agents/vscode-copilot-failures.md", True), ("docs/agents/cli-failures.md", False),
    ("intent/INT-31-gap.md", False),
])
def test_t31_the_coordinator_may_append_to_failure_records_and_create_a_draft_intent(path, exists):
    assert guard.classify_write("coordinator", path, exists) == (True, "")


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit", "NotebookEdit"])
@pytest.mark.parametrize("name", ["docs/plans/PHASE_2_PLAN.md", "server/app.py", "bundles/base/tests/test_x.py"])
def test_t31_a_coordinator_write_to_a_plan_source_or_test_is_refused_by_the_hook_and_logged(tmp_path, tool, name):
    payload = {"tool_name": tool, "agent_type": "coordinator", "tool_input": {"file_path": str(tmp_path / name)}}
    p = run_hook(tmp_path, payload)
    assert p.returncode == 2 and "coordinator" in p.stderr
    (entry,) = log_lines(tmp_path)
    assert entry["agent_type"] == "coordinator" and entry["tool"] == tool


def test_t31_the_coordinators_skill_file_is_protected_like_every_other_skill_file():
    # the guard cannot import build.py; T32 adds the coordinate-cycle skill, so the guard's list must name it
    path = ".claude/skills/coordinate-cycle/SKILL.md"
    for agent in AGENTS_ALL:
        allowed, message = guard.classify_write(agent, path, True)
        assert allowed is False, agent
        assert "path exception" in message
    assert "coordinate-cycle" in guard.SKILL_DIRS


# ---- worktrees: the hook's project directory is the main checkout, the agent works in a checkout under it.
# Structure follows the test_r1_through_main_* tests (run_main with a project directory and a payload).

def _main_with_worktrees(tmp_path):
    """A main checkout (project directory) with two linked worktrees under .claude/worktrees/, each with a `.git` file."""
    main = tmp_path / "main"
    (main / ".git").mkdir(parents=True)
    trees = [_add_worktree(main, main / ".claude" / "worktrees" / name, name) for name in ("wt-a", "wt-b")]
    return main, trees[0], trees[1]


def _add_worktree(main, wt, name):
    """A linked worktree of `main` at `wt`, laid out as git does: a `.git` file pointing at `.git/worktrees/<name>`,
    which holds `commondir` and a `gitdir` file pointing back at the worktree's `.git` file."""
    (wt / "docs" / "plans").mkdir(parents=True)
    (wt / "docs" / "agents").mkdir(parents=True)
    (wt / "intent").mkdir()
    (wt / ".claude" / "agents").mkdir(parents=True)
    (wt / ".manifold" / "hooks").mkdir(parents=True)
    gitdir = main / ".git" / "worktrees" / name
    gitdir.mkdir(parents=True)
    (gitdir / "commondir").write_text("../..\n")
    (gitdir / "gitdir").write_text("%s\n" % (wt / ".git"))
    (wt / ".git").write_text("gitdir: %s\n" % gitdir)
    return wt


def _other_repository(tmp_path):
    other = tmp_path / "other"
    (other / ".git").mkdir(parents=True)
    (other / "docs" / "plans").mkdir(parents=True)
    (other / "docs" / "agents").mkdir(parents=True)
    return other


def _write_payload(agent, path, tool="Write"):
    return {"tool_name": tool, "tool_input": {"file_path": str(path)}, "agent_type": agent}


def test_wt_a_reviewer_may_write_its_review_file_in_a_worktree_under_the_project_directory(tmp_path):
    main, wt, _ = _main_with_worktrees(tmp_path)
    p = run_main(main, _write_payload("reviewer", wt / "docs" / "plans" / "REVIEW_PLAN_3.md"))
    assert p.returncode == 0, p.stderr
    assert log_lines(main) == []


def test_wt_a_coordinator_may_write_its_failures_record_and_a_new_draft_in_a_worktree(tmp_path):
    main, wt, _ = _main_with_worktrees(tmp_path)
    for path in (wt / "docs" / "agents" / "claude-desktop-failures.md", wt / "intent" / "INT-31-gap.md"):
        p = run_main(main, _write_payload("coordinator", path))
        assert p.returncode == 0, (path, p.stderr)
    (wt / "intent" / "INT-1-old.md").write_text("x")
    assert run_main(main, _write_payload("coordinator", wt / "intent" / "INT-1-old.md")).returncode == 2


@pytest.mark.parametrize("name", ["docs/plans/PHASE_3_PLAN.md", "server/app.py", "docs/plans/sub/REVIEW_PLAN_3.md",
                                  "docs/plans/REVIEW_PLAN_x.md"])
def test_wt_a_reviewer_is_refused_any_other_path_in_a_worktree(tmp_path, name):
    main, wt, _ = _main_with_worktrees(tmp_path)
    p = run_main(main, _write_payload("reviewer", wt / name))
    assert p.returncode == 2
    assert "may write only" in p.stderr
    assert log_lines(main)[-1]["rule"] == "write-allowlist"


def test_wt_a_directory_without_a_git_entry_under_the_project_is_not_a_checkout(tmp_path):
    main, wt, _ = _main_with_worktrees(tmp_path)
    (main / "sub" / "docs" / "plans").mkdir(parents=True)
    p = run_main(main, _write_payload("reviewer", main / "sub" / "docs" / "plans" / "REVIEW_PLAN_3.md"))
    assert p.returncode == 2


def test_wt_a_reviewer_still_writes_its_review_file_in_the_main_checkout(tmp_path):
    main, _, _ = _main_with_worktrees(tmp_path)
    (main / "docs" / "plans").mkdir(parents=True)
    assert run_main(main, _write_payload("reviewer", main / "docs" / "plans" / "REVIEW_PLAN_3.md")).returncode == 0
    assert run_main(main, _write_payload("reviewer", main / "docs" / "plans" / "PHASE_3_PLAN.md")).returncode == 2


@pytest.mark.parametrize("agent", ["reviewer", "coordinator", "coder", ""])
@pytest.mark.parametrize("rel", [".manifold/guard-allow.json", ".manifold/guard-log.jsonl", ".manifold/hooks/guard.py"])
def test_wt_the_manifold_files_stay_protected_in_the_main_checkout_and_in_a_worktree(tmp_path, agent, rel):
    main, wt, _ = _main_with_worktrees(tmp_path)
    for base in (main, wt):
        p = run_main(main, _write_payload(agent, base / rel, tool="Edit"))
        assert p.returncode == 2, (base, rel)
        assert log_lines(main)[-1]["rule"] == "protected-file"


@pytest.mark.parametrize("agent", ["reviewer", "coordinator", "coder", ""])
@pytest.mark.parametrize("rel", [".claude/agents/coder.md", ".claude/settings.json",
                                 ".claude/skills/fix-bug/SKILL.md", ".github/agents/coder.agent.md"])
def test_wt_agent_definitions_stay_protected_in_the_main_checkout_and_in_a_worktree(tmp_path, agent, rel):
    main, wt, _ = _main_with_worktrees(tmp_path)
    for base in (main, wt):
        p = run_main(main, _write_payload(agent, base / rel))
        assert p.returncode == 2, (base, rel)
        assert "path exception" in p.stderr


def test_wt_a_path_exception_for_a_definition_still_needs_to_match_the_path_as_the_guard_sees_it(tmp_path):
    main, wt, _ = _main_with_worktrees(tmp_path)
    (main / ".manifold").mkdir(exist_ok=True)
    entry = dict(ENTRY, scope="path", pattern=r"\.claude/worktrees/wt-a/\.claude/agents/coder\.md",
                 expires=TOMORROW.isoformat())
    (main / ".manifold" / "guard-allow.json").write_text(json.dumps([entry]))
    assert run_main(main, _write_payload("coder", wt / ".claude" / "agents" / "coder.md")).returncode == 0
    assert run_main(main, _write_payload("coder", main / ".claude" / "agents" / "coder.md")).returncode == 2


def test_wt_a_write_into_another_worktrees_definitions_is_refused_from_either_project_directory(tmp_path):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    target = wt_b / ".claude" / "agents" / "coder.md"
    for project in (main, wt_a):  # the hook's project directory is the main checkout or the worktree the agent works in
        p = run_main(project, _write_payload("coder", target))
        assert p.returncode == 2, project
        assert "path exception" in p.stderr
    p = run_main(wt_a, _write_payload("coder", main / ".claude" / "agents" / "coder.md"))
    assert p.returncode == 2


def test_wt_a_symlink_in_a_worktree_to_another_checkouts_definitions_is_refused(tmp_path):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    (wt_a / "docs" / "plans" / "link").symlink_to(wt_b / ".claude" / "agents", target_is_directory=True)
    (wt_a / "docs" / "plans" / "mainlink").symlink_to(main / ".manifold", target_is_directory=True)
    for given in ("link/coder.md", "mainlink/guard-allow.json"):
        for agent in ("reviewer", "coder"):
            p = run_main(main, _write_payload(agent, wt_a / "docs" / "plans" / given))
            assert p.returncode == 2, (agent, given)


def test_wt_a_symlink_that_makes_a_review_file_land_outside_the_worktree_is_refused(tmp_path):
    main, wt_a, _ = _main_with_worktrees(tmp_path)
    (main / "docs" / "plans").mkdir(parents=True)
    (wt_a / "docs" / "plans" / "REVIEW_PLAN_3.md").symlink_to(main / "docs" / "plans" / "PHASE_3_PLAN.md")
    p = run_main(main, _write_payload("reviewer", wt_a / "docs" / "plans" / "REVIEW_PLAN_3.md"))
    assert p.returncode == 2


def test_wt_a_planted_git_entry_inside_a_definitions_folder_does_not_lift_the_protection(tmp_path):
    main, wt, _ = _main_with_worktrees(tmp_path)
    (wt / ".claude" / "agents" / ".git").write_text("gitdir: elsewhere\n")
    (main / ".manifold" / "hooks").mkdir(parents=True)
    (main / ".manifold" / "hooks" / ".git").write_text("gitdir: elsewhere\n")
    cases = [wt / ".claude" / "agents" / "coder.md", main / ".manifold" / "hooks" / "guard.py"]
    for agent in ("reviewer", "coder", ""):
        for target in cases:
            assert run_main(main, _write_payload(agent, target)).returncode == 2, (agent, target)


def test_wt_an_error_in_the_checkout_lookup_blocks_the_call(monkeypatch, tmp_path, capsys):
    main, wt, _ = _main_with_worktrees(tmp_path)

    def boom(*a, **k):
        raise OSError("lookup failed")
    monkeypatch.setattr(guard.os.path, "lexists", boom)
    rc = _call_main_in_process(monkeypatch, main, "claude", _write_payload("reviewer", wt / "docs" / "plans" / "REVIEW_PLAN_3.md"))
    assert rc == 2 and "Manifold guard failed" in capsys.readouterr().err


def test_wt_the_exception_file_and_the_log_belong_to_the_project_directory_not_the_worktree(tmp_path):
    main, wt, _ = _main_with_worktrees(tmp_path)
    (main / ".manifold").mkdir(exist_ok=True)
    (wt / ".manifold" / "guard-allow.json").write_text(json.dumps([dict(ENTRY, pattern="echo x > f")]))  # a worktree's own file grants nothing
    bash = {"tool_name": "Bash", "tool_input": {"command": "echo x > f"}, "cwd": str(wt)}
    assert run_main(main, bash).returncode == 2
    assert len(log_lines(main)) == 1 and not (wt / ".manifold" / "guard-log.jsonl").exists()


# ---- sibling checkouts: the hook's project directory is one checkout (here a worktree), the agent works in another
# checkout of the same repository, wherever it sits on disk (the observed refusal of a review file in a sibling worktree).

def test_wt_sibling_a_reviewer_may_write_its_review_file_in_another_worktree_of_the_same_repository(tmp_path):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    target = wt_b / "docs" / "plans" / "REVIEW_PLAN_3.md"
    for project in (wt_a, main):
        p = run_main(project, _write_payload("reviewer", target))
        assert p.returncode == 0, (project, p.stderr)
        assert log_lines(project) == []
    # and into the main checkout from a worktree
    assert run_main(wt_a, _write_payload("reviewer", main / "docs" / "plans" / "REVIEW_PLAN_3.md")).returncode == 0


def test_wt_sibling_a_worktree_outside_the_project_directory_tree_counts_too(tmp_path):
    main, wt_a, _ = _main_with_worktrees(tmp_path)
    far = _add_worktree(main, tmp_path / "elsewhere" / "far", "far")
    assert run_main(wt_a, _write_payload("reviewer", far / "docs" / "plans" / "REVIEW_PLAN_3.md")).returncode == 0
    assert run_main(wt_a, _write_payload("coordinator", far / "docs" / "agents" / "cli-failures.md")).returncode == 0
    assert run_main(wt_a, _write_payload("reviewer", far / "server" / "app.py")).returncode == 2


def test_wt_sibling_a_coordinator_may_write_failures_and_a_new_draft_in_another_worktree(tmp_path):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    for path in (wt_b / "docs" / "agents" / "claude-desktop-failures.md", wt_b / "intent" / "INT-31-gap.md"):
        assert run_main(wt_a, _write_payload("coordinator", path)).returncode == 0, path
    (wt_b / "intent" / "INT-1-old.md").write_text("x")
    assert run_main(wt_a, _write_payload("coordinator", wt_b / "intent" / "INT-1-old.md")).returncode == 2


@pytest.mark.parametrize("name", ["docs/plans/PHASE_3_PLAN.md", "server/app.py", "docs/plans/REVIEW_PLAN_x.md"])
def test_wt_sibling_a_reviewer_is_refused_any_other_path_in_another_worktree(tmp_path, name):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    p = run_main(wt_a, _write_payload("reviewer", wt_b / name))
    assert p.returncode == 2
    assert "may write only" in p.stderr
    assert log_lines(wt_a)[-1]["rule"] == "write-allowlist"


@pytest.mark.parametrize("agent", ["reviewer", "coordinator", "coder", ""])
@pytest.mark.parametrize("rel", [".manifold/guard-allow.json", ".manifold/guard-log.jsonl", ".manifold/hooks/guard.py",
                                 ".claude/agents/coder.md", ".claude/settings.json", ".claude/skills/fix-bug/SKILL.md"])
def test_wt_sibling_protected_files_and_definitions_stay_protected_in_every_checkout(tmp_path, agent, rel):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    for base in (wt_a, wt_b, main):
        assert run_main(wt_a, _write_payload(agent, base / rel)).returncode == 2, (base, rel)


def test_wt_sibling_a_checkout_of_a_different_repository_stays_refused(tmp_path):
    main, wt_a, _ = _main_with_worktrees(tmp_path)
    other = _other_repository(tmp_path)
    for agent, rel in (("reviewer", "docs/plans/REVIEW_PLAN_3.md"), ("coordinator", "docs/agents/cli-failures.md")):
        p = run_main(wt_a, _write_payload(agent, other / rel))
        assert p.returncode == 2, agent
        assert str(other) in p.stderr  # judged as a path outside the project, as given
    other_wt = _add_worktree(other, tmp_path / "other-wt", "ow")
    assert run_main(wt_a, _write_payload("reviewer", other_wt / "docs" / "plans" / "REVIEW_PLAN_3.md")).returncode == 2


def test_wt_sibling_a_forged_git_entry_is_not_accepted(tmp_path):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    real_common = main / ".git"
    review = "docs/plans/REVIEW_PLAN_3.md"
    # 1. a `.git` file that points at a real worktree's git directory: the back-link names the real worktree, not this one
    f1 = tmp_path / "forged1"
    (f1 / "docs" / "plans").mkdir(parents=True)
    (f1 / ".git").write_text("gitdir: %s\n" % (real_common / "worktrees" / "wt-b"))
    # 2. a `.git` file with its own git directory whose `commondir` names the real repository and whose back-link is right
    f2 = tmp_path / "forged2"
    (f2 / "docs" / "plans").mkdir(parents=True)
    (tmp_path / "forged2-gitdir").mkdir()
    (tmp_path / "forged2-gitdir" / "commondir").write_text(str(real_common) + "\n")
    (tmp_path / "forged2-gitdir" / "gitdir").write_text("%s\n" % (f2 / ".git"))
    (f2 / ".git").write_text("gitdir: %s\n" % (tmp_path / "forged2-gitdir"))
    # 3. a `.git` directory (a repository of its own, never the same one)
    f3 = tmp_path / "forged3"
    (f3 / ".git").mkdir(parents=True)
    (f3 / "docs" / "plans").mkdir(parents=True)
    # 4. a `.git` file with garbage in it, and one whose git directory does not exist
    f4 = tmp_path / "forged4"
    (f4 / "docs" / "plans").mkdir(parents=True)
    (f4 / ".git").write_text("not a gitdir line\n")
    f5 = tmp_path / "forged5"
    (f5 / "docs" / "plans").mkdir(parents=True)
    (f5 / ".git").write_text("gitdir: %s\n" % (tmp_path / "does-not-exist"))
    for forged in (f1, f2, f3, f4, f5):
        for project in (wt_a, main):
            p = run_main(project, _write_payload("reviewer", forged / review))
            assert p.returncode == 2, (forged, project)


def test_wt_sibling_a_symlink_to_another_repository_is_refused(tmp_path):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    other = _other_repository(tmp_path)
    (wt_b / "docs" / "plans" / "REVIEW_PLAN_3.md").symlink_to(other / "docs" / "plans" / "REVIEW_PLAN_3.md")
    assert run_main(wt_a, _write_payload("reviewer", wt_b / "docs" / "plans" / "REVIEW_PLAN_3.md")).returncode == 2


def test_wt_sibling_an_error_while_reading_the_git_entry_blocks_the_call(monkeypatch, tmp_path, capsys):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)

    def boom(*a, **k):
        raise OSError("lookup failed")
    monkeypatch.setattr(guard.os.path, "lexists", boom)
    rc = _call_main_in_process(monkeypatch, wt_a, "claude", _write_payload("reviewer", wt_b / "docs" / "plans" / "REVIEW_PLAN_3.md"))
    assert rc == 2 and "Manifold guard failed" in capsys.readouterr().err


def test_wt_sibling_the_exception_file_and_the_log_stay_the_project_directorys_own(tmp_path):
    main, wt_a, wt_b = _main_with_worktrees(tmp_path)
    p = run_main(wt_a, _write_payload("reviewer", wt_b / "server" / "app.py"))
    assert p.returncode == 2
    assert len(log_lines(wt_a)) == 1 and not (wt_b / ".manifold" / "guard-log.jsonl").exists()
