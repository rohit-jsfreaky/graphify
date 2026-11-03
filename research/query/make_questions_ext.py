"""Extra held-out questions: SWE-bench Verified issues of the 8 non-Django repos that
are not already in the Lite set. Same rule as make_questions.py (question = issue
title, files = non-test files of the gold patch; issues touching only tests are
dropped). Each issue keeps its OWN base commit (one graph per commit).

usage: python -I make_questions_ext.py VERIFIED.parquet LITE.parquet OUT_DIR
"""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
from make_questions import gold_files

REPOS = ["pytest-dev/pytest", "sphinx-doc/sphinx", "astropy/astropy", "psf/requests",
         "pylint-dev/pylint", "pydata/xarray", "mwaskom/seaborn", "pallets/flask"]

def main(verified, lite, out):
    v = pd.read_parquet(verified); l = pd.read_parquet(lite)
    v = v[v.repo.isin(REPOS) & ~v.instance_id.isin(l.instance_id)]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    total = dropped = 0
    for repo in REPOS:
        name = repo.split("/")[1]
        rows = []
        for _, r in v[v.repo == repo].sort_values("instance_id").iterrows():
            files = gold_files(r.patch)
            if not files:
                dropped += 1; continue
            rows.append({"id": r.instance_id, "question": r.problem_statement.strip().splitlines()[0].strip(),
                         "files": files, "commit": r.base_commit})
        (out / f"{name}.jsonl").write_text("".join(json.dumps(x) + "\n" for x in rows))
        total += len(rows); print(name, len(rows))
    print("total", total, "dropped (tests only)", dropped)

if __name__ == "__main__":
    main(*sys.argv[1:4])
