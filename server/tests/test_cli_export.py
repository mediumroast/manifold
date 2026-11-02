# SPDX-License-Identifier: Apache-2.0
"""admin audit show / export / import (PHASE_1_PLAN T25)."""

import json
import os
import stat

import pytest

from manifold_security import export, principals, settings, tokens
from tests.conftest import CliRunner


@pytest.fixture()
def populated(cli, tmp_path):
    cli("principal", "create", "alice")
    cli("principal", "create", "build-bot", "--kind", "agent")
    cli("role", "set", "alice", "contributor")
    cli("role", "set", "alice", "registrar")
    cli("role", "set", "build-bot", "reader")
    cli("grant", "add", "alice", "acme-api")
    cli("deny", "add", "alice", "acme-web")
    cli("authority", "set", "acme-api", "grants")
    cli("settings", "set", "purge_hold_days", "30")
    cli("settings", "set", "allowed_hosts", "wiki.example.test")
    secret = tmp_path / "alice.secret"
    assert cli("credential", "issue", "alice", "--secret-file", str(secret))[0] == 0
    return secret.read_text().strip()


@pytest.fixture()
def other(tmp_path):
    return CliRunner(tmp_path / "other-data", tmp_path / "wiki-root")


def snapshot(runner):
    conn = runner.store()
    try:
        data = export.export_store(conn)
        data.pop("exported_at")
        return data
    finally:
        conn.close()


def test_export_then_import_into_an_empty_store_reproduces_roles_grants_denies_authority_and_settings(
        cli, other, populated, tmp_path):
    path = tmp_path / "out.json"
    assert cli("export", str(path))[0] == 0
    code, out, err = other("import", str(path))
    assert code == 0, err
    assert snapshot(other) == snapshot(cli)
    data = json.loads(path.read_text())
    alice = next(p for p in data["principals"] if p["name"] == "alice")
    assert alice["roles"] == ["contributor", "registrar"] and alice["grants"] == ["acme-api"]
    assert alice["denies"] == ["acme-web"] and data["component_authority"] == {"acme-api": "grants"}
    assert data["settings"]["purge_hold_days"] == "30"


def test_the_default_export_has_no_credential_no_hash_and_no_secret(cli, populated, tmp_path):
    path = tmp_path / "out.json"
    cli("export", str(path))
    text = path.read_text()
    secret = populated.split("_", 2)[2]
    assert "credentials" not in json.loads(text) and "secret_hash" not in text and secret not in text
    assert json.loads(text)["includes_hashes"] is False
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600


def test_export_with_hashes_carries_hashes_so_a_credential_still_works_but_never_the_secret(
        cli, other, populated, tmp_path):
    path = tmp_path / "out.json"
    cli("export", "--with-hashes", str(path))
    text = path.read_text()
    assert "secret_hash" in text and populated.split("_", 2)[2] not in text
    assert other("import", str(path))[0] == 0
    conn = other.store()
    assert tokens.verify(conn, populated).ok
    conn.close()


def test_export_never_overwrites_a_file(cli, populated, tmp_path):
    path = tmp_path / "out.json"
    path.write_text("keep me")
    code, _, err = cli("export", str(path))
    assert code == 1 and "already exists" in err and path.read_text() == "keep me"


def test_import_into_a_store_that_has_principals_needs_a_flag(cli, other, populated, tmp_path):
    path = tmp_path / "out.json"
    cli("export", str(path))
    other("principal", "create", "carol")
    code, _, err = other("import", str(path))
    assert code == 1 and "--merge" in err and "--replace" in err
    assert [p["name"] for p in snapshot(other)["principals"]] == ["carol"]


def test_merge_adds_and_keeps_what_was_there(cli, other, populated, tmp_path):
    path = tmp_path / "out.json"
    cli("export", str(path))
    other("principal", "create", "carol")
    other("principal", "create", "alice")  # same name: merged by name
    code, out, err = other("import", "--merge", str(path))
    assert code == 0, err
    names = [p["name"] for p in snapshot(other)["principals"]]
    assert names == ["alice", "build-bot", "carol"]
    conn = other.store()
    alice = principals.get_principal(conn, "alice")
    assert principals.roles_of(conn, alice.id) == ["contributor", "registrar"]
    assert principals.grants_of(conn, alice.id) == ["acme-api"]
    conn.close()


def test_replace_makes_the_store_match_the_file(cli, other, populated, tmp_path):
    path = tmp_path / "out.json"
    cli("export", str(path))
    other("principal", "create", "carol")
    other("settings", "set", "tls", "on")
    assert other("import", "--replace", str(path))[0] == 0
    now = snapshot(other)
    assert [p["name"] for p in now["principals"]] == ["alice", "build-bot"]
    assert "tls" not in now["settings"] and now["settings"]["purge_hold_days"] == "30"


def test_a_dry_run_changes_nothing_and_says_what_would_happen(cli, other, populated, tmp_path):
    path = tmp_path / "out.json"
    cli("export", str(path))
    before = snapshot(other)
    code, out, _ = other("import", "--dry-run", str(path))
    assert code == 0 and "Dry run, nothing changed" in out and "principals added 2" in out
    assert snapshot(other) == before
    other("principal", "create", "carol")
    before = snapshot(other)
    assert other("import", "--replace", "--dry-run", str(path))[0] == 0
    assert snapshot(other) == before


@pytest.mark.parametrize("change,message", [
    ({"version": 2}, "not supported"),
    ({"format": "something-else"}, "not a Manifold security export"),
    ({"principals": "none"}, "must be a list"),
])
def test_a_file_with_the_wrong_shape_is_refused(cli, other, populated, tmp_path, change, message):
    path = tmp_path / "out.json"
    cli("export", str(path))
    data = json.loads(path.read_text())
    data.update(change)
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data))
    code, _, err = other("import", str(bad))
    assert code == 1 and message in err
    assert snapshot(other)["principals"] == []


def test_a_file_that_would_break_a_rule_is_refused_whole(cli, other, populated, tmp_path):
    path = tmp_path / "out.json"
    cli("export", str(path))
    data = json.loads(path.read_text())
    data["principals"][1]["roles"].append("admin")  # build-bot is an agent
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(data))
    code, _, err = other("import", str(bad))
    assert code == 1 and "cannot hold the admin role" in err
    assert snapshot(other)["principals"] == []  # nothing was imported, not even the valid principal


def test_unreadable_json_is_refused(other, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    code, _, err = other("import", str(bad))
    assert code == 1 and "Cannot read" in err


# ── audit show ───────────────────────────────────────────────────────────────

def test_audit_show_filters_by_principal_event_and_time(cli, populated):
    code, out, _ = cli("audit", "show")
    assert code == 0 and "credential.issued" in out and "role.changed" in out
    only_credentials = cli("audit", "show", "--event", "credential.")[1]
    assert "credential.issued" in only_credentials and "role.changed" not in only_credentials
    exact = cli("audit", "show", "--event", "role.changed")[1]
    assert exact.count("role.changed") == 3 and "credential" not in exact
    alice = cli("audit", "show", "--principal", "alice")[1]
    assert "acme-api" in alice or "contributor" in alice
    assert "No audit rows match" in cli("audit", "show", "--principal", "carol")[1]
    assert "credential.issued" in cli("audit", "show", "--since", "1d")[1]
    assert "No audit rows match" in cli("audit", "show", "--since", "2999-01-01")[1]


def test_audit_show_never_contains_a_secret(cli, populated):
    secret = populated.split("_", 2)[2]
    assert secret not in cli("audit", "show", "--limit", "500")[1]
