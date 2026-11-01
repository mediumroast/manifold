# SPDX-License-Identifier: Apache-2.0
"""The principal on whose behalf the backend is acting during one tool call or request.

The guard (``wiki_backend.guard``) sets it once at the start of a tool call, from the
credential of the HTTP request that carried the call.  Backend code that records who did
something (git commits, log entries) reads it here; nothing the caller supplies in the
request body can change it.  Outside a tool call (tests, the host command) it is None.
"""

import contextvars
from typing import Optional

from manifold_security.context import Caller

acting_var: contextvars.ContextVar = contextvars.ContextVar("manifold_acting_principal", default=None)


def current_actor() -> Optional[Caller]:
    """The principal the current tool call is attributed to, or None."""
    return acting_var.get()
