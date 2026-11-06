"""Compare two benchmark result files: top-1/3/5/anywhere per split, and every question whose rank changed.
usage: python -I cmp_fix.py BEFORE.jsonl AFTER.jsonl SPLIT.json"""
import json, sys
A = {r["id"]: r for r in map(json.loads, open(sys.argv[1]))}
B = {r["id"]: r for r in map(json.loads, open(sys.argv[2]))}
sp = json.load(open(sys.argv[3]))
sets = {"Django (114)": set(sp["tune"]), "held-out (179)": set(sp["heldout"]) | set(sp["heldout_ext"]),
        "Verified (116)": set(sp["heldout_ext"]), "all (293)": set(A)}
def row(R, ids):
    rs = [R[i]["rank"] for i in ids]; n = len(rs); h = lambda k: sum(1 for r in rs if r is not None and r < k)
    t = sorted(R[i]["tokens"] for i in ids)
    return f"{100*h(1)/n:.0f}% ({h(1)}) | {100*h(3)/n:.0f}% ({h(3)}) | {100*h(5)/n:.0f}% ({h(5)}) | {100*sum(r is not None for r in rs)/n:.0f}% ({sum(r is not None for r in rs)}) | {t[n//2]:,}"
print("| split | version | top-1 | top-3 | top-5 | anywhere | median tokens |\n|---|---|---|---|---|---|---|")
for name, ids in sets.items():
    print(f"| {name} | before fix | {row(A, ids)} |\n| {name} | after fix | {row(B, ids)} |")
ch = [i for i in A if A[i]["rank"] != B[i]["rank"]]
fmt = lambda r: "not shown" if r is None else str(r + 1)
print(f"\n{len(ch)} questions changed rank (1 = first file shown):\n")
print("| question | repo | set | before | after | top-5 effect |\n|---|---|---|---|---|---|")
for i in sorted(ch):
    a, b = A[i]["rank"], B[i]["rank"]; ha, hb = a is not None and a < 5, b is not None and b < 5
    eff = "gained" if hb and not ha else "lost" if ha and not hb else "same"
    print(f"| {i} | {A[i]['repo']} | {'tune' if i in sets['Django (114)'] else 'held-out ' + A[i]['set']} | {fmt(a)} | {fmt(b)} | {eff} |")
tok = sum(1 for i in A if A[i]["tokens"] != B[i]["tokens"]); tf = sum(1 for i in A if A[i]["top_files"] != B[i]["top_files"])
print(f"\nanswer size changed for {tok} questions; first-5 file list changed for {tf}")
