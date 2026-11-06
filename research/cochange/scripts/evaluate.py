"""Co-change vs. graph `affected` study: per-repo prediction run.

For one repo:
  * reads the cut commit T and the v8 graph built at T (see prepare.sh),
  * mines co-change from commits BEFORE T (windows: 3 months, 1 year, 3 years),
  * replays every test commit AFTER T: each changed code file is a seed, the
    other files changed in that commit are the truth,
  * writes one JSON line per (commit, seed) query with the top-20 files of
    every predictor, plus a cost/metadata JSON.

Aggregation and statistics live in report.py.

All choices below were fixed before looking at test results:
  - headline co-change predictor: `cc_s2` (3-year window, min support 2,
    confidence ranking, no decay);
  - headline combined predictor: `comb_fusion` (0.5 * confidence +
    0.5 * 1/graph_depth over v8 `affected` depth 2 and `cc_s2`).
Everything else is reported as a variant.

Usage: python evaluate.py <repo_checkout> <worktree_at_T> <results_dir> <name>
"""
from __future__ import annotations

import gzip
import json
import math
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path, PurePosixPath

from graphify.affected import (
    DEFAULT_AFFECTED_RELATIONS,
    affected_nodes,
    load_graph,
    resolve_seed,
)

K_MAX = 20
DAY = 86400
WINDOWS = {"3m": 91 * DAY, "1y": 365 * DAY, "3y": 3 * 365 * DAY}
MAX_TRAIN_FILES = 30          # skip bulk commits when mining (same as PR #4544)
TEST_MIN_FILES, TEST_MAX_FILES = 2, 20
DECAY_HALF_LIFE = 180 * DAY

# ---------------------------------------------------------------- file classes

LOCKFILES = {
    "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml",
    "bun.lock", "bun.lockb", "poetry.lock", "uv.lock", "pipfile.lock", "pdm.lock",
    "go.sum", "cargo.lock", "composer.lock", "gemfile.lock",
}
GENERATED_SUFFIXES = (".min.js", ".min.css", ".map", ".mo", ".pb.go", "_pb2.py",
                      ".snap", ".pyc")
EXCLUDED_DIRS = {"node_modules", "vendor", "third_party", "dist", "__snapshots__",
                 ".yarn", "site-packages"}

CODE_EXT = {".py", ".pyi", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".mts",
            ".cts", ".java", ".kt", ".go", ".c", ".h", ".cc", ".cpp", ".rs",
            ".rb", ".php", ".cs", ".swift", ".scala"}
TEST_DIRS = {"test", "tests", "testing", "__tests__", "spec", "specs", "testdata",
             "caddytest", "integration"}
DOC_EXT = {".md", ".rst", ".txt", ".adoc", ".mdx"}
DOC_NAMES = {"changes", "changelog", "authors", "readme", "license", "notice",
             "contributing", "history", "security"}
CONFIG_NAMES = {"setup.py", "setup.cfg", "pyproject.toml", "tox.ini", "package.json",
                "pom.xml", "go.mod", "makefile", "dockerfile", "manifest.in",
                "jsr.json", "requirements.txt", ".gitignore", ".gitattributes",
                ".editorconfig", "noxfile.py", "conftest.py", "build.gradle",
                "caddyfile", "eslint.config.js", "eslint.config.mjs",
                "vitest.config.ts", "bunfig.toml", ".goreleaser.yml",
                ".golangci.yml", ".pre-commit-config.yaml", ".readthedocs.yaml"}
CONFIG_EXT = {".yml", ".yaml", ".toml", ".ini", ".cfg", ".json", ".sh", ".lock"}
OTHER_DIRS = {"migrations", "templates", "template", "static", "locale", "fixtures",
              "resources"}
OTHER_EXT = {".html", ".htm", ".jinja", ".j2", ".tmpl", ".po", ".css", ".svg",
             ".png", ".jpg", ".gif", ".ico", ".xml"}


