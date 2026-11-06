"""File order of `affected` for the study's 2,070 commit queries, with whatever
graphify checkout runs this (used for the ranking PR: run once under v8, once
under the branch, then compare with bench_order_compare.py).

Graphs: <worktrees>/<repo>/graphify-out/graph.json at the cut commit T.
Usage: python bench_order.py <results_dir> <worktrees_dir> <label>
"""
import gzip
import json
import sys
from pathlib import Path

from graphify.affected import affected_nodes, load_graph, resolve_seed

res, wts, label = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
out = {}
for r in ["django", "flask", "requests", "hono", "jsoup", "caddy"]:
    g = load_graph(wts / r / "graphify-out" / "graph.json")
    cache = {}
    rows = []
    for q in (json.loads(x) for x in gzip.open(res / f"{r}.queries.jsonl.gz", "rt")):
        seed_file = q["seed"]
        if seed_file not in cache:
            s = resolve_seed(g, seed_file, wts / r)
            files = []
            if s is not None:
                for h in affected_nodes(g, s):
                    f = g.nodes[h.node_id].get("source_file")
                    if f and f != seed_file and f not in files:
                        files.append(f)
            cache[seed_file] = files
        rows.append({"sha": q["sha"], "seed": seed_file, "truth": q["truth"], "files": cache[seed_file]})
    out[r] = rows
with gzip.open(res / f"order_{label}.json.gz", "wt", encoding="utf-8") as fh:
    json.dump(out, fh, sort_keys=True)
print(label, {r: len(v) for r, v in out.items()})
