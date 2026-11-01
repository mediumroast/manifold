# SPDX-License-Identifier: Apache-2.0
"""manifold init: preflight, detection, the plan, create with undo, the first credentials, start, check, handoff
(PHASE_1_PLAN T31 to T33).

Nothing here needs Docker.  The runner stands in for `docker` and `./svc_ctl.sh`: `compose version` answers, `admin ...`
runs the real host command in this process on the data folder, and `start`/`stop` start and stop the REAL server
process (`python server.py`) on the instance and data folder init made, the pattern of test_server_smoke.py.
"""

import io
import os
import shutil
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

pytest.importorskip("fastmcp")

from manifold_cli import init_cmd, runner as cli_runner  # noqa: E402
from manifold_cli.journal import Journal  # noqa: E402
from manifold_cli.mcp_client import McpClient, McpError  # noqa: E402
from tests.realserver import SERVER_DIR, free_port  # noqa: E402

REAL_REPO = SERVER_DIR.parent
ENV = "production"


class FakeServices:
    """A stand-in for docker and svc_ctl.sh that runs the real host command and the real server."""

    def __init__(self, checkout, fail_on=None):
        self.checkout = checkout
        self.fail_on = fail_on          # a substring of a command line that should fail
        self.calls = []
        self.process = None
        self.compose_ok = True
        self.log = checkout.parent / "server.log"

    def _values(self):
        values = init_cmd.read_env_file(self.checkout / "docker" / (".env.%s" % ENV))
        return Path(values["WIKI_ROOT"]), Path(values["DATA_DIR"]), int(values["PORT"])

    def __call__(self, command, **kwargs):
        line = " ".join(str(c) for c in command)
        self.calls.append(line)
        if self.fail_on and self.fail_on in line:
            return subprocess.CompletedProcess(command, 1, "", "simulated failure of: %s" % self.fail_on)
        if command[:3] == ["docker", "compose", "version"]:
            return subprocess.CompletedProcess(command, 0 if self.compose_ok else 1, "Docker Compose version v2", "")
        if command[0] == "git":
            return subprocess.run(command, **kwargs)
        if command[0].endswith("svc_ctl.sh"):
            action = command[2]
            if action == "build":
                return subprocess.CompletedProcess(command, 0, "", "")
            if action == "start":
                return self._start()
            if action == "stop":
                self.stop()
                return subprocess.CompletedProcess(command, 0, "", "")
            if action == "admin":
                return self._admin(command[3:])
        raise AssertionError("unexpected command: " + line)

    def _admin(self, args):
        instance, data, _ = self._values()
        args = [a.replace("/data/", str(data) + "/") for a in args]
        out, err = io.StringIO(), io.StringIO()
        code = cli_runner.main(["admin", "--data-dir", str(data), "--wiki-root", str(instance), *args],
                               out=out, err=err, is_tty=False)
        return subprocess.CompletedProcess(args, code, out.getvalue(), err.getvalue())

    def _start(self):
        if self.process is not None and self.process.poll() is None:
            return subprocess.CompletedProcess([], 0, "", "")
        instance, data, port = self._values()
        env = dict(os.environ, CONTAINER_WIKI_ROOT=str(instance), PORT=str(port), MANIFOLD_DATA_DIR=str(data),
                   MANIFOLD_HOST="127.0.0.1", MANIFOLD_STORE_JOURNAL_MODE="delete", PYTHONUNBUFFERED="1")
        for name in ("MANIFOLD_TOKEN", "MANIFOLD_TOKEN_FILE", "MANIFOLD_RELOAD"):
            env.pop(name, None)
        self.process = subprocess.Popen([sys.executable, "server.py"], cwd=SERVER_DIR, env=env,
                                        stdout=open(self.log, "a"), stderr=subprocess.STDOUT)
        return subprocess.CompletedProcess([], 0, "", "")

    def stop(self):
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None


@pytest.fixture()
def checkout(tmp_path):
    """A private copy of just what init reads from a checkout: svc_ctl.sh, the env templates, the starter."""
    root = tmp_path / "checkout"
    (root / "docker").mkdir(parents=True)
    (root / "svc_ctl.sh").write_text("#!/bin/sh\n")
    for name in ("dev", "staging", "production"):
        shutil.copy(REAL_REPO / "docker" / (".env.%s.template" % name), root / "docker")
    shutil.copytree(REAL_REPO / "examples" / "starter", root / "examples" / "starter")
    return root


