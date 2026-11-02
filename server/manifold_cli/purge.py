# SPDX-License-Identifier: Apache-2.0
"""``admin registry purge``: remove an archived component for good, from the host only.

Preconditions, all checked before anything changes: the component is archived, its hold period
(``purge_hold_days`` from the day it was archived) has passed, no handoff that involves it is
still open, and the slug was typed again with ``--confirm-slug``.  The files are removed by
:func:`remove_component_files`, the one function a second implementation (through the GitHub
API, for a server with no local checkout) can replace.  Completed handoff pages stay as
history; git history keeps everything else.  One git commit is made, authored ``host:<os user>``.
The server never offers this over MCP or HTTP.
"""

import getpass
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

from manifold_security import audit, principals
from manifold_security.store import now_iso, transaction


@dataclass(frozen=True)
class HostActor:
    """A commit author for a host command: anything with ``principal_id``, ``name`` and ``kind``."""

    principal_id: str
    name: str
    kind: str = "host"


def removable_paths(wiki_root: Path, slug: str) -> List[str]:
    """The files and folders that belong to ``slug`` and exist now, relative to the wiki root."""
    candidates = ["wiki/components/%s.md" % slug, "wiki/guides/agents/%s.md" % slug, "raw/%s" % slug]
    return [c for c in candidates if (wiki_root / c).exists() or (wiki_root / c).is_symlink()]


def remove_component_files(wiki_root: Path, slug: str) -> List[str]:
    """Delete the page, the agent guide and ``raw/<slug>/`` from the checkout; return what was removed."""
    removed = []
    for relative in removable_paths(wiki_root, slug):
        target = wiki_root / relative
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
        removed.append(relative)
    return removed


def _tracked(wiki_root: Path, relative: str) -> bool:
    """True if git tracks anything at or under ``relative``."""
    done = subprocess.run(["git", "-c", "safe.directory=%s" % wiki_root, "ls-files", "--", relative],
                          cwd=wiki_root, capture_output=True, text=True)
    return done.returncode == 0 and bool(done.stdout.strip())


def run(ctx, args) -> None:
    from .admin import CliError
    try:
        from wiki_backend import config as wiki_config
        from wiki_backend.git import git_commit
        from wiki_backend.handoff import open_handoffs_of
        from wiki_backend.register import remove_from_index, remove_from_sidebar
    except ImportError as exc:
        raise CliError("The purge needs the server's own Python packages (%s). Run it through the container: "
                       "./manifold admin --env <name> registry purge ..." % exc)
    slug = args.slug
    wiki_root = ctx.wiki_root
    if not wiki_config.valid_slug(slug):
        raise CliError("%r is not a valid component name." % slug)
    if not (wiki_root / "manifold.yaml").is_file():
        raise CliError("%s is not an instance repository (no manifold.yaml). Use --wiki-root." % wiki_root)

    state = principals.get_component_state(ctx.conn, slug)
    if not state.archived:
        raise CliError("%s is not archived. A registrar archives it first with wiki_component_manage_tool "
                       "(action='archive'); it can then be purged after the hold period." % slug)
    if state.purge_after and state.purge_after > now_iso():
        raise CliError("%s is held until %s (archived %s, reason: %s). It cannot be purged before then; "
                       "restore it with wiki_component_manage_tool if it is needed again."
                       % (slug, state.purge_after, state.archived_at, state.reason))
    open_pages = open_handoffs_of(wiki_root, slug)
    if open_pages:
        raise CliError("Handoffs that involve %s are not completed: %s. Complete or reject them first."
                       % (slug, ", ".join(open_pages)))

    paths = removable_paths(wiki_root, slug)
    ctx.say("Purging %s (archived %s: %s) will remove:" % (slug, state.archived_at, state.reason))
    for relative in paths:
        ctx.say("  - %s" % relative)
    ctx.say("  - its entry in manifold.yaml, its sidebar links and index row, and every grant and deny on %s" % slug)
    ctx.say("Completed handoff pages that involve it are kept as history; git history keeps everything.")
    if args.confirm_slug != slug:
        raise CliError("Nothing was changed. To go ahead, type the slug again: --confirm-slug %s" % slug)

    removed = remove_component_files(wiki_root, slug)
    changed = [wiki_root / r for r in removed if _tracked(wiki_root, r)]  # only what git knows can be staged
    try:
        if wiki_config.remove_component(wiki_root, slug):
            changed.append(wiki_root / "manifold.yaml")
    except wiki_config.ConfigError as exc:
        raise CliError("The files were removed but manifold.yaml could not be edited: %s" % exc)
    for edited in (remove_from_sidebar(wiki_root, slug), remove_from_index(wiki_root, slug),
                   wiki_config.sync_schema_slugs(wiki_root)):
        if edited is not None:
            changed.append(edited)

    with transaction(ctx.conn):
        ctx.conn.execute("DELETE FROM grants WHERE scope = ?", (slug,))
        ctx.conn.execute("DELETE FROM denies WHERE scope = ?", (slug,))
        ctx.conn.execute("DELETE FROM component_state WHERE slug = ?", (slug,))
    audit.record(ctx.conn, audit.COMPONENT_LIFECYCLE, ctx.actor, slug, "purged: %s" % state.reason)

    user = ctx.actor.split(":", 1)[-1] or getpass.getuser()
    result = git_commit(wiki_root, changed, "wiki: purge archived component %s" % slug,
                        principal=HostActor("host-%s" % user, ctx.actor))
    if not result.get("committed"):
        raise CliError("%s was purged but the git commit failed (%s); commit the removal by hand."
                       % (slug, result.get("reason")))
    ctx.say("Purged %s in commit %s. To bring it back: git revert that commit in the instance repository, "
            "then register or restore the component." % (slug, result.get("sha")))
