# SPDX-License-Identifier: Apache-2.0
"""Every recorded tool contract still holds (PHASE_4_PLAN Tasks 17 and 18, INT-2 S1).

One test per recording file.  A failure names the tool and the field that differs.  To change a
contract on purpose, re-record by hand with `python server/tests/contracts/record.py --write` and
review the diff.
"""

import pytest

from tests.contracts import harness

RECORDINGS = harness.recording_files()


def test_there_are_recordings():
    assert len(RECORDINGS) >= 30


@pytest.mark.parametrize("path", RECORDINGS, ids=lambda p: p.stem)
def test_the_tool_still_matches_its_recording(contract_world, path):
    recording = harness.load(path)
    actual = harness.run_case(contract_world, recording)
    harness.compare(recording["tool"], recording["result"], actual)
