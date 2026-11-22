# SPDX-License-Identifier: Apache-2.0
"""Loader for the curated test instances (PHASE_4_PLAN Task 24, INT-3 S2).

``copy_curated(tmp_path, name)`` gives a private git-backed copy of a folder of ``curated/``, made
the way the ``acme`` fixture of ``test_example_acme.py`` makes its copy, with a fixed author and
commit date.  ``long_page(chars)`` gives the text of a very long page; it is generated, never
committed.  Nothing here uses the network.
"""

import os
import shutil
import subprocess
from pathlib import Path

CURATED = Path(__file__).resolve().parent / "curated"

# A fixed identity and date, so two copies of one set have the same history.
_GIT_ENV = {
    "GIT_AUTHOR_NAME": "datasets", "GIT_AUTHOR_EMAIL": "datasets@example.test",
    "GIT_COMMITTER_NAME": "datasets", "GIT_COMMITTER_EMAIL": "datasets@example.test",
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+0000", "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+0000",
}


def curated_names():
    """The names of the sets under ``curated/``, sorted."""
    return sorted(p.name for p in CURATED.iterdir() if p.is_dir())


def copy_curated(tmp_path, name):
    """A private git-backed copy of ``curated/<name>`` under ``tmp_path``; returns its root.

    Raises ValueError for a name that is not one of the sets.
    """
    if name not in curated_names():
        raise ValueError("no curated set %r (have: %s)" % (name, ", ".join(curated_names())))
    root = Path(tmp_path) / ("%s-wiki" % name)
    shutil.copytree(CURATED / name, root)
    env = {**os.environ, **_GIT_ENV}
    for args in (["init", "-q"], ["add", "-A"], ["-c", "commit.gpgsign=false", "commit", "-q", "-m", "start"]):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, env=env)
    return root


_UNIT = "Line %06d of a very long page, written to test how the server handles a lot of text.\n"


def long_page(chars):
    """Text of exactly ``chars`` characters, the same every time, starting and ending with a non-space."""
    if chars < 1:
        raise ValueError("chars must be at least 1")
    text = "".join(_UNIT % n for n in range(chars // len(_UNIT % 0) + 1))[:chars]
    return text[:-1] + "." if text[-1].isspace() else text
