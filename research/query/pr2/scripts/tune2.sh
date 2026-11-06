#!/usr/bin/env bash
# usage: [PR2_* env] tune2.sh LABEL SRC   -> Django-only run of query_graph from SRC on graphs_pr2
S=/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad; here=$S/rq
cd /tmp && PYTHONPATH="$2" uv run -q --frozen --project /home/user/graphify python "$here/evalset.py" "$1" query_graph \
  "$S/graphs_pr2" "$S/graphs_pr2" "$S/repos" '{}' tune </dev/null 2>/dev/null
python3 -c "
import json; r=[json.loads(x) for x in open('$here/results2/$1.jsonl')]; h=lambda k:sum(1 for x in r if x['rank'] is not None and x['rank']<k)
t=sorted(x['tokens'] for x in r); print('$1', len(r), 'top1',h(1),'top3',h(3),'top5',h(5),'any',sum(x['rank'] is not None for x in r),'tok',t[len(t)//2])"
