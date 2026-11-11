#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Manifold tool-boundary guard. Standard library only; written for Python 3.10 or newer.

A client runs this file before a tool call (a pre-tool hook) and passes the call as JSON on
standard input. The guard enforces three rules and refuses the call when one is broken:

1. Shell writes (rule `no-heredocs`): a shell command may not write or change file contents
   (heredocs, `python - <<`, `sed -i`, `perl -i`, `tee`, `>` or `>>` into a file, `python -c`
   or `node -e` and similar code that writes, a program piped into an interpreter) and may not
   write to `/tmp` or `/private/tmp`. The refusal
   names the sanctioned route: create or edit with the Write or Edit tool, or write a snippet
   with Write to `.manifold/scratch/` and run the file.
2. Write allowlist (rules `write-allowlist` and `protected-file`): the `reviewer` may write only
   `docs/plans/REVIEW_PLAN_<N>.md`; the `coordinator` may write `docs/agents/*-failures.md`
   and create (not replace) `intent/INT-*.md`. The identity is normalised (`Reviewer`,
   `manifold:reviewer` are `reviewer`). A file inside any checkout (the main checkout or a linked worktree, wherever
   it sits on disk) of the same git repository as the project directory is judged for these two allowlists relative
   to that checkout's root, because the hook's project directory can be the main checkout or one worktree while the
   agent works in another; the protected files and definitions below are still judged by the end of the path.
3. Protected files (rule `protected-file`), for every agent including one with no identity, against
   Write/Edit and the shell, after resolving `./`, `..`, case and symlinks:
   - always, with no exception route: `.manifold/guard-allow.json`, `.manifold/guard-log.jsonl`,
     `.manifold/hooks/guard.py` (PROTECTED_FILES);
   - unless a human grants a path exception: `.claude/agents/*.md`, `.claude/settings.json`,
     `.claude/settings.local.json`, `.claude/skills/<name>/SKILL.md`, `.github/agents/*.agent.md`,
     `.github/hooks/manifold-guard.json` (PROTECTED_DEFINITIONS).
   Definitions are protected wherever they are, inside or outside the project, by the end of the path
   (a Write to another checkout's `.claude/agents/coder.md` is refused), and `.github` itself is protected
   against the shell (`rm -rf .github`; its other contents are not).
   The shell may only read these files and their directories (cat, grep, ls, diff, git status/diff/log ...).
   Root `AGENTS.md` and `CLAUDE.md` are not protected: the installer writes the managed rules block there,
   but the same files carry "Project commands" and the "Review process" section that agents edit routinely;
   a change to rule text stays visible in review and in the "Rule exceptions" comparison (owner, 2026-11-07).

Usage as a hook:  python3 guard.py --client claude|copilot   (hook JSON on stdin)

Claude Code: a refusal exits 2 with the message on stderr (the model sees it). An allowed call
exits 0 with no output. Copilot: a refusal prints `{"permissionDecision": "deny",
"permissionDecisionReason": ...}` on stdout and exits 0; the Copilot field names and tool names
are normalised here, but they are unverified in VS Code Local (see docs/agents/harness-capabilities.md).

Fail closed: input the guard cannot read, and any exception inside the guard, block the call (exit 2 for
Claude Code, the deny JSON for Copilot) with "Manifold guard failed: <type>: <text>. This tool call is
blocked; tell a human." and a log line with rule `guard-error`. The hook command in the agent definition
(build.GUARD_COMMAND) also blocks when this file is missing or does not exit 0 or 2.

A human exception is an entry in `.manifold/guard-allow.json`, a JSON list of objects with
`pattern`, `reason`, `granted_by` and `date`, all non-empty, plus two optional fields:
- `scope`: `"command"` (the default when absent) or `"path"`.
- `expires`: `"YYYY-MM-DD"`, required for `"scope": "path"`, unused for command entries. A path entry holds
  through the whole of that date (UTC) and grants nothing after it, or when `expires` is missing or not a real date.
A command entry's `pattern` is a regular expression that must match the whole command, so a second command
appended to an allowed one is still judged. A path entry's `pattern` must match the whole normalised
project-relative path (for a path outside the project, the whole path as given); it lifts a protected definition and the reviewer and coordinator allowlist refusals, never
the three PROTECTED_FILES, and never a shell command. An entry missing a field, or an unreadable file, grants nothing.

Every refusal appends `{time, rule, tool, agent_type, command}` to `.manifold/guard-log.jsonl`
(local, git-ignored); a use of an exception appends the same line with rule `exception-used`.
`command` is the first 80 characters, which keeps secrets out.

Residual gaps (stated, not fixed), one per line:
- a script that writes when it is run from a file (`bash s.sh`, `bash < s.sh`, `source s.sh`) is not read;
- a command or a path built from a variable (`eval $CMD`, `sh -c "$CMD"`, `X=.manifold/guard-allow.json; cp a $X`);
- the scratch route reaches protected files: a snippet written with Write to `.manifold/scratch/` and run is not
  read, so it can write `.manifold/guard-allow.json` (a path exception) and the agent can then Edit its own
  definition; the control is the coordinator's listing of every entry in `.manifold/guard-allow.json` and its review
  of each `exception-used` log line against an entry a human granted;
- code is matched, not understood: `-c`/`--eval` code is refused when it names a protected path or an API on the
  list, so a path built from parts (`"op"+"en"`) or an API not on the list passes;
- git commands that rewrite files without naming them (`git stash`, `reset --hard`, `checkout`, `restore`, `merge`,
  `pull`, `rebase`, `cherry-pick`) are allowed, they are normal work;
- wrappers and stdin: `script -c`, `su -c` and `xargs` fed from standard input are not followed;
- Copilot output may carry the guard's partial output before the fallback deny JSON;
- kept refusals: `cd` into a protected directory, and `python3 .manifold/hooks/guard.py` typed by an agent (the
  client runs the hook);
- command substitution inside double quotes;
- `sed` with a `w` command (it cannot be told from text without parsing sed);
- other languages, editors and tools than the ones named in the shell rule (for example `dd of=`, `curl -o`, `wget -O`, `tar x`, `unzip`, `install`, `python3 -m json.tool in out` are allowed although they write files);
- a `cd` in an earlier call followed by a bare file name;
- worktrees: a checkout counts as part of the project's repository only when its `.git` proves it (a `.git` directory, or a `.git` file whose git directory sits in the common directory's `worktrees/` folder, holds `commondir` and points back at that `.git` file); a checkout of another repository, a forged or unreadable `.git`, or a path in no checkout is judged as a path outside the project and matches no allowlist; whoever can write inside the repository's own `.git` directory can forge that proof; `.manifold/guard-allow.json` and `.manifold/guard-log.jsonl` are always the project directory's own, never another checkout's, so every checkout that can be a project directory needs its own installed guard;
- tools the guard does not look at;
- clients and sessions the hook does not cover: the main session under per-agent hooks, plugin agents, and
  Copilot, where enforcement is unverified;
