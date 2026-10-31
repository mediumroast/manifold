#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Rebuild assets/web/vendor/ from pinned npm packages.

The wiki browser (Docsify and its plugins) is served from the server itself, so a
browser that is offline, or an organization that blocks public CDNs, still gets a
working page.  This script is the record of exactly what is vendored:

  * each package is downloaded from the npm registry at an exact version;
  * the tarball is checked against the SHA-512 integrity value pinned below, and the
    script stops if it differs;
  * only the listed files are copied out, byte for byte, except for the two documented
    patches to the Darklight theme (it fetches fonts and two icons from public hosts);
  * a SHA256SUMS file and VENDORED.md are written, and the tests check them.

Standard library only.  Usage:  python3 tools/vendor_web.py [--check]
(--check rebuilds in a temporary folder and compares it with what is committed.)
"""

import argparse
import base64
import hashlib
import io
import json
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "assets" / "web" / "vendor"

REGISTRY = "https://registry.npmjs.org/%s/-/%s-%s.tgz"

# name -> (version, sha512 integrity of the tarball as published on the npm registry)
PACKAGES = {
    "docsify": ("4.13.1", "sha512-BsDypTBhw0mfslw9kZgAspCMZSM+sUIIDg5K/t1hNLkvbem9h64ZQc71e1IpY+iWsi/KdeqfazDfg52y2Lmm0A=="),
    "prismjs": ("1.30.0", "sha512-DEvV2ZF2r2/63V+tK8hQvrR2ZGn10srHbXviTlcv7Kpzw8jWiNTqbVgjO3IY8RxrrOUF8VPMQQFysYYYv0YZxw=="),
    "docsify-copy-code": ("2.1.1", "sha512-3+foIMuohrvYTA8dyDwr4wylKSZHXBq4tvoAP24BvzqSM9Rbh0gvXQunVoFZ7If4FOYmUXOBveg3EbJSBUMaow=="),
    "docsify-darklight-theme": ("3.2.0", "sha512-nAu98+833qcbH/32O7ia3kGk2xnAtCgcQjgjzGgBzmXEmr3jUWcMGcGpf8LJ+C+V4AK00rKng09bUS56H31gcw=="),
}

# (package, path inside the tarball, name in vendor/)
FILES = [
    ("docsify", "package/lib/docsify.min.js", "docsify.min.js"),
    ("docsify", "package/lib/plugins/search.min.js", "search.min.js"),
    ("prismjs", "package/components/prism-python.min.js", "prism-python.min.js"),
    ("prismjs", "package/components/prism-bash.min.js", "prism-bash.min.js"),
    ("prismjs", "package/components/prism-json.min.js", "prism-json.min.js"),
    ("prismjs", "package/components/prism-yaml.min.js", "prism-yaml.min.js"),
    ("prismjs", "package/components/prism-typescript.min.js", "prism-typescript.min.js"),
    ("docsify-copy-code", "package/dist/docsify-copy-code.min.js", "docsify-copy-code.min.js"),
    ("docsify-darklight-theme", "package/dist/index.min.js", "darklight.min.js"),
    ("docsify-darklight-theme", "package/dist/style.min.css", "darklight.min.css"),
    ("docsify-darklight-theme", "package/icons/moon.svg", "icons/moon.svg"),
    ("docsify-darklight-theme", "package/icons/sun.svg", "icons/sun.svg"),
]

# MIT license text of each package, kept next to the code.
LICENSES = {name: "package/LICENSE" for name in PACKAGES}

ICON_BASE = "https://cdn.jsdelivr.net/npm/docsify-darklight-theme@latest/icons/"
FONT_IMPORT = '@import url("https://fonts.googleapis.com/css?family=PT+Sans&Source+Sans+Pro&Roboto+Mono&display=swap");'
URL_PREFIX = "/docs/_manifold/vendor/icons/"   # where the server serves the icons

# (vendored name, old text, new text, expected number of occurrences)
PATCHES = [
    ("darklight.min.css", FONT_IMPORT, "", 1),
    ("darklight.min.js", ICON_BASE, URL_PREFIX, 2),
]
PATCH_NOTE = {
    "darklight.min.css": "/* Modified from docsify-darklight-theme 3.2.0 (MIT): the Google Fonts import was removed. "
                         "See VENDORED.md. */\n",
    "darklight.min.js": "/* Modified from docsify-darklight-theme 3.2.0 (MIT): the two icon URLs point at this server "
                        "instead of a public CDN. See VENDORED.md. */\n",
}


def fetch(name, version):
    url = REGISTRY % (name, name, version)
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    algorithm, _, expected = PACKAGES[name][1].partition("-")
    actual = base64.b64encode(hashlib.new(algorithm, data).digest()).decode()
    if actual != expected:
        sys.exit("integrity mismatch for %s %s: expected %s, got %s" % (name, version, expected, actual))
    return data


def member(archive, path):
    handle = archive.extractfile(archive.getmember(path))
    if handle is None:
        sys.exit("not a file: " + path)
    return handle.read()


def build(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    (out / "icons").mkdir(parents=True)
    (out / "licenses").mkdir()
    archives = {}
    for name, (version, _) in PACKAGES.items():
        archives[name] = tarfile.open(fileobj=io.BytesIO(fetch(name, version)), mode="r:gz")
    for package, inside, target in FILES:
        (out / target).write_bytes(member(archives[package], inside))
    for name, inside in LICENSES.items():
        (out / "licenses" / ("%s-LICENSE.txt" % name)).write_bytes(member(archives[name], inside))
    for target, old, new, count in PATCHES:
        path = out / target
        text = path.read_text(encoding="utf-8")
        if text.count(old) != count:
            sys.exit("patch for %s expected %d occurrence(s) of %r, found %d" % (target, count, old[:50], text.count(old)))
        path.write_text(text.replace(old, new), encoding="utf-8")
    for target, note in PATCH_NOTE.items():
        path = out / target
        path.write_text(note + path.read_text(encoding="utf-8"), encoding="utf-8")

    sums = []
    for path in sorted(p for p in out.rglob("*") if p.is_file()):
        sums.append("%s  %s" % (hashlib.sha256(path.read_bytes()).hexdigest(), path.relative_to(out).as_posix()))
    (out / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")

    rows = "\n".join("| `%s` | %s | `%s` |" % (n, v, i) for n, (v, i) in PACKAGES.items())
    (out / "VENDORED.md").write_text("""<!-- SPDX-License-Identifier: Apache-2.0 -->
