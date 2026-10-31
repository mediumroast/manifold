#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Install the Manifold base bundle into a repository. Standard library only.

Dry-run by default: nothing is written until you pass --apply.

    ./install.sh --target /path/to/repo                 # show the plan
    ./install.sh --target /path/to/repo --apply         # do it
    ./install.sh --target /path/to/repo --format skills # experimental: install as Agent Skills
    ./install.sh --target /path/to/repo --profile quality  # a separate repository for behavior scenarios
    ./install.sh --target /path/to/repo --status        # compare with what is installed
    ./install.sh --target /path/to/repo --uninstall --apply

A file you have modified is never overwritten unless you pass --force, and then
the old version is archived under .manifold/archive/ first.
Exit codes: 0 ok, 1 error, 2 finished but some files were skipped as conflicts.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST_REL = ".manifold/manifest.json"
ARCHIVE_REL = ".manifold/archive"
COMMANDS_STUB = (
    "## Project commands\n\n"
    "<!-- Not recorded yet. An agent will propose the build, verify and test commands it finds in this\n"
    "     repository and ask you to confirm them; keep the confirmed ones here. The managed block above\n"
    "     is overwritten on update; this section is yours. -->\n"
)


class InstallError(Exception):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def safe_dest(target: Path, rel: str) -> Path:
    if rel.startswith(("/", "\\")) or ".." in Path(rel).parts or ":" in rel.split("/")[0]:
        raise InstallError("refusing unsafe path in bundle: %r" % rel)
    dest = (target / rel).resolve()
    try:
        dest.relative_to(target.resolve())
    except ValueError:
        raise InstallError("path escapes the target directory: %r" % rel)
    return dest


def load_bundle() -> dict:
    path = HERE / "bundle.json"
    if not path.exists():
        raise InstallError("bundle.json not found next to install.py; run this from the unzipped bundle")
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(target: Path) -> dict:
    path = target / MANIFEST_REL
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            raise InstallError("%s is not valid JSON; fix or remove it" % MANIFEST_REL)
    return {"files": {}}


FORMAT_NAMES = ("claude", "copilot", "skills")
AGENT_FORMATS = ("claude", "copilot")


def parse_formats(value: str):
    """'claude', 'skills', 'claude,skills', 'both' (claude+copilot) or 'all' -> ordered list of formats."""
    out = []
    for part in [p.strip() for p in value.split(",") if p.strip()]:
        if part == "both":
            items = ["claude", "copilot"]
        elif part == "all":
            items = list(FORMAT_NAMES)
        elif part in FORMAT_NAMES:
            items = [part]
        else:
            raise InstallError("unknown format %r (choose from claude, copilot, skills, both, all)" % part)
        out.extend(i for i in items if i not in out)
    if not out:
        raise InstallError("no format selected")
    return out


def resolve_skills_dir(bundle: dict, manifest: dict, requested):
    """Explicit --skills-dir wins, then the directory a previous install used, then the bundle default."""
    raw = (requested or manifest.get("skills_dir") or bundle.get("skills_root", ".claude/skills")).strip()
    if not raw or raw.startswith(("/", "\\")) or ":" in raw.split("/")[0] or ".." in Path(raw).parts:
        raise InstallError("--skills-dir must be a relative path inside the repository")
    return raw.rstrip("/")


PROFILE_NAMES = ("build", "quality", "single")
DEFAULT_PROFILE = "build"


def profile_roles(bundle: dict, profiles):
    roles = []
    for name in profiles:
        for role in bundle["profiles"][name]:
            if role not in roles:
                roles.append(role)
    return roles


def effective_profile(profiles):
    """The profile whose instruction block describes what is installed: build plus quality is single."""
    names = set(profiles)
    if "single" in names or {"build", "quality"} <= names:
        return "single"
    return next(iter(names))


