#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
"""Manifold tool-boundary guard. Standard library only; written for Python 3.8.

A client runs this file before a tool call (a pre-tool hook) and passes the call as JSON on
standard input. The guard enforces two rules and refuses the call when one is broken:

1. Shell writes (rule `no-heredocs`): a shell command may not write or change file contents
   (heredocs, `python - <<`, `sed -i`, `perl -i`, `tee`, `>` or `>>` into a file, `python -c`
   that opens a file for writing) and may not write to `/tmp` or `/private/tmp`. The refusal
   names the sanctioned route: create or edit with the Write or Edit tool, or write a snippet
   with Write to `.manifold/scratch/` and run the file.
2. Write allowlist (rules `write-allowlist` and `protected-file`): the `reviewer` may write only
   `docs/plans/REVIEW_PLAN_<N>.md`; the `coordinator` may write `docs/agents/*-failures.md`
   and create (not replace) `intent/INT-*.md`; no agent may write the guard's own files:
   `.manifold/guard-allow.json`, `.manifold/hooks/guard.py` and `.manifold/guard-log.jsonl`.

Usage as a hook:  python3 guard.py --client claude|copilot   (hook JSON on stdin)

Claude Code: a refusal exits 2 with the message on stderr (the model sees it). An allowed call
exits 0 with no output. Copilot: a refusal prints `{"permissionDecision": "deny",
"permissionDecisionReason": ...}` on stdout and exits 0; the Copilot field names and tool names
are normalised here, but they are unverified in VS Code Local (see docs/agents/harness-capabilities.md).
Input the guard cannot read exits 1 with a message: that is a visible, non-blocking error, not
a silent allow.

A human exception is an entry in `.manifold/guard-allow.json`, a JSON list of objects with
`pattern`, `reason`, `granted_by` and `date`, all non-empty. `pattern` is a regular expression
that must match the whole command, so a second command appended to an allowed one is still judged.
An entry missing a field, or an unreadable file, grants nothing.

Every refusal appends `{time, rule, tool, agent_type, command}` to `.manifold/guard-log.jsonl`
(local, git-ignored). `command` is the first 80 characters, which keeps secrets out.

Residual gaps (stated, not fixed): a script that writes files when it is run from a file is not
inspected; command substitution inside double quotes is not scanned; an agent can still
write through a tool the guard does not look at; the guard covers only agents whose client runs
it (see the enforcement table in the install guide).
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

SCRATCH = ".manifold/scratch/"
ALLOW_FILE = ".manifold/guard-allow.json"
LOG_FILE = ".manifold/guard-log.jsonl"
ALLOW_FIELDS = ("pattern", "reason", "granted_by", "date")

SHELLS = {"bash", "sh", "zsh", "dash", "ksh"}
WRAPPERS = {"env", "command", "sudo", "nohup", "time", "exec", "xargs", "nice", "builtin", "stdbuf", "timeout"}
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")"}
REDIRECT_OUT = {">", ">>", ">|", "&>", "&>>"}
HARMLESS_TARGETS = {"/dev/null", "/dev/stderr", "/dev/stdout", "/dev/tty"}
TMP_RE = re.compile(r"^(/private)?/tmp(/|$)")
SED_INPLACE_RE = re.compile(r"^-[nEersz]*i")
PERL_INPLACE_RE = re.compile(r"^-[pnalswcT0-9]*i")
CODE_WRITE_RE = re.compile(
    r"open\s*\(\s*[^,()]+,\s*(mode\s*=\s*)?['\"][rbtU]*[wax+]"      # open(f, 'w')
    r"|open\s*\([^)]*mode\s*=\s*['\"][rbtU]*[wax+]"                  # open(f, mode='w')
    r"|\.open\s*\(\s*['\"][rbtU]*[wax+]"                              # Path(f).open('w')
    r"|\.write_text\s*\(|\.write_bytes\s*\("
    r"|writeFileSync|appendFileSync|createWriteStream")
PROTECTED_RE = re.compile(r"(^|/)\.manifold/(guard-allow\.json|guard-log\.jsonl|hooks/guard\.py)$", re.IGNORECASE)
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
    return ("Refused by the Manifold guard (rule %s): %s is a guard file; only a human changes it. "
            "Do not work around this block. Tell a human what you need." % (RULE_PROTECTED, path))


def allowlist_message(agent_type, allowed, path):
    return ("Refused by the Manifold guard (rule %s): the %s agent may write only %s, not %s. "
            "Do not work around this block. If the file is yours to change, tell a human, who may grant an "
            "exception in %s." % (RULE_ALLOWLIST, agent_type, allowed, path, ALLOW_FILE))


# ------------------------------------------------------------------ tokenizer

def tokenize(command):
    """Split a shell command into ('w', word) and ('op', operator) tokens, tracking quotes so that
    an operator inside quotes stays part of a word. File-descriptor duplications (2>&1, >&2) vanish."""
    toks, buf, state = [], [], {"quoted": False}
    quote = None
    i, n = 0, len(command)

    def flush():
        if buf or state["quoted"]:
            toks.append(("w", "".join(buf)))
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
        elif c == "\n":
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
            flush()
            toks.append(("op", c))
        else:
            buf.append(c)
        i += 1
    flush()
    return toks


def split_segments(toks):
    segs, seg = [], []
    for kind, text in toks:
        if kind == "op" and text in SEPARATORS:
            segs.append(seg)
            seg = []
        else:
            seg.append((kind, text))
    segs.append(seg)
    return segs


# --------------------------------------------------------------- shell scanning

def is_tmp(path):
    return bool(TMP_RE.match(path))


def scan(command, depth=0):
    """Return a reason string when the command writes files, else None."""
    if depth > MAX_DEPTH:
        return "a command nested too deeply to inspect"
    for seg in split_segments(tokenize(command)):
        reason = scan_segment(seg, depth)
        if reason:
            return reason
    return None


def scan_segment(seg, depth):
    words, j = [], 0
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
                j += 1
        else:
            words.append(text)
        j += 1
    return scan_words(words, depth)


def scan_words(words, depth):
    i = 0
    while i < len(words):
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[i]):
            i += 1
            continue
        base = posixpath.basename(words[i])
        if base in WRAPPERS:
            i += 1
            while i < len(words) and (words[i].startswith("-") or (base == "timeout" and words[i][:1].isdigit())):
                i += 1
            continue
        break
    if i >= len(words):
        return None
    cmd = re.sub(r"[0-9.]+$", "", posixpath.basename(words[i]))
    args = words[i + 1:]
    plain = [a for a in args if not a.startswith("-")]

    if cmd in SHELLS:
        for k, a in enumerate(args):
            if a.startswith("-") and not a.startswith("--") and "c" in a[1:] and k + 1 < len(args):
                return scan(args[k + 1], depth + 1)
        return None
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
    elif cmd in ("python", "node", "nodejs"):
        flag = "-c" if cmd == "python" else "-e"
        for k, a in enumerate(args):
            if a == flag and k + 1 < len(args) and CODE_WRITE_RE.search(args[k + 1]):
                return "%s %s code that opens a file for writing" % (cmd, flag)
    elif cmd in ("cp", "mv", "install", "ln", "rsync"):
        if plain and is_tmp(plain[-1]):
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
    return None


# ------------------------------------------------------------------ public API

def valid_entry(entry):
    return isinstance(entry, dict) and all(isinstance(entry.get(f), str) and entry[f].strip() for f in ALLOW_FIELDS)


def excepted(command, allow):
    for entry in allow or ():
        if not valid_entry(entry):
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
    if reason:
        return False, shell_message(reason)
    return True, ""


def normalise_path(path):
    return posixpath.normpath(path.replace("\\", "/"))


def classify_write(agent_type, path, exists):
    """Return (allowed, message). `path` is relative to the project root where the caller can make it so;
    `exists` says whether the file is already there (a coordinator may create an intent, not replace one)."""
    norm = normalise_path(path)
    if PROTECTED_RE.search(norm):
        return False, protected_message(norm)
    if agent_type == "reviewer":
        if REVIEW_FILE_RE.match(norm):
            return True, ""
        return False, allowlist_message("reviewer", "docs/plans/REVIEW_PLAN_<N>.md", norm)
    if agent_type == "coordinator":
        if FAILURES_RE.match(norm) or (INTENT_RE.match(norm) and not exists):
            return True, ""
        return False, allowlist_message(
            "coordinator", "docs/agents/<harness>-failures.md, or a new intent/INT-*.md draft (never an existing one)", norm)
    return True, ""


# ------------------------------------------------------------------------ main

def load_allow(project_dir):
    """Return (entries, problem). A missing file is not a problem; a broken one grants nothing."""
    path = os.path.join(project_dir, ALLOW_FILE)
    if not os.path.exists(path):
        return [], None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
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


def main(argv=None):
    ap = argparse.ArgumentParser(description="Manifold tool-boundary guard (hook JSON on stdin)")
    ap.add_argument("--client", choices=("claude", "copilot"), default="claude")
    args = ap.parse_args(argv)
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
    except ValueError as exc:
        sys.stderr.write("guard: cannot read the hook input as JSON: %s\n" % exc)
        return 1
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    kind, tool, command, path, agent_type = normalise_call(data, args.client)
    if kind == "bash":
        allow, problem = load_allow(project_dir)
        allowed, message = classify_bash(command, allow)
        if allowed:
            return 0
        if problem:
            message += " (" + problem + ")"
        log_refusal(project_dir, RULE_SHELL, tool, agent_type, command)
        return refuse(args.client, message)
    if kind == "write":
        full = path if os.path.isabs(path) else os.path.join(project_dir, path)
        rel = os.path.relpath(full, project_dir)
        shown = path if rel.startswith("..") else rel
        allowed, message = classify_write(agent_type, shown, os.path.exists(full))
        if allowed:
            return 0
        rule = RULE_PROTECTED if PROTECTED_RE.search(normalise_path(shown)) else RULE_ALLOWLIST
        log_refusal(project_dir, rule, tool, agent_type, shown)
        return refuse(args.client, message)
    return 0


if __name__ == "__main__":
    sys.exit(main())
