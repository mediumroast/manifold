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


def test_a_renamed_field_in_one_tool_leaves_the_other_recordings_alone():
    recordings = {p.stem: harness.load(p) for p in harness.recording_files()}
    broken = copy.deepcopy(recordings["wiki_read_tool.ok"]["result"])
    broken["entity_tag"] = broken.pop("etag")
    for stem, recording in recordings.items():
        if recording["tool"] != "wiki_read_tool":
            harness.compare(recording["tool"], recording["result"], copy.deepcopy(recording["result"]))


def test_volatile_values_are_replaced():
    value = {"a": "commit " + "a" * 40, "b": "2026-02-03T04:05:06+00:00 and 2026-02-03", "c": "/x/y/z/file"}
    out = harness.normalise(value, root="/x/y/z")
    assert out == {"a": "commit <sha>", "b": "<timestamp> and <date>", "c": "<root>/file"}


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