- Copilot agent identity is unverified, so the reviewer and coordinator allowlists may not apply there, while
  the protected files apply to every identity;
- root `AGENTS.md` and `CLAUDE.md` are not protected (above).
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import posixpath
import re
import sys

RULE_SHELL = "no-heredocs"
RULE_ALLOWLIST = "write-allowlist"
RULE_PROTECTED = "protected-file"
RULE_ERROR = "guard-error"
RULE_EXCEPTION_USED = "exception-used"

SCRATCH = ".manifold/scratch/"
ALLOW_FILE = ".manifold/guard-allow.json"
LOG_FILE = ".manifold/guard-log.jsonl"
ALLOW_FIELDS = ("pattern", "reason", "granted_by", "date")

SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
# Wrapper command -> options that take a value (the next word is not the command). Any other option is judged
# both ways: a flag, or an option with a value.
WRAPPERS = {
    "env": {"-u", "-C", "-S", "--unset", "--chdir"},
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-U"},
    "nice": {"-n"},
    "timeout": {"-s", "-k"},
    "stdbuf": {"-i", "-o", "-e"},
    "xargs": {"-I", "-n", "-P", "-L", "-d", "-a", "-E", "-s"},
    "time": {"-f", "-o"},
    "command": set(), "nohup": set(), "exec": set(), "builtin": set(), "uvx": set(), "npx": set(),
}
# Wrappers named by two words: `uv run`, `poetry run`, `pipx run`, `pyenv exec`.
TWO_WORD_WRAPPERS = {"uv": "run", "poetry": "run", "pipx": "run", "pyenv": "exec"}
ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
INTERPRETERS = {"python", "node", "nodejs", "deno", "ruby", "perl", "php"}
READ_ONLY = {"cat", "head", "tail", "less", "more", "wc", "grep", "egrep", "fgrep", "rg", "ls", "stat", "file",
             "diff", "cmp", "sha256sum", "shasum", "echo", "printf", "test", "[", "[[", "find", "git",
             # reading forms only: the write forms (sed -i, awk -i inplace, awk redirects and system()) are judged
             # in scan_command before touches_protected runs
             "sed", "awk", "jq", "comm"}
READ_GIT = {"status", "diff", "log", "show", "blame", "ls-files", "check-ignore", "rev-parse", "grep", "add", "commit"}
BARE_PROTECTED = {"guard-allow.json", "guard-log.jsonl", "manifold-guard.json"}
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")"}
REDIRECT_OUT = {">", ">>", ">|", "&>", "&>>"}
HARMLESS_TARGETS = {"/dev/null", "/dev/stderr", "/dev/stdout", "/dev/tty"}
TMP_RE = re.compile(r"^(/private)?/tmp(/|$)")
SED_INPLACE_RE = re.compile(r"^-[nEersz]*i")
PERL_INPLACE_RE = re.compile(r"^-[pnalswcT0-9]*i")
CODE_WRITE_RE = re.compile(
    r"open\s*\(\s*[^,()]+,\s*(mode\s*=\s*)?['\"][rbtU]*[wax+]"      # python open(f, 'w')
    r"|open\s*\([^)]*mode\s*=\s*['\"][rbtU]*[wax+]"                  # python open(f, mode='w')
    r"|\.open\s*\(\s*['\"][rbtU]*[wax+]"                              # Path(f).open('w')
    r"|\.write_text\s*\(|\.write_bytes\s*\("
    r"|\bshutil\.(copy|copy2|copyfile|copytree|move|rmtree)\b"        # python
    r"|\bos\.(system|popen|rename|replace|remove|unlink|rmdir|truncate|mkdir|makedirs|symlink|link|exec\w*|spawn\w*)\b"
    r"|\.(touch|mkdir|rename|unlink|rmdir|symlink_to)\s*\("
    r"|shell\s*=\s*True"
    r"|\bsubprocess\.|__import__|(?<![.\w])(exec|eval)\s*\("                                                   # run anything
    r"|\bos\.open\b|\bfileinput\b|\bimportlib\b|\bpty\.|\bdistutils\b"
    r"|\blogging\.(File|Rotating|Timed)\w*Handler\b"
    r"|(zipfile|tarfile)[\s\S]*\.extract(all)?\s*\("
    r"|(ZipFile|TarFile|tarfile\.open)\s*\([^)]*,\s*['\"][wax]"
    r"|sqlite3\.connect\s*\((?!\s*['\"]:memory:['\"])"
    r"|\b(fs|fsp|promises)\s*\.\s*(write|append|copy|cp|rename|rm|unlink|mkdir|rmdir|truncate|symlink|link)\w*"  # node
    r"|\b(writeFile|writeFileSync|appendFile|appendFileSync|copyFile|copyFileSync|cpSync|rmSync|unlinkSync"
    r"|renameSync|mkdirSync|rmdirSync|truncateSync|symlinkSync|createWriteStream)\b"
    r"|\bchild_process\b"
    r"|\bDeno\.(write|remove|rename|mkdir|copy|create|truncate|symlink|link)\w*"                               # deno
    r"|\bFile\.(write|binwrite|delete|rename|unlink|symlink)\b|\bFile\.open\s*\([^)]*,\s*['\"][wa+]"          # ruby
    r"|\bIO\.(write|binwrite)\b|\bFileUtils\b"
    r"|open\s*\(?\s*[A-Za-z_$][\w$]*\s*,\s*['\"]\s*\+?>|\bunlink\b"                                           # perl
    r"|(?<![.\w])(file_put_contents|fwrite|rename|mkdir|rmdir|copy|touch|chmod)\s*\("                         # php
    r"|(?<![.\w])fopen\s*\([^)]*,\s*['\"][wax+]"
    r"|(?<![.\w])(system|passthru|shell_exec)\s*\(")
