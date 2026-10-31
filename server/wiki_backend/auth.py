# SPDX-License-Identifier: Apache-2.0
"""Shared-token authentication for the HTTP surface.

One secret, ``MANIFOLD_TOKEN`` (or ``MANIFOLD_TOKEN_FILE``, a path to a file that
holds it, for container secrets), protects everything the server exposes except
``GET /health``: the MCP endpoints, ``/ingest`` and the wiki browser under
``/docs``.  A request is accepted when it carries the token as either

* ``Authorization: Bearer <token>``, for agents and scripts; or
* ``Authorization: Basic <base64 user:password>`` with the token as the
  password and any user name, so a browser can ask for it once and then send it
  with every request, including the static files the wiki browser loads.

This is a stopgap, not the security baseline: one shared secret, no per-user
identity, no per-component permissions, no rate limiting, no audit trail, no
TLS.  Those belong to the authentication plan that follows the migration.

Rules enforced at startup (see :func:`check_startup`):

* a token, when set, must be at least 24 characters;
* the server refuses to listen on any address except loopback without a token.
"""

import base64
import binascii
import hmac
import ipaddress
import os
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

MIN_TOKEN_LENGTH = 24
OPEN_PATHS = ("/health",)


class AuthConfigError(Exception):
    """The authentication settings are unusable.  The message says how to fix them."""


def configured_token() -> Optional[str]:
    """The shared token from the environment, or None when authentication is off."""
    token = os.environ.get("MANIFOLD_TOKEN", "").strip()
    if token:
        return token
    token_file = os.environ.get("MANIFOLD_TOKEN_FILE", "").strip()
    if token_file:
        try:
            return Path(token_file).read_text(encoding="utf-8").strip() or None
        except OSError as exc:
            raise AuthConfigError("MANIFOLD_TOKEN_FILE could not be read: %s" % exc)
    return None


def is_loopback(host: str) -> bool:
    """True for ``localhost`` and loopback addresses; anything else is reachable from elsewhere."""
    host = (host or "").strip().strip("[]")
    if host.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def check_startup(host: str) -> Optional[str]:
    """
    Refuse unsafe settings.  Returns a warning to log when authentication is off on
    loopback, else None.  Raises :class:`AuthConfigError` for a weak token, or for a
    non-loopback ``host`` with no token.
    """
    token = configured_token()
    if token is not None and len(token) < MIN_TOKEN_LENGTH:
        raise AuthConfigError(
            "The token is too short: use at least %d characters, for example the output of "
            "python3 -c 'import secrets; print(secrets.token_urlsafe(32))'." % MIN_TOKEN_LENGTH
        )
    if token is None and not is_loopback(host):
        raise AuthConfigError(
            "Refusing to listen on %r without authentication. Set MANIFOLD_TOKEN (or "
            "MANIFOLD_TOKEN_FILE), or listen on 127.0.0.1." % host
        )
    if token is None:
        return "Authentication is off: anyone who can reach this port can read and write the wiki."
    return None


def _presented_secret(authorization: str) -> Optional[str]:
    """The secret in an Authorization header value (Bearer token, or Basic password), else None."""
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


def is_authorized(authorization: Optional[str], token: Optional[str]) -> bool:
    """True when authentication is off, or the header carries the token (constant-time comparison)."""
    if token is None:
        return True
    if not authorization:
        return False
    presented = _presented_secret(authorization)
    if presented is None:
        return False
    return hmac.compare_digest(presented.encode("utf-8"), token.encode("utf-8"))


def _authorization(scope) -> Optional[str]:
    for name, value in scope.get("headers", []):
        if name == b"authorization":
            return value.decode("latin-1")
    return None


_CHALLENGES: List[Tuple[bytes, bytes]] = [
    (b"www-authenticate", b'Bearer realm="manifold"'),
    (b"www-authenticate", b'Basic realm="manifold", charset="UTF-8"'),
]


class TokenAuthMiddleware:
    """Pure ASGI middleware (it does not buffer, so streaming and SSE responses are unaffected)."""

    def __init__(self, app, open_paths: Iterable[str] = OPEN_PATHS):
        self.app = app
        self.open_paths = tuple(open_paths)

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket") or scope.get("path") in self.open_paths:
            await self.app(scope, receive, send)
            return
        try:
            token = configured_token()
        except AuthConfigError:
            token = ""  # an unreadable token file must not turn authentication off: deny everything
        if token is None or (token and is_authorized(_authorization(scope), token)):
            await self.app(scope, receive, send)
            return
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 1008})
            return
        body = b'{"status":"error","message":"authentication required"}'
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [(b"content-type", b"application/json"),
                        (b"content-length", str(len(body)).encode())] + _CHALLENGES,
        })
        await send({"type": "http.response.body", "body": body})
