# SPDX-License-Identifier: Apache-2.0
"""The host command skeleton and runner (PHASE_1_PLAN T22): where a command runs, exit codes, stdlib only."""

import io
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from manifold_cli import runner

SERVER_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SERVER_DIR.parent


@pytest.fixture()
def fake_svc_ctl(tmp_path):
    """A stand-in for ./svc_ctl.sh (whose `admin` route, which calls docker, arrives in T29): records its arguments."""
    record = tmp_path / "svc_ctl.args"
    script = tmp_path / "svc_ctl.sh"
    script.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "' + str(record) + '"\nexit "${FAKE_EXIT:-0}"\n')
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script, record


# ── the launcher and the import ──────────────────────────────────────────────

def test_manifold_cli_imports_with_the_standard_library_only():
    code = ("import sys, manifold_cli, manifold_cli.runner, manifold_cli.admin, manifold_cli.purge\n"
            "third = sorted(m for m in sys.modules if m.split('.')[0] in {'yaml', 'fastmcp', 'starlette', 'mcp', "
            "'pydantic', 'frontmatter', 'uvicorn', 'anyio'})\n"
            "assert not third, third\n")
    # -S: no site-packages, so a third-party import would fail outright.
    done = subprocess.run([sys.executable, "-S", "-c", code], cwd=SERVER_DIR, capture_output=True, text=True,
                          env={"PYTHONPATH": str(SERVER_DIR), "PATH": os.environ.get("PATH", "")})
    assert done.returncode == 0, done.stderr


def test_the_launcher_runs_the_command_and_passes_the_exit_status(tmp_path):
    launcher = REPO_ROOT / "manifold"
    assert os.access(launcher, os.X_OK)
    base = [sys.executable, str(launcher), "admin", "--data-dir", str(tmp_path / "d"), "--wiki-root", str(tmp_path / "w")]
    created = subprocess.run(base + ["principal", "create", "alice"], capture_output=True, text=True)
    assert created.returncode == 0 and "Created human alice" in created.stdout
    missing = subprocess.run(base + ["principal", "show", "nobody"], capture_output=True, text=True)
    assert missing.returncode == 1 and missing.stderr.startswith("error: No principal")


def test_the_launcher_checks_the_python_version(tmp_path):
    text = (REPO_ROOT / "manifold").read_text()
    assert "MINIMUM = (3, 11)" in text and "needs Python" in text
    probe = text.replace("MINIMUM = (3, 11)", "MINIMUM = (99, 0)")
    fake = tmp_path / "manifold"
    fake.write_text(probe)
    done = subprocess.run([sys.executable, str(fake), "admin"], capture_output=True, text=True)
    assert done.returncode == 1 and "needs Python 99.0 or newer" in done.stderr


# ── where it runs ────────────────────────────────────────────────────────────

def test_env_hands_the_command_to_svc_ctl_and_returns_its_exit_status(fake_svc_ctl, monkeypatch):
    script, record = fake_svc_ctl
    code = runner.main(["admin", "--env", "dev", "principal", "list"], svc_ctl=script)
    assert code == 0
    assert record.read_text().split() == ["dev", "admin", "principal", "list"]
    monkeypatch.setenv("FAKE_EXIT", "7")
    assert runner.main(["admin", "--env=staging", "principal", "list"], svc_ctl=script) == 7
    assert record.read_text().split() == ["staging", "admin", "principal", "list"]


def test_env_does_not_pass_the_hosts_wiki_root_into_the_container(fake_svc_ctl):
    script, record = fake_svc_ctl
    runner.main(["admin", "--env", "dev", "--wiki-root", "/host/path", "principal", "list"], svc_ctl=script)
    assert "/host/path" not in record.read_text() and "--wiki-root" not in record.read_text()


def test_env_with_a_missing_svc_ctl_says_what_to_do():
    err = io.StringIO()
    code = runner.main(["admin", "--env", "dev", "principal", "list"], err=err, svc_ctl=Path("/nonexistent/svc_ctl.sh"))
    assert code == 1 and "Cannot find" in err.getvalue() and "--data-dir" in err.getvalue()


def test_env_and_data_dir_together_are_refused():
    err = io.StringIO()
    assert runner.main(["admin", "--env", "dev", "--data-dir", "/x", "principal", "list"], err=err) == 1
    assert "either --env or --data-dir" in err.getvalue()


def test_with_no_place_to_run_it_says_how_to_choose(monkeypatch):
    monkeypatch.delenv("MANIFOLD_DATA_DIR", raising=False)
    err = io.StringIO()
    assert runner.main(["admin", "principal", "list"], err=err) == 1
    assert "--env" in err.getvalue() and "--data-dir" in err.getvalue() and "MANIFOLD_DATA_DIR" in err.getvalue()


def test_inside_the_container_the_data_folder_comes_from_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("MANIFOLD_DATA_DIR", str(tmp_path / "volume"))
    monkeypatch.setenv("CONTAINER_WIKI_ROOT", str(tmp_path / "wiki"))
    out = io.StringIO()
    assert runner.main(["admin", "principal", "create", "alice"], out=out) == 0
    assert (tmp_path / "volume" / "manifold.db").is_file()


def test_a_data_folder_inside_the_instance_is_refused_with_the_fix(tmp_path):
    err = io.StringIO()
    code = runner.main(["admin", "--data-dir", str(tmp_path / "wiki" / "data"), "--wiki-root", str(tmp_path / "wiki"),
                        "principal", "list"], err=err)
    assert code == 1 and "inside the instance repository" in err.getvalue()


# ── exit codes and output ────────────────────────────────────────────────────

def test_a_usage_error_exits_2(cli):
    with pytest.raises(SystemExit) as caught:
        cli("principal", "frobnicate")
    assert caught.value.code == 2


def test_a_refused_command_exits_1_with_one_line_on_stderr(cli):
    code, out, err = cli("role", "set", "ghost", "reader")
    assert code == 1 and err.startswith("error: ") and err.count("\n") == 1 and out.count("empty one was created") == 1


def test_init_checks_its_environment_name():
    err = io.StringIO()
    assert runner.main(["init", "--env", "nonsense"], err=err) == 1
    assert "dev, staging or production" in err.getvalue()