@pytest.fixture()
def services(checkout):
    fake = FakeServices(checkout)
    yield fake
    fake.stop()


class Session:
    def __init__(self, checkout, services, tmp_path, **overrides):
        self.checkout, self.services, self.tmp_path = checkout, services, tmp_path
        self.out, self.err = io.StringIO(), io.StringIO()
        self.port = free_port()
        self.answers = []
        self.settings = dict(system="Linux", python=(3, 11, 4), tty=False, present=("git", "docker"))
        self.settings.update(overrides)
        self.clock = [0.0]

    def runtime(self):
        s = self.settings

        def ask(prompt):
            self.out.write(prompt)
            return self.answers.pop(0) if self.answers else ""

        def sleep(seconds):
            self.clock[0] += seconds
            time.sleep(0.05)

        return init_cmd.Runtime(
            repo_root=self.checkout, out=self.out, err=self.err, system=lambda: s["system"],
            python_version=lambda: s["python"], which=lambda name: ("/usr/bin/" + name) if name in s["present"] else None,
            run=self.services, ask=ask, is_tty=s["tty"], user=lambda: "tester",
            port_in_use=lambda host, port: False, sleep=sleep, clock=lambda: self.clock[0])

    def options(self, **kw):
        base = dict(env_name=ENV, instance=self.tmp_path / "manifold-instance", data_dir=self.tmp_path / "manifold-data",
                    port=self.port, yes=True, name="pat", wait_seconds=40)
        base.update(kw)
        return init_cmd.Options(**base)

    def run(self, **kw):
        return init_cmd.run_init(self.options(**kw), self.runtime())

    @property
    def text(self):
        return self.out.getvalue() + self.err.getvalue()


@pytest.fixture()
def session(checkout, services, tmp_path):
    return Session(checkout, services, tmp_path)


def tree(*roots):
    """Every file under the roots with its bytes and mode: to show that nothing changed."""
    seen = {}
    for root in roots:
        for base, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d != ".git"]
            for name in files:
                full = os.path.join(base, name)
                seen[full] = (Path(full).read_bytes(), stat.S_IMODE(os.stat(full).st_mode))
    return seen


def nothing_made(session):
    return (not session.options().instance.exists() and not session.options().data_dir.exists()
            and not (session.checkout / "docker" / (".env.%s" % ENV)).exists())


# ── preflight ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("overrides,message", [
    ({"system": "Windows"}, "WSL2"),
    ({"python": (3, 10, 9)}, "Python 3.11 or newer"),
    ({"present": ("docker",)}, "git is not installed"),
    ({"present": ("git",)}, "docker is not installed"),
])
def test_preflight_refuses_with_a_message_that_says_what_to_fix_and_creates_nothing(
        checkout, services, tmp_path, overrides, message):
    session = Session(checkout, services, tmp_path, **overrides)
    assert session.run() == 2
    assert message in session.text and "cannot start" in session.text
    assert nothing_made(session)


def test_preflight_notes_a_docker_that_does_not_run(session):
    session.services.compose_ok = False
    assert session.run() == 2 and "'docker compose' does not work" in session.text
    assert nothing_made(session)


def test_preflight_lists_every_problem_at_once(checkout, services, tmp_path):
    session = Session(checkout, services, tmp_path, system="Windows", python=(3, 9, 1), present=())
    assert session.run() == 2
    assert session.text.count("\n  - ") == 4  # platform, python, git, docker


def test_a_port_in_use_by_something_else_stops_init(session):
    rt = session.runtime()
    rt.port_in_use = lambda host, port: True
    assert init_cmd.run_init(session.options(), rt) == 2
    assert "in use by something else" in session.text and nothing_made(session)


# ── the plan and the yes ─────────────────────────────────────────────────────

def test_the_plan_is_shown_in_full_and_a_no_creates_nothing(checkout, services, tmp_path):
    session = Session(checkout, services, tmp_path, tty=True)
    session.answers = ["n"]
    assert session.run(yes=False) == 0
    for expected in ("instance folder", "data folder", "settings file", "TLS", "administrator", "pat", "first-agent",
                     "example-api", "example-web", "Nothing was changed"):
        assert expected in session.text, expected
    assert nothing_made(session) and not [c for c in services.calls if "svc_ctl" in c]


