# SPDX-License-Identifier: Apache-2.0
"""Authorization for the tools and the HTTP routes.

``Guard.guarded`` wraps every MCP tool: it refuses a tool that has no entry in
``authorizer.TOOL_POLICY``, refuses a call with no signed-in principal, makes that
principal the acting principal for the call (``wiki_backend.actor``), checks the
``read`` capability for read tools, and turns :class:`Refused` into a plain error result.
Tools whose requirement depends on the page, component or handoff they name call
``Guard.require(capability, scope)`` themselves, before they change anything.

``RoutePolicyMiddleware`` applies ``read`` to the wiki browser under ``/docs``.
"""

import functools
from typing import Callable, Optional

from manifold_security import authorizer, principals
from manifold_security.context import SCOPE_KEY, Caller
from . import actor

_REASON_TEXT = {
    authorizer.NO_PRINCIPAL: "your principal no longer exists",
    authorizer.PRINCIPAL_INACTIVE: "your access was removed",
    authorizer.CREDENTIAL_INVALID: "your credential was revoked or has expired",
    authorizer.UNKNOWN_CAPABILITY: "that operation is not available",
    authorizer.ROLE_MISSING: "none of your roles allows this",
    authorizer.HUMAN_REQUIRED: "only a human registrar may do this",
    authorizer.DENIED: "access to this component is denied for you",
    authorizer.NO_GRANT: "you have no grant on this component",
}


class Refused(Exception):
    """The caller may not do this.  The message says why, in the caller's terms."""

    def __init__(self, message: str, reason: str = "refused"):
        super().__init__(message)
        self.message = message
        self.reason = reason

    def as_dict(self) -> dict:
        return {"error": self.message, "refused": True, "reason": self.reason}


class Guard:
    def __init__(self, store, caller_getter: Callable[[], Optional[Caller]]):
        self.store = store
        self._caller_getter = caller_getter

    def caller(self) -> Caller:
        caller = self._caller_getter()
        if caller is None:
            raise Refused("authentication required", "unauthenticated")
        return caller

    def require(self, capability: str, scope: Optional[str] = None):
        """Raise :class:`Refused` unless the caller may use ``capability`` on ``scope`` now."""
        caller = self.caller()
        decision = self.store.authorize(caller.principal_id, capability, scope, caller.credential_id)
        if not decision:
            where = " on %s" % scope if scope else ""
            raise Refused("Refused: %s (%s%s)." % (_REASON_TEXT.get(decision.reason, "not allowed"), capability, where),
                          decision.reason or "refused")
        return decision

    def has_role(self, role: str) -> bool:
        caller = self.caller()
        return self.store.use(lambda conn: role in principals.roles_of(conn, caller.principal_id))

    def require_active(self, slug: str) -> None:
        """Refuse a change to an archived component."""
        archived = self.store.use(lambda conn: principals.get_component_state(conn, slug).archived)
        if archived:
            raise Refused("Refused: component %s is archived. A registrar can restore it with "
                          "wiki_component_manage_tool(action='restore')." % slug, "archived")

    def guarded(self, func: Callable) -> Callable:
        """Decorator for an MCP tool function.  Apply under ``@app.tool()``."""
        name = func.__name__
        policy = authorizer.TOOL_POLICY.get(name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if policy is None:
                return Refused("Refused: %s has no access policy." % name, "no_policy").as_dict()
            try:
                caller = self.caller()
                token = actor.acting_var.set(caller)
            except Refused as exc:
                return exc.as_dict()
            try:
                if policy == authorizer.READ:
                    self.require(authorizer.READ)
                return func(*args, **kwargs)
            except Refused as exc:
                return exc.as_dict()
            finally:
                actor.acting_var.reset(token)

        wrapper.__manifold_guarded__ = True
        return wrapper


class RoutePolicyMiddleware:
    """Require ``read`` for the wiki browser (``/docs`` and everything under it).  Runs after authentication."""

    def __init__(self, app, store):
        self.app = app
        self.store = store

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if scope["type"] == "http" and (path == "/docs" or path.startswith("/docs/")):
            caller = scope.get(SCOPE_KEY)
            if caller is None or not self.store.authorize(
                    caller.principal_id, authorizer.READ, None, caller.credential_id):
                body = b'{"status":"error","message":"not allowed"}'
                await send({"type": "http.response.start", "status": 403,
                            "headers": [(b"content-type", b"application/json"),
                                        (b"content-length", str(len(body)).encode())]})
                await send({"type": "http.response.body", "body": body})
                return
        await self.app(scope, receive, send)
