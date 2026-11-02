# SPDX-License-Identifier: Apache-2.0
"""Tests for the instance health checks and the /health route."""

import os

import pytest

from wiki_backend.health import wiki_health


def test_a_complete_instance_is_healthy(wiki_root):
    healthy, payload = wiki_health(wiki_root)
    assert healthy and payload["status"] == "healthy"
    assert payload["checks"]["manifold.yaml"].startswith("ok (7 components")
    assert payload["checks"]["wiki writable"] == "ok" and payload["checks"]["git repository"] == "ok"


def test_missing_root_is_unhealthy(tmp_path):
    healthy, payload = wiki_health(tmp_path / "nope")
    assert not healthy and "does not exist" in payload["message"]


@pytest.mark.parametrize("name", ["wiki/CLAUDE.md", "wiki/log.md"])
def test_missing_required_page_is_unhealthy(wiki_root, name):
    (wiki_root / name).unlink()
    healthy, payload = wiki_health(wiki_root)
    assert not healthy and name in payload["message"] and payload["checks"][name] == "missing"


def test_missing_manifold_yaml_is_unhealthy_and_says_what_to_do(wiki_root):
    (wiki_root / "manifold.yaml").unlink()
    healthy, payload = wiki_health(wiki_root)
    assert not healthy and "manifold.yaml not found" in payload["message"]
    assert payload["checks"]["manifold.yaml"] == "invalid"


def test_invalid_manifold_yaml_is_unhealthy(wiki_root):
    (wiki_root / "manifold.yaml").write_text("version: 7\n")
    healthy, payload = wiki_health(wiki_root)
    assert not healthy and "version must be 1" in payload["message"]


@pytest.mark.skipif(os.geteuid() == 0, reason="root can write anywhere")
def test_unwritable_wiki_folder_is_unhealthy(wiki_root):
    wiki = wiki_root / "wiki"
    wiki.chmod(0o555)
    try:
        healthy, payload = wiki_health(wiki_root)
    finally:
        wiki.chmod(0o755)
    assert not healthy and "not writable" in payload["message"]


def test_missing_git_is_only_a_warning(wiki_root):
    import shutil
    shutil.rmtree(wiki_root / ".git")
    healthy, payload = wiki_health(wiki_root)
    assert healthy and payload["checks"]["git repository"].startswith("warning")


# ── the route ────────────────────────────────────────────────────────────────

def _client(monkeypatch, root):
    pytest.importorskip("fastmcp")
    from starlette.testclient import TestClient
    import server
    monkeypatch.setattr(server, "WIKI_ROOT", root)
    return TestClient(server.asgi_app, base_url="http://127.0.0.1:8686")  # an address the Host guard accepts


def test_route_returns_200_with_checks_when_healthy(wiki_root, monkeypatch, auth_world):
    # Detail is shown to an authenticated caller only (the unauthenticated answer is tested in test_auth.py).
    response = _client(monkeypatch, wiki_root).get(
        "/health", headers={"Authorization": "Bearer " + auth_world.human_token})
    assert response.status_code == 200
    assert response.json()["status"] == "healthy" and "checks" in response.json()


def test_route_returns_500_when_the_instance_is_broken(wiki_root, monkeypatch):
    (wiki_root / "manifold.yaml").unlink()
    response = _client(monkeypatch, wiki_root).get("/health")
    assert response.status_code == 500 and response.json()["status"] == "unhealthy"
