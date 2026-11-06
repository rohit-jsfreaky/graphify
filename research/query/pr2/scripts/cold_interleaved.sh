#!/usr/bin/env bash
# usage: cold_interleaved.sh QUESTIONS.jsonl N LABEL=SRC=GRAPH [LABEL=SRC=GRAPH ...]
# For each of the first N questions, run one fresh `python -m graphify query "<q>" --graph GRAPH`
# process per version, alternating versions call by call. Wall time per call; median per version.
qf=$1; n=$2; shift 2; py=/home/user/graphify/.venv/bin/python
mapfile -t QS < <(head -n "$n" "$qf" | python3 -c "import json,sys; [print(json.loads(l)['question']) for l in sys.stdin]")
declare -A T
for q in "${QS[@]}"; do
  for spec in "$@"; do lab=${spec%%=*}; rest=${spec#*=}; src=${rest%%=*}; graph=${rest#*=}
    s=$(date +%s.%N); (cd /tmp && PYTHONPATH="$src" "$py" -m graphify query "$q" --graph "$graph" >/dev/null 2>&1); e=$(date +%s.%N)
    T[$lab]+="$(echo "$e - $s" | bc) "
  done
done
for spec in "$@"; do lab=${spec%%=*}
  echo "${T[$lab]}" | python3 -c "
import sys,statistics; t=[float(x) for x in sys.stdin.read().split()]; print('$lab cold: median %.2fs  min %.2fs  max %.2fs  (%d calls) ' % (statistics.median(t), min(t), max(t), len(t)) + ' '.join('%.2f'%x for x in t))"
done
