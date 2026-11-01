# SPDX-License-Identifier: Apache-2.0
# Scratch experiment for PHASE_1_PLAN T1. Never imported by production code.
#
# Several processes insert rows into one SQLite file in the given folder and the
# script reports lost writes and lock errors.
#
# Host run:       python3 probe.py --dir /some/folder --mode wal
# Container run:  docker run --rm -v /some/folder:/data -v "$PWD":/probe python:3.12-slim \
#                     python /probe/probe.py --dir /data --mode wal
# Cases: (a) run the container command twice at once (two processes inside the
# container, standing in for the server and `compose exec`); (b) run the host
# command and the container command at once against the same folder.
import argparse
import multiprocessing
import os
import sqlite3
import sys
import time


def worker(path, mode, ident, count, out):
    errors = 0
    done = 0
    conn = sqlite3.connect(path, timeout=10)
    conn.execute("PRAGMA synchronous=FULL")
    for i in range(count):
        try:
            conn.execute("INSERT INTO t(worker, n) VALUES (?, ?)", (ident, i))
            conn.commit()
            done += 1
        except sqlite3.Error as exc:
            errors += 1
            sys.stderr.write("worker %s: %s\n" % (ident, exc))
        time.sleep(0.001)
    conn.close()
    out.put((ident, done, errors))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True)
    parser.add_argument("--mode", choices=["wal", "delete"], default="wal")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--count", type=int, default=200)
    parser.add_argument("--tag", default="p%d" % os.getpid())
    args = parser.parse_args()
    path = os.path.join(args.dir, "probe.db")
    # The journal mode is set once here (retrying while another probe sets up at
    # the same moment); workers only open the file. The mode persists in the file.
    for attempt in range(50):
        try:
            setup = sqlite3.connect(path, timeout=10)
            setup.execute("PRAGMA journal_mode=%s" % args.mode)
            setup.execute("CREATE TABLE IF NOT EXISTS t(id INTEGER PRIMARY KEY, worker TEXT, n INTEGER)")
            setup.commit()
            setup.close()
            break
        except sqlite3.OperationalError:
            time.sleep(0.1)
    out = multiprocessing.Queue()
    procs = [
        multiprocessing.Process(target=worker, args=(path, args.mode, "%s-%d" % (args.tag, w), args.count, out))
        for w in range(args.workers)
    ]
    for p in procs:
        p.start()
    results = [out.get() for _ in procs]
    for p in procs:
        p.join()
    expected = sum(r[1] for r in results)
    errors = sum(r[2] for r in results)
    conn = sqlite3.connect(path, timeout=10)
    found = conn.execute("SELECT COUNT(*) FROM t WHERE worker LIKE ?", (args.tag + "-%",)).fetchone()[0]
    check = conn.execute("PRAGMA integrity_check").fetchone()[0]
    conn.close()
    print("tag=%s mode=%s acknowledged=%d found=%d lost=%d lock_errors=%d integrity=%s"
          % (args.tag, args.mode, expected, found, expected - found, errors, check))
    return 0 if (expected == found and errors == 0 and check == "ok") else 1


if __name__ == "__main__":
    sys.exit(main())
