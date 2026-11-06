"""Ranking-only on the failing-tests key: same v8 set, sorted by distance then linking edges.
Usage: python mutation_ranking.py <results/mutation> <mut_dir>"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ranking_only import file_links, v8_files  # noqa: E402

from graphify.affected import load_graph  # noqa: E402

res, mut = Path(sys.argv[1]), Path(sys.argv[2])
md = ["| repo | killed mutants | v8 order R@10 | sorted R@10 | v8 order R@20 | sorted R@20 | v8 order hit@10 | sorted hit@10 | sorted + co-change first R@10 / hit@10 |",
      "|---|---|---|---|---|---|---|---|---|"]
pool = defaultdict(list)
for r in ["click", "flask", "httpx"]:
    g = load_graph(mut / r / "graphify-out" / "graph.json")
    by_file = defaultdict(list)
    for nid, d in g.nodes(data=True):
        if d.get("source_file"):
            by_file[str(d["source_file"])].append(str(nid))
    edges, _ = file_links(g)
    rows = []
    for rec in (json.loads(x) for x in gzip.open(res / f"{r}.mutation.jsonl.gz", "rt")):
        if not rec["failing"] or rec["failing"] == ["<suite did not run>"]:
            continue
        seed = rec["file"]
        order, best = v8_files(g, by_file, seed, mut / r)
        assert order == rec["graph"], (r, seed)

        def link(f):
            closer = {seed} if best[f] == 1 else {x for x, dx in best.items() if dx == best[f] - 1}
            return sum(edges.get((f, c), 0) for c in closer)
        srt = sorted(order, key=lambda f: (best[f], -link(f), f))
        both = rec["cochange"] + [f for f in srt if f not in rec["cochange"]]
        t = set(rec["failing"])
        m = lambda lst, k: sum(f in t for f in lst[:k]) / len(t)  # noqa: E731
        h = lambda lst: 1.0 if any(f in t for f in lst[:10]) else 0.0  # noqa: E731
        rows.append((m(order, 10), m(srt, 10), m(order, 20), m(srt, 20), h(order), h(srt), m(both, 10), h(both)))
    pool["all"] += rows
    a = [sum(c) / len(c) for c in zip(*rows)]
    md.append(f"| {r} | {len(rows)} | " + " | ".join(f"{x:.3f}" for x in a[:6]) + f" | {a[6]:.3f} / {a[7]:.3f} |")
a = [sum(c) / len(c) for c in zip(*pool["all"])]
md.append(f"| pooled | {len(pool['all'])} | " + " | ".join(f"{x:.3f}" for x in a[:6]) + f" | {a[6]:.3f} / {a[7]:.3f} |")
(res / "tables_mutation_ranking.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
