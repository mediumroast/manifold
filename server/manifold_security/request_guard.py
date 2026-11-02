# SPDX-License-Identifier: Apache-2.0
"""The Host and Origin guard: a request for the wrong host or from a foreign web page is refused.

This runs before authentication.  A browser on another site can be tricked into sending a
request to a server on the reader's own network (DNS rebinding, or a form post); the two
checks below stop that without asking for a credential.

* ``Host`` must be one of the served addresses: ``127.0.0.1``, ``localhost`` and ``[::1]`` with
  the served port, plus the entries of the ``allowed_hosts`` setting (an entry without a port
  also matches with the served port).  Refused with ``421`` and no detail.
  ``/health`` accepts a loopback name on any port, so the container health probe keeps working.
* A request that changes things (``POST``, ``PUT``, ``PATCH``, ``DELETE``) and carries an
  ``Origin`` header must name a served origin (``http`` or ``https`` plus an allowed host) or an
  entry of ``allowed_origins``.  Refused with ``403`` and no detail.  A request with no
  ``Origin`` (an MCP client, a script) passes this check.

Standard library only; the settings come from a callable so the package does not depend on
how the server reads them.  They are read on every request, so a change applies at once.
"""

from typing import Callable, Iterable, List, Sequence, Tuple

DEFAULT_HOSTS = ("127.0.0.1", "localhost", "[::1]")
MUTATING_METHODS = ("POST", "PUT", "PATCH", "DELETE")
DEFAULT_PORT = 8686


def _has_port(entry: str) -> bool:
    if entry.startswith("["):
        return entry.rfind("]:") != -1
    return ":" in entry


def allowed_host_values(port: int, extra: Iterable[str] = ()) -> List[str]:
    """Every Host header value accepted, lowercase."""
    values = ["%s:%d" % (name, port) for name in DEFAULT_HOSTS]
    for entry in extra:
        entry = entry.strip().lower()
        if not entry:
            continue
        values.append(entry)
        if not _has_port(entry):
            values.append("%s:%d" % (entry, port))
    return values


def allowed_origin_values(hosts: Sequence[str], extra: Iterable[str] = ()) -> List[str]:
    """Every Origin accepted: the served origins (both schemes, every allowed host) and the configured ones."""
    values = []
    for host in hosts:
        values += ["http://" + host, "https://" + host]
    values += [entry.strip().lower() for entry in extra if entry.strip()]
    return values


def _is_loopback_host(value: str) -> bool:
    name = value.rsplit(":", 1)[0] if _has_port(value) else value
    return name in DEFAULT_HOSTS


def _header(scope, name: bytes):
    for key, value in scope.get("headers", []):
        if key == name:
            return value.decode("latin-1")
    return None


async def _refuse(send, status: int) -> None:
    await send({"type": "http.response.start", "status": status,
                "headers": [(b"content-length", b"0")]})
    await send({"type": "http.response.body", "body": b""})


class RequestGuardMiddleware:
    """Pure ASGI middleware.  ``settings`` returns ``(allowed_hosts, allowed_origins)``; ``port`` is the served port."""

    def __init__(self, app, settings: Callable[[], Tuple[Sequence[str], Sequence[str]]],
                 port: int = DEFAULT_PORT, open_paths: Sequence[str] = ("/health",)):
        self.app = app
        self.settings = settings
        self.port = port
        self.open_paths = tuple(open_paths)

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        try:
            extra_hosts, extra_origins = self.settings()
        except Exception:  # an unreadable store must not open the guard: fall back to the defaults
            extra_hosts, extra_origins = (), ()
        hosts = allowed_host_values(self.port, extra_hosts)
        host = (_header(scope, b"host") or "").strip().lower()
        if host not in hosts and not (scope.get("path") in self.open_paths and _is_loopback_host(host)):
            await self._deny(scope, send, 421)
            return
        if scope["type"] == "http" and scope.get("method", "GET").upper() in MUTATING_METHODS:
            origin = _header(scope, b"origin")
            if origin is not None and origin.strip().lower().rstrip("/") not in allowed_origin_values(
                    hosts, extra_origins):
                await self._deny(scope, send, 403)
                return
        await self.app(scope, receive, send)

    @staticmethod
    async def _deny(scope, send, status):
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
        else:
            await _refuse(send, status)
