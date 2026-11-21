# SPDX-License-Identifier: Apache-2.0
"""The contract harness itself (PHASE_4_PLAN Task 19, INT-2 S1)."""

import asyncio
import copy
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.contracts import harness

import server  # noqa: E402  (the harness puts the server folder on the path)


def test_a_renamed_field_names_the_tool_and_the_field():
    recording = harness.load(harness.CONTRACT_DIR / "wiki_read_tool.ok.json")
    actual = copy.deepcopy(recording["result"])
    actual["entity_tag"] = actual.pop("etag")  # the rename
    with pytest.raises(AssertionError) as caught:
        harness.compare("wiki_read_tool", recording["result"], actual)
    message = str(caught.value)
    assert "wiki_read_tool" in message and "result.etag" in message and "missing" in message


def test_a_changed_type_and_a_changed_value_are_both_differences():
    with pytest.raises(AssertionError, match=r"t: result\.a: expected int, got str"):
        harness.compare("t", {"a": 1}, {"a": "1"})
    with pytest.raises(AssertionError, match=r"t: result\.a\[1\]: expected 2, got 3"):
        harness.compare("t", {"a": [1, 2]}, {"a": [1, 3]})


def test_a_renamed_field_in_one_tool_leaves_the_other_recordings_alone(tmp_path, monkeypatch):
    """Every recording is run for real with one tool's answer renamed; only that tool's recording differs."""
    monkeypatch.setattr(server, "WIKI_ROOT", server.WIKI_ROOT)  # restored when the test ends
    broken_tool = "wiki_inventory_tool"  # no other case calls it as a setup step or to look up an etag
    failures = {}
    for index, path in enumerate(harness.recording_files()):
        recording = harness.load(path)
        parent = tmp_path / str(index)
        parent.mkdir()
        world, _root = harness.open_world(parent, monkeypatch.setenv)
        real_call = world.call

        def call(who, tool, _real=real_call, **arguments):
            result = _real(who, tool, **arguments)
            if tool == broken_tool:
                result = copy.deepcopy(result)
                result["component_list"] = result.pop("components")  # the rename
            return result

        world.call = call
        try:
            actual = harness.run_case(world, recording)
        finally:
            world.conn.close()
        try:
            harness.compare(recording["tool"], recording["result"], actual)
        except AssertionError as exc:
            failures[path.stem] = str(exc)
    assert sorted(failures) == [p.stem for p in harness.recording_files() if p.name.startswith(broken_tool + ".")]
    for message in failures.values():
        assert broken_tool in message and "result.components" in message


def test_the_register_recording_does_not_depend_on_the_day(contract_world, monkeypatch):
    import datetime
    from wiki_backend import register

    class OtherDay(datetime.date):
        @classmethod
        def today(cls):
            return datetime.date(2031, 5, 5)

    monkeypatch.setattr(register, "date", OtherDay)
    recording = harness.load(harness.CONTRACT_DIR / "wiki_register_component_tool.ok.json")
    harness.compare(recording["tool"], recording["result"], harness.run_case(contract_world, recording))


def test_volatile_values_are_replaced():
    value = {"a": "commit " + "a" * 40, "b": "2026-02-03T04:05:06+00:00 and 2026-02-03", "c": "/x/y/z/file"}
    out = harness.normalise(value, root="/x/y/z")
    assert out == {"a": "commit <sha>", "b": "<timestamp> and <date>", "c": "<root>/file"}


def test_only_the_product_version_fields_are_masked():
    out = harness.mask_product_versions(harness.normalise(
        {"bundles": [{"name": "base", "version": "0.3.0"}], "message": "listens on 127.0.0.1 and uses schema 2.4.1"}))
    assert out["bundles"] == [{"name": "base", "version": "<version>"}]
    assert out["message"] == "listens on 127.0.0.1 and uses schema 2.4.1"


def test_every_registered_tool_has_a_contract():
    async def names():
        return {t.name for t in await server.app.list_tools()}
    recorded = {harness.load(p)["tool"] for p in harness.recording_files()}
    assert asyncio.run(names()) == recorded


def test_every_recording_file_name_matches_its_tool():
    for path in harness.recording_files():
        assert path.name.startswith(harness.load(path)["tool"] + "."), path.name


def test_nothing_regenerates_a_recording_during_a_test_run():
    here = Path(__file__).resolve().parents[1]
    importers = []
    for path in here.rglob("test_*.py"):
        text = path.read_text(encoding="utf-8")
        if path.name != "test_harness.py" and ("contracts.record" in text or "import record" in text):
            importers.append(str(path.relative_to(here)))
    assert importers == []
    env = {**os.environ, "PYTEST_CURRENT_TEST": "x"}
    env.pop("CI", None)
    done = subprocess.run([sys.executable, str(harness.CONTRACT_DIR / "record.py"), "--write"],
                          env=env, capture_output=True, text=True)
    assert done.returncode == 2


# The tools that list a directory walk.  The walk order is the file system's, so the same instance
# gave a different order on macOS, Linux 3.11 and Linux 3.12 (GitHub Actions run 43727526573).
WALKING_RECORDINGS = ["wiki_inventory_tool.ok", "wiki_freshness_tool.ok"]
SHUFFLE_SEED = 20261115  # fixed; the instance has 12 wiki pages and 3 components, so the walk lists 12 files


def _walk_in(order, monkeypatch):
    """Make `Path.rglob` and `Path.glob` return their results reversed, or shuffled with SHUFFLE_SEED."""
    import random

    rng = random.Random(SHUFFLE_SEED)

    def patch(real):
        def walk(self, pattern, *args, **kwargs):
            found = list(real(self, pattern, *args, **kwargs))
            if order == "reversed":
                found.reverse()
            else:
                rng.shuffle(found)
            return iter(found)
        return walk

    monkeypatch.setattr(Path, "rglob", patch(Path.rglob))
    monkeypatch.setattr(Path, "glob", patch(Path.glob))


@pytest.mark.parametrize("name", WALKING_RECORDINGS)
@pytest.mark.parametrize("order", ["reversed", "shuffled"])
def test_a_recording_does_not_pin_the_directory_order(contract_world, monkeypatch, name, order):
    recording = harness.load(harness.CONTRACT_DIR / (name + ".json"))
    _walk_in(order, monkeypatch)
    harness.compare(recording["tool"], recording["result"], harness.run_case(contract_world, recording))


def test_the_directory_order_test_can_fail(contract_world, monkeypatch):
    """Without the sort in the harness the reversed walk differs from the recording (the test above has teeth)."""
    recording = harness.load(harness.CONTRACT_DIR / "wiki_inventory_tool.ok.json")
    monkeypatch.setattr(harness, "UNORDERED_LISTS", {})
    _walk_in("reversed", monkeypatch)
    actual = harness.run_case(contract_world, recording)
    with pytest.raises(AssertionError, match=r"wiki_inventory_tool: result\.all_files\[0\]"):
        harness.compare(recording["tool"], recording["result"], actual)
