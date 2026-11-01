# SPDX-License-Identifier: Apache-2.0
"""The per-address delay for repeated bad credentials (PHASE_1_PLAN T20)."""

import asyncio
import json

import pytest

from manifold_security import audit
from manifold_security.throttle import Throttle, client_address
from wiki_backend.auth import PrincipalAuthMiddleware, StoreAccess


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def make_throttle(clock, limits=(5, 600, 1, 900)):
    return Throttle(lambda: limits, clock)


# ── the counting ─────────────────────────────────────────────────────────────

def test_no_delay_until_the_threshold_then_the_delay_doubles_up_to_the_maximum():
    clock = Clock()
    throttle = make_throttle(clock, (3, 600, 1, 8))
    delays = []
    for _ in range(3):
        delays.append(throttle.record_failure("a"))
    assert delays == [0, 0, 1] and throttle.retry_after("a") >= 1
    for expected in (2, 4, 8, 8):
        clock.now += throttle.retry_after("a") + 1  # wait the delay out, then fail again
        assert throttle.record_failure("a") == expected


def test_a_delay_ends_and_a_quiet_window_starts_over():
    clock = Clock()
    throttle = make_throttle(clock, (2, 600, 5, 900))
    throttle.record_failure("a")
    assert throttle.record_failure("a") == 5
    clock.now += 6
    assert throttle.retry_after("a") == 0
    clock.now += 601  # a whole quiet window
    assert throttle.record_failure("a") == 0  # counted from nothing, below the threshold
    assert throttle.record_failure("a") == 5  # and the delay starts from the base again


def test_other_addresses_are_not_affected_and_a_success_clears_the_address():
    clock = Clock()
    throttle = make_throttle(clock, (1, 600, 30, 900))
    throttle.record_failure("a")
    assert throttle.retry_after("a") > 0 and throttle.retry_after("b") == 0
    throttle.record_success("a")
    assert throttle.retry_after("a") == 0


def test_the_limits_are_read_each_time():
    limits = [(5, 600, 1, 900)]
    clock = Clock()
    throttle = Throttle(lambda: limits[0], clock)
    for _ in range(2):
        throttle.record_failure("a")
    limits[0] = (3, 600, 1, 900)
    assert throttle.record_failure("a") == 1


# ── which address ────────────────────────────────────────────────────────────

def test_the_socket_peer_is_the_address_unless_it_is_a_trusted_proxy():
    assert client_address("10.0.0.9", "6.6.6.6", []) == "10.0.0.9"  # spoofed header from an untrusted peer: ignored
    assert client_address("10.0.0.9", "6.6.6.6", ["10.0.0.0/24"]) == "6.6.6.6"
    assert client_address("10.0.0.9", "1.1.1.1, 2.2.2.2", ["10.0.0.9"]) == "2.2.2.2"  # the last entry
    assert client_address("10.0.0.9", "not-an-address", ["10.0.0.9"]) == "10.0.0.9"
    assert client_address(None, "6.6.6.6", ["10.0.0.9"]) == "unknown"


# ── in the middleware ────────────────────────────────────────────────────────

def call(world, middleware, path="/mcp", token=None, client="203.0.113.7", forwarded=None):
    seen = {"reached": False, "messages": []}

    async def app(scope, receive, send):
        seen["reached"] = True
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    async def send(message):
        seen["messages"].append(message)

    headers = []
    if token is not None:
        headers.append((b"authorization", ("Bearer " + token).encode()))
    if forwarded:
        headers.append((b"x-forwarded-for", forwarded.encode()))
    scope = {"type": "http", "path": path, "method": "GET", "headers": headers, "client": (client, 5555)}
    asyncio.run(middleware(scope, None, send))
    start = next(m for m in seen["messages"] if m["type"] == "http.response.start")
    return start["status"], dict(start["headers"]), seen["reached"]


@pytest.fixture()
def guarded(auth_world):
    clock = Clock()
    throttle = make_throttle(clock, (3, 600, 10, 900))
    proxies = []

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = PrincipalAuthMiddleware(app, store=StoreAccess(auth_world.data_dir), throttle=throttle,
                                         trusted_proxies=lambda: proxies)
    return auth_world, middleware, clock, proxies


