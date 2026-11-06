"""Table for bench_built.py results. Usage: python bench_built_report.py <results/built>"""
import json
import sys
from pathlib import Path

REPOS = ["django", "flask", "requests", "hono", "jsoup", "caddy"]
d = Path(sys.argv[1])
res = {r: json.loads((d / f"{r}.built.json").read_text()) for r in REPOS if (d / f"{r}.built.json").exists()}
rows = [("before", "v8 `affected` (graph items only)"),
        ("after_printed", "built, printed order (graph, then co-change section)"),
        ("after_cc_first", "built, co-change items first (by `source` tag)"),
        ("section_view", "built, first k graph files + whole co-change section")]
md = ["| row | " + " | ".join(f"{r} R@10 / hit@10" for r in res) + " | ALL R@5 | ALL R@10 | ALL R@20 | ALL hit@10 | ALL P@10 or shown@10 |",
      "|---|" + "---|" * (len(res) + 5)]
for key, label in rows:
    cells = [f"{res[r][key]['R@10']:.3f} / {res[r][key]['hit@10']:.3f}" for r in res]
    mean = lambda m: sum(res[r][key][m] for r in res) / len(res)  # noqa: E731
    last = "shown@10" if key == "section_view" else "P@10"
    md.append(f"| {label} | " + " | ".join(cells) +
              f" | {mean('R@5'):.3f} | {mean('R@10'):.3f} | {mean('R@20'):.3f} | {mean('hit@10'):.3f} | {mean(last):.3f} |")
md.append("")
md.append("Queries per repo: " + ", ".join(f"{r} {res[r]['queries']}" for r in res))
md.append("Unresolved seeds (CLI would exit 4): " + ", ".join(f"{r} {res[r]['stats'].get('seed_unresolved', 0)}" for r in res))
(d / "tables_built.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
