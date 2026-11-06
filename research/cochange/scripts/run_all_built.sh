#!/usr/bin/env bash
# Before/after benchmark of the BUILT feature. Same repos, cut commits and test
# commits as the study (results/<repo>.meta.json), but graph.json AND
# cochange.json are written by the feature branch's own `graphify update`, and
# predictions come from `affected_payload` (what `graphify affected --json` prints).
#
# Usage: GRAPHIFY_SRC=/path/to/graphify-on-claude-affected-cochange \
#        research/cochange/scripts/run_all_built.sh <repos_dir> <work_dir>
# <repos_dir> holds full clones named django flask requests hono jsoup caddy
# (run_all.sh creates them in <work>/repos).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT="$HERE/../results"
SRC=${GRAPHIFY_SRC:?set GRAPHIFY_SRC to a checkout of the feature branch}
REPOS=$1; WORK=$2
mkdir -p "$WORK" "$OUT/built"
for r in django flask requests hono jsoup caddy; do
  T=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['cut'])" "$OUT/$r.meta.json")
  cp "$OUT/$r.meta.json" "$OUT/built/$r.meta.json"
  [ -d "$WORK/$r" ] || git -C "$REPOS/$r" worktree add -q --detach "$WORK/$r" "$T"
  start=$(date +%s.%N)
  (cd "$WORK/$r" && PYTHONHASHSEED=0 uv run --frozen --project "$SRC" graphify update . --no-cluster > "$OUT/built/$r.update.log" 2>&1)
  end=$(date +%s.%N)
  echo "$r update_seconds=$(python3 -c "print(round($end-$start,1))")" | tee -a "$OUT/built/update_times.txt"
  PYTHONHASHSEED=0 uv run --frozen --project "$SRC" python "$HERE/bench_built.py" \
    "$REPOS/$r" "$WORK/$r" "$OUT/built" "$r"
done
uv run --frozen --project "$SRC" python "$HERE/bench_built_report.py" "$OUT/built"