def selected_entries(bundle: dict, formats, skills_dir=None, profiles=(DEFAULT_PROFILE,)):
    roles = set(profile_roles(bundle, profiles))
    entries = []
    for fmt in formats:
        for e in bundle["formats"][fmt]:
            if e.get("role") not in roles:
                continue
            if fmt == "skills" and skills_dir:
                e = dict(e, path="%s/%s" % (skills_dir, e["rel"]))
            entries.append(e)
    for e in bundle["common"]:
        if set(e.get("profiles", PROFILE_NAMES)) & set(profiles):
            entries.append(e)
    return entries


def styles_of_formats(formats):
    return {"agents" if f in AGENT_FORMATS else "skills" for f in formats}


def installed_styles(recorded: dict):
    styles = set()
    for path in recorded:
        if path.startswith((".claude/agents/", ".github/agents/")):
            styles.add("agents")
        elif path.endswith("/SKILL.md"):
            styles.add("skills")
    return styles


def style_conflict(formats, recorded: dict):
    """True when this run would leave both agents and skills installed for the same roles, newly."""
    before, chosen = installed_styles(recorded), styles_of_formats(formats)
    after = before | chosen
    return len(after) == 2 and bool(chosen - before)


def classify(entry: dict, target: Path, recorded: dict):
    """Return (action, detail). Actions: CREATE, UPDATE, SKIP, CONFLICT."""
    dest = safe_dest(target, entry["path"])
    if not dest.exists():
        return "CREATE", "new file"
    if dest.is_dir():
        return "CONFLICT", "a directory is in the way"
    current = sha256_file(dest)
    if current == entry["sha256"]:
        return "SKIP", "already up to date"
    known = recorded.get(entry["path"])
    if known and current == known:
        return "UPDATE", "newer bundle version; your copy is unmodified"
    if known:
        return "CONFLICT", "you modified this file since it was installed"
    return "CONFLICT", "a different file already exists here and was not installed by this bundle"


def find_instruction_file(target: Path):
    agents, claude = target / "AGENTS.md", target / "CLAUDE.md"
    if agents.exists():
        return agents, False
    if claude.exists():
        return claude, False
    return agents, True


def apply_block(existing: str, block: str, begin: str, end: str) -> str:
    if begin in existing:
        if end not in existing or existing.index(end) < existing.index(begin):
            raise InstallError("found the begin marker without a matching end marker; fix the file by hand")
        pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.DOTALL)
        text = pattern.sub(lambda _m: block, existing, count=1)
    else:
        text = existing.rstrip("\n") + ("\n\n" if existing.strip() else "") + block
    if re.search(r"^## Project commands\s*$", text, re.MULTILINE) is None:
        text = text.rstrip("\n") + "\n\n" + COMMANDS_STUB
    return text


def plan_instructions(bundle: dict, target: Path, style: str = "agents", profile: str = "single"):
    info = bundle["instructions"]
    block = (HERE / info["variants"][profile][style]["src"]).read_text(encoding="utf-8")
    file, creating = find_instruction_file(target)
    existing = "" if creating else file.read_text(encoding="utf-8")
    updated = apply_block(existing, block, info["begin"], info["end"])
    extra = []
    claude = target / "CLAUDE.md"
    if creating and not claude.exists():
        extra.append(("CREATE", "CLAUDE.md", "@AGENTS.md\n"))
    notes = []
    if not creating and file.name == "AGENTS.md" and claude.exists() and "@AGENTS.md" not in claude.read_text(encoding="utf-8"):
        notes.append("CLAUDE.md exists but does not import AGENTS.md; Claude Code reads CLAUDE.md, so add a line containing @AGENTS.md")
    if updated == existing:
        action = "SKIP"
    else:
        action = "CREATE" if creating else "UPDATE"
    return file, updated, action, extra, notes


def timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


KNOWN_ROLES = ("scenario-writer", "bug-coder", "test-planner", "test-coder", "reviewer", "planner", "coder")
AGENT_DIRS = {"claude": (".claude/agents", ".md"), "copilot": (".github/agents", ".agent.md")}


def role_of(stem: str):
    """Return the known role a name ends with ('acme-planner' -> 'planner'), longest match first."""
    for role in KNOWN_ROLES:
        if stem == role or stem.endswith("-" + role):
            return role
    return None


