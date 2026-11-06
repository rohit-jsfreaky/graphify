#!/usr/bin/env bash
# usage: build_one.sh SRC OUT_DIR REPO COMMIT KIND(lite|verified)  -- one fresh build (graphify-out wiped)
src=$1; out=$2; repo=$3; c=$4; kind=$5; mkdir -p "$out"
cd "$S_REPOS/$repo"; rm -f .git/index.lock; git checkout -q -f "$c" </dev/null; rm -rf graphify-out
PYTHONPATH="$src" uv run -q --frozen --project /home/user/graphify python -m graphify update . </dev/null >/dev/null 2>&1 || echo "BUILD FAILED $repo $c"
if [ "$kind" = lite ]; then f="$out/$repo.json"; else f="$out/$repo@${c:0:12}.json"; fi
cp graphify-out/graph.json "$f" && echo "built $f"
