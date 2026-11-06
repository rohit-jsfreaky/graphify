"""Final numbers through the real CLI: `python -m graphify benchmark <graph> --questions <file> --json`
(PR #4342 harness), run with the graphify package in SRC, once per graph.

usage: python -I bench_cli.py LABEL SRC GRAPHS_DIR [only=tune|heldout|all]
GRAPHS_DIR/<repo>.json = Lite commit graph, GRAPHS_DIR/<repo>@<sha12>.json = Verified commit graphs.
Writes results2/LABEL.jsonl rows {id, repo, set, rank, tokens, top_files, over_budget}.
"""
import json, subprocess, sys, tempfile
from collections import defaultdict
from pathlib import Path
here = Path(__file__).parent

def main(label, src, graphs, only="all"):
    commits = json.loads((here / "questions/commits.json").read_text())
    groups = defaultdict(list)
    for f in sorted((here / "questions").glob("*.jsonl")):
        for l in f.read_text().splitlines():
            groups[(f.stem, f"{graphs}/{f.stem}.json", "lite")].append(json.loads(l))
    for f in sorted((here / "questions_ext").glob("*.jsonl")):
        for l in f.read_text().splitlines():
            q = json.loads(l)
            groups[(f.stem, f"{graphs}/{f.stem}@{q['commit'][:12]}.json", "verified")].append(q)
    out = []
    with tempfile.TemporaryDirectory() as td:
        for i, ((repo, gpath, qset), qs) in enumerate(groups.items()):
            if only == "tune" and repo != "django": continue
            if only == "heldout" and repo == "django": continue
            qf = Path(td) / f"q{i}.jsonl"
            qf.write_text("".join(json.dumps({"question": q["question"], "files": q["files"]}) + "\n" for q in qs))
            p = subprocess.run([sys.executable, "-m", "graphify", "benchmark", gpath, "--questions", str(qf), "--json"],
                               capture_output=True, text=True, cwd=td, env={"PYTHONPATH": src, "PATH": "/usr/bin:/bin",
                                                                       "HOME": str(Path.home())})
            if p.returncode != 0:
                print(f"FAILED {repo} {gpath}: {p.stderr[-300:]}", file=sys.stderr); continue
            res = json.loads(p.stdout[p.stdout.find("{"):])
            assert len(res["per_question"]) == len(qs)
            for q, r in zip(qs, res["per_question"]):
                assert r["question"] == q["question"]
                out.append({"id": q["id"], "repo": repo, "set": qset, "rank": r["rank"], "tokens": r["tokens"],
                            "top_files": r["top_files"], "over_budget": r["over_budget"]})
    (here / "results2").mkdir(exist_ok=True)
    (here / "results2" / f"{label}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
    print(f"{label}: {len(out)} questions", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:])
