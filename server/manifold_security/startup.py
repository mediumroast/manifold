# SPDX-License-Identifier: Apache-2.0
"""Startup rules for the server (INT-1 S6, S8, S13).

* There is no setting, flag or environment variable that turns authentication off.
* With no principal in the store the server still starts (so the first administrator can be
  created), warns, and refuses every request until ``./manifold init`` has run.  On an address
  other than loopback it refuses to start at all.
* ``MANIFOLD_TOKEN`` and ``MANIFOLD_TOKEN_FILE`` are no longer accepted; if either is set the
  server says so and names the host command that creates the first administrator.

Standard library only.
"""

import ipaddress
import sqlite3
from dataclasses import dataclass, field
from typing import List, Mapping, Optional

from . import audit, principals

INIT_COMMAND = "./manifold init"
LEGACY_VARIABLES = ("MANIFOLD_TOKEN", "MANIFOLD_TOKEN_FILE")


class StartupError(Exception):
    """The server must not start.  The message says how to fix it."""


@dataclass
class StartupReport:
    notices: List[str] = field(default_factory=list)


def is_loopback(host: str) -> bool:
    """True for ``localhost`` and loopback addresses; anything else is reachable from elsewhere."""
    host = (host or "").strip().strip("[]")
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def check_startup(conn: sqlite3.Connection, host: Optional[str], environ: Mapping[str, str],
                  record: bool = True) -> StartupReport:
    """
    Apply the startup rules.  ``host`` is ``MANIFOLD_HOST`` (None when the server is started by
    another launcher, which cannot be checked).  Raises :class:`StartupError` to stop the start;
    otherwise returns the notices to log, and writes each to the audit unless ``record`` is false.
    """
    report = StartupReport()
    if principals.count_principals(conn) == 0:
        if host is not None and not is_loopback(host):
            raise StartupError(
                "Refusing to listen on %r: no principal exists yet, so no one could sign in. "
                "Run %s on this host first, or listen on 127.0.0.1." % (host, INIT_COMMAND))
        report.notices.append(
            "No principals exist: the server refuses every request until the first administrator is "
            "created. Run %s." % INIT_COMMAND)
    legacy = [name for name in LEGACY_VARIABLES if (environ.get(name) or "").strip()]
    if legacy:
        report.notices.append(
            "%s is set but is no longer accepted: the shared token was replaced by credentials issued to "
            "individual principals. Create the first administrator with %s, then remove the variable."
            % (" and ".join(legacy), INIT_COMMAND))
    if record:
        for notice in report.notices:
            audit.record(conn, audit.STARTUP_NOTICE, "server", "", notice)
    return report
