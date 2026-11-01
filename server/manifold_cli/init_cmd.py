# SPDX-License-Identifier: Apache-2.0
"""``manifold init``: from nothing to a running, protected server and a first handoff (INT-6, local part).

The steps, in order: preflight (platform, Python, git, docker, the port); detect what exists; show the
whole plan and wait for a yes; create everything with a journal (so a failure undoes exactly what this run
made); start the service; check that a request with no credential is refused and the host command works;
act as the first agent to register two sample components and create a handoff, and read it back; check
the person's credential reads it and cannot register.

Nothing is created before the yes.  Nothing already there is overwritten or changed: a second run
detects it, says what exists and offers to create only what is missing.  A credential is written only to
a 0600 file and is never printed.  The security store is touched only by the host command running in
the container (``svc_ctl.sh <env> admin ...``), never by this process.  No GitHub, no outside request.
"""

import getpass
import json
import os
import platform
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, TextIO

from .journal import Journal
from .mcp_client import McpClient, McpError

SAMPLE_COMPONENTS = ("example-api", "example-web")
DEFAULT_PORT = 8686
ADMIN_NAME = "admin"
AGENT_NAME = "first-agent"
MINIMUM_PYTHON = (3, 11)


class InitError(Exception):
    """A step failed.  The message says what to fix."""


@dataclass
class Options:
    env_name: str = "production"
    instance: Optional[Path] = None
    data_dir: Optional[Path] = None
    port: Optional[int] = None
    yes: bool = False
    name: Optional[str] = None
    person_secret_file: Optional[Path] = None
    agent_secret_file: Optional[Path] = None
    wait_seconds: int = 120


@dataclass
class Runtime:
    """Everything that touches the outside world, so tests can stand in for it."""

    repo_root: Path
    out: TextIO = field(default_factory=lambda: sys.stdout)
    err: TextIO = field(default_factory=lambda: sys.stderr)
    system: Callable[[], str] = platform.system
    python_version: Callable[[], tuple] = lambda: tuple(sys.version_info[:3])
    which: Callable[[str], Optional[str]] = shutil.which
    run: Callable = subprocess.run
    ask: Callable[[str], str] = input
    is_tty: bool = field(default_factory=lambda: sys.stdin.isatty())
    user: Callable[[], str] = getpass.getuser
    port_in_use: Callable[[str, int], bool] = None  # set in __post_init__
    sleep: Callable[[float], None] = None
    urlopen: Callable = urllib.request.urlopen
    clock: Callable[[], float] = None

    def __post_init__(self):
        import time
        self.port_in_use = self.port_in_use or _port_in_use
        self.sleep = self.sleep or time.sleep
        self.clock = self.clock or time.monotonic

    def say(self, text: str = "") -> None:
        self.out.write(text + "\n")


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0


# ── preflight ────────────────────────────────────────────────────────────────

def preflight(rt: Runtime) -> List[str]:
    """The problems that stop init before it looks at anything, each saying what to fix. Empty when all is well."""
    problems = []
    system = rt.system()
    if system not in ("Linux", "Darwin"):
        problems.append("%s is not supported. Manifold's host command runs on Linux and macOS; on Windows use WSL2 "
                        "and run it from there." % (system or "This system"))
    if tuple(rt.python_version())[:2] < MINIMUM_PYTHON:
        problems.append("Python %d.%d or newer is needed (this is %s). Install a newer Python and run it with that."
                        % (MINIMUM_PYTHON + (".".join(str(p) for p in rt.python_version()),)))
    if not rt.which("git"):
        problems.append("git is not installed or not on the PATH. Install git (the instance is a git repository).")
    if not rt.which("docker"):
        problems.append("docker is not installed or not on the PATH. Install Docker (Docker Desktop on macOS), "
                        "then start it.")
    else:
        done = rt.run(["docker", "compose", "version"], capture_output=True, text=True)
        if done.returncode != 0:
            problems.append("'docker compose' does not work (is Docker running, and is the Compose plugin installed?).")
    if not (rt.repo_root / "svc_ctl.sh").is_file():
        problems.append("Cannot find svc_ctl.sh in %s. Run ./manifold from a Manifold checkout." % rt.repo_root)
    return problems