# Vendored web files

The wiki browser's page scripts and styles are served from this folder so the browser needs no
network access. The files are third-party and MIT-licensed; their license texts are in `licenses/`.
Do not edit them by hand: run `python3 tools/vendor_web.py` to rebuild them, or `--check` to compare.

| Package | Version | Tarball integrity (npm registry) |
|---|---|---|
%s

Each tarball is checked against the integrity value above before a file is taken from it.
`SHA256SUMS` lists the SHA-256 of every file here; the tests compare it with the files.

## Changes to upstream files

Only `docsify-darklight-theme` is changed, because it reaches out to public hosts at run time (fonts and two icons):

* `darklight.min.css`: the `@import` of Google Fonts is removed. The page falls back to the
  system fonts already named in the style sheet.
* `darklight.min.js`: the two toggle-icon URLs, which pointed at jsDelivr, point at this
  server (`/docs/_manifold/vendor/icons/`), where the icons are served from `icons/`.

Each changed file starts with a comment saying so. All other files are byte-for-byte copies.
""" % rows, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true", help="rebuild in a temporary folder and compare")
    args = parser.parse_args()
    if not args.check:
        build(VENDOR)
        print("rebuilt", VENDOR.relative_to(ROOT))
        return
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp) / "vendor"
        build(fresh)
        def snapshot(base):
            return {p.relative_to(base).as_posix(): p.read_bytes() for p in base.rglob("*") if p.is_file()}
        if snapshot(fresh) != snapshot(VENDOR):
            sys.exit("assets/web/vendor differs from a fresh build; run tools/vendor_web.py")
    print("vendored files match a fresh build")


if __name__ == "__main__":
    main()