def test_without_a_terminal_and_without_yes_nothing_is_created(checkout, services, tmp_path):
    session = Session(checkout, services, tmp_path, tty=False)
    assert session.run(yes=False) == 1
    assert "Not a terminal" in session.text and nothing_made(session)


def test_nothing_is_created_before_the_yes(checkout, services, tmp_path):
    session = Session(checkout, services, tmp_path, tty=True)
    seen = []
    original = session.runtime

    def runtime():
        rt = original()
        real_ask = rt.ask
        rt.ask = lambda prompt: (seen.append(nothing_made(session)), real_ask(prompt))[1]
        return rt
    session.runtime = runtime
    session.answers = ["no"]
    session.run(yes=False)
    assert seen == [True]


def test_the_person_is_asked_for_a_name_on_a_terminal(checkout, services, tmp_path):
    session = Session(checkout, services, tmp_path, tty=True)
    session.answers = ["Jo Q. Public", "n"]
    session.run(yes=False, name=None)
    assert "Jo-Q.-Public" in session.text


# ── paths that must be refused ───────────────────────────────────────────────

def test_an_instance_inside_the_checkout_is_refused(session):
    assert session.run(instance=session.checkout / "inst") == 2
    assert "inside the Manifold checkout" in session.text and not (session.checkout / "inst").exists()


def test_a_data_folder_inside_the_instance_is_refused(session, tmp_path):
    assert session.run(data_dir=tmp_path / "manifold-instance" / "data") == 2
    assert "end up in git" in session.text and nothing_made(session)


def test_a_folder_that_is_not_an_instance_is_refused_and_left_alone(session, tmp_path):
    folder = tmp_path / "manifold-instance"
    folder.mkdir()
    (folder / "notes.txt").write_text("mine")
    assert session.run() == 2 and "not an instance" in session.text
    assert (folder / "notes.txt").read_text() == "mine" and not (session.checkout / "docker" / (".env.%s" % ENV)).exists()


def test_an_instance_inside_another_git_repository_is_refused_and_undone(session, tmp_path):
    outer = tmp_path / "outer"
    outer.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=outer, check=True)
    assert session.run(instance=outer / "inst") == 1
    assert "inside the git repository" in session.text and not (outer / "inst").exists()


def test_a_reserved_name_is_refused(session):
    assert session.run(name="admin") == 2 and "reserved" in session.text


# ── the whole run ────────────────────────────────────────────────────────────

def test_a_full_run_ends_with_a_healthy_server_two_components_and_a_handoff_read_back(session):
    code = session.run()
    assert code == 0, session.text
    opts = session.options()
    for expected in ("the server is healthy", "a request with no credential is refused", "the host command works",
                     "the first agent registered example-api and example-web", "created the handoff",
                     "your credential reads the handoff and cannot register", "Done."):
        assert expected in session.text, expected
    # the instance: a repository of its own with the first commit, both components registered, one handoff page
    instance = opts.instance
    log = subprocess.run(["git", "log", "--format=%an|%s"], cwd=instance, capture_output=True, text=True).stdout
    assert "Manifold|Start from the Manifold starter" in log
    yaml_text = (instance / "manifold.yaml").read_text()
    assert "example-api" in yaml_text and "example-web" in yaml_text
    handoffs = list((instance / "wiki" / "handoffs").glob("*/*.md"))
    assert len(handoffs) == 1 and "First handoff from init" in handoffs[0].read_text()
    # the registrations and the handoff are authored by the first agent, not by the server
    assert "first-agent|" in log
    # the data folder and the settings file
    assert stat.S_IMODE(opts.data_dir.stat().st_mode) == 0o700
    env_file = session.checkout / "docker" / (".env.%s" % ENV)
    assert stat.S_IMODE(env_file.stat().st_mode) == 0o600
    values = init_cmd.read_env_file(env_file)
    assert values["WIKI_ROOT"] == str(instance) and values["DATA_DIR"] == str(opts.data_dir) \
        and values["PORT"] == str(session.port) and values["MANIFOLD_TLS"] == "off"
    # no shared token, anywhere
    assert "MANIFOLD_TOKEN" not in env_file.read_text()
    assert "Claude Code" in session.text and "VS Code" in session.text and "Browser" in session.text