# ── detection ────────────────────────────────────────────────────────────────

_KEY = re.compile(r"^([A-Z_]+)=(.*)$")


def read_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            match = _KEY.match(line)
            if match:
                values[match.group(1)] = match.group(2).strip()
    return values


def count_principals(db: Path) -> Optional[int]:
    """Principals in an existing store, read-only; None if there is no store (or it has no such table)."""
    if not db.is_file():
        return None
    try:
        conn = sqlite3.connect("file:%s?mode=ro" % db, uri=True, timeout=5)
        try:
            return conn.execute("SELECT COUNT(*) FROM principals").fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error:
        return None


@dataclass
class State:
    env_name: str
    instance: Path
    data_dir: Path
    port: int
    env_file: Path
    env_template: Path
    instance_exists: bool
    instance_is_repo: bool
    data_exists: bool
    store_exists: bool
    principals: int
    env_exists: bool
    env_values: Dict[str, str]
    person: str = ""
    person_secret_file: Optional[Path] = None
    agent_secret_file: Optional[Path] = None

    @property
    def anything_exists(self) -> bool:
        return self.instance_exists or self.data_exists or self.env_exists or self.store_exists


def safe_name(text: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._@-]+", "-", text).strip("-._@")
    return (cleaned or "me")[:63]


def detect(rt: Runtime, opts: Options) -> State:
    docker_dir = rt.repo_root / "docker"
    env_file = docker_dir / (".env.%s" % opts.env_name)
    values = read_env_file(env_file)
    if values.get("WIKI_ROOT") and not values["WIKI_ROOT"].startswith("/path/to/"):
        instance = Path(values["WIKI_ROOT"])
        if opts.instance and Path(opts.instance).resolve() != instance.resolve():
            raise InitError("%s already points at %s, not %s. Use that folder (leave out --instance), or move the "
                            "settings file aside if you want a different one." % (env_file, instance, opts.instance))
    else:
        instance = Path(opts.instance) if opts.instance else rt.repo_root.parent / "manifold-instance"
    if values.get("DATA_DIR"):
        data_dir = Path(values["DATA_DIR"])
        if opts.data_dir and Path(opts.data_dir).resolve() != data_dir.resolve():
            raise InitError("%s already sets DATA_DIR=%s, not %s. Use that folder (leave out --data-dir)."
                            % (env_file, data_dir, opts.data_dir))
    else:
        data_dir = Path(opts.data_dir) if opts.data_dir else rt.repo_root / ".manifold-data" / opts.env_name
    port = opts.port or int(values.get("PORT") or DEFAULT_PORT)
    instance, data_dir = instance.expanduser().absolute(), data_dir.expanduser().absolute()
    principals_found = count_principals(data_dir / "manifold.db")
    return State(
        env_name=opts.env_name, instance=instance, data_dir=data_dir, port=port, env_file=env_file,
        env_template=docker_dir / (".env.%s.template" % opts.env_name),
        instance_exists=instance.exists(), instance_is_repo=(instance / ".git").exists(),
        data_exists=data_dir.exists(), store_exists=(data_dir / "manifold.db").exists(),
        principals=principals_found or 0, env_exists=env_file.is_file(), env_values=values)


def validate_paths(state: State) -> None:
    inside = lambda child, parent: child == parent or parent in child.parents  # noqa: E731
    if inside(state.data_dir.resolve(), state.instance.resolve()):
        raise InitError("The data folder (%s) is inside the instance folder (%s): the credential store would end "
                        "up in git. Choose a data folder outside it." % (state.data_dir, state.instance))
    if inside(state.instance.resolve(), state.data_dir.resolve()):
        raise InitError("The instance folder is inside the data folder. Choose separate folders.")
    if inside(state.instance.resolve(), state.env_file.parent.parent.resolve()):
        raise InitError("The instance folder (%s) is inside the Manifold checkout. The instance is a repository of "
                        "its own: choose a folder outside the checkout." % state.instance)
    if state.instance_exists and not (state.instance / "manifold.yaml").is_file():
        raise InitError("%s exists but has no manifold.yaml, so it is not an instance. Choose another folder or "
                        "add the file; init never writes into a folder it did not make." % state.instance)


