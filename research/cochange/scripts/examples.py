"""List candidate examples: co-change wins over the graph, and co-change noise.

Usage: python examples.py <results_dir> <repos_dir>
"""
import gzip, json, subprocess, sys
from pathlib import Path

res, repos = Path(sys.argv[1]), Path(sys.argv[2])
qs = []
for p in sorted(res.glob("*.queries.jsonl.gz")):
    with gzip.open(p, "rt") as fh:
        qs += [json.loads(l) for l in fh]

def subj(repo, sha):
    return subprocess.run(["git", "-C", str(repos / repo), "log", "-1", "--format=%s", sha],
                          capture_output=True, text=True).stdout.strip()

print("# WINS: co-change top-10 finds a true file that v8 depth-2 never returns (any rank)")
seen = set()
for q in qs:
    cc10 = q["pred"]["cc_s2_3y"][:10]
    v8all = set(q["v8_d2_all_hits"])
    won = [f for f in cc10 if f in q["truth"] and f not in v8all]
    cats = {f: c for f, c in zip(q["truth"], q["truth_cat"])}
    noncode = [f for f in won if cats[f] in ("docs", "config", "other", "test")]
    if noncode and (q["repo"], cats[noncode[0]]) not in seen and len(won) >= 2:
        seen.add((q["repo"], cats[noncode[0]]))
        print(f"\n[{q['repo']}] {q['sha'][:10]} {subj(q['repo'], q['sha'])!r}\n  seed={q['seed']}\n  truth={q['truth']}"
              f"\n  v8_d2 top10={q['pred']['v8_d2'][:10]}\n  v8_d2 returns {q['v8_d2_size']} files, true among them: {q['v8_d2_all_hits']}"
              f"\n  cc top10 (conf)={[(f, q['cc_conf'].get(f)) for f in cc10]}\n  cc-only true hits={won}")

print("\n\n# NOISE: v8 hit@10 but co-change top-10 is all wrong / fusion lost the hit")
for q in qs:
    v8h = set(q["pred"]["v8_d2"][:10]) & set(q["truth"])
    ccw = [f for f in q["pred"]["cc_s2_3y"][:10] if f not in q["truth"]]
    fush = set(q["pred"]["comb_fusion"][:10]) & set(q["truth"])
    if v8h and (not fush or len(fush) < len(v8h)) and len(ccw) >= 5:
        print(f"\n[{q['repo']}] {q['sha'][:10]} {subj(q['repo'], q['sha'])!r}\n  seed={q['seed']}\n  truth={q['truth']}"
              f"\n  v8 top10 true={sorted(v8h)} fusion top10 true={sorted(fush)}"
              f"\n  cc top10 (conf)={[(f, q['cc_conf'].get(f)) for f in q['pred']['cc_s2_3y'][:10]]}"
              f"\n  fusion top10={q['pred']['comb_fusion'][:10]}")
