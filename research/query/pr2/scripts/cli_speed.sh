#!/usr/bin/env bash
# usage: cli_speed.sh LABEL SRC GRAPH QUESTIONS.jsonl N
# Cold: each of the first N questions is a fresh `python -m graphify query "<q>" --graph GRAPH` process
# (CLI defaults); wall time per call. Prints per-call seconds and the median.
lab=$1; src=$2; graph=$3; qf=$4; n=$5
py=/home/user/graphify/.venv/bin/python
mapfile -t QS < <(head -n "$n" "$qf" | python3 -c "import json,sys; [print(json.loads(l)['question']) for l in sys.stdin]")
ts=()
for q in "${QS[@]}"; do
  s=$(date +%s.%N); (cd /tmp && PYTHONPATH="$src" "$py" -m graphify query "$q" --graph "$graph" >/dev/null 2>&1); e=$(date +%s.%N)
  ts+=("$(echo "$e - $s" | bc)")
done
printf "%s\n" "${ts[@]}" | python3 -c "
import sys,statistics; t=[float(x) for x in sys.stdin]; print('$lab cold: median %.2fs  min %.2fs  max %.2fs  (%d calls)' % (statistics.median(t), min(t), max(t), len(t)))"
