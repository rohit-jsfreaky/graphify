#!/usr/bin/env bash
# Before/after for the ranking PR. Usage: V8=<graphify v8> BRANCH=<graphify ranking branch> run_repro_ranking.sh <work_dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=$1; rm -rf "$W"; mkdir -p "$W"
for side in v8 branch; do
  src=$([ $side = v8 ] && echo "$V8" || echo "$BRANCH")
  "$HERE/make_repo_ranking.sh" "$W/$side"
  (cd "$W/$side" && uv run --frozen --project "$src" graphify update . > update.log 2>&1 &&
   echo "\$ graphify affected core.py    # $side" &&
   uv run --frozen --project "$src" graphify affected core.py 2>/dev/null) > "$W/$side.txt"
done
cat "$W/v8.txt"; echo; cat "$W/branch.txt"
