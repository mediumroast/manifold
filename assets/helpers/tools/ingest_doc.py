#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Push a local document into the manifold wiki via the MCP server's /ingest endpoint.

Usage:
    python3 tools/ingest_doc.py <component> <file_path> [doc_type]

Arguments:
    component   Component slug, e.g. "acme-api"
    file_path   Absolute or relative path to the document file
    doc_type    Optional: readme | architecture | api | other
                Auto-detected from filename if omitted.

Examples:
    python3 tools/ingest_doc.py acme-api README.md
    python3 tools/ingest_doc.py acme-api /home/me/dev/acme-api/ARCHITECTURE.md architecture
    python3 tools/ingest_doc.py acme-api docs/API.md api

Output on success:
    ✅  Ingested → raw/acme-api/2026-05-25-acme-api-architecture.md  (4821 bytes)

The MCP server must be running at the URL configured below (default: http://127.0.0.1:8686).
The server always requires a credential of your own (issued to you by whoever runs the server). Put it in
the MANIFOLD_TOKEN environment variable (that is only the name of the variable; the value is YOUR
credential, not a shared token). You also need a write grant on the component.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


DEFAULT_SERVER_URL = "http://127.0.0.1:8686"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push a local doc file into the manifold wiki raw/ directory.",
    )
    parser.add_argument("component", help="Component slug, e.g. acme-api")
    parser.add_argument("file_path", help="Path to the document file")
    parser.add_argument(
        "doc_type",
        nargs="?",
        default="",
        help="Doc type: readme | architecture | api | other (auto-detected if omitted)",
    )
    parser.add_argument(
        "--server",
        default=DEFAULT_SERVER_URL,
        help=f"MCP server URL (default: {DEFAULT_SERVER_URL})",
    )
    args = parser.parse_args()

    path = Path(args.file_path)
    if not path.exists():
        print(f"❌  File not found: {path}", file=sys.stderr)
        sys.exit(1)
    if not path.is_file():
        print(f"❌  Not a file: {path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")

    payload = json.dumps({
        "component": args.component,
        "doc_type":  args.doc_type,
        "content":   content,
        "filename":  path.name,   # used by server to derive a unique dated slug
    }).encode("utf-8")

    url = args.server.rstrip("/") + "/ingest"

    headers = {"Content-Type": "application/json"}
    token = os.environ.get("MANIFOLD_TOKEN", "").strip()  # the name of the variable that holds YOUR credential
    if token:
        headers["Authorization"] = "Bearer " + token

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            msg = json.loads(raw).get("message", raw)
        except Exception:
            msg = raw
        print(f"❌  Server error {e.code}: {msg}", file=sys.stderr)
        if e.code == 401:
            print("    The server needs your credential: set MANIFOLD_TOKEN to it in your environment "
                  "(it may also have been revoked or expired: ask whoever runs the server).", file=sys.stderr)
        elif e.code == 403:
            print("    Your credential is not allowed to add documents for this component (a write grant is needed).",
                  file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌  Could not reach MCP server at {url}: {e.reason}", file=sys.stderr)
        print(
            "    Is the server running? From the manifold repo: ./svc_ctl.sh dev start",
            file=sys.stderr,
        )
        sys.exit(1)

    if body.get("status") == "ok":
        out_path = body.get("path", "?")
        byte_count = body.get("bytes", len(content))
        print(f"✅  Ingested → {out_path}  ({byte_count} bytes)")
    else:
        msg = body.get("message", json.dumps(body))
        print(f"❌  Ingest failed: {msg}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
