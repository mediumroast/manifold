# SPDX-License-Identifier: Apache-2.0
"""The per-address delay for repeated bad credentials (PHASE_1_PLAN T20)."""

import asyncio
import gc
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


# ── T43: a flood of refused requests ─────────────────────────────────────────

# No randomness is used: the flood is FLOOD_REQUESTS identical requests from one address, with the
# limits below, so a run can be repeated exactly.
FLOOD_REQUESTS = 1000
FLOOD_LAG_BOUND_SECONDS = 0.05  # measured on macOS (Python 3.11), 5 runs: the loop's worst stall was 4.4 to 4.5 ms


def flood_world(auth_world):
    clock = Clock()
    throttle = make_throttle(clock, (3, 100, 1000, 1000))  # the delay (1000s) outlasts the window (100s)

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"ok"})

    middleware = PrincipalAuthMiddleware(app, store=StoreAccess(auth_world.data_dir), throttle=throttle,
                                         trusted_proxies=lambda: [])
    return middleware, clock


async def request_from(middleware, client, token):
    status = []

    async def send(message):
        await asyncio.sleep(0)  # let other tasks run, as a real connection would
        if message["type"] == "http.response.start":
            status.append(message["status"])

    scope = {"type": "http", "path": "/mcp", "method": "GET", "client": (client, 5555),
             "headers": [(b"authorization", ("Bearer " + token).encode())]}
    await middleware(scope, None, send)
    return status[0]


def test_flood_a_throttled_address_adds_one_audit_row_and_counts_the_rest(auth_world):
    middleware, clock = flood_world(auth_world)
    guess = "mf_000000000000_" + "a" * 43

    async def run():
        for _ in range(3):
            await request_from(middleware, "203.0.113.7", guess)
        return await asyncio.gather(*[request_from(middleware, "203.0.113.7", guess) for _ in range(FLOOD_REQUESTS)])

    assert set(asyncio.run(run())) == {429}
    rows = [dict(r) for r in auth_world.conn.execute("SELECT * FROM audit WHERE event = 'signin.throttled'")]
    assert len(rows) == 1

    clock.now += 150  # a whole window later the address is still throttled: the next row carries the count
    assert asyncio.run(request_from(middleware, "203.0.113.7", guess)) == 429
    rows = [dict(r) for r in auth_world.conn.execute("SELECT * FROM audit WHERE event = 'signin.throttled' ORDER BY id")]
    assert len(rows) == 2 and str(FLOOD_REQUESTS - 1) in rows[1]["detail"]
    assert guess not in json.dumps(rows)


def test_flood_does_not_stall_the_loop_for_other_addresses(auth_world):
    middleware, _ = flood_world(auth_world)
    guess = "mf_000000000000_" + "a" * 43

    async def run():
        for _ in range(3):
            await request_from(middleware, "203.0.113.7", guess)
        worst = 0.0
        running = True

        async def ticker():
            nonlocal worst
            last = asyncio.get_running_loop().time()
            while running:
                await asyncio.sleep(0.001)
                now = asyncio.get_running_loop().time()
                worst, last = max(worst, now - last), now

        watcher = asyncio.create_task(ticker())
        flood = [request_from(middleware, "203.0.113.7", guess) for _ in range(FLOOD_REQUESTS)]
        other = request_from(middleware, "198.51.100.2", auth_world.human_token)
        results = await asyncio.gather(*flood, other)
        running = False
        await watcher
        return results, worst

    # A collector pause stalls the whole process and has nothing to do with how the flood is handled. On CI one
    # generation-2 collection (68 ms with about 185,000 live objects, set off by the burst of FLOOD_REQUESTS
    # tasks) was the whole stall (PR #30). So collect now, keep the collector off for the measured window, and
    # put it back as it was.
    collector_was_on = gc.isenabled()
    gc.collect()
    gc.disable()
    try:
        results, worst = asyncio.run(run())
    finally:
        if collector_was_on:
            gc.enable()
    assert results[-1] == 200 and set(results[:-1]) == {429}
    assert worst < FLOOD_LAG_BOUND_SECONDS, "the event loop stalled for %.3fs during the flood" % worst


def test_the_state_is_capped_and_drops_the_quietest_address():
    clock = Clock()
    throttle = Throttle(lambda: (5, 600, 1, 900), clock, max_addresses=100)
    for i in range(500):
        clock.now += 1
        throttle.record_failure("10.0.%d.%d" % (i // 250, i % 250))
    assert len(throttle._state) <= 100
    assert "10.0.1.249" in throttle._state and "10.0.0.0" not in throttle._state


def test_a_blocked_address_is_kept_when_the_table_overflows():
    clock = Clock()
    throttle = Throttle(lambda: (5, 600, 100, 900), clock, max_addresses=5)
    for _ in range(5):
        clock.now += 1
        throttle.record_failure("blocked")
    assert throttle.retry_after("blocked") > 0
    for i in range(10):
        clock.now += 1
        throttle.record_failure("other-%d" % i)  # each fails once, later than "blocked"
    assert throttle.retry_after("blocked") > 0
    assert len(throttle._state) <= 5


def test_an_expired_block_is_dropped_before_one_still_running():
    clock = Clock()
    limits = [2, 600, 1000, 2000]  # threshold, window, base delay, max delay (read on every call)
    throttle = Throttle(lambda: tuple(limits), clock, max_addresses=5)
    for _ in range(2):
        throttle.record_failure("live")  # blocked for 1000 s, the quietest entry
    clock.now += 10
    limits[2] = 1
    for _ in range(2):
        throttle.record_failure("expired")  # blocked for 1 s
    clock.now += 10  # "expired" is past its delay but still inside the window
    assert throttle.retry_after("live") > 0
    for i in range(3):
        clock.now += 1
        throttle.record_failure("other-%d" % i)
    assert "expired" in throttle._state  # the table is full (5), not yet over
    clock.now += 1
    throttle.record_failure("other-3")  # overflow
    assert throttle.retry_after("live") > 0
    assert "expired" not in throttle._state
    assert len(throttle._state) <= 5


def test_the_bound_holds_when_every_entry_is_blocked():
    clock = Clock()
    throttle = Throttle(lambda: (1, 600, 1000, 2000), clock, max_addresses=5)
    for i in range(20):
        clock.now += 1
        throttle.record_failure("blocked-%d" % i)
        assert len(throttle._state) <= 5
    assert "blocked-19" in throttle._state


def test_a_credential_is_never_locked(guarded):
    world, middleware, clock, _ = guarded
    for _ in range(5):
        call(world, middleware, token=world.human_token[:-1] + "x", client="203.0.113.7")
    clock.now += 2000
    assert call(world, middleware, token=world.human_token, client="198.51.100.2")[0] == 200
    assert call(world, middleware, token=world.human_token, client="203.0.113.7")[0] == 200