def excluded(path: str) -> bool:
    p = PurePosixPath(path)
    name = p.name.lower()
    if name in LOCKFILES or name.endswith(GENERATED_SUFFIXES):
        return True
    return any(part in EXCLUDED_DIRS for part in p.parts[:-1])


def category(path: str) -> str:
    """source | test | config | docs | other (migrations/templates/assets/...)."""
    p = PurePosixPath(path)
    parts = [x.lower() for x in p.parts]
    name = parts[-1]
    stem, ext = os.path.splitext(name)
    if (any(x in TEST_DIRS for x in parts[:-1]) or name.startswith("test_")
            or re.search(r"(_test\.(go|py)|\.(test|spec)\.[cm]?[jt]sx?|tests?\.java)$", name)):
        return "test"
    if any(x in OTHER_DIRS for x in parts[:-1]) and name != "__init__.py" or ext in OTHER_EXT:
        return "other"
    if ext in DOC_EXT and name != "requirements.txt" or stem in DOC_NAMES or "docs" in parts[:-1] or "doc" in parts[:-1]:
        return "docs"
    if name in CONFIG_NAMES or parts[0] in {".github", ".circleci", "scripts", ".devcontainer"} or ext in CONFIG_EXT:
        return "config"
    if ext in CODE_EXT:
        return "source"
    return "other"


def is_code(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in CODE_EXT


# ---------------------------------------------------------------- git

def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-c", "core.quotepath=false", "-C", str(repo), *args],
                          check=True, capture_output=True).stdout.decode("utf-8", "replace")


def log_commits(repo: Path, rev_range: list[str]) -> list[dict]:
    """Non-merge commits with name-status (renames detected), newest first."""
    out = git(repo, "log", "--no-merges", "-M", "--name-status",
              "--format=%x1e%H%x1f%ct", *rev_range, "--")
    commits = []
    for rec in out.split("\x1e"):
        lines = [ln for ln in rec.splitlines() if ln.strip()]
        if not lines:
            continue
        sha, ts = lines[0].split("\x1f")
        entries = []
        for ln in lines[1:]:
            cols = ln.split("\t")
            st = cols[0]
            if st[0] in "RC":
                entries.append((st, cols[1], cols[2]))
            else:
                entries.append((st, cols[1], cols[1]))
        commits.append({"sha": sha, "ts": int(ts), "entries": entries})
    return commits


# ---------------------------------------------------------------- co-change mining

def mine(train: list[dict], files_at_t: set[str], t_ts: int, window: int):
    """Count commits per file and per file pair, following renames to T's names.

    `train` is newest-first. Returns (n, pair, n_w, pair_w, n_commits_used,
    n_bulk_skipped); *_w are recency-weighted (half-life 180 days).
    """
    alias: dict[str, str] = {}   # historical path -> path at T
    n: Counter = Counter()
    pair: Counter = Counter()
    n_w: defaultdict = defaultdict(float)
    pair_w: defaultdict = defaultdict(float)
    used = skipped = 0
    for c in train:
        if t_ts - c["ts"] > window:
            break
        files = set()
        for st, old, new in c["entries"]:
            if st.startswith("R") and st == "R100":
                pass  # pure rename: no content coupling, but still record the alias
            else:
                cur = alias.get(new, new)
                if not excluded(cur):
                    files.add(cur)
        for st, old, new in c["entries"]:
            if st.startswith("R"):
                alias[old] = alias.get(new, new)
        files = sorted(f for f in files if f in files_at_t)
        if not files:
            continue
        if len(files) > MAX_TRAIN_FILES:
            skipped += 1
            continue
        used += 1
        w = 0.5 ** ((t_ts - c["ts"]) / DECAY_HALF_LIFE)
        for f in files:
            n[f] += 1
            n_w[f] += w
        for a, b in combinations(files, 2):
            pair[(a, b)] += 1
            pair_w[(a, b)] += w
    return n, pair, n_w, pair_w, used, skipped


