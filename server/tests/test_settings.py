# SPDX-License-Identifier: Apache-2.0
"""The settings registry: defaults, overrides, refusals."""

import pytest

from manifold_security import settings
from manifold_security.settings import SettingError


def test_defaults_as_planned(security_conn):
    values = settings.get_all(security_conn)
    assert values == {
        "agent_registrations_per_day": 5,
        "agent_archives_per_day": 1,
        "purge_hold_days": 14,
        "throttle_failure_threshold": 5,
        "throttle_window_seconds": 600,
        "throttle_base_delay_seconds": 1,
        "throttle_max_delay_seconds": 900,
        "allowed_hosts": [],
        "allowed_origins": [],
        "trusted_proxies": [],
        "tls": "off",
    }


def test_there_is_no_setting_that_turns_authentication_off():
    for key in settings.SPECS:
        lowered = key.lower()
        assert not any(word in lowered for word in ("auth", "token", "disable", "insecure", "open")), key


def test_override_persists_and_unset_restores_default(security_conn):
    assert settings.set_value(security_conn, "agent_registrations_per_day", "9") == 9
    assert settings.get(security_conn, "agent_registrations_per_day") == 9
    settings.unset(security_conn, "agent_registrations_per_day")
    assert settings.get(security_conn, "agent_registrations_per_day") == 5


def test_override_is_seen_by_another_connection(tmp_path, security_conn):
    from manifold_security.store import open_store
    settings.set_value(security_conn, "purge_hold_days", 30)
    other = open_store(tmp_path / "security-data", wiki_root=tmp_path / "wiki-root")
    assert settings.get(other, "purge_hold_days") == 30
    other.close()


@pytest.mark.parametrize("key,value,fragment", [
    ("agent_registrations_per_day", "-1", "from 0 to 1000"),
    ("agent_registrations_per_day", "1001", "from 0 to 1000"),
    ("agent_archives_per_day", "many", "whole number from 0 to 1000"),
    ("purge_hold_days", "3651", "from 0 to 3650"),
    ("throttle_failure_threshold", "0", "from 1 to 1000"),
    ("throttle_window_seconds", "86401", "from 1 to 86400"),
    ("throttle_base_delay_seconds", "0", "from 1 to 3600"),
    ("tls", "maybe", "one of: off, on"),
    ("allowed_origins", "example.com", "not an origin"),
    ("allowed_origins", "https://example.com/path", "not an origin"),
    ("allowed_hosts", "https://example.com", "not a host"),
    ("trusted_proxies", "not-an-ip", "not an IP address"),
])
def test_out_of_range_or_malformed_is_refused_with_the_range(security_conn, key, value, fragment):
    with pytest.raises(SettingError, match=fragment):
        settings.set_value(security_conn, key, value)
    assert security_conn.execute("SELECT COUNT(*) FROM settings").fetchone()[0] == 0


def test_unknown_key_is_refused_and_lists_known_keys(security_conn):
    with pytest.raises(SettingError, match="Unknown setting 'auth_required'.*tls"):
        settings.set_value(security_conn, "auth_required", "off")
    with pytest.raises(SettingError, match="Unknown setting"):
        settings.get(security_conn, "nope")


def test_boolean_is_not_a_number(security_conn):
    with pytest.raises(SettingError):
        settings.set_value(security_conn, "purge_hold_days", True)


def test_lists_parse_and_round_trip(security_conn):
    settings.set_value(security_conn, "allowed_hosts", "wiki.example.org, wiki.example.org:8443")
    settings.set_value(security_conn, "allowed_origins", ["https://wiki.example.org"])
    settings.set_value(security_conn, "trusted_proxies", "172.18.0.0/16,::1")
    assert settings.get(security_conn, "allowed_hosts") == ["wiki.example.org", "wiki.example.org:8443"]
    assert settings.get(security_conn, "allowed_origins") == ["https://wiki.example.org"]
    assert settings.get(security_conn, "trusted_proxies") == ["172.18.0.0/16", "::1"]


def test_default_lists_are_not_shared_between_calls(security_conn):
    settings.get(security_conn, "allowed_hosts").append("mutated")
    assert settings.get(security_conn, "allowed_hosts") == []


def test_base_delay_may_not_exceed_max_delay(security_conn):
    with pytest.raises(SettingError, match="must not exceed"):
        settings.set_value(security_conn, "throttle_base_delay_seconds", 1000)
    settings.set_value(security_conn, "throttle_max_delay_seconds", 2000)
    assert settings.set_value(security_conn, "throttle_base_delay_seconds", 1000) == 1000


def test_tls_choice_is_case_insensitive(security_conn):
    assert settings.set_value(security_conn, "tls", "ON") == "on"
