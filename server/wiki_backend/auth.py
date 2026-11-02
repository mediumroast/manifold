# SPDX-License-Identifier: Apache-2.0
"""Principal authentication for the HTTP surface.

Every request except ``GET /health`` must carry a credential issued to a principal
(``manifold admin credential issue``), as either

* ``Authorization: Bearer <credential>``, for agents and scripts; or
* ``Authorization: Basic <base64 user:password>`` with the credential as the password
  and any user name, so a browser can ask for it once and then send it with every
  request, including the static files the wiki browser loads.

The credential is checked against the security store on every request (no cache), so a
revocation or a disabled principal takes effect on the very next request, without a
restart.  A valid request gets a :class:`~manifold_security.context.Caller` in its ASGI
scope and in ``current_caller_var``.  There is no setting that turns this off; with no
principals in the store nothing can authenticate, so every request is refused.

Failures answer ``401`` with the same body whether the credential is missing, malformed,
unknown or wrong, so a guess learns nothing.  Only a holder of a complete, correct
secret that was revoked or has expired (or whose principal was disabled) is told
"your access was removed or has expired".  If the store cannot be opened the answer is
``503``: authentication fails closed.
"""

import base64
import binascii
import os
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from manifold_security import audit, principals, tokens
from manifold_security.context import SCOPE_KEY, Caller, current_caller_var
from manifold_security.startup import is_loopback  # noqa: F401  (re-exported: the one definition lives with the startup rules)
from manifold_security.store import StoreError, open_store
from manifold_security.throttle import Throttle, client_address

OPEN_PATHS = ("/health",)
DEFAULT_DATA_DIR = "/data"

GENERIC_BODY = b'{"status":"error","message":"authentication required"}'
REMOVED_BODY = b'{"status":"error","message":"your access was removed or has expired"}'
FORBIDDEN_BODY = b'{"status":"error","message":"this session belongs to another principal"}'
UNAVAILABLE_BODY = b'{"status":"error","message":"the security store is unavailable"}'


THROTTLED_BODY = b'{"status":"error","message":"too many failed attempts; try again later"}'


def data_dir_from_env() -> Path:
    """The security data folder: ``MANIFOLD_DATA_DIR``, else ``/data`` (the container's data volume)."""
    return Path(os.environ.get("MANIFOLD_DATA_DIR", "").strip() or DEFAULT_DATA_DIR)


