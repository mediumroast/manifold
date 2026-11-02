# SPDX-License-Identifier: Apache-2.0
"""Git auto-commit helper for wiki write operations."""

import os
import subprocess
from pathlib import Path
from typing import Sequence, Union

from .actor import current_actor


# Default identity used when no git user is configured in the environment.
# Override with MANIFOLD_GIT_NAME and MANIFOLD_GIT_EMAIL.
_DEFAULT_NAME = "manifold"
_DEFAULT_EMAIL = "manifold@localhost"


def _identity() -> tuple:
    return (
        os.environ.get("MANIFOLD_GIT_NAME", "").strip() or _DEFAULT_NAME,
        os.environ.get("MANIFOLD_GIT_EMAIL", "").strip() or _DEFAULT_EMAIL,
    )


def git_commit(
    wiki_root: Path,
    paths: Sequence[Union[Path, str]],
    message: str,
    principal=None,
) -> dict:
    """
    Stage ``paths`` and create a git commit inside ``wiki_root``.

    Non-fatal: if any git operation fails the function returns a dict with
    ``committed=False`` and a ``reason`` string — it never raises.  The
    write/append that triggered this call already succeeded on disk.

    Git identity is injected via ``-c`` flags so no ``~/.gitconfig`` is
    required inside the container.  The ``safe.directory`` override handles
    the common case where the repo is owned by a different UID on the host.

    Args:
        wiki_root:  Absolute path to the repository root (e.g. /workspace).
        paths:      Files to stage — may be absolute or relative to wiki_root.
        message:    Commit message.
        principal:  The principal the change is attributed to (anything with ``principal_id``,
                    ``name`` and ``kind``).  Defaults to the acting principal of the current tool
                    call.  It becomes the commit author and a ``Manifold-Principal`` trailer; the
                    committer stays ``MANIFOLD_GIT_NAME``.  Nothing from a request body is used.

    Returns:
        {"committed": True,  "sha": "<hash>", "message": "..."}
        {"committed": False, "reason": "<explanation>"}
    """
    if not message:
        message = "wiki: update"

    safe_flag = f"safe.directory={wiki_root}"
    author_name, author_email = _identity()
    if principal is None:
        principal = current_actor()
    author_args = []
    if principal is not None:
        message = "%s\n\nManifold-Principal: %s (%s)" % (message, principal.principal_id, principal.kind)
        author_args = ["--author", "%s <%s@principals.manifold.invalid>" % (principal.name, principal.principal_id)]

    try:
        # Normalise paths to repo-relative strings for git add.
        rel_paths = []
        for p in paths:
            p = Path(p)
            rel_paths.append(
                str(p.relative_to(wiki_root)) if p.is_absolute() else str(p)
            )

        # The wiki root must be the top of its own repository.  Inside another repository
        # (an instance folder copied into a larger project, for example) a commit here would
        # land in that other repository's history.
        top = subprocess.run(
            ["git", "-c", safe_flag, "rev-parse", "--show-toplevel"],
            cwd=wiki_root,
            capture_output=True,
            text=True,
        )
        if top.returncode != 0:
            return {"committed": False, "reason": "not a git repository: run git init in the wiki root"}
        if Path(top.stdout.strip()).resolve() != Path(wiki_root).resolve():
            return {
                "committed": False,
                "reason": (
                    f"the wiki root is inside another git repository ({top.stdout.strip()}); "
                    "run git init in the wiki root so changes are committed there"
                ),
            }

        # git add
        add_result = subprocess.run(
            ["git", "-c", safe_flag, "add", "--", *rel_paths],
            cwd=wiki_root,
            capture_output=True,
            text=True,
        )
        if add_result.returncode != 0:
            return {"committed": False, "reason": add_result.stderr.strip() or "git add failed"}

        # git commit
        commit_result = subprocess.run(
            [
                "git",
                "-c", safe_flag,
                "-c", f"user.name={author_name}",
                "-c", f"user.email={author_email}",
                "commit",
                *author_args,
                "-m", message,
            ],
            cwd=wiki_root,
            capture_output=True,
            text=True,
        )

        if commit_result.returncode == 0:
            # Parse the short SHA from output like "[main abc1234] message"
            sha = None
            for line in commit_result.stdout.splitlines():
                if line.startswith("["):
                    parts = line.split()
                    if len(parts) >= 2:
                        sha = parts[1].rstrip("]")
                    break
            return {"committed": True, "sha": sha, "message": message}

        # "nothing to commit" is not a real failure.
        combined = commit_result.stdout + commit_result.stderr
        if "nothing to commit" in combined:
            return {"committed": False, "reason": "nothing to commit"}

        return {"committed": False, "reason": combined.strip()}

    except Exception as exc:
        return {"committed": False, "reason": str(exc)}