def find_overlapping_agents(bundle: dict, target: Path, formats, recorded: dict, skills_dir=None, profiles=(DEFAULT_PROFILE,)):
    """Existing agents or skills, not installed by this bundle, that fill the same role as one we ship."""
    ours = {e["path"] for e in selected_entries(bundle, formats, skills_dir, profiles)} | set(recorded)
    shipped_roles = set(profile_roles(bundle, profiles))
    found = []
    for fmt in formats:
        if fmt in AGENT_DIRS:
            directory, suffix = AGENT_DIRS[fmt]
            folder = target / directory
            if not folder.is_dir():
                continue
            for path in sorted(folder.iterdir()):
                if not path.is_file() or not path.name.endswith(suffix):
                    continue
                rel = "%s/%s" % (directory, path.name)
                if rel in ours:
                    continue
                role = role_of(path.name[: -len(suffix)])
                if role in shipped_roles:
                    found.append((rel, role))
        elif fmt == "skills" and skills_dir:
            folder = target / skills_dir
            if not folder.is_dir():
                continue
            for path in sorted(folder.iterdir()):
                if not path.is_dir():
                    continue
                rel = "%s/%s" % (skills_dir, path.name)
                if any(p.startswith(rel + "/") for p in ours):
                    continue
                role = role_of(path.name)
                if role in shipped_roles:
                    found.append((rel + "/", role))
    return found


def cmd_status(bundle, target, formats) -> int:
    manifest = load_manifest(target)
    recorded = manifest.get("files", {})
    if not recorded:
        print("No manifest at %s: this bundle is not installed here." % MANIFEST_REL)
        return 0
    print("Installed: %s %s (%s; profile: %s)" % (manifest.get("name", "?"), manifest.get("version", "?"),
                                              ", ".join(manifest.get("formats", [])), ", ".join(manifest.get("profiles", ["build"]))))
    bad = 0
    for rel, known in sorted(recorded.items()):
        dest = safe_dest(target, rel)
        if not dest.exists():
            state = "MISSING"
        elif sha256_file(dest) == known:
            state = "ok"
        else:
            state = "MODIFIED"
        if state != "ok":
            bad += 1
        print("  %-9s %s" % (state, rel))
    print("Bundle in this folder: version %s" % bundle["version"])
    return 0


SINGLE_WARNING = (
    "WARNING   The single profile puts the builders and the behavior-scenario writers in one repository.",
    "          Verification of product behavior is then NOT independent: the AI that builds the code can",
    "          read and edit what judges it. Use it to get started; move scenarios to a separate quality",
    "          repository (install the quality profile there) for independent verification.",
)


