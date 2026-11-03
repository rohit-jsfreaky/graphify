"""Held-out report: per split and per repo, top-1/3/5/anywhere and median tokens for
each system, plus exact McNemar tests (two-sided binomial on the discordant pairs)
on top-5 hits.

usage: python -I heldout_report.py OUT.md LABEL=results2/file.jsonl ...  [--pairs A:B,A:C]
Splits come from split.json: tune (Django, 114), heldout_lite (63), heldout_verified (116),
heldout_all (179), all (293).
"""
import json, sys
from math import comb
from pathlib import Path
here = Path(__file__).parent

def mcnemar(b, c):
    n = b + c
    if n == 0: return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)

def main():
    out = sys.argv[1]; args = sys.argv[2:]
    pairs = []
    if "--pairs" in args:
        i = args.index("--pairs"); pairs = [p.split(":") for p in args[i + 1].split(",")]; args = args[:i] + args[i + 2:]
    systems = {}
    for a in args:
        lab, f = a.split("=", 1)
        systems[lab] = {r["id"]: r for r in map(json.loads, open(here / f))}
    split = json.loads((here / "split.json").read_text())
    sets = {"tune (Django)": set(split["tune"]), "held-out Lite (63)": set(split["heldout"]),
            "held-out Verified (116)": set(split["heldout_ext"]),
            "held-out all non-Django": set(split["heldout"]) | set(split["heldout_ext"])}
    sets["all questions"] = set().union(*sets.values())
    hit = lambda r: r is not None and r < 5
    L = []
    for name, ids in sets.items():
        common = set.intersection(ids, *[set(s) for s in systems.values()])
        L += [f"\n### {name}: {len(common)} questions\n", "| system | top-1 | top-3 | top-5 | anywhere | median tokens |", "|---|---|---|---|---|---|"]
        for lab, s in systems.items():
            rs = [s[i] for i in common]; n = len(rs) or 1
            h = lambda k: sum(1 for r in rs if r["rank"] is not None and r["rank"] < k)
            t = sorted(r["tokens"] for r in rs)
            L.append(f"| {lab} | {100*h(1)/n:.0f}% ({h(1)}) | {100*h(3)/n:.0f}% ({h(3)}) | {100*h(5)/n:.0f}% ({h(5)}) | "
                     f"{100*sum(r['rank'] is not None for r in rs)/n:.0f}% | {t[len(t)//2] if t else 0:,} |")
        if pairs:
            L += ["", "| pair (top-5) | A only | B only | McNemar p |", "|---|---|---|---|"]
            for a, b in pairs:
                bo = sum(1 for i in common if hit(systems[a][i]["rank"]) and not hit(systems[b][i]["rank"]))
                co = sum(1 for i in common if hit(systems[b][i]["rank"]) and not hit(systems[a][i]["rank"]))
                L.append(f"| {a} vs {b} | {bo} | {co} | {mcnemar(bo, co):.3g} |")
        if name.startswith("held-out all") or name.startswith("all"):
            repos = sorted({systems[next(iter(systems))][i]["repo"] for i in common})
            L += ["", f"Per repo ({name}), top-5 hits:", "", "| repo | n | " + " | ".join(systems) + " |",
                  "|---|---|" + "---|" * len(systems)]
            for repo in repos:
                rid = [i for i in common if systems[next(iter(systems))][i]["repo"] == repo]
                cells = [f"{100*sum(hit(s[i]['rank']) for i in rid)/len(rid):.0f}% ({sum(hit(s[i]['rank']) for i in rid)})" for s in systems.values()]
                L.append(f"| {repo} | {len(rid)} | " + " | ".join(cells) + " |")
            if pairs:
                L += ["", f"Per repo ({name}), McNemar on top-5 (A only / B only, p):", "",
                      "| repo | " + " | ".join(f"{x} vs {y}" for x, y in pairs) + " |", "|---|" + "---|" * len(pairs)]
                for repo in repos:
                    rid = [i for i in common if systems[next(iter(systems))][i]["repo"] == repo]
                    cells = []
                    for x, y in pairs:
                        bo = sum(1 for i in rid if hit(systems[x][i]["rank"]) and not hit(systems[y][i]["rank"]))
                        co = sum(1 for i in rid if hit(systems[y][i]["rank"]) and not hit(systems[x][i]["rank"]))
                        cells.append(f"{bo}/{co}, p={mcnemar(bo, co):.2g}")
                    L.append(f"| {repo} | " + " | ".join(cells) + " |")
    Path(out).write_text("\n".join(L) + "\n"); print("\n".join(L))

if __name__ == "__main__":
    main()
