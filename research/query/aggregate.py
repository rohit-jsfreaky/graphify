"""Pool per-repo benchmark JSON (graphify benchmark --questions --json) into one row."""
import json, sys
from pathlib import Path

def load(d):
    rows = []
    for f in sorted(Path(d).glob("*.json")):
        if f.name == "summary.json":
            continue
        txt = f.read_text()
        start = txt.find("{")
        r = json.loads(txt[start:])
        for p in r["per_question"]:
            p["repo"] = f.stem
            rows.append(p)
    return rows

def summarize(rows):
    n = len(rows)
    ranks = [p["rank"] for p in rows]
    toks = sorted(p["tokens"] for p in rows)
    hit = lambda k: sum(1 for r in ranks if r is not None and r < k)
    return {"n": n, "top1": hit(1), "top3": hit(3), "top5": hit(5),
            "found": sum(r is not None for r in ranks), "median_tokens": toks[n // 2] if n else 0,
            "over_budget": sum(1 for p in rows if p.get("over_budget"))}

if __name__ == "__main__":
    d = sys.argv[1]
    s = summarize(load(d))
    Path(d, "summary.json").write_text(json.dumps(s, indent=1))
    n = s["n"]
    print(f"{Path(d).name}: n={n} top1={100*s['top1']/n:.0f}% top3={100*s['top3']/n:.0f}% "
          f"top5={100*s['top5']/n:.0f}% anywhere={100*s['found']/n:.0f}% median_tokens={s['median_tokens']} over_budget={s['over_budget']}")
