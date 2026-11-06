#!/usr/bin/env python3
"""Classify `calls` edges flagged as extra by compare.py that are new in variant B vs A.
usage: wrongdiff.py A B"""
import json, sys, collections, re
A, B = sys.argv[1], sys.argv[2]
P = ["Dapper", "AutoMapper", "Newtonsoft.Json"]
def W(v, p): return [json.loads(l) for l in open(f"/home/user/mres/{v}/{p}/wrong_calls.jsonl") if l.strip()]
def key(w): return (w["source"], w["source_line"], w["target"], w["target_line"])
tot = collections.Counter()
for p in P:
    g = json.load(open(f"/home/user/runs/{B}/{p}/graphify-out/graph.json"))
    lab = {n["id"]: n["label"] for n in g["nodes"]}
    loc = {n["id"]: n.get("source_location") for n in g["nodes"]}
    meta = {n["id"]: (n.get("metadata") or {}) for n in g["nodes"]}
    owner = {}
    for l in g["links"]:
        if l["relation"] in ("method", "defines"): owner[l["target"]] = l["source"]
    member_pairs = set()
    for l in open(f"/home/user/mres/{B}/{p}/members.rows.jsonl"):
        r = json.loads(l)
        for s in r["g_callers"]:
            for t in r["g_targets"]: member_pairs.add((lab.get(s), loc.get(s), lab.get(t), loc.get(t)))
    a = {key(w): w for w in W(A, p)}; b = {key(w): w for w in W(B, p)}
    # A-side edges by (target label/line) with class-labelled source, to detect "moved"
    a_by_target = collections.defaultdict(set)
    for k, w in a.items(): a_by_target[(w["target"], w["target_line"])].add((w["source"], w["source_line"]))
    for k in sorted(set(b) - set(a)):
        w = b[k]
        src_type = w["source"].split(".")[0]
        if (w["source"], w["source_line"], w["target"], w["target_line"]) in member_pairs:
            cls = "correct: confirmed by Roslyn member key (ctor initializer)"
        elif any(s == src_type for s, _ in a_by_target[(w["target"], w["target_line"])]):
            cls = "same wrong edge, caller moved from the type to its constructor"
        elif w["target"].endswith("()") and w["target"].split(".")[0] == w["target"].split(".")[-1][:-2]:
            tgt_type = w["target"].split(".")[0]
            mirrored = [x for x in a.values() if x["source"].split(".")[-1] == w["source"].split(".")[-1] and x["target"] == tgt_type] or \
                       [x for x in a.values() if x["source"] == w["source"] and x["target"].split(".")[0] == tgt_type]
            cls = "ctor edge mirroring an existing extra edge to the type" if mirrored else "NEW: edge to a constructor"
        else:
            cls = "NEW"
        tot[cls] += 1
        if not cls.startswith("correct"):
            print(f"  [{p}] {cls}: {w['source']} {w['source_line']} -> {w['target']} {w['target_line']} | {w['verdict']} | {w['text']!r:.90} | compiler: {w['compiler_target']}")
    for k in sorted(set(a) - set(b)):
        w = a[k]
        moved = any(x["target"] == w["target"] and x["source"].endswith(w["source"] + "()") for x in b.values())
        tot["removed: " + ("moved to the constructor node" if moved else "gone")] += 1
for k, n in tot.most_common(): print(n, k)
