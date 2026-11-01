# SPDX-License-Identifier: Apache-2.0
"""admin principal / credential / role (PHASE_1_PLAN T23)."""

import getpass
import json
import os
import stat

import pytest

from manifold_security import authorizer, principals, tokens


def secret_in(text):
    for word in text.split():
        if word.startswith("mf_"):
            return word
    return None


def issue_to_file(cli, tmp_path, principal="alice", name="secret.txt", *extra):
    path = tmp_path / name
    code, out, err = cli("credential", "issue", principal, "--secret-file", str(path), *extra)
    assert code == 0, err
    return path.read_text().strip(), out


@pytest.fixture()
def alice(cli):
    assert cli("principal", "create", "alice")[0] == 0
    assert cli("role", "set", "alice", "contributor")[0] == 0


def test_create_list_and_show(cli, alice):
    cli("principal", "create", "build-bot", "--kind", "agent")
    code, out, _ = cli("principal", "list")
    assert code == 0 and "alice" in out and "build-bot" in out and "agent" in out
    code, out, _ = cli("principal", "show", "alice")
    assert "roles:   contributor" in out and "credentials: none" in out


def test_a_duplicate_name_is_refused(cli, alice):
    code, _, err = cli("principal", "create", "alice")
    assert code == 1 and err.startswith("error:")


def test_issue_shows_the_secret_once_on_a_terminal_and_show_never_does(cli, alice):
    code, out, _ = cli("credential", "issue", "alice", "--label", "laptop", tty=True)
    token = secret_in(out)
    assert code == 0 and token and out.count(token) == 1
    for args in (("principal", "show", "alice"), ("principal", "list"), ("audit", "show")):
        shown = cli(*args)[1]
        assert token not in shown and token.split("_")[-1] not in shown
    conn = cli.store()
    assert tokens.verify(conn, token).ok
    conn.close()


def test_issue_without_a_terminal_or_a_file_is_refused_and_issues_nothing(cli, alice):
    code, out, err = cli("credential", "issue", "alice")
    assert code == 1 and "--secret-file" in err and secret_in(out + err) is None
    conn = cli.store()
    assert conn.execute("SELECT COUNT(*) FROM credentials").fetchone()[0] == 0
    conn.close()


def test_issue_to_a_file_makes_it_private_and_prints_no_secret(cli, alice, tmp_path):
    token, out = issue_to_file(cli, tmp_path)
    assert token.startswith("mf_") and token not in out
    assert stat.S_IMODE(os.stat(tmp_path / "secret.txt").st_mode) == 0o600
    code, _, err = cli("credential", "issue", "alice", "--secret-file", str(tmp_path / "secret.txt"))
    assert code == 1 and "already exists" in err  # never overwrites


def test_the_secret_never_reaches_the_audit_or_the_database(cli, alice, tmp_path):
    token, _ = issue_to_file(cli, tmp_path)
    secret = token.split("_", 2)[2]
    conn = cli.store()
    dump = json.dumps([dict(r) for r in conn.execute("SELECT * FROM audit")])
    conn.close()
    assert secret not in dump
    assert secret not in (cli.data_dir / "manifold.db").read_bytes().decode("latin-1")


def test_no_expiry_by_default_and_an_expiry_can_be_set_per_credential(cli, alice, tmp_path):
    issue_to_file(cli, tmp_path, "alice", "a.txt")
    issue_to_file(cli, tmp_path, "alice", "b.txt", "--expires", "30d")
    conn = cli.store()
    rows = conn.execute("SELECT expires_at FROM credentials ORDER BY created_at, credential_id").fetchall()
    conn.close()
    assert sorted(r["expires_at"] is None for r in rows) == [False, True]
    code, _, err = cli("credential", "issue", "alice", "--secret-file", str(tmp_path / "c.txt"), "--expires", "2001-01-01")
    assert code == 1 and "in the past" in err
    code, _, err = cli("credential", "issue", "alice", "--secret-file", str(tmp_path / "d.txt"), "--expires", "soon")
    assert code == 1 and "not a time" in err


def test_revoke_affects_only_that_credential_and_says_which_lever_was_used(cli, alice, tmp_path):
    first, _ = issue_to_file(cli, tmp_path, "alice", "a.txt")
    second, _ = issue_to_file(cli, tmp_path, "alice", "b.txt")
    conn = cli.store()
    first_id = tokens.parse(first)[0]
    code, out, _ = cli("credential", "revoke", first_id)
    assert code == 0 and "Lever used: credential revoked" in out
    assert "still has 1 working credential" in out and "principal disable alice" in out
    assert tokens.verify(conn, first).status == tokens.REVOKED
    assert tokens.verify(conn, second).ok
    assert cli("credential", "revoke", first_id)[0] == 1  # already revoked
    conn.close()


def test_disable_says_which_lever_and_refuses_every_credential_of_the_principal(cli, alice, tmp_path):
    token, _ = issue_to_file(cli, tmp_path)
    code, out, _ = cli("principal", "disable", "alice")
    assert code == 0 and "Lever used: principal disabled" in out and "1 working credential" in out
    conn = cli.store()
    principal = principals.get_principal(conn, "alice")
    decision = authorizer.authorize(conn, principal.id, "read", credential_id=tokens.parse(token)[0])
    assert not decision and decision.reason == authorizer.PRINCIPAL_INACTIVE
    cli("principal", "enable", "alice")
    assert authorizer.authorize(conn, principal.id, "read", credential_id=tokens.parse(token)[0])
    conn.close()


def test_rotate_replaces_a_credential(cli, alice, tmp_path):
    old, _ = issue_to_file(cli, tmp_path, "alice", "old.txt")
    old_id = tokens.parse(old)[0]
    new_path = tmp_path / "new.txt"
    code, out, _ = cli("credential", "rotate", old_id, "--secret-file", str(new_path))
    assert code == 0 and old_id in out
    new = new_path.read_text().strip()
    conn = cli.store()
    assert tokens.verify(conn, old).status == tokens.REVOKED and tokens.verify(conn, new).ok
    assert cli("credential", "rotate", old_id, "--secret-file", str(tmp_path / "x.txt"))[0] == 1
    conn.close()


def test_roles_are_set_and_unset_and_admin_is_refused_for_an_agent(cli, alice):
    assert cli("role", "set", "alice", "admin")[0] == 0
    cli("principal", "create", "bot", "--kind", "agent")
    code, _, err = cli("role", "set", "bot", "admin")
    assert code == 1 and "admin" in err
    code, out, _ = cli("role", "unset", "alice", "admin")
    assert code == 0 and "contributor" in out
    assert cli("role", "unset", "alice", "admin")[0] == 1


def test_every_action_is_audited_with_the_host_user_as_actor(cli, alice, tmp_path):
    issue_to_file(cli, tmp_path)
    cli("principal", "disable", "alice")
    conn = cli.store()
    rows = [dict(r) for r in conn.execute("SELECT * FROM audit")]
    conn.close()
    events = {r["event"] for r in rows}
    assert {"principal.changed", "role.changed", "credential.issued"} <= events
    assert {r["actor"] for r in rows} == {"host:%s" % getpass.getuser()}
