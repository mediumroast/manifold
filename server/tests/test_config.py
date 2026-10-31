# SPDX-License-Identifier: Apache-2.0
"""Tests for manifold.yaml: loading, validation, the component registry and the generated schema list."""

import subprocess

import pytest

from wiki_backend.config import (
    Component,
    ConfigError,
    add_component,
    load_config,
    registered_slugs,
    sync_schema_slugs,
    valid_slug,
)
from wiki_backend.handoff import handoff_create
from wiki_backend.models import WikiRegisterRequest
from wiki_backend.register import wiki_register_component


def _write(root, text):
    (root / "manifold.yaml").write_text(text, encoding="utf-8")


# ── slugs ────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("slug", ["a", "acme-api", "acme_api", "acme.io", "a1-b2.c3", "x" * 64])
def test_valid_slugs(slug):
    assert valid_slug(slug)


@pytest.mark.parametrize("slug", [
    "", "-a", "a-", ".a", "a.", "a--b", "a..b", "a/b", "A", "a b", "café", "x" * 65, None, 5,
])
def test_invalid_slugs(slug):
    assert not valid_slug(slug)


# ── loading ──────────────────────────────────────────────────────────────────

def test_load_reads_settings_and_components(tmp_path):
    _write(tmp_path, 'version: 1\nname: Acme Wiki\nserver_name: acme-wiki\ncomponents:\n'
                     '  - slug: acme-api\n    owner: Platform\n    repo: "https://example.test/acme-api"\n'
                     '  - slug: acme-web\n')
    config = load_config(tmp_path)
    assert (config.name, config.server_name) == ("Acme Wiki", "acme-wiki")
    assert config.slugs() == ["acme-api", "acme-web"]
    assert config.components[0].owner == "Platform"


def test_defaults_apply_when_omitted(tmp_path):
    _write(tmp_path, "version: 1\n")
    config = load_config(tmp_path)
    assert (config.name, config.server_name, config.components) == ("Manifold", "manifold", ())


def test_unknown_keys_are_ignored(tmp_path):
    _write(tmp_path, "version: 1\nfuture: {a: 1}\ncomponents:\n  - slug: acme-api\n    extra: yes\n")
    assert registered_slugs(tmp_path) == ["acme-api"]


def test_missing_file_says_how_to_fix_it(tmp_path):
    with pytest.raises(ConfigError, match="manifold.yaml not found"):
        load_config(tmp_path)


@pytest.mark.parametrize("text,message", [
    ("version: 2\n", "version must be 1"),
    ("components: []\n", "version must be 1"),
    ("- a\n- b\n", "must be a mapping"),
    ("version: 1\ncomponents: nope\n", "components must be a list"),
    ("version: 1\ncomponents:\n  - acme\n", "must be a mapping"),
    ("version: 1\ncomponents:\n  - slug: Bad Slug\n", "invalid slug"),
    ("version: 1\ncomponents:\n  - slug: ../x\n", "invalid slug"),
    ("version: 1\ncomponents:\n  - owner: x\n", "invalid slug"),
    ("version: 1\ncomponents:\n  - slug: a\n  - slug: a\n", "listed twice"),
    ("version: 1\ncomponents:\n  - slug: a\n    owner: [x]\n", "must be text"),
    ("version: 1\n  bad: : indent", "not valid YAML"),
])
def test_invalid_files_are_refused_with_a_reason(tmp_path, text, message):
    _write(tmp_path, text)
    with pytest.raises(ConfigError, match=message):
        load_config(tmp_path)


# ── adding components ────────────────────────────────────────────────────────

def test_add_keeps_comments_and_other_keys(tmp_path):
    _write(tmp_path, "# instance settings\nversion: 1\nname: Acme   # shown in the browser\n"
                     "components:\n  # the API\n  - slug: acme-api\n    owner: Platform\n\nstore:\n  kind: local-git\n")
    assert add_component(tmp_path, Component("acme-web", repo="https://example.test/web", owner="Web team"))
    text = (tmp_path / "manifold.yaml").read_text()
    assert "# instance settings" in text and "# the API" in text and "# shown in the browser" in text
    assert "store:\n  kind: local-git" in text
    assert text.index("acme-web") < text.index("store:")
    assert registered_slugs(tmp_path) == ["acme-api", "acme-web"]


def test_add_to_empty_flow_list(tmp_path):
    _write(tmp_path, "version: 1\ncomponents: []\nname: X\n")
    assert add_component(tmp_path, Component("acme-api"))
    assert registered_slugs(tmp_path) == ["acme-api"]
    assert load_config(tmp_path).name == "X"


def test_add_when_there_is_no_components_key(tmp_path):
    _write(tmp_path, "version: 1\nname: X")
    assert add_component(tmp_path, Component("acme-api", description='says "hi": ok'))
    config = load_config(tmp_path)
    assert config.slugs() == ["acme-api"] and config.components[0].description == 'says "hi": ok'


def test_add_to_a_list_that_is_not_indented(tmp_path):
    _write(tmp_path, "version: 1\ncomponents:\n- slug: acme-api\n- slug: acme-web\nname: X\n")
    assert add_component(tmp_path, Component("acme-cli"))
    assert registered_slugs(tmp_path) == ["acme-api", "acme-web", "acme-cli"]
    assert load_config(tmp_path).name == "X"


