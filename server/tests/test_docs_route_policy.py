# SPDX-License-Identifier: Apache-2.0
"""The wiki browser under /docs is confined to the wiki and needs the read capability
(PHASE_1_TEST_PLAN A5, A6; INT-1 S9, S16; PHASE_1_PLAN T12).

The app is the real browser routes of ``server`` for a temporary instance, behind the real
authentication and route-policy middleware and a temporary store.
"""

import pytest

pytest.importorskip("fastmcp")

from starlette.applications import Starlette  # noqa: E402
from starlette.middleware import Middleware  # noqa: E402
from starlette.testclient import TestClient  # noqa: E402

from wiki_backend.auth import PrincipalAuthMiddleware, StoreAccess  # noqa: E402
from wiki_backend.guard import RoutePolicyMiddleware  # noqa: E402


@pytest.fixture()
def docs_world(tool_world, wiki_root):
    """Browser routes of the temporary instance with an admin-only principal and a reader, each with a credential."""
    import server
    (wiki_root / "raw").mkdir()
    (wiki_root / "raw" / "note.md").write_text("raw note\n")
    (wiki_root / "wiki" / "index.md").write_text("# Home\n")
    tool_world.who("root", "human", roles=["admin"])
    tool_world.who("rita", "human", roles=["reader"])
    store = StoreAccess(tool_world.data_dir)
    app = Starlette(routes=server._build_docs_routes(wiki_root),
                    middleware=[Middleware(PrincipalAuthMiddleware, store=store),
                                Middleware(RoutePolicyMiddleware, store=store)])
    tool_world.client = TestClient(app, base_url="http://127.0.0.1:8686")
    return tool_world


def _get(world, path, who=None):
    headers = {"Authorization": "Bearer " + world.tokens[who]} if who else {}
    return world.client.get(path, headers=headers)


# ── A5 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", [
    "/docs/..%2fmanifold.yaml",
    "/docs/../manifold.yaml",
    "/docs/raw/../../manifold.yaml",
    "/docs/leak.md",
    "/docs/g.md",
])
def test_A5_browser_routes_refuse_traversal_and_escaping_symlinks(docs_world, wiki_root, path):
    (wiki_root / "wiki" / "leak.md").symlink_to("../manifold.yaml")
    (wiki_root / "wiki" / "g.md").symlink_to("../.git/config")

    response = _get(docs_world, path, "rita")

    assert 400 <= response.status_code < 500, response.status_code
    assert "components:" not in response.text and "acme-api" not in response.text  # manifold.yaml content
    assert "[core]" not in response.text  # .git/config content


# ── A6 ───────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("path", [
    "/docs/",
    "/docs/index.html",
    "/docs/raw/note.md",
    "/docs/_manifold/vendor/docsify.min.js",
])
def test_A6_browser_routes_need_the_read_capability(docs_world, path):
    assert _get(docs_world, path, "root").status_code == 403
    assert _get(docs_world, path, "rita").status_code == 200
    assert _get(docs_world, path).status_code == 401
