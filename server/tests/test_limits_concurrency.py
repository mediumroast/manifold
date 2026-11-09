# SPDX-License-Identifier: Apache-2.0
"""Concurrent registrations cannot exceed the daily limit (PHASE_1_TEST_PLAN A9; INT-1 S11 Must never).

4 processes x 3 calls = 12 calls against a limit of 5; no randomness.  Each process opens its own
connection to the same temporary store and waits for a shared start time so the calls overlap.
"""

import multiprocessing
import time

from manifold_security import limits, principals, settings
from manifold_security.store import open_store

PROCESSES = 4
CALLS_EACH = 3
LIMIT = 5


def _worker(data_dir, wiki_root, principal_id, start_at, queue):
    """Own connection; wait for the start time; try CALLS_EACH registrations; report what happened."""
    conn = open_store(data_dir, wiki_root=wiki_root)
    outcomes = []
    time.sleep(max(0.0, start_at - time.time()))
    for _ in range(CALLS_EACH):
        try:
            limits.consume(conn, principal_id, "agent", limits.REGISTRATIONS)
            outcomes.append(("allowed", ""))
        except limits.LimitReached as exc:
            outcomes.append(("refused", str(exc)))
        except Exception as exc:  # a lock error or anything else is itself a finding
            outcomes.append(("error", "%s: %s" % (type(exc).__name__, exc)))
    conn.close()
    queue.put(outcomes)


def test_A9_concurrent_registrations_cannot_exceed_the_daily_limit(tmp_path):
    data_dir, wiki_root = tmp_path / "security-data", tmp_path / "wiki-root"
    conn = open_store(data_dir, wiki_root=wiki_root)
    agent = principals.create_principal(conn, "build-bot", "agent")
    settings.set_value(conn, "agent_registrations_per_day", LIMIT)

    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    start_at = time.time() + 3
    workers = [context.Process(target=_worker, args=(data_dir, wiki_root, agent.id, start_at, queue))
               for _ in range(PROCESSES)]
    for worker in workers:
        worker.start()
    outcomes = [item for _ in workers for item in queue.get(timeout=60)]
    for worker in workers:
        worker.join(timeout=30)

    assert len(outcomes) == PROCESSES * CALLS_EACH
    assert [o for o in outcomes if o[0] == "error"] == []
    assert sum(1 for o in outcomes if o[0] == "allowed") == LIMIT
    refused = [o for o in outcomes if o[0] == "refused"]
    assert len(refused) == PROCESSES * CALLS_EACH - LIMIT
    assert all("agent_registrations_per_day" in message for _, message in refused)
    assert limits.used_today(conn, agent.id, limits.REGISTRATIONS) == LIMIT
    conn.close()
