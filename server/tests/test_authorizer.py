# SPDX-License-Identifier: Apache-2.0
"""The authorizer: evaluation order, role matrix, revocation seen on the next call."""

from manifold_security import audit, tokens
from manifold_security import authorizer as az
from manifold_security import principals as pr
from manifold_security.store import open_store


def _mk(conn, name, kind="human", roles=(), grants=(), denies=()):
    p = pr.create_principal(conn, name, kind)
    for r in roles:
        pr.set_role(conn, p.id, r)
    for g in grants:
        pr.add_grant(conn, p.id, g)
    for d in denies:
        pr.add_deny(conn, p.id, d)
    return p


def test_capability_set_is_the_planned_one():
    assert set(az.CAPABILITIES) == {
        "read", "write", "handoff.create", "handoff.confirm", "handoff.reject", "handoff.close",
        "handoff.claim", "handoff.request_review", "component.register", "component.update",
        "component.protected_update", "component.archive", "component.restore", "ingest"}


def test_reader_reads_everywhere_but_writes_nothing(security_conn):
    p = _mk(security_conn, "r", roles=["reader"], grants=["acme-api"])
    assert az.authorize(security_conn, p.id, "read", "acme-api").via == "role"
    assert az.authorize(security_conn, p.id, "read").allowed
    d = az.authorize(security_conn, p.id, "write", "acme-api")
    assert not d and d.reason == az.ROLE_MISSING