def test_the_principals_are_what_the_plan_said(session):
    assert session.run() == 0
    from manifold_security import principals
    conn = session.options().data_dir and __import__("manifold_security.store", fromlist=["x"]).open_store(
        session.options().data_dir, wiki_root=session.options().instance)
    try:
        by_name = {p.name: p for p in principals.list_principals(conn)}
        assert set(by_name) == {"admin", "pat", "first-agent"}
        assert principals.roles_of(conn, by_name["admin"].id) == ["admin"]
        assert principals.grants_of(conn, by_name["admin"].id) == []
        assert by_name["pat"].kind == "human" and principals.roles_of(conn, by_name["pat"].id) == ["contributor", "reader"]
        assert by_name["first-agent"].kind == "agent"
        assert principals.roles_of(conn, by_name["first-agent"].id) == ["contributor", "reader", "registrar"]
        for name in ("pat", "first-agent"):
            assert principals.grants_of(conn, by_name[name].id) == ["_shared", "example-api", "example-web"]
        # the administrator has no credential; the other two have exactly one, with no expiry
        counts = {r["name"]: r["n"] for r in conn.execute(
            "SELECT p.name, COUNT(c.credential_id) n FROM principals p LEFT JOIN credentials c "
            "ON c.principal_id = p.id GROUP BY p.name")}
        assert counts == {"admin": 0, "pat": 1, "first-agent": 1}
        assert conn.execute("SELECT COUNT(*) FROM credentials WHERE expires_at IS NOT NULL").fetchone()[0] == 0
    finally:
        conn.close()


# ── credentials ──────────────────────────────────────────────────────────────

def secrets_of(session):
    creds = session.options().data_dir / "credentials"
    return {p.stem: p.read_text().strip() for p in creds.glob("*.secret")}


def test_a_credential_appears_only_in_its_file_and_never_in_output_logs_or_any_other_file(session):
    assert session.run() == 0
    found = secrets_of(session)
    assert set(found) == {"pat", "first-agent"} and all(v.startswith("mf_") for v in found.values())
    for name, token in found.items():
        path = session.options().data_dir / "credentials" / ("%s.secret" % name)
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        secret = token.split("_", 2)[2]
        assert secret not in session.text and token not in session.text
        assert secret not in session.services.log.read_text()
        holders = [p for p in session.tmp_path.rglob("*") if p.is_file() and ".git" not in p.parts
                   and secret.encode() in p.read_bytes()]
        assert holders == [path]


def test_credentials_go_to_the_files_the_person_names_and_nowhere_else(session, tmp_path):
    mine, agents = tmp_path / "keys" / "pat.secret", tmp_path / "keys" / "agent.secret"
    assert session.run(person_secret_file=mine, agent_secret_file=agents) == 0, session.text
    assert mine.read_text().startswith("mf_") and agents.read_text().startswith("mf_")
    assert stat.S_IMODE(mine.stat().st_mode) == 0o600 and stat.S_IMODE(agents.stat().st_mode) == 0o600
    assert not list((session.options().data_dir / "credentials").glob("*.secret"))  # moved, not copied
    secret = mine.read_text().split("_", 2)[2]
    assert [p for p in tmp_path.rglob("*") if p.is_file() and secret.encode() in p.read_bytes()] == [mine]


def test_a_named_credential_file_that_exists_is_never_overwritten_and_the_run_is_undone(session, tmp_path):
    mine = tmp_path / "mine.secret"
    mine.write_text("keep me")
    assert session.run(person_secret_file=mine) == 1
    assert mine.read_text() == "keep me" and "does not overwrite" in session.text and nothing_made(session)


# ── undo ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("fail_on", [
    "commit -q -m", "git init", "admin bootstrap", "svc_ctl.sh production start", "admin principal list",
])
def test_a_failure_at_any_step_leaves_no_created_path(checkout, services, tmp_path, fail_on):
    services.fail_on = fail_on
    session = Session(checkout, services, tmp_path)
    assert session.run() == 1
    assert "Init failed" in session.text and "Nothing from this run is left" in session.text
    assert nothing_made(session)
    if "start" in fail_on or "principal list" in fail_on:
        assert any(c.endswith("production stop") for c in services.calls)  # the service is stopped again


