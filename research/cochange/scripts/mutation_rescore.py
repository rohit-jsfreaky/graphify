"""Re-score the 107 killed mutants with whatever graphify checkout runs this.

The truth (failing test files per mutant) comes from mutation.py and does not
depend on graphify, so changing `affected` needs no new test runs. For each
mutant this recomputes, with the running code:
  * graph files: `affected_nodes` from the CLI-resolved seed, mapped to files in
    the order the CLI prints them;
  * co-change files (only if graphify.git_cochange exists): `mine_cochange` from
    the commit BEFORE the tested one, with `corpus_filter`, then
    `cochange_partners` with the shipped defaults.
"before" is the graph order recorded by mutation.py on the first build (the v8
order, since that build did not change `affected`).

Usage: python mutation_rescore.py <results/mutation> <mut_dir> <label>
Writes <label>_<repo>.jsonl.gz and tables_<label>.md in <results/mutation>.
"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report import binom_two_sided  # noqa: E402

from graphify.affected import affected_nodes, load_graph, resolve_seed  # noqa: E402

try:
    from graphify.git_cochange import cochange_partners, corpus_filter, mine_cochange
except ImportError:  # e.g. the ranking branch, which has no co-change
    mine_cochange = None

res, mut, label = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
REPOS = ["click", "flask", "httpx"]


def files_in_cli_order(graph, seed_file, root):
    seed = resolve_seed(graph, seed_file, root)
    if seed is None:
        return []
    out = []
    for h in affected_nodes(graph, seed):
        f = graph.nodes[h.node_id].get("source_file")
        if f and f != seed_file and f not in out:
            out.append(f)
    return out


def metrics(lst, truth, k):
    return sum(f in truth for f in lst[:k]) / len(truth), 1.0 if any(f in truth for f in lst[:k]) else 0.0


rows_all = {}
md = []
for r in REPOS:
    meta = json.loads((res / f"{r}.mutation_meta.json").read_text())
    graph = load_graph(mut / r / "graphify-out" / "graph.json")
    co_data = None
    if mine_cochange is not None:
        co_data = mine_cochange(mut / r, rev=f"{meta['commit']}^", keep=corpus_filter(mut / r))
    out = []
    for rec in (json.loads(x) for x in gzip.open(res / f"{r}.mutation.jsonl.gz", "rt")):
        if not rec["failing"] or rec["failing"] == ["<suite did not run>"]:
            continue
        g = files_in_cli_order(graph, rec["file"], mut / r)
        co = [p["file"] for p in cochange_partners(co_data, rec["file"])] if co_data else []
        out.append({"file": rec["file"], "function": rec["function"], "failing": rec["failing"],
                    "before": rec["graph"], "graph": g, "cochange": co,
                    "same_set_as_before": set(g) == set(rec["graph"])})
    with gzip.open(res / f"{label}_{r}.jsonl.gz", "wt", encoding="utf-8") as fh:
        for o in out:
            fh.write(json.dumps(o, sort_keys=True) + "\n")
    rows_all[r] = out

views = {
    "before": lambda o: o["before"],
    "after": lambda o: o["cochange"] + [f for f in o["graph"] if f not in o["cochange"]],
    "graph_only_now": lambda o: o["graph"],
}
md.append(f"## {label}: 107 killed mutants, failing test files as truth\n")
md.append("| repo | mutants | view | R@10 | R@20 | hit@10 | section + first 10 graph files: R / hit / files shown |")
md.append("|---|---|---|---|---|---|---|")
pooled = {v: [] for v in views}
sec = []
for r in REPOS:
    out = rows_all[r]
    for v, fn in views.items():
        vals = [(*metrics(fn(o), set(o["failing"]), 10), metrics(fn(o), set(o["failing"]), 20)[0]) for o in out]
        pooled[v] += vals
        m = [sum(c) / len(c) for c in zip(*vals)]
        extra = ""
        if v == "after" and any(o["cochange"] for o in out):
            sv = []
            for o in out:
                shown = list(dict.fromkeys(o["graph"][:10] + o["cochange"]))
                t = set(o["failing"])
                sv.append((sum(f in t for f in shown) / len(t), 1.0 if t & set(shown) else 0.0, len(shown)))
            sec += sv
            s = [sum(c) / len(c) for c in zip(*sv)]
            extra = f"{s[0]:.3f} / {s[1]:.3f} / {s[2]:.1f}"
        md.append(f"| {r} | {len(out)} | {v} | {m[0]:.3f} | {m[2]:.3f} | {m[1]:.3f} | {extra} |")
for v in views:
    m = [sum(c) / len(c) for c in zip(*pooled[v])]
    extra = ""
    if v == "after" and sec:
        s = [sum(c) / len(c) for c in zip(*sec)]
        extra = f"{s[0]:.3f} / {s[1]:.3f} / {s[2]:.1f}"
    md.append(f"| pooled | {len(pooled[v])} | {v} | {m[0]:.3f} | {m[2]:.3f} | {m[1]:.3f} | {extra} |")
for v in ("after", "graph_only_now"):
    a = sum(1 for o in sum(rows_all.values(), []) if metrics(views[v](o), set(o["failing"]), 10)[1] and not metrics(o["before"], set(o["failing"]), 10)[1])
    b = sum(1 for o in sum(rows_all.values(), []) if not metrics(views[v](o), set(o["failing"]), 10)[1] and metrics(o["before"], set(o["failing"]), 10)[1])
    md.append(f"\nMcNemar hit@10, {v} vs before: only {v} {a}, only before {b}, p = {binom_two_sided(a, b):.2g}")
same = sum(o["same_set_as_before"] for o in sum(rows_all.values(), []))
md.append(f"\nGraph result SET identical to the recorded v8 set for {same} of {len(pooled['before'])} mutants.")
(res / f"tables_{label}.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
