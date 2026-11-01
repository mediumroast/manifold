# SPDX-License-Identifier: Apache-2.0
"""Guards on the container files: the defaults that must not come back."""

import re
from pathlib import Path

import pytest
import yaml

DOCKER = Path(__file__).resolve().parents[2] / "docker"

pytestmark = pytest.mark.skipif(not (DOCKER / "Dockerfile").is_file(), reason="no docker/ folder beside the server")


def _dockerfile() -> str:
    return (DOCKER / "Dockerfile").read_text()


def _compose(name="docker-compose.yml") -> dict:
    return yaml.safe_load((DOCKER / name).read_text())


def test_dockerfile_never_reloads_and_runs_without_root():
    text = _dockerfile()
    assert "--reload" not in text
    assert re.search(r"^USER manifold$", text, re.M)
    assert re.search(r"^HEALTHCHECK .*\n\s+CMD curl .*127\.0\.0\.1.*/health", text, re.M)


def test_dockerfile_has_one_instance_mount_point_and_it_matches_compose():
    text = _dockerfile()
    assert text.count("CONTAINER_WIKI_ROOT=") == 1 and "CONTAINER_WIKI_ROOT=/workspace" in text
    volumes = _compose()["services"]["manifold"]["volumes"]
    assert len(volumes) == 2 and volumes[0] == "${WIKI_ROOT}:/workspace" and volumes[1].endswith(":/data")


def test_dockerfile_installs_with_the_lock_file():
    assert "pip install -r requirements.txt -c requirements.lock" in _dockerfile()
    assert "requirements.lock" in re.search(r"^COPY .*requirements\.txt.*$", _dockerfile(), re.M).group(0)


def test_dockerfile_carries_the_assets_and_the_bundles():
    text = _dockerfile()
    assert "COPY assets/ ./assets/" in text and "COPY bundles/ ./bundles/" in text
    assert "tools/build.py --out dist" in text


def test_compose_publishes_on_loopback_by_default_and_only_through_caddy():
    services = _compose()["services"]
    assert "ports" not in services["manifold"]  # the server's port is never published directly
    assert services["caddy"]["ports"] == ["${BIND_ADDRESS:-127.0.0.1}:${PORT:-8686}:${PORT:-8686}"]


def test_compose_does_not_mount_source_or_run_a_command():
    service = _compose()["services"]["manifold"]
    assert not any("server" in v or v.startswith("..") for v in service["volumes"])
    assert "command" not in service
    assert service["read_only"] is True and service["cap_drop"] == ["ALL"]
    assert "no-new-privileges:true" in service["security_opt"]


def test_only_the_dev_overlay_mounts_source_and_reloads():
    dev = _compose("docker-compose.dev.yml")["services"]["manifold"]
    assert any("server" in v for v in dev["volumes"]) and "--reload" in dev["command"][-1]


@pytest.mark.parametrize("env", ["dev", "staging", "production"])
def test_env_templates_bind_loopback_and_do_not_set_the_mount_point(env):
    text = (DOCKER / (".env.%s.template" % env)).read_text()
    assert "BIND_ADDRESS=127.0.0.1" in text and "CONTAINER_WIKI_ROOT" not in text
    assert "MANIFOLD_TLS=off" in text and "DATA_DIR=" in text


def test_the_image_build_context_excludes_local_env_files():
    ignored = (DOCKER.parent / ".dockerignore").read_text()
    for name in ("docker/.env.production", "docker/.env.staging", "docker/.env.dev", "**/.env", ".manifold-data/"):
        assert name in ignored


# ── dependencies ─────────────────────────────────────────────────────────────

SERVER = Path(__file__).resolve().parents[1]


def _names(path):
    return {re.split(r"[<>=~!\[; ]", line.strip(), 1)[0].lower().replace("_", "-")
            for line in path.read_text().splitlines() if line.strip() and not line.startswith(("#", "-"))}