def test_a_server_that_never_gets_healthy_is_undone_with_a_clear_message(checkout, services, tmp_path):
    services._start = lambda: subprocess.CompletedProcess([], 0, "", "")  # "starts", but nothing listens
    session = Session(checkout, services, tmp_path)
    assert session.run(wait_seconds=4) == 1
    assert "did not become healthy within 4 seconds" in session.text and "logs" in session.text
    assert nothing_made(session)


def test_a_failed_walk_through_is_undone(session, monkeypatch):
    monkeypatch.setattr(init_cmd, "walk_through", lambda rt, state: (_ for _ in ()).throw(init_cmd.InitError("boom")))
    assert session.run() == 1 and "boom" in session.text and nothing_made(session)
    assert any(c.endswith("production stop") for c in session.services.calls)


def test_an_interrupt_is_undone_too(session, monkeypatch):
    monkeypatch.setattr(init_cmd, "wait_healthy", lambda rt, state, wait: (_ for _ in ()).throw(KeyboardInterrupt()))
    assert session.run() == 1 and "interrupted" in session.text and nothing_made(session)


def test_undo_never_removes_what_was_there_before(checkout, services, tmp_path):
    session = Session(checkout, services, tmp_path)
    instance = session.options().instance
    shutil.copytree(REAL_REPO / "examples" / "starter", instance)
    subprocess.run(["git", "init", "-q"], cwd=instance, check=True)
    (instance / "wiki" / "mine.md").write_text("my page")
    before = tree(instance)
    services.fail_on = "admin bootstrap"
    assert session.run() == 1
    assert tree(instance) == before  # the existing instance is exactly as it was
    assert not session.options().data_dir.exists()


# ── run it again ─────────────────────────────────────────────────────────────

def test_a_second_run_detects_what_exists_and_changes_nothing_without_a_yes(session):
    assert session.run() == 0
    opts = session.options()
    watched = [opts.instance, opts.data_dir / "credentials", session.checkout / "docker"]
    before = tree(*watched)
    second = Session(session.checkout, session.services, session.tmp_path, tty=False)
    second.port = session.port
    assert second.run(yes=False) == 1
    assert "Something is already here" in second.text and "Not a terminal" in second.text
    assert tree(*watched) == before


def test_a_second_run_with_yes_creates_nothing_and_changes_no_credential(session):
    assert session.run() == 0
    opts = session.options()
    watched = [opts.instance, opts.data_dir / "credentials", session.checkout / "docker"]
    before = tree(*watched)
    second = Session(session.checkout, session.services, session.tmp_path)
    second.port = session.port
    assert second.run() == 0, second.text
    assert "3 already exist: none are created or changed" in second.text
    assert "walk-through" in second.text and "skipped" in second.text
    assert tree(*watched) == before


def test_a_second_run_answering_no_at_the_prompt_changes_nothing(session):
    assert session.run() == 0
    opts = session.options()
    before = tree(opts.instance, session.checkout / "docker")
    second = Session(session.checkout, session.services, session.tmp_path, tty=True)
    second.port = session.port
    second.answers = ["n"]
    assert second.run(yes=False) == 0 and "Nothing was changed" in second.text
    assert tree(opts.instance, session.checkout / "docker") == before


def test_repair_fills_in_only_what_is_missing(session):
    assert session.run() == 0
    opts = session.options()
    session.services.stop()
    shutil.rmtree(opts.data_dir / "caddy")
    second = Session(session.checkout, session.services, session.tmp_path)
    second.port = session.port
    assert second.run() == 0
    assert (opts.data_dir / "caddy" / "data").is_dir()