# `.replace(` is str.replace in most code, so it counts only with Path or pathlib in the same code (CP2b R9).
PATH_REPLACE_RE = re.compile(r"\.replace\s*\(")
# A protected name inside `-c`/`--eval` code or a here-string is refused whatever the API (CP2b R4); reading goes
# through cat, grep or the Read tool. Case-insensitive substrings; `.manifold/scratch/` does not match.
CODE_PROTECTED_NAMES = (".manifold/guard-allow.json", ".manifold/guard-log.jsonl", ".manifold/hooks", "guard-allow.json",
                        "guard-log.jsonl", "manifold-guard.json", ".claude/agents", ".claude/settings", ".claude/skills",
                        ".github/agents", ".github/hooks")
# The mechanism itself: always protected, no exception route.
PROTECTED_FILES = (".manifold/guard-allow.json", ".manifold/guard-log.jsonl", ".manifold/hooks/guard.py")
PROTECTED_RE = re.compile(r"(^|/)\.manifold/(guard-allow\.json|guard-log\.jsonl|hooks/guard\.py)$", re.IGNORECASE)
# The skill folder names build.py writes (build.SKILL_NAMES values); a test compares this list with build.py.
SKILL_DIRS = ("plan-change", "execute-plan", "fix-bug", "review-change", "plan-tests", "write-tests", "write-scenarios",
              "coordinate-cycle")
# The agent definitions and hook setup: protected unless a human grants a path exception. Anchored at the
# project root, matched on the normalised lower-case relative path.
PROTECTED_DEFINITIONS = (
    r"\.claude/agents/[^/]+\.md",
    r"\.claude/settings\.json",
    r"\.claude/settings\.local\.json",
    r"\.claude/skills/(%s)/skill\.md" % "|".join(SKILL_DIRS),
    r"\.github/agents/[^/]+\.agent\.md",
    r"\.github/hooks/manifold-guard\.json",
)
# Judged by the end of the normalised path, like PROTECTED_RE, so a definition outside the project is recognised too.
DEFINITION_RE = re.compile(r"(^|/)(%s)$" % "|".join(PROTECTED_DEFINITIONS))
# Directories whose contents the shell may only read (T14d).
PROTECTED_DIRS = (".manifold", ".manifold/hooks", ".claude", ".claude/agents", ".github/hooks", ".github/agents")
# Directories protected as a whole against the shell: the directory itself, not its other contents (`.github/workflows`
# stays writable; `.github/hooks` and `.github/agents` are in PROTECTED_DIRS).
EXACT_PROTECTED_DIRS = (".github",)
DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\Z")  # \Z, not $: "2026-11-07\n" is not a date
REVIEW_FILE_RE = re.compile(r"^docs/plans/REVIEW_PLAN_[0-9]+\.md$")
FAILURES_RE = re.compile(r"^docs/agents/[^/]+-failures\.md$")
INTENT_RE = re.compile(r"^intent/INT-[^/]+\.md$")
MAX_DEPTH = 5

BASH_TOOLS = {"bash", "shell", "powershell", "terminal", "runinterminal", "run_in_terminal", "execute"}
WRITE_TOOLS = {"write", "edit", "multiedit", "notebookedit", "create", "create_file", "edit_file",
               "str_replace_editor", "replace_string_in_file", "insert_edit_into_file"}
PATH_KEYS = ("file_path", "filePath", "path", "notebook_path")


# ------------------------------------------------------------------- messages

def shell_message(reason):
    return ("Refused by the Manifold guard (rule %s): %s. Do not write files from the shell. "
            "Create or edit files with the Write or Edit tool (Edit with replace_all for renames). "
            "For a throwaway snippet, create it with Write in %s (or the scratchpad folder the session names) "
            "and run the file. Do not work around this block. If you need an exception, ask a human to add "
            "it to %s (pattern, reason, granted_by, date), and say in your report what you already tried."
            % (RULE_SHELL, reason, SCRATCH, ALLOW_FILE))


def protected_message(path):
    return ("Refused by the Manifold guard (rule %s): %s is a guard file, an agent definition or hook setup; "
            "only a human changes it. Do not work around this block. Tell a human what you need." % (RULE_PROTECTED, path))


def definition_message(path):
    return ("Refused by the Manifold guard (rule %s): %s is part of the agent definitions or hook setup; "
            "only a human changes it. Ask a human to add a path exception to %s (scope path, pattern, reason, "
            "granted_by, date, expires; for a path outside the project the pattern must match the whole path). "
            "Do not work around this block." % (RULE_PROTECTED, path, ALLOW_FILE))


def allowlist_message(agent_type, allowed, path):
    return ("Refused by the Manifold guard (rule %s): the %s agent may write only %s, not %s. "
            "Do not work around this block. If the file is yours to change, tell a human, who may grant an "
            "exception in %s (scope path, with expires)." % (RULE_ALLOWLIST, agent_type, allowed, path, ALLOW_FILE))


# ------------------------------------------------------------------ tokenizer

