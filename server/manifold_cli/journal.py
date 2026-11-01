# SPDX-License-Identifier: Apache-2.0
"""A journal of what ``manifold init`` created, so a failed run can undo exactly that and nothing else.

Every step records what it is about to create *before* creating it.  ``undo`` walks the entries in
reverse order and removes only paths this run made (never a folder or file that existed before the
run, never the content of one).  A file that the run only appended to is restored to its earlier
text.  Standard library only.
"""

import shutil
from pathlib import Path
from typing import Callable, List, Optional, Tuple

CREATED = "created"      # a file or folder that did not exist; removed on undo
RESTORE = "restore"      # a file that existed; its earlier text is put back on undo
ACTION = "action"        # something to run on undo (for example: stop the service)


class Journal:
    def __init__(self) -> None:
        self.entries: List[Tuple[str, object, object]] = []

    def created(self, path) -> None:
        """Note a path the run is about to create. Call before creating it, and only if it does not exist."""
        path = Path(path)
        if path.exists() or path.is_symlink():
            raise FileExistsError("%s already exists; init does not overwrite it." % path)
        self.entries.append((CREATED, path, None))

    def restore(self, path, earlier_text: str) -> None:
        """Note a file the run is about to change; undo puts ``earlier_text`` back."""
        self.entries.append((RESTORE, Path(path), earlier_text))

    def action(self, description: str, run: Callable[[], None]) -> None:
        """Note something to do on undo, in reverse order with the rest (for example, stop the service)."""
        self.entries.append((ACTION, description, run))

    def paths(self) -> List[Path]:
        return [entry[1] for entry in self.entries if entry[0] == CREATED]

    def undo(self, say: Optional[Callable[[str], None]] = None) -> List[str]:
        """Undo every entry, newest first; returns the problems met (undo goes on past a failure)."""
        problems: List[str] = []
        for kind, what, extra in reversed(self.entries):
            try:
                if kind == CREATED:
                    path = Path(what)
                    if path.is_symlink() or path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        shutil.rmtree(path)
                    if say:
                        say("removed %s" % path)
                elif kind == RESTORE:
                    Path(what).write_text(extra, encoding="utf-8")
                    if say:
                        say("restored %s" % what)
                elif kind == ACTION:
                    extra()
                    if say:
                        say(str(what))
            except Exception as exc:  # undo must go on; the caller reports what is left
                problems.append("could not undo %s: %s" % (what, exc))
        self.entries = []
        return problems
