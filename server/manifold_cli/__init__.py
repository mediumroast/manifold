# SPDX-License-Identifier: Apache-2.0
"""The Manifold host command: administration that happens on the host, never over MCP or HTTP.

Standard library only at import time (the launcher checks the Python version and runs
``python -m manifold_cli``); code that needs the server's own dependencies imports them when a
command that needs them runs.
"""
