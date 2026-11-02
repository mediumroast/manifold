# SPDX-License-Identifier: Apache-2.0
"""A per-address delay for repeated bad credentials.  A credential is never locked.

Failed sign-ins are counted per client address, in memory.  Once an address reaches
``throttle_failure_threshold`` failures within ``throttle_window_seconds`` it is refused
(429 with ``Retry-After``) for ``throttle_base_delay_seconds``; each further failure after a
delay ends doubles the next delay, up to ``throttle_max_delay_seconds``.  While a delay runs the
credential is not checked at all, so the delay cannot be used to test guesses.  An address that
stays quiet for a whole window starts again from nothing, and so does one that signs in
successfully.  Another address is not affected.

The address is the socket peer.  ``X-Forwarded-For`` is read (its last entry) only when the peer
is in ``trusted_proxies``, which holds the Caddy service in the container setup.
Standard library only.
"""

import ipaddress
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence


@dataclass
class _State:
    failures: List[float] = field(default_factory=list)
    level: int = 0           # how many delays this address has been given in a row
    blocked_until: float = 0.0
    last_failure: float = 0.0


MAX_ADDRESSES = 10000  # how many addresses are remembered; beyond this the quietest are dropped


def _cap(table: dict, limit: int, quietness, keep: Optional[str] = None,
         protected: Optional[Callable[[object], bool]] = None) -> None:
    """
    Keep ``table`` within ``limit`` entries by dropping the quietest (oldest) 10% when it is exceeded.

    Entries for which ``protected`` is true go last: they are dropped (quietest first) only when the
    others are not enough to reach the target.
    """
    if len(table) <= limit:
        return
    drop = len(table) - int(limit * 0.9)
    candidates = sorted((k for k in table if k != keep), key=lambda k: quietness(table[k]))
    if protected is not None:
        candidates = ([k for k in candidates if not protected(table[k])]
                      + [k for k in candidates if protected(table[k])])
    for key in candidates[:drop]:
        del table[key]


def client_address(peer: Optional[str], forwarded_for: Optional[str], trusted_proxies: Sequence[str]) -> str:
    """The address to count: the peer, or the last X-Forwarded-For entry when the peer is a trusted proxy."""
    peer = peer or "unknown"
    if forwarded_for and _trusted(peer, trusted_proxies):
        last = forwarded_for.split(",")[-1].strip()
        try:
            ipaddress.ip_address(last)
            return last
        except ValueError:
            return peer  # a forwarded value that is not an address is ignored
    return peer


def _trusted(peer: str, trusted_proxies: Sequence[str]) -> bool:
    try:
        address = ipaddress.ip_address(peer)
    except ValueError:
        return False
    for entry in trusted_proxies:
        try:
            if address in ipaddress.ip_network(entry, strict=False):
                return True
        except ValueError:
            continue
    return False


class Throttle:
    """``limits()`` returns ``(threshold, window, base_delay, max_delay)``, read on every call."""

    def __init__(self, limits: Callable[[], Sequence[int]], clock: Callable[[], float] = time.monotonic,
                 max_addresses: int = MAX_ADDRESSES):
        self._limits = limits
        self._clock = clock
        self._max_addresses = max_addresses
        self._state: Dict[str, _State] = {}
        self._refusals: Dict[str, List[float]] = {}  # address -> [time of the last audited refusal, repeats since]

    def should_audit_refusal(self, address: str) -> Optional[int]:
        """
        Whether this throttled refusal gets an audit row of its own.

        Returns None for a repeat inside the window of the last audited refusal (it is only counted);
        otherwise the number of repeats suppressed since the previous audited refusal (0 the first time).
        """
        _, window, _, _ = self._limits()
        now = self._clock()
        entry = self._refusals.get(address)
        if entry is not None and now - entry[0] <= window:
            entry[1] += 1
            return None
        suppressed = int(entry[1]) if entry is not None else 0
        self._refusals[address] = [now, 0]
        _cap(self._refusals, self._max_addresses, lambda e: e[0])
        return suppressed

    def retry_after(self, address: str) -> int:
        """Whole seconds the address must still wait (0 when it may try)."""
        state = self._state.get(address)
        if state is None:
            return 0
        now = self._clock()
        _, window, _, _ = self._limits()
        if now - state.last_failure > window and now >= state.blocked_until:
            del self._state[address]
            return 0
        remaining = state.blocked_until - now
        return int(remaining) + 1 if remaining > 0 else 0

    def record_failure(self, address: str) -> int:
        """Count a failed sign-in; returns the delay now imposed (0 if none)."""
        threshold, window, base, maximum = self._limits()
        now = self._clock()
        state = self._state.get(address)
        if state is None:
            state = self._state[address] = _State()
            _cap(self._state, self._max_addresses, lambda s: s.last_failure or now, keep=address,
                 protected=lambda s: s.blocked_until > now)
        if now - state.last_failure > window and now >= state.blocked_until:
            state = self._state[address] = _State()  # a whole quiet window: start from nothing
        state.failures = [t for t in state.failures if now - t <= window] + [now]
        state.last_failure = now
        if len(state.failures) >= threshold:
            state.level += 1
            delay = min(base * 2 ** (state.level - 1), maximum)
            state.blocked_until = now + delay
            return delay
        return 0

    def record_success(self, address: str) -> None:
        self._state.pop(address, None)