# ── the plan ─────────────────────────────────────────────────────────────────

def show_plan(rt: Runtime, state: State, opts: Options) -> None:
    rt.say("This is what init will do for the '%s' environment:" % state.env_name)
    rt.say()
    rt.say("  instance folder   %-60s %s" % (state.instance, "exists, kept as it is" if state.instance_exists
                                              else "create (a copy of examples/starter, with a first git commit)"))
    rt.say("  data folder       %-60s %s" % (state.data_dir, "exists, kept" if state.data_exists
                                              else "create (mode 0700: credential hashes and the audit trail)"))
    rt.say("  settings file     %-60s %s" % (state.env_file, "exists, only missing settings are added" if state.env_exists
                                              else "create (mode 0600, no secret in it)"))
    rt.say("  TLS               off: the server is reachable on this machine only (127.0.0.1:%d)" % state.port)
    if state.principals:
        rt.say("  principals        %d already exist: none are created or changed, and no credential is issued"
               % state.principals)
    else:
        rt.say("  principals        create three:")
        rt.say("                      %-14s administrator (admin role): runs the host command; cannot read the "
               "wiki; no credential" % ADMIN_NAME)
        rt.say("                      %-14s you (reader, contributor; write grants on %s and _shared); a credential "
               "written to %s" % (state.person, ", ".join(SAMPLE_COMPONENTS), state.person_secret_file))
        rt.say("                      %-14s a first agent (reader, contributor, registrar; the same grants); a "
               "credential written to %s" % (AGENT_NAME, state.agent_secret_file))
        rt.say("                    The credentials are shown nowhere else and cannot be shown again.")
    rt.say("  then              start the service, check that a request with no credential is refused, register "
           "%s as the agent," % " and ".join(SAMPLE_COMPONENTS))
    rt.say("                    create a handoff between them and read it back; nothing is sent outside this machine.")
    if state.anything_exists:
        rt.say()
        rt.say("Something is already here. Init will create only what is missing, never change a credential and "
               "never overwrite content.")
    rt.say()


def confirm(rt: Runtime, opts: Options, question: str) -> bool:
    if opts.yes:
        return True
    if not rt.is_tty:
        rt.say("Not a terminal, so there is nobody to say yes. Nothing was changed. Run it again from a terminal, "
               "or add --yes.")
        return False
    return rt.ask(question + " [y/N] ").strip().lower() in ("y", "yes")


# ── helpers for the steps ────────────────────────────────────────────────────

def run_checked(rt: Runtime, command: Sequence[str], what: str, cwd: Optional[Path] = None):
    done = rt.run(list(command), capture_output=True, text=True, **({"cwd": str(cwd)} if cwd else {}))
    if done.returncode != 0:
        tail = "\n".join(((done.stderr or "") + (done.stdout or "")).strip().splitlines()[-12:])
        raise InitError("%s failed (exit %d)%s" % (what, done.returncode, (":\n" + tail) if tail else "."))
    return done


def http_status(rt: Runtime, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[int]:
    """The HTTP status of a GET, or None if nothing answered."""
    try:
        with rt.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, OSError):
        return None


