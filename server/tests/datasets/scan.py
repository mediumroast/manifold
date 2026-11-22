# SPDX-License-Identifier: Apache-2.0
"""Scan files for real-shaped data (PHASE_4_PLAN Task 26, INT-3 S3).

``scan(path)`` walks a file or folder and reports:

* email addresses;
* hosts in URLs (``scheme://host``) that do not end in ``.test``, ``.example`` or ``.invalid``
  (a bare dotted word such as the slug ``acme.io`` is not a URL and is not reported);
* strings shaped like tokens or keys (known vendor prefixes, long hexadecimal runs, long mixed
  letter-and-digit runs);
* every term in a private term list, a JSON list of strings kept outside every checkout.

A finding names the file, the line and the kind.  It never carries the matched text for any kind,
so a report and a log never hold an address, a host, a secret or a private term.  The term list is never
committed or printed.

The term list path is always an argument.  Called with no ``terms_file`` the scan uses
``~/.manifold/excluded_terms.json`` if that file exists; that default is looked up only when
``scan`` runs, never when this module is imported.  Tests and manual runs pass a fixture file.

Command line::

    python scan.py PATH [--terms-file FILE]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional, Sequence

SAFE_HOST_SUFFIXES = (".test", ".example", ".invalid")

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
_URL_HOST = re.compile(r"\b[a-z][a-z0-9+.-]*://(?:[^/\s@]*@)?([A-Za-z0-9.-]+)", re.I)
_VENDOR_TOKEN = re.compile(r"\b(?:sk|pk|rk)[-_][A-Za-z0-9_-]{16,}|\b(?:gh[pousr]_|github_pat_|xox[abpr]-)[A-Za-z0-9_-]{16,}"
                           r"|\bAKIA[0-9A-Z]{16}\b")
_HEX_RUN = re.compile(r"\b[0-9a-fA-F]{32,}\b")
_MIXED_RUN = re.compile(r"[A-Za-z0-9+/_=]{32,}")


class Finding(NamedTuple):
    path: str
    line: int
    kind: str  # "email", "host", "token", "term" or "pattern"

    def __str__(self):
        return "%s:%d: %s" % (self.path, self.line, self.kind)


def default_terms_file() -> Path:
    """The default place of the private term list, outside every checkout."""
    return Path.home() / ".manifold" / "excluded_terms.json"


def load_terms(terms_file) -> List[str]:
    """The non-empty terms of a JSON list of strings.  Raises FileNotFoundError or ValueError (never quoting the content)."""
    try:
        data = json.loads(Path(terms_file).read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise ValueError("the term list must be a JSON list of strings; this file is not valid JSON") from None
    if not isinstance(data, list) or not all(isinstance(t, str) for t in data):
        raise ValueError("the term list must be a JSON list of strings")
    return [t for t in data if t.strip()]


def _files(path: Path):
    if path.is_file():
        yield path
        return
    for item in sorted(path.rglob("*")):
        if item.is_file() and ".git" not in item.relative_to(path).parts:
            yield item


def _mixed_token(match: str) -> bool:
    return any(c.isdigit() for c in match) and any(c.isalpha() for c in match)


def scan(path, terms_file=None, extra_patterns: Sequence["re.Pattern"] = ()) -> List[Finding]:
    """Findings for a file or a folder.

    ``terms_file``: a JSON list of private terms (matched case-insensitively); None uses the default
    file if it exists.  ``extra_patterns``: compiled regular expressions reported as ``pattern``
    (the personal-data test passes first-name-plus-surname patterns).  Raises FileNotFoundError when
    ``path`` or an explicitly given ``terms_file`` does not exist.
    """
    root = Path(path)
    if not root.exists():
        raise FileNotFoundError("nothing to scan at %s" % root)
    if terms_file is None:
        default = default_terms_file()
        terms = load_terms(default) if default.is_file() else []
    else:
        terms = load_terms(terms_file)
    lowered = [t.lower() for t in terms]

    findings: List[Finding] = []
    for file in _files(root):
        shown = str(file if root.is_file() else file.relative_to(root))
        text = file.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            for m in _EMAIL.finditer(line):
                findings.append(Finding(shown, number, "email"))
            for m in _URL_HOST.finditer(line):
                host = m.group(1).rstrip(".").lower()
                if not host.endswith(SAFE_HOST_SUFFIXES):
                    findings.append(Finding(shown, number, "host"))
            if (_VENDOR_TOKEN.search(line) or any(_mixed_token(m.group(0)) for m in _MIXED_RUN.finditer(line))
                    or _HEX_RUN.search(line)):
                findings.append(Finding(shown, number, "token"))
            low = line.lower()
            if any(t in low for t in lowered):
                findings.append(Finding(shown, number, "term"))
            if any(p.search(line) for p in extra_patterns):
                findings.append(Finding(shown, number, "pattern"))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Scan files for emails, real hosts, token-shaped strings and private terms.")
    parser.add_argument("path")
    parser.add_argument("--terms-file", help="JSON list of private terms (default: ~/.manifold/excluded_terms.json if it exists)")
    args = parser.parse_args(argv)
    try:
        findings = scan(args.path, terms_file=args.terms_file)
    except (OSError, ValueError) as exc:
        print("scan: %s" % exc, file=sys.stderr)
        return 2
    for finding in findings:
        print(finding)
    if not findings:
        print("scan: no findings")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
