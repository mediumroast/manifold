# SPDX-License-Identifier: Apache-2.0
"""Who is calling: the principal behind the credential of the current request.

The authentication middleware builds a :class:`Caller` for every request that carries a
valid credential, stores it in the ASGI scope under :data:`SCOPE_KEY`, and also sets
:data:`current_caller_var` for code that runs inside the same task.  Tool code asks the
*scope of the HTTP request that carried the call* (see ``server.current_caller``), because
over the SSE transport a tool call runs in the task that opened the stream, not in the
task that handled the POST; the context variable is a fallback for code the middleware
wraps directly.  Standard library only.
"""

import contextvars
from dataclasses import dataclass
from typing import Optional, Tuple

SCOPE_KEY = "manifold.caller"


@dataclass(frozen=True)
class Caller:
    """The authenticated caller of one request."""

    principal_id: str
    name: str
    kind: str
    roles: Tuple[str, ...]
    credential_id: str

    def as_dict(self) -> dict:
        """What a tool may tell the caller about itself (never the credential)."""
        return {"id": self.principal_id, "name": self.name, "kind": self.kind, "roles": list(self.roles)}


current_caller_var: contextvars.ContextVar = contextvars.ContextVar("manifold_current_caller", default=None)


def caller_from_scope(scope) -> Optional[Caller]:
    """The caller the middleware stored in an ASGI scope, or None."""
    return scope.get(SCOPE_KEY) if scope is not None else None
