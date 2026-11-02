# SPDX-License-Identifier: Apache-2.0
"""admin grant / deny / authority / settings / registrar-flag (PHASE_1_PLAN T24)."""

import pytest

from manifold_security import principals, settings


@pytest.fixture()
def alice(cli):
    cli("principal", "create", "alice")
    cli("role", "set", "alice", "contributor")


def state(cli):
    conn = cli.store()
    try:
        p = principals.get_principal(conn, "alice")
        return {"grants": principals.grants_of(conn, p.id), "denies": principals.denies_of(conn, p.id),
                "self": p.may_self_grant_on_register}
    finally:
        conn.close()


def test_grant_add_and_remove(cli, alice):
    assert cli("grant", "add", "alice", "acme-api")[0] == 0
    assert cli("grant", "add", "alice", "_shared")[0] == 0
    assert state(cli)["grants"] == ["_shared", "acme-api"]
    assert cli("grant", "remove", "alice", "acme-api")[0] == 0
    assert state(cli)["grants"] == ["_shared"]
    code, _, err = cli("grant", "remove", "alice", "acme-api")
    assert code == 1 and "no grant" in err


def test_a_scope_that_is_not_a_slug_is_refused(cli, alice):
    code, _, err = cli("grant", "add", "alice", "Not A Slug")
    assert code == 1 and "not a component slug" in err


def test_removing_a_grant_names_the_routes_that_remain_and_how_to_end_access(cli, alice):
    cli("grant", "add", "alice", "acme-api")
    code, out, _ = cli("grant", "remove", "alice", "acme-api")
    assert code == 0
    assert "reading" in out and "contributor" in out  # the role still reads everything
    assert "repository" in out and "not available in this version" in out  # authority 'either' by default
    assert "none left on acme-api" in out
    assert "deny add alice acme-api" in out and "principal disable alice" in out


def test_removing_a_grant_when_the_authority_is_grants_only_does_not_mention_the_repository(cli, alice):
    cli("authority", "set", "acme-api", "grants")
    cli("grant", "add", "alice", "acme-api")
    out = cli("grant", "remove", "alice", "acme-api")[1]
    assert "through the repository" not in out


def test_deny_add_remove_and_the_advice(cli, alice):
    code, out, _ = cli("deny", "add", "alice", "acme-api")
    assert code == 0 and "principal disable alice" in out and state(cli)["denies"] == ["acme-api"]
    assert cli("deny", "remove", "alice", "acme-api")[0] == 0 and state(cli)["denies"] == []
    assert cli("deny", "remove", "alice", "acme-api")[0] == 1


def test_authority_set(cli):
    assert cli("authority", "set", "acme-api", "grants")[0] == 0
    conn = cli.store()
    assert principals.get_authority(conn, "acme-api") == "grants"
    conn.close()
    with pytest.raises(SystemExit):
        cli("authority", "set", "acme-api", "anything")  # not one of the three: a usage error
    assert cli("authority", "set", "_shared", "grants")[0] == 1  # _shared is not a component


def test_settings_list_get_set_unset(cli):
    code, out, _ = cli("settings", "list")
    assert code == 0 and "agent_registrations_per_day" in out and "throttle_max_delay_seconds" in out
    assert cli("settings", "get", "agent_registrations_per_day")[1].strip().endswith("5")
    assert cli("settings", "set", "agent_registrations_per_day", "7")[0] == 0
    assert cli("settings", "get", "agent_registrations_per_day")[1].strip().endswith("7")
    assert cli("settings", "unset", "agent_registrations_per_day")[0] == 0
    assert cli("settings", "get", "agent_registrations_per_day")[1].strip().endswith("5")


@pytest.mark.parametrize("key,value,range_text", [
    ("agent_registrations_per_day", "100000", "from 0 to 1000"),
    ("throttle_failure_threshold", "0", "from 1 to 1000"),
    ("purge_hold_days", "abc", "from 0 to 3650"),
    ("tls", "maybe", "one of: off, on"),
])
def test_out_of_range_settings_are_refused_with_the_range(cli, key, value, range_text):
    code, _, err = cli("settings", "set", key, value)
    assert code == 1 and range_text in err
    conn = cli.store()
    assert settings.get(conn, key) == settings.SPECS[key].default
    conn.close()


def test_an_unknown_setting_is_refused_and_the_known_ones_are_listed(cli):
    code, _, err = cli("settings", "set", "auth_enabled", "false")
    assert code == 1 and "Unknown setting" in err and "tls" in err


def test_list_settings_take_comma_separated_values(cli):
    assert cli("settings", "set", "allowed_hosts", "wiki.example.test,10.0.0.5:8686")[0] == 0
    conn = cli.store()
    assert settings.get(conn, "allowed_hosts") == ["wiki.example.test", "10.0.0.5:8686"]
    conn.close()
    assert cli("settings", "set", "allowed_origins", "https://wiki.example.test/path")[0] == 1


def test_registrar_flag(cli, alice):
    assert cli("registrar-flag", "set", "alice", "--self-grant", "on")[0] == 0
    assert state(cli)["self"] is True
    assert cli("registrar-flag", "set", "alice", "--self-grant", "off")[0] == 0
    assert state(cli)["self"] is False


def test_changes_are_audited(cli, alice):
    cli("grant", "add", "alice", "acme-api")
    cli("deny", "add", "alice", "acme-api")
    cli("settings", "set", "purge_hold_days", "30")
    cli("authority", "set", "acme-api", "grants")
    conn = cli.store()
    events = {r["event"] for r in conn.execute("SELECT event FROM audit")}
    conn.close()
    assert {"grant.changed", "deny.changed", "setting.changed", "authority.changed"} <= events