def write_env_file(rt: Runtime, state: State, journal: Journal) -> None:
    """Create the settings file from its template, or add the settings an older file lacks; never change a value."""
    wanted = {"WIKI_ROOT": str(state.instance), "DATA_DIR": str(state.data_dir), "PORT": str(state.port)}
    if not state.env_exists:
        if not state.env_template.is_file():
            raise InitError("Cannot find %s." % state.env_template)
        journal.created(state.env_file)
        lines = []
        for line in state.env_template.read_text(encoding="utf-8").splitlines():
            match = _KEY.match(line)
            if match and match.group(1) in wanted:
                line = "%s=%s" % (match.group(1), wanted[match.group(1)])
            lines.append(line)
        fd = os.open(str(state.env_file), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")
        return
    current = state.env_file.read_text(encoding="utf-8")
    missing = [(k, v) for k, v in wanted.items() if k in ("WIKI_ROOT", "DATA_DIR") and not state.env_values.get(k)]
    for key, default in (("MANIFOLD_TLS", "off"), ("TLS_NAMES", "localhost 127.0.0.1"), ("ALLOWED_HOSTS", "")):
        if key not in state.env_values:
            missing.append((key, default))
    if missing:
        journal.restore(state.env_file, current)
        addition = "".join("%s=%s\n" % kv for kv in missing)
        state.env_file.write_text(current + ("" if current.endswith("\n") else "\n") + addition, encoding="utf-8")


def create_instance(rt: Runtime, state: State, journal: Journal) -> None:
    if state.instance_exists:
        return
    parent = state.instance.parent
    parent.mkdir(parents=True, exist_ok=True)
    inside = rt.run(["git", "-C", str(parent), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if inside.returncode == 0 and inside.stdout.strip():
        raise InitError("%s is inside the git repository %s. The server commits only in a repository whose top "
                        "level is the instance, so choose a folder outside any repository."
                        % (parent, inside.stdout.strip()))
    starter = rt.repo_root / "examples" / "starter"
    if not starter.is_dir():
        raise InitError("Cannot find %s." % starter)
    journal.created(state.instance)
    shutil.copytree(starter, state.instance)
    identity = ["-c", "user.name=Manifold", "-c", "user.email=manifold@localhost"]
    run_checked(rt, ["git", "init", "-q"], "git init", cwd=state.instance)
    run_checked(rt, ["git", "add", "-A"], "git add", cwd=state.instance)
    run_checked(rt, ["git", *identity, "commit", "-q", "-m", "Start from the Manifold starter"], "the first commit",
                cwd=state.instance)


def create_data_dir(state: State, journal: Journal) -> None:
    if not state.data_exists:
        journal.created(state.data_dir)
        old = os.umask(0o077)
        try:
            state.data_dir.mkdir(parents=True)
        finally:
            os.umask(old)
        os.chmod(state.data_dir, 0o700)
    for sub in ("credentials", "caddy/data", "caddy/config"):
        folder = state.data_dir / sub
        if not folder.exists():
            if state.data_exists:  # a pre-existing data folder: note each folder this run adds
                journal.created(folder)
            old = os.umask(0o077)
            try:
                folder.mkdir(parents=True)
            finally:
                os.umask(old)


def svc_ctl(rt: Runtime, state: State, *args: str) -> List[str]:
    return [str(rt.repo_root / "svc_ctl.sh"), state.env_name, *args]


def bootstrap_principals(rt: Runtime, state: State, journal: Journal) -> None:
    """Create the three first principals through the host command in a one-off container (the host never opens the store)."""
    creds = state.data_dir / "credentials"
    person_tmp = creds / ("%s.secret" % state.person)
    agent_tmp = creds / ("%s.secret" % AGENT_NAME)
    for path in (person_tmp, agent_tmp, state.data_dir / "manifold.db"):
        if not path.exists():
            journal.created(path)
    command = svc_ctl(rt, state, "admin", "bootstrap", "--admin", ADMIN_NAME, "--person", state.person,
                      "--agent", AGENT_NAME, "--slugs", ",".join(SAMPLE_COMPONENTS),
                      "--person-secret-file", "/data/credentials/%s.secret" % state.person,
                      "--agent-secret-file", "/data/credentials/%s.secret" % AGENT_NAME)
    run_checked(rt, command, "Creating the first principals")
    for temp, final in ((person_tmp, state.person_secret_file), (agent_tmp, state.agent_secret_file)):
        if final and Path(final).absolute() != temp.absolute():
            final = Path(final).absolute()
            if final.exists():
                raise InitError("%s already exists; init does not overwrite it. Its credential is in %s." % (final, temp))
            final.parent.mkdir(parents=True, exist_ok=True)
            journal.created(final)
            shutil.move(str(temp), str(final))
            os.chmod(final, 0o600)


def wait_healthy(rt: Runtime, state: State, wait_seconds: int) -> None:
    url = "http://127.0.0.1:%d/health" % state.port
    deadline = rt.clock() + wait_seconds
    while True:
        if http_status(rt, url) == 200:
            return
        if rt.clock() >= deadline:
            raise InitError("The server did not become healthy within %d seconds (%s). Look at the logs: %s %s logs"
                            % (wait_seconds, url, rt.repo_root / "svc_ctl.sh", state.env_name))
        rt.sleep(2)


def read_secret(path: Path) -> str:
    try:
        text = Path(path).read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise InitError("Cannot read the credential file %s: %s" % (path, exc))
    if not text.startswith("mf_"):
        raise InitError("%s does not hold a Manifold credential." % path)
    return text


def walk_through(rt: Runtime, state: State) -> str:
    """Act as the first agent, then check as the person. Returns the path of the handoff that was created."""
    base = "http://127.0.0.1:%d" % state.port
    agent = McpClient(base, read_secret(state.agent_secret_file), opener=rt.urlopen)
    person = McpClient(base, read_secret(state.person_secret_file), opener=rt.urlopen)
    try:
        agent.initialize()
        for slug in SAMPLE_COMPONENTS:
            result = agent.call_tool("wiki_register_component_tool", {
                "name": slug, "description": "A sample component for the first walk-through.",
                "repo": "https://example.invalid/%s" % slug, "owner": "sample-team", "skip_source_docs": True})
            if result.get("status") not in ("created", "already_registered"):
                raise InitError("Registering %s failed: %s" % (slug, result.get("error") or result.get("message") or result))
        created = agent.call_tool("wiki_handoff_tool", {
            "action": "create", "source": SAMPLE_COMPONENTS[0], "target": SAMPLE_COMPONENTS[1], "type": "feature",
            "priority": "low", "title": "First handoff from init",
            "summary": "Created by manifold init to show the whole path works.",
            "what_needs_to_happen": "Nothing: this is a sample."})
        if created.get("status") != "created":
            raise InitError("Creating the handoff failed: %s" % (created.get("error") or created))
        path = created["path"]
        listed = agent.call_tool("wiki_handoff_tool", {"action": "list"})
        if path not in json.dumps(listed):
            raise InitError("The handoff %s was created but did not show up when read back." % path)
        person.initialize()
        page = person.call_tool("wiki_read_tool", {"path": path})
        if "First handoff from init" not in json.dumps(page):
            raise InitError("The person's credential could not read the handoff back: %s" % (page.get("error") or page))
        refused = person.call_tool("wiki_register_component_tool", {
            "name": "not-allowed", "description": "x", "repo": "https://example.invalid/x", "owner": "x",
            "skip_source_docs": True})
        if not refused.get("refused"):
            raise InitError("The person's credential was able to register a component; it must not be.")
    except McpError as exc:
        raise InitError(str(exc))
    return path


def client_steps(rt: Runtime, state: State) -> None:
    if not state.person_secret_file.is_file():
        # a repeat run: the credentials already existed and were not touched; the file is wherever you put it
        state.person_secret_file = Path("<your credential file>")
        rt.say("Connect a client (use the credential file you saved when your credential was created; none is ever "
               "printed or re-issued here):")
    else:
        rt.say("Connect a client (your credential is in %s; it is never printed):" % state.person_secret_file)
    rt.say("  Claude Code: copy examples/clients/claude-code-mcp.json to .mcp.json in your component repository, set the")
    rt.say("               address to http://127.0.0.1:%d/mcp, and start Claude Code with the variable set:" % state.port)
    rt.say("                 MANIFOLD_TOKEN=\"$(cat %s)\" claude" % state.person_secret_file)
    rt.say("               (MANIFOLD_TOKEN here is only the name of the variable that holds YOUR credential.)")
    rt.say("  VS Code:     copy examples/clients/vscode-mcp.json to .vscode/mcp.json, set the address as above, and paste")
    rt.say("               the credential when VS Code asks for it (the prompt is hidden).")
    rt.say("  Browser:     open http://127.0.0.1:%d/docs/ ; use any user name and your credential as the password." % state.port)
    rt.say("  Claude Desktop and claude.ai are not supported yet (INT-18).")


# ── the whole run ────────────────────────────────────────────────────────────

def run_init(opts: Options, rt: Runtime) -> int:
    problems = preflight(rt)
    if problems:
        rt.say("Init cannot start:")
        for problem in problems:
            rt.say("  - " + problem)
        return 2
    try:
        state = detect(rt, opts)
        validate_paths(state)
        asked = ""
        if not opts.name and rt.is_tty and not opts.yes:
            asked = rt.ask("Your name for your own principal [%s]: " % safe_name(rt.user())).strip()
        state.person = safe_name(opts.name or asked or rt.user())
        if state.person in (ADMIN_NAME, AGENT_NAME):
            raise InitError("'%s' is reserved; choose another name with --name." % state.person)
        creds = state.data_dir / "credentials"
        state.person_secret_file = Path(opts.person_secret_file).absolute() if opts.person_secret_file \
            else creds / ("%s.secret" % state.person)
        state.agent_secret_file = Path(opts.agent_secret_file).absolute() if opts.agent_secret_file \
            else creds / ("%s.secret" % AGENT_NAME)
        if rt.port_in_use("127.0.0.1", state.port) and http_status(rt, "http://127.0.0.1:%d/health" % state.port) != 200:
            raise InitError("Port %d on this machine is in use by something else. Free it, or set PORT in %s."
                            % (state.port, state.env_file))
    except InitError as exc:
        rt.say("Init cannot go on: %s" % exc)
        return 2

    show_plan(rt, state, opts)
    question = "Create what is missing and go on?" if state.anything_exists else "Create all of this and go on?"
    if not confirm(rt, opts, question):
        rt.say("Nothing was changed.")
        return 0 if rt.is_tty else 1  # a "no" at a prompt is fine; no terminal and no --yes is a refusal

    journal = Journal()
    try:
        rt.say("Creating…")
        create_instance(rt, state, journal)
        rt.say("  instance folder ready: %s" % state.instance)
        create_data_dir(state, journal)
        write_env_file(rt, state, journal)
        rt.say("  data folder and settings file ready")
        rt.say("Building the image (the first time takes a few minutes)…")
        run_checked(rt, svc_ctl(rt, state, "build"), "Building the image")  # the host command runs from this image
        if state.principals == 0:
            bootstrap_principals(rt, state, journal)
            rt.say("  principals created; credentials written to their files (mode 0600)")
        journal.action("stopped the service", lambda: rt.run(svc_ctl(rt, state, "stop"), capture_output=True, text=True))
        rt.say("Starting the service (the first start builds the image and can take a few minutes)…")
        run_checked(rt, svc_ctl(rt, state, "start"), "Starting the service")
        wait_healthy(rt, state, opts.wait_seconds)
        rt.say("  the server is healthy")
        base = "http://127.0.0.1:%d" % state.port
        if http_status(rt, base + "/docs/") != 401 or http_status(rt, base + "/docs/", {"Authorization": "Bearer nope"}) != 401:
            raise InitError("The server answered a request with no (or a wrong) credential. It must refuse it.")
        rt.say("  a request with no credential is refused")
        run_checked(rt, svc_ctl(rt, state, "admin", "principal", "list"), "The host command (admin principal list)")
        rt.say("  the host command works")
        if state.principals == 0:
            path = walk_through(rt, state)
            rt.say("  the first agent registered %s and %s, created the handoff %s, and read it back"
                   % (SAMPLE_COMPONENTS[0], SAMPLE_COMPONENTS[1], path))
            rt.say("  your credential reads the handoff and cannot register a component")
        else:
            rt.say("  the principals already existed, so the walk-through (which needs a credential) was skipped; "
                   "get one with: %s %s admin credential issue <name> --secret-file /data/<file>"
                   % (rt.repo_root / "svc_ctl.sh", state.env_name))
    except (InitError, OSError, FileExistsError, KeyboardInterrupt) as exc:
        rt.say("")
        rt.say("Init failed: %s" % (exc if not isinstance(exc, KeyboardInterrupt) else "interrupted"))
        rt.say("Undoing what this run created…")
        problems = journal.undo(lambda line: rt.say("  " + line))
        for problem in problems:
            rt.say("  ! " + problem)
        rt.say("Nothing from this run is left." if not problems else "Some of it could not be removed (see above).")
        return 1
    rt.say()
    rt.say("Done. The server is running at http://127.0.0.1:%d (stop it with %s %s stop)."
           % (state.port, rt.repo_root / "svc_ctl.sh", state.env_name))
    rt.say("Run ./manifold init again at any time: it changes nothing without your yes.")
    rt.say()
    client_steps(rt, state)
    return 0
