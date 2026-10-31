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
