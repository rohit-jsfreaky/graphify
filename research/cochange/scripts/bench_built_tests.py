"""Paired McNemar (hit@10) for the built benchmark. Usage: python bench_built_tests.py <results/built>"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report import binom_two_sided  # noqa: E402

d = Path(sys.argv[1])
lines = []
for view in ("after_cc_first", "section_view", "after_printed"):
    a = b = 0
    for r in ["django", "flask", "requests", "hono", "jsoup", "caddy"]:
        for q in (json.loads(x) for x in gzip.open(d / f"{r}.built_queries.jsonl.gz", "rt")):
            t, g, co = set(q["truth"]), q["graph"], q["cochange"]
            lst = {"after_cc_first": (co + [f for f in g if f not in co])[:10],
                   "section_view": list(dict.fromkeys(g[:10] + co)),
                   "after_printed": (g + [f for f in co if f not in g])[:10]}[view]
            new, old = bool(t & set(lst)), bool(t & set(g[:10]))
            a += new and not old
            b += old and not new
    lines.append(f"- {view} vs before, hit@10: only {view} hits {a}, only before hits {b}, McNemar p = {binom_two_sided(a, b):.2g}")
(d / "tests_built.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