def test_after_the_threshold_even_the_right_credential_is_refused_with_429_and_retry_after(guarded):
    world, middleware, clock, _ = guarded
    for _ in range(3):
        assert call(world, middleware, token="mf_000000000000_" + "a" * 43)[0] == 401
    status, headers, reached = call(world, middleware, token=world.human_token)
    assert (status, reached) == (429, False)
    assert int(headers[b"retry-after"]) >= 1
    clock.now += 11
    assert call(world, middleware, token=world.human_token)[0] == 200  # the delay ended


def test_the_credential_is_not_checked_while_the_delay_runs(guarded):
    world, middleware, clock, _ = guarded
    for _ in range(3):
        call(world, middleware, token="mf_000000000000_" + "a" * 43)
    before = world.conn.execute("SELECT COUNT(*) FROM audit WHERE event = 'signin.failed'").fetchone()[0]
    for _ in range(4):
        assert call(world, middleware, token="mf_000000000000_" + "b" * 43)[0] == 429
    after = world.conn.execute("SELECT COUNT(*) FROM audit WHERE event = 'signin.failed'").fetchone()[0]
    assert after == before  # guesses during the delay are not even counted as sign-in attempts


def test_a_correct_credential_from_another_address_works_during_the_delay(guarded):
    world, middleware, _, _ = guarded
    for _ in range(3):
        call(world, middleware, token="mf_000000000000_" + "a" * 43, client="203.0.113.7")
    assert call(world, middleware, token=world.human_token, client="203.0.113.7")[0] == 429
    assert call(world, middleware, token=world.human_token, client="198.51.100.2")[0] == 200


def test_a_spoofed_forwarded_header_from_an_untrusted_peer_is_ignored(guarded):
    world, middleware, _, proxies = guarded
    for _ in range(3):  # the attacker tries to hide behind other addresses
        call(world, middleware, token="mf_000000000000_" + "a" * 43, client="203.0.113.7", forwarded="10.1.1.1")
    assert call(world, middleware, token=world.human_token, client="203.0.113.7", forwarded="10.9.9.9")[0] == 429
    proxies.append("203.0.113.7")  # now the peer is a trusted proxy: the forwarded address is the client
    assert call(world, middleware, token=world.human_token, client="203.0.113.7", forwarded="10.9.9.9")[0] == 200


def test_health_stays_reachable_but_a_guess_there_counts_and_gives_nothing_away(guarded):
    world, middleware, _, _ = guarded
    for _ in range(3):
        assert call(world, middleware, path="/health", token="mf_000000000000_" + "a" * 43)[0] == 200
    status, _, reached = call(world, middleware, path="/mcp", token=world.human_token)
    assert (status, reached) == (429, False)  # the guesses at /health counted against the address


def test_failures_and_throttled_refusals_are_audited_with_the_address_and_never_the_credential(guarded):
    world, middleware, _, _ = guarded
    guess = "mf_000000000000_" + "z" * 43
    for _ in range(3):
        call(world, middleware, token=guess)
    call(world, middleware, token=guess)  # throttled
    rows = [dict(r) for r in world.conn.execute("SELECT * FROM audit WHERE event LIKE 'signin.%'")]
    assert {r["event"] for r in rows} == {"signin.failed", "signin.throttled"}
    assert all(r["subject"] == "203.0.113.7" for r in rows)
    assert not any("zzzz" in json.dumps(r) or guess in json.dumps(r) for r in rows)


def test_a_missing_header_is_not_a_failed_sign_in(guarded):
    world, middleware, _, _ = guarded
    for _ in range(10):
        assert call(world, middleware)[0] == 401
    assert call(world, middleware, token=world.human_token)[0] == 200


def test_a_credential_is_never_locked(guarded):
    world, middleware, clock, _ = guarded
    for _ in range(5):
        call(world, middleware, token=world.human_token[:-1] + "x", client="203.0.113.7")
    clock.now += 2000
    assert call(world, middleware, token=world.human_token, client="198.51.100.2")[0] == 200
    assert call(world, middleware, token=world.human_token, client="203.0.113.7")[0] == 200
