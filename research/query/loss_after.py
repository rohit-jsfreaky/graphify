"""Post-hoc (no changes made after this): held-out questions where BM25-files hits top-5
and the TUNED prototype does not. Prints the facts used to name each cause.
usage: PYTHONPATH=<v8> python loss_after.py"""
import json, sys
from pathlib import Path
here = Path(__file__).parent; sys.path.insert(0, str(here))
import graphify.serve as s
import proto, bm25_files as B
from evalset import groups, GitReader
S = "/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad"
L = lambda l: {r["id"]: r for r in map(json.loads, open(here / f"results2/{l}.jsonl"))}
A, P = L("final-bm25files"), L("final-proto-tuned")
hit = lambda r: r is not None and r < 5
ids = {i for i in A if A[i]["repo"] != "django" and hit(A[i]["rank"]) and not hit(P[i]["rank"])}
proto.PARAMS.update(json.loads((here / "tuned_params.json").read_text()))
print(len(ids), "losses")
for (repo, commit, gpath, qset), qs in groups(f"{S}/graphs", f"{S}/graphs_ext").items():
    qs = [q for q in qs if q["id"] in ids]
    if not qs: continue
    G = s._load_graph(gpath); read = GitReader(Path(S) / "repos" / repo, commit)
    nfiles = len({d.get("source_file") for _, d in G.nodes(data=True) if d.get("source_file")})
    for q in qs:
        gold = q["files"][0]; gn = sum(1 for _, d in G.nodes(data=True) if d.get("source_file") in q["files"])
        txt = read(gold) or ""; qw = set(B.tokens(q["question"]))
        dem = [f for f in q["files"] if proto.demote_factor(G, next((n for n, d in G.nodes(data=True) if d.get("source_file") == f), None) or "x", qw) != 1.0] if False else []
        print(f"\n{q['id']} [{qset}, {nfiles} files] {q['question'][:100]}")
        print(f"  gold {q['files']} ({gn} nodes, {len(txt.splitlines())} lines); BM25 rank {A[q['id']]['rank']}, tuned proto rank {P[q['id']]['rank']}")
        print(f"  q-words in gold text: {sorted(qw & set(B.tokens(txt)))}")
        print(f"  proto top: {P[q['id']]['top_files'][:5]}")
        print(f"  BM25 top:  {A[q['id']]['top_files'][:5]}")
    read.close()
