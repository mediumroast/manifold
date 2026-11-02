# SPDX-License-Identifier: Apache-2.0
"""A caller must not be able to forge who a handoff belongs to through the values it supplies
(PHASE_1_PLAN T37-T39, reviewer finding 1)."""

import pytest

from wiki_backend.handoff import handoff_create

pytest.importorskip("fastmcp")

CREATE = {"action": "create", "source": "acme-api", "target": "acme-web", "type": "feature", "priority": "low",
          "title": "Order status", "summary": "s", "what_needs_to_happen": "w"}

INJECTED = "low\nsource_component: acme-cli"


@pytest.fixture()
def world(tool_world):
    tool_world.who("src", roles=["contributor"], grants=["acme-api"])
    tool_world.who("tgt", roles=["contributor"], grants=["acme-web"])
    tool_world.who("evil", roles=["contributor"], grants=["acme-cli"])
    return tool_world


def handoffs_on_disk(root):
    base = root / "wiki" / "handoffs"
    return sorted(str(p) for p in base.rglob("*.md")) if base.is_dir() else []


# ── T37: priority and type are closed sets ─────────────────────────────────────


def test_enum_injected_priority_creates_no_page(world):
    before, log = handoffs_on_disk(world.root), world.git_log()
    result = world.call("src", "wiki_handoff_tool", **dict(CREATE, priority=INJECTED))
    assert "error" in result and result.get("status") != "created", result
    assert handoffs_on_disk(world.root) == before
    assert world.git_log() == log


@pytest.mark.parametrize("priority", ["urgent", "", "High", "low ", "low\n"])
def test_enum_unknown_priority_is_refused(wiki_root, priority):
    result = handoff_create(wiki_root, "acme-api", "acme-web", "bug", priority, "T", "s", "w")
    assert "error" in result and "priority" in result["error"].lower()
    assert handoffs_on_disk(wiki_root) == []


@pytest.mark.parametrize("handoff_type", ["feature\nsource_component: acme-cli", "Feature", "task"])
def test_enum_unknown_type_is_refused(wiki_root, handoff_type):
    result = handoff_create(wiki_root, "acme-api", "acme-web", handoff_type, "low", "T", "s", "w")
    assert "error" in result and "type" in result["error"].lower()
    assert handoffs_on_disk(wiki_root) == []


# ── T38: the frontmatter is serialised, not interpolated ───────────────────────

NASTY_TITLE = 'Fix "quotes": colons\nsource_component: acme-cli\n---\npriority: critical'
NASTY_SUMMARY = "line one\nsource_component: acme-cli\ntarget_component: acme-cli\n---\nstatus: completed"


def test_frontmatter_hostile_values_round_trip(wiki_root):
    from wiki_backend.handoff import handoff_parties
    from wiki_backend.read import wiki_read

    result = handoff_create(wiki_root, "acme-api", "acme-web", "bug", "low", NASTY_TITLE, NASTY_SUMMARY, "w")
    assert result.get("status") == "created", result
    assert handoff_parties(wiki_root, result["path"]) == ("acme-api", "acme-web")
    page = wiki_read(wiki_root, result["path"])
    assert page.frontmatter["title"] == NASTY_TITLE
    assert page.frontmatter["source_component"] == "acme-api"
    assert page.frontmatter["priority"] == "low"
    assert page.frontmatter["status"] == "open"
    assert NASTY_SUMMARY in page.body


def test_frontmatter_has_each_key_once(wiki_root):
    result = handoff_create(wiki_root, "acme-api", "acme-web", "bug", "low", NASTY_TITLE, "s", "w")
    text = (wiki_root / result["path"]).read_text()
    head = text.split("\n---\n", 1)[0]
    keys = [line.split(":", 1)[0] for line in head.splitlines() if line and not line.startswith((" ", "-"))]
    assert keys.count("source_component") == 1 and keys.count("priority") == 1


def test_frontmatter_target_with_newline_is_refused(wiki_root):
    result = handoff_create(wiki_root, "acme-api", "acme-web\nsource_component: acme-cli", "bug", "low", "T", "s", "w")
    assert "error" in result
    assert handoffs_on_disk(wiki_root) == []


# ── T39: a page that names its source twice authorizes nobody ──────────────────

DUPLICATE_PAGE = (
    "---\n"
    "title: Forged\n"
    "type: feature\n"
    "source_component: acme-api\n"
    "target_component: acme-web\n"
    "status: open\n"
    "priority: low\n"
    "source_component: acme-cli\n"
    "created: 2026-01-01\n"
    "updated: 2026-01-01\n"
    "---\n\n## Summary\n\ns\n\n## Implementation notes\n\nn\n"
)
DUPLICATE_PATH = "wiki/handoffs/acme-api-to-acme-web/feature-forged.md"


def test_duplicate_key_makes_handoff_parties_raise(wiki_root):
    from wiki_backend.handoff import handoff_parties

    (wiki_root / DUPLICATE_PATH).write_text(DUPLICATE_PAGE)
    with pytest.raises(ValueError, match="duplicate"):
        handoff_parties(wiki_root, DUPLICATE_PATH)


