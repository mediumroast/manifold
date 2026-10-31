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
    assert volumes == ["${WIKI_ROOT}:/workspace"]


def test_dockerfile_installs_with_the_lock_file():
    assert "pip install -r requirements.txt -c requirements.lock" in _dockerfile()
    assert "requirements.lock" in re.search(r"^COPY .*requirements\.txt.*$", _dockerfile(), re.M).group(0)


def test_dockerfile_carries_the_assets_and_the_bundles():
    text = _dockerfile()
    assert "COPY assets/ ./assets/" in text and "COPY bundles/ ./bundles/" in text
    assert "tools/build.py --out dist" in text


def test_compose_publishes_on_loopback_by_default():
    ports = _compose()["services"]["manifold"]["ports"]
    assert ports == ["${BIND_ADDRESS:-127.0.0.1}:${PORT:-8686}:${PORT:-8686}"]


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


def test_the_image_build_context_excludes_local_env_files():
    ignored = (DOCKER.parent / ".dockerignore").read_text()
    for name in ("docker/.env.production", "docker/.env.staging", "docker/.env.dev", "**/.env"):
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
def service_folder(tmp_path):
    if not shutil.which("docker"):
        pytest.skip("svc_ctl.sh needs the docker command line before it gets as far as the instance check")
    root = tmp_path / "svc"
    (root / "docker").mkdir(parents=True)
    shutil.copy(DOCKER.parent / "svc_ctl.sh", root / "svc_ctl.sh")
    for name in ("docker-compose.yml", "docker-compose.dev.yml", ".env.dev.template"):
        shutil.copy(DOCKER / name, root / "docker" / name)
    run(root, "dev", "init-env")
    return root


def run(root, *args):
    return subprocess.run(["bash", str(root / "svc_ctl.sh"), *args], cwd=root, capture_output=True, text=True,
                          env=dict(os.environ, NO_COLOR="1"))


def set_wiki_root(root, value):
    env_file = root / "docker" / ".env.dev"
    lines = [("WIKI_ROOT=%s" % value) if line.startswith("WIKI_ROOT=") else line for line in env_file.read_text().splitlines()]
    env_file.write_text("\n".join(lines) + "\n")


def test_init_env_generates_a_token_in_a_private_file(service_folder):
    env_file = service_folder / "docker" / ".env.dev"
    token = [line for line in env_file.read_text().splitlines() if line.startswith("MANIFOLD_TOKEN=")][0].split("=", 1)[1]
    assert len(token) >= 24 and oct(env_file.stat().st_mode & 0o777) == "0o600"


def test_start_refuses_the_placeholder_instance_path(service_folder):
    result = run(service_folder, "dev", "start")
    assert result.returncode != 0 and "/path/to/your/instance" in result.stderr + result.stdout
    assert "is not a folder" in result.stderr + result.stdout


def test_start_refuses_a_folder_that_is_not_an_instance(service_folder, tmp_path):
    (tmp_path / "plain").mkdir()
    set_wiki_root(service_folder, tmp_path / "plain")
    result = run(service_folder, "dev", "start")
    assert result.returncode != 0 and "No manifold.yaml" in result.stderr + result.stdout


def test_start_goes_on_to_docker_for_a_real_instance(service_folder, tmp_path):
    (tmp_path / "inst").mkdir()
    (tmp_path / "inst" / "manifold.yaml").write_text("version: 1\n")
    set_wiki_root(service_folder, tmp_path / "inst")
    output = run(service_folder, "dev", "start")
    assert "WIKI_ROOT" not in output.stderr + output.stdout or "docker" in (output.stderr + output.stdout).lower()
    assert "No manifold.yaml" not in output.stderr + output.stdout and "is not a folder" not in output.stderr + output.stdout


def test_templates_ask_for_an_instance_path():
    for env in ("dev", "staging", "production"):
        text = (DOCKER / (".env.%s.template" % env)).read_text()
        assert "WIKI_ROOT=/path/to/your/instance" in text and "manifold.yaml" in text