def test_every_runtime_requirement_has_a_floor_and_a_ceiling():
    for line in (SERVER / "requirements.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            assert ">=" in line and "<" in line, line


def test_every_requirement_is_pinned_in_the_lock():
    locked = {line.split("==")[0].lower().replace("_", "-") for line in (SERVER / "requirements.lock").read_text().splitlines()
              if "==" in line}
    assert _names(SERVER / "requirements.txt") <= locked


def test_the_lock_satisfies_the_ranges():
    from importlib.metadata import version as installed
    pins = {line.split("==")[0].lower(): line.split("==")[1] for line in (SERVER / "requirements.lock").read_text().splitlines()
            if "==" in line}
    for line in (SERVER / "requirements.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name = re.split(r"[<>=~!\[]", line, 1)[0].strip().lower()
        floor = re.search(r">=([\d.]+)", line).group(1)
        ceiling = re.search(r"<([\d.]+)", line).group(1)
        pinned = tuple(int(p) for p in pins[name].split("."))
        assert tuple(int(p) for p in floor.split(".")) <= pinned < tuple(int(p) for p in ceiling.split(".")), name


def test_unused_packages_are_not_requirements():
    declared = _names(SERVER / "requirements.txt")
    assert not {"aiofiles", "python-dotenv"} & declared


# ── svc_ctl.sh: the instance check ───────────────────────────────────────────

import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402


@pytest.fixture()
def service_folder(tmp_path, monkeypatch):
    """A scratch copy of svc_ctl.sh and the compose files, with a stand-in `docker` that only records its calls."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "docker"
    # `compose ps` prints a container id only when FAKE_RUNNING is set, so both admin routes can be tried.
    fake.write_text('#!/bin/sh\necho "$@" >> "%s"\ncase " $* " in *" ps "*) [ -n "$FAKE_RUNNING" ] && echo abc123;; esac\nexit 0\n'
                    % (tmp_path / "docker.log"))
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir) + os.pathsep + os.environ["PATH"])
    root = tmp_path / "svc"
    (root / "docker").mkdir(parents=True)
    shutil.copy(DOCKER.parent / "svc_ctl.sh", root / "svc_ctl.sh")
    for name in ("docker-compose.yml", "docker-compose.dev.yml", ".env.dev.template", ".env.staging.template",
                 ".env.production.template"):
        shutil.copy(DOCKER / name, root / "docker" / name)
    shutil.copytree(DOCKER / "caddy", root / "docker" / "caddy")
    run(root, "dev", "init-env")
    return root


def docker_calls(root):
    log = root.parent / "docker.log"
    return log.read_text().splitlines() if log.exists() else []


def run(root, *args):
    return subprocess.run(["bash", str(root / "svc_ctl.sh"), *args], cwd=root, capture_output=True, text=True,
                          env=dict(os.environ, NO_COLOR="1"))


def set_wiki_root(root, value, environment="dev"):
    env_file = root / "docker" / (".env.%s" % environment)
    lines = [("WIKI_ROOT=%s" % value) if line.startswith("WIKI_ROOT=") else line for line in env_file.read_text().splitlines()]
    env_file.write_text("\n".join(lines) + "\n")


def test_init_env_creates_a_private_file_and_data_folder_and_no_token(service_folder):
    env_file = service_folder / "docker" / ".env.dev"
    text = env_file.read_text()
    assert "MANIFOLD_TOKEN" not in text and oct(env_file.stat().st_mode & 0o777) == "0o600"
    data = service_folder / ".manifold-data" / "dev"
    assert "DATA_DIR=%s" % data in text
    assert data.is_dir() and oct(data.stat().st_mode & 0o777) == "0o700"
    assert (data / "caddy" / "data").is_dir() and (data / "caddy" / "config").is_dir()
    assert "MANIFOLD_TLS=off" in text and "BIND_ADDRESS=127.0.0.1" in text


def test_start_refuses_the_placeholder_instance_path(service_folder):
    result = run(service_folder, "dev", "start")
    assert result.returncode != 0 and "/path/to/your/instance" in result.stderr + result.stdout
    assert "is not a folder" in result.stderr + result.stdout


def test_start_refuses_a_folder_that_is_not_an_instance(service_folder, tmp_path):
    (tmp_path / "plain").mkdir()
    set_wiki_root(service_folder, tmp_path / "plain")
    result = run(service_folder, "dev", "start")
    assert result.returncode != 0 and "No manifold.yaml" in result.stderr + result.stdout


def _instance(tmp_path):
    (tmp_path / "inst").mkdir()
    (tmp_path / "inst" / "manifold.yaml").write_text("version: 1\n")
    return tmp_path / "inst"


def test_start_goes_on_to_compose_for_a_real_instance(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    result = run(service_folder, "dev", "start")
    assert result.returncode == 0, result.stderr + result.stdout
    up = [c for c in docker_calls(service_folder) if " up " in c + " "]
    assert len(up) == 1 and "up -d --build" in up[0] and "--project-name manifold-dev" in up[0]


def test_only_the_dev_environment_adds_the_overlay(service_folder, tmp_path):
    inst = _instance(tmp_path)
    run(service_folder, "production", "init-env")
    set_wiki_root(service_folder, inst, "production")
    set_wiki_root(service_folder, inst)
    run(service_folder, "dev", "start")
    run(service_folder, "production", "start")
    calls = [c for c in docker_calls(service_folder) if " up " in c + " "]
    dev = [c for c in calls if "manifold-dev" in c][0]
    production = [c for c in calls if "manifold-production" in c][0]
    assert "docker-compose.dev.yml" in dev and "docker-compose.dev.yml" not in production


def test_health_checks_the_instance_before_calling_compose(service_folder, tmp_path):
    result = run(service_folder, "dev", "health")
    assert result.returncode != 0 and "WIKI_ROOT" in result.stderr + result.stdout
    assert not [c for c in docker_calls(service_folder) if " run " in c + " "]
    set_wiki_root(service_folder, _instance(tmp_path))
    assert run(service_folder, "dev", "health").returncode == 0
    assert [c for c in docker_calls(service_folder) if " run " in c + " "]


def test_templates_ask_for_an_instance_path():
    for env in ("dev", "staging", "production"):
        text = (DOCKER / (".env.%s.template" % env)).read_text()
        assert "WIKI_ROOT=/path/to/your/instance" in text and "manifold.yaml" in text


# ── the data volume: no shared token, a /data mount outside the instance (T28) ─

def test_no_shared_token_in_the_compose_files_or_the_templates():
    for path in [DOCKER / "docker-compose.yml", DOCKER / "docker-compose.dev.yml", DOCKER / "Dockerfile",
                 *(DOCKER / (".env.%s.template" % e) for e in ("dev", "staging", "production"))]:
        assert "MANIFOLD_TOKEN" not in path.read_text(), path.name


def test_the_server_keeps_a_read_only_root_and_gets_a_data_mount_outside_the_instance():
    service = _compose()["services"]["manifold"]
    assert service["read_only"] is True and service["user"] == "${HOST_UID}:${HOST_GID}"
    data = [v for v in service["volumes"] if v.endswith(":/data")]
    assert len(data) == 1 and data[0].startswith("${DATA_DIR")
    assert "WIKI_ROOT" not in data[0] and "/workspace" not in data[0]  # not inside the instance mount
    assert service["environment"]["MANIFOLD_DATA_DIR"] == "/data"


def test_the_container_uses_the_rollback_journal_because_wal_fails_on_a_shared_bind_mount():
    # PHASE_1_PLAN T1: two container processes on one bind-mounted folder (the server and `admin`).
    assert _compose()["services"]["manifold"]["environment"]["MANIFOLD_STORE_JOURNAL_MODE"] == "delete"
    assert "MANIFOLD_STORE_JOURNAL_MODE=delete" in _dockerfile() and "MANIFOLD_DATA_DIR=/data" in _dockerfile()


def test_the_server_is_on_an_internal_network_with_no_route_out():
    compose = _compose()
    assert compose["services"]["manifold"]["networks"] == ["internal"]
    assert compose["networks"]["internal"]["internal"] is True
    assert set(compose["services"]["caddy"]["networks"]) == {"internal", "edge"}


# ── Caddy and the TLS switch (T29) ───────────────────────────────────────────

def test_caddy_is_pinned_by_tag_and_digest_and_locked_down():
    caddy = _compose()["services"]["caddy"]
    assert re.fullmatch(r"caddy:\d+\.\d+\.\d+-alpine@sha256:[0-9a-f]{64}", caddy["image"])
    assert caddy["read_only"] is True and caddy["cap_drop"] == ["ALL"] and caddy["user"] == "${HOST_UID}:${HOST_GID}"
    assert "no-new-privileges:true" in caddy["security_opt"]
    assert any(v.endswith(":/caddy") for v in caddy["volumes"])  # its data and config are writable, under the data folder


def test_both_caddyfiles_exist_and_neither_names_a_public_acme_issuer():
    on = (DOCKER / "caddy" / "Caddyfile.on").read_text()
    off = (DOCKER / "caddy" / "Caddyfile.off").read_text()
    for text in (on, off):
        code = "\n".join(line for line in text.splitlines() if not line.strip().startswith("#"))
        assert not re.search(r"acme|letsencrypt|zerossl|acme-v02|issuer|\bca\b", code, re.I), code
        assert "reverse_proxy manifold:{$PORT}" in code
    assert "tls internal" in on and "auto_https off" in off


def test_caddy_mounts_the_caddyfile_that_matches_the_tls_setting():
    volumes = _compose()["services"]["caddy"]["volumes"]
    assert "./caddy/Caddyfile.${MANIFOLD_TLS:-off}:/etc/caddy/Caddyfile:ro" in volumes


def test_the_server_is_told_the_tls_setting_and_that_caddy_is_a_trusted_proxy():
    env = _compose()["services"]["manifold"]["environment"]
    assert env["MANIFOLD_TLS"] == "${MANIFOLD_TLS:-off}"
    assert "MANIFOLD_INTERNAL_SUBNET" in env["MANIFOLD_TRUSTED_PROXIES"]


def run_with(root, extra_env, *args):
    return subprocess.run(["bash", str(root / "svc_ctl.sh"), *args], cwd=root, capture_output=True, text=True,
                          env=dict(os.environ, NO_COLOR="1", **extra_env))


def test_init_env_turns_tls_on_for_an_address_other_than_loopback(tmp_path, service_folder):
    result = run_with(service_folder, {"BIND_ADDRESS": "192.168.1.5"}, "staging", "init-env")
    text = (service_folder / "docker" / ".env.staging").read_text()
    assert result.returncode == 0 and "BIND_ADDRESS=192.168.1.5" in text and "MANIFOLD_TLS=on" in text
    assert "HTTPS is on" in result.stdout


def test_start_refuses_plain_http_on_a_network_address(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    env_file = service_folder / "docker" / ".env.dev"
    env_file.write_text(env_file.read_text().replace("BIND_ADDRESS=127.0.0.1", "BIND_ADDRESS=0.0.0.0"))
    result = run(service_folder, "dev", "start")
    assert result.returncode != 0 and "MANIFOLD_TLS=off" in result.stderr + result.stdout
    assert "MANIFOLD_ALLOW_PLAIN_ON_NETWORK" in result.stderr + result.stdout
    assert not [c for c in docker_calls(service_folder) if " up " in c + " "]


def test_start_allows_plain_http_on_a_network_address_only_as_a_deliberate_act_with_a_warning(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    env_file = service_folder / "docker" / ".env.dev"
    env_file.write_text(env_file.read_text().replace("BIND_ADDRESS=127.0.0.1", "BIND_ADDRESS=0.0.0.0"))
    result = run_with(service_folder, {"MANIFOLD_ALLOW_PLAIN_ON_NETWORK": "yes"}, "dev", "start")
    assert result.returncode == 0, result.stderr
    assert "WARNING: serving plain HTTP on 0.0.0.0" in result.stderr
    assert [c for c in docker_calls(service_folder) if " up " in c + " "]


def test_start_goes_ahead_with_tls_on_for_a_network_address(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    env_file = service_folder / "docker" / ".env.dev"
    env_file.write_text(env_file.read_text().replace("BIND_ADDRESS=127.0.0.1", "BIND_ADDRESS=0.0.0.0")
                        .replace("MANIFOLD_TLS=off", "MANIFOLD_TLS=on"))
    result = run(service_folder, "dev", "start")
    assert result.returncode == 0 and "WARNING" not in result.stderr


def test_an_invalid_tls_value_is_refused(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    env_file = service_folder / "docker" / ".env.dev"
    env_file.write_text(env_file.read_text().replace("MANIFOLD_TLS=off", "MANIFOLD_TLS=maybe"))
    assert "must be 'off' or 'on'" in run(service_folder, "dev", "start").stderr


def test_start_warns_when_the_old_settings_file_still_has_a_shared_token(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    env_file = service_folder / "docker" / ".env.dev"
    env_file.write_text(env_file.read_text() + "MANIFOLD_TOKEN=old-shared-token-old-shared-token\n")
    result = run(service_folder, "dev", "start")
    assert result.returncode == 0 and "no longer accepted" in result.stderr and "old-shared-token" not in result.stderr


def test_start_refuses_a_data_folder_inside_the_instance(service_folder, tmp_path):
    inst = _instance(tmp_path)
    set_wiki_root(service_folder, inst)
    env_file = service_folder / "docker" / ".env.dev"
    lines = [("DATA_DIR=%s" % (inst / "data")) if line.startswith("DATA_DIR=") else line
             for line in env_file.read_text().splitlines()]
    env_file.write_text("\n".join(lines) + "\n")
    result = run(service_folder, "dev", "start")
    assert result.returncode != 0 and "inside the instance repository" in result.stderr
    assert not (inst / "data").exists()


def test_start_creates_a_missing_private_data_folder(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    data = service_folder / ".manifold-data" / "dev"
    shutil.rmtree(data)
    assert run(service_folder, "dev", "start").returncode == 0
    assert oct(data.stat().st_mode & 0o777) == "0o700" and (data / "caddy" / "config").is_dir()


# ── svc_ctl.sh admin (T29) ───────────────────────────────────────────────────

def test_admin_runs_a_one_off_container_when_the_server_is_not_running(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    result = run(service_folder, "dev", "admin", "principal", "list")
    assert result.returncode == 0, result.stderr
    calls = docker_calls(service_folder)
    runs = [c for c in calls if " run " in c + " "]
    assert len(runs) == 1 and "--rm" in runs[0] and "--no-deps" in runs[0]
    assert runs[0].endswith("manifold python -m manifold_cli admin principal list")
    assert not [c for c in calls if " exec " in c + " "]


def test_admin_execs_in_the_running_container(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    result = run_with(service_folder, {"FAKE_RUNNING": "1"}, "dev", "admin", "credential", "revoke", "abc")
    assert result.returncode == 0, result.stderr
    execs = [c for c in docker_calls(service_folder) if " exec " in c + " "]
    assert len(execs) == 1 and execs[0].endswith("manifold python -m manifold_cli admin credential revoke abc")
    assert " -T " in execs[0]  # no terminal here, so none is asked for inside the container


def test_admin_needs_a_command(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    result = run(service_folder, "dev", "admin")
    assert result.returncode != 0 and "admin needs a command" in result.stderr


def test_admin_works_with_the_environment_given_after_the_command(service_folder, tmp_path):
    set_wiki_root(service_folder, _instance(tmp_path))
    assert run(service_folder, "admin", "dev", "principal", "list").returncode == 0


# ── the CI workflow (T30; whether it passes in GitHub Actions is observed there, not here) ──

def test_the_ci_workflow_parses_has_a_macos_job_and_never_skips_certificate_checks():
    path = DOCKER.parent / ".github" / "workflows" / "server.yml"
    workflow = yaml.safe_load(path.read_text())
    jobs = workflow["jobs"]
    assert jobs["tests-macos"]["runs-on"] == "macos-latest"
    assert "docker" not in path.read_text().split("tests-macos:")[1].split("  image:")[0].lower().replace("no docker", "")
    text = path.read_text()
    assert re.search(r"\bcurl\b[^\n]*(\s-k\b|--insecure)", text) is None
    assert "--cacert" in text and "MANIFOLD_TLS=on" in text and "admin credential issue" in text
    assert "ReadonlyRootfs" in text and "no longer accepted" in text


# ── the compose files render for both TLS settings (real docker, if present) ──

@pytest.mark.skipif(subprocess.run("docker compose version", shell=True, capture_output=True).returncode != 0,
                    reason="docker compose is not available")
@pytest.mark.parametrize("tls,caddyfile", [("off", "Caddyfile.off"), ("on", "Caddyfile.on")])
def test_compose_config_renders_for_tls_on_and_off(tmp_path, tls, caddyfile):
    root = tmp_path / "svc"
    (root / "docker").mkdir(parents=True)
    shutil.copy(DOCKER.parent / "svc_ctl.sh", root / "svc_ctl.sh")
    for name in ("docker-compose.yml", "docker-compose.dev.yml", ".env.production.template"):
        shutil.copy(DOCKER / name, root / "docker" / name)
    shutil.copytree(DOCKER / "caddy", root / "docker" / "caddy")
    inst = _instance(tmp_path)
    assert run_with(root, {"BIND_ADDRESS": "127.0.0.1"}, "production", "init-env").returncode == 0
    env_file = root / "docker" / ".env.production"
    text = env_file.read_text().replace("WIKI_ROOT=/path/to/your/instance", "WIKI_ROOT=%s" % inst)
    text = text.replace("MANIFOLD_TLS=off", "MANIFOLD_TLS=%s" % tls).replace(
        "TLS_NAMES=localhost 127.0.0.1", "TLS_NAMES=localhost 127.0.0.1 192.168.1.5")
    env_file.write_text(text)
    result = run(root, "production", "config")
    assert result.returncode == 0, result.stderr
    assert caddyfile in result.stdout
    assert "https://localhost:8686, https://127.0.0.1:8686, https://192.168.1.5:8686" in result.stdout
    assert "CADDY_DEFAULT_SNI: 192.168.1.5" in result.stdout
    assert "MANIFOLD_TLS: " + ("'on'" if tls == "on" else "'off'") in result.stdout
    assert "published:" in result.stdout and result.stdout.count("published:") == 1  # only Caddy publishes
