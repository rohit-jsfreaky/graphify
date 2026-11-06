"""Aggregate the per-query results of evaluate.py into tables and statistics.

Usage: python report.py <results_dir>
Writes <results_dir>/summary.json and <results_dir>/tables.md
"""
from __future__ import annotations

import gzip
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPOS = ["django", "flask", "requests", "hono", "jsoup", "caddy"]
KS = (5, 10, 20)
MAIN = [
    ("floor_same_dir", "Floor: same directory"),
    ("v8_d1", "v8 affected, depth 1"),
    ("v8_d2", "v8 affected, depth 2 (default)"),
    ("v8_d3", "v8 affected, depth 3"),
    ("cc_s2_3y", "Co-change, support>=2, 3y"),
    ("cc_s3_3y", "Co-change, support>=3, 3y"),
    ("cc_s2d_3y", "Co-change, support>=2, 3y, decay"),
    ("comb_union_graph_first", "Union: v8 d2 first, co-change fills"),
    ("comb_union_cc_first", "Union: co-change first, v8 d2 fills"),
    ("comb_fusion", "Fusion: 0.5 conf + 0.5/depth (HEADLINE)"),
    ("comb_rrf", "Fusion: reciprocal rank (RRF)"),
    ("comb_fusion_d1", "Fusion with v8 depth 1"),
    ("undirected_d1", "Extra: graph both directions, depth 1"),
    ("undirected_d2", "Extra: graph both directions, depth 2"),
    ("comb_fusion_undirected_d2", "Extra: fusion, both-directions graph + co-change"),
]
CATS = ["source", "test", "config", "docs", "other"]
CAT_LABEL = {"source": "source code", "test": "test", "config": "config/build",
             "docs": "docs", "other": "migrations/templates/other"}


def load(results: Path):
    qs = []
    runs = {}
    for r in REPOS:
        p = results / f"{r}.queries.jsonl.gz"
        if not p.exists():
            continue
        runs[r] = json.loads((results / f"{r}.run.json").read_text())
        with gzip.open(p, "rt", encoding="utf-8") as fh:
            qs += [json.loads(line) for line in fh]
    return qs, runs


