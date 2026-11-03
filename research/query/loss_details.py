"""For questions where system A (default BM25-files) hits top-5 and system B (default the
prototype) misses, print the facts needed to name the cause.

usage: PYTHONPATH=<v8> python loss_details.py A_LABEL B_LABEL SET [REPO_FILTER]
SET: lite_nondjango | verified | all_nondjango
"""
import json, sys
from collections import defaultdict
from pathlib import Path
here = Path(__file__).parent; sys.path.insert(0, str(here))
import graphify.serve as s
import proto, bm25_files as B
from evalset import groups, GitReader

S = "/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad"
a_lab, b_lab, which = sys.argv[1:4]
load = lambda l: {r["id"]: r for r in map(json.loads, open(here / f"results2/{l}.jsonl"))}
A, Bres = load(a_lab), load(b_lab)
hit = lambda r: r is not None and r < 5
def inset(r):
    if r["repo"] == "django": return False
    return {"lite_nondjango": r["set"] == "lite", "verified": r["set"] == "verified", "all_nondjango": True}[which]
ids = {i for i in A if inset(A[i]) and i in Bres and hit(A[i]["rank"]) and not hit(Bres[i]["rank"])}
print(len(ids), "losses")
for (repo, commit, gpath, qset), qs in groups(f"{S}/graphs", f"{S}/graphs_ext").items():
    qs = [q for q in qs if q["id"] in ids]
    if not qs: continue
    G = s._load_graph(gpath); read = GitReader(Path(S) / "repos" / repo, commit)
    idx = proto.NodeBM25(proto.node_docs(G, read))
    nfiles = len({d.get("source_file") for _, d in G.nodes(data=True) if d.get("source_file")})
    for q in qs:
        qw = set(B.tokens(q["question"]))
        raw = idx.score(B.tokens(q["question"]))
        dem = {n: v * proto.demote_factor(G, n, qw) for n, v in raw.items()}
        def frank(sc, pooled):
            per = defaultdict(list)
            for n, v in sc.items(): per[G.nodes[n].get("source_file") or ""].append(v)
            key = (lambda f: -(max(per[f]) + 0.3 * sum(sorted(per[f])[:-1][-5:]))) if pooled else (lambda f: -max(per[f]))
            order = sorted(per, key=key)
            return next((i for i, f in enumerate(order) if f in q["files"]), None), order[:5]
        gold = q["files"][0]
        gnodes = [n for n, d in G.nodes(data=True) if d.get("source_file") in q["files"]]
        txt = read(gold) or ""
        body_hits = sorted(qw & set(B.tokens(txt)))
        node_hits = sorted(qw & {t for n in gnodes for t in B.tokens(G.nodes[n].get("label") or "")})
        r_raw, _ = frank(raw, True); r_dem, top = frank(dem, True); r_max, _ = frank(dem, False)
        print(f"\n{q['id']} [{repo}, {nfiles} files] {q['question'][:110]}")
        print(f"  gold {q['files']} ({len(gnodes)} nodes, {len(txt.splitlines())} lines); BM25-files rank {A[q['id']]['rank']}, proto rank {Bres[q['id']]['rank']}")
        print(f"  proto file rank: pooled+demoted {r_dem}, pooled no-demote {r_raw}, max-node only {r_max}; q-words in gold names {node_hits}; in gold text {body_hits}")
        print(f"  proto top files: {top}")
        print(f"  BM25 top files:  {A[q['id']]['top_files'][:5]}")
    read.close()
