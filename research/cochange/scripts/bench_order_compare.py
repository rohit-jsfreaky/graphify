"""Compare two bench_order.py runs. Usage: python bench_order_compare.py <results_dir> <before> <after>"""
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report import binom_two_sided  # noqa: E402

res, a_lab, b_lab = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
A = json.load(gzip.open(res / f"order_{a_lab}.json.gz", "rt"))
B = json.load(gzip.open(res / f"order_{b_lab}.json.gz", "rt"))
md = [f"| repo | queries | {a_lab} R@10 | {b_lab} R@10 | {a_lab} R@20 | {b_lab} R@20 | {a_lab} hit@10 | {b_lab} hit@10 | same set |",
      "|---|---|---|---|---|---|---|---|---|"]
means = []
only_b = only_a = 0
for r in A:
    vals = []
    same = 0
    for qa, qb in zip(A[r], B[r]):
        assert qa["seed"] == qb["seed"] and qa["sha"] == qb["sha"]
        t = set(qa["truth"])
        ra, rb = qa["files"], qb["files"]
        same += set(ra) == set(rb)
        ha, hb = bool(t & set(ra[:10])), bool(t & set(rb[:10]))
        only_a += ha and not hb
        only_b += hb and not ha
        vals.append((len(t & set(ra[:10])) / len(t), len(t & set(rb[:10])) / len(t),
                     len(t & set(ra[:20])) / len(t), len(t & set(rb[:20])) / len(t), ha, hb))
    m = [sum(c) / len(c) for c in zip(*vals)]
    means.append(m)
    md.append(f"| {r} | {len(vals)} | " + " | ".join(f"{x:.3f}" for x in m) + f" | {same}/{len(vals)} |")
mm = [sum(c) / len(c) for c in zip(*means)]
md.append("| ALL (repo mean) | 2070 | " + " | ".join(f"{x:.3f}" for x in mm) + " | |")
md.append(f"\nMcNemar hit@10: only {b_lab} {only_b}, only {a_lab} {only_a}, p = {binom_two_sided(only_b, only_a):.2g}")
(res / f"tables_order_{a_lab}_vs_{b_lab}.md").write_text("\n".join(md) + "\n")
print("\n".join(md))
