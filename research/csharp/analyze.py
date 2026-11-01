#!/usr/bin/env python3
"""Attribute every compiler link graphify misses to one primary cause (first matching rule wins).

usage: analyze.py <results-dir> <ts_errors.jsonl> <project> [<project> ...]
"""
import collections
import gzip
import json
import sys
from pathlib import Path


def read_jsonl(path: Path) -> list:
    """Read <name>.jsonl, or <name>.jsonl.gz as committed in results/."""
    text = path.read_text() if path.exists() else gzip.open(str(path) + ".gz", "rt").read()
    return [json.loads(l) for l in text.splitlines() if l.strip()]

res_dir, ts_path, projects = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3:]
ts_err = {}
for l in ts_path.read_text().splitlines():
    r = json.loads(l)
    ts_err[r["file"]] = r["first_error_line"]

NON_METHOD_CALLERS = {"ctor", "dtor", "operator", "conversion", "accessor_get", "accessor_set",
                      "accessor_add", "accessor_remove", "accessor_init", "local_function"}


def cause(r):
    if r["kind"] == "extension":
        return "1 extension-method call"
    ck = r["caller"]["decl_kind"]
    if ck in NON_METHOD_CALLERS:
        return f"2 caller is {ck.split('_')[0] if ck.startswith('accessor') else ck} (no graphify function node)"
    f = r["call_file"]
    if f in ts_err and r["call_line"] >= ts_err[f]:
        return "3 call after a tree-sitter ERROR in the file (#if/#endif)"
    if r["status"] == "caller_node_missing":
        return "4 caller method has no node (merged overload / explicit interface impl)"
    if r["kind"] == "ctor" and r["receiver"] == "new_implicit":
        return "5 target-typed new()"
    if r["target"] and r["target"]["name"] == r["caller"]["name"]:
        return "6 target has the caller's own name (base.X() in override X / overload forwarding)"
    return f"7 other: {r['kind']} via {r['receiver'].split(':')[0]}"


total = collections.Counter()
per = {}
examples = collections.defaultdict(list)
for p in projects:
    rows = read_jsonl(res_dir / p / "pairs.jsonl")
    c = collections.Counter()
    for r in rows:
        if r["status"] in ("found", "found_other_overload"):
            continue
        k = cause(r)
        c[k] += 1
        if len(examples[k]) < 6:
            examples[k].append(f"{p}: {r['call_file']}:{r['call_line']} {r['caller']['type']}.{r['caller']['name']} -> {r['target_sig'][:100]}  [{r['call_text'][:60]}]")
    per[p] = c
    total.update(c)

keys = sorted(total)
print(f"{'cause':86} " + " ".join(f"{p[:10]:>10}" for p in projects) + "      total")
for k in keys:
    print(f"{k:86} " + " ".join(f"{per[p][k]:10}" for p in projects) + f" {total[k]:10}")
print(f"{'ALL MISSED':86} " + " ".join(f"{sum(per[p].values()):10}" for p in projects) + f" {sum(total.values()):10}")
print()
for k in keys:
    print("##", k)
    for e in examples[k]:
        print("   ", e.replace("\n", " "))
