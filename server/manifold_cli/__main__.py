# SPDX-License-Identifier: Apache-2.0
"""``python -m manifold_cli``: see ``manifold_cli.runner``."""

import sys

from .runner import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