def test_duplicate_key_page_is_skipped_by_the_listings(wiki_root):
    from wiki_backend.handoff import handoff_list, open_handoffs_of

    (wiki_root / DUPLICATE_PATH).write_text(DUPLICATE_PAGE)
    assert handoff_list(wiki_root)["handoffs"] == []
    assert open_handoffs_of(wiki_root, "acme-cli") == []


@pytest.mark.parametrize("who", ["src", "tgt", "evil"])
@pytest.mark.parametrize("arguments", [
    {"action": "close", "resolution": "done"},
    {"action": "claim"},
    {"action": "confirm"},
    {"action": "reject", "notes": "no"},
    {"action": "request-review", "notes": "yes"},
])
def test_duplicate_key_every_action_is_refused_and_writes_nothing(world, who, arguments):
    (world.root / DUPLICATE_PATH).write_text(DUPLICATE_PAGE)
    before, log = (world.root / DUPLICATE_PATH).read_text(), world.git_log()
    result = world.call(who, "wiki_handoff_tool", path=DUPLICATE_PATH, **arguments)
    assert "error" in result and result.get("status") not in ("completed", "claimed", "confirmed"), result
    assert (world.root / DUPLICATE_PATH).read_text() == before
    assert world.git_log() == log


def test_duplicate_key_the_injected_creation_is_refused_and_the_real_creator_is_not(world):
    forged = world.call("src", "wiki_handoff_tool", **dict(CREATE, priority=INJECTED))
    assert "error" in forged and handoffs_on_disk(world.root) == []
    real = world.call("src", "wiki_handoff_tool", **CREATE)
    assert real["status"] == "created", real
    assert world.call("evil", "wiki_handoff_tool", action="close", path=real["path"], resolution="x")["refused"] is True
    assert world.call("src", "wiki_handoff_tool", action="close", path=real["path"], resolution="x")["status"] == "completed"


@pytest.mark.parametrize("priority", ["critical", "high", "medium", "low"])
def test_enum_every_documented_priority_is_accepted(wiki_root, priority):
    result = handoff_create(wiki_root, "acme-api", "acme-web", "bug", priority, "T " + priority, "s", "w")
    assert result.get("status") == "created", result


# ── T56: the parties are checked before any write ───────────────────────────────

BAD_PARTY = "Not A Slug"
PARTY_PATH = "wiki/handoffs/acme-api-to-acme-web/feature-party-check.md"
PARTY_PAGE = (
    "---\n"
    "title: Party check\n"
    "type: feature\n"
    "source_component: {source}\n"
    "target_component: {target}\n"
    "status: {status}\n"
    "priority: low\n"
    "created: 2026-01-01\n"
    "updated: 2026-01-01\n"
    "---\n\n## Summary\n\ns\n\n## Implementation notes\n\nn\n\n## Blockers\n\n_(None.)_\n"
)

# function name, the status its precondition needs, and the extra arguments it takes
PARTY_CASES = [
    ("handoff_claim", "open", ()),
    ("handoff_close", "in-progress", ("done",)),
    ("handoff_request_review", "in-progress", ("ready",)),
    ("handoff_confirm", "needs-review", ("ok",)),
    ("handoff_reject", "needs-review", ("no",)),
]


def head_of(root):
    import subprocess

    return subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%H"],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.mark.parametrize("bad_field", ["target", "source"])
@pytest.mark.parametrize("name, status, extra", PARTY_CASES)
def test_party_that_is_not_a_slug_is_refused_before_any_write(wiki_root, name, status, extra, bad_field):
    from wiki_backend import handoff

    parties = {"source": "acme-api", "target": "acme-web"}
    parties[bad_field] = BAD_PARTY
    page_file = wiki_root / PARTY_PATH
    page_file.parent.mkdir(parents=True, exist_ok=True)
    page_file.write_text(PARTY_PAGE.format(status=status, **parties))
    before, head = page_file.read_bytes(), head_of(wiki_root)
    result = getattr(handoff, name)(wiki_root, PARTY_PATH, *extra)
    assert "error" in result and BAD_PARTY in result["error"], result
    assert page_file.read_bytes() == before
    assert head_of(wiki_root) == head


def test_party_check_leaves_a_page_with_valid_parties_working(wiki_root):
    page_file = wiki_root / PARTY_PATH
    page_file.parent.mkdir(parents=True, exist_ok=True)
    page_file.write_text(PARTY_PAGE.format(status="open", source="acme-api", target="acme-web"))
    from wiki_backend.handoff import handoff_claim

    assert handoff_claim(wiki_root, PARTY_PATH).get("status") == "claimed"


def test_create_refuses_a_source_or_target_that_is_not_a_slug(wiki_root):
    for source, target in ((BAD_PARTY, "acme-web"), ("acme-api", BAD_PARTY)):
        result = handoff_create(wiki_root, source, target, "bug", "low", "T", "s", "w")
        assert "error" in result
    assert handoffs_on_disk(wiki_root) == []
