#!/usr/bin/env python3
"""Node-id stability: every v8 node id must survive in the branch; list what is new."""
import json, sys, collections
A, B = sys.argv[1], sys.argv[2]
for p in ["Dapper", "AutoMapper", "Newtonsoft.Json"]:
    ga = json.load(open(f"/home/user/runs/{A}/{p}/graphify-out/graph.json"))
    gb = json.load(open(f"/home/user/runs/{B}/{p}/graphify-out/graph.json"))
    na = {n["id"]: n for n in ga["nodes"]}; nb = {n["id"]: n for n in gb["nodes"]}
    lost = set(na) - set(nb); new = set(nb) - set(na)
    kinds = collections.Counter(((nb[i].get("metadata") or {}).get("kind") or "other") for i in new)
    changed = sum(1 for i in set(na) & set(nb) if (na[i]["label"], na[i].get("source_file"), na[i].get("source_location")) != (nb[i]["label"], nb[i].get("source_file"), nb[i].get("source_location")))
    print(f"{p}: v8 nodes {len(na)}, branch {len(nb)}, lost {len(lost)}, new {len(new)} {dict(kinds)}, same id but label/file/line changed {changed}")
    for i in sorted(lost)[:5]: print("   LOST", i, na[i]["label"])
    for i in sorted(new):
        if (nb[i].get("metadata") or {}).get("kind") not in ("constructor",) and kinds.get("other"): print("   NEW non-ctor", i, nb[i]["label"]); break
