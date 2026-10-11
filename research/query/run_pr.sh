#!/usr/bin/env bash
# usage: run_pr.sh N WT_ROOT GRAPHS_DIR  -> results/pr-N/*.json + summary
set -u
n=$1; root=$2; graphs=$3; here=$(cd "$(dirname "$0")" && pwd); wt=$root/pr-$n
if grep -q "def run_answer_benchmark" "$wt/graphify/benchmark.py" 2>/dev/null; then
  "$here/run_bench.sh" pr-$n "$wt" "$graphs"
else
  mkdir -p "$here/results/pr-$n"
  for q in "$here"/questions/*.jsonl; do repo=$(basename "$q" .jsonl)
    (cd /tmp && PYTHONPATH="$wt" uv run -q --frozen --project /home/user/graphify python "$here/bench_driver.py" "$graphs/$repo.json" "$q" </dev/null) \
      > "$here/results/pr-$n/$repo.json" 2>"$here/results/pr-$n/$repo.err" || echo "FAILED pr-$n $repo: $(tail -1 "$here/results/pr-$n/$repo.err")" >&2
  done
  uv run -q --frozen --project /home/user/graphify python "$here/aggregate.py" "$here/results/pr-$n"
fi
