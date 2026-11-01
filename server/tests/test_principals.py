# SPDX-License-Identifier: Apache-2.0
"""Principals, roles, grants, denies, authority and component state."""

import subprocess
import sys

import pytest

from manifold_security import principals as pr
from manifold_security.principals import PrincipalError
from manifold_security.store import open_store
from wiki_backend import config


def test_slug_rule_matches_the_server_config_rule():
    assert pr._SLUG_RE.pattern == config._SLUG_RE.pattern and pr._MAX_SLUG == config._MAX_SLUG


def test_create_list_and_lookup(security_conn):
    a = pr.create_principal(security_conn, "alice", "human")
    b = pr.create_principal(security_conn, "billing-agent", "agent")
    assert a.active and a.id.startswith("p_") and not a.may_self_grant_on_register
    assert [p.name for p in pr.list_principals(security_conn)] == ["alice", "billing-agent"]
    assert pr.get_principal(security_conn, "alice") == a
    assert pr.get_principal(security_conn, b.id) == b
    assert pr.get_principal(security_conn, "ghost") is None
    assert pr.count_principals(security_conn) == 2


def test_names_are_unique_and_validated(security_conn):
    pr.create_principal(security_conn, "alice", "human")
    with pytest.raises(PrincipalError, match="already exists"):
        pr.create_principal(security_conn, "alice", "agent")
    for bad in ("", " lead", "a<b>", "x" * 65, None):
        with pytest.raises(PrincipalError, match="name must be"):
            pr.create_principal(security_conn, bad, "human")
    with pytest.raises(PrincipalError, match="kind must be"):
        pr.create_principal(security_conn, "bob", "robot")


def test_disable_and_enable(security_conn):
    p = pr.create_principal(security_conn, "alice", "human")
    assert pr.disable_principal(security_conn, "alice").active is False
    assert pr.get_principal(security_conn, p.id).active is False
    assert pr.enable_principal(security_conn, p.id).active is True
    with pytest.raises(PrincipalError, match="No principal"):
        pr.disable_principal(security_conn, "ghost")


def test_roles_set_unset_and_are_additive(security_conn):
    p = pr.create_principal(security_conn, "alice", "human")
    pr.set_role(security_conn, "alice", "reader")
    pr.set_role(security_conn, "alice", "contributor")
    pr.set_role(security_conn, "alice", "contributor")  # idempotent
    assert pr.roles_of(security_conn, p.id) == ["contributor", "reader"]
    assert pr.unset_role(security_conn, "alice", "reader") is True
    assert pr.unset_role(security_conn, "alice", "reader") is False
    assert pr.roles_of(security_conn, p.id) == ["contributor"]
    with pytest.raises(PrincipalError, match="role must be"):
        pr.set_role(security_conn, "alice", "root")


@pytest.mark.parametrize("kind", ["agent", "service"])
def test_admin_is_refused_for_agent_and_service(security_conn, kind):
    p = pr.create_principal(security_conn, "bot", kind)
    with pytest.raises(PrincipalError, match="admin role is for people only"):
        pr.set_role(security_conn, "bot", "admin")
    assert pr.roles_of(security_conn, p.id) == []
    pr.set_role(security_conn, "bot", "registrar")  # other roles are fine


def test_admin_is_allowed_for_a_human(security_conn):
    p = pr.create_principal(security_conn, "root-person", "human")
    pr.set_role(security_conn, p.id, "admin")
    assert pr.roles_of(security_conn, p.id) == ["admin"]


def test_grants_and_denies(security_conn):
    p = pr.create_principal(security_conn, "bot", "agent")
    pr.add_grant(security_conn, "bot", "acme-api")
    pr.add_grant(security_conn, "bot", "_shared")
    pr.add_grant(security_conn, "bot", "acme-api")  # idempotent
    pr.add_deny(security_conn, "bot", "acme.io")
    assert pr.grants_of(security_conn, p.id) == ["_shared", "acme-api"]
    assert pr.denies_of(security_conn, p.id) == ["acme.io"]
    assert pr.remove_grant(security_conn, "bot", "acme-api") is True
    assert pr.remove_grant(security_conn, "bot", "acme-api") is False
    assert pr.remove_deny(security_conn, "bot", "acme.io") is True
    assert pr.grants_of(security_conn, p.id) == ["_shared"] and pr.denies_of(security_conn, p.id) == []


