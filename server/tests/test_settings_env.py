# SPDX-License-Identifier: Apache-2.0
"""A deployment can give a few settings a starting value in the environment (PHASE_1_PLAN T29)."""

import pytest

from manifold_security import settings


def test_the_environment_gives_the_starting_value_of_trusted_proxies_hosts_origins_and_tls(security_conn, monkeypatch):
    monkeypatch.setenv("MANIFOLD_TRUSTED_PROXIES", "172.30.173.0/24")
    monkeypatch.setenv("MANIFOLD_ALLOWED_HOSTS", "wiki.example.test,192.168.1.5:8686")
    monkeypatch.setenv("MANIFOLD_ALLOWED_ORIGINS", "https://wiki.example.test")
    monkeypatch.setenv("MANIFOLD_TLS", "on")
    assert settings.get(security_conn, "trusted_proxies") == ["172.30.173.0/24"]
    assert settings.get(security_conn, "allowed_hosts") == ["wiki.example.test", "192.168.1.5:8686"]
    assert settings.get(security_conn, "allowed_origins") == ["https://wiki.example.test"]
    assert settings.get(security_conn, "tls") == "on"


def test_a_value_set_with_the_host_command_wins_over_the_environment(security_conn, monkeypatch):
    monkeypatch.setenv("MANIFOLD_TRUSTED_PROXIES", "172.30.173.0/24")
    settings.set_value(security_conn, "trusted_proxies", "10.0.0.0/8")
    assert settings.get(security_conn, "trusted_proxies") == ["10.0.0.0/8"]
    settings.unset(security_conn, "trusted_proxies")
    assert settings.get(security_conn, "trusted_proxies") == ["172.30.173.0/24"]


def test_an_empty_variable_is_the_default(security_conn, monkeypatch):
    monkeypatch.setenv("MANIFOLD_ALLOWED_HOSTS", "")
    monkeypatch.setenv("MANIFOLD_TLS", "  ")
    assert settings.get(security_conn, "allowed_hosts") == [] and settings.get(security_conn, "tls") == "off"


def test_a_bad_value_in_the_environment_is_refused_and_names_the_variable(security_conn, monkeypatch):
    monkeypatch.setenv("MANIFOLD_TLS", "maybe")
    with pytest.raises(settings.SettingError, match="MANIFOLD_TLS"):
        settings.get(security_conn, "tls")


def test_limits_and_the_security_relevant_numbers_cannot_be_set_from_the_environment(security_conn, monkeypatch):
    monkeypatch.setenv("MANIFOLD_THROTTLE_FAILURE_THRESHOLD", "100000")
    monkeypatch.setenv("MANIFOLD_AGENT_REGISTRATIONS_PER_DAY", "1000")
    assert settings.get(security_conn, "throttle_failure_threshold") == 5
    assert settings.get(security_conn, "agent_registrations_per_day") == 5