def build_rules(n, pair, n_w, pair_w, min_support: int, decay: bool):
    """seed -> ranked list of (file, confidence, support)."""
    nbrs: dict[str, list] = defaultdict(list)
    for (a, b), s in pair.items():
        if s < min_support:
            continue
        for x, y in ((a, b), (b, a)):
            conf = (pair_w[(a, b)] / n_w[x]) if decay else (s / n[x])
            nbrs[x].append((y, conf, s))
    for x in nbrs:
        nbrs[x].sort(key=lambda r: (-r[1], -r[2], r[0]))
    return nbrs


# ---------------------------------------------------------------- graph predictors

class GraphPredictor:
    def __init__(self, graph_path: Path, root: Path, files_at_t: set[str]):
        self.g = load_graph(graph_path)
        self.root = root
        self.files_at_t = files_at_t
        self.by_file: dict[str, list[str]] = defaultdict(list)
        for nid, d in self.g.nodes(data=True):
            sf = d.get("source_file")
            if sf:
                self.by_file[str(sf)].append(str(nid))
        self.cache: dict = {}
        self.resolve_stats: Counter = Counter()
        self._file_adj = None

    def seed_nodes(self, path: str) -> tuple[list[str], str]:
        s = resolve_seed(self.g, path, self.root)
        if s is not None and self.g.nodes[s].get("source_file") == path:
            return [s], "resolve_seed"
        nodes = self.by_file.get(path, [])
        if nodes:
            return sorted(nodes), "all_nodes_of_file"
        return [], "not_in_graph"

    def affected_files(self, path: str, depth: int) -> list[tuple[str, int]]:
        """v8 `affected` from the seed file, mapped to files in CLI (BFS) order."""
        key = (path, depth)
        if key in self.cache:
            return self.cache[key]
        seeds, how = self.seed_nodes(path)
        if depth == 2:
            self.resolve_stats[how] += 1
        best: dict[str, int] = {}
        order: list[str] = []
        for s in seeds:
            for h in affected_nodes(self.g, s, depth=depth):
                f = self.g.nodes[h.node_id].get("source_file")
                if not f or f == path or f not in self.files_at_t:
                    continue
                if f not in best:
                    best[f] = h.depth
                    order.append(f)
                else:
                    best[f] = min(best[f], h.depth)
        if len(seeds) > 1:  # merged walks: re-sort by depth, keep first-seen order
            order.sort(key=lambda f: best[f])
        res = [(f, best[f]) for f in order]
        self.cache[key] = res
        return res

    def file_adjacency(self):
        if self._file_adj is None:
            rels = set(DEFAULT_AFFECTED_RELATIONS)
            adj: dict[str, Counter] = defaultdict(Counter)
            for u, v, d in self.g.edges(data=True):
                if str(d.get("relation", "")) not in rels:
                    continue
                fu = self.g.nodes[u].get("source_file")
                fv = self.g.nodes[v].get("source_file")
                if fu and fv and fu != fv:
                    adj[fu][fv] += 1
                    adj[fv][fu] += 1
            self._file_adj = adj
        return self._file_adj

    def undirected_files(self, path: str, depth: int) -> list[tuple[str, int]]:
        """Extra baseline: file-level neighbours in BOTH directions (not v8 behaviour)."""
        adj = self.file_adjacency()
        seen = {path}
        out = []
        frontier = [path]
        for d in range(1, depth + 1):
            cand: Counter = Counter()
            for f in frontier:
                for g, w in adj.get(f, {}).items():
                    if g not in seen:
                        cand[g] += w
            ranked = sorted(cand, key=lambda g: (-cand[g], g))
            for g in ranked:
                seen.add(g)
                if g in self.files_at_t:
                    out.append((g, d))
            frontier = ranked
        return out


# ---------------------------------------------------------------- combination

def union(first: list[str], second: list[str]) -> list[str]:
    out, seen = [], set()
    for f in first + second:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out[:K_MAX]