def test_add_twice_is_a_no_op(tmp_path):
    _write(tmp_path, "version: 1\ncomponents:\n  - slug: acme-api\n")
    before = (tmp_path / "manifold.yaml").read_text()
    assert add_component(tmp_path, Component("acme-api")) is False
    assert (tmp_path / "manifold.yaml").read_text() == before


def test_add_refuses_a_bad_slug_and_a_bad_file_without_changing_anything(tmp_path):
    _write(tmp_path, "version: 1\n")
    with pytest.raises(ConfigError):
        add_component(tmp_path, Component("../x"))
    _write(tmp_path, "version: 9\n")
    with pytest.raises(ConfigError):
        add_component(tmp_path, Component("acme-api"))
    assert (tmp_path / "manifold.yaml").read_text() == "version: 9\n"


def test_add_restores_the_file_when_the_result_does_not_load(tmp_path):
    _write(tmp_path, "version: 1\ncomponents: [{slug: acme-api}]\n")  # flow style with an item
    original = (tmp_path / "manifold.yaml").read_text()
    with pytest.raises(ConfigError, match="by hand"):
        add_component(tmp_path, Component("acme-web"))
    assert (tmp_path / "manifold.yaml").read_text() == original


# ── the generated slug list in the schema page ───────────────────────────────

def test_schema_list_is_regenerated_from_the_registry(tmp_path):
    _write(tmp_path, "version: 1\ncomponents:\n  - slug: acme-api\n  - slug: acme-web\n")
    (tmp_path / "wiki").mkdir()
    page = tmp_path / "wiki" / "CLAUDE.md"
    page.write_text("# Schema\n\nValid component slugs:\n- `old-one`\n- `old-two`\n\nUse these slugs.\n")
    assert sync_schema_slugs(tmp_path) == page
    assert page.read_text() == "# Schema\n\nValid component slugs:\n- `acme-api`\n- `acme-web`\n\nUse these slugs.\n"
    assert sync_schema_slugs(tmp_path) is None  # nothing left to change


def test_schema_sync_skips_a_page_without_the_list(tmp_path):
    _write(tmp_path, "version: 1\n")
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "CLAUDE.md").write_text("# Schema\n")
    assert sync_schema_slugs(tmp_path) is None


# ── handoffs use the registry ────────────────────────────────────────────────

def _handoff(root, source, target):
    return handoff_create(root, source, target, "feature", "medium", "Add a thing", "Summary", "Do it")


def test_handoff_between_registered_components_works(wiki_root):
    assert _handoff(wiki_root, "acme-api", "acme-data").get("status") == "created"


def test_handoff_to_an_unregistered_component_names_the_registered_ones(wiki_root):
    result = _handoff(wiki_root, "acme-api", "nope")
    assert "Unknown target component slug 'nope'" in result["error"]
    assert "'acme-api'" in result["error"] and "wiki_register_component_tool" in result["error"]


def test_handoff_from_an_unregistered_component_is_refused(wiki_root):
    assert "Unknown source component slug 'nope'" in _handoff(wiki_root, "nope", "acme-api")["error"]


def test_handoff_without_manifold_yaml_says_to_create_it(wiki_root):
    (wiki_root / "manifold.yaml").unlink()
    assert "manifold.yaml not found" in _handoff(wiki_root, "acme-api", "acme-web")["error"]


def test_a_newly_registered_component_can_be_used_at_once(wiki_root):
    assert "Unknown target" in _handoff(wiki_root, "acme-api", "acme-extra")["error"]
    (wiki_root / "manifold.yaml").write_text(
        (wiki_root / "manifold.yaml").read_text() + "  - slug: acme-extra\n")
    assert _handoff(wiki_root, "acme-api", "acme-extra").get("status") == "created"


# ── registering a component updates the registry ─────────────────────────────

def _register(root, name="acme-extra", **kw):
    request = WikiRegisterRequest(name=name, description="The API", repo="https://example.test/acme-extra",
                                  owner="Platform", skip_source_docs=True, **kw)
    return wiki_register_component(root, request)


def test_register_adds_the_component_to_the_registry_and_the_schema_list(wiki_root):
    (wiki_root / "wiki" / "CLAUDE.md").write_text("# Wiki Schema\n\nValid component slugs:\n- `acme-api`\n\nEnd.\n")
    assert _register(wiki_root).status == "created"
    config = load_config(wiki_root)
    assert "acme-extra" in config.slugs()
    assert next(c for c in config.components if c.slug == "acme-extra").owner == "Platform"
    assert "- `acme-extra`" in (wiki_root / "wiki" / "CLAUDE.md").read_text()
    assert _handoff(wiki_root, "acme-api", "acme-extra").get("status") == "created"
    log = subprocess.run(["git", "log", "--format=%s"], cwd=wiki_root, capture_output=True, text=True).stdout
    assert "register acme-extra in manifold.yaml" in log


def test_register_without_manifold_yaml_is_refused_before_writing_a_page(wiki_root):
    (wiki_root / "manifold.yaml").unlink()
    result = _register(wiki_root)
    assert result.status == "error" and "manifold.yaml not found" in result.message
    assert not (wiki_root / "wiki" / "components" / "acme-extra.md").exists()


@pytest.mark.parametrize("name", ["Bad Name", "a/b", "..", "a..b"])
def test_register_refuses_a_bad_name(wiki_root, name):
    assert _register(wiki_root, name=name).status == "error"
