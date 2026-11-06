#!/usr/bin/env python3
"""Per-kind found counts for several variants, per project + total, plus wrong `calls` edges.
usage: table.py v8 ctor [members ...]"""
import json, sys, collections
V = sys.argv[1:]
P = ["Dapper", "AutoMapper", "Newtonsoft.Json"]
K = ["same","inherited","static","typed","extension","interface","generic","ctor","other"]
FOUND = ("found", "found_other_overload")
def load(v, p):
    rows = [json.loads(l) for l in open(f"/home/user/mres/{v}/{p}/pairs.jsonl")]
    wrong = [json.loads(l) for l in open(f"/home/user/mres/{v}/{p}/wrong_calls.jsonl") if l.strip()]
    try: mem = json.load(open(f"/home/user/mres/{v}/{p}/members.json"))["table"]
    except FileNotFoundError: mem = {}
    return rows, wrong, mem
data = {(v, p): load(v, p) for v in V for p in P}
MK = ["ctor_init", "property_get", "property_set", "indexer_get", "indexer_set", "conversion", "operator"]
def table(projects, title):
    print(f"\n#### {title}\n")
    print("| kind | links | " + " | ".join(V) + " |")
    print("|---|---:|" + "---:|" * len(V))
    tot = collections.Counter()
    for k in K:
        n = sum(1 for r in data[(V[0], projects[0])][0] if False)  # placeholder
        n = sum(sum(1 for r in data[(V[0], p)][0] if r["kind"] == k) for p in projects)
        vals = [sum(sum(1 for r in data[(v, p)][0] if r["kind"] == k and r["status"] in FOUND) for p in projects) for v in V]
        tot["n"] += n
        for v, x in zip(V, vals): tot[v] += x
        print(f"| {k} | {n} | " + " | ".join(map(str, vals)) + " |")
    print(f"| **total (7349 key)** | **{tot['n']}** | " + " | ".join(f"**{tot[v]}**" for v in V) + " |")
    # callers by decl kind (subset of the total above)
    for ck in ("ctor", "accessor_get", "accessor_set", "conversion"):
        n = sum(sum(1 for r in data[(V[0], p)][0] if r["caller"]["decl_kind"] == ck) for p in projects)
        vals = [sum(sum(1 for r in data[(v, p)][0] if r["caller"]["decl_kind"] == ck and r["status"] in FOUND) for p in projects) for v in V]
        if n: print(f"| _of which caller is {ck}_ | {n} | " + " | ".join(map(str, vals)) + " |")
    for mk in MK:
        n = sum(data[(V[0], p)][2].get(mk, {}).get("links", 0) for p in projects)
        if not n: continue
        vals = [sum(data[(v, p)][2].get(mk, {}).get("found", 0) for p in projects) for v in V]
        print(f"| member key: {mk} | {n} | " + " | ".join(map(str, vals)) + " |")
    w = [sum(len(data[(v, p)][1]) for p in projects) for v in V]
    print(f"| wrong `calls` edges | | " + " | ".join(map(str, w)) + " |")
for p in P: table([p], p)
table(P, "All three")
