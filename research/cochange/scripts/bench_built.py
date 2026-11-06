"""Before/after benchmark on the BUILT feature (branch claude/affected-cochange).

Unlike evaluate.py (the study's own predictors), this drives the shipped code:
`graphify update` has already written graph.json and cochange.json at the cut
commit T (see run_all.sh), and every query calls `affected_payload`, the
function `graphify affected --json` prints, with the shipped defaults
(depth 2, confidence >= 0.2, top 10 co-change items).

Test commits, seeds and truth are replayed exactly as in evaluate.py.

Rows (top-k files):
  before            graph items only (v8 behaviour; must equal the study's v8 row)
  after_printed     the order the text report prints: graph items, then the
                    co-change section
  after_cc_first    co-change items first, then graph items (merge by the
                    `source` tag, the ranking the study found best)
  section_view      first k graph files PLUS the whole co-change section
                    (what a reader sees when reading k graph lines and the
                    section); it shows up to k + 10 files, see `shown`

Usage: python bench_built.py <repo_checkout> <worktree_at_T> <results_dir> <name>
"""
from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import TEST_MAX_FILES, TEST_MIN_FILES, category, excluded, git, is_code, log_commits  # noqa: E402

from graphify.affected import affected_payload, load_graph, resolve_seed  # noqa: E402
from graphify.git_cochange import FILE_NAME, load_cochange  # noqa: E402

KS = (5, 10, 20)


def main() -> None:
    repo, wt, outdir, name = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
    meta = json.loads((outdir / f"{name}.meta.json").read_text())
    T, HEAD = meta["cut"], meta["head"]
    files_at_t = set(git(repo, "ls-tree", "-r", "--name-only", T).splitlines())
    graph = load_graph(wt / "graphify-out" / "graph.json")
    cochange = load_cochange(wt / "graphify-out" / FILE_NAME)
    assert cochange is not None and cochange["rev"].startswith(T[:7]), "cochange.json missing or not at T"

    rows: dict[str, list] = {r: [] for r in ("before", "after_printed", "after_cc_first", "section_view")}
    per_query = []
    stats = Counter()
    t0 = time.perf_counter()
    cache: dict = {}
    for c in reversed(log_commits(repo, [f"{T}..{HEAD}"])):
        entries = []
        for st, old, new in c["entries"]:
            if st == "R100" or excluded(new):
                continue
            at_t = old if st[0] in "RMDT" else None
            if at_t is not None and at_t not in files_at_t:
                at_t = None
            entries.append(at_t)
        if not (TEST_MIN_FILES <= len(entries) <= TEST_MAX_FILES):
            continue
        for seed_file in sorted({a for a in entries if a and is_code(a)}):
            truth = sorted({a for a in entries if a and a != seed_file})
            if not truth:
                continue
            if seed_file not in cache:
                seed = resolve_seed(graph, seed_file, wt)  # exactly what the CLI resolves
                if seed is None:
                    stats["seed_unresolved"] += 1
                    cache[seed_file] = ([], [])
                else:
                    payload = affected_payload(graph, seed, root=wt, cochange=cochange, cochange_state="ok")
                    g, co = [], []
                    for item in payload["results"]:
                        f = item["file"]
                        if not f or f == seed_file:
                            continue
                        target = g if item["source"] == "graph" else co
                        if f not in target:
                            target.append(f)
                    cache[seed_file] = (g, co)
            g, co = cache[seed_file]
            printed = g + [f for f in co if f not in g]
            cc_first = co + [f for f in g if f not in co]
            ts = set(truth)
            vals = {}
            for row, lst in (("before", g), ("after_printed", printed), ("after_cc_first", cc_first)):
                v = []
                for k in KS:
                    h = sum(1 for f in lst[:k] if f in ts)
                    v += [h / len(ts), h / k, 1.0 if h else 0.0]
                rows[row].append(v)
                vals[row] = v
            v = []
            for k in KS:
                shown = list(dict.fromkeys(g[:k] + co))
                h = sum(1 for f in shown if f in ts)
                v += [h / len(ts), len(shown), 1.0 if h else 0.0]
            rows["section_view"].append(v)
            per_query.append({"sha": c["sha"], "seed": seed_file, "truth": truth,
                              "truth_cat": [category(f) for f in truth], "graph": g[:20], "cochange": co})
    elapsed = time.perf_counter() - t0
    summary = {"repo": name, "queries": len(per_query), "seconds": round(elapsed, 1), "stats": dict(stats),
               "cochange_rev": cochange["rev"], "cochange_commits_used": cochange["commits_used"]}
    for row, vals in rows.items():
        m = [sum(col) / len(col) for col in zip(*vals)]
        if row == "section_view":
            summary[row] = {f"R@{k}": m[3 * i] for i, k in enumerate(KS)} | \
                           {f"shown@{k}": m[3 * i + 1] for i, k in enumerate(KS)} | \
                           {f"hit@{k}": m[3 * i + 2] for i, k in enumerate(KS)}
        else:
            summary[row] = {f"R@{k}": m[3 * i] for i, k in enumerate(KS)} | \
                           {f"P@{k}": m[3 * i + 1] for i, k in enumerate(KS)} | \
                           {f"hit@{k}": m[3 * i + 2] for i, k in enumerate(KS)}
    (outdir / f"{name}.built.json").write_text(json.dumps(summary, indent=1, sort_keys=True))
    import gzip
    with gzip.open(outdir / f"{name}.built_queries.jsonl.gz", "wt", encoding="utf-8") as fh:
        for q in per_query:
            fh.write(json.dumps(q, sort_keys=True) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
