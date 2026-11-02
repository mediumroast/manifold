# SPDX-License-Identifier: Apache-2.0
"""The audit: synchronous writes, filters, and no credential ever stored."""

from manifold_security import audit, tokens
from manifold_security import principals as pr


def test_record_is_committed_on_return(tmp_path, security_conn):
    from manifold_security.store import open_store
    row_id = audit.record(security_conn, audit.ROLE_CHANGED, "host:mihay42", "alice", "added contributor")
    assert not security_conn.in_transaction
    other = open_store(tmp_path / "security-data", wiki_root=tmp_path / "wiki-root")
    rows = audit.show(other)
    other.close()
    assert [(r.id, r.event, r.actor, r.subject, r.detail) for r in rows] == [
        (row_id, "role.changed", "host:mihay42", "alice", "added contributor")]


def test_host_actor_form():
    assert audit.host_actor("mihay42") == "host:mihay42"


def test_failed_signin_records_address_and_generic_reason(security_conn):
    audit.record_failed_signin(security_conn, "203.0.113.9")
    [row] = audit.show(security_conn, event=audit.SIGNIN_FAILED)
    assert row.subject == "203.0.113.9" and row.detail == audit.GENERIC_FAILURE and row.actor == "anonymous"


def test_a_presented_credential_never_appears_in_any_audit_row(security_conn):
    p = pr.create_principal(security_conn, "alice", "human")
    issued = tokens.issue_credential(security_conn, p.id)
    guess = "mf_%s_%s" % (issued.credential_id, "Zx9-guess_secretvalue")
    # Even if a caller carelessly passes a credential into free text, it is redacted.
    for text in (issued.token, guess, "Authorization: Bearer %s" % issued.token):
        audit.record(security_conn, audit.AUTHORIZER_REFUSAL, text, text, text)
    audit.record(security_conn, audit.CREDENTIAL_ISSUED, "host:me", p.id, {"credential_id": issued.credential_id,
                                                                            "echo": issued.token})
    dump = "\n".join(
        "|".join(str(v) for v in tuple(r)) for r in security_conn.execute("SELECT * FROM audit"))
    assert issued.secret not in dump and "Zx9-guess_secretvalue" not in dump
    assert issued.credential_id in dump  # the id (not a secret) may be recorded
    assert "mf_<redacted>" in dump


def test_filters(security_conn):
    audit.record(security_conn, audit.CREDENTIAL_ISSUED, "host:me", "alice")
    audit.record(security_conn, audit.CREDENTIAL_REVOKED, "host:me", "alice")
    audit.record(security_conn, audit.ROLE_CHANGED, "host:me", "bob")
    audit.record(security_conn, audit.AUTHORIZER_REFUSAL, "bob", "acme-api", "write")
    assert [r.event for r in audit.show(security_conn, principal="alice")] == [
        "credential.revoked", "credential.issued"]
    assert {r.event for r in audit.show(security_conn, principal="bob")} == {"role.changed", "authorizer.refusal"}
    assert [r.event for r in audit.show(security_conn, event="credential.")] == [
        "credential.revoked", "credential.issued"]
    assert [r.event for r in audit.show(security_conn, event="role.changed")] == ["role.changed"]
    assert audit.show(security_conn, since="2999-01-01T00:00:00Z") == []
    assert len(audit.show(security_conn, limit=2)) == 2


def test_event_prefix_filter_escapes_like_wildcards(security_conn):
    audit.record(security_conn, "xcredential.issued", "a")
    assert audit.show(security_conn, event="_redential.") == []
