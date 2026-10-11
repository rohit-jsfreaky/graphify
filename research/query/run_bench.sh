#!/usr/bin/env bash
# usage: run_bench.sh LABEL GRAPHIFY_SRC_DIR GRAPHS_DIR [extra benchmark args]
# Runs `graphify benchmark <graph> --questions <file> --json` for every repo with the
# graphify package imported from GRAPHIFY_SRC_DIR (a PR worktree with the
# benchmark commits cherry-picked), writing results/LABEL/<repo>.json.
set -euo pipefail
label=$1; src=$2; graphs=$3; shift 3
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$here/results/$label"
for q in "$here"/questions/*.jsonl; do
  repo=$(basename "$q" .jsonl)
  (cd /tmp && PYTHONPATH="$src" uv run -q --frozen --project /home/user/graphify python -m graphify benchmark \
     "$graphs/$repo.json" --questions "$q" --json "$@" </dev/null) > "$here/results/$label/$repo.json" \
     || echo "FAILED $label $repo" >&2
done
uv run -q --frozen --project /home/user/graphify python "$here/aggregate.py" "$here/results/$label"
