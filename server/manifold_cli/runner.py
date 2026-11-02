# SPDX-License-Identifier: Apache-2.0
"""Where a host command runs, and the command line that selects it.

* ``--env NAME`` (the Docker deployments): the command is handed to ``./svc_ctl.sh NAME admin ...``,
  which runs ``python -m manifold_cli admin ...`` inside the container, on the same file system and
  data volume as the server (``docker compose exec`` while the server runs, ``compose run --rm``
  before it exists).  Nothing on the host opens the database.
* ``--data-dir PATH`` (or ``MANIFOLD_DATA_DIR``, which is how the command finds the volume once it
  runs inside the container): the command opens the store directly.  This is also the route for a run
  without Docker.

Output never contains a stored secret.  A failure prints one line saying what to fix and exits
non-zero (1 for a refused or failed command, 2 for a usage error).  Standard library only.
"""

import argparse
import getpass
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Optional, Sequence, TextIO

from manifold_security.principals import PrincipalError
from manifold_security.settings import SettingError
from manifold_security.store import DB_NAME, StoreError, open_store

from . import admin

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WIKI_ROOT = "/workspace"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manifold", description="Manifold host command. Administration happens here, never over MCP or HTTP.")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    common = argparse.ArgumentParser(add_help=False)
    where = common.add_argument_group("where to run")
    where.add_argument("--env", metavar="NAME", help="a Docker environment (dev, staging, production): run inside its container")
    where.add_argument("--data-dir", metavar="PATH", help="open the security store in this folder directly")
    where.add_argument("--wiki-root", metavar="PATH", help="the instance repository (default: CONTAINER_WIKI_ROOT or /workspace)")
    init = sub.add_parser("init", help="set up an instance, a protected server, a first administrator, you, a first agent "
                                       "and a first handoff")
    init.add_argument("--env", default="production", metavar="NAME", help="dev, staging or production (default production)")
    init.add_argument("--instance", metavar="PATH", help="the instance folder (default: manifold-instance beside this checkout)")
    init.add_argument("--data-dir", metavar="PATH", help="the folder for the security store (default: .manifold-data/<env>)")
    init.add_argument("--port", type=int, help="the port on 127.0.0.1 (default 8686)")
    init.add_argument("--name", help="the name of your own principal (default: your user name)")
    init.add_argument("--person-secret-file", metavar="FILE", help="where to write your credential (mode 0600)")
    init.add_argument("--agent-secret-file", metavar="FILE", help="where to write the first agent's credential (mode 0600)")
    init.add_argument("--yes", action="store_true", help="answer yes to the question after the plan (for scripts)")
    adm = sub.add_parser("admin", parents=[common], help="principals, credentials, roles, grants, settings, audit, export, purge")
    admin.add_parsers(adm.add_subparsers(dest="group", metavar="GROUP", required=True))
    return parser


def strip_option(argv: Sequence[str], name: str) -> List[str]:
    """``argv`` without ``name VALUE`` or ``name=VALUE``."""
    out, skip = [], False
    for item in argv:
        if skip:
            skip = False
        elif item == name:
            skip = True
        elif not item.startswith(name + "="):
            out.append(item)
    return out


def delegate(env: str, argv: Sequence[str], svc_ctl: Optional[Path] = None,
             run: Callable = subprocess.run) -> int:
    """Run the command inside the container of ``env`` through ``svc_ctl.sh``; return its exit status."""
    script = Path(svc_ctl) if svc_ctl else REPO_ROOT / "svc_ctl.sh"
    if not script.is_file():
        raise admin.CliError("Cannot find %s; run this from a Manifold checkout, or use --data-dir." % script)
    inner = strip_option(strip_option(argv, "--env"), "--wiki-root")  # the container knows its own wiki root
    result = run([str(script), env, *inner])  # inner starts with "admin": svc_ctl.sh <env> admin <group> <verb> ...
    return result.returncode


def run_direct(args: argparse.Namespace, out: TextIO, is_tty: bool) -> int:
    data_dir = args.data_dir or os.environ.get("MANIFOLD_DATA_DIR", "").strip()
    if not data_dir:
        raise admin.CliError("Say where the data is: --env NAME (a Docker environment), --data-dir PATH, or set "
                             "MANIFOLD_DATA_DIR.")
    wiki_root = Path(args.wiki_root or os.environ.get("CONTAINER_WIKI_ROOT") or DEFAULT_WIKI_ROOT)
    existed = (Path(data_dir).expanduser() / DB_NAME).exists()
    try:
        conn = open_store(data_dir, wiki_root=wiki_root)
    except StoreError as exc:
        raise admin.CliError(str(exc))
    try:
        ctx = admin.Context(conn, "host:%s" % _os_user(), out, is_tty, wiki_root)
        if not existed:
            ctx.say("Note: there was no security store in %s; an empty one was created." % data_dir)
        handler = admin.COMMANDS.get((args.group, getattr(args, "verb", "")))
        if handler is None:  # cannot happen with the parser; a clear failure beats a traceback
            raise admin.CliError("Unknown command: admin %s %s" % (args.group, getattr(args, "verb", "")))
        try:
            handler(ctx, args)
        except (PrincipalError, SettingError, sqlite3.Error, ValueError, OSError) as exc:
            raise admin.CliError(str(exc))
    finally:
        conn.close()
    return 0


def _os_user() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


def main(argv: Optional[Sequence[str]] = None, out: Optional[TextIO] = None, err: Optional[TextIO] = None,
         is_tty: Optional[bool] = None, svc_ctl: Optional[Path] = None, run: Callable = subprocess.run) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    out = out or sys.stdout
    err = err or sys.stderr
    if is_tty is None:
        is_tty = bool(getattr(out, "isatty", lambda: False)())
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            from . import init_cmd
            if args.env not in ("dev", "staging", "production"):
                raise admin.CliError("--env must be dev, staging or production.")
            options = init_cmd.Options(
                env_name=args.env, instance=Path(args.instance) if args.instance else None,
                data_dir=Path(args.data_dir) if args.data_dir else None, port=args.port, yes=args.yes, name=args.name,
                person_secret_file=Path(args.person_secret_file) if args.person_secret_file else None,
                agent_secret_file=Path(args.agent_secret_file) if args.agent_secret_file else None)
            return init_cmd.run_init(options, init_cmd.Runtime(repo_root=REPO_ROOT, out=out, err=err,
                                                               is_tty=bool(sys.stdin.isatty())))
        if args.env:
            if args.data_dir:
                raise admin.CliError("Use either --env or --data-dir, not both.")
            return delegate(args.env, argv, svc_ctl=svc_ctl, run=run)
        return run_direct(args, out, is_tty)
    except admin.CliError as exc:
        err.write("error: %s\n" % exc)
        return 1
