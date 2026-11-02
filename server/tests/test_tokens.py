# SPDX-License-Identifier: Apache-2.0
"""Credentials: format, hashing at rest, verification outcomes, secrecy."""

import pytest

from manifold_security import tokens
from manifold_security.store import open_store


def _principal(conn, pid="p1", name="alice"):
    conn.execute(
        "INSERT INTO principals(id, name, kind, created_at) VALUES (?, ?, 'human', 't')", (pid, name))
    return pid


def test_token_format_and_issue_fields(security_conn):
    pid = _principal(security_conn)
    issued = tokens.issue_credential(security_conn, pid, label="laptop")
    assert issued.token.startswith("mf_%s_" % issued.credential_id)
    assert issued.token == "mf_%s_%s" % (issued.credential_id, issued.secret)
    assert issued.expires_at is None  # no expiry by default (D9)
    assert issued.label == "laptop"


def test_stored_row_has_hash_only(security_conn):
    pid = _principal(security_conn)
    issued = tokens.issue_credential(security_conn, pid)
    row = security_conn.execute("SELECT * FROM credentials").fetchone()
    assert issued.secret not in tuple(str(v) for v in row)
    assert len(row["secret_hash"]) == 64


def test_database_file_bytes_do_not_contain_the_secret(tmp_path):
    conn = open_store(tmp_path / "d", wiki_root=tmp_path / "w", journal_mode="delete")
    pid = _principal(conn)
    issued = tokens.issue_credential(conn, pid)
    conn.close()
    data = (tmp_path / "d" / "manifold.db").read_bytes()
    assert issued.secret.encode() not in data
    assert issued.token.encode() not in data


def test_wal_files_do_not_contain_the_secret(tmp_path):
    conn = open_store(tmp_path / "d", wiki_root=tmp_path / "w")
    pid = _principal(conn)
    issued = tokens.issue_credential(conn, pid)
    blobs = b"".join(p.read_bytes() for p in (tmp_path / "d").iterdir())
    conn.close()
    assert issued.secret.encode() not in blobs


def test_repr_and_str_hide_the_secret(security_conn):
    pid = _principal(security_conn)
    issued = tokens.issue_credential(security_conn, pid)
    assert issued.secret not in repr(issued) and issued.secret not in str(issued)
    assert issued.token not in repr(issued)
    assert "<hidden>" in repr(issued)


def test_verify_valid(security_conn):
    pid = _principal(security_conn)
    issued = tokens.issue_credential(security_conn, pid)
    result = tokens.verify(security_conn, issued.token)
    assert result.status == tokens.VALID and result.ok
    assert result.principal_id == pid and result.credential_id == issued.credential_id


@pytest.mark.parametrize("bad", ["", "mf_", "mf_abc", "mf_abc_", "mf__x", "nope", "Bearer x", None, 5])
def test_verify_malformed_is_unknown(security_conn, bad):
    assert tokens.verify(security_conn, bad).status == tokens.UNKNOWN


def test_verify_wrong_secret_and_unknown_id(security_conn):
    pid = _principal(security_conn)
    issued = tokens.issue_credential(security_conn, pid)
    assert tokens.verify(security_conn, "mf_%s_wrong" % issued.credential_id).status == tokens.UNKNOWN
    assert tokens.verify(security_conn, "mf_000000000000_%s" % issued.secret).status == tokens.UNKNOWN


def test_secret_may_contain_underscores_and_dashes(security_conn):
    pid = _principal(security_conn)
    for _ in range(30):
        issued = tokens.issue_credential(security_conn, pid)
        assert tokens.verify(security_conn, issued.token).ok


def test_expired(security_conn):
    pid = _principal(security_conn)
    issued = tokens.issue_credential(security_conn, pid, expires_at="2030-01-01T00:00:00Z")
    assert tokens.verify(security_conn, issued.token, now="2029-12-31T23:59:59Z").status == tokens.VALID
    assert tokens.verify(security_conn, issued.token, now="2030-01-01T00:00:00Z").status == tokens.EXPIRED


def test_revoked_applies_to_that_credential_only(security_conn):
    pid = _principal(security_conn)
    first = tokens.issue_credential(security_conn, pid)
    second = tokens.issue_credential(security_conn, pid)
    assert tokens.revoke_credential(security_conn, first.credential_id) is True
    assert tokens.revoke_credential(security_conn, first.credential_id) is False
    assert tokens.verify(security_conn, first.token).status == tokens.REVOKED
    assert tokens.verify(security_conn, second.token).status == tokens.VALID


def test_revoked_is_not_revealed_without_the_secret(security_conn):
    pid = _principal(security_conn)
    issued = tokens.issue_credential(security_conn, pid)
    tokens.revoke_credential(security_conn, issued.credential_id)
    assert tokens.verify(security_conn, "mf_%s_guess" % issued.credential_id).status == tokens.UNKNOWN


def test_issue_for_missing_principal_is_refused(security_conn):
    with pytest.raises(ValueError, match="No principal"):
        tokens.issue_credential(security_conn, "ghost")
