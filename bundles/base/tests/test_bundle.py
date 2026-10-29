# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Tests for the Manifold build tool and installer (installer exercised through its real CLI)."""
import hashlib
import importlib.util
import json
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
    keys = {line.split(":")[0] for line in head.strip().splitlines()}
    assert keys == {"name", "description", "disallowedTools"}


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
    assert tops == {"manifold-base-0.1.0"}
    assert not any(n.startswith("/") or ".." in n.split("/") for n in names)


def test_installers_are_executable_in_the_zip(built):
    with zipfile.ZipFile(built) as zf:
        for info in zf.infolist():
            if info.filename.endswith(("install.py", "install.sh")):
                assert (info.external_attr >> 16) & 0o111


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
    assert manifest["version"] == "0.1.0" and set(AGENT_FILES) <= set(manifest["files"])


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

BUILD_ROLES = ["planner", "coder", "bug-coder", "reviewer", "test-planner", "test-coder"]
QUALITY_ROLES = ["scenario-writer", "test-planner", "test-coder"]


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


def test_planner_has_intent_mode_and_never_accepts_its_own_plan():
    t = _agent_text("planner")
    assert "## Intent mode" in t and "scenario seeds" in t and "Concerns flagged" in t
    assert "**Never** mark the intent accepted" in t and "Approved by" in t


def test_reviewer_is_read_only_and_never_approves():
    tools = _tools("reviewer")
    assert "edit" not in tools and "write" not in tools
    t = _agent_text("reviewer")
    assert "must not review its own change" in t
    assert "you do **not approve or block** anything" in t
    assert "REVIEW.md" in t and "Read-only" in t


def test_claude_format_denies_the_tools_an_agent_does_not_declare():
    """Claude Code agents inherit every tool unless told otherwise, so the read-only
    and black-box roles must carry a denylist (an allowlist would also hide MCP tools)."""
    def fm(role):
        out = build.render_agent(role, _agent_text(role), "claude", build.load_fragments(), build.load_rules())
        return out.split("---")[1]
    reviewer = fm("reviewer")
    assert "disallowedTools: Edit, Write, NotebookEdit, WebFetch, WebSearch" in reviewer
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
        assert "Say which mode you are in at the start of your first reply" in _agent_text(role), role


def test_planner_carries_the_intents_constraints_into_the_plan():
    """Live run: the plan kept 'Python 3.8' but dropped the intent's 'standard library only'."""
    assert "Every constraint stated in the intent appears in the plan" in _agent_text("planner")


def test_planner_refuses_to_fill_in_the_approval_even_when_asked():
    """Live run (Copilot, Sonnet 4.6): asked to mark the plan approved, the planner wrote an approver name itself."""
    t = _agent_text("planner")
    assert "decline even when they insist" in t and "Never invent an approver name" in t


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
    for needle in ("## Passes", "What Important means", "Cap the nits", "Do not report", "Human threshold"):
        assert needle in t, needle


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
