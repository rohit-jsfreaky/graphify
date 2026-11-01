#!/usr/bin/env python3
"""Aggregate results/<project>/{pairs,wrong_calls}.jsonl into markdown tables (stdout).

usage: summarize.py <results-dir> <project> [<project> ...]
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

res, projects = Path(sys.argv[1]), sys.argv[2:]
KINDS = ["same", "inherited", "static", "typed", "extension", "interface", "generic", "ctor", "other"]
FOUND = ("found", "found_other_overload")


def load(p, name):
    return read_jsonl(res / p / name)


def recall_table(rows_by_proj, title):
    print(f"### {title}\n")
    print("| kind | compiler links | graphify found | recall % | found via `calls` edge | found only via other relation |")
    print("|---|---:|---:|---:|---:|---:|")
    tot = collections.Counter()
    for k in KINDS:
        rs = [r for rows in rows_by_proj for r in rows if r["kind"] == k]
        n = len(rs)
        f = sum(r["status"] in FOUND for r in rs)
        fc = sum(r["status"] in FOUND and "calls" in r["rels"] for r in rs)
        tot.update(n=n, f=f, fc=fc)
        if n:
            print(f"| {k} | {n} | {f} | {100*f/n:.1f} | {fc} | {f-fc} |")
    print(f"| **total** | **{tot['n']}** | **{tot['f']}** | **{100*tot['f']/tot['n']:.1f}** | {tot['fc']} | {tot['f']-tot['fc']} |\n")


all_rows = []
for p in projects:
    rows = load(p, "pairs.jsonl")
    all_rows.append(rows)
    recall_table([rows], p)
recall_table(all_rows, "All three projects")

print("### Strict vs lenient (overload) matching\n")
print("| project | links | found (exact overload node) | found (any same-name node in target file) |")
print("|---|---:|---:|---:|")
for p, rows in zip(projects, all_rows):
    print(f"| {p} | {len(rows)} | {sum(r['status']=='found' for r in rows)} | {sum(r['status'] in FOUND for r in rows)} |")
print()

VERDICT = {
    "external_target": "wrong target: compiler binds to a BCL/package method, graphify to a same-named own method",
    "wrong_own_target": "wrong target: compiler binds to a different own method",
    "right_target_other_caller": "right target, wrong caller node (class node for ctor bodies, merged overload/explicit impl, #if-orphaned method)",
    "inactive_preprocessor_branch": "call sits in an #if branch the net8.0 build does not compile",
    "no_call_with_that_name_at_line": "no call with that name on that line",
}
print("### graphify `calls` edges the compiler does not have (both ends in the library source)\n")
print("| verdict | " + " | ".join(projects) + " | total | by compiler KIND of the call at that line |")
print("|---|" + "---:|" * (len(projects) + 1) + "---|")
wr = {p: load(p, "wrong_calls.jsonl") for p in projects}
calls_in_scope = {p: json.loads((res / p / "summary.json").read_text())["graphify_calls_edges_in_scope"] for p in projects}
for v, desc in VERDICT.items():
    cnt = [sum(w["verdict"] == v for w in wr[p]) for p in projects]
    kinds = collections.Counter(w["kind"] for p in projects for w in wr[p] if w["verdict"] == v)
    print(f"| {desc} | " + " | ".join(map(str, cnt)) + f" | {sum(cnt)} | " + ", ".join(f"{k} {n}" for k, n in kinds.most_common()) + " |")
print("| **all extra `calls` edges** | " + " | ".join(str(len(wr[p])) for p in projects) + f" | {sum(len(wr[p]) for p in projects)} | |")
print("| in-scope graphify `calls` edges | " + " | ".join(str(calls_in_scope[p]) for p in projects) + f" | {sum(calls_in_scope.values())} | |")
