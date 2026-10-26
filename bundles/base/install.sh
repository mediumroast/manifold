#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mediumroast, Inc.
# Thin launcher for install.py (needs Python 3.8 or newer).
here=$(cd "$(dirname "$0")" && pwd)
for py in python3 python; do
  if command -v "$py" >/dev/null 2>&1; then
    exec "$py" "$here/install.py" "$@"
  fi
done
echo "The Manifold installer needs Python 3.8 or newer, and none was found." >&2
echo "Manual install: copy the files under payload/ into your repository (see INSTALL.md)." >&2
exit 1
