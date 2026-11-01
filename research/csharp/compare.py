#!/usr/bin/env python3
"""Compare graphify's graph.json against the Roslyn answer key.

usage: compare.py <project-name> <repo-root> <key.jsonl> [--out results/<name>]

Matching rules
- A key declaration (caller / target) is matched to graphify nodes by (source_file, start line) where the
  line may be the declaration line incl. attributes, the line after attributes, or the identifier line,
  AND the node's short name (label without "Type." prefix, "()" and generic args) equals the member name.
- caller: the innermost method/ctor/accessor/local function. For local functions the enclosing member's
  node also counts (graphify folds local-function bodies into the outer method).
- target: the method node. For ctor calls the target is the ctor node OR the class node(s) of the
  constructed type (graphify has no ctor nodes; `new T()` may become an edge to T).
- "found": graphify has an edge caller->target with relation in {calls, references, uses, instantiates}.
- "found (lenient)": same, but the target may be any node with the same name declared in the same
  file (ignores overload mix-ups, #1533).
Compiler links are unique (caller decl, target decl) pairs; the pair's KIND is that of its first call site.
"""
import collections
import json
import re
import sys
from pathlib import Path

EDGE_RELS = {"calls", "references", "uses", "instantiates"}


def short(label: str) -> str:
    s = label.strip()
    if s.endswith("()"):
        s = s[:-2]
    s = re.sub(r"<[^<>]*>", "", s)
    s = re.sub(r"<[^<>]*>", "", s)
    s = s.split(".")[-1] if "." in s and not s.endswith(".cs") else s
    return s.lower()


def load_graph(root: Path):
    g = json.loads((root / "graphify-out" / "graph.json").read_text())
    nodes = {n["id"]: n for n in g["nodes"]}
    by_loc = collections.defaultdict(list)  # (file, line) -> [node]
    by_file_name = collections.defaultdict(list)  # (file, shortname) -> [node]
    for n in g["nodes"]:
        sf, loc = n.get("source_file"), n.get("source_location") or ""
        m = re.match(r"L(\d+)", loc)
        if sf and m:
            by_loc[(sf, int(m.group(1)))].append(n)
        if sf:
            by_file_name[(sf, short(n.get("label", "")))].append(n)
    out_edges = collections.defaultdict(lambda: collections.defaultdict(set))  # src -> dst -> {rel}
    for l in g["links"]:
        out_edges[l["source"]][l["target"]].add(l["relation"])
    return g, nodes, by_loc, by_file_name, out_edges


def match_decl(d, by_loc, want_name=True):
    if not d:
        return set()
    lines = {d["line"], d["noattr_line"], d["id_line"]}
    name = (d["name"] or "").lower()
    res = set()
    for ln in lines:
        for n in by_loc.get((d["file"], ln), []):
            if not want_name or short(n.get("label", "")) == name:
                res.add(n["id"])
    return res


