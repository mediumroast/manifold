#!/usr/bin/env bash
# Helper for the live protocol. Run from anywhere.
#
#   lp.sh <client> ready              commit the installed bundle in all three repositories and mark the baseline
#   lp.sh <client> reset <repo>       put <repo> back to the baseline (repo: product | quality | manifold)
#   lp.sh <client> evidence <label>   save git status, diff and log of all repositories under evidence/<label>/,
#                                     then digest the agent sessions and judge the checks that can be judged (task8, dogfood)
#   lp.sh <client> where              print the folders
#
# <client> is claude or copilot. Everything lives under ~/manifold-live/<client>/ (set LIVE_ROOT to change the parent).
set -euo pipefail

CLIENT="${1:-}"; CMD="${2:-}"; ARG="${3:-}"
case "$CLIENT" in claude|copilot) ;; *) echo "usage: $0 claude|copilot ready|reset <repo>|evidence <label>|where" >&2; exit 2 ;; esac
ROOT="${LIVE_ROOT:-$HOME/manifold-live}/$CLIENT"
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -d "$ROOT" ] || { echo "$ROOT does not exist. Run setup.sh $CLIENT first." >&2; exit 1; }

case "$CMD" in
  where)
    ls -d "$ROOT"/*/ ;;

  ready)
    # Every reset returns a repository to this baseline and wipes whatever an agent wrote after it. An
    # agent that is asked to record the test command would otherwise ask again after every reset, so the
    # confirmed commands go into the baseline itself (the quality repository has none yet: the planner asks).
    seed() {  # $1 repo, $2 test command, $3 verify command or "none"
      python3 - "$ROOT/$1/AGENTS.md" "$2" "$3" <<'PY'
import sys, re
path, test, verify = sys.argv[1:4]
text = open(path).read()
if "(confirmed for the protocol)" not in text:
    add = "\n- **test:** `%s` (confirmed for the protocol)\n- **build, verify (lint / type-check):** %s\n" % (test, ("`%s` (confirmed for the protocol)" % verify) if verify != "none" else "none configured")
    text = re.sub(r"(## Project commands\n)", lambda m: m.group(1) + add, text, count=1)
    open(path, "w").write(text)
PY
    }
    seed product "cd mcp-server && ../.venv/bin/python -m pytest -q ." none
    seed manifold ".venv/bin/python -m pytest -q bundles/base/tests" ".venv/bin/python bundles/base/tools/build.py --check"
    for r in product quality manifold; do
      cd "$ROOT/$r"
      if [ -n "$(git status --porcelain)" ]; then
        git add -A
        git commit -q -m "chore: install the manifold bundle (protocol baseline)"
      fi
      git tag -f protocol-ready >/dev/null
      echo "$r: baseline is $(git rev-parse --short HEAD) on $(git branch --show-current)"
    done
    cd "$ROOT/product"
    git checkout -q review-target
    git rebase -q live-protocol                 # the review branch must carry the installed agents too
    git tag -f protocol-review-target >/dev/null
    git checkout -q live-protocol
    echo "product: review-target rebased onto the baseline" ;;

  reset)
    case "$ARG" in product|quality|manifold) ;; *) echo "reset needs: product | quality | manifold" >&2; exit 2 ;; esac
    cd "$ROOT/$ARG"
    BASE=live-protocol; [ "$ARG" = quality ] && BASE=main
    git checkout -q -f "$BASE"
    git reset -q --hard protocol-ready
    git clean -qfd                               # .venv is ignored, so it survives
    if [ "$ARG" = product ]; then git branch -q -f review-target protocol-review-target; fi
    echo "$ARG: back to the baseline ($(git rev-parse --short HEAD)), working tree clean" ;;

  evidence)
    [ -n "$ARG" ] || { echo "evidence needs a label, for example task2" >&2; exit 2; }
    OUT="$ROOT/evidence/$ARG"; mkdir -p "$OUT"
    for r in product quality manifold; do
      cd "$ROOT/$r"
      { echo "# branch: $(git branch --show-current)"; git status --short; } > "$OUT/$r.status.txt"
      git diff HEAD > "$OUT/$r.diff.patch" || true
      git log --oneline --decorate -12 > "$OUT/$r.log.txt"
      # new files are not in the diff; keep a copy of every untracked file
      git ls-files --others --exclude-standard | grep -v '^.venv/' > "$OUT/$r.untracked.txt" || true
      while IFS= read -r f; do mkdir -p "$OUT/$r.untracked/$(dirname "$f")"; if [ -L "$f" ]; then cp -P "$f" "$OUT/$r.untracked/$f"; elif [ -f "$f" ]; then cp "$f" "$OUT/$r.untracked/$f"; fi; done < "$OUT/$r.untracked.txt"
    done
    echo "saved to $OUT"
    # digest of the agent sessions, plus automatic verdicts for the tasks that have checks (task8, dogfood)
    python3 "$HERE/lp_verify.py" "$CLIENT" "$ARG" ;;

  *) echo "unknown command: $CMD" >&2; exit 2 ;;
esac
