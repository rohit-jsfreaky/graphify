#!/usr/bin/env bash
# Reproduce the whole study. Needs network (clones), git, uv.
# Usage: research/cochange/scripts/run_all.sh [work_dir]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../.." && pwd)
WORK=${1:-$HOME/cc-work}
OUT="$ROOT/research/cochange/results"
mkdir -p "$WORK/repos" "$OUT"
declare -A URL=(
  [django]=https://github.com/django/django.git
  [flask]=https://github.com/pallets/flask.git
  [requests]=https://github.com/psf/requests.git
  [hono]=https://github.com/honojs/hono.git
  [jsoup]=https://github.com/jhy/jsoup.git
  [caddy]=https://github.com/caddyserver/caddy.git
)
# HEAD commits used in the published run (pin them to reproduce exactly).
declare -A PIN=(
  [django]=d9d05f104e3187bd42b4bc288234ef1523a2cc73
  [flask]=49943b5a94413a530761350f04e896f76e8d620e
  [requests]=3c7baaa05ab4aa49cc819ce3a819d260de19c157
  [hono]=eb754bd5ef22c63f1634a4c374a86be086f85710
  [jsoup]=d90d57521d931db7bf7ee464a4c0a1a9293db088
  [caddy]=b3d67c861d0957f68566298227241a171db6e883
)
for r in django flask requests hono jsoup caddy; do
  [ -d "$WORK/repos/$r" ] || git clone -q --no-checkout "${URL[$r]}" "$WORK/repos/$r"
  git -C "$WORK/repos/$r" checkout -q --detach "${PIN[$r]}"
  "$HERE/prepare.sh" "$WORK/repos" "$WORK/worktrees" "$r" "$OUT"
  PYTHONHASHSEED=0 uv run --project "$ROOT" python "$HERE/evaluate.py" \
    "$WORK/repos/$r" "$WORK/worktrees/$r" "$OUT" "$r"
done
uv run --project "$ROOT" python "$HERE/report.py" "$OUT"
uv run --project "$ROOT" python "$HERE/examples.py" "$OUT" "$WORK/repos" > "$OUT/example_candidates.txt"
