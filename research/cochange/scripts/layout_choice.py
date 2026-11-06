"""Which text/JSON layout to ship? Scores flat top-k orders on BOTH answer keys.

Inputs: results/built/<repo>.built_queries.jsonl.gz (commit key) and
results/mutation/cochange_v2_<repo>.jsonl.gz (failing-tests key), both from the
built feature. Usage: python layout_choice.py <results_dir>
"""
import gzip
import json
import sys
from pathlib import Path

res = Path(sys.argv[1])


def layouts(g, co):
    out = {"graph_only (v8)": g}
    for n in (3, 5, 10):
        c = co[:n]
        out[f"section capped at {n}, then graph"] = c + [f for f in g if f not in c]
    il, gi, ci = [], iter(g), iter(co)
    for _ in range(len(g) + len(co)):
        for it in (gi, ci):
            x = next(it, None)
            if x is not None and x not in il:
                il.append(x)
    out["interleave graph/co-change"] = il
    out["graph, then section (first build)"] = g + [f for f in co if f not in g]
    return out


def score(rows):
    names = list(rows[0][0])
    return {n: (sum(sum(f in t for f in L[n][:10]) / len(t) for L, t in rows) / len(rows),
                sum(bool(t & set(L[n][:10])) for L, t in rows) / len(rows)) for n in names}


com = {r: score([(layouts(q["graph"], q["cochange"]), set(q["truth"]))
                 for q in map(json.loads, gzip.open(res / "built" / f"{r}.built_queries.jsonl.gz", "rt"))])
       for r in ["django", "flask", "requests", "hono", "jsoup", "caddy"]}
mut = {r: score([(layouts(q["graph"], q["cochange"]), set(q["failing"]))
                 for q in map(json.loads, gzip.open(res / "mutation" / f"cochange_v2_{r}.jsonl.gz", "rt"))])
       for r in ["click", "flask", "httpx"]}
md = ["| layout (flat top 10) | commits R@10 / hit@10 (repo mean) | mutants R@10: click / flask / httpx | mutants R@10 / hit@10 (repo mean) |",
      "|---|---|---|---|"]
for n in com["django"]:
    cr = sum(com[r][n][0] for r in com) / len(com)
    ch = sum(com[r][n][1] for r in com) / len(com)
    mr = sum(mut[r][n][0] for r in mut) / len(mut)
    mh = sum(mut[r][n][1] for r in mut) / len(mut)
    md.append(f"| {n} | {cr:.3f} / {ch:.3f} | " + " / ".join(f"{mut[r][n][0]:.3f}" for r in mut) + f" | {mr:.3f} / {mh:.3f} |")
(res / "tables_layout_choice.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