def _presented_secret(authorization: str) -> Optional[str]:
    """The secret in an Authorization header value (Bearer credential, or Basic password), else None."""
    scheme, _, value = authorization.strip().partition(" ")
    value = value.strip()
    if not value:
        return None
    scheme = scheme.lower()
    if scheme == "bearer":
        return value
    if scheme == "basic":
        try:
            decoded = base64.b64decode(value, validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            return None
        _, separator, password = decoded.partition(":")
        return password if separator else None
    return None


@dataclass(frozen=True)
class Outcome:
    caller: Optional[Caller] = None
    removed: bool = False  # a complete, correct secret whose access was removed or has expired


class StoreAccess:
    """
    A lazily opened connection to the security store, shared by the middleware.

    The data folder is read from ``MANIFOLD_DATA_DIR`` on each use and the connection is reopened
    if it changed (tests rely on this); a lock serialises use because the connection is shared
    between threads.  Reads always see committed changes from other processes.
    """

    def __init__(self, data_dir=None):
        self._explicit = Path(data_dir) if data_dir else None
        self._lock = threading.Lock()
        self._conn = None
        self._path = None

    def _connection(self):
        path = self._explicit or data_dir_from_env()
        if self._conn is None or self._path != path:
            if self._conn is not None:
                self._conn.close()
                self._conn = None
            self._conn = open_store(path, check_same_thread=False)
            self._path = path
        return self._conn

    def authenticate(self, presented: Optional[str]) -> Outcome:
        """Check ``presented`` against the store now.  Raises :class:`StoreError` if the store cannot be opened."""
        with self._lock:
            conn = self._connection()
            if not presented:
                return Outcome()
            result = tokens.verify(conn, presented)
            if result.status == tokens.UNKNOWN:
                return Outcome()
            if result.status != tokens.VALID:
                return Outcome(removed=True)
            principal = principals.get_principal(conn, result.principal_id)
            if principal is None:
                return Outcome()
            if not principal.active:
                return Outcome(removed=True)
            roles = tuple(sorted(principals.roles_of(conn, principal.id)))
            return Outcome(Caller(principal.id, principal.name, principal.kind, roles, result.credential_id))

    def authorize(self, principal_id: str, capability: str, scope: Optional[str] = None,
                  credential_id: Optional[str] = None):
        """The authorizer's decision for this principal now (a refusal is audited)."""
        from manifold_security import authorizer
        with self._lock:
            return authorizer.authorize(self._connection(), principal_id, capability, scope, credential_id)

    def use(self, fn):
        """Run ``fn(connection)`` under the lock and return its result (the connection is shared between threads)."""
        with self._lock:
            return fn(self._connection())

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                self._conn.close()
                self._conn = None

    def principal_count(self) -> int:
        with self._lock:
            return principals.count_principals(self._connection())


def _authorization(scope) -> Optional[str]:
    for name, value in scope.get("headers", []):
        if name == b"authorization":
            return value.decode("latin-1")
    return None


_SESSION_RE = re.compile(r"session_id=([0-9A-Za-z]+)")


def _session_id(scope) -> Optional[str]:
    found = _SESSION_RE.search(scope.get("query_string", b"").decode("latin-1"))
    return found.group(1) if found else None


_CHALLENGES: List[Tuple[bytes, bytes]] = [
    (b"www-authenticate", b'Bearer realm="manifold"'),
    (b"www-authenticate", b'Basic realm="manifold", charset="UTF-8"'),
]


class PrincipalAuthMiddleware:
    """Pure ASGI middleware (it does not buffer, so streaming and SSE responses are unaffected)."""

    def __init__(self, app, store: Optional[StoreAccess] = None, open_paths: Iterable[str] = OPEN_PATHS,
                 throttle: Optional[Throttle] = None, trusted_proxies=None):
        self.app = app
        self.store = store or StoreAccess()
        self.open_paths = tuple(open_paths)
        self.throttle = throttle
        self._trusted_proxies = trusted_proxies or (lambda: [])
        self._sessions = {}  # SSE session id -> id of the principal that opened the stream

    def _address(self, scope) -> str:
        peer = (scope.get("client") or (None,))[0]
        forwarded = None
        for name, value in scope.get("headers", []):
            if name == b"x-forwarded-for":
                forwarded = value.decode("latin-1")
        try:
            proxies = self._trusted_proxies()
        except Exception:
            proxies = []
        return client_address(peer, forwarded, proxies)

    def _audit(self, event: str, address: str) -> None:
        """Record a refused sign-in with the address and a generic reason; never the credential."""
        try:
            self.store.use(lambda conn: audit.record(conn, event, "anonymous", address, audit.GENERIC_FAILURE))
        except Exception:
            pass  # the refusal stands even if the audit cannot be written

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return
        header = _authorization(scope)
        presented = _presented_secret(header) if header else None
        is_open = scope.get("path") in self.open_paths
        address = self._address(scope)
        if self.throttle is not None:
            wait = self.throttle.retry_after(address)
            if wait:
                # A delay is running: the credential is not looked at, so the delay cannot be used to test guesses.
                self._audit(audit.SIGNIN_THROTTLED, address)
                if is_open:
                    await self.app(scope, receive, send)  # /health stays reachable, anonymous
                else:
                    await self._refuse(scope, send, 429, THROTTLED_BODY, retry_after=wait)
                return
        try:
            outcome = self.store.authenticate(presented)
        except StoreError:
            if is_open:  # /health stays reachable for the container probe, with no detail
                await self.app(scope, receive, send)
                return
            await self._refuse(scope, send, 503, UNAVAILABLE_BODY)
            return
        if header is not None and self.throttle is not None:
            if outcome.caller is None:
                self.throttle.record_failure(address)
                self._audit(audit.SIGNIN_FAILED, address)
            else:
                self.throttle.record_success(address)
        if outcome.caller is not None:
            scope[SCOPE_KEY] = outcome.caller
            if scope["type"] == "http" and scope.get("method") == "POST" and scope.get("path", "").startswith("/messages"):
                bound = self._sessions.get(_session_id(scope))
                if bound is not None and bound != outcome.caller.principal_id:
                    # A session id is not a credential: only the principal that opened the stream may post to it.
                    await self._refuse(scope, send, 403, FORBIDDEN_BODY)
                    return
            token = current_caller_var.set(outcome.caller)
            try:
                if scope["type"] == "http" and scope.get("method") == "GET" and scope.get("path") == "/sse":
                    await self._serve_sse(scope, receive, send, outcome.caller)
                else:
                    await self.app(scope, receive, send)
            finally:
                current_caller_var.reset(token)
            return
        if is_open:
            await self.app(scope, receive, send)
            return
        await self._refuse(scope, send, 401, REMOVED_BODY if outcome.removed else GENERIC_BODY)

    async def _serve_sse(self, scope, receive, send, caller):
        """Serve an SSE stream, binding the session id it announces to the principal that opened it."""
        opened = []

        async def watching_send(message):
            if message["type"] == "http.response.body" and not opened:
                found = _SESSION_RE.search(message.get("body", b"").decode("latin-1"))
                if found:
                    opened.append(found.group(1))
                    self._sessions[found.group(1)] = caller.principal_id
            await send(message)

        try:
            await self.app(scope, receive, watching_send)
        finally:
            for session_id in opened:
                self._sessions.pop(session_id, None)

    @staticmethod
    async def _refuse(scope, send, status, body, retry_after=None):
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        headers = [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())]
        if status == 401:
            headers += _CHALLENGES
        if retry_after:
            headers.append((b"retry-after", str(retry_after).encode()))
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": body})
