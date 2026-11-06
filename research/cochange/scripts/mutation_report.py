"""Tables for mutation.py. Usage: python mutation_report.py <results/mutation> [repos...]"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report import binom_two_sided  # noqa: E402

d = Path(sys.argv[1])
repos = sys.argv[2:] or ["click", "flask", "httpx"]
ROWS = [
    ("graph", "v8 `affected` (graph items)"),
    ("printed", "v8 + co-change, printed order (graph, then section)"),
    ("cc_first", "v8 + co-change, co-change first"),
    ("view10", "first 10 graph files + whole co-change section (what a reader sees)"),
    ("cochange", "co-change section only (conf >= 0.2, top 10)"),
    ("cochange_all", "co-change, no confidence floor (top 50)"),
    ("name_floor", "floor: test files whose name contains the module name"),
]


def lists(r):
    g, co = r["graph"], r["cochange"]
    return {
        "graph": g,
        "printed": g + [f for f in co if f not in g],
        "cc_first": co + [f for f in g if f not in co],
        "cochange": co,
        # not a ranking: k=10 and k=20 both read the first 10 graph files plus the section
        "view10": list(dict.fromkeys(g[:10] + co)),
        "cochange_all": r["cochange_all"],
        "name_floor": r["name_floor"],
    }


md = []
pooled = {k: [] for k, _ in ROWS}
pairs = []
for repo in repos:
    p = d / f"{repo}.mutation.jsonl.gz"
    if not p.exists():
        continue
    meta = json.loads((d / f"{repo}.mutation_meta.json").read_text())
    recs = [json.loads(line) for line in gzip.open(p, "rt")]
    killed = [r for r in recs if r["failing"] and r["failing"] != ["<suite did not run>"]]
    broken = sum(1 for r in recs if r["failing"] == ["<suite did not run>"])
    md.append(f"### {repo} @ {meta['commit'][:9]}: {meta['sampled']} functions mutated, {len(killed)} broke at least one test file "
              f"({broken} broke the whole suite, {len(recs) - len(killed) - broken} broke nothing); "
              f"{meta['test_files']} test files; co-change from {meta['cochange_commits_used']} commits before the commit "
              f"(mined in {meta['mine_seconds']} s); failing test files per mutant: "
              f"{sum(len(r['failing']) for r in killed) / max(1, len(killed)):.1f}\n")
    md.append("| predictor | recall@10 | recall@20 | hit@10 | mean list length |")
    md.append("|---|---|---|---|---|")
    for key, label in ROWS:
        vals = []
        for r in killed:
            lst = lists(r)[key]
            truth = set(r["failing"])
            k10, k20 = (len(lst), len(lst)) if key == "view10" else (10, 20)
            vals.append((sum(f in truth for f in lst[:k10]) / len(truth),
                         sum(f in truth for f in lst[:k20]) / len(truth),
                         1.0 if any(f in truth for f in lst[:k10]) else 0.0, len(lst)))
        pooled[key] += vals
        m = [sum(c) / len(c) for c in zip(*vals)] if vals else [float("nan")] * 4
        md.append(f"| {label} | {m[0]:.3f} | {m[1]:.3f} | {m[2]:.3f} | {m[3]:.1f} |")
    for r in killed:
        L = lists(r)
        truth = set(r["failing"])
        pairs.append((any(f in truth for f in L["cc_first"][:10]), any(f in truth for f in L["graph"][:10]),
                      any(f in truth for f in L["view10"])))
    md.append("")
md.append(f"### All repos pooled ({len(pairs)} killed mutants)\n")
md.append("| predictor | recall@10 | recall@20 | hit@10 |")
md.append("|---|---|---|---|")
for key, label in ROWS:
    v = pooled[key]
    m = [sum(c) / len(c) for c in zip(*v)] if v else [float("nan")] * 4
    md.append(f"| {label} | {m[0]:.3f} | {m[1]:.3f} | {m[2]:.3f} |")
a = sum(1 for c, g, _ in pairs if c and not g)
b = sum(1 for c, g, _ in pairs if g and not c)
a2 = sum(1 for _, g, pr in pairs if pr and not g)
b2 = sum(1 for _, g, pr in pairs if g and not pr)
md.append("")
md.append(f"McNemar on hit@10, co-change first vs v8: only co-change-first hits {a}, only v8 hits {b}, p = {binom_two_sided(a, b):.2g}")
md.append(f"McNemar, first 10 graph files + section vs v8 top 10: only the section view hits {a2}, only v8 hits {b2}, p = {binom_two_sided(a2, b2):.2g}")
md.append("")
md.append("The printed order (graph, then section) equals v8 at k = 10 and 20 whenever the graph list is longer than k, which it usually is here.")
(d / "tables_mutation.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
