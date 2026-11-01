# SPDX-License-Identifier: Apache-2.0
"""The startup rules (PHASE_1_PLAN T21): empty start, non-loopback, no off switch, the legacy token."""

import re
from pathlib import Path

import pytest

from manifold_security import audit, principals, settings
from manifold_security.startup import StartupError, check_startup, is_loopback

SERVER_DIR = Path(__file__).resolve().parents[1]


def rows(conn, event):
    return [dict(r) for r in conn.execute("SELECT * FROM audit WHERE event = ?", (event,))]


# ── the empty start (D1) ─────────────────────────────────────────────────────

def test_an_empty_store_on_loopback_starts_with_a_warning_that_names_the_init_command(security_conn):
    report = check_startup(security_conn, "127.0.0.1", {})
    assert len(report.notices) == 1
    assert "./manifold init" in report.notices[0] and "refuses every request" in report.notices[0]


def test_an_empty_store_with_no_host_given_also_starts_with_the_warning(security_conn):
    assert "./manifold init" in check_startup(security_conn, None, {}).notices[0]


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.5", "wiki.example.test"])
def test_an_empty_store_on_another_address_refuses_to_start_and_names_the_command(security_conn, host):
    with pytest.raises(StartupError, match=r"\./manifold init"):
        check_startup(security_conn, host, {})


def test_with_a_principal_every_address_starts_without_a_notice(security_conn):
    principals.create_principal(security_conn, "root", "human")
    for host in ("127.0.0.1", "0.0.0.0", None):
        assert check_startup(security_conn, host, {}).notices == []


def test_an_empty_start_refuses_every_request(monkeypatch, wiki_root, auth_world):
    """With the store holding no principal, the real middleware answers 401 to everything but /health."""
    import asyncio
    from wiki_backend.auth import PrincipalAuthMiddleware, StoreAccess
    from manifold_security.store import open_store
    empty = auth_world.data_dir.parent / "empty-store"
    open_store(empty, wiki_root=auth_world.data_dir.parent / "wiki-root").close()
    sent = []

    async def app(scope, receive, send):
        sent.append("reached")

    async def send(message):
        sent.append(message.get("status"))
    middleware = PrincipalAuthMiddleware(app, store=StoreAccess(empty))
    for path in ("/mcp", "/sse", "/ingest", "/docs/", "/"):
        asyncio.run(middleware({"type": "http", "path": path, "headers": []}, None, send))
    assert "reached" not in sent and sent.count(401) == 5


# ── the notices are recorded ─────────────────────────────────────────────────

def test_notices_are_written_to_the_audit_unless_told_not_to(security_conn):
    check_startup(security_conn, "127.0.0.1", {}, record=False)
    assert rows(security_conn, audit.STARTUP_NOTICE) == []
    check_startup(security_conn, "127.0.0.1", {})
    assert len(rows(security_conn, audit.STARTUP_NOTICE)) == 1


# ── the old shared token ─────────────────────────────────────────────────────

@pytest.mark.parametrize("variable", ["MANIFOLD_TOKEN", "MANIFOLD_TOKEN_FILE"])
def test_the_legacy_token_is_reported_as_no_longer_accepted_and_the_command_is_named(security_conn, variable):
    principals.create_principal(security_conn, "root", "human")
    report = check_startup(security_conn, "127.0.0.1", {variable: "something"})
    assert len(report.notices) == 1
    assert variable in report.notices[0] and "no longer accepted" in report.notices[0]
    assert "./manifold init" in report.notices[0]


def test_an_empty_legacy_variable_is_not_a_notice(security_conn):
    principals.create_principal(security_conn, "root", "human")
    assert check_startup(security_conn, "127.0.0.1", {"MANIFOLD_TOKEN": "  "}).notices == []


def test_the_old_token_does_not_authenticate(auth_world, monkeypatch):
    from wiki_backend.auth import StoreAccess
    monkeypatch.setenv("MANIFOLD_TOKEN", "t" * 40)
    assert StoreAccess().authenticate("t" * 40).caller is None


# ── there is no off switch ───────────────────────────────────────────────────

OFF_SWITCH = re.compile(r"(NO|DISABLE|SKIP|OFF|ANON|INSECURE|OPEN|UNSAFE)[A-Z_]*AUTH|AUTH[A-Z_]*(OFF|DISABLE|NONE|OPTIONAL)"
                        r"|(DISABLE|NO)[_]?(SECURITY|TOKEN|PROTECTION)", re.IGNORECASE)


def test_no_setting_turns_authentication_off():
    assert [key for key in settings.SPECS if OFF_SWITCH.search(key) or "auth" in key] == []
    for key in settings.SPECS:
        with pytest.raises(settings.SettingError):
            settings.parse(key + "_off", "true")


def test_no_environment_variable_or_flag_in_the_server_can_turn_it_off():
    names = set()
    for path in [SERVER_DIR / "server.py", *(SERVER_DIR / "wiki_backend").rglob("*.py"),
                 *(SERVER_DIR / "manifold_security").rglob("*.py")]:
        names |= set(re.findall(r"MANIFOLD_[A-Z0-9_]+", path.read_text(encoding="utf-8")))
    legacy = {"MANIFOLD_TOKEN", "MANIFOLD_TOKEN_FILE"}  # named only to report that they are ignored
    assert [n for n in names - legacy if OFF_SWITCH.search(n)] == []


def test_the_legacy_variables_are_only_ever_reported_never_read_as_a_secret():
    for path in [SERVER_DIR / "server.py", *(SERVER_DIR / "wiki_backend").rglob("*.py")]:
        assert "MANIFOLD_TOKEN" not in path.read_text(encoding="utf-8"), path.name


def test_loopback_helper():
    assert all(is_loopback(h) for h in ("127.0.0.1", "::1", "[::1]", "localhost"))
    assert not any(is_loopback(h) for h in ("0.0.0.0", "", "10.0.0.1"))


# ── the server module applies them ───────────────────────────────────────────

def test_the_server_applies_the_rules_when_it_starts(monkeypatch, auth_world, caplog):
    pytest.importorskip("fastmcp")
    import logging
    import server
    from manifold_security import principals as p
    for principal in p.list_principals(auth_world.conn):  # make the store empty
        auth_world.conn.execute("DELETE FROM principals WHERE id = ?", (principal.id,))
    monkeypatch.setenv("MANIFOLD_HOST", "0.0.0.0")
    with pytest.raises(StartupError, match=r"\./manifold init"):
        server._check_auth_settings()
    monkeypatch.setenv("MANIFOLD_HOST", "127.0.0.1")
    monkeypatch.setenv("MANIFOLD_TOKEN", "x" * 30)
    with caplog.at_level(logging.WARNING):
        server._check_auth_settings()
    text = caplog.text
    assert "refuses every request" in text and "no longer accepted" in text