def test_an_instance_that_used_the_shared_token_is_adopted_through_repair(checkout, services, tmp_path):
    """INT-1 S8: an old settings file with a token line and an instance with no store."""
    session = Session(checkout, services, tmp_path)
    instance = session.options().instance
    shutil.copytree(REAL_REPO / "examples" / "starter", instance)
    subprocess.run(["git", "init", "-q"], cwd=instance, check=True)
    subprocess.run(["git", "add", "-A"], cwd=instance, check=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t.test", "commit", "-q", "-m", "mine"], cwd=instance, check=True)
    env_file = checkout / "docker" / (".env.%s" % ENV)
    old = "WIKI_ROOT=%s\nPORT=%d\nENVIRONMENT=production\nBIND_ADDRESS=127.0.0.1\nMANIFOLD_TOKEN=old-shared-token-old-shared-token\n" % (
        instance, session.port)
    env_file.write_text(old)
    assert session.run(instance=None, data_dir=tmp_path / "manifold-data") == 0, session.text
    text = env_file.read_text()
    assert text.startswith(old.rstrip("\n"))                      # nothing existing was changed
    assert "DATA_DIR=%s" % (tmp_path / "manifold-data") in text   # what was missing was added
    assert "MANIFOLD_TOKEN=old-shared-token-old-shared-token" in text
    assert "Something is already here" in session.text and "registered example-api" in session.text.replace("first agent ", "")
    log = subprocess.run(["git", "log", "--format=%s"], cwd=instance, capture_output=True, text=True).stdout
    assert "mine" in log


def test_an_environment_file_that_points_elsewhere_is_not_overridden(checkout, services, tmp_path):
    session = Session(checkout, services, tmp_path)
    (checkout / "docker" / (".env.%s" % ENV)).write_text("WIKI_ROOT=%s\n" % (tmp_path / "somewhere"))
    assert session.run() == 2 and "already points at" in session.text
    assert not session.options().instance.exists()


# ── the MCP client and the journal ───────────────────────────────────────────

class FakeResponse:
    def __init__(self, body, kind="application/json", session=None):
        self._body, self.headers = body.encode(), {"Content-Type": kind}
        if session:
            self.headers["Mcp-Session-Id"] = session

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_the_mcp_client_reads_json_and_event_stream_answers_and_keeps_the_session():
    sent = []
    answers = [
        FakeResponse('{"jsonrpc":"2.0","id":1,"result":{"serverInfo":{"name":"manifold"}}}', session="abc"),
        FakeResponse("", "text/plain"),
        FakeResponse('event: message\ndata: {"jsonrpc":"2.0","id":2,"result":{"structuredContent":{"status":"created"}}}\n\n',
                     "text/event-stream"),
    ]

    def opener(request, timeout):
        sent.append(request)
        return answers.pop(0)
    client = McpClient("http://x.test:1", "mf_aaa_bbb", opener=opener)
    assert client.initialize()["serverInfo"]["name"] == "manifold"
    assert client.call_tool("t", {"a": 1}) == {"status": "created"}
    assert sent[0].get_header("Authorization") == "Bearer mf_aaa_bbb" and sent[2].get_header("Mcp-session-id") == "abc"
    assert "mf_aaa_bbb" not in repr(client)


def test_the_mcp_client_reports_a_refusal_without_the_credential():
    def opener(request, timeout):
        raise urllib.error.HTTPError(request.full_url, 401, "no", {}, None)
    client = McpClient("http://x.test:1", "mf_secret_value", opener=opener)
    with pytest.raises(McpError) as caught:
        client.initialize()
    assert "401" in str(caught.value) and "mf_secret_value" not in str(caught.value)


def test_the_journal_undoes_in_reverse_removes_only_what_it_made_and_restores_appended_files(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "keep.txt").write_text("keep")
    notes = tmp_path / "notes.txt"
    notes.write_text("before")
    order = []
    journal = Journal()
    journal.created(tmp_path / "made")
    (tmp_path / "made").mkdir()
    (tmp_path / "made" / "child").write_text("x")
    journal.restore(notes, "before")
    notes.write_text("before and after")
    journal.action("stopped", lambda: order.append("stop"))
    with pytest.raises(FileExistsError):
        journal.created(existing)  # never claims what exists
    assert journal.undo() == []
    assert order == ["stop"] and not (tmp_path / "made").exists() and notes.read_text() == "before"
    assert (existing / "keep.txt").read_text() == "keep"


def test_the_journal_goes_on_past_a_failure_and_reports_it(tmp_path):
    journal = Journal()
    journal.created(tmp_path / "a")
    (tmp_path / "a").write_text("x")
    journal.action("boom", lambda: (_ for _ in ()).throw(RuntimeError("no")))
    problems = journal.undo()
    assert len(problems) == 1 and "boom" in problems[0] and not (tmp_path / "a").exists()