def m(q, pred, k):
    top = q["pred"][pred][:k]
    truth = set(q["truth"])
    h = sum(1 for f in top if f in truth)
    return h / len(truth), h / k, 1.0 if h else 0.0


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def binom_two_sided(b, c):
    """Exact two-sided sign/McNemar p-value for b vs c discordant pairs."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    lp = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) - n * math.log(2)
          for i in range(0, k + 1)]
    mx = max(lp)
    p = 2 * math.exp(mx) * sum(math.exp(x - mx) for x in lp)
    return min(1.0, p)


def table_main(qs, by_repo, repos):
    rows = {}
    for pred, _ in MAIN:
        rows[pred] = {}
        for r in repos + ["ALL (repo mean)", "ALL (pooled)"]:
            if r == "ALL (repo mean)":
                vals = {key: mean(rows[pred][rr][key] for rr in repos) for key in rows[pred][repos[0]]}
            else:
                sub = qs if r == "ALL (pooled)" else by_repo[r]
                vals = {}
                for k in KS:
                    ms = [m(q, pred, k) for q in sub]
                    vals[f"R@{k}"] = mean(x[0] for x in ms)
                    vals[f"P@{k}"] = mean(x[1] for x in ms)
                    vals[f"hit@{k}"] = mean(x[2] for x in ms)
            rows[pred][r] = vals
    return rows


def mcnemar(qs, a, b, k=10):
    a_only = b_only = both = neither = 0
    for q in qs:
        ha, hb = m(q, a, k)[2], m(q, b, k)[2]
        if ha and hb:
            both += 1
        elif ha:
            a_only += 1
        elif hb:
            b_only += 1
        else:
            neither += 1
    return {"a_only": a_only, "b_only": b_only, "both": both, "neither": neither,
            "p": binom_two_sided(a_only, b_only)}


def commit_sign(qs, a, b, k=10):
    """Commit-level sign test on mean recall@k (seeds in a commit are not independent)."""
    per = defaultdict(lambda: [[], []])
    for q in qs:
        per[(q["repo"], q["sha"])][0].append(m(q, a, k)[0])
        per[(q["repo"], q["sha"])][1].append(m(q, b, k)[0])
    win = lose = tie = 0
    for xa, xb in per.values():
        d = mean(xa) - mean(xb)
        if d > 1e-12:
            win += 1
        elif d < -1e-12:
            lose += 1
        else:
            tie += 1
    return {"commits": len(per), "a_better": win, "b_better": lose, "tie": tie,
            "p": binom_two_sided(win, lose)}


def bootstrap_diff(by_repo, repos, a, b, k=10, n_boot=2000, seed=0):
    """Commit-cluster bootstrap CI of repo-mean recall@k difference a - b."""
    rng = random.Random(seed)
    groups = {}
    for r in repos:
        per = defaultdict(list)
        for q in by_repo[r]:
            per[q["sha"]].append(m(q, a, k)[0] - m(q, b, k)[0])
        groups[r] = list(per.values())
    stats = []
    for _ in range(n_boot):
        rm = []
        for r in repos:
            g = groups[r]
            sample = [g[rng.randrange(len(g))] for _ in range(len(g))]
            flat = [x for c in sample for x in c]
            rm.append(mean(flat))
        stats.append(mean(rm))
    stats.sort()
    point = mean(mean(x for c in groups[r] for x in c) for r in repos)
    return {"diff": point, "ci95": [stats[int(0.025 * n_boot)], stats[int(0.975 * n_boot) - 1]]}


def by_category(qs, preds, k=10):
    out = {}
    for pred in preds:
        found, total = Counter(), Counter()
        for q in qs:
            top = set(q["pred"][pred][:k])
            for f, c in zip(q["truth"], q["truth_cat"]):
                total[c] += 1
                found[c] += f in top
        out[pred] = {c: (found[c] / total[c] if total[c] else float("nan")) for c in CATS}
        out[pred]["_n"] = dict(total)
    return out


def fmt(x):
    return "n/a" if x != x else f"{x:.3f}"


def main():
    results = Path(sys.argv[1])
    qs, runs = load(results)
    repos = [r for r in REPOS if r in runs]
    by_repo = {r: [q for q in qs if q["repo"] == r] for r in repos}
    summary = {"repos": repos, "n_queries": {r: len(by_repo[r]) for r in repos}}
    md = []

    # ---- dataset
    md.append("## Dataset\n")
    md.append("| repo | HEAD | cut T (date) | test commits after T | in 2-20 files | used (>=1 query) | queries (seed files) | true files / query | share of changed files new since T | seeds in graph |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in repos:
        run = runs[r]
        st = run["stats"]
        sub = by_repo[r]
        newshare = sum(q["n_new_files"] for q in sub) / max(1, sum(q["n_files"] for q in sub))
        import datetime as dt
        tdate = dt.datetime.fromtimestamp(run["t_ts"], dt.timezone.utc).date().isoformat()
        md.append(f"| {r} | {run['head'][:9]} | {run['cut'][:9]} ({tdate}) | {st['commits_total']} | {st['commits_in_size']} | {st['commits_used']} | {len(sub)} | {mean(len(q['truth']) for q in sub):.1f} | {newshare:.1%} | {mean(q['seed_in_graph'] for q in sub):.0%} |")
    md.append("")

    # ---- main table
    rows = table_main(qs, by_repo, repos)
    summary["main"] = rows
    for scope in ["ALL (repo mean)", "ALL (pooled)"] + repos:
        n = len(qs) if scope.startswith("ALL") else len(by_repo[scope])
        md.append(f"### {scope} — {n} queries\n")
        md.append("| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |")
        md.append("|---|---|---|---|---|---|---|---|---|---|")
        for pred, label in MAIN:
            v = rows[pred][scope]
            md.append(f"| {label} | " + " | ".join(fmt(v[f"{x}@{k}"]) for x in ("R", "P", "hit") for k in KS) + " |")
        md.append("")

    # ---- graph ceiling
    md.append("## v8 `affected` depth 2 without a cut-off (all files it returns)\n")
    md.append("| repo | mean files returned | recall over all returned files | share of queries returning nothing |")
    md.append("|---|---|---|---|")
    for r in repos:
        sub = by_repo[r]
        md.append(f"| {r} | {mean(q['v8_d2_size'] for q in sub):.1f} | {mean(len(q['v8_d2_all_hits'])/len(q['truth']) for q in sub):.3f} | {mean(q['v8_d2_size']==0 for q in sub):.0%} |")
    md.append("")

    # ---- paired tests
    md.append("## Paired tests on hit@10 (McNemar, exact) and commit-level sign test on recall@10\n")
    md.append("| comparison | scope | queries both hit | only A hit | only B hit | McNemar p | commits A better | B better | tie | sign p |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    pairs = [("comb_fusion", "v8_d2"), ("comb_union_graph_first", "v8_d2"),
             ("comb_union_cc_first", "v8_d2"), ("comb_rrf", "v8_d2"), ("cc_s2_3y", "v8_d2"),
             ("comb_fusion", "cc_s2_3y"), ("comb_union_cc_first", "cc_s2_3y"),
             ("comb_fusion_undirected_d2", "undirected_d2")]
    summary["tests"] = {}
    for a, b in pairs:
        for scope in ["ALL"] + repos:
            sub = qs if scope == "ALL" else by_repo[scope]
            t = mcnemar(sub, a, b)
            s = commit_sign(sub, a, b)
            summary["tests"][f"{a} vs {b} [{scope}]"] = {"mcnemar": t, "sign": s}
            md.append(f"| A={a} vs B={b} | {scope} | {t['both']} | {t['a_only']} | {t['b_only']} | {t['p']:.2g} | {s['a_better']} | {s['b_better']} | {s['tie']} | {s['p']:.2g} |")
    md.append("")
    md.append("Commit-cluster bootstrap (2000 resamples), repo-mean recall@10 difference:\n")
    for a, b in pairs:
        bd = bootstrap_diff(by_repo, repos, a, b)
        summary["tests"][f"bootstrap {a} - {b}"] = bd
        md.append(f"- {a} − {b}: {bd['diff']:+.3f} (95% CI {bd['ci95'][0]:+.3f} … {bd['ci95'][1]:+.3f})")
    md.append("")

    # ---- category breakdown
    cat_preds = ["floor_same_dir", "v8_d2", "undirected_d2", "cc_s2_3y", "comb_fusion",
                 "comb_union_graph_first", "comb_union_cc_first", "comb_rrf", "comb_fusion_undirected_d2"]
    md.append("## Recall@10 by kind of true file (pooled over all queries)\n")
    cb = by_category(qs, cat_preds)
    summary["by_category"] = cb
    md.append("| predictor | " + " | ".join(f"{CAT_LABEL[c]} (n={cb['v8_d2']['_n'].get(c, 0)})" for c in CATS) + " |")
    md.append("|---|" + "---|" * len(CATS))
    for p in cat_preds:
        md.append(f"| {p} | " + " | ".join(fmt(cb[p][c]) for c in CATS) + " |")
    md.append("")
    md.append("Share of true files that have any node in the v8 graph, by kind:\n")
    tig = defaultdict(list)
    for q in qs:
        for c, ing in zip(q["truth_cat"], q["truth_in_graph"]):
            tig[c].append(ing)
    md.append("| " + " | ".join(CAT_LABEL[c] for c in CATS) + " |")
    md.append("|" + "---|" * len(CATS))
    md.append("| " + " | ".join(f"{mean(tig[c]):.0%}" if tig[c] else "n/a" for c in CATS) + " |")
    md.append("")
    md.append("Recall@10 by kind of true file, per repo (v8_d2 → comb_fusion):\n")
    md.append("| repo | " + " | ".join(CAT_LABEL[c] for c in CATS) + " |")
    md.append("|---|" + "---|" * len(CATS))
    summary["by_category_repo"] = {}
    for r in repos:
        cr = by_category(by_repo[r], ["v8_d2", "cc_s2_3y", "comb_fusion"])
        summary["by_category_repo"][r] = cr
        cells = []
        for c in CATS:
            n = cr["v8_d2"]["_n"].get(c, 0)
            cells.append("—" if not n else f"{fmt(cr['v8_d2'][c])} → {fmt(cr['comb_fusion'][c])} (n={n})")
        md.append(f"| {r} | " + " | ".join(cells) + " |")
    md.append("")

    # ---- seed kind
    md.append("## By kind of seed file (pooled R@10 / hit@10)\n")
    md.append("| seed kind | queries | v8_d2 R@10 | undirected_d2 R@10 | cc_s2_3y R@10 | comb_fusion R@10 | comb_union_cc_first R@10 | v8_d2 hit@10 | comb_fusion hit@10 | comb_union_cc_first hit@10 |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for c in CATS:
        sub = [q for q in qs if q["seed_cat"] == c]
        if not sub:
            continue
        md.append(f"| {CAT_LABEL[c]} | {len(sub)} | " + " | ".join(
            fmt(mean(m(q, p, 10)[i] for q in sub)) for i, p in ((0, "v8_d2"), (0, "undirected_d2"), (0, "cc_s2_3y"), (0, "comb_fusion"), (0, "comb_union_cc_first"),
                         (2, "v8_d2"), (2, "comb_fusion"), (2, "comb_union_cc_first"))) + " |")
    md.append("")

    # ---- cold start
    md.append("## Cold start: history window before T (R@10 / hit@10, repo mean)\n")
    md.append("| repo | cc 3 months | cc 1 year | cc 3 years | fusion 3 months | fusion 1 year | fusion 3 years | v8_d2 | seeds with any rule (3m / 1y / 3y) |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    summary["cold_start"] = {}
    for r in repos + ["ALL"]:
        cells = []
        vals = {}
        for p in ["cc_s2_3m", "cc_s2_1y", "cc_s2_3y", "comb_fusion_3m", "comb_fusion_1y", "comb_fusion", "v8_d2"]:
            if r == "ALL":
                rr = mean(mean(m(q, p, 10)[0] for q in by_repo[x]) for x in repos)
                hh = mean(mean(m(q, p, 10)[2] for q in by_repo[x]) for x in repos)
            else:
                rr = mean(m(q, p, 10)[0] for q in by_repo[r])
                hh = mean(m(q, p, 10)[2] for q in by_repo[r])
            vals[p] = (rr, hh)
            cells.append(f"{rr:.3f} / {hh:.2f}")
        sub = qs if r == "ALL" else by_repo[r]
        cov = " / ".join(f"{mean(bool(q['pred'][f'cc_s2_{w}']) for q in sub):.0%}" for w in ("3m", "1y", "3y"))
        summary["cold_start"][r] = vals
        md.append(f"| {r} | " + " | ".join(cells) + f" | {cov} |")
    md.append("")

    # ---- cost
    md.append("## Cost of mining (3-year window) and of the stored rules\n")
    md.append("| repo | commits mined | bulk skipped (>30 files) | git log seconds | counting seconds | total seconds | files with history | pairs support>=2 | stored JSON bytes | gzip bytes | graph build seconds (v8, for scale) | graph nodes |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    summary["cost"] = {}
    for r in repos:
        c = runs[r]["cost"]
        summary["cost"][r] = c
        md.append(f"| {r} | {c['commits_used_3y']} | {c['bulk_skipped_3y']} | {c['git_log_seconds_3y']} | {c['count_seconds_3y']} | {c['mine_total_seconds_3y']} | {c['files_with_history_3y']} | {c['pairs_support2_3y']} | {c['store_bytes_3y']:,} | {c['store_bytes_gz_3y']:,} | {runs[r]['graph_build_seconds']} | {c['graph_nodes']:,} |")
    md.append("")
    md.append("Seed resolution for v8 `affected` (how the seed file was mapped to a node):\n")
    for r in repos:
        md.append(f"- {r}: {runs[r]['cost']['seed_resolution']}")
    md.append("")

    (results / "tables.md").write_text("\n".join(md) + "\n")
    (results / "summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True, default=str))
    print("\n".join(md))


if __name__ == "__main__":
    main()
