#!/usr/bin/env bash
# Failing-tests answer key. Usage: GRAPHIFY_SRC=<feature checkout> run_mutation.sh <mut_dir>
# <mut_dir> holds clones click/ flask/ httpx/ each with a .venv that can run its tests.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT="$HERE/../results/mutation"; M=$1
SRC=${GRAPHIFY_SRC:?}
mkdir -p "$OUT"
for r in click flask httpx; do
  case $r in click) s=src/click;; flask) s=src/flask;; httpx) s=httpx;; esac
  (cd "$M/$r" && PYTHONHASHSEED=0 uv run --frozen --project "$SRC" graphify update . --no-cluster > "$OUT/$r.update.log" 2>&1)
  PYTHONHASHSEED=0 uv run --frozen --project "$SRC" python "$HERE/mutation.py" "$M/$r" "$M/$r/.venv/bin/python" "$s" "$OUT" "$r" 40 2026 > "$OUT/$r.log" 2>&1
  rm -f "$M/httpx/test"  # httpx's own test_download leaves this file behind
done
uv run --frozen --project "$SRC" python "$HERE/mutation_report.py" "$OUT"
