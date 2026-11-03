#!/usr/bin/env bash
# Grid over proto:bm25b_ff2 weights on the TUNE set only (Django). usage: tune.sh STAGE_NAME 'json1' 'json2' ...
here=$(cd "$(dirname "$0")" && pwd); stage=$1; shift
i=0; for p in "$@"; do i=$((i+1)); echo "$p" > "$here/results2/tune-$stage-$i.params"
  "$here/run_eval.sh" "tune-$stage-$i" proto:bm25b_ff2 "$p" "" tune 2>/dev/null &
  [ $((i % 3)) -eq 0 ] && wait; done; wait
for f in "$here"/results2/tune-$stage-*.params; do l=$(basename "$f" .params)
  python3 -c "
import json,sys; r=[json.loads(x) for x in open('$here/results2/$l.jsonl')]; h=lambda k:sum(1 for x in r if x['rank'] is not None and x['rank']<k)
t=sorted(x['tokens'] for x in r); print(f'{len(r)} top1={h(1)} top3={h(3)} top5={h(5)} tok={t[len(t)//2]}', open('$f').read().strip())"
done
