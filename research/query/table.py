"""Build results/table.md: every variant's top-1/3/5/anywhere and median tokens,
each PR next to its own merge-base (the code it was written against)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from aggregate import load, summarize
here = Path(__file__).parent; R = here / "results"

def row(d):
    rows = load(R / d)
    if len(rows) != 177: return None
    s = summarize(rows); n = s["n"]
    return s, rows

def pct(s, k): return f"{100 * s[k] / s['n']:.0f}%"
def fmt(name, s): return f"| {name} | {pct(s,'top1')} | {pct(s,'top3')} | {pct(s,'top5')} | {pct(s,'found')} | {s['median_tokens']:,} |"

bases = dict(l.split() for l in (here / "pr_bases.txt").read_text().splitlines())
prep = dict(l.split() for l in (here / "pr_prep.txt").read_text().splitlines())
out = ["| variant | top-1 | top-3 | top-5 | anywhere | median tokens |", "|---|---|---|---|---|---|"]
for name, d in [("upstream/v8 query_graph", "v8"), ("BM25 over whole files (tokens = reading the 5 files)", "bm25_files")]:
    out.append(fmt(name, row(d)[0]))
out += ["", "PRs (each on its own head, same v8-built graphs; base = its merge-base with v8):", "",
        "| PR | how run | top-1 | top-3 | top-5 | anywhere | median tokens | base top-5 | Δ top-5 vs base |", "|---|---|---|---|---|---|---|---|---|"]
prs = sorted((p for p in R.glob("pr-*") if not p.name.startswith("pr-base")), key=lambda p: -(row(p.name)[0]["top5"] if row(p.name) else -1))
for p in prs:
    r = row(p.name)
    if not r: continue
    s = r[0]; n = p.name[3:].split("-")[0]
    b = row("pr-" + bases[n]) if n in bases else None
    how = {"clean": "cherry-pick", "help-conflict-resolved": "cherry-pick (help text kept)", "conflict": "driver"}.get(prep.get(n), "?")
    if p.name.endswith("rebuilt"): how += ", graphs rebuilt with PR"
    bt = pct(b[0], "top5") if b else "n/a"
    delta = f"{(s['top5'] - b[0]['top5']):+d} q" if b else "n/a"
    out.append(f"| #{p.name[3:]} | {how} | {pct(s,'top1')} | {pct(s,'top3')} | {pct(s,'top5')} | {pct(s,'found')} | {s['median_tokens']:,} | {bt} | {delta} |")
out += ["", "Prototypes (on top of upstream/v8, same graphs, same scoring):", "",
        "| variant | top-1 | top-3 | top-5 | anywhere | median tokens |", "|---|---|---|---|---|---|"]
for p in sorted(R.glob("proto-*"), key=lambda p: -(row(p.name)[0]["top5"])):
    out.append(fmt(p.name[6:], row(p.name)[0]))
# per-repo split and paired comparison for the headline variants
out += ["", "Django (114) vs the other 8 repos (63), top-5:", "", "| variant | django | others |", "|---|---|---|"]
for d in ["v8", "bm25_files", "pr-3417", "pr-2403", "proto-bm25b_filefirst", "proto-bm25b_filefirst_set", "proto-bm25b_rel"]:
    rows = row(d)[1]
    dj = [x for x in rows if x["repo"] == "django"]; ot = [x for x in rows if x["repo"] != "django"]
    h = lambda xs: f"{100*sum(1 for x in xs if x['rank'] is not None and x['rank'] < 5)/len(xs):.0f}%"
    out.append(f"| {d} | {h(dj)} | {h(ot)} |")
a = {(x["repo"], x["question"]): x["rank"] for x in row("proto-bm25b_filefirst")[1]}
b = {(x["repo"], x["question"]): x["rank"] for x in row("bm25_files")[1]}
hit = lambda r: r is not None and r < 5
w = sum(1 for k in a if hit(a[k]) and not hit(b[k])); l = sum(1 for k in a if hit(b[k]) and not hit(a[k]))
out += ["", f"Paired, top-5: bm25b_filefirst wins {w} questions BM25-files misses, loses {l} (sign test on {w+l} discordant pairs)."]
(R / "table.md").write_text("\n".join(out) + "\n")
print("\n".join(out))
