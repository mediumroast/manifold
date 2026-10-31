# SPDX-License-Identifier: Apache-2.0
"""The wiki browser: the shell page, brand settings, vendored files, and the offline guarantee."""

import hashlib
import re
from pathlib import Path

import pytest

from wiki_backend import assets
from wiki_backend.config import ConfigError, DEFAULT_ACCENT, DEFAULT_ACCENT_DARK, load_config
from wiki_backend.web import VENDOR_URL, instance_shell, render_shell, vendor_dir


@pytest.fixture(autouse=True)
def real_assets(monkeypatch):
    monkeypatch.delenv("MANIFOLD_ASSETS_DIR", raising=False)


def _set_config(root, body):
    (root / "manifold.yaml").write_text("version: 1\n" + body)


# ── brand settings ───────────────────────────────────────────────────────────

def test_brand_defaults(tmp_path):
    _set_config(tmp_path, "")
    config = load_config(tmp_path)
    assert (config.accent, config.accent_dark) == (DEFAULT_ACCENT, DEFAULT_ACCENT_DARK)


def test_brand_colors_are_read(tmp_path):
    _set_config(tmp_path, 'brand:\n  accent: "#112233"\n  accent_dark: "#AABBCC"\n')
    config = load_config(tmp_path)
    assert (config.accent, config.accent_dark) == ("#112233", "#AABBCC")


@pytest.mark.parametrize("body,message", [
    ('brand:\n  accent: red\n', "brand.accent must be a color"),
    ('brand:\n  accent_dark: "#12345"\n', "brand.accent_dark must be a color"),
    ('brand:\n  accent: "#12345g"\n', "brand.accent must be a color"),
    ('brand: nope\n', "brand must be a mapping"),
    ('brand:\n  accent: ["#112233"]\n', "must be text"),
])
def test_bad_brand_settings_are_refused(tmp_path, body, message):
    _set_config(tmp_path, body)
    with pytest.raises(ConfigError, match=message):
        load_config(tmp_path)


# ── the shell page ───────────────────────────────────────────────────────────

def test_shell_shows_the_instance_name_and_colors(tmp_path):
    _set_config(tmp_path, 'name: Acme Wiki\nbrand:\n  accent: "#112233"\n  accent_dark: "#445566"\n')
    page = render_shell(tmp_path)
    assert "<title>Acme Wiki</title>" in page
    assert '"#112233"' in page and '"#445566"' in page
    assert "{{" not in page


def test_shell_uses_defaults_without_a_valid_config(tmp_path):
    page = render_shell(tmp_path)  # no manifold.yaml at all
    assert "<title>Manifold</title>" in page and DEFAULT_ACCENT in page and DEFAULT_ACCENT_DARK in page


def test_a_hostile_name_cannot_break_out_of_the_page(tmp_path):
    _set_config(tmp_path, 'name: "</script><script>alert(1)</script><b>x</b>"\n')
    page = render_shell(tmp_path)
    assert "<script>alert(1)" not in page and "<b>x</b>" not in page
    assert "&lt;/script&gt;" in page.split("<title>")[1].split("</title>")[0]
    config_block = page.split("window.$docsify = ", 1)[1].split("\n  </script>", 1)[0]
    assert "<" not in config_block and ">" not in config_block


def test_instance_template_overrides_the_core_shell(tmp_path):
    _set_config(tmp_path, "name: Mine\n")
    (tmp_path / "assets" / "web").mkdir(parents=True)
    (tmp_path / "assets" / "web" / "index.html").write_text("<h1>{{TITLE}}</h1>{{DOCSIFY_CONFIG}}")
    assert render_shell(tmp_path).startswith("<h1>Mine</h1>{")


def test_a_complete_instance_page_is_detected(tmp_path):
    assert instance_shell(tmp_path) is None
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.html").write_text("<html></html>")
    assert instance_shell(tmp_path) == tmp_path / "wiki" / "index.html"


def test_the_shell_strips_frontmatter_for_readers():
    template = assets.read_text(Path("/nonexistent"), "web/index.html")
    assert "hook.beforeEach" in template and "---" in template


# ── what the page loads ──────────────────────────────────────────────────────

def _page_references(tmp_path):
    _set_config(tmp_path, "")
    page = render_shell(tmp_path)
    return re.findall(r'(?:src|href)="([^"]+)"', page)


def test_the_page_loads_only_from_this_server(tmp_path):
    for reference in _page_references(tmp_path):
        assert reference == "data:," or reference.startswith(VENDOR_URL + "/"), reference


