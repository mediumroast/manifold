# SPDX-License-Identifier: Apache-2.0
"""The settings registry: every known setting with its type, bounds and default.

Values live in the ``settings`` table as text.  There is deliberately no
setting that turns authentication off.  Unknown keys and out-of-range values
are refused with a message that names the allowed range.
"""

import ipaddress
import sqlite3
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .store import now_iso, transaction


class SettingError(ValueError):
    """A setting key or value is not allowed.  The message says what is."""


@dataclass(frozen=True)
class Spec:
    kind: str  # "int", "choice" or "list"
    default: Any
    doc: str
    minimum: Optional[int] = None
    maximum: Optional[int] = None
    choices: Tuple[str, ...] = ()
    item: str = ""  # for lists: "host", "origin" or "network"


SPECS: Dict[str, Spec] = {
    "agent_registrations_per_day": Spec("int", 5, "Components an agent or service may register per UTC day.", 0, 1000),
    "agent_archives_per_day": Spec("int", 1, "Components an agent or service may archive per UTC day.", 0, 1000),
    "purge_hold_days": Spec("int", 14, "Days an archived component is held before it can be purged.", 0, 3650),
    "throttle_failure_threshold": Spec("int", 5, "Failed sign-ins per address within the window before delays start.", 1, 1000),
    "throttle_window_seconds": Spec("int", 600, "Length of the failed-sign-in window, in seconds.", 1, 86400),
    "throttle_base_delay_seconds": Spec("int", 1, "First delay once the threshold is reached, in seconds.", 1, 3600),
    "throttle_max_delay_seconds": Spec("int", 900, "Longest delay, in seconds; the delay doubles up to this.", 1, 86400),
    "allowed_hosts": Spec("list", [], "Extra Host header values accepted, comma separated (host or host:port).", item="host"),
    "allowed_origins": Spec("list", [], "Extra Origin values accepted, comma separated (scheme://host[:port]).", item="origin"),
    "trusted_proxies": Spec("list", [], "Addresses or networks whose X-Forwarded-For is trusted, comma separated.", item="network"),
    "tls": Spec("choice", "off", "Whether the server is served over TLS by the Caddy service.", choices=("off", "on")),
}


def _spec(key: str) -> Spec:
    try:
        return SPECS[key]
    except KeyError:
        raise SettingError("Unknown setting %r. Known settings: %s." % (key, ", ".join(sorted(SPECS)))) from None


def _list_item(spec: Spec, key: str, entry: str) -> str:
    if not entry or any(ch.isspace() for ch in entry):
        raise SettingError("%s: entries must be non-empty and contain no spaces (got %r)." % (key, entry))
    if spec.item == "origin":
        if not (entry.startswith("http://") or entry.startswith("https://")) or entry.endswith("/") \
                or entry.count("/") != 2:
            raise SettingError("%s: %r is not an origin; use scheme://host[:port] with no path." % (key, entry))
    elif spec.item == "network":
        try:
            ipaddress.ip_network(entry, strict=False)
        except ValueError:
            raise SettingError("%s: %r is not an IP address or network." % (key, entry)) from None
    elif "/" in entry or "://" in entry:
        raise SettingError("%s: %r is not a host; use host or host:port with no scheme or path." % (key, entry))
    return entry


def parse(key: str, raw: Any) -> Any:
    """Validate ``raw`` for ``key`` and return the typed value."""
    spec = _spec(key)
    if spec.kind == "int":
        try:
            if isinstance(raw, bool):
                raise ValueError
            value = int(str(raw).strip())
        except ValueError:
            raise SettingError("%s must be a whole number from %d to %d (got %r)." % (
                key, spec.minimum, spec.maximum, raw)) from None
        if not spec.minimum <= value <= spec.maximum:
            raise SettingError("%s must be from %d to %d (got %d)." % (key, spec.minimum, spec.maximum, value))
        return value
    if spec.kind == "choice":
        value = str(raw).strip().lower()
        if value not in spec.choices:
            raise SettingError("%s must be one of: %s (got %r)." % (key, ", ".join(spec.choices), raw))
        return value
    entries = raw if isinstance(raw, (list, tuple)) else str(raw).split(",")
    entries = [str(e).strip() for e in entries if str(e).strip()]
    return [_list_item(spec, key, e) for e in entries]


def _encode(value: Any) -> str:
    return ",".join(value) if isinstance(value, list) else str(value)


def get(conn: sqlite3.Connection, key: str) -> Any:
    """The current value (the stored one if set, otherwise the default).  Read on every call."""
    spec = _spec(key)
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if row is None:
        return list(spec.default) if isinstance(spec.default, list) else spec.default
    return parse(key, row["value"])


def get_all(conn: sqlite3.Connection) -> Dict[str, Any]:
    return {key: get(conn, key) for key in SPECS}


def set_value(conn: sqlite3.Connection, key: str, raw: Any) -> Any:
    """Validate and store a setting.  Returns the typed value."""
    value = parse(key, raw)
    with transaction(conn):
        pending = {k: get(conn, k) for k in ("throttle_base_delay_seconds", "throttle_max_delay_seconds")}
        pending[key] = value
        if pending["throttle_base_delay_seconds"] > pending["throttle_max_delay_seconds"]:
            raise SettingError(
                "throttle_base_delay_seconds (%d) must not exceed throttle_max_delay_seconds (%d)."
                % (pending["throttle_base_delay_seconds"], pending["throttle_max_delay_seconds"]))
        conn.execute(
            "INSERT INTO settings(key, value, updated_at) VALUES (?, ?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
            (key, _encode(value), now_iso()),
        )
    return value


def unset(conn: sqlite3.Connection, key: str) -> None:
    """Return a setting to its default."""
    _spec(key)
    with transaction(conn):
        conn.execute("DELETE FROM settings WHERE key = ?", (key,))
