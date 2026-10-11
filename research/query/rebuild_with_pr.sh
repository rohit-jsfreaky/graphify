#!/usr/bin/env bash
# usage: rebuild_with_pr.sh N WT_ROOT REPOS_DIR OUT_GRAPHS_DIR
# For PRs that change extraction: rebuild every repo's graph with that PR's
# graphify (`graphify update .`, no cache), copy graph.json out, restore v8's graphify-out.
set -u
n=$1; wt=$2/pr-$n; repos=$3; out=$4; mkdir -p "$out"
for r in django pytest sphinx astropy requests pylint xarray seaborn flask; do
  cd "$repos/$r"; mv graphify-out graphify-out.v8
  PYTHONPATH="$wt" uv run -q --frozen --project /home/user/graphify python -m graphify update . </dev/null >/dev/null 2>&1 || echo "FAILED rebuild pr-$n $r" >&2
  cp graphify-out/graph.json "$out/$r.json" 2>/dev/null; rm -rf graphify-out; mv graphify-out.v8 graphify-out
done
