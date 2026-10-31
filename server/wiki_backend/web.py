# SPDX-License-Identifier: Apache-2.0
"""The wiki browser page: a generic Docsify shell filled in from manifold.yaml.

The shell is ``assets/web/index.html``.  An instance can replace it, either with its own
``assets/web/index.html`` (same placeholders) or with a complete ``wiki/index.html``, which
is served as it is.  The scripts and styles it loads come from ``assets/web/vendor/`` and
are served by this server, so the page makes no request to any other host.
"""

import html
import json
from pathlib import Path
from typing import Optional

from . import assets
from .config import ConfigError, DEFAULT_ACCENT, DEFAULT_ACCENT_DARK, DEFAULT_NAME, load_config

VENDOR_URL = "/docs/_manifold/vendor"


def vendor_dir() -> Path:
    return assets.core_assets_dir() / "web" / "vendor"


def instance_shell(wiki_root: Path) -> Optional[Path]:
    """A complete page the instance supplies as wiki/index.html, if any."""
    page = Path(wiki_root) / "wiki" / "index.html"
    return page if page.is_file() else None


def _script_safe(text: str) -> str:
    """JSON that can sit inside a <script> element: no </script>, no HTML comment openers."""
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def render_shell(wiki_root: Path) -> str:
    """The shell page with this instance's name and colors filled in."""
    template = assets.read_text(wiki_root, "web/index.html")
    if template is None:
        raise FileNotFoundError("assets/web/index.html is missing from the server installation")
    try:
        config = load_config(wiki_root)
        name, accent, accent_dark = config.name, config.accent, config.accent_dark
    except ConfigError:
        name, accent, accent_dark = DEFAULT_NAME, DEFAULT_ACCENT, DEFAULT_ACCENT_DARK
    docsify = {
        "name": html.escape(name),
        "repo": "",
        "loadSidebar": "_sidebar.md",
        "subMaxLevel": 3,
        "homepage": "index.md",
        "relativePath": True,
        "search": {"placeholder": "Search docs...", "noData": "No results.", "depth": 6},
        "darklightTheme": {
            "defaultTheme": "os",
            "light": {"accent": accent},
            "dark": {"accent": accent_dark},
        },
    }
    return (template
            .replace("{{TITLE}}", html.escape(name))
            .replace("{{DOCSIFY_CONFIG}}", _script_safe(json.dumps(docsify, indent=2))))
