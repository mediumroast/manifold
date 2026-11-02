# SPDX-License-Identifier: Apache-2.0
"""``source_docs`` may only name files in the readable folders of the wiki (PHASE_1_PLAN T42, reviewer finding 3)."""

from wiki_backend.models import WikiRegisterRequest
from wiki_backend.register import wiki_register_component

SECRET = "TOP-SECRET-OUTSIDE-CONTENT"


def register(root, name, docs):
    return wiki_register_component(root, WikiRegisterRequest(
        name=name, description="A component.", repo="https://example.test/org/" + name,
        owner="team", source_docs=docs))


def test_an_absolute_path_outside_the_root_is_not_embedded(wiki_root):
    outside = wiki_root.parent / ("outside-%s-readme.md" % wiki_root.name)
    outside.write_text(SECRET)
    result = register(wiki_root, "acme-qa", [str(outside)])
    page = (wiki_root / "wiki" / "components" / "acme-qa.md").read_text()
    assert SECRET not in page
    assert str(outside) in result.message


def test_a_dotdot_path_is_not_embedded(wiki_root):
    (wiki_root.parent / ("up-%s.md" % wiki_root.name)).write_text(SECRET)
    result = register(wiki_root, "acme-data", ["../up-%s.md" % wiki_root.name])
    page = (wiki_root / "wiki" / "components" / "acme-data.md").read_text()
    assert SECRET not in page
    assert "up-%s.md" % wiki_root.name in result.message


def test_a_file_outside_wiki_and_raw_is_not_embedded(wiki_root):
    (wiki_root / "manifold.private").write_text(SECRET)
    result = register(wiki_root, "acme-io", ["manifold.private"])
    assert SECRET not in (wiki_root / "wiki" / "components" / "acme-io.md").read_text()
    assert "manifold.private" in result.message


def test_a_readable_doc_is_still_embedded(wiki_root):
    raw = wiki_root / "raw" / "acme-cli"
    raw.mkdir(parents=True)
    (raw / "README.md").write_text("A readable readme sentence.")
    register(wiki_root, "acme-cli", ["raw/acme-cli/README.md"])
    assert "A readable readme sentence." in (wiki_root / "wiki" / "components" / "acme-cli.md").read_text()
