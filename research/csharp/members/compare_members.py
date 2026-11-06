#!/usr/bin/env python3
"""Score graphify against the --members key (ctor initializers, property/indexer accessors, operators).

usage: compare_members.py <project> <repo-root> <members.jsonl> <out.json>
Uses compare.py's own matching (load_graph / match_decl / short) unchanged: unique (caller decl, target decl)
pairs; found = edge caller->target with relation in {calls, references, uses, instantiates}.
"""
import collections, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from compare import load_graph, match_decl, EDGE_RELS  # noqa: E402

proj, root, keyp, outp = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
g, nodes, by_loc, by_file_name, out_edges = load_graph(root)
key = [json.loads(l) for l in keyp.read_text().splitlines() if l.strip()]

def rows_for(recs):
    pairs = {}
    for r in sorted(recs, key=lambda r: (r["call_file"], r["call_line"])):
        c, t = r["caller"], r["target"]
        pk = (c["file"], c["line"], c["name"], t["file"], t["line"], t["name"], r["kind"])
        pairs.setdefault(pk, r)
    out = []
    for r in pairs.values():
        callers = match_decl(r["caller"], by_loc)
        if r.get("caller_outer"):
            callers |= match_decl(r["caller_outer"], by_loc)
        targets = match_decl(r["target"], by_loc)
        if r["kind"] == "ctor_init":
            for td in r["target_type"]:
                targets |= match_decl(td, by_loc)
        rels = {rel for s in callers for d in targets for rel in out_edges.get(s, {}).get(d, set()) & EDGE_RELS}
        status = ("caller_node_missing" if not callers else "target_node_missing" if not targets
                  else "found" if rels else "missing")
        out.append({**r, "status": status, "rels": sorted(rels), "g_callers": sorted(callers), "g_targets": sorted(targets)})
    return out

rows = rows_for(key)
def sub(r):
    k = r["kind"]
    if k.startswith("property_"):
        return k + (" (auto)" if r.get("auto_property") else " (body)")
    return k
table = collections.defaultdict(collections.Counter)
for r in rows:
    for k in {r["kind"], sub(r)}:
        table[k]["links"] += 1
        table[k][r["status"]] += 1
        if "calls" in r["rels"]:
            table[k]["via_calls"] += 1
outp.write_text(json.dumps({"project": proj, "table": {k: dict(v) for k, v in table.items()}}, indent=1))
outp.with_suffix(".rows.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
for k in sorted(table):
    c = table[k]
    print(f"{proj:16} {k:26} links={c['links']:5} found={c['found']:5} callerMissing={c['caller_node_missing']:5} targetMissing={c['target_node_missing']:5} missing={c['missing']:5}")
