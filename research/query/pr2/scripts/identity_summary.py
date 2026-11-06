"""Compare answer dumps (dump_answers.py) and the benchmark rows (bench_cli.py).
usage: python -I identity_summary.py RESULTS_DIR"""
import json, sys
from pathlib import Path
R = Path(sys.argv[1])
L = lambda f: {(r["id"], r["depth"]): r for r in map(json.loads, open(R / "identity" / f))}
def cmp(name, a, b):
    dj = sum(1 for k in a if k[0].startswith("django"))
    print(f"{name}: {len(a)} answers ({dj} Django, {len(a) - dj} held-out; depth 2 and 3), "
          f"full text differs {sum(a[k]['sha256'] != b[k]['sha256'] for k in a)}, "
          f"NODE files or their order differ {sum(a[k]['files'] != b[k]['files'] for k in a)}")
cmp("before vs after, PYTHONHASHSEED=0", L("ans_before_seed0.jsonl"), L("ans_after_seed0.jsonl"))
cmp("before vs after, random hash seed", L("ans_before_all.jsonl"), L("ans_after_all.jsonl"))
cmp("v8 run 1 vs v8 run 2, random hash seed", L("ans_v8_run1.jsonl"), L("ans_v8_run2.jsonl"))
B = lambda f: {r["id"]: (r["rank"], r["tokens"], r["top_files"]) for r in map(json.loads, open(R / f))}
a, b = B("final2-pr2.jsonl"), B("final3-pr2fast.jsonl")
print(f"graphify benchmark --questions, 24d81d2d (final2-pr2) vs this commit (final3-pr2fast): {len(a)} questions, "
      f"rank/tokens/top files differ for {sum(a[i] != b[i] for i in a)}")
