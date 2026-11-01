# SPDX-License-Identifier: Apache-2.0
"""Daily limits for agent and service principals (registrations and archives).

Counts live in the ``usage`` table, one row per principal, UTC day and counter.  The limit
for an ``agent`` or ``service`` principal is the setting ``agent_registrations_per_day`` or
``agent_archives_per_day``; a ``human`` principal is counted but never limited.

``consume`` checks the limit and counts the use in one ``BEGIN IMMEDIATE`` transaction, so
two concurrent calls cannot both take the last slot.  The registry operations themselves are
file changes and cannot join that transaction, so the caller consumes first and calls
``refund`` if the operation then did not happen.
"""

import datetime
import sqlite3
from typing import Optional

from . import audit, settings
from .store import transaction

REGISTRATIONS = "registrations"
ARCHIVES = "archives"
LIMITED_KINDS = ("agent", "service")
_SETTING = {REGISTRATIONS: "agent_registrations_per_day", ARCHIVES: "agent_archives_per_day"}
_WORDS = {REGISTRATIONS: "registrations", ARCHIVES: "archives"}


class LimitReached(Exception):
    """The principal used up its limit for today.  The message says which limit and when it resets."""


def _day(now: Optional[datetime.datetime] = None) -> str:
    return (now or datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%d")


def _resets_at(now: Optional[datetime.datetime] = None) -> str:
    now = now or datetime.datetime.now(datetime.timezone.utc)
    tomorrow = (now + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return tomorrow.strftime("%Y-%m-%d 00:00 UTC")


def used_today(conn: sqlite3.Connection, principal_id: str, counter: str,
               now: Optional[datetime.datetime] = None) -> int:
    row = conn.execute("SELECT count FROM usage WHERE principal_id = ? AND day = ? AND counter = ?",
                       (principal_id, _day(now), counter)).fetchone()
    return row["count"] if row else 0


def consume(conn: sqlite3.Connection, principal_id: str, kind: str, counter: str,
            now: Optional[datetime.datetime] = None) -> int:
    """
    Count one use of ``counter`` for today; raise :class:`LimitReached` if an agent or service is
    already at its limit (the refusal is audited).  Returns the count after this use.
    """
    if counter not in _SETTING:
        raise ValueError("unknown counter %r" % counter)
    limit = settings.get(conn, _SETTING[counter])
    day = _day(now)
    refused = None
    with transaction(conn):
        row = conn.execute("SELECT count FROM usage WHERE principal_id = ? AND day = ? AND counter = ?",
                           (principal_id, day, counter)).fetchone()
        current = row["count"] if row else 0
        if kind in LIMITED_KINDS and current >= limit:
            refused = current
        else:
            conn.execute(
                "INSERT INTO usage(principal_id, day, counter, count) VALUES (?, ?, ?, 1)"
                " ON CONFLICT(principal_id, day, counter) DO UPDATE SET count = count + 1",
                (principal_id, day, counter))
    if refused is not None:
        message = ("Limit reached: %s principals may make %d %s per day (setting %s); "
                   "the count resets at %s." % (kind, limit, _WORDS[counter], _SETTING[counter], _resets_at(now)))
        audit.record(conn, audit.AUTHORIZER_REFUSAL, principal_id, "", "limit %s: %s" % (counter, refused))
        raise LimitReached(message)
    return current + 1


def refund(conn: sqlite3.Connection, principal_id: str, counter: str,
           now: Optional[datetime.datetime] = None) -> None:
    """Give back one use (the operation that consumed it did not happen)."""
    with transaction(conn):
        conn.execute("UPDATE usage SET count = MAX(count - 1, 0) WHERE principal_id = ? AND day = ? AND counter = ?",
                     (principal_id, _day(now), counter))
