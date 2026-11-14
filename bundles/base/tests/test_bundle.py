# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Tests for the Manifold build tool and installer (installer exercised through its real CLI)."""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("agentkit_build", ROOT / "tools" / "build.py")
build = importlib.util.module_from_spec(_spec)
sys.modules["agentkit_build"] = build
_spec.loader.exec_module(build)


# ------------------------------------------------------------------ fixtures

def copy_source(dst: Path) -> Path:
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns("dist", "tests", "__pycache__", ".pytest_cache"))
    return dst


@pytest.fixture(scope="session")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("dist")
    return build.build_zip(ROOT, out)


@pytest.fixture()
def bundle_dir(built, tmp_path):
    with zipfile.ZipFile(built) as zf:
        zf.extractall(tmp_path)
    (inner,) = [p for p in tmp_path.iterdir() if p.is_dir()]
    return inner


@pytest.fixture()
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / ".git").mkdir(parents=True)
    return r


def run(bundle_dir, repo, *args):
    p = subprocess.run([sys.executable, str(bundle_dir / "install.py"), "--target", str(repo), *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def tree(repo):
    return sorted(str(p.relative_to(repo)) for p in repo.rglob("*") if p.is_file() and ".git" not in p.parts)


AGENT_FILES = [".claude/agents/%s.md" % r for r in ("planner", "coder", "bug-coder", "test-planner", "test-coder")]
COPILOT_FILES = [".github/agents/%s.agent.md" % r for r in ("planner", "coder", "bug-coder", "test-planner", "test-coder")]
TEMPLATE_FILES = ["docs/templates/PHASE_PLAN_TEMPLATE.md", "docs/templates/PHASE_TEST_PLAN_TEMPLATE.md", "docs/templates/WT_TEMPLATE.md"]


# --------------------------------------------------------------------- lint

def test_lint_is_clean():
    assert build.lint(ROOT) == []


def test_all_sources_and_rendered_agents_start_with_frontmatter():
    fragments, rules = build.load_fragments(ROOT), build.load_rules(ROOT)
    for role, text in build.load_agents(ROOT).items():
        assert text.startswith("---\n"), role
        for fmt in ("claude", "copilot"):
            assert build.render_agent(role, text, fmt, fragments, rules).startswith("---\n")


def test_lint_rejects_license_comment_before_frontmatter(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "agents" / "planner.agent.md"
    p.write_text("<!-- Copyright -->\n" + p.read_text())
    assert any("line 1" in x for x in build.lint(src))


def test_lint_rejects_unknown_include(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "agents" / "coder.agent.md"
    p.write_text(p.read_text().replace("<!-- include: project-facts -->", "<!-- include: nope -->"))
    assert any("unknown include" in x for x in build.lint(src))


def test_lint_rejects_forbidden_term(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "templates" / "PHASE_PLAN_TEMPLATE.md"
    p.write_text(p.read_text() + "\nSee Mediumroast docs.\n")
    assert any("forbidden term" in x for x in build.lint(src))


@pytest.mark.parametrize("section", ["Why", "Instead"])
def test_rule_without_why_or_instead_is_rejected(tmp_path, section):
    src = copy_source(tmp_path / "src")
    p = src / "rules" / "core" / "no-secrets.md"
    text = p.read_text()
    start = text.index("## " + section)
    nxt = text.find("## ", start + 3)
    p.write_text(text[:start] + (text[nxt:] if nxt != -1 else ""))
    assert any(section in x for x in build.lint(src))


def test_rule_with_reference_marker_is_rejected(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "rules" / "core" / "no-secrets.md"
    p.write_text(p.read_text().replace("tell the user to rotate it", "ask the {{ref:planner}} to rotate it"))
    assert any("markers" in x for x in build.lint(src))


def test_rule_id_must_match_filename(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "rules" / "core" / "no-secrets.md"
    p.write_text(p.read_text().replace("id: no-secrets", "id: something-else"))
    assert any("must equal the file name" in x for x in build.lint(src))


def test_rule_unknown_role_is_rejected(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "rules" / "core" / "no-secrets.md"
    p.write_text(p.read_text().replace("applies_to: coder, bug-coder", "applies_to: wizard"))
    assert any("unknown role" in x for x in build.lint(src))


def test_deprecated_rules_are_not_rendered(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "rules" / "core" / "no-secrets.md"
    p.write_text(p.read_text().replace("status: active", "status: deprecated"))
    assert "no-secrets" not in {r["id"] for r in build.load_rules(src)}


# ---------------------------------------------------------------- rendering

def test_claude_format_keeps_only_name_description_and_denied_tools(built):
    with zipfile.ZipFile(built) as zf:
        name = [n for n in zf.namelist() if n.endswith("payload/claude/.claude/agents/reviewer.md")][0]
        head = zf.read(name).decode().split("---")[1]
    # top-level keys only: the guard hook block (T6) adds "hooks" and its nested lines are indented
    keys = {line.split(":")[0] for line in head.strip().splitlines() if not line.startswith((" ", "-"))}
    assert keys == {"name", "description", "disallowedTools", "hooks"}


def test_copilot_format_keeps_tools_hint_and_handoffs(built):
    with zipfile.ZipFile(built) as zf:
        name = [n for n in zf.namelist() if n.endswith("payload/copilot/.github/agents/planner.agent.md")][0]
        head = zf.read(name).decode().split("---")[1]
    for key in ("name:", "description:", "argument-hint:", "tools:", "handoffs:"):
        assert key in head
    assert "agent: coder" in head


def test_description_with_colon_and_quotes_is_emitted_as_valid_quoted_scalar():
    text = ('---\nname: planner\ndescription: Does X: then "Y" # not a comment\n---\n\nBody\n'
            "<!-- include: rules -->\n")
    out = build.render_agent("planner", text, "claude", {}, [])
    line = [x for x in out.splitlines() if x.startswith("description:")][0]
    assert json.loads(line.split(": ", 1)[1]) == 'Does X: then "Y" # not a comment'


def test_multiline_description_is_rejected():
    text = "---\nname: planner\ndescription: >\n  folded\n---\n\nBody\n"
    with pytest.raises(build.BuildError):
        build.render_agent("planner", text, "claude", {}, [])


def test_rules_are_selected_by_role():
    rules = build.load_rules(ROOT)
    planner = {r["id"] for r in build.rules_for(rules, "planner")}
    coder = {r["id"] for r in build.rules_for(rules, "coder")}
    bug = {r["id"] for r in build.rules_for(rules, "bug-coder")}
    assert "plan-means-stop" in planner and "plan-means-stop" not in coder and "plan-means-stop" not in bug
    assert "diagnose-before-fix" in bug and "diagnose-before-fix" not in planner
    assert "scope-stage-only-changed-files" in coder and "scope-stage-only-changed-files" not in planner
    for group in (planner, coder, bug):
        assert "frontmatter-first-line" in group


def test_every_rule_is_rendered_somewhere():
    rules = build.load_rules(ROOT)
    used = set()
    for role in build.ROLES:
        used |= {r["id"] for r in build.rules_for(rules, role)}
    assert used == {r["id"] for r in rules}


# ------------------------------------------------------------------ packaging

def test_build_is_deterministic(tmp_path):
    a = build.build_zip(ROOT, tmp_path / "a")
    b = build.build_zip(ROOT, tmp_path / "b")
    assert hashlib.sha256(a.read_bytes()).hexdigest() == hashlib.sha256(b.read_bytes()).hexdigest()


def test_payload_hashes_match_bundle_json(bundle_dir):
    bundle = json.loads((bundle_dir / "bundle.json").read_text())
    entries = [e for fmt in bundle["formats"].values() for e in fmt] + bundle["common"]
    assert entries
    for e in entries:
        assert hashlib.sha256((bundle_dir / e["src"]).read_bytes()).hexdigest() == e["sha256"], e["path"]


def test_zip_has_one_visible_top_level_folder_and_safe_paths(built):
    with zipfile.ZipFile(built) as zf:
        names = zf.namelist()
    tops = {n.split("/")[0] for n in names}
    assert tops == {"manifold-base-" + (ROOT / "VERSION").read_text().strip()}
    assert not any(n.startswith("/") or ".." in n.split("/") for n in names)


def test_installers_are_executable_in_the_zip(built):
    with zipfile.ZipFile(built) as zf:
        for info in zf.infolist():
            if info.filename.endswith(("install.py", "install.sh")):
                assert (info.external_attr >> 16) & 0o111


HOOK_INSTALLED = ".manifold/hooks/guard.py"
SCRATCH_INSTALLED = ".manifold/scratch/.gitignore"
LOG_IGNORE_INSTALLED = ".manifold/.gitignore"


def test_hook_scratch_and_log_ignore_files_are_in_the_zip_and_bundle_json(built, bundle_dir):
    with zipfile.ZipFile(built) as zf:
        names = zf.namelist()
    for path in (HOOK_INSTALLED, SCRATCH_INSTALLED, LOG_IGNORE_INSTALLED):
        assert any(n.endswith("payload/common/" + path) for n in names), path
    bundle = json.loads((bundle_dir / "bundle.json").read_text())
    by_path = {e["path"]: e for e in bundle["common"]}
    for path in (HOOK_INSTALLED, SCRATCH_INSTALLED, LOG_IGNORE_INSTALLED):
        assert set(by_path[path]["profiles"]) == {"build", "quality", "single"}, path


def test_scratch_gitignore_ignores_everything_but_itself_and_the_log_is_ignored():
    assert (ROOT / "config" / "scratch.gitignore").read_text() == "*\n!.gitignore\n"
    assert "guard-log.jsonl" in (ROOT / "config" / "manifold.gitignore").read_text().split()


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
def test_hook_script_scratch_folder_and_log_ignore_are_installed_in_every_profile(bundle_dir, repo, profile):
    assert run(bundle_dir, repo, "--profile", profile, "--apply")[0] == 0
    assert (repo / HOOK_INSTALLED).read_bytes() == (ROOT / "hooks" / "guard.py").read_bytes()
    assert (repo / SCRATCH_INSTALLED).read_text() == "*\n!.gitignore\n"
    assert "guard-log.jsonl" in (repo / LOG_IGNORE_INSTALLED).read_text()


def test_lint_rejects_a_hook_that_does_not_compile(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "hooks" / "guard.py"
    p.write_text(p.read_text() + "\ndef broken(:\n")
    assert any("hooks/guard.py does not compile" in x for x in build.lint(src))


@pytest.mark.parametrize("line", ["import requests", "from yaml import safe_load", "from . import sibling"])
def test_lint_rejects_a_hook_that_imports_outside_the_standard_library(tmp_path, line):
    src = copy_source(tmp_path / "src")
    p = src / "hooks" / "guard.py"
    p.write_text(p.read_text() + "\n" + line + "\n")
    assert any("hooks/guard.py" in x and ("standard library" in x or "relative import" in x) for x in build.lint(src))


def _frontmatter_lines(text):
    assert text.startswith("---\n")
    return text.split("\n---\n", 1)[0].split("\n")[1:]


def test_every_claude_agent_carries_the_guard_hook_block_after_disallowed_tools(bundle_dir):
    folder = bundle_dir / "payload" / "claude" / ".claude" / "agents"
    files = sorted(folder.glob("*.md"))
    assert [p.stem for p in files] == sorted(build.ROLES)
    for p in files:
        fm = _frontmatter_lines(p.read_text())
        assert fm[0] == "name: " + p.stem, p.name
        start = fm.index("hooks:")
        assert fm[start:] == list(build.GUARD_HOOKS_CLAUDE), p.name
        assert all(not line.startswith("disallowedTools") for line in fm[start:])
        assert start == len(fm) - len(build.GUARD_HOOKS_CLAUDE)


def test_the_claude_guard_hook_uses_the_project_dir_and_an_exact_name_matcher():
    lines = list(build.GUARD_HOOKS_CLAUDE)
    matcher = json.loads([x for x in lines if "matcher:" in x][0].split(": ", 1)[1])
    command = json.loads([x for x in lines if "command:" in x][0].split(": ", 1)[1])
    # only letters and | make Claude Code read the matcher as a list of exact tool names (harness-capabilities.md)
    assert all(c.isalpha() or c == "|" for c in matcher)
    assert {"Bash", "Write", "Edit"} <= set(matcher.split("|"))
    assert '"${CLAUDE_PROJECT_DIR}/.manifold/hooks/guard.py"' in command and command.endswith("--client claude")
    assert "PreToolUse" in lines[1]


def test_rendered_claude_frontmatter_still_starts_on_line_one_for_every_role():
    fragments, rules = build.load_fragments(ROOT), build.load_rules(ROOT)
    for role, text in build.load_agents(ROOT).items():
        out = build.render_agent(role, text, "claude", fragments, rules)
        assert out.startswith("---\nname: %s\n" % role), role
        assert "hooks:" in out.split("\n---\n", 1)[0], role


def test_copilot_and_skills_outputs_do_not_carry_the_claude_hook_block(bundle_dir):
    for folder in ("copilot", "skills"):
        for p in (bundle_dir / "payload" / folder).rglob("*.md"):
            text = p.read_text()
            assert "PreToolUse" not in text and "CLAUDE_PROJECT_DIR" not in text, p
            assert "hooks:" not in text.split("\n---\n", 1)[0], p


COPILOT_HOOK_INSTALLED = ".github/hooks/manifold-guard.json"


def test_copilot_hook_file_has_the_verified_schema_and_calls_the_guard():
    data = json.loads((ROOT / "hooks" / "copilot-guard.json").read_text())
    assert data["version"] == 1
    (entry,) = data["hooks"]["preToolUse"]
    assert entry["type"] == "command"
    # CP2a T14a (named in the plan): the exact-command assertion changes with the fail-closed command (T14b);
    # the old expectation was "python3 .manifold/hooks/guard.py --client copilot" alone.
    # CP2b T14h, R5 (named in the plan): the three `in` checks below are replaced by one exact `==` against the
    # whole command, so dropping the `||` fallback or the `test -f` check fails it. The change makes the test stricter.
    deny = '{"permissionDecision":"deny","permissionDecisionReason":"%s"}'
    expected = (
        "test -f .manifold/hooks/guard.py || { echo '" + deny % build.GUARD_MISSING_MESSAGE + "'; exit 0; }; "
        "python3 .manifold/hooks/guard.py --client copilot || echo '"
        + deny % "The Manifold guard failed to run, so this tool call is blocked. Tell a human." + "'"
    )
    assert entry["command"] == expected
    assert isinstance(entry["timeoutSec"], int)


# ---- CP2a T14a, F4: the hook commands fail closed (run with `sh -c`, the shell form the plan records)

def _sh(command, cwd, project_dir=None, stdin="{}"):
    env = {"PATH": "/usr/bin:/bin"}
    if project_dir is not None:
        env["CLAUDE_PROJECT_DIR"] = str(project_dir)
    return subprocess.run(["sh", "-c", command], input=stdin, capture_output=True, text=True, env=env, cwd=str(cwd))


def _stub(project, code, message=""):
    script = project / ".manifold" / "hooks" / "guard.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("import sys\nsys.stderr.write(%r)\nsys.exit(%d)\n" % (message, code))


def test_the_claude_command_blocks_with_a_plain_message_when_the_guard_script_is_missing(tmp_path):
    p = _sh(build.GUARD_COMMAND, tmp_path, project_dir=tmp_path)
    assert p.returncode == 2
    assert build.GUARD_MISSING_MESSAGE in p.stderr
    assert "re-running the installer" in build.GUARD_MISSING_MESSAGE and ".manifold/hooks/guard.py" in build.GUARD_MISSING_MESSAGE


def test_the_claude_command_blocks_when_the_project_dir_variable_is_not_set(tmp_path):
    p = _sh(build.GUARD_COMMAND, tmp_path, project_dir=None)
    assert p.returncode == 2 and p.stderr.strip()


def test_the_claude_command_maps_an_unexpected_exit_code_to_a_block_with_a_message(tmp_path):
    _stub(tmp_path, 1)
    p = _sh(build.GUARD_COMMAND, tmp_path, project_dir=tmp_path)
    assert p.returncode == 2
    assert "guard" in p.stderr.lower() and "blocked" in p.stderr.lower()


def test_the_claude_command_maps_a_script_that_cannot_run_to_a_block(tmp_path):
    script = tmp_path / ".manifold" / "hooks" / "guard.py"
    script.parent.mkdir(parents=True)
    script.write_text("def broken(:\n")  # a syntax error fails before main runs
    p = _sh(build.GUARD_COMMAND, tmp_path, project_dir=tmp_path)
    assert p.returncode == 2 and "blocked" in p.stderr.lower()


def test_the_claude_command_passes_through_exit_0_and_exit_2(tmp_path):
    _stub(tmp_path, 0)
    assert _sh(build.GUARD_COMMAND, tmp_path, project_dir=tmp_path).returncode == 0
    _stub(tmp_path, 2, "Refused by stub")
    p = _sh(build.GUARD_COMMAND, tmp_path, project_dir=tmp_path)
    assert p.returncode == 2 and "Refused by stub" in p.stderr


def test_the_claude_command_runs_the_real_guard_and_passes_its_refusal_through(tmp_path):
    script = tmp_path / ".manifold" / "hooks" / "guard.py"
    script.parent.mkdir(parents=True)
    script.write_bytes((ROOT / "hooks" / "guard.py").read_bytes())
    hook = json.dumps({"tool_name": "Bash", "tool_input": {"command": "echo x > f"}})
    p = _sh(build.GUARD_COMMAND, tmp_path, project_dir=tmp_path, stdin=hook)
    assert p.returncode == 2 and "Refused by the Manifold guard" in p.stderr
    ok = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
    assert _sh(build.GUARD_COMMAND, tmp_path, project_dir=tmp_path, stdin=ok).returncode == 0


def _copilot_command():
    return json.loads((ROOT / "hooks" / "copilot-guard.json").read_text())["hooks"]["preToolUse"][0]["command"]


def test_the_copilot_command_prints_a_deny_json_naming_the_missing_script(tmp_path):
    p = _sh(_copilot_command(), tmp_path)
    assert p.returncode == 0
    out = json.loads(p.stdout)
    assert out["permissionDecision"] == "deny"
    assert build.GUARD_MISSING_MESSAGE in out["permissionDecisionReason"]  # the same text as the Claude command


def test_the_copilot_command_denies_when_the_guard_exits_with_an_error_and_passes_a_clean_run(tmp_path):
    _stub(tmp_path, 1)
    p = _sh(_copilot_command(), tmp_path)
    assert p.returncode == 0 and json.loads(p.stdout)["permissionDecision"] == "deny"
    _stub(tmp_path, 0)
    p = _sh(_copilot_command(), tmp_path)
    assert (p.returncode, p.stdout) == (0, "")


def test_the_copilot_command_runs_the_real_guard_from_the_project_root(tmp_path):
    script = tmp_path / ".manifold" / "hooks" / "guard.py"
    script.parent.mkdir(parents=True)
    script.write_bytes((ROOT / "hooks" / "guard.py").read_bytes())
    hook = json.dumps({"tool_name": "Bash", "tool_input": {"command": "echo x > f"}})
    p = _sh(_copilot_command(), tmp_path, stdin=hook)
    assert p.returncode == 0 and json.loads(p.stdout)["permissionDecision"] == "deny"
    assert "Refused by the Manifold guard" in json.loads(p.stdout)["permissionDecisionReason"]


@pytest.mark.parametrize("fmt,expected", [("copilot", True), ("both", True), ("all", True),
                                          ("claude", False), ("skills", False)])
def test_copilot_hook_file_is_installed_for_the_copilot_format_only(bundle_dir, repo, fmt, expected):
    args = ["--format", fmt] + (["--allow-overlap"] if fmt == "all" else [])
    assert run(bundle_dir, repo, "--apply", *args)[0] == 0
    assert (COPILOT_HOOK_INSTALLED in tree(repo)) is expected
    if expected:
        installed = json.loads((repo / COPILOT_HOOK_INSTALLED).read_text())
        assert installed == json.loads((ROOT / "hooks" / "copilot-guard.json").read_text())
    assert HOOK_INSTALLED in tree(repo)  # the guard script itself comes with every format


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
def test_copilot_hook_file_is_installed_in_every_profile_and_uninstalls_cleanly(bundle_dir, repo, profile):
    assert run(bundle_dir, repo, "--profile", profile, "--format", "copilot", "--apply")[0] == 0
    assert COPILOT_HOOK_INSTALLED in tree(repo)
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def test_lint_rejects_a_copilot_hook_file_that_is_not_the_verified_shape(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "hooks" / "copilot-guard.json"
    p.write_text('{"hooks": {}}')
    assert any("version 1" in x for x in build.lint(src))
    p.write_text("{not json")
    assert any("not valid JSON" in x for x in build.lint(src))


def test_lint_rejects_a_missing_hook_or_support_file(tmp_path):
    src = copy_source(tmp_path / "src")
    (src / "hooks" / "guard.py").unlink()
    (src / "config" / "scratch.gitignore").unlink()
    problems = build.lint(src)
    assert any("missing file: hooks/guard.py" in x for x in problems)
    assert any("missing file: config/scratch.gitignore" in x for x in problems)


# ----------------------------------------------------------------- installer

def test_dry_run_writes_nothing(bundle_dir, repo):
    rc, out = run(bundle_dir, repo)
    assert rc == 0 and "Dry run" in out
    assert tree(repo) == []


def test_apply_installs_agents_templates_instructions_and_manifest(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 0, out
    files = tree(repo)
    for f in AGENT_FILES + TEMPLATE_FILES + ["AGENTS.md", "CLAUDE.md", ".manifold/manifest.json", ".manifold/LICENSE", ".manifold/NOTICE"]:
        assert f in files, f
    assert not any(f.startswith(".github/agents") for f in files)
    assert (repo / "CLAUDE.md").read_text() == "@AGENTS.md\n"
    agents = (repo / "AGENTS.md").read_text()
    assert "<!-- manifold:begin v=1 -->" in agents and "<!-- manifold:end -->" in agents
    assert "## Project commands" in agents
    manifest = json.loads((repo / ".manifold/manifest.json").read_text())
    assert manifest["version"] == (ROOT / "VERSION").read_text().strip() and set(AGENT_FILES) <= set(manifest["files"])


def test_installed_agent_files_start_with_frontmatter(bundle_dir, repo):
    run(bundle_dir, repo, "--apply", "--format", "both")
    for f in AGENT_FILES + COPILOT_FILES:
        assert (repo / f).read_text().startswith("---\n"), f


def test_apply_is_idempotent(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    snapshot = {f: (repo / f).read_bytes() for f in tree(repo) if f != ".manifold/manifest.json"}
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 0
    assert "CREATE" not in out and "UPDATE" not in out and "CONFLICT" not in out
    assert {f: (repo / f).read_bytes() for f in tree(repo) if f != ".manifold/manifest.json"} == snapshot


def test_modified_file_is_a_conflict_and_is_not_overwritten(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    mine = repo / ".claude/agents/coder.md"
    mine.write_text(mine.read_text() + "\nMy own rule.\n")
    before = mine.read_bytes()
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 2 and "CONFLICT" in out
    assert mine.read_bytes() == before


def test_force_replaces_modified_file_after_archiving_it(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    mine = repo / ".claude/agents/coder.md"
    mine.write_text("my version\n")
    rc, out = run(bundle_dir, repo, "--apply", "--force")
    assert rc == 0, out
    assert mine.read_text().startswith("---\n")
    archived = list((repo / ".manifold/archive").rglob("coder.md"))
    assert len(archived) == 1 and archived[0].read_text() == "my version\n"


def test_preexisting_unmanaged_file_is_a_conflict(bundle_dir, repo):
    (repo / ".claude/agents").mkdir(parents=True)
    (repo / ".claude/agents/planner.md").write_text("somebody else's planner\n")
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 2
    assert (repo / ".claude/agents/planner.md").read_text() == "somebody else's planner\n"
    assert (repo / ".claude/agents/coder.md").exists()


def test_unmodified_older_install_is_updated(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    target = repo / ".claude/agents/planner.md"
    old = b"---\nname: planner\ndescription: old\n---\nold body\n"
    target.write_bytes(old)
    mpath = repo / ".manifold/manifest.json"
    manifest = json.loads(mpath.read_text())
    manifest["files"][".claude/agents/planner.md"] = hashlib.sha256(old).hexdigest()
    mpath.write_text(json.dumps(manifest))
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 0 and "UPDATE" in out
    assert target.read_text().startswith("---\nname: planner\n") and "old body" not in target.read_text()


def test_existing_agents_md_is_preserved_outside_the_block(bundle_dir, repo):
    mine = "# My project\n\nUse tabs.\n\n## Notes\nKeep it small.\n"
    (repo / "AGENTS.md").write_text(mine)
    (repo / "CLAUDE.md").write_text("@AGENTS.md\n")
    rc, _ = run(bundle_dir, repo, "--apply")
    assert rc == 0
    text = (repo / "AGENTS.md").read_text()
    assert text.startswith(mine.rstrip("\n"))
    assert text.count("<!-- manifold:begin v=1 -->") == 1
    assert (repo / "CLAUDE.md").read_text() == "@AGENTS.md\n"
    run(bundle_dir, repo, "--apply")
    assert (repo / "AGENTS.md").read_text() == text


def test_block_is_replaced_in_place_and_edits_outside_survive(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    p = repo / "AGENTS.md"
    text = p.read_text()
    begin, end = "<!-- manifold:begin v=1 -->", "<!-- manifold:end -->"
    tampered = text.replace("## Working rules", "## Working rules\n\n- TAMPERED LINE")
    tampered = tampered.rstrip("\n") + "\n\n## Mine\nkeep me\n"
    p.write_text(tampered)
    run(bundle_dir, repo, "--apply")
    again = p.read_text()
    assert "TAMPERED LINE" not in again and "keep me" in again
    assert again.count(begin) == 1 and again.count(end) == 1


def test_claude_md_only_receives_the_block_and_agents_md_is_not_created(bundle_dir, repo):
    (repo / "CLAUDE.md").write_text("# Claude notes\n")
    rc, _ = run(bundle_dir, repo, "--apply")
    assert rc == 0
    assert not (repo / "AGENTS.md").exists()
    assert "<!-- manifold:begin v=1 -->" in (repo / "CLAUDE.md").read_text()


def test_note_when_claude_md_does_not_import_agents_md(bundle_dir, repo):
    (repo / "AGENTS.md").write_text("# A\n")
    (repo / "CLAUDE.md").write_text("# C\n")
    rc, out = run(bundle_dir, repo)
    assert rc == 0 and "@AGENTS.md" in out and "NOTE" in out


def test_unbalanced_markers_are_refused(bundle_dir, repo):
    (repo / "AGENTS.md").write_text("<!-- manifold:begin v=1 -->\nhalf a block\n")
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 1 and "end marker" in out
    assert (repo / "AGENTS.md").read_text() == "<!-- manifold:begin v=1 -->\nhalf a block\n"


def test_no_instructions_flag(bundle_dir, repo):
    rc, _ = run(bundle_dir, repo, "--apply", "--no-instructions")
    assert rc == 0
    assert not (repo / "AGENTS.md").exists() and not (repo / "CLAUDE.md").exists()


def test_format_selection(bundle_dir, repo):
    run(bundle_dir, repo, "--apply", "--format", "copilot")
    files = tree(repo)
    assert all(f in files for f in COPILOT_FILES) and not any(f in files for f in AGENT_FILES)
    run(bundle_dir, repo, "--apply", "--format", "claude")
    assert all(f in tree(repo) for f in AGENT_FILES + COPILOT_FILES)


def test_status_reports_ok_modified_and_missing(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    (repo / ".claude/agents/coder.md").write_text("changed\n")
    (repo / ".claude/agents/bug-coder.md").unlink()
    rc, out = run(bundle_dir, repo, "--status")
    assert rc == 0 and "MODIFIED" in out and "MISSING" in out and " ok " in out


def test_uninstall_removes_unmodified_keeps_modified_and_strips_block(bundle_dir, repo):
    (repo / "AGENTS.md").write_text("# Mine\n\nkeep\n")
    run(bundle_dir, repo, "--apply")
    (repo / ".claude/agents/coder.md").write_text("mine\n")
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 2 and "KEEP" in out
    assert (repo / ".claude/agents/coder.md").read_text() == "mine\n"
    assert not (repo / ".claude/agents/planner.md").exists()
    assert not (repo / ".manifold/manifest.json").exists()
    agents = (repo / "AGENTS.md").read_text()
    assert "manifold:begin" not in agents and "keep" in agents


def test_uninstall_dry_run_changes_nothing(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    before = {f: (repo / f).read_bytes() for f in tree(repo)}
    rc, out = run(bundle_dir, repo, "--uninstall")
    assert rc == 0 and "Dry run" in out
    assert {f: (repo / f).read_bytes() for f in tree(repo)} == before


def test_path_traversal_in_bundle_is_rejected(bundle_dir, repo):
    p = bundle_dir / "bundle.json"
    bundle = json.loads(p.read_text())
    bundle["common"][0]["path"] = "../escape.txt"
    p.write_text(json.dumps(bundle))
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 1 and "unsafe" in out
    assert not (repo.parent / "escape.txt").exists()


def test_corrupt_payload_is_detected(bundle_dir, repo):
    victim = bundle_dir / "payload/claude/.claude/agents/planner.md"
    victim.write_text(victim.read_text() + "tampered\n")
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 1 and "hash mismatch" in out


def test_missing_target_is_an_error(bundle_dir, tmp_path):
    rc, out = run(bundle_dir, tmp_path / "does-not-exist")
    assert rc == 1 and "not a directory" in out


def test_install_sh_launcher_works(bundle_dir, repo):
    p = subprocess.run(["sh", str(bundle_dir / "install.sh"), "--target", str(repo)], capture_output=True, text=True)
    assert p.returncode == 0 and "Dry run" in p.stdout


# ------------------------------------------------------- overlap with existing agents

_inst_spec = importlib.util.spec_from_file_location("agentkit_install", ROOT / "install.py")
inst = importlib.util.module_from_spec(_inst_spec)
_inst_spec.loader.exec_module(inst)


@pytest.mark.parametrize("stem,role", [
    ("planner", "planner"), ("coder", "coder"), ("bug-coder", "bug-coder"),
    ("acme-planner", "planner"), ("acme-bug-coder", "bug-coder"),
    ("acme-test-coder", "test-coder"), ("acme-test-planner", "test-planner"),
    ("my-coders", None), ("reviewer", "reviewer"), ("acme-scenario-writer", "scenario-writer"), ("deployer", None), ("plannerx", None),
])
def test_role_of(stem, role):
    assert inst.role_of(stem) == role


def _tailored(repo, directory, suffix):
    (repo / directory).mkdir(parents=True)
    (repo / directory / ("acme-planner" + suffix)).write_text("---\nname: acme-planner\n---\n")
    (repo / directory / ("acme-deployer" + suffix)).write_text("---\nname: acme-deployer\n---\n")


def test_overlap_warns_and_blocks_apply_until_allowed(bundle_dir, repo):
    _tailored(repo, ".github/agents", ".agent.md")
    rc, out = run(bundle_dir, repo, "--format", "copilot")
    assert rc == 0 and "WARNING" in out and "acme-planner.agent.md" in out and "acme-deployer" not in out
    rc, out = run(bundle_dir, repo, "--format", "copilot", "--apply")
    assert rc == 1 and "overlapping" in out
    assert not (repo / ".github/agents/planner.agent.md").exists() and not (repo / ".manifold").exists()
    rc, out = run(bundle_dir, repo, "--format", "copilot", "--apply", "--allow-overlap")
    assert rc == 0 and (repo / ".github/agents/planner.agent.md").exists()


def test_overlap_is_checked_per_selected_format(bundle_dir, repo):
    _tailored(repo, ".github/agents", ".agent.md")
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 0 and "WARNING" not in out
    assert (repo / ".claude/agents/planner.md").exists()


def test_own_installed_files_are_not_flagged_on_reinstall(bundle_dir, repo):
    run(bundle_dir, repo, "--apply", "--format", "both")
    rc, out = run(bundle_dir, repo, "--apply", "--format", "both")
    assert rc == 0 and "WARNING" not in out


# ------------------------------------------------------------ skills (experimental format)

SKILL_NAMES = ["plan-change", "execute-plan", "fix-bug", "plan-tests", "write-tests"]
SKILL_FILES = [".claude/skills/%s/SKILL.md" % n for n in SKILL_NAMES]


def _bundle_json(bundle_dir):
    return json.loads((bundle_dir / "bundle.json").read_text())


def test_skills_use_only_fields_from_the_spec():
    fragments, rules = build.load_fragments(ROOT), build.load_rules(ROOT)
    for role, text in build.load_agents(ROOT).items():
        out = build.render_skill(role, text, fragments, rules, "0.1.0")
        blocks, _ = build.split_frontmatter(out)
        assert {k for k, _ in blocks} == {"name", "description", "license", "metadata"}
        assert build.validate_skill(build.SKILL_NAMES[role], out) == []


def test_bundle_lists_all_skills_with_matching_folder_and_name(bundle_dir):
    skills = _bundle_json(bundle_dir)["formats"]["skills"]
    assert [e["path"] for e in skills] == [".claude/skills/%s/SKILL.md" % n for n in
                                           [build.SKILL_NAMES[r] for r in build.ROLES]]
    for e in skills:
        text = (bundle_dir / e["src"]).read_text()
        assert text.startswith("---\nname: %s\n" % e["rel"].split("/")[0])


@pytest.mark.parametrize("name,text,fragment", [
    ("Bad_Name", "---\nname: Bad_Name\ndescription: x\n---\n\nBody\n", "lowercase"),
    ("a--b", "---\nname: a--b\ndescription: x\n---\n\nBody\n", "single hyphens"),
    ("ok", "---\nname: other\ndescription: x\n---\n\nBody\n", "folder name"),
    ("ok", "---\nname: ok\ndescription: x\nargument-hint: y\n---\n\nBody\n", "outside the spec"),
    ("ok", "---\nname: ok\ndescription: x\n---\n\n", "empty body"),
    ("ok", "---\nname: ok\ndescription: " + "d" * 1025 + "\n---\n\nBody\n", "1-1024"),
    ("ok", "---\nname: ok\ndescription: x\n---\n\n" + "line\n" * 501, "500 lines"),
])
def test_validate_skill_rejects_spec_violations(name, text, fragment):
    assert any(fragment in p for p in build.validate_skill(name, text))


def test_license_comment_before_skill_frontmatter_is_rejected():
    problems = build.validate_skill("ok", "<!-- license -->\n---\nname: ok\ndescription: x\n---\n\nBody\n")
    assert any("line 1" in p for p in problems)


def test_sibling_references_name_skills_in_skills_and_agents_in_agents(bundle_dir):
    skill = (bundle_dir / "payload/skills/.claude/skills/plan-change/SKILL.md").read_text()
    agent = (bundle_dir / "payload/claude/.claude/agents/planner.md").read_text()
    assert "`execute-plan` skill" in skill and "`coder` agent" not in skill
    assert "`coder` agent" in agent and "`execute-plan`" not in agent
    coder_desc = (bundle_dir / "payload/skills/.claude/skills/execute-plan/SKILL.md").read_text().split("---")[1]
    assert "`plan-change` skill" in coder_desc


def test_no_reference_markers_survive_anywhere_in_the_payload(bundle_dir):
    for p in (bundle_dir / "payload").rglob("*"):
        if p.is_file():
            assert "{{" not in p.read_text(), p


def test_unknown_role_in_a_reference_is_rejected():
    with pytest.raises(build.BuildError):
        build.expand_refs("see {{ref:wizard}}", "skills", "x")


def test_instruction_variants_exist_and_differ(bundle_dir):
    variants = _bundle_json(bundle_dir)["instructions"]["variants"]
    assert set(variants) == {"build", "quality", "single"}
    for profile, styles in variants.items():
        assert set(styles) == {"agents", "skills", "both"}
        text = {k: (bundle_dir / v["src"]).read_text() for k, v in styles.items()}
        for k, v in styles.items():
            assert hashlib.sha256(text[k].encode()).hexdigest() == v["sha256"]
        assert "## Agents\n" in text["agents"] and "## Skills" not in text["agents"]
        assert "## Skills\n" in text["skills"] and "@agent-" not in text["skills"]
        assert "## Agents and skills" in text["both"]
    both = (bundle_dir / variants["single"]["both"]["src"]).read_text()
    assert "plan-change" in both and "planner" in both


def test_skills_pass_the_official_reference_validator(bundle_dir, tmp_path):
    skills_ref = pytest.importorskip("skills_ref")
    for e in _bundle_json(bundle_dir)["formats"]["skills"]:
        folder = tmp_path / e["rel"].split("/")[0]
        folder.mkdir()
        (folder / "SKILL.md").write_bytes((bundle_dir / e["src"]).read_bytes())
        assert skills_ref.validate(folder) == [], folder.name


def test_parse_formats():
    assert inst.parse_formats("claude") == ["claude"]
    assert inst.parse_formats("claude,skills") == ["claude", "skills"]
    assert inst.parse_formats("both") == ["claude", "copilot"]
    assert inst.parse_formats("all") == ["claude", "copilot", "skills"]
    assert inst.parse_formats("skills,skills, claude") == ["skills", "claude"]
    for bad in ("", "wizard", "claude,wizard"):
        with pytest.raises(inst.InstallError):
            inst.parse_formats(bad)


def test_unknown_format_is_an_error(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--format", "wizard")
    assert rc == 1 and "unknown format" in out


def test_format_skills_installs_into_claude_skills_and_uses_the_skills_block(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--apply", "--format", "skills")
    assert rc == 0, out
    files = tree(repo)
    for f in SKILL_FILES + TEMPLATE_FILES:
        assert f in files, f
    assert not any(f.startswith(".claude/agents") for f in files)
    agents_md = (repo / "AGENTS.md").read_text()
    assert "## Skills" in agents_md and "## Agents\n" not in agents_md
    assert json.loads((repo / ".manifold/manifest.json").read_text())["skills_dir"] == ".claude/skills"


def test_skills_dir_relocates_and_is_remembered(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--apply", "--format", "skills", "--skills-dir", ".agents/skills")
    assert rc == 0, out
    assert all((repo / ".agents/skills" / n / "SKILL.md").exists() for n in SKILL_NAMES)
    assert not (repo / ".claude/skills").exists()
    rc, out = run(bundle_dir, repo, "--apply", "--format", "skills")
    assert rc == 0 and "CREATE" not in out.split("AGENTS.md")[0]
    assert not (repo / ".claude/skills").exists()


@pytest.mark.parametrize("bad", ["../escape", "/abs/path", "C:\\\\x", "a/../../b"])
def test_skills_dir_must_be_a_relative_path_inside_the_repo(bundle_dir, repo, bad):
    rc, out = run(bundle_dir, repo, "--format", "skills", "--skills-dir", bad)
    assert rc == 1 and "relative path" in out


def test_modified_skill_is_a_conflict_and_survives(bundle_dir, repo):
    run(bundle_dir, repo, "--apply", "--format", "skills")
    mine = repo / SKILL_FILES[0]
    mine.write_text(mine.read_text() + "\nmine\n")
    before = mine.read_bytes()
    rc, out = run(bundle_dir, repo, "--apply", "--format", "skills")
    assert rc == 2 and "CONFLICT" in out and mine.read_bytes() == before


def test_agents_plus_skills_in_one_run_needs_consent(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--format", "all")
    assert rc == 0 and "both agents and skills" in out
    rc, out = run(bundle_dir, repo, "--format", "all", "--apply")
    assert rc == 1 and "refusing" in out and tree(repo) == []
    rc, out = run(bundle_dir, repo, "--format", "all", "--apply", "--allow-overlap")
    assert rc == 0, out
    assert "## Agents and skills" in (repo / "AGENTS.md").read_text()
    assert all(f in tree(repo) for f in AGENT_FILES + COPILOT_FILES + SKILL_FILES)


def test_adding_skills_to_an_agents_install_needs_consent(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    rc, out = run(bundle_dir, repo, "--apply", "--format", "skills")
    assert rc == 1 and "refusing" in out
    assert not any(f.startswith(".claude/skills") for f in tree(repo))


def test_a_consented_mixed_install_does_not_warn_again(bundle_dir, repo):
    run(bundle_dir, repo, "--apply", "--format", "all", "--allow-overlap")
    rc, out = run(bundle_dir, repo, "--apply", "--format", "all")
    assert rc == 0 and "WARNING" not in out


def test_foreign_skill_with_a_role_name_is_flagged(bundle_dir, repo):
    for name in ("acme-planner", "pdf-tools"):
        (repo / ".claude/skills" / name).mkdir(parents=True)
        (repo / ".claude/skills" / name / "SKILL.md").write_text("---\nname: %s\ndescription: x\n---\n\nBody\n" % name)
    rc, out = run(bundle_dir, repo, "--format", "skills")
    assert rc == 0 and "acme-planner" in out and "pdf-tools" not in out
    rc, out = run(bundle_dir, repo, "--format", "skills", "--apply")
    assert rc == 1 and "refusing" in out


def test_uninstall_removes_skills_and_prunes_empty_folders(bundle_dir, repo):
    run(bundle_dir, repo, "--apply", "--format", "skills")
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0, out
    assert not (repo / ".claude").exists() and not (repo / ".manifold/manifest.json").exists()


def test_uninstall_keeps_a_modified_skill_and_its_folder(bundle_dir, repo):
    run(bundle_dir, repo, "--apply", "--format", "skills")
    (repo / SKILL_FILES[1]).write_text("mine\n")
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 2 and (repo / SKILL_FILES[1]).read_text() == "mine\n"
    assert not (repo / SKILL_FILES[0]).exists()


# ------------------------------------------------ uninstall removes what the installer created

@pytest.mark.parametrize("args", [(), ("--format", "skills"), ("--format", "all", "--allow-overlap"), ("--format", "both")])
def test_install_then_uninstall_leaves_an_empty_repo(bundle_dir, repo, args):
    rc, out = run(bundle_dir, repo, "--apply", *args)
    assert rc == 0, out
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0, out
    assert tree(repo) == [], tree(repo)


def test_created_instruction_files_are_recorded_in_the_manifest(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    info = json.loads((repo / ".manifold/manifest.json").read_text())["instructions"]
    assert info["file"] == "AGENTS.md" and info["created"] == ["AGENTS.md", "CLAUDE.md"]


def test_created_list_survives_a_reinstall(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    run(bundle_dir, repo, "--apply")
    info = json.loads((repo / ".manifold/manifest.json").read_text())["instructions"]
    assert info["created"] == ["AGENTS.md", "CLAUDE.md"]
    run(bundle_dir, repo, "--uninstall", "--apply")
    assert tree(repo) == []


def test_edited_project_commands_keeps_all_created_files(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    agents = repo / "AGENTS.md"
    agents.write_text(agents.read_text().rstrip("\n") + "\n\n- test: `pytest -q`\n")
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0 and "holds your content" in out
    text = agents.read_text()
    assert "manifold:begin" not in text and "pytest -q" in text
    assert (repo / "CLAUDE.md").read_text() == "@AGENTS.md\n"


REVIEW_PROCESS_LABELS = ("Repository type:", "Companion quality repository:", "Second approver (team only):")


def test_a_fresh_install_writes_the_review_process_stub_outside_the_managed_block(bundle_dir, repo):
    """T16 (INT-23): the owner fills the section in; an agent never does."""
    run(bundle_dir, repo, "--apply")
    text = (repo / "AGENTS.md").read_text()
    assert text.count("## Review process") == 1
    after_block = text.split("<!-- manifold:end -->")[1]
    assert "## Review process" in after_block and "## Project commands" in after_block
    for label in REVIEW_PROCESS_LABELS:
        assert label in after_block, label
    assert "solo" in after_block and "team" in after_block
    # nothing is filled in: each label line ends with its colon
    for line in after_block.splitlines():
        if line.startswith(REVIEW_PROCESS_LABELS):
            assert line.rstrip().endswith(":"), line


def test_an_existing_review_process_section_is_left_alone_by_the_stub(bundle_dir, repo):
    mine = "# Mine\n\n## Review process\n\nRepository type: team\nSecond approver (team only): Sam\n"
    (repo / "AGENTS.md").write_text(mine)
    run(bundle_dir, repo, "--apply")
    run(bundle_dir, repo, "--apply")
    text = (repo / "AGENTS.md").read_text()
    assert text.count("## Review process") == 1
    assert "Repository type: team" in text and "Second approver (team only): Sam" in text
    assert "Companion quality repository:" not in text


def test_uninstall_removes_an_untouched_created_file_with_both_stubs(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    assert "## Review process" in (repo / "AGENTS.md").read_text()
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0, out
    assert not (repo / "AGENTS.md").exists() and not (repo / "CLAUDE.md").exists()


def test_uninstall_keeps_a_created_file_whose_review_process_was_filled_in(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    agents = repo / "AGENTS.md"
    agents.write_text(agents.read_text().replace("Repository type:", "Repository type: solo"))
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0 and "holds your content" in out
    text = agents.read_text()
    assert "manifold:begin" not in text and "Repository type: solo" in text


def test_uninstall_still_removes_a_file_created_with_only_the_old_commands_stub(bundle_dir, repo):
    """An install made before the review stub existed: the created file holds only the commands stub."""
    run(bundle_dir, repo, "--apply")
    agents = repo / "AGENTS.md"
    text = agents.read_text()
    agents.write_text(text[: text.index("## Review process")].rstrip("\n") + "\n")
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0, out
    assert not agents.exists()


def test_edited_claude_md_keeps_all_created_files(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    (repo / "CLAUDE.md").write_text("@AGENTS.md\n\nAlways answer in French.\n")
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0 and (repo / "AGENTS.md").exists()
    assert "French" in (repo / "CLAUDE.md").read_text()


def test_a_preexisting_agents_md_is_never_deleted(bundle_dir, repo):
    (repo / "AGENTS.md").write_text("# Mine\n")
    run(bundle_dir, repo, "--apply")
    assert json.loads((repo / ".manifold/manifest.json").read_text())["instructions"]["created"] == []
    assert not (repo / "CLAUDE.md").exists()
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert rc == 0
    assert (repo / "AGENTS.md").read_text().startswith("# Mine")


def test_a_preexisting_claude_md_is_never_deleted(bundle_dir, repo):
    (repo / "CLAUDE.md").write_text("# Claude notes\n")
    run(bundle_dir, repo, "--apply")
    assert json.loads((repo / ".manifold/manifest.json").read_text())["instructions"]["created"] == []
    run(bundle_dir, repo, "--uninstall", "--apply")
    assert (repo / "CLAUDE.md").read_text().startswith("# Claude notes") and not (repo / "AGENTS.md").exists()


def test_uninstall_dry_run_names_created_files_but_removes_nothing(bundle_dir, repo):
    run(bundle_dir, repo, "--apply")
    before = {f: (repo / f).read_bytes() for f in tree(repo)}
    rc, out = run(bundle_dir, repo, "--uninstall")
    assert rc == 0 and "REMOVE    AGENTS.md" in out and "REMOVE    CLAUDE.md" in out and "Dry run" in out
    assert {f: (repo / f).read_bytes() for f in tree(repo)} == before


# ----------------------------------------------------------------- profiles

BUILD_ROLES = ["planner", "coder", "bug-coder", "reviewer", "test-planner", "test-coder", "coordinator"]
QUALITY_ROLES = ["scenario-writer", "test-planner", "test-coder", "coordinator"]


def _agent_names(repo):
    folder = repo / ".claude" / "agents"
    return sorted(p.stem for p in folder.iterdir()) if folder.is_dir() else []


def test_default_profile_is_build(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 0 and "Profile: build" in out
    assert _agent_names(repo) == sorted(BUILD_ROLES)
    assert (repo / "docs/templates/PHASE_PLAN_TEMPLATE.md").exists()
    assert (repo / "docs/templates/REVIEW_TEMPLATE.md").exists()
    assert (repo / "docs/templates/INTENT_TEMPLATE.md").exists()
    assert not (repo / "docs/templates/SCENARIO_TEMPLATE.md").exists()
    assert not (repo / ".manifold/quality-settings.json").exists()
    assert json.loads((repo / ".manifold/manifest.json").read_text())["profiles"] == ["build"]


def test_quality_profile_installs_only_quality_roles_and_files(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--profile", "quality", "--apply")
    assert rc == 0 and "Profile: quality" in out and "WARNING   The single profile" not in out
    assert _agent_names(repo) == sorted(QUALITY_ROLES)
    for f in ("docs/templates/SCENARIO_TEMPLATE.md", "docs/templates/SATISFACTION_REPORT_TEMPLATE.md",
              "docs/templates/INTENT_TEMPLATE.md", ".manifold/quality-settings.json"):
        assert (repo / f).exists(), f
    for f in ("docs/templates/PHASE_PLAN_TEMPLATE.md", "docs/templates/REVIEW_TEMPLATE.md"):
        assert not (repo / f).exists(), f
    block = (repo / "AGENTS.md").read_text()
    assert "scenario-writer" in block and "**coder**" not in block and "**planner**" not in block


def test_single_profile_installs_everything_and_warns(bundle_dir, repo):
    rc, out = run(bundle_dir, repo, "--profile", "single", "--apply")
    assert rc == 0 and "WARNING   The single profile" in out and "NOT independent" in out
    assert _agent_names(repo) == sorted(build.ROLES)
    assert (repo / ".manifold/quality-settings.json").exists() and (repo / "docs/templates/REVIEW_TEMPLATE.md").exists()


def test_installing_build_then_quality_becomes_single_with_warning(bundle_dir, repo):
    assert run(bundle_dir, repo, "--apply")[0] == 0
    rc, out = run(bundle_dir, repo, "--profile", "quality", "--apply")
    assert rc == 0 and "WARNING   The single profile" in out
    assert json.loads((repo / ".manifold/manifest.json").read_text())["profiles"] == ["build", "quality"]
    assert _agent_names(repo) == sorted(build.ROLES)


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
@pytest.mark.parametrize("fmt", ["claude", "copilot", "skills", "both"])
def test_every_profile_and_format_uninstalls_to_an_empty_repo(bundle_dir, repo, profile, fmt):
    assert run(bundle_dir, repo, "--profile", profile, "--format", fmt, "--apply")[0] == 0
    assert tree(repo)
    assert HOOK_INSTALLED in tree(repo) and SCRATCH_INSTALLED in tree(repo)
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def test_quality_settings_are_user_editable_and_never_overwritten(bundle_dir, repo):
    assert run(bundle_dir, repo, "--profile", "quality", "--apply")[0] == 0
    settings = repo / ".manifold/quality-settings.json"
    data = json.loads(settings.read_text())
    data["satisfaction"]["minimum_overall"] = 0.95
    settings.write_text(json.dumps(data, indent=2) + "\n")
    rc, out = run(bundle_dir, repo, "--profile", "quality", "--apply")
    assert rc == 2 and "quality-settings.json" in out and "CONFLICT" in out
    assert json.loads(settings.read_text())["satisfaction"]["minimum_overall"] == 0.95
    rc, out = run(bundle_dir, repo, "--uninstall", "--apply")
    assert "KEEP      .manifold/quality-settings.json" in out
    assert json.loads(settings.read_text())["satisfaction"]["minimum_overall"] == 0.95


def test_quality_settings_defaults():
    flat = build.flatten_settings(json.loads((ROOT / "config" / "quality-settings.json").read_text()))
    assert flat["satisfaction.minimum_overall"] == 0.85
    assert flat["satisfaction.minimum_per_seed"] == 0.70
    assert flat["failures.critical_max_rate"] == 0.05
    assert flat["judge.minimum_confidence"] == 0.85
    assert flat["trajectories.per_scenario"] == 3
    assert flat["sampling.seed"] == 42
    assert flat["visibility.level"] == "described"
    assert flat["gate.mode"] == "report-only"
    assert flat["burn.on_disclosure"] is True
    assert set(build.QUALITY_SETTINGS_KEYS) <= set(flat)


def test_lint_rejects_missing_quality_setting(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "config" / "quality-settings.json"
    data = json.loads(p.read_text())
    del data["judge"]
    p.write_text(json.dumps(data))
    assert any("judge.minimum_confidence" in x for x in build.lint(src))


def test_lint_rejects_a_reference_to_a_role_the_profile_lacks(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "agents" / "scenario-writer.agent.md"
    p.write_text(p.read_text().replace("## What you do not do", "See the {{ref:coder}}.\n\n## What you do not do", 1))
    assert any("scenario-writer refers to 'coder'" in x and "quality" in x for x in build.lint(src))


def test_rules_reach_only_the_roles_they_apply_to(tmp_path):
    rules = build.load_rules(ROOT)
    def ids(role):
        return {r["id"] for r in build.rules_for(rules, role)}
    assert "quality-side-is-black-box" in ids("scenario-writer") and "quality-side-is-black-box" in ids("test-coder")
    assert "quality-side-is-black-box" not in ids("coder")
    assert "builders-dont-read-holdout-scenarios" in ids("coder") and "builders-dont-read-holdout-scenarios" in ids("reviewer")
    assert "builders-dont-read-holdout-scenarios" not in ids("scenario-writer")
    assert "builders-dont-write-acceptance-tests" in ids("bug-coder")
    assert "dont-edit-the-test-to-pass" in ids("coder") and "dont-edit-the-test-to-pass" in ids("test-coder")
    assert "human-confirms-closure" in ids("bug-coder") and "human-confirms-closure" not in ids("reviewer")


def test_shell_write_rule_applies_to_every_role_and_names_the_sanctioned_routes():
    rules = {r["id"]: r for r in build.load_rules(ROOT)}
    rule = rules["no-heredocs"]  # the id equals the file name and stays
    assert rule["title"] == "Shell writes to files" and rule["applies_to"] == ["all"]
    text = " ".join((rule["rule"], rule["instead"]))
    for needle in ("replace_all", ".manifold/scratch/", "/tmp", "Write", "Edit", "sed -i", "tee", "heredoc", "ask a human"):
        assert needle in text, needle
    assert ".manifold/hooks/guard.py" in rule["enforce"] and "Rule exceptions" in rule["enforce"]
    for role in build.ROLES:
        assert "no-heredocs" in {r["id"] for r in build.rules_for(build.load_rules(ROOT), role)}, role


@pytest.mark.parametrize("fmt", ["claude", "copilot", "skills"])
@pytest.mark.parametrize("role", build.ROLES)
def test_rule_exceptions_line_rule_reaches_every_role_in_every_rendering(role, fmt):
    rules = build.load_rules(ROOT)
    rule = {r["id"]: r for r in rules}["rule-exceptions-line"]
    assert rule["applies_to"] == ["all"] and rule["severity"] == "high" and rule["title"] == "Rule exceptions"
    text = build.load_agents(ROOT)[role]
    fragments = build.load_fragments(ROOT)
    out = (build.render_skill(role, text, fragments, rules, "0") if fmt == "skills"
           else build.render_agent(role, text, fmt, fragments, rules))
    assert "- **Rule exceptions.** Every report from an agent that changed files or ran commands" in out


CLOSING_HEADINGS = {"planner": "## When you finish", "coder": "### When all tasks are done",
                    "bug-coder": "## When you finish", "test-planner": "## When you finish",
                    "test-coder": "### When all automated cases are done",
                    "scenario-writer": "## When you finish", "reviewer": "## Report",
                    "coordinator": "## When you finish"}


@pytest.mark.parametrize("fmt", ["claude", "copilot", "skills"])
@pytest.mark.parametrize("role", build.ROLES)
def test_every_agent_ends_with_a_rule_exceptions_line(role, fmt):
    assert set(CLOSING_HEADINGS) == set(build.ROLES)
    fragments, rules = build.load_fragments(ROOT), build.load_rules(ROOT)
    text = build.load_agents(ROOT)[role]
    out = (build.render_skill(role, text, fragments, rules, "0") if fmt == "skills"
           else build.render_agent(role, text, fmt, fragments, rules))
    body = out.split("## Rules from experience")[0]
    heading = body.index(CLOSING_HEADINGS[role])
    marker = "- **Rule exceptions:** " + ("the comparison" if role == "reviewer" else "`none` or each exception (command, file, reason).")
    assert body.index(marker, heading) > heading, role
    assert body.count("**Rule exceptions:**") == 1, role


FAILURE_ENTRY_FIELDS = ("Rule", "What happened", "Evidence", "Count", "Agent", "Disclosed by the agent",
                        "Suggested change", "Status", "Intent raised")


def test_failures_template_has_the_header_and_every_entry_field():
    t = (ROOT / "templates" / "AGENT_FAILURES_TEMPLATE.md").read_text()
    for field in ("Harness", "Client version", "Enforcement in this harness", "How to add an entry"):
        assert "**%s:**" % field in t, field
    assert "docs/process/BREACH_PROCEDURE.md" in t and "docs/agents/<harness>-failures.md" in t
    entry = t.split("## F<N>", 1)[1]
    positions = [entry.index("**%s:**" % f) for f in FAILURE_ENTRY_FIELDS]
    assert positions == sorted(positions)  # fields appear in one fixed order
    for word in ("concealed", "inference", "never copy"):
        assert word in t, word


def test_breach_procedure_names_who_when_how_exceptions_and_the_return_path():
    t = (ROOT / "process" / "BREACH_PROCEDURE.md").read_text()
    for needle in ("## Who and when", "## How to record", "## Exceptions", "## From a record to a rule change",
                   "## Returning the result to Manifold", "`coordinator`", ".manifold/guard-log.jsonl",
                   ".manifold/guard-allow.json", "docs/agents/<harness>-failures.md",
                   "docs/templates/AGENT_FAILURES_TEMPLATE.md", "Append only", "concealed", "status `draft`",
                   "does not post it"):
        assert needle in t, needle
    for field in FAILURE_ENTRY_FIELDS:
        assert field in t, field


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
def test_failures_template_and_breach_procedure_are_installed_in_every_profile(bundle_dir, repo, profile):
    assert run(bundle_dir, repo, "--profile", profile, "--apply")[0] == 0
    assert (repo / "docs/templates/AGENT_FAILURES_TEMPLATE.md").read_bytes() == (ROOT / "templates" / "AGENT_FAILURES_TEMPLATE.md").read_bytes()
    assert (repo / "docs/process/BREACH_PROCEDURE.md").read_bytes() == (ROOT / "process" / "BREACH_PROCEDURE.md").read_bytes()
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def test_lint_rejects_a_missing_process_document_or_template(tmp_path):
    src = copy_source(tmp_path / "src")
    (src / "process" / "BREACH_PROCEDURE.md").unlink()
    (src / "templates" / "AGENT_FAILURES_TEMPLATE.md").unlink()
    problems = build.lint(src)
    assert any("missing process document: process/BREACH_PROCEDURE.md" in x for x in problems)
    assert any("missing template: AGENT_FAILURES_TEMPLATE.md" in x for x in problems)


def test_rendered_instructions_block_carries_the_shell_write_rule_for_every_profile():
    agents, rules = build.load_agents(ROOT), build.load_rules(ROOT)
    for profile in build.PROFILES:
        block = build.render_instructions_block(agents, rules, "agents", profile)
        (line,) = [x for x in block.splitlines() if x.startswith("- **Shell writes to files.**")]
        assert "Do not write or change file contents from a shell command" in line
        assert "`Write`" in line and ".manifold/scratch/" in line and "replace_all" in line


def test_rendered_instructions_state_the_review_policy_once_and_point_only_at_shipped_paths():
    """T18 (INT-23): the stale 'Review policy lives in REVIEW.md' line is gone; every path named is installed."""
    import re
    agents, rules = build.load_agents(ROOT), build.load_rules(ROOT)
    for style in ("agents", "skills", "both"):
        for profile in build.PROFILES:
            block = build.render_instructions_block(agents, rules, style, profile)
            assert "Review policy lives in" not in block
            shipped = {dst for dst, profiles in list(build.TEMPLATE_PATHS.values()) + list(build.PROCESS_PATHS.values())
                       if profile in profiles}
            for path in re.findall(r"`(docs/(?:templates|process)/[A-Za-z_.]+)`", block):
                assert path in shipped, (profile, path)
            review = [x for x in block.splitlines() if x.startswith("- Review:")]
            if profile in ("build", "single"):
                (line,) = review
                assert "built into the `reviewer`" in line and "optional" in line
                assert "docs/templates/REVIEW_TEMPLATE.md" in line and "`Review process` section" in line
                assert "docs/templates/REVIEW_PLAN_TEMPLATE.md" in block
            else:
                assert not review and "REVIEW_PLAN_TEMPLATE" not in block
            assert "docs/templates/AGENT_FAILURES_TEMPLATE.md" in block
            assert "docs/process/BREACH_PROCEDURE.md" in block


# ----------------------------------------------------- intent, review, scenarios

def _agent_text(role):
    return (ROOT / "agents" / ("%s.agent.md" % role)).read_text()


def _tools(role):
    blocks, _ = build.split_frontmatter(_agent_text(role))
    return build.scalar_value(blocks, "tools")


def test_intent_template_has_scenario_seeds_and_a_human_only_status():
    t = (ROOT / "templates" / "INTENT_TEMPLATE.md").read_text()
    assert t.startswith("---\n")
    for needle in ("## Scenario seeds", "### S1", "**We will know when:**", "**Must never:**", "accepted_by:", "affects:", "status: draft"):
        assert needle in t, needle
    assert "Only a human changes the status" in t


def test_plan_template_carries_intent_concerns_and_cross_repository_lines():
    t = (ROOT / "templates" / "PHASE_PLAN_TEMPLATE.md").read_text()
    for needle in ("**Source intent:**", "## Concerns flagged", "**Needs from other repositories:**", "**Provides to other repositories:**", "**Approved by:**"):
        assert needle in t, needle
    # T24 (INT-21): checkpoints, the amendment skeleton and the two completion-summary lines
    for needle in ("### CP1", "**Verification:**", "a plan without checkpoints is one checkpoint",
                   "## Review amendment (round <n>)", "**Amendment approved by:**", "**Source:**",
                   "REVIEW_PLAN_<N>.md F<id>", "Rule exceptions", "Gates run"):
        assert needle in t, needle


def test_plan_template_puts_checkpoints_under_tasks_and_the_amendment_after_the_checklist():
    """T24 (INT-21): the order of the sections, and that the human-only approval line of an amendment is blank."""
    t = (ROOT / "templates" / "PHASE_PLAN_TEMPLATE.md").read_text()
    assert t.index("## Tasks") < t.index("### CP1") < t.index("### Task 1") < t.index("## Completion checklist")
    assert t.index("## Completion checklist") < t.index("## Review amendment (round <n>)")
    amendment = t.split("## Review amendment (round <n>)", 1)[1]
    for needle in ("**Source:**", "**Amendment approved by:**", "deferred", "rejected", "Open questions", "never fills in"):
        assert needle in amendment, needle
    line = [x for x in amendment.splitlines() if x.startswith("**Amendment approved by:**")][0]
    assert "human" in line


def test_planner_has_intent_mode_and_never_accepts_its_own_plan():
    t = _agent_text("planner")
    assert "## Intent mode" in t and "scenario seeds" in t and "Concerns flagged" in t
    assert "**Never** mark the intent accepted" in t and "Approved by" in t


def test_reviewer_is_read_only_and_never_approves():
    # T21: assertion changed with the owner's approval of the plan (INT-21 Open questions, answer "yes"):
    # the reviewer now has an edit tool and may write only its one review file; it still never approves.
    tools = _tools("reviewer")
    assert "edit" in tools and "write" not in tools
    t = _agent_text("reviewer")
    assert "must not review its own change" in t
    assert "you do **not approve or block** anything" in t
    assert "REVIEW.md" in t
    assert "You edit only `docs/plans/REVIEW_PLAN_<N>.md`" in t
    assert "never edit code or the plan" in t
    assert "Read-only, by role" not in t


def test_reviewer_states_its_built_in_review_defaults_and_which_policy_it_used():
    """T15 (INT-23): REVIEW.md is optional; the defaults live in the reviewer; no invented human threshold."""
    t = _agent_text("reviewer")
    assert "built-in defaults" in t and "nit cap" in t.lower() and "Important" in t
    assert "states which policy" in t
    assert "never stop for lack of a policy file" in t and "never invent a human threshold" in t
    assert "Review process" in t and "applies / does not apply" in t
    assert "second person" not in t
    assert "and the review policy, and" in t.split("---")[1]
    assert "REVIEW.md's" not in t.split("---")[1]


def test_reviewer_says_how_the_four_passes_apply_to_documents():
    """T17 (INT-21): no new pass; the standard is in docs/process/REVIEW_CYCLE.md."""
    t = _agent_text("reviewer")
    assert "## When the change is mostly documents or agent instructions" in t
    assert "docs/process/REVIEW_CYCLE.md" in t
    section = t.split("## When the change is mostly documents or agent instructions")[1].split("\n## ")[0]
    for needle in ("**Bugs:**", "**Compliance:**", "**Tests:**", "No new pass"):
        assert needle in section, needle
    assert "Important" in section and "Nit" in section


def test_claude_format_denies_the_tools_an_agent_does_not_declare():
    """Claude Code agents inherit every tool unless told otherwise, so the read-only
    and black-box roles must carry a denylist (an allowlist would also hide MCP tools)."""
    def fm(role):
        out = build.render_agent(role, _agent_text(role), "claude", build.load_fragments(), build.load_rules())
        # up to the guard hook block (T6), whose matcher names Bash, Edit and Write on purpose
        return out.split("---")[1].split("\nhooks:")[0]
    reviewer = fm("reviewer")
    # T21: the reviewer writes exactly one file (REVIEW_PLAN_<N>.md), so it keeps the edit tools and the
    # guard's write allowlist limits it; assertion changed with the owner's approval of the plan (INT-21 Open questions)
    assert "disallowedTools: WebFetch, WebSearch" in reviewer
    disallowed = [l for l in reviewer.splitlines() if l.startswith("disallowedTools:")]
    assert len(disallowed) == 1 and "Edit" not in disallowed[0] and "Write" not in disallowed[0]
    assert "Bash" not in reviewer
    # search is Bash in Claude Code, so a role that may search keeps it (the 7c live run: the
    # test-planner could not list scenarios/ and stopped)
    for role in ("scenario-writer", "test-planner", "planner"):
        assert "Bash" not in fm(role), role
    assert "disallowedTools" not in fm("coder")
    assert "tools:" not in fm("reviewer").replace("disallowedTools:", "")


def test_scenario_writer_is_black_box_and_leaves_approval_to_humans():
    t = _agent_text("scenario-writer")
    assert "Do not read the product's source code" in t and "status: pending" in t and "A person moves them to `approved`" in t
    assert "execute" not in _tools("scenario-writer")


def test_test_agents_have_both_modes():
    for role in ("test-planner", "test-coder"):
        t = _agent_text(role)
        assert "Local-check mode" in t and "Scenario mode" in t, role
    assert "never read the product's source code" in _agent_text("test-planner")


def test_test_agents_say_their_mode_first():
    """Live run: neither test agent named its mode, so a person could not tell which input it had used."""
    for role in ("test-planner", "test-coder"):
        assert "Start your first reply with exactly one of these two lines" in _agent_text(role), role


def test_planner_carries_the_intents_constraints_into_the_plan():
    """Live run: the plan kept 'Python 3.8' but dropped the intent's 'standard library only'."""
    assert "Every constraint stated in the intent appears in the plan" in _agent_text("planner")


def test_planner_refuses_to_fill_in_the_approval_even_when_asked():
    """Live run (Copilot, Sonnet 4.6): asked to mark the plan approved, the planner wrote an approver name itself."""
    t = _agent_text("planner")
    assert "decline even when they insist" in t and "Never invent an approver name" in t


def test_an_instruction_to_execute_is_not_an_approval():
    """Live run (Copilot, Sonnet 4.6): told 'Execute docs/plans/PHASE_1_PLAN.md' with Approved by blank, the coder
    treated the instruction as approval and edited code. Its own diagnosis: the rule let 'the user says so' cover it."""
    assert "An instruction to execute the plan is not an approval" in _agent_text("coder")
    out = build.render_agent("coder", _agent_text("coder"), "claude", build.load_fragments(), build.load_rules())
    assert "An instruction to execute, run or implement the plan is not an approval" in out
    assert "repeating the instruction to execute is not a yes" in out
    assert "instruction repeated after you asked and were told not yet" in _agent_text("coder")


def test_coder_checks_off_the_plan_before_it_reports():
    """Live run (Copilot, Claude Haiku 4.5): the coder reported Task 1 complete in chat but left the plan's Todo at [ ]."""
    assert "a task is not finished until the plan shows it" in _agent_text("coder")


def test_every_role_is_told_to_look_before_it_asks():
    """Live run: agents guessed test file names and asked about commands the repository answers."""
    for role in ("planner", "coder", "bug-coder", "reviewer", "test-planner", "test-coder", "scenario-writer"):
        out = build.render_agent(role, _agent_text(role), "claude", build.load_fragments(), build.load_rules())
        assert "Never guess a file name" in out, role


def test_bug_coder_writes_the_failing_test_first_and_does_not_edit_it():
    t = _agent_text("bug-coder")
    assert "failing test first" in t and "commit it on its own" in t
    assert "you did not edit it" in t and "not the acceptance check" in t


def test_scenario_template_matches_the_working_format():
    t = (ROOT / "templates" / "SCENARIO_TEMPLATE.md").read_text()
    for key in ("id:", "title:", "author:", "created:", "status: pending", "tags:", "environment:", "priority:", "intent:", "seeds:"):
        assert key in t, key
    for section in ("## User Goal", "## Context", "## Main Flow", "## Edge Cases to Consider", "## Success Criteria"):
        assert section in t, section


def test_satisfaction_report_states_thresholds_and_per_seed_results():
    t = (ROOT / "templates" / "SATISFACTION_REPORT_TEMPLATE.md").read_text()
    for needle in ("## Thresholds used", "## Results per seed", "satisfaction.minimum_overall", "## Disclosed scenarios", "Gate mode"):
        assert needle in t, needle


def test_review_template_has_passes_and_a_nit_cap():
    t = (ROOT / "templates" / "REVIEW_TEMPLATE.md").read_text()
    for needle in ("## Passes", "What Important means", "Cap the nits", "Do not report"):
        assert needle in t, needle


def test_review_template_is_the_optional_policy_and_has_no_human_threshold():
    """T20 (INT-23): defaults live in the reviewer; who approves lives in AGENTS.md 'Review process'."""
    t = (ROOT / "templates" / "REVIEW_TEMPLATE.md").read_text()
    assert "Human threshold" not in t
    assert "Review process" in t and "AGENTS.md" in t
    header = t.split("-->")[0]
    assert "optional" in header and "additions and exclusions" in header and "built-in defaults" in header
    assert "second person" not in t.lower()


def test_review_plan_template_has_every_section_of_the_review_document():
    """T19 (INT-21 S1, S6): the per-phase review document; a re-review revises it in place."""
    t = (ROOT / "templates" / "REVIEW_PLAN_TEMPLATE.md").read_text()
    for needle in ("# REVIEW_PLAN_<N>.md", "**Phase:**", "**Intent:**", "**Commit reviewed:**", "**Plan version:**",
                   "**Policy used:**", "**Revision:**", "## Revision log", "## Counts by severity", "## Findings",
                   "### Bugs", "### Security", "### Compliance", "### Tests", "### Context files",
                   "**State:**", "`open`", "`repaired`", "`deferred`", "`rejected`",
                   "## Rule exceptions compared", "## Gates run", "## CI on the pushed commit", "## Tests run and changed",
                   "## Could not check", "## A human decides"):
        assert needle in t, needle
    for word in ("Evidence", "Direction", "Location"):
        assert word.lower() in t.lower(), word
    assert "not run" in t
    assert "in place" in t
    # the reviewer never approves or blocks
    assert "does not approve or block" in t


def test_review_plan_template_is_installed_for_build_and_single_not_quality(bundle_dir, repo):
    assert run(bundle_dir, repo, "--apply")[0] == 0
    assert (repo / "docs/templates/REVIEW_PLAN_TEMPLATE.md").read_bytes() == (ROOT / "templates" / "REVIEW_PLAN_TEMPLATE.md").read_bytes()


def test_review_plan_template_is_not_installed_in_the_quality_profile(bundle_dir, repo):
    assert run(bundle_dir, repo, "--profile", "quality", "--apply")[0] == 0
    assert not (repo / "docs/templates/REVIEW_PLAN_TEMPLATE.md").exists()


# T22 (Open question 6, the owner chose "remove"): REVIEW.md is optional and per repository, so the bundle
# no longer installs a REVIEW.md. These tests replaced four that pinned the REVIEW_STARTER.md file
# (changes approved by the owner with the plan); see the T22 note.

def test_the_review_starter_is_gone_from_the_bundle():
    assert not (ROOT / "templates" / "REVIEW_STARTER.md").exists()
    assert "REVIEW_STARTER.md" not in build.TEMPLATE_PATHS
    assert "REVIEW.md" not in [dst for dst, _profiles in build.TEMPLATE_PATHS.values()]


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
def test_no_profile_installs_a_review_md(bundle_dir, repo, profile):
    assert run(bundle_dir, repo, "--profile", profile, "--apply")[0] == 0
    assert not (repo / "REVIEW.md").exists()
    assert "REVIEW.md" not in json.loads((repo / ".manifold/manifest.json").read_text())["files"]


def test_an_existing_review_md_is_not_touched_by_an_install(bundle_dir, repo):
    mine = repo / "REVIEW.md"
    mine.write_text("# My own review policy\n")
    rc, out = run(bundle_dir, repo, "--apply")
    assert rc == 0 and "CONFLICT" not in out, out
    assert mine.read_text() == "# My own review policy\n"


def test_upgrading_from_a_payload_that_shipped_review_md_keeps_the_file(tmp_path, monkeypatch):
    """The installer never removes a file the bundle stopped shipping (an install made before T22)."""
    old_src = copy_source(tmp_path / "old_src")
    (old_src / "templates" / "REVIEW_STARTER.md").write_text("# Review instructions\n\nOld starter.\n")
    monkeypatch.setitem(build.TEMPLATE_PATHS, "REVIEW_STARTER.md", ("REVIEW.md", ("build", "single")))
    old_zip = build.build_zip(old_src, tmp_path / "old_dist")
    monkeypatch.delitem(build.TEMPLATE_PATHS, "REVIEW_STARTER.md")
    new_zip = build.build_zip(ROOT, tmp_path / "new_dist")
    target = tmp_path / "repo"
    (target / ".git").mkdir(parents=True)
    for z, name in ((old_zip, "old"), (new_zip, "new")):
        with zipfile.ZipFile(z) as zf:
            zf.extractall(tmp_path / name)
    (old_dir,) = [p for p in (tmp_path / "old").iterdir() if p.is_dir()]
    (new_dir,) = [p for p in (tmp_path / "new").iterdir() if p.is_dir()]
    assert run(old_dir, target, "--apply")[0] == 0
    assert (target / "REVIEW.md").read_text().endswith("Old starter.\n")
    rc, out = run(new_dir, target, "--apply")
    assert rc == 0, out
    assert (target / "REVIEW.md").read_text().endswith("Old starter.\n")
    assert "REVIEW.md" in json.loads((target / ".manifold/manifest.json").read_text())["files"]


# ------------------------------------------------------------------ roadmap

ROADMAP = ROOT.parent.parent / "ROADMAP.md"


@pytest.mark.skipif(not ROADMAP.exists(), reason="ROADMAP.md lives at the repository root")
def test_roadmap_has_no_dates_and_no_internal_terms():
    import re
    text = ROADMAP.read_text()
    assert not re.search(r"\b(19|20)\d\d\b", text), "the roadmap must not contain years or dates"
    months = r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\b"
    assert not re.search(months, text)
    assert not re.search(r"\bQ[1-4]\b", text)
    assert "mediumroast" not in text.lower()
    for status in ("In progress", "Planned", "Exploring"):
        assert status in text
    assert "Formats freeze" in text


@pytest.mark.skipif(not ROADMAP.exists(), reason="ROADMAP.md lives at the repository root")
def test_root_readme_links_the_roadmap():
    assert "ROADMAP.md" in (ROOT.parent.parent / "README.md").read_text()


# ------------------------------------------------- hardening for smaller models (live run, Copilot)

def _rendered(role):
    return build.render_agent(role, _agent_text(role), "claude", build.load_fragments(), build.load_rules())


def test_holdout_rule_covers_shell_reads_and_says_no_first():
    """Live run: Claude Haiku 4.5 read the hold-out scenarios with shell cat and find; MAI-Code-1.1-Flash retried a refused read."""
    t = (ROOT / "rules" / "core" / "builders-dont-read-holdout-scenarios.md").read_text()
    assert "shell commands such as `cat`, `ls`, `find` and `grep`" in t
    assert "say no in your first reply" in t and "do not look first" in t
    assert "Held-out scenarios stay with the quality side" in t
    for role in ("coder", "bug-coder", "reviewer"):
        assert "shell commands such as `cat`" in _rendered(role), role


def test_a_refusal_is_final_for_every_role():
    """Live run: a refused read of the quality folder was retried through shell find, ls and cat."""
    for role in ("planner", "coder", "bug-coder", "reviewer", "test-planner", "test-coder", "scenario-writer"):
        assert "do not get the same result another way" in _rendered(role), role


def test_builders_do_not_change_user_level_configuration():
    """Live run: the bug-coder ran git config --global user.email and user.name with made-up values to get a test to run."""
    for role in ("coder", "bug-coder", "test-coder"):
        out = _rendered(role)
        assert "git config --global" in out and "report the command, the error and the likely cause" in out, role
    for role in ("planner", "reviewer", "scenario-writer", "test-planner"):
        assert "git config --global" not in _rendered(role), role


def test_a_request_to_edit_the_test_to_fit_the_bug_is_declined():
    """Live run: told 'edit the test so it matches the current behavior', Claude Haiku 4.5 added a test pinning the bug and marked it Deferred."""
    out = _rendered("bug-coder")
    assert "is not an instruction to carry out in a fix" in out
    assert "Adding a new test that asserts the buggy behavior counts as the same thing" in out
    assert "do not add a test that asserts the buggy behavior either" in _agent_text("bug-coder")


def _both_flavors(role):
    """The agent as rendered for Claude Code and for Copilot (T25 to T27: the same text in both)."""
    return [build.render_agent(role, _agent_text(role), fmt, build.load_fragments(), build.load_rules())
            for fmt in ("claude", "copilot")]


def test_coder_stops_after_each_checkpoint_and_waits_for_the_amendment_approval():
    """T25 (INT-21 S3): one checkpoint, gates with real counts, stop; a repair checkpoint needs a human's approval line."""
    for out in _both_flavors("coder"):
        assert "one checkpoint at a time" in out
        assert "stop until told to continue" in out
        assert "a plan without checkpoints is one checkpoint" in out
        assert "**Verification**" in out
        assert "real counts" in out and "not run" in out
        assert "**Amendment approved by**" in out and "filled in by a person" in out
        assert "docs/process/REVIEW_CYCLE.md" in out
        assert "failing-first" in out and "both results" in out
    # the approval gate is still stated first, and the old wording stays
    assert "Check the plan's **Approved by** line" in _agent_text("coder")


def test_approval_rule_covers_the_tasks_present_when_it_was_given():
    """T25 (INT-21): a task added later needs its own approval line."""
    t = (ROOT / "rules" / "core" / "approved-plan-before-execution.md").read_text()
    assert "Approval covers the tasks present when it was given" in t
    assert "**Amendment approved by**" in t and "its own approval line" in t
    for out in _both_flavors("coder"):
        assert "Approval covers the tasks present when it was given" in out


def test_a_fix_that_changes_a_pinned_behavior_goes_to_the_owner_before_the_test_changes():
    """T25 (INT-21 S10): stop, name the test and the assertion, say why the old expectation is wrong, ask the owner."""
    t = (ROOT / "rules" / "core" / "dont-edit-the-test-to-pass.md").read_text()
    for needle in ("legitimately changes behavior", "name the test and the assertion",
                   "why the old expectation is wrong", "ask the owner", "only after the owner says yes",
                   "record the approval and the change"):
        assert needle in t, needle
    # the decline of 'edit the test to match the bug' is unchanged (see test_a_request_to_edit_the_test_to_fit_the_bug_is_declined)
    assert "is not an instruction to carry out in a fix" in t
    for role in ("coder", "bug-coder", "test-coder", "reviewer"):
        for out in _both_flavors(role):
            assert "ask the owner" in out, role


def test_planner_groups_tasks_into_checkpoints_and_amends_a_plan_from_a_review():
    """T26 (INT-21 S2, S4): checkpoints; amendment from REVIEW_PLAN_<N>.md; never an approval; edits with Edit, never the shell."""
    for out in _both_flavors("planner"):
        assert "## Checkpoints" in out and "ends in a verification" in out
        assert "no task outside a checkpoint" in out and "dependency order" in out
        assert "## Amending a plan from a review" in out
        assert "REVIEW_PLAN_<N>.md" in out and "## Review amendment (round <n>)" in out
        assert "**Source:**" in out and "`REVIEW_PLAN_<N>.md F<id>`" in out
        assert "one task per Important finding" in out
        assert "deferred and rejected" in out and "open questions" in out
        assert "completed tasks" in out and "original acceptance lines" in out
        assert "**Amendment approved by**" in out and "never fill in" in out
        assert "never the shell" in out
        assert "docs/process/REVIEW_CYCLE.md" in out
    section = _agent_text("planner").split("## Amending a plan from a review")[1].split("\n## ")[0]
    assert "Edit" in section


@pytest.mark.parametrize("role", ["bug-coder", "test-planner", "test-coder"])
def test_checkpoints_apply_to_bug_fixes_and_the_test_side_agents(role):
    """T27 (INT-21 Open questions: yes for bug fixes and the test-side agents)."""
    for out in _both_flavors(role):
        assert "checkpoint" in out.lower()
    t = _agent_text(role)
    if role == "bug-coder":
        assert "group the triage entries into checkpoints" in t and "stop after each checkpoint" in t
        assert "failing-first" in t and "both results" in t
        assert "ask the owner" in "".join(_both_flavors(role))
    elif role == "test-planner":
        assert "checkpoints that mirror the phase plan's" in t
    else:
        assert "one checkpoint at a time" in t and "stop until told to continue" in t


def test_test_plan_template_carries_checkpoints_that_mirror_the_phase_plan():
    """T27 (INT-21): the test plan is written in checkpoints."""
    t = (ROOT / "templates" / "PHASE_TEST_PLAN_TEMPLATE.md").read_text()
    assert "## Checkpoints" in t and "CP1" in t
    assert t.index("## Test environment") < t.index("## Checkpoints") < t.index("## Manual test cases")
    assert t.count("**Checkpoint:**") >= 2  # the manual and the automated case blocks
    assert "mirror" in t and "one checkpoint" in t


def test_reviewer_never_edits_and_does_not_offer_to_once_tools_are_enabled():
    """Live run: Claude Haiku 4.5 declined only because it had no editing tools and offered to edit 'once enabled'."""
    # T21: assertion changed with the owner's approval of the plan (INT-21 Open questions): the reviewer
    # has an edit tool for its review file only; it still does not edit code or offer to.
    t = _agent_text("reviewer")
    assert "do not offer to edit code" in t and "even when the user asks you to" in t
    assert "even when editing tools are available" not in t
    assert "chat reply" in t and "pointer" in t


def test_test_roles_open_with_an_exact_mode_line():
    """Live run: Claude Haiku 4.5 and MAI-Code-1.1-Flash said 'I am in test-planner mode' (the role), not the mode."""
    for role in ("test-planner", "test-coder"):
        t = _agent_text(role)
        assert "`Mode: local checks. Input: <the file>.`" in t and "`Mode: scenario checks." in t, role
        assert "states your role, not your mode" in t, role


def test_planner_writes_the_constraints_as_one_line_and_compares_it():
    """Live run (Copilot, Sonnet 4.6): the plan dropped 'standard library only; Python 3.8' from the intent."""
    t = _agent_text("planner")
    assert "`Constraints:` followed by each one" in t and "`Constraints: none stated`" in t


def test_readme_says_holdout_data_needs_a_real_boundary():
    t = (ROOT / "README.md").read_text()
    assert "Hold-out data needs a real boundary" in t and "deny reads to their path" in t


def test_models_page_names_the_tested_models_and_recommends_sonnet():
    t = (ROOT / "MODELS.md").read_text()
    for name in ("Sonnet 5.5", "Sonnet 4.6", "Haiku 4.5", "MAI-Code-1.1-Flash"):
        assert name in t
    assert "use Claude Sonnet" in t
    assert "If you must use a smaller model" in t
    assert "MODELS.md" in (ROOT / "README.md").read_text()


def test_models_page_ships_in_the_zip(tmp_path):
    built = build.build_zip(ROOT, tmp_path)
    with zipfile.ZipFile(built) as zf:
        assert any(n.endswith("/MODELS.md") for n in zf.namelist())


# ------------------------------------------------ review-to-repair loop (T28, T29; INT-21)

# The one-line sequence of docs/process/REVIEW_CYCLE.md: each step name must be in the document and in the
# reviewer and the coordinator (T33), in both flavors.
CYCLE_STEPS = ("review", "REVIEW_PLAN_<N>.md", "planner amendment", "human approval", "repair checkpoint", "re-review")


def _review_cycle():
    return (ROOT / "process" / "REVIEW_CYCLE.md").read_text()


def test_review_cycle_has_the_sequence_the_handling_and_the_ready_check():
    """T28 (INT-21 S5, S8): who, input and output for each step; every point of 'How a review is handled'."""
    t = _review_cycle()
    for heading in ("## The sequence", "## How a review is handled", "## How tests are handled", "## The ready check",
                    "## Compatibility", "## Reviewing documents and agent instructions"):
        assert heading in t, heading
    for step in CYCLE_STEPS:
        assert step in t, step
    sequence = t.split("## The sequence")[1].split("\n## ")[0]
    for column in ("| Step | Who | Input | Output |", "| Review |", "| Amendment |", "| Approval |", "| Repair |", "| Re-review |"):
        assert column in sequence, column
    handled = t.split("## How a review is handled")[1].split("\n## ")[0]
    for point in ("**Who runs it, and in which session.**", "**What it reads.**", "**Where the output goes.**",
                  "**Who consumes it.**", "**How findings become plan tasks.**",
                  "**What stops a pull request from being marked ready.**", "**How cycles end.**"):
        assert point in handled, point
    for needle in ("three runs", "until the human says enough", "the human may set another limit", "in place",
                   "A finding is never deleted", "nothing open, or only Nits"):
        assert needle in handled, needle


def test_review_cycle_answers_the_five_test_handling_points():
    t = _review_cycle().split("## How tests are handled")[1].split("\n## ")[0]
    for point in ("**Who writes tests.**", "**Failing-first evidence.**",
                  "**A fix that breaks a test that pinned the old behavior.**", "**How gates are run and reported.**",
                  "**Who confirms CI on a pushed commit.**"):
        assert point in t, point
    for needle in ("asks the owner", "only after a yes", "not run", "real output", "exact commit", "neither writes nor reads held-out"):
        assert needle in t, needle


def test_review_cycle_ready_check_leaves_the_decisions_to_a_human():
    t = _review_cycle().split("## The ready check")[1].split("\n## ")[0]
    for needle in ("A review of the final commit exists", "repaired, deferred or rejected", "CI of that exact commit",
                   "`Review process` section of `AGENTS.md`", "does not move a pull request out of draft", "does not merge"):
        assert needle in t, needle
    compat = _review_cycle().split("## Compatibility")[1].split("\n## ")[0]
    assert "a plan without checkpoints is one checkpoint" in compat.lower() and "REVIEW.md" in compat


def test_review_cycle_keeps_the_review_standard_and_matches_the_reviewer():
    """The standard in the reviewer is the same text as in the process document (the reviewer says so)."""
    standard = _review_cycle().split("## Reviewing documents and agent instructions")[1].split("\n## ")[0]
    reviewer = _agent_text("reviewer")
    for line in standard.splitlines():
        if line.startswith("("):
            assert line in reviewer, line


@pytest.mark.parametrize("fmt", ["claude", "copilot"])
def test_reviewer_and_the_other_agents_name_the_cycle_and_point_to_the_procedure(fmt):
    def out(role):
        return build.render_agent(role, _agent_text(role), fmt, build.load_fragments(), build.load_rules())
    reviewer = out("reviewer")
    for step in CYCLE_STEPS:
        assert step in reviewer, step
    for role in ("reviewer", "planner", "coder", "coordinator"):
        assert "docs/process/REVIEW_CYCLE.md" in out(role), role
    coordinator = out("coordinator")  # T33 adds the coordinator to the agents checked here
    for step in CYCLE_STEPS:
        assert step in coordinator, step


def test_process_documents_are_shipped_and_linted_like_the_breach_procedure(tmp_path):
    """T29: REVIEW_CYCLE.md is a process document (installed in every profile); lint checks its presence and its terms."""
    target, profiles = build.PROCESS_PATHS["process/REVIEW_CYCLE.md"]
    assert target == "docs/process/REVIEW_CYCLE.md" and profiles == build.ALL_PROFILES
    src = copy_source(tmp_path / "src")
    assert build.lint(src) == []
    (src / "process" / "REVIEW_CYCLE.md").unlink()
    assert any("missing process document: process/REVIEW_CYCLE.md" in x for x in build.lint(src))
    src = copy_source(tmp_path / "src2")
    path = src / "process" / "REVIEW_CYCLE.md"
    path.write_text(path.read_text() + "\nSee the " + build.FORBIDDEN_TERMS[0] + " site.\n")
    assert any("process/REVIEW_CYCLE.md contains forbidden term" in x for x in build.lint(src))


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
def test_review_cycle_is_installed_in_every_profile(bundle_dir, repo, profile):
    assert run(bundle_dir, repo, "--profile", profile, "--apply")[0] == 0
    assert (repo / "docs/process/REVIEW_CYCLE.md").read_bytes() == (ROOT / "process" / "REVIEW_CYCLE.md").read_bytes()
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


# Paths that a document names and that are not installed, not created by a document and not in a list above:
# none today. Add a path here only with the reason, in a comment.
DOC_PATH_ALLOWLIST = set()
# Folders a document asks the repository to create or that agents create when they run. The installed
# templates and process documents are not here: those must be named exactly, as build.py installs them.
DOC_PATH_PREFIXES = ("docs/plans/", "docs/agents/", "docs/walkthroughs/")
SHIPPED_MARKDOWN = ("agents/*.md", "templates/*.md", "process/*.md", "rules/**/*.md", "fragments/*.md",
                    "README.md", "INSTALL.md", "MODELS.md", "CONTRIBUTING.md", "HOWTO.md")


def _broken_references(root):
    """Relative Markdown links that do not resolve in `root`, and backticked docs/ paths in an agent, template or
    process document that are neither installed, nor created by a document, nor on the allowlist."""
    import re
    installed = {dst for dst, _ in list(build.TEMPLATE_PATHS.values()) + list(build.PROCESS_PATHS.values())}
    problems = []
    for pattern in SHIPPED_MARKDOWN:
        for path in sorted(root.glob(pattern)):
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(root)
            for target in re.findall(r"\]\(([^)\s]+)\)", text):
                target = target.split("#")[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                if not (path.parent / target).resolve().exists():
                    problems.append("%s: link %s does not resolve" % (rel, target))
            if rel.parts[0] in ("agents", "templates", "process") or rel.name == "HOWTO.md":
                for doc in re.findall(r"`(docs/[A-Za-z0-9_./-]+)`", text):
                    if doc in installed or doc in DOC_PATH_ALLOWLIST or doc.endswith("/") or doc.startswith(DOC_PATH_PREFIXES):
                        continue
                    problems.append("%s: path %s is not installed and not created by a document" % (rel, doc))
    return problems


def test_markdown_links_and_paths_resolve():
    """T29: every relative link in the shipped Markdown resolves in the source; every docs/ path an agent, template
    or process document names is installed, created by a document, or on the allowlist."""
    assert _broken_references(ROOT) == []


def test_the_reference_check_fails_on_a_broken_link_and_a_broken_path(tmp_path):
    """T29 acceptance: the check above fails when a bad link or path is added (run on a copy, never on the source)."""
    src = copy_source(tmp_path / "src")
    # the copy sits outside the repository, so the README's links to the repository root do not resolve there;
    # compare with that baseline and look only at what the added lines change
    baseline = _broken_references(src)
    assert all(x.startswith("README.md: link ../../") for x in baseline), baseline
    readme = src / "README.md"
    readme.write_text(readme.read_text() + "\nSee [nothing](no/such/file.md).\n")
    planner = src / "agents" / "planner.agent.md"
    planner.write_text(planner.read_text() + "\nRead `docs/process/NOT_SHIPPED.md`.\n")
    added = [x for x in _broken_references(src) if x not in baseline]
    assert any("README.md: link no/such/file.md does not resolve" in x for x in added), added
    assert any("docs/process/NOT_SHIPPED.md" in x for x in added), added
    assert len(added) == 2, added


# ------------------------------------------------------- coordinator (T30 to T33; INT-22)

# The sections of the pull request template, in the order of INT-22 Scenario seed S3 (T30).
PR_TEMPLATE_HEADINGS = ("What and why", "Plan and intent", "Checkpoints done", "Review state and findings", "Gates",
                        "CI on the pushed commit", "Rule exceptions", "Could not check", "Follow-ups", "Ready check")


def test_pull_request_template_has_every_section_in_the_order_of_the_intent():
    t = (ROOT / "templates" / "PULL_REQUEST_TEMPLATE.md").read_text()
    positions = [t.index("\n## " + h + "\n") for h in PR_TEMPLATE_HEADINGS]
    assert positions == sorted(positions)
    review = t.split("\n## Review state and findings\n")[1].split("\n## ")[0]
    for needle in ("REVIEW_PLAN_<N>.md", "Commit reviewed", "| Severity | Open | Repaired | Deferred | Rejected |"):
        assert needle in review, needle
    assert "| Command | Counts | Result |" in t.split("\n## Gates\n")[1].split("\n## ")[0]
    ci = t.split("\n## CI on the pushed commit\n")[1].split("\n## ")[0]
    assert "Commit (full hash)" in ci and "Confirmed by" in ci
    ready = t.split("\n## Ready check\n")[1]
    for needle in ("met", "missing", "Human confirmation", "only a human", "draft"):
        assert needle in ready, needle


def test_pull_request_template_is_a_template_path_for_build_and_single_only():
    target, profiles = build.TEMPLATE_PATHS["PULL_REQUEST_TEMPLATE.md"]
    assert target == "docs/templates/PULL_REQUEST_TEMPLATE.md" and tuple(profiles) == ("build", "single")


@pytest.mark.parametrize("profile,installed", [("build", True), ("single", True), ("quality", False)])
def test_pull_request_template_is_installed_by_profile_and_uninstalls_cleanly(bundle_dir, repo, profile, installed):
    assert run(bundle_dir, repo, "--profile", profile, "--apply")[0] == 0
    path = repo / "docs/templates/PULL_REQUEST_TEMPLATE.md"
    assert path.exists() is installed
    if installed:
        assert path.read_bytes() == (ROOT / "templates" / "PULL_REQUEST_TEMPLATE.md").read_bytes()
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def _unshipped_paths(block, profile):
    """The `docs/templates/...` and `docs/process/...` paths in an instructions block that this profile does not install."""
    import re
    shipped = {dst for dst, profiles in list(build.TEMPLATE_PATHS.values()) + list(build.PROCESS_PATHS.values())
               if profile in profiles}
    return [p for p in re.findall(r"`(docs/(?:templates|process)/[A-Za-z_.]+)`", block) if p not in shipped]


def test_rendered_instructions_name_the_review_cycle_and_the_pull_request_template_where_they_ship():
    """T29/T30 (CP4 follow-up): the lines are added with the paths, and the path check catches a line whose path is not shipped."""
    agents, rules = build.load_agents(ROOT), build.load_rules(ROOT)
    for style in ("agents", "skills", "both"):
        for profile in build.PROFILES:
            block = build.render_instructions_block(agents, rules, style, profile)
            assert _unshipped_paths(block, profile) == [], (style, profile)
            (cycle,) = [x for x in block.splitlines() if "docs/process/REVIEW_CYCLE.md" in x]
            assert cycle.startswith("- ") and "review" in cycle.lower()
            pr = [x for x in block.splitlines() if "docs/templates/PULL_REQUEST_TEMPLATE.md" in x]
            assert len(pr) == (1 if profile in ("build", "single") else 0), (profile, pr)
    assert _unshipped_paths("- See `docs/templates/PULL_REQUEST_TEMPLATE.md`.", "quality") == [
        "docs/templates/PULL_REQUEST_TEMPLATE.md"]
    assert _unshipped_paths("- See `docs/process/NOT_SHIPPED.md`.", "build") == ["docs/process/NOT_SHIPPED.md"]


def _coordinator(fmt):
    return build.render_agent("coordinator", _agent_text("coordinator"), fmt, build.load_fragments(), build.load_rules())


def _install_module():
    spec = importlib.util.spec_from_file_location("manifold_install", ROOT / "install.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_t32_coordinator_is_a_role_in_every_profile_with_a_skill_name_and_a_known_install_role():
    assert "coordinator" in build.ROLES
    for profile, roles in build.PROFILES.items():
        assert "coordinator" in roles, profile
    assert build.SKILL_NAMES["coordinator"] == "coordinate-cycle"
    installer = _install_module()
    assert set(installer.KNOWN_ROLES) == set(build.ROLES)
    assert installer.role_of("acme-coordinator") == "coordinator" and installer.role_of("coordinator") == "coordinator"


def test_t32_the_claude_coordinator_keeps_the_agent_tool_and_carries_the_guard_hook():
    """The Agent tool is denied to no role today (CLAUDE_DENY has no entry for it), so the coordinator keeps it."""
    out = _coordinator("claude")
    front = out.split("\n---\n")[0].splitlines()
    assert "disallowedTools: WebFetch, WebSearch" in front
    assert front[front.index("hooks:"):] == list(build.GUARD_HOOKS_CLAUDE)
    for role in build.ROLES:
        blocks, _ = build.split_frontmatter(_agent_text(role))
        assert "Agent" not in build.claude_disallowed(blocks), role
    copilot_front = _coordinator("copilot").split("\n---\n")[0]
    assert "tools: [read, search, execute, edit, agent, todo]" in copilot_front


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
@pytest.mark.parametrize("fmt", ["claude", "copilot", "skills"])
def test_t33_coordinator_is_installed_in_every_profile_and_format_and_uninstalls_cleanly(bundle_dir, repo, profile, fmt):
    path = {"claude": ".claude/agents/coordinator.md", "copilot": ".github/agents/coordinator.agent.md",
            "skills": ".claude/skills/coordinate-cycle/SKILL.md"}[fmt]
    assert run(bundle_dir, repo, "--profile", profile, "--format", fmt, "--apply")[0] == 0
    assert (repo / path).exists(), path
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def test_t33_coordinator_is_one_source_for_both_flavors_and_uses_no_role_references():
    source = _agent_text("coordinator")
    assert "{{" not in source  # Concern 4: the quality profile does not install the planner, coder or reviewer
    assert build.lint(ROOT) == []
    bodies = [_coordinator(fmt).split("\n---\n", 1)[1] for fmt in ("claude", "copilot")]
    assert bodies[0] == bodies[1]
    agents, rules = build.load_agents(ROOT), build.load_rules(ROOT)
    for style in ("agents", "both"):
        for profile in build.PROFILES:
            block = build.render_instructions_block(agents, rules, style, profile)
            assert "**coordinator**" in block, (style, profile)


# every duty of INT-22 (Proposed outcome items 1 to 8) and the owner's decisions, as phrases the agent must carry
COORDINATOR_DUTIES = {
    "runs the loop in the written order": ("review -> `docs/plans/REVIEW_PLAN_<N>.md` -> planner amendment -> human approval",
                                           "docs/process/REVIEW_CYCLE.md", "own session", "Amendment approved by"),
    "does no one's work": ("no code, no plan and no review", "do not commit unless asked"),
    "a human decides": ("never moves a PR out of draft", "never merges", "never accepts an intent",
                        "never fills in **Approved by** or **Amendment approved by**", "never approves a plan or closes a phase"),
    "no outward action without the owner": ("push", "only with the owner's go-ahead", "the repository the owner names"),
    "ready check": ("docs/templates/PULL_REQUEST_TEMPLATE.md", "never says \"ready\" while a line is missing",
                    "exact commit", "a human confirms"),
    "reads CI of the exact commit": ("gh run list --commit <full hash> --json", "gh pr view <number> --json headRefOid,isDraft",
                                     "treat red or missing CI as a finding", "unverified"),
    "watches the guardrails": ("\"Rule exceptions\"", ".manifold/guard-log.jsonl", ".manifold/guard-allow.json",
                               "docs/process/BREACH_PROCEDURE.md", "Record your own breaches"),
    "collects process gaps and drafts an intent": ("process gaps", "status `draft`", "never `accepted`",
                                                  "docs/templates/INTENT_TEMPLATE.md"),
    "handles tests": ("failing-first", "Relay the question", "the owner's yes", "held-out", "separate from"),
    "where it cannot start agents": ("ask the human to start the agent", "inputs"),
    "is concise": ("short",),
}


@pytest.mark.parametrize("fmt", ["claude", "copilot"])
def test_t33_coordinator_carries_every_intent_duty_and_the_owner_decisions(fmt):
    out = _coordinator(fmt)
    for duty, needles in COORDINATOR_DUTIES.items():
        for needle in needles:
            assert needle in out, (fmt, duty, needle)
    assert "REVIEW_PLAN_" in out and "Rule exceptions" in out
    assert out.index("## When you finish") < out.index("- **Rule exceptions:** `none` or each exception (command, file, reason).")


def test_t33_coordinator_leaves_no_step_of_the_pull_request_to_an_agent():
    """The owner's binding decisions: a human moves a pull request out of draft; the coordinator never marks ready."""
    out = _coordinator("claude")
    for forbidden in ("mark the pull request ready", "gh pr ready", "gh pr merge", "git push"):
        assert forbidden not in out.replace("never " + forbidden, ""), forbidden


# ------------------------------------------------------------- HOWTO (T34; INT-21, INT-22)

def _doc(name):
    return (ROOT / name).read_text(encoding="utf-8")


def _howto():
    return _doc("HOWTO.md")


def _headings(text, prefix):
    return [x[len(prefix):].strip() for x in text.splitlines() if x.startswith(prefix) and not x.startswith(prefix + "#")]


def _cycle_step_names():
    """The first column of the table under '## The sequence' in REVIEW_CYCLE.md (header and rule rows skipped)."""
    section = _review_cycle().split("## The sequence\n")[1].split("\n## ")[0]
    names = []
    for line in section.splitlines():
        if line.startswith("|"):
            cell = line.split("|")[1].strip()
            if cell and cell != "Step" and set(cell) != {"-"}:
                names.append(cell)
    return names


def test_t34_howto_is_a_process_path_for_every_profile_and_ships_at_the_zip_root(built):
    """Open question 9: installed to docs/process/HOWTO.md in every profile, and at the zip root like the README."""
    target, profiles = build.PROCESS_PATHS["HOWTO.md"]
    assert target == "docs/process/HOWTO.md" and tuple(profiles) == build.ALL_PROFILES
    with zipfile.ZipFile(built) as zf:
        (root_copy,) = [n for n in zf.namelist() if n.endswith("/HOWTO.md") and n.count("/") == 1]
        assert zf.read(root_copy) == (ROOT / "HOWTO.md").read_bytes()
        assert zf.read([n for n in zf.namelist() if n.endswith("payload/common/docs/process/HOWTO.md")][0]) == \
            (ROOT / "HOWTO.md").read_bytes()


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
def test_t34_howto_is_installed_in_every_profile_and_uninstalls_cleanly(bundle_dir, repo, profile):
    assert run(bundle_dir, repo, "--profile", profile, "--apply")[0] == 0
    assert (repo / "docs/process/HOWTO.md").read_bytes() == (ROOT / "HOWTO.md").read_bytes()
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def test_t34_lint_requires_the_howto(tmp_path):
    src = copy_source(tmp_path / "src")
    assert build.lint(src) == []
    (src / "HOWTO.md").unlink()
    assert any("missing process document: HOWTO.md" in x for x in build.lint(src))
    src = copy_source(tmp_path / "src2")
    path = src / "HOWTO.md"
    path.write_text(path.read_text() + "\nSee the " + build.FORBIDDEN_TERMS[0] + " site.\n")
    assert any("HOWTO.md contains forbidden term" in x for x in build.lint(src))


def test_t34_howto_names_every_role_and_every_step_of_the_review_cycle():
    """K2: every role in build.ROLES, and every step name of the table in REVIEW_CYCLE.md, in order as headings."""
    t = _howto()
    for role in build.ROLES:
        assert "`%s`" % role in t, role
    steps = _cycle_step_names()
    assert steps == ["Review", "Amendment", "Approval", "Repair", "Re-review", "Close"], steps
    cycle = t.split("\n## The cycle in order\n")[1].split("\n## ")[0]
    headings = _headings(cycle, "### ")
    position = 0
    for step in steps:
        found = [i for i, h in enumerate(headings) if i >= position and step in h]
        assert found, (step, headings)
        position = found[0] + 1
    for word in ("Intent", "Plan", "Build", "ready check", "Merge"):
        assert any(word.lower() in h.lower() for h in headings), (word, headings)


def test_t34_howto_has_its_sections_and_three_labels_for_every_step():
    t = _howto()
    sections = _headings(t, "## ")
    expected = ["When to use each agent", "The cycle in order", "The human gates", "Breaches",
                "Solo or team", "What differs by client", "How to start"]
    positions = [sections.index(h) for h in expected]
    assert positions == sorted(positions), sections
    cycle = t.split("\n## The cycle in order\n")[1].split("\n## ")[0]
    for block in cycle.split("\n### ")[1:]:
        for label in ("**What usually happens.**", "**What you do.**", "**What the agents will not do.**"):
            assert label in block, (block.splitlines()[0], label)
    agents = t.split("\n## When to use each agent\n")[1].split("\n## ")[0]
    assert "| Use it when | Do not use it when |" in agents


def test_t34_howto_links_the_procedures_and_does_not_contradict_them():
    t = _howto()
    for path in ("docs/process/REVIEW_CYCLE.md", "docs/process/BREACH_PROCEDURE.md", "docs/templates/REVIEW_PLAN_TEMPLATE.md",
                 "docs/templates/PULL_REQUEST_TEMPLATE.md", ".claude/agents/", ".github/agents/"):
        assert path in t, path
    assert "three runs" in t and "three runs" in _review_cycle()
    assert "never moves a PR out of draft" in t or "never moves a pull request out of draft" in t
    assert "fills in **Approved by**" in t and "**Amendment approved by**" in t


def test_t34_howto_lists_the_human_gates_and_states_enforcement_per_client_as_far_as_verified():
    t = _howto()
    gates = t.split("\n## The human gates\n")[1].split("\n## ")[0]
    for needle in ("status: accepted", "**Approved by**", "**Amendment approved by**", "out of draft", "merge",
                   "guard-allow.json", "CI", "Pending human confirmation", "go-ahead"):
        assert needle in gates, needle
    client = t.split("\n## What differs by client\n")[1].split("\n## ")[0]
    for needle in ("Claude Code", "Copilot", "unverified", "instruction only", "docs/agents/harness-capabilities.md",
                   "main session", "skills"):
        assert needle in client, needle
    breach = t.split("\n## Breaches\n")[1].split("\n## ")[0]
    for needle in (".manifold/guard-log.jsonl", "Rule exceptions", "docs/agents/", "docs/process/BREACH_PROCEDURE.md",
                   ".manifold/guard-allow.json"):
        assert needle in breach, needle
    team = t.split("\n## Solo or team\n")[1].split("\n## ")[0]
    assert "Review process" in team and "second approver" in team.lower()


def test_t34_rendered_instructions_point_to_the_howto_in_every_profile_and_style():
    """Owner's answer: the AGENTS.md block names docs/process/HOWTO.md; it is shipped in every profile, so no unshipped path."""
    agents, rules = build.load_agents(ROOT), build.load_rules(ROOT)
    for style in ("agents", "skills", "both"):
        for profile in build.PROFILES:
            block = build.render_instructions_block(agents, rules, style, profile)
            assert len([x for x in block.splitlines() if "docs/process/HOWTO.md" in x]) == 1, (style, profile)
            assert _unshipped_paths(block, profile) == [], (style, profile)


def test_t34_howto_has_no_forbidden_term_and_no_bundle_version():
    t = _howto().lower()
    for term in build.FORBIDDEN_TERMS:
        assert term not in t
    assert (ROOT / "VERSION").read_text().strip() not in t


# -------------------------------------------- README, INSTALL, MODELS, live protocol, CONTRIBUTING (T35)

def test_t35_readme_has_eight_roles_one_install_table_and_the_whole_loop():
    t = _doc("README.md")
    assert "Seven" not in t and "seven" not in t.lower().replace("seventh", "")
    assert t.startswith("# Manifold: base bundle\n\nEight focused agents")
    roles = t.split("\n## The roles\n")[1].split("\n## ")[0]
    for role in build.ROLES:
        assert "| **%s** |" % role in roles, role
    assert t.count("## What gets installed") == 1
    loop = t.split("\n## How the roles fit the loop\n")[1].split("\n### ")[0]
    for needle in ("REVIEW_PLAN_", "Amendment approved by", "Re-review", "Ready check", "Repair", "Amendment"):
        assert needle in loop, needle
    installed = t.split("\n## What gets installed\n")[1].split("\n## ")[0]
    assert "| Path in your repo | Profiles | What |" in installed
    for needle in (".manifold/hooks/guard.py", ".github/hooks/manifold-guard.json", ".manifold/scratch/", ".manifold/.gitignore",
                   "docs/process/", "HOWTO.md", "REVIEW_PLAN_TEMPLATE", "PULL_REQUEST_TEMPLATE", "AGENT_FAILURES_TEMPLATE",
                   "Review process", "coordinator"):
        assert needle in installed, needle
    skills = t.split("\n## Agent Skills (experimental)\n")[1].split("\n## ")[0]
    for skill in build.SKILL_NAMES.values():
        assert "`%s`" % skill in skills, skill
    profiles = t.split("\n## Install profiles\n")[1].split("\n## ")[0]
    assert "| planner, coder, bug-coder, reviewer, test-planner, test-coder, coordinator |" in profiles
    assert "| scenario-writer, test-planner, test-coder, coordinator |" in profiles
    assert "all eight" in profiles and "HOWTO.md" in t


def test_t35_readme_describes_the_guard_and_its_residual_gap_and_drops_the_old_claims():
    t = _doc("README.md")
    section = t.split("\n### Rules are advice, not enforcement\n")[1].split("\n## ")[0].split("\n### ")[0]
    for needle in ("guard", "Claude Code", "Copilot", "unverified", "main session", "script", "instruction", "INSTALL.md"):
        assert needle in section, needle
    assert "Nothing in this bundle stops an agent" not in t
    assert "Optional hooks are on the" not in t
    assert "the reviewer cannot edit files" not in t and "reviewer cannot edit" not in t
    assert "writes exactly one file" in t or "one file" in t.split("| **reviewer** |")[1].split("\n")[0]


def test_t35_user_documents_link_nothing_outside_the_zip_and_name_no_bundle_version():
    """Open links into the source repository do not resolve in the zip; the version is read from VERSION, not typed."""
    import re
    version = (ROOT / "VERSION").read_text().strip()
    for name in ("README.md", "INSTALL.md", "MODELS.md", "HOWTO.md", "CONTRIBUTING.md"):
        text = _doc(name)
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            assert not target.startswith("../"), (name, target)
        assert version not in text, name
    assert "manifold-base-<version>" in _doc("INSTALL.md") and "manifold-base-<version>" in _doc("README.md")


def test_deferred_text_fixes_f1_f4_f5():
    """Phase 3 CP1: no repository history or pronoun in the review cycle, no 'never seen live' claim that a live
    refusal contradicts, and the guard's stated limits name the write-capable tools it allows."""
    cycle = (ROOT / "process" / "REVIEW_CYCLE.md").read_text()
    for needle in ("Phase 2", "CP2a", "CP2b", " his "):
        assert needle not in cycle, needle
    for name in ("INSTALL.md", "HOWTO.md"):
        assert "not yet seen in a live run" not in _doc(name), name
        assert "recorded in a live" not in _doc(name), name
    docstring = (ROOT / "hooks" / "guard.py").read_text().split("from __future__")[0]
    assert "curl -o" in docstring


def test_review_cycle_names_homes_levels_and_light_path():
    """Phase 3 CP2: one home per fact, a definition of done with three levels, and a light path for text fixes."""
    cycle = (ROOT / "process" / "REVIEW_CYCLE.md").read_text()
    for heading in ("## Where each fact is recorded", "## Definition of done", "## Light path for text fixes"):
        assert heading in cycle, heading
    light = cycle.split("## Light path for text fixes")[1].split("\n## ")[0]
    assert "solo" in light and "never code" in light
    ready = cycle.split("## The ready check")[1].split("\n## ")[0]
    item3 = [x for x in ready.splitlines() if x.startswith("3.")][0]
    assert "never a commit" in item3 or "no second confirmation" in item3
    assert "run for an older commit is not the result" in ready


def test_review_cycle_round2_repairs():
    """Phase 3 CP6: ready-check item 3 asks a CI read and tick for every commit, the reviewer's file records only
    open and repaired, and the light path says what it skips, what it keeps and who judges 'text only'."""
    cycle = (ROOT / "process" / "REVIEW_CYCLE.md").read_text()
    ready = cycle.split("## The ready check")[1].split("\n## ")[0]
    item3 = [x for x in ready.splitlines() if x.startswith("3.")][0]
    assert "no second confirmation" not in item3 and "changes no code" not in item3
    assert "never a commit" in item3 and "run for an older commit is not the result" in item3
    assert "The reviewer's file records only `open` and `repaired`" in cycle
    assert "as repaired, deferred or rejected with evidence" not in cycle
    light = cycle.split("## Light path for text fixes")[1].split("\n## ")[0]
    assert "the human who ticks judges" in light and "ready check" in light


def test_coordinator_reports_level_and_compares_branch_rules():
    """Phase 3 CP3: the coordinator writes the CI result into the pull request for a human to tick (no commit),
    reports the level of the definition of done, batches decisions, and compares branch rules with the workflows."""
    text = _agent_text("coordinator")
    for needle in ("## Branch rules", "mergeable", "releasable", "accept all", "never declare", "never change the ruleset"):
        assert needle in text, needle
    ci = text.split("## CI of the exact commit")[1].split("\n## ")[0]
    assert "remaining-steps list" in ci and "no commit" in ci
    branch = text.split("## Branch rules")[1].split("\n## ")[0]
    assert ".github/workflows/" in branch and "required check" in branch


def test_coordinator_ci_write_is_the_one_standing_exception():
    """Phase 3 CP7 (review round 3, F11): the four statements about pull request writes agree. The CI result line
    is the one write the coordinator makes without asking each time; every other pull request write needs the go-ahead."""
    text = _agent_text("coordinator")
    ci = text.split("## CI of the exact commit")[1].split("\n## ")[0]
    assert "without asking each time" in ci and "the one write" in ci
    ready = text.split("## Ready check")[1].split("\n## ")[0]
    for needle in ("only with the owner's go-ahead", "the one exception", "remaining-steps list",
                   "Every other pull request write needs the go-ahead"):
        assert needle in ready, needle
    rule = text.split("**No outward action without the owner.**")[1].split("\n- **")[0]
    assert "only with the owner's go-ahead" in rule and "the one exception" in rule
    donot = text.split("## What you do not do")[1].split("\n## ")[0]
    assert "the one exception" in donot


def test_ask_rule_requires_self_contained_asks_for_coordinator():
    """Phase 3 CP3: every ask says what, why, consequence and default, never an internal ID alone, and the
    rule reaches the coordinator."""
    rules = build.load_rules(ROOT)
    rule = [r for r in rules if r["id"] == "ask-on-ambiguity"][0]
    assert "coordinator" in rule["applies_to"]
    for needle in ("internal ID", "the consequence", "the default"):
        assert needle in rule["instead"], needle
    fragments = build.load_fragments(ROOT)
    for fmt in ("claude", "copilot"):
        rendered = build.render_agent("coordinator", _agent_text("coordinator"), fmt, fragments, rules)
        assert "internal ID" in rendered, fmt


def test_pr_template_has_remaining_steps_and_decisions_table():
    """Phase 3 CP2: the pull request template carries the human's remaining steps and one batch of decisions."""
    t = (ROOT / "templates" / "PULL_REQUEST_TEMPLATE.md").read_text()
    assert "## What remains for you" in t and "## Decisions for you" in t
    assert "| What | Why | Consequence | Default |" in t
    assert "accept all" in t and "Where each fact is recorded" in t


_SLUG_RE = re.compile(r"<Insert [^<>]*>")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def _pr_template():
    return (ROOT / "templates" / "PULL_REQUEST_TEMPLATE.md").read_text()


def test_pr_template_has_visible_instructions_and_one_slug_shape():
    """Phase 4 CP1 (INT-27 S1, S3, S7): each human-written line holds one slug; instructions are visible text."""
    t = _pr_template()
    for label in ("**Confirmed by:**", "**Human confirmation:**"):
        (line,) = [ln for ln in t.splitlines() if ln.startswith(label)]
        assert len(_SLUG_RE.findall(line)) == 1, line
    assert len(_SLUG_RE.findall(t)) == 2  # no slug anywhere else in the template
    visible = _HTML_COMMENT_RE.sub("", t)
    assert visible.count("**Instructions:**") >= 4  # CI, ready check, human confirmation, remaining steps
    assert not _SLUG_RE.search("".join(_HTML_COMMENT_RE.findall(t)))  # a slug only in a comment would be hidden


def test_pr_template_state_cells_name_both_values():
    """Phase 4 CP1 (INT-27 S4): the State cell says what to write; the instructions name both values."""
    t = _pr_template()
    assert "met / missing" not in t
    visible = _HTML_COMMENT_RE.sub("", t)
    instructions = visible.split("## Ready check")[1]
    assert "`met`" in instructions and "`missing`" in instructions


def test_pr_template_names_the_approve_review_and_claims_nothing_about_self_approval():
    """Phase 4 CP1 (INT-27 S5): the Approve review step exists; no claim about what GitHub allows an author."""
    t = _pr_template()
    assert "Approve" in t and "Review changes" in t
    lowered = t.lower()
    for forbidden in ("own pull request", "self-approv", "cannot approve"):
        assert forbidden not in lowered, forbidden


def test_pr_template_is_generic():
    """Phase 4 CP1 (INT-27): shipped text names no person and no repository."""
    t = _pr_template()
    for needle in ("Michael Hay", "mihay42", "mediumroast"):  # `.manifold/` is the install's own folder, not a repository name
        assert needle.lower() not in t.lower(), needle


def test_t35_install_states_the_guard_per_client_and_how_a_human_grants_an_exception():
    t = _doc("INSTALL.md")
    for needle in ("Claude Code", "Copilot", "unverified", ".manifold/hooks/guard.py", ".github/hooks/manifold-guard.json",
                   ".manifold/guard-allow.json", '"scope": "path"', "expires", ".manifold/guard-log.jsonl",
                   ".manifold/scratch/", "instruction only", "docs/process/", "HOWTO.md", "docs/agents/harness-capabilities.md"):
        assert needle in t, needle
    manual = t.split("\n## Without Python\n")[1].split("\n## ")[0]
    assert "payload/common/.manifold/" in manual and "guard" in manual
    assert "git add" in t and "docs/process" in t.split("git add", 1)[1].split("\n")[0]


def test_t35_models_says_phase_2_content_is_not_run_on_any_model():
    t = _doc("MODELS.md")
    assert "Phase 2 content (guard, coordinator, loop) is not run on any model" in t


def test_t35_live_protocol_has_rows_for_the_guard_the_route_the_review_file_a_stop_and_the_coordinator():
    t = (ROOT / "tests" / "live-protocol.md").read_text()
    assert "six roles" not in t and "all seven" not in t and "**edits nothing**" not in t
    rows = {}
    for line in t.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| ") and cells[0].isdigit():
            assert len(cells) == 5, line
            rows[int(cells[0])] = line.lower()
    assert sorted(rows) == list(range(1, 14)), sorted(rows)
    for number, needles in {9: ("guard", "refus"), 10: (".manifold/scratch/", "write"), 11: ("review_plan_", "one file"),
                            12: ("checkpoint", "stop"), 13: ("coordinator", "draft")}.items():
        for needle in needles:
            assert needle in rows[number], (number, needle)
    header = [x for x in t.splitlines() if x.startswith("| # |")][0]
    assert "Claude Code" in header and "Copilot" in header


def test_t35_contributing_says_how_the_hook_is_tested_and_lists_the_coordinator_role():
    t = _doc("CONTRIBUTING.md")
    for needle in ("tests/test_guard.py", "hooks/guard.py", "standard library", "exit code", "coordinator"):
        assert needle in t, needle


# ------------------------------------------------ INT-25: a skeptical test planner (T44 to T52)

def _rule_text(rule_id):
    """One rule source on one line, the way render_rules joins it."""
    return " ".join((ROOT / "rules" / "core" / ("%s.md" % rule_id)).read_text().split())


def test_int25_test_planner_reads_the_intent_judges_existing_tests_asks_and_never_approves():
    """INT-25 S2, S3, S4, S6, S7 (T50): the planner is skeptical of the builders' tests and asks before it pads."""
    for out in _both_flavors("test-planner"):
        assert "so you do not duplicate coverage" not in out
        for needle in ("originating intent", "adequate, thin or absent", "no gap found",
                       "Questions for the human", "Unconfirmed: owner to confirm", "no quality repository",
                       "never fill in **Approved by**"):
            assert needle in out, needle


def test_int25_test_coder_stops_on_approval_and_blocking_questions_and_keeps_a_failing_check_red():
    """INT-25 S5 (T51): approval first, a blocking question stops the work, a failing check is a defect and stays red."""
    for out in _both_flavors("test-coder"):
        for needle in ("Approved by", "blocking question", "stays red", "call shape", "bug-coder"):
            assert needle in out, needle


def test_int25_test_plan_template_has_the_skeptical_sections_and_fields():
    """INT-25 S2, S3, S4, S6 (T49)."""
    t = (ROOT / "templates" / "PHASE_TEST_PLAN_TEMPLATE.md").read_text()
    for heading in ("## Source intents", "## Coverage judgement", "## Gaps found", "## Questions for the human"):
        assert heading in t, heading
    for field in ("**Approved by:**", "**Derived from:**", "**Existing or new:**", "**Blocking:**", "**Answer:**"):
        assert field in t, field


def test_int25_rule_derive_tests_names_the_intent_and_asks_for_a_source_per_case():
    """INT-25 S2 (T47): the old sentence that made the plan the only source is gone."""
    t = _rule_text("derive-tests-from-plan")
    assert "Test cases come from the phase plan's objective, file inventory and acceptance lines" not in t
    for needle in ("originating intent", "gap check", "cites a source"):
        assert needle in t, needle
    for role in ("test-planner", "test-coder"):
        for out in _both_flavors(role):
            assert "Test cases come from the phase plan's objective, file inventory and acceptance lines" not in out
            assert "cites a source" in out, role


def test_int25_rule_black_box_limits_the_pseudo_holdout_to_repositories_without_a_quality_repository():
    """INT-25 S7 (T48)."""
    assert "no quality repository" in _rule_text("quality-side-is-black-box")


def test_int25_test_planner_modes_say_who_is_held_out_from_what():
    """INT-25 S7 (T50 follow-up, owner 2026-11-08): the scenario-mode planner is the quality side and reads
    its own scenarios by design; the local-check planner never reads held-out scenarios and has no pseudo
    hold-out where a quality repository exists."""
    for out in _both_flavors("test-planner"):
        local = out.split("- **Local-check mode**")[1].split("- **Scenario mode**")[0]
        scenario = out.split("- **Scenario mode**")[1].split("\n\n")[0]
        assert "you never read them" in local and "only where there is no quality repository" in local
        assert "you are the quality side" in scenario
        assert "read this repository's scenarios by design" in scenario
        assert "the pseudo hold-out is not used" in scenario
        assert "held-out scenarios are never read" not in scenario


def test_int25_rule_builders_say_what_a_gap_check_is():
    """INT-25 S2 (T48): a gap check is a local integration check the builders do not write."""
    assert "gap check" in _rule_text("builders-dont-write-acceptance-tests")


def test_int25_reviewer_checks_a_test_plan_for_reflection_inside_the_tests_pass_and_never_approves_it():
    """INT-25 S1, S8 (T52, Open question 18 option A): a named section under the existing Tests pass, no new pass."""
    for out in _both_flavors("reviewer"):
        assert "## When the change includes a test plan" in out
        section = out.split("## When the change includes a test plan")[1].split("\n## ")[0]
        for sign in ("no intent cited", "every automated case pre-ticked", "no gaps", "no questions", "a case with no source"):
            assert sign in section, sign
        assert "**Tests**" in section and "PHASE_<N>_TEST_PLAN.md" in section
        assert "never approve the test plan" in section
        assert "no new pass" in section


@pytest.mark.parametrize("role", ["test-planner", "test-coder"])
def test_int25_both_flavors_carry_the_same_body(role):
    """INT-25 S8 (T44): one source, so the two rendered bodies are identical."""
    bodies = [out.split("\n---\n", 1)[1] for out in _both_flavors(role)]
    assert bodies[0] == bodies[1]


# The optional marker {{name?:role}} (owner's decision, 2026-11-08): names a role that some profile
# may not install. Patterned on test_unknown_role_in_a_reference_is_rejected and
# test_lint_rejects_a_reference_to_a_role_the_profile_lacks.

@pytest.mark.parametrize("fmt,expected", [("claude", "`bug-coder`"), ("copilot", "`bug-coder`"), ("skills", "`fix-bug`")])
def test_optional_name_marker_expands_like_name_per_flavor(fmt, expected):
    assert build.expand_refs("see {{name?:bug-coder}}.", fmt, "x") == "see %s." % expected


def test_optional_marker_with_an_unknown_role_is_rejected_when_expanded():
    with pytest.raises(build.BuildError):
        build.expand_refs("see {{name?:wizard}}", "skills", "x")


def test_lint_passes_a_quality_role_that_names_the_optional_bug_coder(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "agents" / "scenario-writer.agent.md"
    p.write_text(p.read_text().replace("## What you do not do", "Hand a defect to the {{name?:bug-coder}} where installed.\n\n## What you do not do", 1))
    assert build.lint(src) == []


def test_lint_still_rejects_an_optional_marker_naming_a_nonexistent_role(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "agents" / "scenario-writer.agent.md"
    p.write_text(p.read_text().replace("## What you do not do", "Ask the {{name?:bug-coderr}}.\n\n## What you do not do", 1))
    assert build.lint(src) != []


def test_lint_still_rejects_the_plain_ref_to_bug_coder_from_test_coder(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "agents" / "test-coder.agent.md"
    p.write_text(p.read_text().replace("## What you do not do", "See the {{ref:bug-coder}}.\n\n## What you do not do", 1))
    assert any("test-coder refers to 'bug-coder'" in x and "quality" in x for x in build.lint(src))


def test_test_coder_names_bug_coder_per_flavor():
    fragments, rules = build.load_fragments(), build.load_rules()
    text = _agent_text("test-coder")
    assert "{{name?:bug-coder}}" in text
    for fmt in ("claude", "copilot"):
        out = build.render_agent("test-coder", text, fmt, fragments, rules)
        assert "`bug-coder`" in out and "fix-bug" not in out and "{{" not in out
    out = build.render_skill("test-coder", text, fragments, rules, build.read_version(ROOT))
    assert "`fix-bug`" in out and "bug-coder" not in out and "{{" not in out


# ---- Phase 3 CP4 (Task 17): the /phase-status script and its command, in the build and the install

PHASE_SCRIPT_INSTALLED = ".manifold/phase_status.py"
PHASE_CLAUDE_COMMAND = ".claude/commands/phase-status.md"
PHASE_COPILOT_PROMPT = ".github/prompts/phase-status.prompt.md"


def test_phase_status_files_are_in_the_zip_and_the_manifest_for_every_profile(built, bundle_dir):
    bundle = json.loads((bundle_dir / "bundle.json").read_text())
    common = {e["path"]: e for e in bundle["common"]}
    assert set(common[PHASE_SCRIPT_INSTALLED]["profiles"]) == {"build", "quality", "single"}
    assert (bundle_dir / common[PHASE_SCRIPT_INSTALLED]["src"]).read_bytes() == (ROOT / "scripts" / "phase_status.py").read_bytes()
    for fmt, path, source in (("claude", PHASE_CLAUDE_COMMAND, "phase-status.md"),
                              ("copilot", PHASE_COPILOT_PROMPT, "phase-status.prompt.md")):
        (entry,) = [e for e in bundle["formats"][fmt] if e["path"] == path]
        assert set(entry["profiles"]) == {"build", "quality", "single"}, fmt
        assert (bundle_dir / entry["src"]).read_bytes() == (ROOT / "commands" / source).read_bytes()
    assert not [e for e in bundle["formats"]["skills"] if "phase" in e["path"]]


@pytest.mark.parametrize("profile", ["build", "quality", "single"])
@pytest.mark.parametrize("fmt,command", [("claude", PHASE_CLAUDE_COMMAND), ("copilot", PHASE_COPILOT_PROMPT), ("skills", None)])
def test_phase_status_is_installed_per_profile_and_flavor_and_uninstalled_cleanly(bundle_dir, repo, profile, fmt, command):
    assert run(bundle_dir, repo, "--profile", profile, "--format", fmt, "--apply")[0] == 0
    installed = tree(repo)
    assert PHASE_SCRIPT_INSTALLED in installed  # the script comes with every flavor and profile
    assert (repo / PHASE_SCRIPT_INSTALLED).read_bytes() == (ROOT / "scripts" / "phase_status.py").read_bytes()
    for path in (PHASE_CLAUDE_COMMAND, PHASE_COPILOT_PROMPT):
        assert (path in installed) is (path == command), (fmt, path)
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def test_both_and_all_formats_install_both_commands(bundle_dir, repo):
    assert run(bundle_dir, repo, "--format", "all", "--allow-overlap", "--apply")[0] == 0
    assert {PHASE_CLAUDE_COMMAND, PHASE_COPILOT_PROMPT, PHASE_SCRIPT_INSTALLED} <= set(tree(repo))
    assert run(bundle_dir, repo, "--uninstall", "--apply")[0] == 0
    assert tree(repo) == []


def test_two_builds_are_byte_equal_and_carry_the_phase_status_files(tmp_path):
    first = build.build_zip(ROOT, tmp_path / "a")
    second = build.build_zip(ROOT, tmp_path / "b")
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as zf:
        names = zf.namelist()
    for suffix in ("payload/common/" + PHASE_SCRIPT_INSTALLED, "payload/claude/" + PHASE_CLAUDE_COMMAND,
                   "payload/copilot/" + PHASE_COPILOT_PROMPT):
        assert any(n.endswith(suffix) for n in names), suffix


def test_the_claude_command_pre_approves_python3_and_runs_the_script_inline():
    text = (ROOT / "commands" / "phase-status.md").read_text()
    assert text.startswith("---\n")
    front = text.split("\n---\n", 1)[0]
    assert "allowed-tools: Bash(python3 *)" in front.split("\n")
    assert "!`python3 .manifold/phase_status.py $ARGUMENTS`" in text


def test_the_copilot_prompt_states_its_limit_and_claims_no_deterministic_run():
    text = (ROOT / "commands" / "phase-status.prompt.md").read_text()
    assert text.startswith("---\n")
    assert "python3 .manifold/phase_status.py ${input:phase}" in text
    for needle in ("paste its output unedited", "the run is your act", "not a read the client performs by itself",
                   "Local harness", "deprecated", "February 2027"):
        assert needle in text, needle
    assert "!`" not in text  # the inline shell form is the Claude Code one; a prompt file has none


def test_the_skills_instruction_names_the_script_and_says_it_is_unverified():
    agents, rules = build.load_agents(), build.load_rules()
    for style in ("skills", "both"):
        block = build.render_instructions_block(agents, rules, style, "build")
        (line,) = [x for x in block.split("\n") if "phase_status.py" in x]
        assert "python3 .manifold/phase_status.py <N>" in line and "unverified" in line, style
    assert "phase_status.py" not in build.render_instructions_block(agents, rules, "agents", "build")


def test_lint_rejects_a_phase_status_script_that_imports_outside_the_standard_library(tmp_path):
    src = copy_source(tmp_path / "src")
    p = src / "scripts" / "phase_status.py"
    p.write_text(p.read_text() + "\nimport requests\n")
    assert any("scripts/phase_status.py" in x and "standard library" in x for x in build.lint(src))
    p.write_text(p.read_text() + "\ndef broken(:\n")
    assert any("scripts/phase_status.py does not compile" in x for x in build.lint(src))


def test_lint_rejects_a_missing_phase_status_file_or_a_command_that_does_not_run_the_script(tmp_path):
    src = copy_source(tmp_path / "src")
    (src / "scripts" / "phase_status.py").unlink()
    assert any("missing file: scripts/phase_status.py" in x for x in build.lint(src))
    src = copy_source(tmp_path / "src2")
    claude = src / "commands" / "phase-status.md"
    claude.write_text(claude.read_text().replace("allowed-tools: Bash(python3 *)\n", ""))
    assert any("phase-status.md" in x and "allowed-tools" in x for x in build.lint(src))
    claude.write_text(claude.read_text().replace("phase_status.py", "elsewhere.py"))
    assert any("phase-status.md" in x for x in build.lint(src))
    src = copy_source(tmp_path / "src3")
    (src / "commands" / "phase-status.prompt.md").unlink()
    assert any("missing file: commands/phase-status.prompt.md" in x for x in build.lint(src))


def test_the_installed_script_runs_from_the_install_and_reads_the_plan(bundle_dir, repo):
    assert run(bundle_dir, repo, "--apply")[0] == 0
    plans = repo / "docs" / "plans"
    plans.mkdir(parents=True)
    (plans / "PHASE_9_PLAN.md").write_text("**Approved by:**\n\n### Task 1 - x\n**Todo:** [ ]\n")
    p = subprocess.run([sys.executable, str(repo / PHASE_SCRIPT_INSTALLED), "9"], capture_output=True, text=True, cwd=repo)
    assert p.returncode == 0 and "Approved by: BLANK" in p.stdout and "Unticked tasks ([ ]): 1" in p.stdout
