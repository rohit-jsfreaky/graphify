"""Django-only diagnostic: for questions PR 2 misses, where does the gold file rank
(by best node) in the combined name+body scoring, and in body-tier-only scoring?"""
import json, sys, os
from collections import Counter
from pathlib import Path
here = Path(__file__).parent; sys.path.insert(0, str(here))
import graphify.serve as s
S = os.environ["S"]
res = {r["id"]: r for r in map(json.loads, open(here / f"results2/{sys.argv[1]}.jsonl"))}
G = s._load_graph(f"{S}/graphs_pr2/django.json")
bidx = s._get_body_index(G)
qs_ = [json.loads(l) for l in open(here / "questions/django.jsonl")]
c = Counter()
for q in qs_:
    r = res[q["id"]]
    if r["rank"] is not None and r["rank"] < 5: continue
    terms = s._query_terms(q["question"])
    sc = s._score_query(G, terms, collect_per_term_seeds=False, path_weight=s._query_path_weight(terms), body=True)
    def frank(ranked):
        seen = []
        for _, nid in ranked:
            f = G.nodes[nid].get("source_file") or ""
            if f not in seen: seen.append(f)
            if f in q["files"]: return len(seen) - 1
        return None
    norm = list(dict.fromkeys(t for x in terms for t in s._search_tokens(x)))
    body_only = sorted(((sum(1 for t in norm if t in w), nid) for nid, w in bidx["sets"].items()), key=lambda x: -x[0])[:3000]
    fr, fb = frank(sc.ranked), frank([(v, n) for v, n in body_only])
    c["combined<5" if fr is not None and fr < 5 else "combined>=5"] += 1
    c["bodycount<5" if fb is not None and fb < 5 else "bodycount>=5"] += 1
    print(q["id"], "combined file rank", fr, "| body-word-count file rank", fb, "| top", [G.nodes[n].get("label") for _, n in sc.ranked[:3]])
print(dict(c))