def test_every_file_the_page_loads_exists(tmp_path):
    for reference in _page_references(tmp_path):
        if reference.startswith(VENDOR_URL + "/"):
            assert (vendor_dir() / reference[len(VENDOR_URL) + 1:]).is_file(), reference


def test_vendored_styles_and_scripts_reach_no_other_host():
    css = (vendor_dir() / "darklight.min.css").read_text(encoding="utf-8")
    assert "@import" not in css and not re.search(r"url\(\s*['\"]?(https?:)?//", css)
    script = (vendor_dir() / "darklight.min.js").read_text(encoding="utf-8")
    assert "cdn.jsdelivr.net" not in script and "googleapis" not in script
    assert VENDOR_URL + "/icons/moon.svg" in script and VENDOR_URL + "/icons/sun.svg" in script
    assert (vendor_dir() / "icons" / "moon.svg").is_file() and (vendor_dir() / "icons" / "sun.svg").is_file()


# ── vendored files are what the record says ──────────────────────────────────

def test_checksums_match_the_vendored_files():
    listed = {}
    for line in (vendor_dir() / "SHA256SUMS").read_text().splitlines():
        digest, _, name = line.partition("  ")
        listed[name] = digest
    on_disk = {p.relative_to(vendor_dir()).as_posix() for p in vendor_dir().rglob("*")
               if p.is_file() and p.name not in ("SHA256SUMS", "VENDORED.md")}
    assert set(listed) == on_disk
    for name, digest in listed.items():
        assert hashlib.sha256((vendor_dir() / name).read_bytes()).hexdigest() == digest, name


def test_every_vendored_package_has_its_license_text():
    for package in ("docsify", "prismjs", "docsify-copy-code", "docsify-darklight-theme"):
        text = (vendor_dir() / "licenses" / ("%s-LICENSE.txt" % package)).read_text()
        assert "mit license" in text.lower() and "Permission is hereby granted" in text


def test_the_vendoring_record_names_every_package_and_the_two_patches():
    record = (vendor_dir() / "VENDORED.md").read_text()
    for token in ("docsify", "prismjs", "docsify-copy-code", "docsify-darklight-theme", "sha512-", "darklight.min.css", "darklight.min.js"):
        assert token in record
    for name in ("darklight.min.css", "darklight.min.js"):
        assert (vendor_dir() / name).read_text(encoding="utf-8").startswith("/* Modified from docsify-darklight-theme")


# ── the routes ───────────────────────────────────────────────────────────────

@pytest.fixture()
def docs_client(tmp_path):
    """The wiki browser routes of a small instance, mounted in their own app."""
    pytest.importorskip("fastmcp")
    from starlette.applications import Starlette
    from starlette.testclient import TestClient
    import server
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "index.md").write_text("# Home\n")
    (tmp_path / "raw").mkdir()
    (tmp_path / "raw" / "note.md").write_text("raw note")
    _set_config(tmp_path, "name: Test Wiki\n")
    return TestClient(Starlette(routes=server._build_docs_routes(tmp_path))), tmp_path


def test_the_docs_route_returns_the_shell(docs_client):
    client, _ = docs_client
    for path in ("/docs/", "/docs/index.html"):
        response = client.get(path)
        assert response.status_code == 200 and "text/html" in response.headers["content-type"]
        assert "<title>Test Wiki</title>" in response.text and "window.$docsify" in response.text


def test_vendored_files_are_served_with_the_right_types(docs_client):
    client, _ = docs_client
    script = client.get(VENDOR_URL + "/docsify.min.js")
    assert script.status_code == 200 and "javascript" in script.headers["content-type"]
    assert client.get(VENDOR_URL + "/darklight.min.css").headers["content-type"].startswith("text/css")
    assert client.get(VENDOR_URL + "/icons/moon.svg").status_code == 200
    assert client.get(VENDOR_URL + "/nope.js").status_code == 404
    assert client.get(VENDOR_URL + "/../../../etc/passwd").status_code in (400, 404)


def test_pages_and_raw_files_are_still_served(docs_client):
    client, _ = docs_client
    assert client.get("/docs/index.md").text == "# Home\n"
    assert client.get("/docs/raw/note.md").text == "raw note"


def test_an_instance_page_replaces_the_shell(docs_client):
    client, root = docs_client
    (root / "wiki" / "index.html").write_text("<html>my own page</html>")
    assert client.get("/docs/").text == "<html>my own page</html>"


def test_no_wiki_folder_means_no_browser(tmp_path):
    pytest.importorskip("fastmcp")
    import server
    assert server._build_docs_routes(tmp_path) == []
