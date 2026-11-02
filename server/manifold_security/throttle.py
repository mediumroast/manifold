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

    def __init__(self, limits: Callable[[], Sequence[int]], clock: Callable[[], float] = time.monotonic):
        self._limits = limits
        self._clock = clock
        self._state: Dict[str, _State] = {}

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
        state = self._state.setdefault(address, _State())
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