def test_scope_must_be_a_slug_or_shared(security_conn):
    pr.create_principal(security_conn, "bot", "agent")
    for bad in ("Acme", "../x", "a/b", "_other", "", ".hidden", "x" * 65):
        with pytest.raises(PrincipalError, match="not a component slug"):
            pr.add_grant(security_conn, "bot", bad)
        with pytest.raises(PrincipalError):
            pr.add_deny(security_conn, "bot", bad)


def test_shared_is_not_a_component_slug(security_conn):
    assert pr.is_slug("_shared") is False
    with pytest.raises(PrincipalError, match="reserved"):
        pr.set_authority(security_conn, "_shared", "grants")
    with pytest.raises(PrincipalError, match="reserved"):
        pr.archive_component(security_conn, "_shared", "why", 14)
    with pytest.raises(PrincipalError, match="reserved"):
        pr.restore_component(security_conn, "_shared")


def test_self_grant_flag_defaults_off(security_conn):
    p = pr.create_principal(security_conn, "bot", "agent")
    assert p.may_self_grant_on_register is False
    pr.set_may_self_grant(security_conn, "bot", True)
    assert pr.get_principal(security_conn, "bot").may_self_grant_on_register is True


def test_authority_defaults_to_either(security_conn):
    assert pr.get_authority(security_conn, "acme-api") == "either"
    pr.set_authority(security_conn, "acme-api", "grants")
    assert pr.get_authority(security_conn, "acme-api") == "grants"
    with pytest.raises(PrincipalError, match="authority must be"):
        pr.set_authority(security_conn, "acme-api", "anyone")


def test_archive_and_restore(security_conn):
    pr.set_authority(security_conn, "acme-api", "grants")
    with pytest.raises(PrincipalError, match="reason is required"):
        pr.archive_component(security_conn, "acme-api", "  ", 14)
    state = pr.archive_component(security_conn, "acme-api", "retired", 14)
    assert state.archived and state.reason == "retired" and state.authority == "grants"
    assert state.archived_at < state.purge_after
    restored = pr.restore_component(security_conn, "acme-api")
    assert not restored.archived and restored.purge_after is None and restored.authority == "grants"
    assert not pr.get_component_state(security_conn, "never-seen").archived


def test_second_connection_sees_a_committed_mutation(tmp_path, security_conn):
    p = pr.create_principal(security_conn, "alice", "human")
    pr.set_role(security_conn, "alice", "contributor")
    pr.add_grant(security_conn, "alice", "acme-api")
    other = open_store(tmp_path / "security-data", wiki_root=tmp_path / "wiki-root")
    assert pr.roles_of(other, p.id) == ["contributor"]
    assert pr.grants_of(other, p.id) == ["acme-api"]
    other.close()


def test_another_process_sees_a_committed_mutation(tmp_path, security_conn):
    pr.create_principal(security_conn, "alice", "human")
    pr.disable_principal(security_conn, "alice")
    code = ("import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);"
            "print(c.execute(\"select active from principals where name='alice'\").fetchone()[0])")
    out = subprocess.run([sys.executable, "-c", code, str(tmp_path / "security-data" / "manifold.db")],
                         capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "0"


def test_failed_mutation_leaves_no_partial_state(security_conn):
    with pytest.raises(PrincipalError):
        pr.add_grant(security_conn, "ghost", "acme-api")
    assert security_conn.execute("SELECT COUNT(*) FROM grants").fetchone()[0] == 0
    assert not security_conn.in_transaction
