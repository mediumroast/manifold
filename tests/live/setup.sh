#!/usr/bin/env bash
# Build a fresh, isolated protocol tree for one client.
#
#   ./setup.sh claude     -> ~/manifold-live/claude/{bundle,product,quality,manifold}
#   ./setup.sh copilot    -> ~/manifold-live/copilot/{bundle,product,quality,manifold}
#
# Re-running deletes that client's tree and rebuilds it from nothing. Nothing
# here has a git remote, so nothing can be pushed. The bundle is NOT installed:
# the protocol makes you do that, because installing is part of what we test.
set -euo pipefail

CLIENT="${1:-}"
case "$CLIENT" in
  claude|copilot) ;;
  *) echo "usage: $0 claude|copilot" >&2; exit 2 ;;
esac

HERE="$(cd "$(dirname "$0")" && pwd)"
PRODUCT_SRC="${PRODUCT_SRC:?set PRODUCT_SRC to the product repository to copy (see tests/live/README.md)}"
PUBLIC_SRC="${PUBLIC_SRC:-$(cd "$HERE/../.." && pwd)}"          # this repository, on the branch under test
PRODUCT_BRANCH="${PRODUCT_BRANCH:-main}"
ROOT="${LIVE_ROOT:-$HOME/manifold-live}/$CLIENT"

echo "== Rebuilding $ROOT from nothing"
rm -rf "$ROOT"
mkdir -p "$ROOT"

git_id() { git -C "$1" config user.name "Live Protocol"; git -C "$1" config user.email "live@example.invalid"; }

echo "== 1/6 Build the bundle zip from $PUBLIC_SRC ($(git -C "$PUBLIC_SRC" branch --show-current))"
python3 "$PUBLIC_SRC/bundles/base/tools/build.py" --out "$ROOT/download" >/dev/null
unzip -q "$ROOT/download/manifold-base-0.1.0.zip" -d "$ROOT/unzipped"
# the zip may or may not wrap everything in one folder; normalize to $ROOT/bundle
if [ -f "$ROOT/unzipped/install.py" ]; then mv "$ROOT/unzipped" "$ROOT/bundle"
else mv "$ROOT/unzipped/$(ls "$ROOT/unzipped" | head -1)" "$ROOT/bundle"; fi

echo "== 2/6 Product repository (scratch clone of the product repository, branch $PRODUCT_BRANCH)"
git clone -q --branch "$PRODUCT_BRANCH" "$PRODUCT_SRC" "$ROOT/product"
git -C "$ROOT/product" remote remove origin
git_id "$ROOT/product"
git -C "$ROOT/product" checkout -q -b live-protocol
mkdir -p "$ROOT/product/intent" "$ROOT/product/docs/walkthroughs"
cp "$HERE/fixtures/INT-1-freshness-days-behind.md" "$ROOT/product/intent/"
cp "$HERE/fixtures/WT_001_freshness-filename-dates.md" "$ROOT/product/docs/walkthroughs/"
# The real repository may point editors at a running MCP server with real data.
# A scratch session must never be able to reach it.
[ -f "$ROOT/product/.vscode/mcp.json" ] && git -C "$ROOT/product" rm -q .vscode/mcp.json
git -C "$ROOT/product" add -A
git -C "$ROOT/product" commit -q -m "chore: plant protocol intent and walkthrough"
# branch for the reviewer task
git -C "$ROOT/product" checkout -q -b review-target
git -C "$ROOT/product" apply "$HERE/fixtures/review-target.patch"
git -C "$ROOT/product" add -A
git -C "$ROOT/product" commit -q -m "feat: skip directories in freshness (protocol fixture)"
git -C "$ROOT/product" checkout -q live-protocol

echo "== 3/6 Python environment for the product tests (needs network)"
python3 -m venv "$ROOT/product/.venv"
"$ROOT/product/.venv/bin/pip" install -q -r "$ROOT/product/mcp-server/requirements.txt" -r "$ROOT/product/mcp-server/requirements-dev.txt" 2>&1 | grep -v 'notice' || true
( cd "$ROOT/product/mcp-server" && ../.venv/bin/python -m pytest -q 2>&1 | tail -1 )

echo "== 4/6 Quality repository (empty on purpose)"
git init -q -b main "$ROOT/quality"
git_id "$ROOT/quality"
printf '# quality-scratch\n\nBehavior scenarios for the protocol product.\n' > "$ROOT/quality/README.md"
git -C "$ROOT/quality" add -A
git -C "$ROOT/quality" commit -q -m "chore: initial commit"

echo "== 5/6 Dogfood repository (scratch clone of manifold itself)"
git clone -q --branch "$(git -C "$PUBLIC_SRC" branch --show-current)" "$PUBLIC_SRC" "$ROOT/manifold"
git -C "$ROOT/manifold" remote remove origin
git_id "$ROOT/manifold"
git -C "$ROOT/manifold" checkout -q -b live-protocol
python3 -m venv "$ROOT/manifold/.venv"
"$ROOT/manifold/.venv/bin/pip" install -q pytest 2>&1 | grep -v notice || true
( cd "$ROOT/manifold" && .venv/bin/python -m pytest -q bundles/base/tests 2>&1 | tail -1 )
mkdir -p "$ROOT/manifold/intent"
cp "$HERE/fixtures/INT-1-installer-json-plan.md" "$ROOT/manifold/intent/"
git -C "$ROOT/manifold" add -A
git -C "$ROOT/manifold" commit -q -m "chore: plant protocol intent"

echo "== 6/6 Tag the starting point of each repository"
for r in product quality manifold; do git -C "$ROOT/$r" tag protocol-start; done

echo
echo "Ready: $ROOT"
echo "  bundle/    unzipped release asset (run install.py from here)"
echo "  product/   branch live-protocol (also: review-target), tests pass, bundle NOT installed"
echo "  quality/   empty repository, bundle NOT installed"
echo "  manifold/  dogfood repository, bundle NOT installed"
