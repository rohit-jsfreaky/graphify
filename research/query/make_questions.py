"""Build the SWE-bench Lite answer key: one questions file per repo.

usage: python -I make_questions.py LITE.parquet REPOS_DIR OUT_DIR
Question = first line of the issue (its title); files = non-test files the gold
patch changes. Per repo the base commit is the candidate (one of its issues'
base commits) under which the most issues have all their gold files present.
"""
import json, re, subprocess, sys
from collections import Counter
from pathlib import Path
import pandas as pd

REPOS = ["django/django", "pytest-dev/pytest", "sphinx-doc/sphinx", "astropy/astropy", "psf/requests",
         "pylint-dev/pylint", "pydata/xarray", "mwaskom/seaborn", "pallets/flask"]

def is_test(p):
    parts = p.split("/")
    name = parts[-1]
    return (any(d in ("tests", "test", "testing") for d in parts[:-1]) or name.startswith("test_")
            or name.endswith("_test.py") or name == "conftest.py")

def gold_files(patch):
    files = re.findall(r"^diff --git a/(\S+) b/", patch, re.M)
    return [f for f in dict.fromkeys(files) if not is_test(f)]

def tree(repo_dir, commit):
    out = subprocess.run(["git", "-C", repo_dir, "ls-tree", "-r", "--name-only", commit],
                         capture_output=True, text=True, check=True).stdout
    return set(out.splitlines())

def main(parquet, repos_dir, out_dir):
    d = pd.read_parquet(parquet)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for repo in REPOS:
        rows = d[d.repo == repo]
        name = repo.split("/")[1]
        items = []
        for _, r in rows.iterrows():
            files = gold_files(r.patch)
            title = r.problem_statement.strip().splitlines()[0].strip()
            items.append({"id": r.instance_id, "question": title, "files": files, "base": r.base_commit})
        items = [i for i in items if i["files"]]
        trees = {c: tree(str(Path(repos_dir) / name), c) for c in sorted({i["base"] for i in items})}
        cover = {c: sum(all(f in t for f in i["files"]) for i in items) for c, t in trees.items()}
        best = max(cover, key=lambda c: cover[c])
        with open(out / f"{name}.jsonl", "w") as fh:
            for i in items:
                fh.write(json.dumps({"id": i["id"], "question": i["question"], "files": i["files"]}) + "\n")
        summary[name] = {"commit": best, "issues": len(items), "covered": cover[best]}
        print(name, summary[name])
    (out / "commits.json").write_text(json.dumps(summary, indent=1))

if __name__ == "__main__":
    main(*sys.argv[1:4])
