# SPDX-License-Identifier: Apache-2.0
"""Write the contract recordings.  Run by hand, never by a test or CI (PHASE_4_PLAN Task 16).

    python server/tests/contracts/record.py --write

Without `--write` it prints this usage and writes nothing.  With the environment variable `CI` or
`PYTEST_CURRENT_TEST` set it exits with code 2 even with `--write`.  The recordings are then a
reviewed diff: read each changed file before committing it.  No test module imports this file.
"""

import json
import os
import sys
import tempfile
from pathlib import Path

USAGE = __doc__


def main(argv):
    if "--write" not in argv:
        print(USAGE)
        return 0
    if os.environ.get("CI") or os.environ.get("PYTEST_CURRENT_TEST"):
        print("refused: recordings are written by hand, not in CI or a test run", file=sys.stderr)
        return 2
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tests.contracts import harness
    from tests.contracts.cases import CASES

    written = 0
    for tool, name, case in CASES:
        with tempfile.TemporaryDirectory() as parent:
            world, _root = harness.open_world(parent, lambda k, v: os.environ.__setitem__(k, v))
            try:
                result = harness.run_case(world, {**case, "tool": tool})
            finally:
                world.conn.close()
        recording = {"tool": tool, "arguments": case["arguments"], "caller": case["caller"]}
        if case.get("files"):
            recording["files"] = case["files"]
        if case.get("setup"):
            recording["setup"] = case["setup"]
        recording["result"] = result
        target = harness.CONTRACT_DIR / ("%s.%s.json" % (tool, name))
        target.write_text(json.dumps(recording, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written += 1
    print("wrote %d recordings to %s" % (written, harness.CONTRACT_DIR))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