def test_contributor_implies_reader_and_needs_a_grant_to_write(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"], grants=["acme-api"])
    assert az.authorize(security_conn, p.id, "read", "acme.io").allowed
    d = az.authorize(security_conn, p.id, "write", "acme-api")
    assert d.allowed and d.via == "grant"
    d = az.authorize(security_conn, p.id, "write", "acme.io")
    assert not d and d.reason == az.NO_GRANT


def test_a_grant_for_the_wrong_component_is_refused(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"], grants=["acme-web"])
    for cap in ("write", "handoff.create", "handoff.close", "handoff.claim", "ingest"):
        assert az.authorize(security_conn, p.id, cap, "acme-api").reason == az.NO_GRANT
        assert az.authorize(security_conn, p.id, cap, "acme-web").allowed


def test_a_grant_without_the_role_does_nothing(security_conn):
    p = _mk(security_conn, "g", roles=["reader"], grants=["acme-api"])
    assert az.authorize(security_conn, p.id, "handoff.close", "acme-api").reason == az.ROLE_MISSING


def test_a_deny_beats_a_grant(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"], grants=["acme-api", "_shared"], denies=["acme-api"])
    d = az.authorize(security_conn, p.id, "write", "acme-api")
    assert not d and d.reason == az.DENIED
    assert az.authorize(security_conn, p.id, "write", "_shared").allowed


def test_a_deny_beats_a_registrar_role_on_that_component(security_conn):
    p = _mk(security_conn, "reg", roles=["registrar"], denies=["acme-api"])
    assert az.authorize(security_conn, p.id, "component.archive", "acme-api").reason == az.DENIED
    assert az.authorize(security_conn, p.id, "component.archive", "acme-web").allowed


def test_reads_ignore_denies(security_conn):
    p = _mk(security_conn, "c", roles=["reader"], denies=["acme-api"])
    assert az.authorize(security_conn, p.id, "read", "acme-api").allowed


def test_admin_only_principal_is_refused_every_data_capability(security_conn):
    p = _mk(security_conn, "boss", roles=["admin"], grants=["acme-api", "_shared"])
    for cap in az.CAPABILITIES:
        d = az.authorize(security_conn, p.id, cap, "acme-api")
        assert not d and d.reason == az.ROLE_MISSING, cap


def test_registrar_implies_nothing_else(security_conn):
    p = _mk(security_conn, "reg", roles=["registrar"], grants=["acme-api"])
    assert az.authorize(security_conn, p.id, "component.register", "new-one").allowed
    assert az.authorize(security_conn, p.id, "read").reason == az.ROLE_MISSING
    assert az.authorize(security_conn, p.id, "write", "acme-api").reason == az.ROLE_MISSING


def test_protected_update_is_for_a_human_registrar_only(security_conn):
    human = _mk(security_conn, "hreg", "human", roles=["registrar"])
    bot = _mk(security_conn, "areg", "agent", roles=["registrar"])
    assert az.authorize(security_conn, human.id, "component.protected_update", "acme-api").allowed
    d = az.authorize(security_conn, bot.id, "component.protected_update", "acme-api")
    assert d.reason == az.HUMAN_REQUIRED
    assert az.authorize(security_conn, bot.id, "component.update", "acme-api").allowed


def test_the_repo_arm_never_allows_by_default(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"])
    pr.set_authority(security_conn, "acme-api", "repo-write")
    d = az.authorize(security_conn, p.id, "write", "acme-api")
    assert not d and d.reason == az.NO_GRANT


def test_authority_grants_only_and_repo_write_only(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"], grants=["acme-api"])
    pr.set_authority(security_conn, "acme-api", "repo-write")
    assert not az.authorize(security_conn, p.id, "write", "acme-api")  # grants are ignored
    pr.set_authority(security_conn, "acme-api", "grants")
    assert az.authorize(security_conn, p.id, "write", "acme-api").via == "grant"


def test_a_repo_authority_is_asked_only_when_the_authority_allows(security_conn):
    class Yes(az.RepoAuthority):
        def allows(self, principal, capability, scope):
            return True
    p = _mk(security_conn, "c", roles=["contributor"])
    assert az.authorize(security_conn, p.id, "write", "acme-api", repo_authority=Yes()).via == "repo-write"
    pr.set_authority(security_conn, "acme-api", "grants")
    assert not az.authorize(security_conn, p.id, "write", "acme-api", repo_authority=Yes())
    pr.set_authority(security_conn, "acme-api", "repo-write")
    assert az.authorize(security_conn, p.id, "write", "acme-api", repo_authority=Yes()).allowed


def test_unknown_capability_and_unknown_principal_are_refused(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"])
    assert az.authorize(security_conn, p.id, "delete.everything", "x").reason == az.UNKNOWN_CAPABILITY
    assert az.authorize(security_conn, "p_missing", "read").reason == az.NO_PRINCIPAL
    assert az.authorize(security_conn, "c", "read").reason == az.NO_PRINCIPAL  # a name is not an id


def test_disabled_principal_is_refused_on_the_next_call(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"], grants=["acme-api"])
    assert az.authorize(security_conn, p.id, "write", "acme-api").allowed
    pr.disable_principal(security_conn, p.id)
    assert az.authorize(security_conn, p.id, "write", "acme-api").reason == az.PRINCIPAL_INACTIVE
    pr.enable_principal(security_conn, p.id)
    assert az.authorize(security_conn, p.id, "write", "acme-api").allowed


def test_credential_must_be_valid_when_given(security_conn):
    p = _mk(security_conn, "c", roles=["reader"])
    other = _mk(security_conn, "o", roles=["reader"])
    good = tokens.issue_credential(security_conn, p.id)
    expired = tokens.issue_credential(security_conn, p.id, expires_at="2000-01-01T00:00:00Z")
    foreign = tokens.issue_credential(security_conn, other.id)
    assert az.authorize(security_conn, p.id, "read", credential_id=good.credential_id).allowed
    assert az.authorize(security_conn, p.id, "read", credential_id=expired.credential_id).reason == az.CREDENTIAL_INVALID
    assert az.authorize(security_conn, p.id, "read", credential_id=foreign.credential_id).reason == az.CREDENTIAL_INVALID
    assert az.authorize(security_conn, p.id, "read", credential_id="nope").reason == az.CREDENTIAL_INVALID


def test_a_revocation_committed_by_one_connection_is_seen_by_the_next_call(tmp_path, security_conn):
    p = _mk(security_conn, "c", roles=["contributor"], grants=["acme-api"])
    issued = tokens.issue_credential(security_conn, p.id)
    reader = open_store(tmp_path / "security-data", wiki_root=tmp_path / "wiki-root")
    assert az.authorize(reader, p.id, "write", "acme-api", credential_id=issued.credential_id).allowed
    tokens.revoke_credential(security_conn, issued.credential_id)  # different connection
    d = az.authorize(reader, p.id, "write", "acme-api", credential_id=issued.credential_id)
    assert not d and d.reason == az.CREDENTIAL_INVALID
    # grant removal and deny are also seen with no restart or cache flush
    other = tokens.issue_credential(security_conn, p.id)
    assert az.authorize(reader, p.id, "write", "acme-api", credential_id=other.credential_id).allowed
    pr.remove_grant(security_conn, p.id, "acme-api")
    assert not az.authorize(reader, p.id, "write", "acme-api", credential_id=other.credential_id)
    pr.add_grant(security_conn, p.id, "acme-api")
    pr.add_deny(security_conn, p.id, "acme-api")
    assert az.authorize(reader, p.id, "write", "acme-api").reason == az.DENIED
    reader.close()


def test_refusals_are_audited_and_allows_are_not(security_conn):
    p = _mk(security_conn, "c", roles=["contributor"], grants=["acme-api"])
    az.authorize(security_conn, p.id, "write", "acme-api")
    az.authorize(security_conn, p.id, "write", "acme.io")
    az.authorize(security_conn, p.id, "write", "acme.io", record_refusal=False)
    rows = audit.show(security_conn, event=audit.AUTHORIZER_REFUSAL)
    assert len(rows) == 1
    assert (rows[0].actor, rows[0].subject, rows[0].detail) == (p.id, "acme.io", "write: no_grant")


def test_decision_is_truthy_only_when_allowed():
    assert az.allow("role") and not az.refuse("x")
