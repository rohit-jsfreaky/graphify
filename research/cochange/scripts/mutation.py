"""Non-circular answer key: which test FILES fail when a function breaks?

For one repo at its checked-out commit C:
  1. graph: `graphify update . --no-cluster` was run at C (by the caller);
  2. co-change: mined with the BUILT miner from history strictly before C
     (`mine_cochange(repo, rev="C^")`), never from C itself;
  3. baseline: run the repo's own test suite on clean C; tests failing there
     are ignored;
  4. sample N real functions (deterministic seed) from the package source and,
     one at a time, insert `raise RuntimeError("mut")` as the first line of the
     body, run the full suite, and record which test files now fail;
  5. seed = the mutated function's file. Compare v8 `affected` (graph items)
     with v8 + co-change (built `affected_payload`), on recall@10/20 and hit@10
     of the failing test files.

Usage: python mutation.py <repo> <python_of_repo_venv> <src_dir_rel> <results_dir> <name> [n] [seed]
"""
from __future__ import annotations

import ast
import gzip
import json
import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path, PurePosixPath

from graphify.affected import affected_payload, load_graph, resolve_seed
from graphify.git_cochange import cochange_partners, mine_cochange

KS = (10, 20)
CLEAN_ENV = {k: v for k, v in os.environ.items()
             if k.lower() not in ("http_proxy", "https_proxy", "all_proxy", "no_proxy")}
CLEAN_ENV["PYTHONDONTWRITEBYTECODE"] = "1"
LINE = re.compile(r"^(FAILED|ERROR) (\S+?)(::|\s|$)")


def run_tests(repo: Path, python: str) -> tuple[set[str], set[str], float]:
    """Return (failing test ids, failing test files, seconds)."""
    t0 = time.perf_counter()
    proc = subprocess.run(
        [python, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:randomly",
         "--tb=no", "-rfE"],
        cwd=repo, capture_output=True, text=True, env=CLEAN_ENV, timeout=900,
    )
    ids, files = set(), set()
    for ln in proc.stdout.splitlines():
        m = LINE.match(ln)
        if m:
            nodeid = ln.split(" ", 1)[1].split(" - ")[0].strip()
            ids.add(nodeid)
            files.add(m.group(2))
    if proc.returncode not in (0, 1) and not files:
        files.add("<suite did not run>")
    return ids, files, time.perf_counter() - t0


def candidates(repo: Path, src: str) -> list[tuple[str, int, int, str]]:
    out = []
    for path in sorted((repo / src).rglob("*.py")):
        rel = path.relative_to(repo).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if isinstance(parents.get(node), (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue  # nested helper: skip, test the enclosing function instead
            decos = {ast.unparse(d) for d in node.decorator_list}
            if any("overload" in d or "abstractmethod" in d for d in decos):
                continue
            body = node.body
            first = body[0]
            if first.lineno <= node.lineno:
                continue  # one-line def
            stmts = [s for s in body if not (isinstance(s, ast.Expr) and isinstance(getattr(s, "value", None), ast.Constant))]
            if not stmts or all(isinstance(s, (ast.Pass,)) or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)) for s in stmts):
                continue  # stub
            out.append((rel, first.lineno, first.col_offset, node.name))
    return out


def main() -> None:
    repo, python, src, outdir, name = Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4]), sys.argv[5]
    n = int(sys.argv[6]) if len(sys.argv) > 6 else 40
    rnd = random.Random(int(sys.argv[7]) if len(sys.argv) > 7 else 2026)
    C = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--", src], capture_output=True, text=True).stdout
    assert not status.strip(), f"source tree not clean: {status}"

    graph = load_graph(repo / "graphify-out" / "graph.json")
    t0 = time.perf_counter()
    cochange = mine_cochange(repo, rev=f"{C}^")  # history BEFORE C only
    mine_s = time.perf_counter() - t0
    assert cochange["status"] == "ok"
    tests = sorted(p for p in subprocess.run(["git", "-C", str(repo), "ls-files", "tests"],
                                             capture_output=True, text=True).stdout.split()
                   if PurePosixPath(p).name.startswith("test_") and p.endswith(".py"))

    base_ids, base_files, base_s = run_tests(repo, python)
    pool = candidates(repo, src)
    picked = rnd.sample(pool, min(n, len(pool)))
    picked.sort()
    records = []
    for rel, line, col, fname in picked:
        path = repo / rel
        original = path.read_text(encoding="utf-8")
        lines = original.splitlines(keepends=True)
        lines.insert(line - 1, " " * col + 'raise RuntimeError("mut")\n')
        path.write_text("".join(lines), encoding="utf-8")
        try:
            ids, _files, secs = run_tests(repo, python)
        finally:
            path.write_text(original, encoding="utf-8")
        new_ids = ids - base_ids
        failing = sorted({i.split("::")[0] for i in new_ids if i.startswith("tests/")})
        if any(i == "<suite did not run>" for i in ids):
            failing = ["<suite did not run>"]
        seed = resolve_seed(graph, rel, repo)
        g, co = [], []
        if seed is not None:
            payload = affected_payload(graph, seed, root=repo, cochange=cochange, cochange_state="ok")
            for item in payload["results"]:
                f = item["file"]
                if not f or f == rel:
                    continue
                target = g if item["source"] == "graph" else co
                if f not in target:
                    target.append(f)
        # unthresholded co-change too, to see what the 0.2 floor costs here
        co_all = [p["file"] for p in cochange_partners(cochange, rel, min_confidence=0.0, top=50)]
        stem = PurePosixPath(rel).stem.lstrip("_")
        floor = [t for t in tests if stem and stem in PurePosixPath(t).stem]
        records.append({"file": rel, "line": line, "function": fname, "failing": failing,
                        "seconds": round(secs, 1), "seed_resolved": seed is not None,
                        "graph": g, "cochange": co, "cochange_all": co_all, "name_floor": floor})
        print(f"{rel}:{line} {fname}: {len(failing)} failing files", flush=True)
    meta = {"repo": name, "commit": C, "cochange_rev": cochange["rev"], "cochange_commits_used": cochange["commits_used"],
            "mine_seconds": round(mine_s, 2), "baseline_failing_tests": sorted(base_ids),
            "baseline_seconds": round(base_s, 1), "candidates": len(pool), "sampled": len(picked),
            "test_files": len(tests)}
    (outdir / f"{name}.mutation_meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True))
    with gzip.open(outdir / f"{name}.mutation.jsonl.gz", "wt", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    print(json.dumps(meta)[:500])


if __name__ == "__main__":
    main()