def tokenize(command):
    """Split a shell command into ('w', word) and ('op', operator) tokens, tracking quotes so that
    an operator inside quotes stays part of a word. File-descriptor duplications (2>&1, >&2) vanish."""
    toks, buf, state = [], [], {"quoted": False, "dbl": False}
    quote = None
    i, n = 0, len(command)

    def flush():
        if buf or state["quoted"]:
            word = "".join(buf)
            toks.append(("w", word))
            # inside [[ ... ]] a < or > compares strings; only when a closing ]] follows, so an unclosed [[ cannot
            # hide a redirect for the rest of the command
            if word == "[[" and not state["quoted"] and re.search(r"\s\]\]", command[i:]):
                state["dbl"] = True
            elif word == "]]":
                state["dbl"] = False
        del buf[:]
        state["quoted"] = False

    def dup_at(pos):
        m = re.match(r"&(\d+|-)", command[pos:])
        return len(m.group(0)) if m else 0

    while i < n:
        c = command[i]
        if quote == "'":
            if c == "'":
                quote = None
            else:
                buf.append(c)
        elif quote == '"':
            if c == '"':
                quote = None
            elif c == "\\" and i + 1 < n and command[i + 1] in '"\\$`\n':
                i += 1
                buf.append(command[i])
            else:
                buf.append(c)
        elif c in " \t":
            flush()
        elif c == "(" and command.startswith("((", i) and (not buf or buf == ["$"]) and arith_end(command, i) > 0:
            end = arith_end(command, i)  # (( ... )) and $(( ... )) are arithmetic: a < or > in them is a comparison
            buf.append(command[i:end])
            i = end - 1
        elif c == "\n":
            state["dbl"] = False
            flush()
            toks.append(("op", ";"))
        elif c == "\\":
            if i + 1 < n:
                i += 1
                if command[i] != "\n":
                    buf.append(command[i])
        elif c == "'" or c == '"':
            quote = c
            state["quoted"] = True
        elif c == "#" and not buf and not state["quoted"]:
            while i + 1 < n and command[i + 1] != "\n":
                i += 1
        elif c == "`":
            flush()
            toks.append(("op", ";"))
        elif c in "<>" and state["dbl"]:
            buf.append(c)
        elif c in "<>":
            if buf and not state["quoted"] and "".join(buf).isdigit():
                del buf[:]  # a file descriptor number such as the 2 in 2>&1
            else:
                flush()
            op = None
            if c == ">":
                if command.startswith(">>", i):
                    op = ">>"
                    i += 1
                elif command.startswith(">|", i):
                    op = ">|"
                    i += 1
                elif command.startswith(">&", i):
                    skip = dup_at(i + 1)
                    if skip:
                        i += skip
                    else:
                        op = ">"  # `>& file` writes the file
                        i += 1
                else:
                    op = ">"
            else:
                if command.startswith("<<<", i):
                    op = "<<<"
                    i += 2
                elif command.startswith("<<", i):
                    op = "<<"
                    i += 1
                    if command.startswith("-", i + 1):
                        i += 1
                elif command.startswith("<&", i):
                    i += dup_at(i + 1)
                else:
                    op = "<"
            if op:
                toks.append(("op", op))
        elif c == "&":
            flush()
            if command.startswith("&&", i):
                op = "&&"
                i += 1
            elif command.startswith("&>>", i):
                op = "&>>"
                i += 2
            elif command.startswith("&>", i):
                op = "&>"
                i += 1
            else:
                op = "&"
            toks.append(("op", op))
        elif c == "|":
            flush()
            if command.startswith("||", i):
                i += 1
                toks.append(("op", "||"))
            else:
                if command.startswith("|&", i):
                    i += 1
                toks.append(("op", "|"))
        elif c in ";()":
            if c == ";":
                state["dbl"] = False
            flush()
            toks.append(("op", c))
        else:
            buf.append(c)
        i += 1
    flush()
    return toks


def arith_end(command, i):
    """`command[i:]` starts with `((`. Return the index just after the `))` that closes it when the text between is
    balanced (arithmetic), else -1 (a nested subshell such as `((a) | (b))`)."""
    depth, k = 0, i + 2
    while k < len(command):
        c = command[k]
        if c == "(":
            depth += 1
        elif c == ")":
            if depth == 0:
                return k + 2 if command.startswith("))", k) else -1
            depth -= 1
        k += 1
    return -1


def split_segments(toks):
    """Return a list of (segment, piped): `piped` is True when the segment follows a `|`."""
    segs, seg, piped = [], [], False
    for kind, text in toks:
        if kind == "op" and text in SEPARATORS:
            segs.append((seg, piped))
            seg, piped = [], text == "|"
        else:
            seg.append((kind, text))
    segs.append((seg, piped))
    return segs


# --------------------------------------------------------------- shell scanning

def is_tmp(path):
    return bool(TMP_RE.match(path))


class ProtectedHit(str):
    """A scan reason that names a protected file or directory (judged with `protected_message`, not the shell rule)."""


class Stdin(object):
    """Where the standard input of one command comes from: a pipe, a here-string, or a file."""

    def __init__(self, piped=False, here=None, from_file=False):
        self.piped, self.here, self.from_file = piped, here, from_file


def scan(command, depth=0):
    """Return a reason string when the command writes files, else None."""
    if depth > MAX_DEPTH:
        return "a command nested too deeply to inspect"
    for seg, piped in split_segments(tokenize(command)):
        reason = scan_segment(seg, depth, piped)
        if reason:
            return reason
    return None


def scan_segment(seg, depth, piped=False):
    words, j = [], 0
    stdin = Stdin(piped=piped)
    while j < len(seg):
        kind, text = seg[j]
        if kind == "op":
            if text in REDIRECT_OUT:
                target = seg[j + 1][1] if j + 1 < len(seg) and seg[j + 1][0] == "w" else None
                j += 1
                if target is not None and target not in HARMLESS_TARGETS:
                    if is_tmp(target):
                        return "a redirect (%s) into %s, a /tmp path" % (text, target)
                    return "a redirect (%s) into a file" % text
            elif text == "<<":
                return "a heredoc (<<)"
            elif text in ("<", "<<<"):
                if j + 1 < len(seg) and seg[j + 1][0] == "w":
                    if text == "<<<":
                        stdin.here = seg[j + 1][1]
                    else:
                        stdin.from_file = True
                j += 1
        else:
            words.append(text)
        j += 1
    return scan_words(words, depth, stdin)


def command_starts(words, i=0, depth=0):
    """Indexes in `words` where the real command may start, after assignments and wrapper commands. A wrapper
    option that is not in the table of options with a value is judged both ways (flag, or option with a value)."""
    if depth > MAX_DEPTH:
        return []
    while i < len(words) and ASSIGN_RE.match(words[i]):
        i += 1
    if i >= len(words):
        return []
    base = posixpath.basename(words[i])
    if base in TWO_WORD_WRAPPERS:
        if i + 1 < len(words) and words[i + 1] == TWO_WORD_WRAPPERS[base]:
            return wrapper_starts(words, i + 2, set(), base, depth)
        return [i]
    if base in WRAPPERS:
        return wrapper_starts(words, i + 1, WRAPPERS[base], base, depth)
    return [i]


def wrapper_starts(words, j, value_options, base, depth):
    starts, seen_duration = [], False
    while j < len(words):
        w = words[j]
        if w == "--":
            j += 1
            break
        if w.startswith("-") and len(w) > 1:
            if w in value_options:
                j += 2
            elif "=" in w:
                j += 1
            else:
                starts.extend(command_starts(words, j + 2, depth + 1))  # the next word may be this option's value
                j += 1
            continue
        if base == "timeout" and not seen_duration and w[:1].isdigit():
            seen_duration = True
            j += 1
            continue
        if base == "env" and ASSIGN_RE.match(w):
            j += 1
            continue
        break
    starts.extend(command_starts(words, j, depth + 1))
    return starts


