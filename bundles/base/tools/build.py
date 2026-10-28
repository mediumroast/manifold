#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Lint, render and package the Manifold base bundle. Standard library only.

    python3 tools/build.py            # lint + build dist/manifold-base-<version>.zip
    python3 tools/build.py --check    # lint only

Canonical agent sources in agents/*.agent.md are rendered to each client format.
The rules in rules/core/*.md are expanded per role. Output is
deterministic: building twice produces identical bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = ("planner", "coder", "bug-coder", "reviewer", "test-planner", "test-coder", "scenario-writer")
# Which roles each install profile gets. build: a product repository. quality: a separate
# repository for behavior scenarios. single: one repository holding both (verification is
# not independent there, and the installer says so).
PROFILES = {
    "build": ("planner", "coder", "bug-coder", "reviewer", "test-planner", "test-coder"),
    "quality": ("scenario-writer", "test-planner", "test-coder"),
    "single": ROLES,
}
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
SCALAR_KEYS = ("name", "description", "argument-hint")
FORBIDDEN_TERMS = ("mediumroast",)
BLOCK_BEGIN = "<!-- manifold:begin v=1 -->"
BLOCK_END = "<!-- manifold:end -->"
INCLUDE_RE = re.compile(r"^<!-- include: ([a-z-]+) -->\s*$", re.MULTILINE)
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)

CLAUDE_AGENT_PATH = ".claude/agents/{name}.md"
COPILOT_AGENT_PATH = ".github/agents/{name}.agent.md"
SKILL_NAMES = {"planner": "plan-change", "coder": "execute-plan", "bug-coder": "fix-bug",
               "reviewer": "review-change", "test-planner": "plan-tests", "test-coder": "write-tests",
               "scenario-writer": "write-scenarios"}
SKILL_ROOT = ".claude/skills"
SKILL_PATH = SKILL_ROOT + "/{name}/SKILL.md"
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKILL_ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REF_RE = re.compile(r"\{\{(ref|name):([a-z-]+)\}\}")
ALL_PROFILES = tuple(PROFILES)
# template file -> (installed path, profiles that receive it)
TEMPLATE_PATHS = {
    "INTENT_TEMPLATE.md": ("docs/templates/INTENT_TEMPLATE.md", ALL_PROFILES),
    "PHASE_PLAN_TEMPLATE.md": ("docs/templates/PHASE_PLAN_TEMPLATE.md", ("build", "single")),
    "PHASE_TEST_PLAN_TEMPLATE.md": ("docs/templates/PHASE_TEST_PLAN_TEMPLATE.md", ALL_PROFILES),
    "WT_TEMPLATE.md": ("docs/templates/WT_TEMPLATE.md", ALL_PROFILES),
    "REVIEW_TEMPLATE.md": ("docs/templates/REVIEW_TEMPLATE.md", ("build", "single")),
    "SCENARIO_TEMPLATE.md": ("docs/templates/SCENARIO_TEMPLATE.md", ("quality", "single")),
    "SATISFACTION_REPORT_TEMPLATE.md": ("docs/templates/SATISFACTION_REPORT_TEMPLATE.md", ("quality", "single")),
}
# config file (in config/) -> (installed path, profiles). User-editable after install.
SETTINGS_FILES = {
    "quality-settings.json": (".manifold/quality-settings.json", ("quality", "single")),
}
QUALITY_SETTINGS_KEYS = (
    "satisfaction.minimum_overall", "satisfaction.minimum_per_seed", "failures.critical_max_rate",
    "judge.minimum_confidence", "trajectories.per_scenario", "sampling.seed",
    "visibility.level", "gate.mode", "burn.on_disclosure",
)


class BuildError(Exception):
    pass


# ----------------------------------------------------------------- parsing

def split_frontmatter(text: str):
    """Return (blocks, body). blocks = [(key, [raw lines])]. Raises if the
    opening --- is not the very first line (the rule these files must obey)."""
    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        raise BuildError("frontmatter must start on line 1 with ---")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].rstrip() == "---")
    except StopIteration:
        raise BuildError("frontmatter is not closed with ---")
    blocks = []
    for raw in lines[1:end]:
        m = re.match(r"^([A-Za-z][\w-]*):(.*)$", raw)
        if m:
            blocks.append((m.group(1), [raw]))
        elif blocks:
            blocks[-1][1].append(raw)
        elif raw.strip():
            raise BuildError("unexpected line in frontmatter: %r" % raw)
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    return blocks, body


def scalar_value(blocks, key):
    for k, raw in blocks:
        if k == key:
            if len(raw) != 1:
                raise BuildError("%s must be a single-line value" % key)
            value = raw[0].split(":", 1)[1].strip()
            if not value or value[0] in ">|":
                raise BuildError("%s must be a single-line value" % key)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
    return None


def yaml_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


# -------------------------------------------------------------- rules

def parse_rule(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        blocks, body = split_frontmatter(text)
    except BuildError as exc:
        raise BuildError("%s: %s" % (path.name, exc))
    meta = {}
    for key, raw in blocks:
        if len(raw) != 1:
            raise BuildError("%s: %s must be a single-line value" % (path.name, key))
        meta[key] = raw[0].split(":", 1)[1].strip()
    for key in ("id", "title", "severity", "applies_to", "status"):
        if not meta.get(key):
            raise BuildError("%s: missing %s" % (path.name, key))
    if meta["id"] != path.stem:
        raise BuildError("%s: id %r must equal the file name" % (path.name, meta["id"]))
    if meta["severity"] not in SEVERITY_ORDER:
        raise BuildError("%s: severity must be high, medium or low" % path.name)
    if meta["status"] not in ("active", "deprecated"):
        raise BuildError("%s: status must be active or deprecated" % path.name)
    applies = [a.strip() for a in meta["applies_to"].split(",") if a.strip()]
    for a in applies:
        if a != "all" and a not in ROLES:
            raise BuildError("%s: unknown role %r in applies_to" % (path.name, a))
    sections = {}
    for m in re.finditer(r"^## (Rule|Why|Instead|Enforce)\s*\n(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL):
        sections[m.group(1).lower()] = m.group(2).strip()
    for needed in ("rule", "why", "instead"):
        if not sections.get(needed):
            raise BuildError("%s: every rule needs a '%s' section" % (path.name, needed.capitalize()))
    if "{{" in body:
        raise BuildError("%s: rules cannot use {{ref:...}} markers; name the role in plain words" % path.name)
    meta["applies_to"] = applies
    meta.update(sections)
    return meta


def load_rules(root: Path = ROOT):
    rules = [parse_rule(p) for p in sorted((root / "rules" / "core").glob("*.md"))]
    ids = [r["id"] for r in rules]
    if len(ids) != len(set(ids)):
        raise BuildError("duplicate rule ids")
    return [r for r in rules if r["status"] == "active"]


def rules_for(rules, role):
    chosen = [r for r in rules if "all" in r["applies_to"] or role in r["applies_to"]]
    return sorted(chosen, key=lambda r: (SEVERITY_ORDER[r["severity"]], r["id"]))


def one_line(text: str) -> str:
    return " ".join(text.split())


def render_rules(rules, role) -> str:
    out = ["## Rules from experience", "",
           "These rules come from real failures. Follow them even when a shortcut seems reasonable.", ""]
    for r in rules_for(rules, role):
        out.append("- **%s.** %s *Why:* %s *Instead:* %s" % (
            r["title"], one_line(r["rule"]), one_line(r["why"]), one_line(r["instead"])))
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ agents

def load_agents(root: Path = ROOT):
    agents = {}
    for role in ROLES:
        path = root / "agents" / ("%s.agent.md" % role)
        if not path.exists():
            raise BuildError("missing agent source: %s" % path.name)
        agents[role] = path.read_text(encoding="utf-8")
    return agents


def expand_includes(body: str, fragments: dict, rules_md: str, who: str) -> str:
    def sub(m):
        key = m.group(1)
        if key == "rules":
            return rules_md.rstrip("\n")
        if key in fragments:
            return fragments[key].rstrip("\n")
        raise BuildError("%s: unknown include %r" % (who, key))
    return INCLUDE_RE.sub(sub, body)


def load_fragments(root: Path = ROOT):
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted((root / "fragments").glob("*.md"))}


def expand_refs(text: str, fmt: str, who: str) -> str:
    """Replace {{ref:role}} / {{name:role}} with the sibling role's name for this format
    (an agent name for claude/copilot, a skill name for skills)."""
    def sub(m):
        kind, role = m.group(1), m.group(2)
        if role not in ROLES:
            raise BuildError("%s: unknown role %r in a reference" % (who, role))
        name, noun = (SKILL_NAMES[role], "skill") if fmt == "skills" else (role, "agent")
        return "`%s`" % name if kind == "name" else "`%s` %s" % (name, noun)
    return REF_RE.sub(sub, text)


# Claude Code has no allowlist that keeps MCP tools, so a capability an agent does not
# declare in its canonical `tools:` list is removed with `disallowedTools:` instead.
CLAUDE_DENY = (("edit", ("Edit", "Write", "NotebookEdit")),
               ("execute", ("Bash",)),
               ("web", ("WebFetch", "WebSearch")))


def claude_disallowed(blocks) -> list:
    declared = scalar_value(blocks, "tools")
    if declared is None:
        return []
    have = {t.strip() for t in declared.strip("[]").split(",") if t.strip()}
    if "search" in have:
        have.add("execute")  # Claude Code has no Glob or Grep tool: listing and searching go through Bash
    return [tool for cap, tools in CLAUDE_DENY if cap not in have for tool in tools]


def render_agent(role: str, text: str, fmt: str, fragments: dict, rules) -> str:
    blocks, body = split_frontmatter(text)
    name = scalar_value(blocks, "name")
    desc = scalar_value(blocks, "description")
    if name != role:
        raise BuildError("%s.agent.md: name %r must equal the role" % (role, name))
    if not desc:
        raise BuildError("%s.agent.md: missing description" % role)
    desc = expand_refs(desc, fmt, role)
    body = expand_refs(expand_includes(body, fragments, render_rules(rules, role), role), fmt, role)
    if fmt == "claude":
        fm = ["name: %s" % name, "description: %s" % yaml_str(desc)]
        denied = claude_disallowed(blocks)
        if denied:
            fm.append("disallowedTools: %s" % ", ".join(denied))
    elif fmt == "copilot":
        fm = []
        for key, raw in blocks:
            if key in SCALAR_KEYS:
                value = desc if key == "description" else scalar_value(blocks, key)
                fm.append("%s: %s" % (key, yaml_str(value)))
            else:
                fm.extend(raw)
    else:
        raise BuildError("unknown format %r" % fmt)
    return "---\n%s\n---\n\n%s" % ("\n".join(fm), body.rstrip("\n") + "\n")


def render_skill(role: str, text: str, fragments: dict, rules, version: str) -> str:
    """Render a role as an Agent Skill (SKILL.md) using only fields from the Agent Skills spec."""
    blocks, body = split_frontmatter(text)
    desc = scalar_value(blocks, "description")
    if scalar_value(blocks, "name") != role or not desc:
        raise BuildError("%s.agent.md: needs name == role and a description" % role)
    desc = expand_refs(desc, "skills", role)
    body = expand_refs(expand_includes(body, fragments, render_rules(rules, role), role), "skills", role)
    fm = ["name: %s" % SKILL_NAMES[role],
          "description: %s" % yaml_str(desc),
          "license: Apache-2.0",
          "metadata:",
          "  version: %s" % yaml_str(version),
          "  bundle: %s" % yaml_str("manifold-base"),
          "  role: %s" % yaml_str(role)]
    return "---\n%s\n---\n\n%s" % ("\n".join(fm), body.rstrip("\n") + "\n")


def validate_skill(name: str, text: str):
    """Check a rendered skill against the Agent Skills specification. Returns a list of problems."""
    problems = []
    try:
        blocks, body = split_frontmatter(text)
    except BuildError as exc:
        return ["%s: %s" % (name, exc)]
    extra = {k for k, _ in blocks} - SKILL_ALLOWED_KEYS
    if extra:
        problems.append("%s: frontmatter keys outside the spec: %s" % (name, sorted(extra)))
    declared = scalar_value(blocks, "name")
    if declared != name:
        problems.append("%s: name %r must equal the folder name" % (name, declared))
    if not declared or len(declared) > 64 or not SKILL_NAME_RE.match(declared):
        problems.append("%s: name must be 1-64 chars of lowercase letters, digits and single hyphens" % name)
    desc = scalar_value(blocks, "description")
    if not desc or len(desc) > 1024:
        problems.append("%s: description must be 1-1024 characters" % name)
    if not body.strip():
        problems.append("%s: empty body" % name)
    if len(text.splitlines()) > 500:
        problems.append("%s: SKILL.md should stay under 500 lines" % name)
    return problems


def role_description(agents: dict, role: str, fmt: str) -> str:
    blocks, _ = split_frontmatter(agents[role])
    return expand_refs(scalar_value(blocks, "description"), fmt, role)


def first_sentence(text: str) -> str:
    text = one_line(text)
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return m.group(1) if m else text


INSTRUCTION_STYLES = ("agents", "skills", "both")


def profile_rules(rules, profile):
    roles = PROFILES[profile]
    return [r for r in rules if "all" in r["applies_to"] or any(x in r["applies_to"] for x in roles)]


def render_instructions_block(agents: dict, rules, style: str = "agents", profile: str = "single") -> str:
    if style not in INSTRUCTION_STYLES:
        raise BuildError("unknown instructions style %r" % style)
    if profile not in PROFILES:
        raise BuildError("unknown profile %r" % profile)
    roles = PROFILES[profile]
    rules = profile_rules(rules, profile)
    lines = [BLOCK_BEGIN]
    if style == "agents":
        lines += ["## Agents", "",
                  "Installed by the Manifold base bundle. Invoke an agent by asking for it by name "
                  "(in Claude Code, `@agent-<name>` also works) or pick it from your tool's agent list.", ""]
        for role in roles:
            lines.append("- **%s**: %s" % (role, first_sentence(role_description(agents, role, "claude"))))
    elif style == "skills":
        lines += ["## Skills", "",
                  "Installed by the Manifold base bundle. Run a skill by asking for it by name "
                  "(in Claude Code, type `/<name>`).", ""]
        for role in roles:
            lines.append("- **%s**: %s" % (SKILL_NAMES[role], first_sentence(role_description(agents, role, "skills"))))
    else:
        lines += ["## Agents and skills", "",
                  "Installed by the Manifold base bundle. Each role is available as an agent "
                  "(in Claude Code, `@agent-<name>`, or from your tool's agent list) and as a skill "
                  "(in Claude Code, `/<name>`). Use one entry point per role.", ""]
        for role in roles:
            lines.append("- **%s** (agent) / **%s** (skill): %s" % (
                role, SKILL_NAMES[role], first_sentence(role_description(agents, role, "claude"))))
    docs = ["- Intents (what and why, with scenario seeds) follow `docs/templates/INTENT_TEMPLATE.md`."]
    if profile in ("build", "single"):
        docs += ["- Plans live in `docs/plans/PHASE_<N>_PLAN.md`. Start from `docs/templates/PHASE_PLAN_TEMPLATE.md`; the coder records its completion summary in the plan.",
                 "- Review policy lives in `REVIEW.md`, written from `docs/templates/REVIEW_TEMPLATE.md`."]
    docs += ["- Test plans follow `docs/templates/PHASE_TEST_PLAN_TEMPLATE.md`.",
             "- Manual walkthrough notes (`WT_<NNN>_<slug>.md`) follow `docs/templates/WT_TEMPLATE.md`; deferred feature gaps go to `FEATURE_GAPS.md`."]
    if profile in ("quality", "single"):
        docs += ["- Behavior scenarios follow `docs/templates/SCENARIO_TEMPLATE.md`; run results follow `docs/templates/SATISFACTION_REPORT_TEMPLATE.md`; thresholds and visibility are settings in `.manifold/quality-settings.json`."]
    lines += ["", "## Plans and templates", ""] + docs + ["", "## Working rules", ""]
    for r in sorted(rules, key=lambda r: (SEVERITY_ORDER[r["severity"]], r["id"])):
        lines.append("- **%s.** %s *Instead:* %s" % (r["title"], first_sentence(r["rule"]), one_line(r["instead"])))
    lines += ["", BLOCK_END, ""]
    return "\n".join(lines)


# -------------------------------------------------------------------- lint

def flatten_settings(data, prefix=""):
    out = {}
    for key, value in data.items():
        if key.startswith("_"):
            continue
        name = prefix + key
        if isinstance(value, dict):
            out.update(flatten_settings(value, name + "."))
        else:
            out[name] = value
    return out


def lint(root: Path = ROOT):
    """Return a list of problem strings (empty means clean)."""
    problems = []

    def guard(fn, *args):
        try:
            return fn(*args)
        except BuildError as exc:
            problems.append(str(exc))
            return None

    rules = guard(load_rules, root)
    agents = guard(load_agents, root)
    fragments = load_fragments(root)
    if rules is not None and agents is not None:
        for role, text in agents.items():
            for fmt in ("claude", "copilot"):
                out = guard(render_agent, role, text, fmt, fragments, rules)
                if out is None:
                    continue
                if not out.startswith("---\n"):
                    problems.append("%s (%s): rendered file does not start with ---" % (role, fmt))
                if "{{" in out or "<!-- include:" in out:
                    problems.append("%s (%s): unresolved placeholder or include" % (role, fmt))
        version = read_version(root)
        for role, text in agents.items():
            out = guard(render_skill, role, text, fragments, rules, version)
            if out is None:
                continue
            if "{{" in out or "<!-- include:" in out:
                problems.append("%s (skills): unresolved placeholder or include" % role)
            problems.extend(validate_skill(SKILL_NAMES[role], out))
        for profile in PROFILES:
            for style in INSTRUCTION_STYLES:
                guard(render_instructions_block, agents, rules, style, profile)
        for role, text in agents.items():
            for _kind, ref in REF_RE.findall(text):
                for profile, roles in PROFILES.items():
                    if role in roles and ref not in roles:
                        problems.append("%s refers to %r, which the %s profile does not install" % (role, ref, profile))
    for profile, roles in PROFILES.items():
        for role in roles:
            if role not in ROLES:
                problems.append("profile %s lists unknown role %r" % (profile, role))
    for role in ROLES:
        if not any(role in roles for roles in PROFILES.values()):
            problems.append("role %s belongs to no profile" % role)
    for name in TEMPLATE_PATHS:
        if not (root / "templates" / name).exists():
            problems.append("missing template: %s" % name)
    for name in SETTINGS_FILES:
        path = root / "config" / name
        if not path.exists():
            problems.append("missing settings file: %s" % name)
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append("%s is not valid JSON: %s" % (name, exc))
            continue
        if name == "quality-settings.json":
            flat = flatten_settings(data)
            for key in QUALITY_SETTINGS_KEYS:
                if key not in flat:
                    problems.append("%s: missing setting %s" % (name, key))
    for path in list((root / "agents").glob("*.md")) + list((root / "rules").rglob("*.md")) + \
            list((root / "templates").glob("*.md")) + list((root / "fragments").glob("*.md")):
        text = path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_TERMS:
            if term in text:
                problems.append("%s contains forbidden term %r" % (path.relative_to(root), term))
    return problems


# ------------------------------------------------------------------- build

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_version(root: Path = ROOT) -> str:
    return (root / "VERSION").read_text(encoding="utf-8").strip()


def build_payload(root: Path = ROOT):
    """Return (files, bundle) where files maps zip-relative path -> bytes."""
    problems = lint(root)
    if problems:
        raise BuildError("lint failed:\n  - " + "\n  - ".join(problems))
    rules = load_rules(root)
    agents = load_agents(root)
    fragments = load_fragments(root)
    version = read_version(root)
    files, claude, copilot, skills, common = {}, [], [], [], []

    for role in ROLES:
        for fmt, tmpl, bucket in (("claude", CLAUDE_AGENT_PATH, claude), ("copilot", COPILOT_AGENT_PATH, copilot)):
            data = render_agent(role, agents[role], fmt, fragments, rules).encode("utf-8")
            target = tmpl.format(name=role)
            src = "payload/%s/%s" % (fmt, target)
            files[src] = data
            bucket.append({"path": target, "src": src, "sha256": sha256(data), "role": role})
    for role in ROLES:
        name = SKILL_NAMES[role]
        data = render_skill(role, agents[role], fragments, rules, version).encode("utf-8")
        target = SKILL_PATH.format(name=name)
        src = "payload/skills/%s" % target
        files[src] = data
        skills.append({"path": target, "rel": "%s/SKILL.md" % name, "src": src, "sha256": sha256(data), "role": role})
    for fname, (target, profiles) in TEMPLATE_PATHS.items():
        data = (root / "templates" / fname).read_bytes()
        src = "payload/common/%s" % target
        files[src] = data
        common.append({"path": target, "src": src, "sha256": sha256(data), "profiles": list(profiles)})
    for fname, (target, profiles) in SETTINGS_FILES.items():
        data = (root / "config" / fname).read_bytes()
        src = "payload/common/%s" % target
        files[src] = data
        common.append({"path": target, "src": src, "sha256": sha256(data), "profiles": list(profiles)})
    for lic in ("LICENSE", "NOTICE"):
        data = (root / lic).read_bytes()
        target = ".manifold/%s" % lic
        src = "payload/common/%s" % target
        files[src] = data
        common.append({"path": target, "src": src, "sha256": sha256(data), "profiles": list(ALL_PROFILES)})
    variants = {}
    for profile in PROFILES:
        variants[profile] = {}
        for style in INSTRUCTION_STYLES:
            block = render_instructions_block(agents, rules, style, profile).encode("utf-8")
            src = "payload/instructions/AGENTS.%s.%s.md" % (profile, style)
            files[src] = block
            variants[profile][style] = {"src": src, "sha256": sha256(block)}

    bundle = {
        "name": "manifold", "bundle": "base", "version": version,
        "roles": list(ROLES), "profiles": {k: list(v) for k, v in PROFILES.items()}, "skills_root": SKILL_ROOT,
        "formats": {"claude": claude, "copilot": copilot, "skills": skills},
        "common": common,
        "instructions": {"begin": BLOCK_BEGIN, "end": BLOCK_END, "variants": variants},
    }
    return files, bundle


def build_zip(root: Path = ROOT, out_dir: Path = None) -> Path:
    files, bundle = build_payload(root)
    version = bundle["version"]
    top = "manifold-base-%s" % version
    out_dir = out_dir or (root / "dist")
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / ("%s.zip" % top)
    entries = dict(files)
    entries["bundle.json"] = (json.dumps(bundle, indent=2, sort_keys=True) + "\n").encode("utf-8")
    for fname in ("README.md", "INSTALL.md", "LICENSE", "NOTICE", "install.py", "install.sh"):
        entries[fname] = (root / fname).read_bytes()
    executable = {"install.py", "install.sh"}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in sorted(entries):
            info = zipfile.ZipInfo("%s/%s" % (top, rel), date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = ((0o755 if rel in executable else 0o644) << 16)
            zf.writestr(info, entries[rel])
    return zip_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="lint only")
    ap.add_argument("--out", default=None, help="output directory (default: dist/)")
    args = ap.parse_args(argv)
    problems = lint(ROOT)
    if problems:
        print("lint failed:")
        for p in problems:
            print("  - " + p)
        return 1
    print("lint ok")
    if args.check:
        return 0
    path = build_zip(ROOT, Path(args.out) if args.out else None)
    print("built %s (%d bytes, sha256 %s)" % (path, path.stat().st_size, sha256(path.read_bytes())[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