def cmd_install(bundle, target, formats, apply_, force, with_instructions, allow_overlap=False, skills_dir_arg=None, profile_arg=None) -> int:
    manifest = load_manifest(target)
    recorded = dict(manifest.get("files", {}))
    skills_dir = resolve_skills_dir(bundle, manifest, skills_dir_arg)
    profiles = sorted(set(manifest.get("profiles", [])) | {profile_arg or (manifest.get("profiles") or [DEFAULT_PROFILE])[0]})
    profile = effective_profile(profiles)
    print("Profile: %s%s" % (profile, "" if profile == profiles[0] and len(profiles) == 1 else " (installed: %s)" % ", ".join(profiles)))
    if profile == "single":
        for line in SINGLE_WARNING:
            print("  " + line)
    overlaps = find_overlapping_agents(bundle, target, formats, recorded, skills_dir, profiles)
    both_styles = style_conflict(formats, recorded)
    entries = selected_entries(bundle, formats, skills_dir, profiles)
    rows = [(e,) + classify(e, target, recorded) for e in entries]
    conflicts = 0
    for entry, action, detail in rows:
        if action == "CONFLICT":
            conflicts += 1
            shown = "CONFLICT" if not force else "REPLACE"
            print("  %-9s %s   (%s%s)" % (shown, entry["path"], detail, "; old version will be archived" if force else "; skipped"))
        else:
            print("  %-9s %s   (%s)" % (action, entry["path"], detail))

    instr = None
    if with_instructions:
        style_now = installed_styles(recorded) | styles_of_formats(formats)
        style_name = "both" if len(style_now) == 2 else next(iter(style_now))
        instr = plan_instructions(bundle, target, style_name, profile)
        file, _updated, action, extra, notes = instr
        print("  %-9s %s   (managed block between manifold markers)" % (action, file.name))
        for act, name, _content in extra:
            print("  %-9s %s   (imports AGENTS.md for Claude Code)" % (act, name))
        for note in notes:
            print("  NOTE      " + note)


    if overlaps:
        print()
        print("  WARNING   Existing agents or skills already fill roles this bundle also provides:")
        for rel, role in overlaps:
            print("              %s   (role: %s)" % (rel, role))
        print("            Two entry points for one role have overlapping descriptions and can confuse routing.")
        print("            Consider keeping only one set (for example install a different --format), or")
        print("            pass --allow-overlap to install anyway.")
    if both_styles:
        print()
        print("  WARNING   This would leave both agents and skills installed for the same roles.")
        print("            Each role would have two entry points. Pick one style per repository, or")
        print("            pass --allow-overlap if you really want both.")

    if (overlaps or both_styles) and apply_ and not allow_overlap:
        raise InstallError("refusing to install next to overlapping agents or skills; nothing was written. Re-run with --allow-overlap to proceed.")

    if not apply_:
        print("\nDry run: nothing was written. Re-run with --apply to install.")
        if conflicts and not force:
            print("%d file(s) would be skipped as conflicts; --force replaces them after archiving." % conflicts)
        return 0

    stamp = timestamp()
    for entry, action, _detail in rows:
        dest = safe_dest(target, entry["path"])
        if action == "SKIP":
            recorded[entry["path"]] = entry["sha256"]
            continue
        if action == "CONFLICT":
            if not force:
                continue
            archive = safe_dest(target, "%s/%s/%s" % (ARCHIVE_REL, stamp, entry["path"]))
            archive.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, archive)
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = (HERE / entry["src"]).read_bytes()
        if sha256_bytes(data) != entry["sha256"]:
            raise InstallError("payload hash mismatch for %s: the bundle is corrupt" % entry["src"])
        dest.write_bytes(data)
        recorded[entry["path"]] = entry["sha256"]

    instr_info = manifest.get("instructions")
    if instr:
        file, updated, action, extra, _notes = instr
        if action != "SKIP":
            file.write_text(updated, encoding="utf-8")
        for _act, name, content in extra:
            (target / name).write_text(content, encoding="utf-8")
        created = set((manifest.get("instructions") or {}).get("created", []))
        if action == "CREATE":
            created.add(file.name)
        for act, name, _content in extra:
            if act == "CREATE":
                created.add(name)
        instr_info = {"file": file.name, "created": sorted(created)}

    kept = sorted(set(manifest.get("formats", [])) | set(formats))
    new_manifest = {
        "name": bundle["name"], "bundle": bundle["bundle"], "version": bundle["version"],
        "installed_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "formats": kept, "profiles": profiles, "files": dict(sorted(recorded.items())),
    }
    if "skills" in kept:
        new_manifest["skills_dir"] = skills_dir
    if instr_info:
        new_manifest["instructions"] = instr_info
    mpath = target / MANIFEST_REL
    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(json.dumps(new_manifest, indent=2) + "\n", encoding="utf-8")

    skipped = conflicts if not force else 0
    print("\nInstalled %s %s into %s" % (bundle["name"], bundle["version"], target))
    if skipped:
        print("%d file(s) were skipped because you modified them. Review them, or re-run with --force." % skipped)
        return 2
    return 0