def fusion(graph: list[tuple[str, int]], cc: list[tuple], w_cc: float = 0.5) -> list[str]:
    score: dict[str, float] = defaultdict(float)
    gr = {f: i for i, (f, _) in enumerate(graph)}
    sup = {}
    for f, d in graph:
        score[f] += (1 - w_cc) * (1.0 / d)
    for f, conf, s in cc:
        score[f] += w_cc * conf
        sup[f] = s
    return sorted(score, key=lambda f: (-score[f], -sup.get(f, 0), gr.get(f, 1e9), f))[:K_MAX]


def rrf(lists: list[list[str]], k0: int = 60) -> list[str]:
    score: dict[str, float] = defaultdict(float)
    for lst in lists:
        for i, f in enumerate(lst):
            score[f] += 1.0 / (k0 + i + 1)
    return sorted(score, key=lambda f: (-score[f], f))[:K_MAX]


# ---------------------------------------------------------------- main

def main() -> None:
    repo, wt, outdir, name = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
    meta = json.loads((outdir / f"{name}.meta.json").read_text())
    T, HEAD = meta["cut"], meta["head"]
    t_ts = int(git(repo, "log", "-1", "--format=%ct", T).strip())
    files_at_t = set(git(repo, "ls-tree", "-r", "--name-only", T).splitlines())

    # --- mining (timed: this is the cost a `graphify update` would pay)
    import datetime as _dt
    since = _dt.datetime.fromtimestamp(t_ts - WINDOWS["3y"] - 7 * DAY, _dt.timezone.utc).isoformat()
    t0 = time.perf_counter()
    train = log_commits(repo, [f"--since={since}", T])
    t_log = time.perf_counter() - t0
    mined = {}
    cost = {"git_log_seconds_3y": round(t_log, 2), "train_commits_listed_3y": len(train)}
    for wname, wlen in WINDOWS.items():
        t1 = time.perf_counter()
        n, pair, n_w, pair_w, used, skipped = mine(train, files_at_t, t_ts, wlen)
        rules = {
            "s2": build_rules(n, pair, n_w, pair_w, 2, False),
            "s3": build_rules(n, pair, n_w, pair_w, 3, False),
            "s2d": build_rules(n, pair, n_w, pair_w, 2, True),
            "s1": build_rules(n, pair, n_w, pair_w, 1, False),
        }
        mined[wname] = rules
        cost[f"count_seconds_{wname}"] = round(time.perf_counter() - t1, 2)
        cost[f"commits_used_{wname}"] = used
        cost[f"bulk_skipped_{wname}"] = skipped
        cost[f"files_with_history_{wname}"] = len(n)
        cost[f"pairs_support1_{wname}"] = len(pair)
        cost[f"pairs_support2_{wname}"] = sum(1 for s in pair.values() if s >= 2)
        if wname == "3y":
            # what we'd store: per-file commit count + pairs with support >= 2
            store = {"files": dict(sorted(n.items())),
                     "pairs": sorted([a, b, s] for (a, b), s in pair.items() if s >= 2)}
            raw = json.dumps(store, separators=(",", ":")).encode()
            cost["store_bytes_3y"] = len(raw)
            cost["store_bytes_gz_3y"] = len(gzip.compress(raw, 6))
            cost["mine_total_seconds_3y"] = round(t_log + cost["count_seconds_3y"], 2)

    # --- graph
    gp = GraphPredictor(wt / "graphify-out" / "graph.json", wt, files_at_t)
    cost["graph_nodes"] = gp.g.number_of_nodes()
    cost["graph_edges"] = gp.g.number_of_edges()
    graph_files = set(gp.by_file)

    # --- test commits
    tests = log_commits(repo, [f"{T}..{HEAD}"])
    stats = Counter()
    queries = []
    t_pred = time.perf_counter()
    for c in reversed(tests):  # oldest first, deterministic
        stats["commits_total"] += 1
        entries = []
        for st, old, new in c["entries"]:
            if st == "R100":
                continue  # pure rename
            if excluded(new):
                continue
            at_t = old if st[0] in "RMDT" else None  # A, C: new file
            if at_t is not None and at_t not in files_at_t:
                at_t = None  # created after T, unpredictable
            entries.append((new, at_t))
        if not (TEST_MIN_FILES <= len(entries) <= TEST_MAX_FILES):
            stats["commits_out_of_size"] += 1
            continue
        stats["commits_in_size"] += 1
        seeds = sorted({at for _, at in entries if at and is_code(at)})
        if not seeds:
            stats["commits_no_code_seed"] += 1
            continue
        used_commit = False
        for seed in seeds:
            truth = sorted({at for _, at in entries if at and at != seed})
            n_new = sum(1 for _, at in entries if at is None)
            if not truth:
                stats["queries_no_predictable_truth"] += 1
                continue
            used_commit = True
            preds: dict[str, list[str]] = {}
            g = {d: gp.affected_files(seed, d) for d in (1, 2, 3)}
            for d in (1, 2, 3):
                preds[f"v8_d{d}"] = [f for f, _ in g[d][:K_MAX]]
            full2 = {f for f, _ in g[2]}
            ud = {d: gp.undirected_files(seed, d) for d in (1, 2)}
            preds["undirected_d1"] = [f for f, _ in ud[1][:K_MAX]]
            preds["undirected_d2"] = [f for f, _ in ud[2][:K_MAX]]
            for wname, rules in mined.items():
                for rname, rl in rules.items():
                    preds[f"cc_{rname}_{wname}"] = [f for f, _, _ in rl.get(seed, [])[:K_MAX]]
            cc = mined["3y"]["s2"].get(seed, [])
            ccl = [f for f, _, _ in cc]
            v8 = [f for f, _ in g[2]]
            preds["comb_union_graph_first"] = union(v8, ccl)
            preds["comb_union_cc_first"] = union(ccl, v8)
            preds["comb_fusion"] = fusion(g[2], cc)
            preds["comb_rrf"] = rrf([v8, ccl])
            preds["comb_fusion_d1"] = fusion(g[1], cc)
            preds["comb_fusion_undirected_d2"] = fusion(ud[2], cc)
            for wname in ("3m", "1y"):
                ccw = mined[wname]["s2"].get(seed, [])
                preds[f"comb_fusion_{wname}"] = fusion(g[2], ccw)
            d = str(PurePosixPath(seed).parent)
            preds["floor_same_dir"] = sorted(
                f for f in files_at_t
                if f != seed and str(PurePosixPath(f).parent) == d and not excluded(f)
            )[:K_MAX]
            queries.append({
                "repo": name, "sha": c["sha"], "ts": c["ts"], "seed": seed,
                "seed_cat": category(seed), "seed_in_graph": seed in graph_files,
                "truth": truth, "truth_cat": [category(f) for f in truth],
                "truth_in_graph": [f in graph_files for f in truth],
                "n_new_files": n_new, "n_files": len(entries),
                "v8_d2_all_hits": sorted(full2 & set(truth)), "v8_d2_size": len(full2),
                "v8_d3_size": len(g[3]),
                "cc_conf": {f: round(conf, 3) for f, conf, _ in cc[:K_MAX]},
                "pred": preds,
            })
        if used_commit:
            stats["commits_used"] += 1
    cost["predict_seconds_all_queries"] = round(time.perf_counter() - t_pred, 1)
    cost["seed_resolution"] = dict(gp.resolve_stats)
    meta.update({"t_ts": t_ts, "files_at_t": len(files_at_t), "stats": dict(stats),
                 "n_queries": len(queries), "cost": cost})
    (outdir / f"{name}.run.json").write_text(json.dumps(meta, indent=2, sort_keys=True))
    with gzip.open(outdir / f"{name}.queries.jsonl.gz", "wt", encoding="utf-8") as fh:
        for q in queries:
            fh.write(json.dumps(q, sort_keys=True) + "\n")
    print(name, json.dumps(dict(stats)), "queries", len(queries), json.dumps(cost))


if __name__ == "__main__":
    main()