def code_options(cmd, args):
    """Return (codes, kind) for an interpreter or shell: the program text given on the command line, and where the
    program comes from: 'code', 'script', 'module' or 'stdin'."""
    codes = []
    if cmd == "python":
        k = 0
        while k < len(args):
            a = args[k]
            if a == "-":
                return codes, "stdin"
            if a == "--":
                return codes, ("script" if k + 1 < len(args) else "stdin")
            if a.startswith("--"):
                k += 1
                continue
            if a.startswith("-"):
                cluster = a[1:]
                for idx, ch in enumerate(cluster):
                    if ch == "c":
                        rest = cluster[idx + 1:]
                        if rest:
                            return [rest], "code"
                        return (args[k + 1:k + 2], "code")
                    if ch == "m":
                        return codes, "module"
                    if ch in "WXQ":
                        if not cluster[idx + 1:]:
                            k += 1
                        break
                k += 1
                continue
            return codes, "script"
        return codes, "stdin"
    if cmd in SHELLS:
        for k, a in enumerate(args):
            if a.startswith("-") and not a.startswith("--") and "c" in a[1:]:
                return args[k + 1:k + 2], "code"
        plain = [a for a in args if a != "-s" and not a.startswith("-")]
        return codes, ("script" if plain else "stdin")
    if cmd == "deno":
        plain = [a for a in args if not a.startswith("-")]
        if plain[:1] == ["eval"]:
            return plain[1:2], "code"
        return codes, ("script" if plain else "stdin")
    code_re = {"node": re.compile(r"^-(e|p|pe|ep)$"), "nodejs": re.compile(r"^-(e|p|pe|ep)$"),
               "ruby": re.compile(r"^-[nplacswWvdyx0-9]*e$"), "php": re.compile(r"^-r$"),
               "perl": re.compile(r"^-[nplaswWtTuUcEdfFi0-9.]*[eE]$")}[cmd]
    for k, a in enumerate(args):
        if code_re.match(a):
            codes.extend(args[k + 1:k + 2])
        elif a in ("--eval", "--print"):
            codes.extend(args[k + 1:k + 2])
        elif a.startswith(("--eval=", "--print=")):
            codes.append(a.split("=", 1)[1])
    if codes:
        return codes, "code"
    plain = [a for a in args if not a.startswith("-")]
    return codes, ("script" if plain and "-" not in args else "stdin")


def code_names_protected(code):
    """The protected name the interpreter code contains (case-insensitive), else None."""
    text = code.lower()
    return next((name for name in CODE_PROTECTED_NAMES if name in text), None)


def code_writes(code):
    return bool(CODE_WRITE_RE.search(code) or (PATH_REPLACE_RE.search(code) and ("Path" in code or "pathlib" in code)))


def code_reason(cmd, code):
    """Judge interpreter code (not shell): a protected name first, then the API patterns."""
    name = code_names_protected(code)
    if name:
        return ProtectedHit(name)
    if code_writes(code):
        return "%s code that writes, copies, moves or deletes files, or runs a command" % cmd
    return None


def program_reason(cmd, args, depth, stdin):
    """Judge the program an interpreter or shell is given: on the command line, as a here-string or from a pipe."""
    codes, kind = code_options(cmd, args)
    for code in codes:
        if cmd in SHELLS:
            reason = scan(code, depth + 1)
            if reason:
                return reason
        else:
            reason = code_reason(cmd, code)
            if reason:
                return reason
    if kind == "stdin":
        if stdin.here is not None:
            if cmd in SHELLS:
                return scan(stdin.here, depth + 1)
            reason = code_reason(cmd, stdin.here)
            if reason:
                return reason
        elif stdin.piped and not stdin.from_file:
            return ("a program read from a pipe into %s cannot be inspected; write it with Write to %s and run the file"
                    % (cmd, SCRATCH))
    return None


AWK_RE = re.compile(r"^[gmn]?awk$")
AWK_WRITE_RE = re.compile(r"\bsystem\s*\(|\bprintf?\b[^;}]*?(>>?|\|)")


def target_directory(args):
    """For cp, mv, install, ln, rsync: return (destination or None, other plain arguments) when `-t`, a cluster
    ending in t, or `--target-directory` names the destination."""
    rest, dest, k = [], None, 0
    while k < len(args):
        a = args[k]
        if a == "--target-directory" or re.match(r"^-[A-Za-z]*t$", a):
            dest = args[k + 1] if k + 1 < len(args) else None
            k += 2
            continue
        if a.startswith("--target-directory="):
            dest = a.split("=", 1)[1]
        elif not a.startswith("-"):
            rest.append(a)
        k += 1
    return dest, rest


def find_reason(args, depth):
    if "-delete" in args:
        return "find -delete removes files"
    for k, a in enumerate(args):
        if a in ("-exec", "-execdir", "-ok", "-okdir"):
            run = []
            for b in args[k + 1:]:
                if b in (";", "+"):
                    break
                run.append(b)
            reason = scan_words(run, depth + 1, Stdin())
            if reason:
                return reason
    return None


def git_subcommand(args):
    k = 0
    while k < len(args):
        if args[k] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace"):
            k += 2
        elif args[k].startswith("-"):
            k += 1
        else:
            return args[k], args[k + 1:]
    return "", []