def cmd_uninstall(bundle, target, apply_) -> int:
    manifest = load_manifest(target)
    recorded = manifest.get("files", {})
    if not recorded:
        print("Nothing to uninstall: no manifest at %s." % MANIFEST_REL)
        return 0
    left = 0
    for rel, known in sorted(recorded.items()):
        dest = safe_dest(target, rel)
        if not dest.exists():
            print("  GONE      %s" % rel)
        elif sha256_file(dest) == known:
            print("  REMOVE    %s" % rel)
            if apply_:
                dest.unlink()
                parent = dest.parent
                while parent != target.resolve() and parent.is_dir():
                    try:
                        parent.rmdir()
                    except OSError:
                        break
                    parent = parent.parent
        else:
            left += 1
            print("  KEEP      %s   (you modified it)" % rel)
    info = manifest.get("instructions")
    if info:
        file = target / info["file"]
        new_text = None
        if file.exists():
            begin, end = bundle["instructions"]["begin"], bundle["instructions"]["end"]
            text = file.read_text(encoding="utf-8")
            if begin in text and end in text:
                print("  REMOVE    managed block in %s" % info["file"])
                pattern = re.compile(r"\n*" + re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.DOTALL)
                new_text = pattern.sub("\n", text, count=1).lstrip("\n")
                if apply_:
                    file.write_text(new_text, encoding="utf-8")
        created = [n for n in info.get("created", []) if (target / n).exists()]
        if created:
            untouched = True
            for name in created:
                current = new_text if (name == info["file"] and new_text is not None) else (target / name).read_text(encoding="utf-8")
                expected = COMMANDS_STUB if name == info["file"] else "@AGENTS.md\n"
                if current.strip() != expected.strip():
                    untouched = False
            if untouched:
                for name in created:
                    print("  REMOVE    %s   (created by the installer, nothing of yours in it)" % name)
                    if apply_:
                        (target / name).unlink()
            else:
                print("  KEEP      %s   (created by the installer, but it now holds your content)" % ", ".join(created))
    if not apply_:
        print("\nDry run: nothing was removed. Re-run with --apply.")
        return 0
    (target / MANIFEST_REL).unlink()
    for d in sorted((p for p in (target / ".manifold").rglob("*") if p.is_dir()), reverse=True):
        try:
            d.rmdir()
        except OSError:
            pass
    try:
        (target / ".manifold").rmdir()
    except OSError:
        pass
    print("\nUninstalled. Archived versions (if any) were left in %s." % ARCHIVE_REL)
    return 2 if left else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n", 2)[2])
    ap.add_argument("--target", default=".", help="repository to install into (default: current directory)")
    ap.add_argument("--format", default="claude",
                    help="what to install: claude, copilot, skills (experimental), both (claude+copilot), all, "
                         "or a comma list such as claude,skills (default: claude)")
    ap.add_argument("--profile", choices=PROFILE_NAMES, default=None,
                    help="which roles to install: build (product repository: planner, coder, bug-coder, reviewer, "
                         "test-planner, test-coder; default), quality (a separate repository for behavior scenarios: "
                         "scenario-writer, test-planner, test-coder) or single (everything in one repository, "
                         "with a warning that verification is not independent)")
    ap.add_argument("--skills-dir", default=None,
                    help="where skills go, relative to the repository (default: .claude/skills; check your tool's documentation)")
    ap.add_argument("--apply", action="store_true", help="write changes (default is a dry run)")
    ap.add_argument("--force", action="store_true", help="replace files you modified, archiving the old versions first")
    ap.add_argument("--allow-overlap", action="store_true", help="install even if agents for the same roles already exist")
    ap.add_argument("--no-instructions", action="store_true", help="do not add the managed block to AGENTS.md / CLAUDE.md")
    ap.add_argument("--status", action="store_true", help="compare installed files with the manifest")
    ap.add_argument("--uninstall", action="store_true", help="remove unmodified installed files and the managed block")
    args = ap.parse_args(argv)
    try:
        target = Path(args.target).expanduser()
        if not target.is_dir():
            raise InstallError("target is not a directory: %s" % target)
        target = target.resolve()
        bundle = load_bundle()
        formats = parse_formats(args.format)
        if not (target / ".git").exists() and not args.status:
            print("NOTE: %s does not look like a git repository; changes will not be easy to review or undo.\n" % target)
        if args.status:
            return cmd_status(bundle, target, formats)
        if args.uninstall:
            return cmd_uninstall(bundle, target, args.apply)
        return cmd_install(bundle, target, formats, args.apply, args.force, not args.no_instructions, args.allow_overlap, args.skills_dir, args.profile)
    except InstallError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