def main():
    proj, root, keyp = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    outdir = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
    # --pp-root: copy of the repo with #directives / inactive branches blanked (RoslynCallKey --write-preprocessed);
    # a graphify edge whose call line is blank there sits in code the compiler did not compile for this TFM.
    pp_root = Path(sys.argv[sys.argv.index("--pp-root") + 1]) if "--pp-root" in sys.argv else None
    _pp_cache = {}

    def inactive(file, line):
        if pp_root is None:
            return False
        if file not in _pp_cache:
            fp = pp_root / file
            _pp_cache[file] = fp.read_text(errors="replace").split("\n") if fp.exists() else None
        lines = _pp_cache[file]
        return bool(lines) and 0 < line <= len(lines) and not lines[line - 1].strip()
    g, nodes, by_loc, by_file_name, out_edges = load_graph(root)
    key = [json.loads(l) for l in keyp.read_text().splitlines() if l.strip()]
    sites = [json.loads(l) for l in Path(str(keyp).replace(".jsonl", ".sites.jsonl")).read_text().splitlines() if l.strip()]

    def has_edge(srcs, dsts):
        rels = set()
        for s in srcs:
            for d in dsts:
                rels |= out_edges.get(s, {}).get(d, set()) & EDGE_RELS
        return rels

    # ---- unique compiler pairs ----
    pairs = {}
    for r in sorted(key, key=lambda r: (r["call_file"], r["call_line"])):
        c, t = r["caller"], r["target"]
        tk = (t["file"], t["line"], t["name"]) if t else ("<type>", r["target_type_name"], r["target_type"][0]["file"] if r["target_type"] else "")
        pk = (c["file"], c["line"], c["name"], tk)
        if pk not in pairs:
            pairs[pk] = r

    rows = []
    for pk, r in pairs.items():
        callers = match_decl(r["caller"], by_loc)
        if r.get("caller_outer"):
            callers |= match_decl(r["caller_outer"], by_loc)
        targets = match_decl(r["target"], by_loc)
        if r["kind"] == "ctor" or r["target"] is None:
            for td in r["target_type"]:
                targets |= match_decl(td, by_loc)
        lenient_targets = set(targets)
        if r["target"]:
            lenient_targets |= {n["id"] for n in by_file_name.get((r["target"]["file"], r["target"]["name"].lower()), [])}
        rels = has_edge(callers, targets)
        lrels = has_edge(callers, lenient_targets)
        # fallback: edge from the caller's enclosing type node (calls attributed to the class)
        type_nodes = set()
        for td in r.get("caller_type_decls") or []:
            type_nodes |= match_decl(td, by_loc)
        frels = has_edge(type_nodes, lenient_targets)
        if not callers:
            status = "caller_node_missing"
        elif not lenient_targets:
            status = "target_node_missing"
        elif rels:
            status = "found"
        elif lrels:
            status = "found_other_overload"
        else:
            status = "missing"
        rows.append({**r, "status": status, "rels": sorted(rels | lrels), "class_fallback": bool(frels),
                     "g_callers": sorted(callers), "g_targets": sorted(lenient_targets)})

    kinds = ["same", "inherited", "static", "typed", "extension", "interface", "generic", "ctor", "other"]
    table = collections.OrderedDict((k, collections.Counter()) for k in kinds)
    for row in rows:
        c = table[row["kind"]]
        c["links"] += 1
        c["st:" + row["status"]] += 1
        if row["status"] == "found":
            c["found_strict"] += 1
        if row["status"] in ("found", "found_other_overload"):
            c["found"] += 1
        if row["status"] != "found" and row["status"] != "found_other_overload" and row["class_fallback"]:
            c["class_fallback"] += 1
        c["subkind:" + row["subkind"]] += 1 if row["subkind"] else 0

    # ---- graphify `calls` edges the compiler does not have ----
    own_files = {r["call_file"] for r in key} | {s["file"] for s in sites}
    key_pairs = set()
    for row in rows:
        for s in row["g_callers"]:
            for d in row["g_targets"]:
                key_pairs.add((s, d))
    sites_at = collections.defaultdict(list)
    for s in sites:
        sites_at[(s["file"], s["line"])].append(s)
    wrong = []
    for l in g["links"]:
        if l["relation"] != "calls":
            continue
        s, d = nodes.get(l["source"]), nodes.get(l["target"])
        if not s or not d or s.get("source_file") not in own_files or d.get("source_file") not in own_files:
            continue
        if (l["source"], l["target"]) in key_pairs:
            continue
        line = int(re.match(r"L(\d+)", l.get("source_location") or "L0").group(1))
        tname = short(d.get("label", ""))
        here = [x for x in sites_at.get((l.get("source_file") or s["source_file"], line), [])]
        same_name = [x for x in here if (x["name"] or "").lower() == tname]
        # target type of d: graphify id/labels carry "Type.Member" in the label
        dlabel = d.get("label", "")
        dtype = dlabel.split(".")[-2].lower() if dlabel.count(".") >= 1 and dlabel.endswith("()") else ""
        if not same_name and inactive(l.get("source_file") or s["source_file"], line):
            verdict, kind = "inactive_preprocessor_branch", "?"
        elif not same_name:
            verdict, kind = "no_call_with_that_name_at_line", "?"
        else:
            x = same_name[0]
            kind = x["kind"]
            if x["own"] and x["target_name"] and x["target_name"].lower() == tname and (not dtype or (x["target_type"] or "").lower() == dtype):
                verdict = "right_target_other_caller"   # compiler agrees on target, graphify attributes it to a different caller node
            elif x["own"]:
                verdict = "wrong_own_target"            # compiler resolves to a different own method
            elif x["status"] == "unresolved":
                verdict = "compiler_unresolved"
            else:
                verdict = "external_target"             # compiler resolves to BCL/package method; graphify linked a same-named own method
        wrong.append({"source": s.get("label"), "source_file": s.get("source_file"), "source_line": s.get("source_location"),
                      "target": d.get("label"), "target_file": d.get("source_file"), "target_line": d.get("source_location"),
                      "call_line": line, "verdict": verdict, "kind": kind,
                      "compiler_target": same_name[0]["target_sig"] if same_name else None,
                      "text": same_name[0]["text"] if same_name else None})

    summary = {"project": proj, "table": {k: dict(v) for k, v in table.items()},
               "wrong_calls": dict(collections.Counter((w["verdict"], w["kind"]) for w in wrong).most_common()),
               "graphify_calls_edges_in_scope": sum(1 for l in g["links"] if l["relation"] == "calls"
                                                    and nodes.get(l["source"], {}).get("source_file") in own_files
                                                    and nodes.get(l["target"], {}).get("source_file") in own_files)}
    summary["wrong_calls"] = {f"{a}|{b}": n for (a, b), n in collections.Counter((w["verdict"], w["kind"]) for w in wrong).most_common()}
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)
        (outdir / "pairs.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        (outdir / "wrong_calls.jsonl").write_text("\n".join(json.dumps(w) for w in wrong) + "\n")
        (outdir / "summary.json").write_text(json.dumps(summary, indent=1))
    print(f"== {proj}")
    print(f"{'kind':10} {'links':>6} {'found':>6} {'recall':>7} {'strict':>6} | missing callerNode targetNode classFallback")
    tot = collections.Counter()
    for k, c in table.items():
        tot.update(c)
        if c["links"]:
            print(f"{k:10} {c['links']:6} {c['found']:6} {100*c['found']/c['links']:6.1f}% {c['found_strict']:6} | {c['st:missing']:7} {c['st:caller_node_missing']:10} {c['st:target_node_missing']:10} {c['class_fallback']:13}")
    print(f"{'TOTAL':10} {tot['links']:6} {tot['found']:6} {100*tot['found']/tot['links']:6.1f}% {tot['found_strict']:6} | {tot['st:missing']:7} {tot['st:caller_node_missing']:10} {tot['st:target_node_missing']:10} {tot['class_fallback']:13}")
    print("wrong calls edges:", len(wrong), "of", summary["graphify_calls_edges_in_scope"], "in-scope calls edges")
    for k, n in summary["wrong_calls"].items():
        print(f"   {k}: {n}")


if __name__ == "__main__":
    main()
