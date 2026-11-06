"""Ranking-only experiment: keep v8 `affected`'s exact result SET, change only the order.

For every study query (same 2,070 queries as evaluate.py) this recomputes the v8
`affected` file list at depth 2 (reverse edges only, unchanged), then compares:

  * bfs       - v8's current order (breadth-first discovery order)
  * dist_edges - graph distance first, then the number of linking edges from the
                 candidate file into the files one step closer to the seed
                 (the seed itself for depth 1), then path
  * dist_nodes - same, but counting distinct linking nodes instead of edges
  * edges_only - linking edges into the seed file only, ignoring distance

The set of files is identical in every variant, so recall over the full list does
not change; only recall@k does.

Usage: python ranking_only.py <results_dir> <worktrees_dir>
Writes <results_dir>/ranking_only.json and ranking_only.md
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from graphify.affected import DEFAULT_AFFECTED_RELATIONS, affected_nodes, load_graph, resolve_seed

REPOS = ["django", "flask", "requests", "hono", "jsoup", "caddy"]
KS = (5, 10, 20)


def file_links(g):
    rels = set(DEFAULT_AFFECTED_RELATIONS)
    edges: Counter = Counter()
    nodes: dict = defaultdict(set)
    for u, v, d in g.edges(data=True):
        if str(d.get("relation", "")) not in rels:
            continue
        fu, fv = g.nodes[u].get("source_file"), g.nodes[v].get("source_file")
        if fu and fv and fu != fv:
            edges[(fu, fv)] += 1          # fu depends on fv (the direction `affected` walks back)
            nodes[(fu, fv)].add(u)
    return edges, {k: len(v) for k, v in nodes.items()}


def v8_files(g, by_file, seed, root):
    s = resolve_seed(g, seed, root)
    seeds = [s] if s is not None and g.nodes[s].get("source_file") == seed else sorted(by_file.get(seed, []))
    best, order = {}, []
    for sd in seeds:
        for h in affected_nodes(g, sd, depth=2):
            f = g.nodes[h.node_id].get("source_file")
            if not f or f == seed:
                continue
            if f not in best:
                best[f] = h.depth
                order.append(f)
            else:
                best[f] = min(best[f], h.depth)
    if len(seeds) > 1:
        order.sort(key=lambda f: best[f])
    return order, best


def main():
    results, wts = Path(sys.argv[1]), Path(sys.argv[2])
    out = {}
    md = ["## Ranking only: same v8 result set, different order (depth 2)\n",
          "| repo | queries | order | R@5 | R@10 | R@20 | hit@10 | P@10 |", "|---|---|---|---|---|---|---|---|"]
    allrows = defaultdict(lambda: defaultdict(list))
    check_mismatch = 0
    for r in REPOS:
        g = load_graph(wts / r / "graphify-out" / "graph.json")
        root = wts / r
        by_file = defaultdict(list)
        for nid, d in g.nodes(data=True):
            if d.get("source_file"):
                by_file[str(d["source_file"])].append(str(nid))
        edges, lnodes = file_links(g)
        rows = defaultdict(list)
        cache = {}
        with gzip.open(results / f"{r}.queries.jsonl.gz", "rt") as fh:
            qs = [json.loads(line) for line in fh]
        for q in qs:
            seed = q["seed"]
            if seed not in cache:
                cache[seed] = v8_files(g, by_file, seed, root)
            order, best = cache[seed]
            # the study filtered to files that existed at T; graph files all exist at T
            if order[:20] != q["pred"]["v8_d2"][:20]:
                check_mismatch += 1

            def link(f, counts):
                d = best[f]
                closer = {seed} if d == 1 else {x for x, dx in best.items() if dx == d - 1}
                return sum(counts.get((f, c), 0) for c in closer)

            variants = {
                "bfs": order,
                "dist_edges": sorted(order, key=lambda f: (best[f], -link(f, edges), f)),
                "dist_nodes": sorted(order, key=lambda f: (best[f], -link(f, lnodes), f)),
                "edges_only": sorted(order, key=lambda f: (-edges.get((f, seed), 0), best[f], f)),
            }
            truth = set(q["truth"])
            for name, lst in variants.items():
                vals = []
                for k in KS:
                    h = sum(1 for f in lst[:k] if f in truth)
                    vals += [h / len(truth), h / k, 1.0 if h else 0.0]
                rows[name].append(vals)
        out[r] = {}
        for name, vals in rows.items():
            m = [sum(c) / len(c) for c in zip(*vals)]
            out[r][name] = {"R@5": m[0], "R@10": m[3], "R@20": m[6], "P@10": m[4], "hit@10": m[5], "n": len(vals)}
            allrows[name]["R@5"].append(m[0]); allrows[name]["R@10"].append(m[3]); allrows[name]["R@20"].append(m[6])
            allrows[name]["hit@10"].append(m[5]); allrows[name]["P@10"].append(m[4])
            md.append(f"| {r} | {len(vals)} | {name} | {m[0]:.3f} | {m[3]:.3f} | {m[6]:.3f} | {m[5]:.3f} | {m[4]:.3f} |")
    out["ALL (repo mean)"] = {n: {k: sum(v) / len(v) for k, v in d.items()} for n, d in allrows.items()}
    for name, d in out["ALL (repo mean)"].items():
        md.append(f"| ALL (repo mean) | 2070 | {name} | {d['R@5']:.3f} | {d['R@10']:.3f} | {d['R@20']:.3f} | {d['hit@10']:.3f} | {d['P@10']:.3f} |")
    md.append(f"\nSanity check: queries whose recomputed v8 top-20 differs from the study's stored v8 top-20: {check_mismatch}\n")
    (results / "ranking_only.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    (results / "ranking_only.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
