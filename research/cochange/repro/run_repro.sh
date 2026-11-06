#!/usr/bin/env bash
# Before/after for the issue: `graphify affected` on a tiny scripted repo.
# Usage: V8=/path/to/graphify-v8 BRANCH=/path/to/graphify-feature run_repro.sh <work_dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W=$1; rm -rf "$W"; mkdir -p "$W"
for side in v8 branch; do
  src=$([ $side = v8 ] && echo "$V8" || echo "$BRANCH")
  "$HERE/make_repo.sh" "$W/$side" > /dev/null
  (cd "$W/$side" && uv run --frozen --project "$src" graphify update . > update.log 2>&1 &&
   echo "\$ graphify affected app/pricing.py    # $side" &&
   uv run --frozen --project "$src" graphify affected app/pricing.py 2>/dev/null) > "$W/$side.txt"
done
cat "$W/v8.txt"; echo; cat "$W/branch.txt"
