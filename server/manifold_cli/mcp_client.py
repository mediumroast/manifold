# SPDX-License-Identifier: Apache-2.0
"""A very small MCP client over streamable HTTP (``POST /mcp``), standard library only.

``manifold init`` uses it to act as the first agent: it needs only ``initialize`` and ``tools/call``.
The server may answer with JSON or with a ``text/event-stream`` carrying one JSON-RPC message; both are read.
The credential is sent as a Bearer header and never printed or kept beyond the client object.
"""

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

PROTOCOL_VERSION = "2025-06-18"


class McpError(Exception):
    """The server refused or did not answer as expected.  The message says what happened (never the credential)."""


class McpClient:
    def __init__(self, base_url: str, credential: str, timeout: float = 30.0, opener=None):
        self.url = base_url.rstrip("/") + "/mcp"
        self._credential = credential
        self.timeout = timeout
        self._open = opener or urllib.request.urlopen
        self._session: Optional[str] = None
        self._next_id = 0

    def __repr__(self) -> str:
        return "McpClient(url=%r, credential=<hidden>)" % self.url

    def _post(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": "Bearer " + self._credential,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._session:
            headers["Mcp-Session-Id"] = self._session
            headers["MCP-Protocol-Version"] = PROTOCOL_VERSION
        request = urllib.request.Request(self.url, data=json.dumps(message).encode(), headers=headers, method="POST")
        try:
            response = self._open(request, timeout=self.timeout)
        except urllib.error.HTTPError as exc:
            raise McpError("The server answered %d to %s%s." % (
                exc.code, message.get("method", "a call"),
                " (the credential was refused)" if exc.code in (401, 403) else "")) from None
        except (urllib.error.URLError, OSError) as exc:
            raise McpError("Cannot reach %s: %s" % (self.url, getattr(exc, "reason", exc))) from None
        with response:
            session = response.headers.get("Mcp-Session-Id")
            if session:
                self._session = session
            body = response.read().decode("utf-8")
            kind = response.headers.get("Content-Type", "")
        if not body.strip():
            return None
        if "text/event-stream" in kind:
            payloads = [line[5:].strip() for line in body.splitlines() if line.startswith("data:")]
            payloads = [p for p in payloads if p]
            if not payloads:
                return None
            body = payloads[-1]
        try:
            return json.loads(body)
        except ValueError:
            raise McpError("The server answered with something that is not JSON.") from None

    def initialize(self) -> Dict[str, Any]:
        self._next_id += 1
        reply = self._post({
            "jsonrpc": "2.0", "id": self._next_id, "method": "initialize",
            "params": {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                       "clientInfo": {"name": "manifold-init", "version": "1"}}})
        if not reply or "result" not in reply:
            raise McpError("The server did not accept initialize: %s" % (reply or {}).get("error", "no result"))
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return reply["result"]

    def call_tool(self, name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call a tool and return its result as a dict (a tool error or refusal comes back as a dict with ``error``)."""
        self._next_id += 1
        reply = self._post({"jsonrpc": "2.0", "id": self._next_id, "method": "tools/call",
                            "params": {"name": name, "arguments": arguments or {}}})
        if not reply:
            raise McpError("No answer to %s." % name)
        if "error" in reply:
            raise McpError("%s failed: %s" % (name, reply["error"].get("message", reply["error"])))
        result = reply.get("result", {})
        if isinstance(result.get("structuredContent"), dict):
            return result["structuredContent"]
        for part in result.get("content", []):
            if part.get("type") == "text":
                try:
                    value = json.loads(part["text"])
                except ValueError:
                    return {"error": part["text"]} if result.get("isError") else {"text": part["text"]}
                return value if isinstance(value, dict) else {"value": value}
        return {"error": "empty result"} if result.get("isError") else {}