def is_read_only(words, i):
    cmd = re.sub(r"[0-9.]+$", "", posixpath.basename(words[i]))
    args = words[i + 1:]
    if cmd == "find":
        return not any(a in ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprintf", "-fls") for a in args)
    if cmd == "git":
        sub, _ = git_subcommand(args)
        return sub in READ_GIT
    return cmd in READ_ONLY


def norm_word(word):
    w = re.sub(r"/{2,}", "/", word.replace("\\", "/"))
    return posixpath.normpath(w).lower() if w else w


def under(norm, directory):
    return norm == directory or norm.endswith("/" + directory)


def protected_dirs():
    return PROTECTED_DIRS + (".claude/skills",) + tuple(".claude/skills/" + n for n in SKILL_DIRS)


def _brace_groups(word, limit):
    """Expand the first comma list in `word` (`a{b,c}d`), then the rest, recursively. A brace group without a
    top-level comma (`{}`, `{a}`, `${VAR}`, `${V:-a,b}`) is left as written. Raises ValueError for unbalanced
    braces and OverflowError when more than `limit` words would result."""
    start = 0
    while True:
        i = word.find("{", start)
        if i < 0:
            return [word]
        depth, j, commas = 0, i, []
        while j < len(word):
            c = word[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            elif c == "," and depth == 1:
                commas.append(j)
            j += 1
        else:
            raise ValueError("unbalanced braces")
        if commas and not (i > 0 and word[i - 1] == "$"):
            bounds = [i] + commas + [j]
            out = []
            for a, b in zip(bounds, bounds[1:]):
                out.extend(_brace_groups(word[:i] + word[a + 1:b] + word[j + 1:], limit))
                if len(out) > limit:
                    raise OverflowError("too many words")
            return out
        start = i + 1


def expand_braces(word, limit=64):
    """The words a shell would make of `word` by brace expansion (comma lists, nested, leading). A word with
    unbalanced braces, or one that would expand to more than `limit` words, is judged like a glob by its literal
    prefix (the text before the first `{`, then `*`)."""
    if "{" not in word:
        return [word]
    try:
        return _brace_groups(word, limit)
    except (ValueError, OverflowError):
        return [word.split("{", 1)[0] + "*"]


def protected_name(word):
    """Return the normalised path when `word` (or one of its brace expansions) names a protected file, definition or
    directory, or is a glob that reaches one, else None."""
    for expanded in expand_braces(word):
        hit = _protected_name(expanded)
        if hit:
            return hit
    return None


def _protected_name(word):
    """One word, no brace expansion. A part after `=` (`of=...`, `--output=...`) is judged too."""
    for text in ([word, word.split("=", 1)[1]] if "=" in word else [word]):
        if not text or " " in text:
            continue
        norm = norm_word(text)
        if norm.startswith("./"):
            norm = norm[2:]
        if any(c in norm for c in "*?["):
            prefix = re.split(r"[*?\[]", norm, 1)[0]
            if prefix.startswith(".manifold/scratch"):
                continue
            pdir = prefix.rsplit("/", 1)[0] if "/" in prefix else ""
            if any(pdir == d or pdir.startswith(d + "/") for d in protected_dirs()) or (
                    not pdir and prefix and any(top.startswith(prefix) for top in (".manifold", ".claude"))):
                return norm
            continue
        if posixpath.basename(norm) in BARE_PROTECTED:
            return norm
        if any(re.search(r"(^|/)" + re.escape(p) + "$", norm) for p in PROTECTED_FILES):
            return norm
        if re.search(r"(^|/)(%s)$" % "|".join(PROTECTED_DEFINITIONS), norm):
            return norm
        if any(under(norm, d) for d in protected_dirs()):
            return norm
        if any(under(norm, d) for d in EXACT_PROTECTED_DIRS):
            return norm
    return None


def touches_protected(words, starts):
    """Refuse a command that is not read-only when a word names a protected file or directory, and `cd` into one."""
    for i in starts:
        cmd = re.sub(r"[0-9.]+$", "", posixpath.basename(words[i]))
        if cmd in ("cd", "pushd"):
            for a in words[i + 1:]:
                hit = protected_name(a) if not a.startswith("-") else None
                if hit:
                    return ProtectedHit(hit)
            continue
        if is_read_only(words, i):
            continue
        if cmd == "cp":
            # a copy out: the sources are only read when the destination is not protected (mv, install, ln and
            # rsync are not, a move removes the protected file)
            dest, sources = target_directory(words[i + 1:])
            if dest is None and sources:
                dest = sources[-1]
            if dest is not None and protected_name(dest) is None:
                continue
        for a in words[i + 1:]:
            hit = protected_name(a)
            if hit:
                return ProtectedHit(hit)
    return None


def scan_words(words, depth, stdin=None):
    stdin = stdin or Stdin()
    starts = command_starts(words)
    for i in starts:
        reason = scan_command(words, i, depth, stdin)
        if reason:
            return reason
    return touches_protected(words, starts)


def scan_command(words, i, depth, stdin):
    cmd = re.sub(r"[0-9.]+$", "", posixpath.basename(words[i]))
    args = words[i + 1:]
    plain = [a for a in args if not a.startswith("-")]

    if cmd in SHELLS or cmd in INTERPRETERS:
        reason = program_reason(cmd, args, depth, stdin)
        if reason:
            return reason
    if cmd == "eval":
        return scan(" ".join(args), depth + 1)
    if cmd == "sed":
        if any(SED_INPLACE_RE.match(a) or a.startswith("--in-place") for a in args):
            return "sed -i edits a file in place"
    elif cmd in ("perl", "ruby"):
        if any(PERL_INPLACE_RE.match(a) for a in args):
            return "%s -i edits a file in place" % cmd
    elif cmd == "tee":
        for a in plain:
            if a not in HARMLESS_TARGETS:
                return "tee writes to a file%s" % (" under /tmp" if is_tmp(a) else "")
    elif cmd in ("cp", "mv", "install", "ln", "rsync"):
        dest = target_directory(args)[0] if cmd != "rsync" else None  # rsync -t means "preserve times"
        if dest is None and plain:
            dest = plain[-1]
        if dest is not None and is_tmp(dest):
            return "%s into /tmp" % cmd
    elif cmd in ("touch", "mkdir", "truncate", "mkfifo"):
        if any(is_tmp(a) for a in plain):
            return "%s in /tmp" % cmd
    elif cmd == "dd":
        if any(a.startswith("of=") and is_tmp(a[3:]) for a in args):
            return "dd into /tmp"
    elif cmd in ("curl", "wget"):
        flags = ("-o", "--output") if cmd == "curl" else ("-O", "--output-document")
        for k, a in enumerate(args):
            if a in flags and k + 1 < len(args) and is_tmp(args[k + 1]):
                return "%s output into /tmp" % cmd
    elif cmd in ("sponge", "ed", "ex"):
        return "%s writes the file it is given" % cmd
    elif cmd == "patch":
        if not any(a in ("--dry-run",) for a in args):
            return "patch changes files"
    elif cmd == "git":
        sub, rest = git_subcommand(args)
        if sub in ("apply", "am") and not any(a in ("--check", "--stat", "--numstat", "--summary") for a in rest):
            return "git %s changes files" % sub
    elif cmd == "find":
        return find_reason(args, depth)
    elif AWK_RE.match(cmd):
        for k, a in enumerate(args):
            if a == "-i" and args[k + 1:k + 2] == ["inplace"]:
                return "awk -i inplace edits a file in place"
        if any(AWK_WRITE_RE.search(a) for a in plain):
            return "awk code that writes to a file or runs a command"
    return None


# ------------------------------------------------------------------ public API

def valid_entry(entry):
    return isinstance(entry, dict) and all(isinstance(entry.get(f), str) and entry[f].strip() for f in ALLOW_FIELDS)


def entry_scope(entry):
    """`command` when the entry has no `scope`; an unknown scope grants nothing (None)."""
    scope = entry.get("scope", "command")
    return scope if scope in ("path", "command") else None


def excepted(command, allow):
    """A command entry (no `scope`, or `"scope": "command"`) whose pattern matches the whole command."""
    for entry in allow or ():
        if not valid_entry(entry) or entry_scope(entry) != "command":
            continue
        try:
            if re.fullmatch(entry["pattern"], command.strip()):
                return True
        except re.error:
            continue
    return False


def classify_bash(command, allow=None):
    """Return (allowed, message). `allow` is the list of human exceptions (see the module docstring)."""
    if excepted(command, allow):
        return True, ""
    reason = scan(command)
    if isinstance(reason, ProtectedHit):
        return False, protected_message(str(reason))
    if reason:
        return False, shell_message(reason)
    return True, ""


def normalise_path(path):
    return posixpath.normpath(path.replace("\\", "/"))


def normalise_agent(agent_type):
    """`Reviewer`, `reviewer ` and `manifold:reviewer` are all `reviewer`; empty stays empty."""
    text = str(agent_type or "").strip().lower()
    return re.split(r"[:/]", text)[-1].strip() if text else ""


def is_definition(norm):
    return bool(DEFINITION_RE.search(norm.lower()))


def parse_expires(value):
    """Return a date for a real YYYY-MM-DD string, else None."""
    if not isinstance(value, str):
        return None
    m = DATE_RE.match(value)
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def today_utc():
    return datetime.datetime.now(datetime.timezone.utc).date()


def path_exception(norm, allow):
    """Look for a human path exception for `norm`. Return (granted, note): `note` is "" or says why a matching
    entry grants nothing (expired on a date, or no valid expires date)."""
    note = ""
    for entry in allow or ():
        if not valid_entry(entry) or entry_scope(entry) != "path":
            continue
        try:
            if not re.fullmatch(entry["pattern"], norm, re.IGNORECASE):
                continue
        except re.error:
            continue
        expires = parse_expires(entry.get("expires"))
        if expires is None:
            note = note or "a path exception for this file has no valid expires date (use YYYY-MM-DD), so it grants nothing"
        elif expires < today_utc():
            note = "a path exception for this file expired on %s, so it grants nothing" % expires.isoformat()
        else:
            return True, ""
    return False, note


def judge_write(agent_type, path, exists, allow=None, checkout_path=None):
    """`checkout_path` is the same file relative to the git checkout (a worktree) that holds it under the project
    directory, or None. It is used only for the reviewer and coordinator allowlists, so that a worktree's
    `docs/plans/REVIEW_PLAN_3.md` counts as that file. The protected files and the definitions are always judged on
    `path`, by the end of the path, so a checkout never lifts them."""
    norm = normalise_path(path)
    if PROTECTED_RE.search(norm):  # the mechanism: no exception route
        return False, protected_message(norm)
    agent = normalise_agent(agent_type)
    listed = normalise_path(checkout_path) if checkout_path else norm  # the spelling the allowlists judge
    refusal = None
    if is_definition(norm):
        refusal = definition_message(norm)
    elif agent == "reviewer":
        if not REVIEW_FILE_RE.match(listed):
            refusal = allowlist_message("reviewer", "docs/plans/REVIEW_PLAN_<N>.md", listed)
            norm = listed
    elif agent == "coordinator":
        if not (FAILURES_RE.match(listed) or (INTENT_RE.match(listed) and not exists)):
            refusal = allowlist_message(
                "coordinator", "docs/agents/<harness>-failures.md, or a new intent/INT-*.md draft (never an existing one)", listed)
            norm = listed
    if refusal is None:
        return True, ""
    granted, note = path_exception(norm, allow)
    if granted:
        return True, ""
    return False, refusal + (" Note: " + note + "." if note else "")


def classify_write(agent_type, path, exists, allow=None, checkout_path=None):
    """Return (allowed, message). `path` is relative to the project root where the caller can make it so;
    `exists` says whether the file is already there (a coordinator may create an intent, not replace one).
    `allow` is the list of human exceptions; only entries with `"scope": "path"` and a valid `expires` apply.
    `checkout_path` is the path relative to the worktree that holds the file (see judge_write)."""
    return judge_write(agent_type, path, exists, allow, checkout_path)


# ------------------------------------------------------------------------ main

def load_allow(project_dir):
    """Return (entries, problem). A missing file is not a problem; a broken one grants nothing."""
    path = os.path.join(project_dir, ALLOW_FILE)
    if not os.path.exists(path):
        return [], None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError, RecursionError) as exc:  # RecursionError: a deeply nested file
        return [], "could not read %s (%s); it grants no exception" % (ALLOW_FILE, exc)
    if not isinstance(data, list):
        return [], "%s must be a JSON list; it grants no exception" % ALLOW_FILE
    return data, None


def normalise_call(data, client):
    """Return (kind, tool_name, command, path, agent_type). kind is 'bash', 'write' or None."""
    name = data.get("tool_name") or (data.get("toolName") if client == "copilot" else None) or ""
    args = data.get("tool_input")
    if args is None and client == "copilot":
        args = data.get("toolArgs")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {}
    if not isinstance(args, dict):
        args = {}
    agent_type = data.get("agent_type") or data.get("agentType") or ""
    key = str(name).lower()
    if key in BASH_TOOLS:
        return "bash", name, str(args.get("command") or ""), "", agent_type
    if key in WRITE_TOOLS:
        path = next((str(args[k]) for k in PATH_KEYS if args.get(k)), "")
        return "write", name, "", path, agent_type
    return None, name, "", "", agent_type


def log_refusal(project_dir, rule, tool, agent_type, text):
    entry = {"time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "rule": rule, "tool": tool, "agent_type": agent_type, "command": text[:80]}
    path = os.path.join(project_dir, LOG_FILE)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except OSError as exc:
        sys.stderr.write("guard: could not append to %s: %s\n" % (LOG_FILE, exc))


def refuse(client, message):
    if client == "copilot":
        sys.stdout.write(json.dumps({"permissionDecision": "deny", "permissionDecisionReason": message}) + "\n")
        return 0
    sys.stderr.write(message + "\n")
    return 2


def guard_error(client, text):
    """Block the call because the guard itself could not judge it (fail closed), and log it."""
    message = "Manifold guard failed: %s. This tool call is blocked; tell a human." % text
    try:
        log_refusal(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd(), RULE_ERROR, "", "", text)
    except Exception:  # the block below must happen even when logging fails
        pass
    return refuse(client, message)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Manifold tool-boundary guard (hook JSON on stdin)")
    ap.add_argument("--client", choices=("claude", "copilot"), default="claude")
    args = ap.parse_args(argv)
    try:
        return run(args)
    except Exception as exc:  # fail closed: an error inside the guard must never read as an allow
        return guard_error(args.client, "%s: %s" % (type(exc).__name__, exc))


def run(args):
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
    except ValueError as exc:
        return guard_error(args.client, "cannot read the hook input as JSON (%s)" % exc)
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    kind, tool, command, path, agent_type = normalise_call(data, args.client)
    if kind == "bash":
        allow, problem = load_allow(project_dir)
        allowed, message = classify_bash(command, allow)
        if allowed:
            if allow and not classify_bash(command)[0]:  # it was refused without the exceptions: one was used
                log_refusal(project_dir, RULE_EXCEPTION_USED, tool, agent_type, command)
            return 0
        if problem:
            message += " (" + problem + ")"
        rule = RULE_PROTECTED if "(rule %s)" % RULE_PROTECTED in message else RULE_SHELL
        log_refusal(project_dir, rule, tool, agent_type, command)
        return refuse(args.client, message)
    if kind == "write":
        allow, problem = load_allow(project_dir)
        full = path if os.path.isabs(path) else os.path.join(project_dir, path)
        exists = os.path.exists(full)
        used = None
        # Judge the path as written and the path after symlinks are resolved: both must pass.
        for shown, local in write_spellings(project_dir, path, agent_type):
            allowed, message = classify_write(agent_type, shown, exists, allow, local)
            if not allowed:
                if problem:
                    message += " (" + problem + ")"
                norm = normalise_path(shown)
                rule = RULE_PROTECTED if PROTECTED_RE.search(norm) or is_definition(norm) else RULE_ALLOWLIST
                log_refusal(project_dir, rule, tool, agent_type, shown)
                return refuse(args.client, message)
            if allow and not classify_write(agent_type, shown, exists, None, local)[0]:
                used = shown
        if used is not None:
            log_refusal(project_dir, RULE_EXCEPTION_USED, tool, agent_type, used)
        return 0
    return 0


def real_target(full):
    """Resolve symlinks in `full` through its nearest existing ancestor (the file itself may not exist yet)."""
    head, tail = os.path.abspath(full), []
    while not os.path.lexists(head):
        parent, last = os.path.split(head)
        if parent == head:
            break
        head = parent
        tail.insert(0, last)
    return os.path.join(os.path.realpath(head), *tail) if tail else os.path.realpath(head)


def find_checkout(start):
    """The nearest directory at or above `start` that holds a `.git` entry (file or directory), or None. An error
    here propagates, and main() turns it into a refusal."""
    d = os.path.abspath(start)
    while True:
        if os.path.lexists(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _read_line(path):
    """The first line of a small text file, stripped, or None when it cannot be read (it then proves nothing)."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.readline().strip() or None
    except (OSError, ValueError):
        return None


def repository_id(root):
    """The real path of the git common directory of the checkout at `root`, or None when `root` does not prove it.
    A main checkout has a `.git` directory, which is its common directory. A linked worktree has a `.git` file
    `gitdir: <common>/worktrees/<name>`; that directory holds `commondir` and a `gitdir` file that must point back at
    this checkout's `.git` file. A forged `.git` entry (a file that names another checkout's git directory, a
    `commondir` that names a repository the git directory does not sit in) has no matching back-link and gives None."""
    dot = os.path.join(root, ".git")
    if os.path.isdir(dot):
        return os.path.realpath(dot)
    line = _read_line(dot) if os.path.isfile(dot) else None
    if not line or not line.startswith("gitdir:"):
        return None
    gitdir = os.path.realpath(os.path.join(root, line[len("gitdir:"):].strip()))
    common_text = _read_line(os.path.join(gitdir, "commondir"))
    back_text = _read_line(os.path.join(gitdir, "gitdir"))
    if not common_text or not back_text:
        return None
    common = os.path.realpath(os.path.join(gitdir, common_text))
    if os.path.dirname(gitdir) != os.path.join(common, "worktrees"):
        return None
    if os.path.realpath(os.path.join(gitdir, back_text)) != os.path.realpath(dot):
        return None
    return common


def checkout_relative(target, project_repo):
    """The path of `target` relative to the root of the checkout that holds it, when that checkout belongs to the
    same git repository as the project directory (`project_repo` is its repository_id); else None. The checkout can
    be the main checkout or any linked worktree, wherever it sits on disk."""
    if project_repo is None:
        return None
    root = find_checkout(os.path.dirname(target))
    if root is None or repository_id(root) != project_repo:
        return None
    return os.path.relpath(target, root)


def write_spellings(project_dir, path, agent_type=None):
    """(project-relative spelling, checkout-relative spelling or None) pairs to judge for a written path: as written,
    and after resolving symlinks in the path and in the project directory. A path outside the project is judged as
    given. The checkout-relative spelling is looked up only for the reviewer and the coordinator, whose allowlists
    use it, and is set only when the file lies in a checkout of the project directory's own repository."""
    full = os.path.abspath(path if os.path.isabs(path) else os.path.join(project_dir, path))
    project_repo = None
    if normalise_agent(agent_type) in ("reviewer", "coordinator"):
        root = find_checkout(os.path.realpath(project_dir))
        project_repo = repository_id(root) if root else None
    out = []
    for target, base, resolved in ((full, os.path.abspath(project_dir), False),
                                   (real_target(full), os.path.realpath(project_dir), True)):
        rel = os.path.relpath(target, base)
        # Outside the project: the path as given, and for the resolved spelling the resolved absolute path, so a
        # symlink that points at another checkout's definitions is judged by where it lands (CP2b R1).
        shown = (target if resolved else path) if rel.startswith("..") else rel
        pair = (shown, checkout_relative(target, project_repo))
        if pair not in out:
            out.append(pair)
    return out


def write_candidates(project_dir, path):
    """The project-relative spellings to judge for a written path (see write_spellings)."""
    out = []
    for shown, _ in write_spellings(project_dir, path):
        if shown not in out:
            out.append(shown)
    return out


if __name__ == "__main__":
    sys.exit(main())
