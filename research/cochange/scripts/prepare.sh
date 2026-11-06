#!/usr/bin/env bash
# Pick the cut commit T (~182 days before HEAD, on HEAD's first-parent line),
# check T out in a worktree, and build the v8 code graph there.
# Usage: prepare.sh <repos_dir> <worktrees_dir> <repo-name> <results_dir>
set -euo pipefail
REPOS=$1; WT=$2; R=$3; OUT=$4
GRAPHIFY_SRC=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$REPOS/$R"
HEAD_SHA=$(git rev-parse HEAD)
since=$(date -d "$(git log -1 --format=%cI HEAD) -182 days" -I)
T=$(git rev-list -1 --first-parent --before="$since" HEAD)
mkdir -p "$WT" "$OUT"
[ -d "$WT/$R" ] || git worktree add -q --detach "$WT/$R" "$T"
cd "$WT/$R"
start=$(date +%s.%N)
PYTHONHASHSEED=0 uv run --project "$GRAPHIFY_SRC" graphify update . --no-cluster > "$OUT/$R.graph_build.log" 2>&1
end=$(date +%s.%N)
python3 - "$OUT/$R.meta.json" "$R" "$HEAD_SHA" "$T" "$start" "$end" "$GRAPHIFY_SRC" <<'PY'
import json, sys, subprocess
out, r, head, t, s, e, src = sys.argv[1:]
v8 = subprocess.run(["git", "-C", src, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
json.dump({"repo": r, "head": head, "cut": t, "graph_build_seconds": round(float(e) - float(s), 1),
           "graphify_commit": v8}, open(out, "w"), indent=2)
PY
echo "$R done: T=$T"
