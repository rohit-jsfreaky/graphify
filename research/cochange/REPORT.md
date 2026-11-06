# Does git co-change make `graphify affected` better?

Research only. No feature code. Branch `claude/cochange-study`, based on upstream `v8`
at `16218bf`.

## Short answer

**Yes, clearly.** On 6 real repos (2,070 test queries from 701 real commits made after
the cut date), adding co-change to `affected` more than doubles how many of the
really-changed files show up in the top 10:

| (repo mean, k = 10) | recall@10 | precision@10 | hit@10 (at least one true file) |
|---|---|---|---|
| Floor: files in the same directory | 0.267 | 0.123 | 0.494 |
| **v8 `affected`, depth 2 (default)** | **0.180** | 0.079 | **0.341** |
| Co-change only (3 years, support ≥ 2) | 0.485 | 0.136 | 0.736 |
| **Combined: co-change first, graph fills the rest** | **0.521** | 0.168 | **0.783** |
| Combined: score fusion (pre-declared headline) | 0.468 | 0.150 | 0.725 |

- Every combined variant beats v8 in every repo. Paired test on hit@10, all queries:
  combined (co-change first) finds something v8 misses in **946** queries, v8 finds
  something it misses in **22** (McNemar p ≈ 1e-247). Commit-level sign test: 545
  commits better, 14 worse. Bootstrap 95% CI for the recall@10 gain: **+0.30 … +0.40**.
- It still holds when the seed is a **source file** (not a test): recall@10
  0.293 → 0.525, hit@10 0.505 → 0.791 (316 vs 21 discordant queries).
- Co-change wins most on **non-code**: docs recall@10 0.017 → 0.370, config/build
  0.015 → 0.190. But it also wins on code, mainly because `affected` only walks
  *reverse* edges (who depends on me), and people also edit what the seed depends on.
- It is cheap: mining 3 years of Django history takes **0.3 s** and stores **305 KB**
  of JSON (34 KB gzipped). The v8 graph build for the same Django tree takes 75 s.
- It needs history: with only 3 months, co-change alone is *worse* than the graph
  (0.125 vs 0.180 recall@10). Combined is still better than the graph alone (0.274),
  so the combined design does not hurt young repos.

Important caveat (read "What I am unsure about"): the answer key is "files changed in
the same commit". That is exactly the signal co-change learns from, so this test
favours co-change by its nature. It is the standard test in the papers, and it matches
the question "what else will I have to touch", but it is not the same question as
"what could break".

## 1. Prior art and what graphify already does

### How `affected` works (v8)

- CLI: `graphify affected "<node-or-label>" [--relation R] [--depth N] [--graph path]`,
  `graphify/cli.py:2117`. Default depth **2**.
- Code: `graphify/affected.py`. `resolve_seed` maps a file path to its file node
  (`source_location == L1`). `affected_nodes` does a breadth-first walk over
  **incoming** edges only (who calls / imports / inherits / references me), over the
  relations in `DEFAULT_AFFECTED_RELATIONS` (calls, indirect_call, references, imports,
  imports_from, dynamic_import, re_exports, inherits, extends, implements, uses,
  mixes_in, embeds, defines, requires). It first steps into the seed's own members
  (`method` / `contains`) and follows overridden supertype members.
- Output is in BFS order. There is **no score**, so for a hub file the "top 10" is just
  the first 10 found. Example: Django `django/conf/__init__.py` returns 938 files at
  depth 2.
- A file that nothing depends on (most test files, JS assets, scripts) returns
  **nothing**. In this study 44% of Django queries and 48% of Hono queries got an empty
  answer from v8.
- `ARCHITECTURE.md` does not describe `affected`.

### Does graphify already read git history?

No, not for coupling. `grep -rn "git log\|subprocess.*git" graphify` shows git used only for:

| where | what for |
|---|---|
| `export.py:245`, `watch.py:473` | `git rev-parse HEAD`, to stamp the graph with the commit it was built at |
| `cli.py:1782/1791` | `git clone --depth 1` / `git pull`, for `graphify clone <url>` |
| `hooks.py` | installing post-commit/post-checkout hooks; the hook runs `git diff --name-only HEAD~1 HEAD` to know which files to re-extract |
| `detect.py:1415/1557` | `git ls-files` and `core.excludesFile`, for ignore rules |
| `prs.py` | `gh pr diff --name-only`, `git worktree list`, default branch |

### Upstream issues and PRs

Searched titles and bodies (GitHub search API) for: co-change, cochange, co-changed,
change coupling, git history, churn, hotspot, temporal coupling, evolutionary coupling,
git log, changed together, commit history.

| item | state | relation to this study |
|---|---|---|
| **PR #4544** "feat(cli): add cochange, check (with SARIF) and dead-code graph analyses" (omsenjalia, Oct 2026) | **open, not merged** | Adds a separate `graphify cochange` report: "hidden coupling" (pairs that change together with no graph edge) and churn hotspots. Reads `git log --no-merges --name-only`, last 500 commits, min count 3, skips commits > 30 files, only files that are already a graph `source_file`. It says "co-change is a statistical signal, never an edge" and writes nothing. **It does not feed `affected` and has no accuracy measurement.** Its git reader can be reused. |
| Issue #1220 "literal/identifier usage index for string-coupling navigation" | open | Same problem (coupling the AST cannot see), different fix (string index). |
| Issue #3182 "Graph health trend over time" | open | Uses history for metrics over time, not coupling. |
| PR #4759 "graph who has worked on each core area" | open | Uses history for authorship. |

Nobody has built co-change into `affected`, so I continued. If this goes ahead, it should
be coordinated with the author of PR #4544 (same git reader, one data file).

## 2. Method

### Repos

| repo | language | HEAD used | cut T (~182 days before HEAD) | test commits after T | commits used | queries |
|---|---|---|---|---|---|---|
| django/django | Python | d9d05f104 | 3e0190a45 (2026-05-08) | 537 | 244 | 760 |
| pallets/flask | Python | 49943b5a9 | 2ac89889f (2026-04-09) | 26 | 14 | 31 |
| psf/requests | Python | 3c7baaa05 | 6ec76b4a3 (2026-04-27) | 54 | 14 | 47 |
| honojs/hono | TypeScript | eb754bd5e | f10dee89c (2026-05-06) | 302 | 185 | 473 |
| jhy/jsoup | Java | d90d57521 | 477740fc0 (2026-05-04) | 169 | 79 | 297 |
| caddyserver/caddy | Go | b3d67c861 | fb324331f (2026-05-07) | 286 | 165 | 462 |

I first tried gin for Go, but it had only 33 commits in the test half-year, so I used
caddy (413 Go files, 286 test commits). Flask and requests are small samples (31 and 47
queries); read their per-repo numbers as noisy.

### Time split (no peeking)

- **T** = last commit on HEAD's first-parent line at least 182 days before HEAD's date.
- **Graph**: `git worktree` at T, `graphify update . --no-cluster` with v8
  (`--no-cluster` changes no edges, it only skips community detection). One graph per
  repo, used for every query.
- **Mining**: non-merge commits that are ancestors of T, within 3 years before T
  (also 3 months and 1 year for cold start). Renames are followed so old paths count
  for the file's name at T. Commits with more than 30 files are skipped as bulk.
- **Test**: non-merge commits in `T..HEAD`. Lockfiles, generated files
  (`*.min.js`, `.map`, `.mo`, `*.pb.go`, snapshots, …) and vendored dirs are dropped,
  and so are pure renames (`R100`). A commit is kept if it then has 2–20 files.
- **Queries**: each changed **code** file that existed at T is a seed. The truth is the
  other files in the commit **that existed at T**. Files created after T cannot be
  predicted by any method, so they are left out (about 11% of changed files overall, 18% in caddy).
- Metrics per query, then averaged: recall@k = found / true, precision@k = found / k,
  hit@k = at least one true file in the top k. "ALL" = the mean of the 6 repo means
  (each repo counts the same); pooled numbers are in `results/tables.md`.

### Predictors (top-k files, k = 5, 10, 20)

1. **v8 `affected`**: `affected_nodes` from `graphify.affected` (the function the CLI
   calls), seed resolved with `resolve_seed` exactly like the CLI, at depth 1, 2
   (default) and 3. Hits are mapped to their `source_file` in BFS order, duplicates and
   the seed's own file removed. `resolve_seed` found the file node for all but 7 seed
   files: 5 Hono files are not in the graph at all, and for 1 Hono and 1 Caddy file I
   fell back to walking from every node of that file.
2. **Co-change only**: rule seed → file, `confidence = commits(seed and file) /
   commits(seed)`, minimum support 2 (also tried 3, and 2 with recency decay,
   half-life 180 days). Ranked by confidence, then support, then path. Only files that
   exist at T can be predicted.
3. **Combined** (graph = v8 depth 2, co-change = support 2, 3 years):
   - *union, graph first*: v8 list, then co-change fills free slots;
   - *union, co-change first*: co-change list, then v8 fills free slots;
   - *fusion*: score = 0.5 × confidence + 0.5 × (1 / graph depth) — **pre-declared
     headline**;
   - *RRF*: reciprocal rank fusion of the two lists (k0 = 60).
4. **Floor**: other files in the seed's directory, alphabetical.
5. **Extra** (not v8 behaviour): the graph walked in **both directions** at file level,
   depth 1 and 2, ranked by edge count. I added it to see how much of the gap is just the
   direction of `affected`.

All choices were fixed before looking at test results. The pre-declared headline
combination (fusion) turned out *not* to be the best variant; I report it anyway and say
why below.

## 3. Results

### Main table (repo mean over 6 repos, 2,070 queries)

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.188 | 0.267 | 0.362 | 0.140 | 0.123 | 0.092 | 0.421 | 0.494 | 0.561 |
| v8 affected, depth 1 | 0.127 | 0.155 | 0.170 | 0.097 | 0.060 | 0.032 | 0.271 | 0.314 | 0.341 |
| **v8 affected, depth 2 (default)** | 0.138 | **0.180** | 0.221 | 0.107 | 0.079 | 0.050 | 0.281 | **0.341** | 0.385 |
| v8 affected, depth 3 | 0.138 | 0.184 | 0.238 | 0.107 | 0.083 | 0.056 | 0.282 | 0.345 | 0.396 |
| Co-change, support ≥ 2, 3y | 0.398 | 0.485 | 0.519 | 0.213 | 0.136 | 0.077 | 0.662 | 0.736 | 0.745 |
| Co-change, support ≥ 3, 3y | 0.343 | 0.387 | 0.401 | 0.167 | 0.098 | 0.054 | 0.569 | 0.610 | 0.613 |
| Co-change, support ≥ 2, 3y, decay | 0.398 | 0.485 | 0.524 | 0.214 | 0.136 | 0.077 | 0.670 | 0.737 | 0.751 |
| Union: v8 first, co-change fills | 0.293 | 0.403 | 0.502 | 0.181 | 0.135 | 0.089 | 0.518 | 0.636 | 0.724 |
| **Union: co-change first, v8 fills** | 0.414 | **0.521** | 0.570 | 0.245 | 0.168 | 0.100 | 0.697 | **0.783** | 0.797 |
| Fusion 0.5/0.5 (pre-declared headline) | 0.364 | 0.468 | 0.539 | 0.212 | 0.150 | 0.094 | 0.623 | 0.725 | 0.763 |
| Fusion: RRF | 0.386 | 0.499 | 0.573 | 0.223 | 0.160 | 0.098 | 0.653 | 0.752 | 0.801 |
| Extra: graph both directions, depth 2 | 0.308 | 0.432 | 0.522 | 0.183 | 0.148 | 0.106 | 0.583 | 0.712 | 0.768 |
| Extra: both-directions graph + co-change (fusion) | 0.399 | 0.508 | 0.605 | 0.233 | 0.170 | 0.117 | 0.695 | 0.800 | 0.840 |

### Per repo (recall@10 / hit@10)

| predictor | django | flask | requests | hono | jsoup | caddy | ALL |
|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.10 / 0.26 | 0.15 / 0.35 | 0.31 / 0.60 | 0.57 / 0.73 | 0.14 / 0.54 | 0.33 / 0.49 | 0.27 / 0.49 |
| v8 depth 1 | 0.11 / 0.24 | 0.05 / 0.10 | 0.31 / 0.68 | 0.29 / 0.39 | 0.08 / 0.29 | 0.10 / 0.19 | 0.15 / 0.31 |
| **v8 depth 2 (default)** | 0.11 / 0.25 | 0.06 / 0.16 | 0.37 / 0.68 | 0.32 / 0.41 | 0.12 / 0.34 | 0.11 / 0.20 | 0.18 / 0.34 |
| v8 depth 3 | 0.11 / 0.25 | 0.06 / 0.16 | 0.38 / 0.68 | 0.32 / 0.42 | 0.13 / 0.35 | 0.11 / 0.21 | 0.18 / 0.34 |
| Co-change only | 0.33 / 0.53 | 0.42 / 0.68 | 0.47 / 0.74 | 0.72 / 0.90 | 0.53 / 0.90 | 0.46 / 0.66 | 0.49 / 0.74 |
| Union: v8 first | 0.29 / 0.52 | 0.27 / 0.45 | 0.50 / 0.81 | 0.68 / 0.86 | 0.43 / 0.80 | 0.25 / 0.37 | 0.40 / 0.64 |
| **Union: co-change first** | 0.36 / 0.61 | 0.42 / 0.68 | 0.62 / 0.91 | 0.72 / 0.90 | 0.54 / 0.91 | 0.47 / 0.68 | 0.52 / 0.78 |
| Fusion 0.5/0.5 | 0.33 / 0.58 | 0.34 / 0.55 | 0.58 / 0.89 | 0.72 / 0.90 | 0.49 / 0.90 | 0.35 / 0.53 | 0.47 / 0.73 |
| RRF | 0.36 / 0.60 | 0.35 / 0.55 | 0.62 / 0.91 | 0.72 / 0.90 | 0.51 / 0.89 | 0.44 / 0.65 | 0.50 / 0.75 |
| Extra: both directions, d2 | 0.29 / 0.59 | 0.27 / 0.52 | 0.70 / 1.00 | 0.68 / 0.86 | 0.29 / 0.74 | 0.37 / 0.57 | 0.43 / 0.71 |
| Extra: both directions + co-change | 0.35 / 0.67 | 0.32 / 0.58 | 0.70 / 1.00 | 0.74 / 0.93 | 0.45 / 0.94 | 0.47 / 0.68 | 0.51 / 0.80 |

Notes:
- v8 does **worse than the same-directory floor** in 4 of 6 repos. Two reasons: it only
  looks at reverse edges, and its list has no ranking. Depth 3 hardly helps.
- The pre-declared fusion is dominated by the graph for hub files: every depth-1 file
  scores 0.5, while co-change confidence × 0.5 is usually below 0.25. So for a file with
  many dependents, the co-change files never make the top 10. Caddy shows this most
  (fusion 0.35 vs co-change-first 0.47). Rank-based mixing (union co-change first, RRF)
  does not have this problem.

### Paired comparison against v8 (hit@10, McNemar exact; commit-level sign test on recall@10)

| A vs B | scope | both hit | only A | only B | McNemar p | commits A better / B better / tie | sign p |
|---|---|---|---|---|---|---|---|
| fusion (headline) vs v8 | all 2,070 | 614 | 825 | 2 | 8e-244 | 521 / 1 / 179 | 8e-155 |
| union co-change first vs v8 | all | 594 | 946 | 22 | 3e-247 | 545 / 14 / 142 | 3e-141 |
| union v8 first vs v8 | all | 616 | 649 | 0 | 9e-196 | 465 / 0 / 236 | 2e-140 |
| RRF vs v8 | all | 608 | 901 | 8 | 5e-255 | 544 / 5 / 152 | 5e-154 |
| co-change only vs v8 | all | 513 | 946 | 103 | 3e-171 | 528 / 53 / 120 | 2e-99 |
| union co-change first vs co-change only | all | 1459 | 81 | 0 | 8e-25 | 87 / 0 / 614 | 1e-26 |
| both-dir graph + co-change vs both-dir graph | all | 1383 | 223 | 15 | 1e-48 | 224 / 16 / 461 | 4e-48 |
| **source-file seeds only** | | | | | | | |
| union co-change first vs v8 | 1,033 | 501 | 316 | 21 | 1e-68 | 306 / 22 / 305 | 4e-65 |
| fusion vs v8 | 1,033 | 520 | 234 | 2 | 5e-67 | 254 / 1 / 378 | 9e-75 |

Per repo, every combined variant beats v8 with p < 0.05 on both tests (flask and
requests are the weakest, p ≈ 0.0005–0.03, because they are small). Full per-repo rows
are in `results/tables.md`.

Bootstrap over commits (2,000 resamples), repo-mean recall@10 difference:
- union co-change first − v8: **+0.341** (95% CI +0.303 … +0.402)
- fusion − v8: +0.288 (+0.253 … +0.348)
- RRF − v8: +0.319 (+0.282 … +0.381)
- union co-change first − co-change only: +0.035 (+0.014 … +0.045), so the graph still adds a little
- fusion − co-change only: −0.017 (−0.047 … +0.001), so the fixed 0.5/0.5 weighting wastes the graph

### Breakdown by kind of true file (recall@10, pooled)

| predictor | source code (n=3,696) | test (n=3,461) | config/build (n=273) | docs (n=881) | migrations/templates/other (n=228) |
|---|---|---|---|---|---|
| Floor: same directory | 0.248 | 0.195 | 0.099 | 0.024 | 0.061 |
| **v8 depth 2** | 0.117 | 0.136 | 0.015 | 0.017 | 0.031 |
| Extra: both-directions graph | 0.351 | 0.209 | 0.099 | 0.008 | 0.123 |
| Co-change only | 0.323 | 0.231 | 0.187 | **0.370** | 0.158 |
| **Union: co-change first** | 0.356 | 0.256 | **0.190** | **0.370** | **0.171** |
| Fusion 0.5/0.5 | 0.323 | 0.245 | 0.128 | 0.269 | 0.145 |
| RRF | 0.354 | 0.251 | 0.147 | 0.304 | 0.158 |
| Both-directions graph + co-change | **0.411** | 0.248 | 0.121 | 0.166 | 0.149 |

Share of true files that have any node in the v8 graph: source 100%, test 98%,
config 87%, docs **37%**, migrations/templates/other **42%**.

What this says:
- **Your expectation holds for non-code.** On docs, config and templates the graph is
  close to blind (0.015–0.031), and often the file is not in the graph at all.
  Co-change gets 0.16–0.37 there. Examples: Django `docs/releases/*.txt`,
  `docs/ref/settings.txt`, `AUTHORS`; jsoup `CHANGES.md` (0.056 → 0.663 in jsoup);
  flask `pyproject.toml`, `.pre-commit-config.yaml`.
- **Co-change also beats v8 on code**, but that is mostly the direction problem: a graph
  walked both ways reaches 0.351 on source files, the same as co-change. On source code,
  the two signals add up: both-directions graph + co-change gets 0.411, the best of all.
- Tests: co-change 0.231–0.256 vs v8 0.136. Tests are leaves for `affected`, so from a
  source seed v8 reaches them only when they call the seed directly.

Per repo (v8 depth 2 → fusion), recall@10:

| repo | source code | test | config/build | docs | migrations/templates/other |
|---|---|---|---|---|---|
| django | 0.051 → 0.215 (n=1072) | 0.096 → 0.172 (n=1786) | 0.098 → 0.415 (n=41) | 0.000 → 0.092 (n=568) | 0.031 → 0.150 (n=193) |
| flask | 0.097 → 0.323 (n=31) | 0.057 → 0.229 (n=35) | 0.000 → 0.021 (n=47) | 0.000 → 0.190 (n=21) | — |
| requests | 0.360 → 0.423 (n=317) | 0.857 → 0.905 (n=21) | 0.000 → 0.000 (n=29) | 0.000 → 1.000 (n=4) | — |
| hono | 0.093 → 0.467 (n=621) | 0.375 → 0.522 (n=504) | 0.000 → 0.179 (n=95) | 0.000 → 0.000 (n=9) | 0.000 → 0.000 (n=6) |
| jsoup | 0.199 → 0.461 (n=683) | 0.084 → 0.248 (n=597) | — | 0.056 → 0.663 (n=267) | 0.000 → 0.250 (n=8) |
| caddy | 0.070 → 0.220 (n=972) | 0.075 → 0.199 (n=518) | 0.000 → 0.000 (n=61) | 0.000 → 0.000 (n=12) | 0.048 → 0.095 (n=21) |

(Django docs stay low, 0.092, because most Django commits touch a release-notes file
created for the next release, and many docs pages change only once or twice.)

### By kind of seed (pooled)

| seed kind | queries | v8 R@10 | both-dir graph R@10 | co-change R@10 | union co-change first R@10 | v8 hit@10 | union co-change first hit@10 |
|---|---|---|---|---|---|---|---|
| source code | 1,033 | 0.293 | 0.409 | 0.495 | 0.525 | 0.505 | 0.791 |
| test | 980 | 0.025 | 0.399 | 0.468 | 0.478 | 0.073 | 0.702 |

With test-file seeds, v8 is nearly useless (by design: nothing depends on a test).
Source seeds are the fair case for `affected`, and the gain is still large.

### Cold start: how much history co-change needs (recall@10 / hit@10)

| repo | co-change 3 months | co-change 1 year | co-change 3 years | fusion 3 months | fusion 1 year | fusion 3 years | v8 depth 2 | seeds that have any rule (3m / 1y / 3y) |
|---|---|---|---|---|---|---|---|---|
| django | 0.065 / 0.11 | 0.220 / 0.37 | 0.327 / 0.53 | 0.158 / 0.32 | 0.257 / 0.47 | 0.333 / 0.58 | 0.114 / 0.25 | 18% / 52% / 71% |
| flask | 0.160 / 0.29 | 0.173 / 0.32 | 0.415 / 0.68 | 0.215 / 0.42 | 0.221 / 0.42 | 0.342 / 0.55 | 0.058 / 0.16 | 42% / 52% / 84% |
| requests | 0.149 / 0.34 | 0.149 / 0.34 | 0.470 / 0.74 | 0.478 / 0.81 | 0.478 / 0.81 | 0.582 / 0.89 | 0.365 / 0.68 | 51% / 51% / 79% |
| hono | 0.200 / 0.23 | 0.461 / 0.60 | 0.716 / 0.90 | 0.430 / 0.55 | 0.578 / 0.75 | 0.716 / 0.90 | 0.318 / 0.41 | 29% / 68% / 96% |
| jsoup | 0.035 / 0.11 | 0.298 / 0.60 | 0.528 / 0.90 | 0.151 / 0.40 | 0.344 / 0.68 | 0.488 / 0.90 | 0.117 / 0.34 | 14% / 63% / 93% |
| caddy | 0.144 / 0.19 | 0.234 / 0.34 | 0.456 / 0.66 | 0.211 / 0.33 | 0.264 / 0.39 | 0.349 / 0.53 | 0.107 / 0.20 | 39% / 51% / 87% |
| **ALL** | **0.125 / 0.21** | **0.256 / 0.43** | **0.485 / 0.74** | 0.274 / 0.47 | 0.357 / 0.59 | 0.468 / 0.73 | 0.180 / 0.34 | 26% / 57% / 84% |

- 3 months is not enough on its own (0.125 < 0.180 for v8). About **1 year** is where
  co-change alone passes the graph, and it keeps improving up to 3 years.
- Combined with the graph, even 3 months beats v8 alone (0.274). So a combined design
  is safe for young repos and shallow history.
- Recency decay (half-life 180 days) changed almost nothing (0.485 vs 0.485). Support ≥ 3
  is clearly worse than ≥ 2 (0.387): most useful pairs are rare.

### Cost

| repo | commits mined (3y) | bulk skipped (> 30 files) | git log, s | counting, s | total, s | files with history | pairs, support ≥ 2 | stored JSON | gzip | v8 graph build, s (for scale) |
|---|---|---|---|---|---|---|---|---|---|---|
| django | 2,834 | 29 | 0.20 | 0.10 | **0.30** | 1,685 | 3,182 | 305 KB | 34 KB | 74.7 |
| flask | 294 | 1 | 0.02 | 0.01 | 0.03 | 115 | 596 | 37 KB | 3.7 KB | 3.0 |
| requests | 210 | 0 | 0.01 | 0.00 | 0.01 | 87 | 131 | 11 KB | 1.4 KB | 1.3 |
| hono | 1,573 | 5 | 0.10 | 0.03 | 0.13 | 449 | 1,367 | 103 KB | 9.9 KB | 5.2 |
| jsoup | 607 | 3 | 0.03 | 0.01 | 0.04 | 197 | 717 | 79 KB | 5.7 KB | 3.7 |
| caddy | 896 | 4 | 0.05 | 0.02 | 0.07 | 460 | 689 | 81 KB | 8.0 KB | 2.5 |

(Measured on a 4-core cloud VM, full clones, `git log --no-merges -M --name-status`.
Stored JSON = per-file commit counts + all pairs with support ≥ 2; it has not been
size-optimised.) Mining is 36–250× cheaper than the AST graph build, so it can simply
be recomputed in full on every `graphify update`.

## 4. Examples

### Where co-change found what the graph missed

1. **Django `3328078a01`** "Refs CVE-2026-6873 -- Defaulted SIGNED_COOKIE_LEGACY_SALT_FALLBACK
   transitional setting to False." Seed `django/conf/__init__.py` (a source file).
   v8 depth 2 returns **938 files**; 2 true ones are in there somewhere, none in the top 10.
   Co-change top 3: `django/conf/global_settings.py` (0.50), `docs/ref/settings.txt`
   (0.50), and further `docs/internals/deprecation.txt` (0.25). All three were really
   changed. A settings module and its docs are linked only by convention, never by an import.
2. **jsoup `a682fd5bc8`** "`noscript` is an island (#2537)". Seed
   `parser/HtmlTreeBuilderState.java`. v8 returns 8 files in total, 1 of them true
   (`HtmlTreeBuilder.java`). Co-change's top 10 has 4 true files: `CHANGES.md` (0.47),
   `HtmlTreeBuilder.java` (0.47), `HtmlParserTest.java` (0.20), `PositionTest.java`
   (0.13); v8 never returns the other three. jsoup's changelog is edited in almost every
   fix commit; the graph cannot know that.
3. **Flask `7689f98403`** "drop support for Python 3.10". Seed `src/flask/cli.py`.
   v8's top 10 is the import neighbourhood (`__main__.py`, `blueprints.py`,
   `testing.py`, …); 1 true file. Co-change top 2: `CHANGES.rst` (0.77) ✓,
   `pyproject.toml` (0.46) ✓, plus `helpers.py` ✓. Version-support changes always touch
   packaging and the changelog.

   Also typical (test-file seeds, where v8 is empty): Hono `c831020fb1` with seed
   `src/middleware/ip-restriction/index.test.ts`: co-change lists exactly the 3 true files
   (`utils/ipaddr.ts` 1.0, `ip-restriction/index.ts` 0.67, `utils/ipaddr.test.ts` 0.67).

### Where co-change added noise

1. **Caddy `7e82a6b528`** "admin: fix warnings and status code in /load API". Seed
   `admin.go`, truth `caddyconfig/configadapters.go`, `caddyconfig/load.go`. v8 has
   `configadapters.go` in its top 10. `admin.go` has a long history, so its rules are
   weak and generic: `admin_test.go` 0.21, `caddy.go` 0.18, `context.go` 0.18, `go.mod`
   0.14, … all wrong. Fusion pushed the graph's true hit out of the top 10. Hub files
   with many commits produce flat, low-confidence lists.
2. **Django `512b92a493`** "Deprecated django.utils.functional.cached_property". Seed
   `django/db/models/query.py` (63 commits in the window). Every rule is below 0.15
   confidence (`docs/ref/models/querysets.txt`, `tests/composite_pk/tests.py`,
   `contenttypes/fields.py`, …), and the real change was driven by a different module
   (`utils/functional.py`). v8 had 2 true files in its top 10 (`prefetch_related/models.py`
   and `tests.py`); fusion kept only 1.

Both cases point to the same fix: **hide rules below a confidence floor** (for example
0.2), or show co-change as its own section so it never displaces graph results.
More candidates are in `results/example_candidates.txt`.

## 5. Decision

**Build it.** The gain is large (recall@10 ×2.9, hit@10 0.34 → 0.78 with co-change
first), it shows in all 6 repos and 4 languages, it holds for source-file seeds, and the
graph-only answer almost never wins (22 of 2,070 queries vs 946). It costs under a second
and a few hundred KB.

Two findings change *how* to build it:
1. Do not mix by a fixed score (the 0.5/0.5 fusion let the graph drown co-change for hub
   files). Show co-change as **its own labelled list**, or mix by rank.
2. A separate, cheaper win exists inside the graph: `affected` follows only reverse
   edges and does not rank. A both-directions walk ranked by edge count gets 0.432
   recall@10 without any history. That is a different change of meaning ("what I
   depend on" is not "what depends on me"), so it should be a separate proposal, but it
   is worth measuring with the same harness.

## 6. Design proposal (text only)

Smallest design that fits graphify.

**Where the data lives.** `graphify-out/cochange.json`, **not** edges in `graph.json`.
- The graph is a function of the source tree; co-change is a function of history. Keeping
  them apart keeps `graph.json` byte-stable for the same tree, and keeps statistical
  links out of `query`, `path`, clustering, god-nodes and the wiki. This matches
  PR #4544's rule ("a statistical signal, never an edge").
- Content: `{"version": 1, "head": "<sha>", "window": {"since": "<iso>", "commits": N,
  "bulk_skipped": M}, "files": {"path": commits, ...}, "pairs": [["a", "b", support], ...]}`
  with pairs sorted, support ≥ 2. Confidence is computed when reading (support / files[x]).

**When it is computed.** At the end of `graphify update` (and the git hooks, which
already call it), after the graph is written:
`git -c core.quotepath=false log --no-merges -M --name-status --format=%x1e%H%x1f%ct
--since=<HEAD date − 3 years> --max-count=10000 HEAD --`. Follow renames to the
names at HEAD, drop lockfiles/generated/vendored and anything `.graphifyignore` excludes,
skip commits with more than 30 files. Recompute fully every time: 0.3 s for Django's 3
years, so "incremental" is not worth its bugs. Skip the work when `head` in the file
already equals `HEAD`. Opt-out: `GRAPHIFY_NO_COCHANGE=1` or `--no-cochange`.

**Scope of files.** Do **not** limit to files that are graph nodes (PR #4544 does).
The gain is largest exactly on files that are not in the graph: 63% of true doc files
and 58% of templates/other had no graph node. Keep only files that exist at HEAD.

**How `affected` uses it.** On by default when `cochange.json` exists, as a **separate,
labelled section** after the graph hits, so existing output lines do not change meaning:

```
Affected nodes for conf/__init__.py
...existing graph lines, unchanged...
Changed together in git history (3y, 2,834 commits; not code links):
- django/conf/global_settings.py   [co-change 0.50, 8 commits]
- docs/ref/settings.txt            [co-change 0.50, 8 commits]
```

- Only for file seeds. For a symbol seed, use the symbol's `source_file`.
- Top 10, confidence ≥ 0.2, support ≥ 2 (both flags: `--cochange-top`,
  `--cochange-min-confidence`). `--no-cochange` hides it. Files already in the graph
  list get a `(also a code link)` mark instead of being hidden.
- For callers that want one ranked list (MCP tool, `--json`), merge by rank: co-change
  first, graph fills (the best variant here), or RRF. Each item keeps a `source`
  field: `graph` or `cochange`.

**Without git or with a shallow clone.**
- No `.git`, or `git` not on PATH: write nothing, print nothing on `update`.
  `affected` prints one line: `co-change: not available (not a git repository)`.
- Shallow clone (`git rev-parse --is-shallow-repository` = true), or fewer than ~100
  usable commits: still mine what is there, but record `"shallow": true` and the commit
  count, and print `co-change: only N commits of history (shallow clone); run git fetch
  --unshallow for better results`. Per the cold-start table, little history alone is
  weak, but next to graph results it never makes the answer worse.
- CI checkouts are usually `--depth 1`: this gives one commit, so co-change is off there.

**Determinism.** Same repo and HEAD → same bytes:
- the window is anchored on **HEAD's committer date**, never on the wall clock;
- `--max-count` bounds the walk; git's commit order for a fixed HEAD is fixed;
- `core.quotepath=false`, `-M` with git's default rename threshold, recorded in the file;
- every list sorted (pairs by path; rankings by confidence, then support, then path);
- no use of Python set or dict iteration order in the output.
  (The study harness was checked: output is byte-identical under PYTHONHASHSEED 0 and 1.)

**Size limits.**
- Window: 3 years or 10,000 commits, whichever is smaller.
- Skip commits with more than 30 files.
- Keep at most 50 partners per file (the highest confidence ones), support ≥ 2.
- Hard cap on the file, for example 5 MB; if it would be larger, raise the support
  floor until it fits and record that in the file. Django's 3 years are 305 KB before any
  trimming.

**How a PR would show the gain.** Ship this harness as the benchmark:

```bash
research/cochange/scripts/run_all.sh /path/to/workdir
```

It clones the 6 repos at the pinned HEADs, builds the v8 graph at each cut, replays the
test half-year and prints `results/tables.md`. The PR should show the repo-mean row for
v8 depth 2 vs the shipped ranking and the paired test:

| | recall@10 | hit@10 | McNemar (hit@10) |
|---|---|---|---|
| v8 `affected` depth 2 | 0.180 | 0.341 | — |
| with co-change (co-change first, graph fills) | 0.521 | 0.783 | 946 vs 22, p ≈ 1e-247 |

plus the cost table (seconds and bytes per repo), and a test that `cochange.json` is
byte-identical across two runs at the same HEAD.

## 7. What I am unsure about

- **The answer key favours co-change.** "Changed in the same commit" is the same kind of
  data co-change learns from. Commits also bundle unrelated edits (changelog, typo fixes),
  which co-change predicts and the graph cannot. The "what could break" question is not
  tested here: a caller that must not break but is not edited counts as a miss for
  `affected` *and* is never rewarded. A test-failure-based answer key would be a fairer
  second check.
- **v8 is handicapped by its own design**, not only by missing data: reverse edges only
  and no ranking. Part of the gap could be closed inside the graph (see the
  both-directions extra). The combination still adds +0.076 recall@10 on top of a
  both-directions graph, so co-change keeps its value.
- **Small samples** for flask (31 queries) and requests (47). Their direction agrees with
  the others, but their exact numbers are noisy.
- **One cut per repo.** I did not repeat the study at other cut dates.
- **Combination choice is post-hoc.** The pre-declared headline (fusion) beat v8 by +0.29,
  but the best variant (co-change first) was found after looking. All combined variants
  beat v8 by at least +0.22, so the decision does not depend on this choice, but the
  exact numbers for "the shipped ranking" should be re-checked on new repos.
- **Each query is one seed file.** Real use often starts from a diff with several files;
  multi-seed rules (Zimmermann-style itemsets) were not tried.
- **File classification is by path rules** (`evaluate.py:category`), so some files are
  misfiled (for example, Django's `docs/` Python is "docs").
- **Mining time** was measured on mid-size repos. A monorepo with 100k commits in 3 years
  needs the `--max-count` cap; I did not measure one.

## 8. Follow-up: the built feature and two extra measurements

The feature is on branch `claude/affected-cochange` (one commit on upstream `v8`
`16218bf`). Nothing in this section uses the study's own predictors: the numbers
come from the shipped code (`graphify update` writes `cochange.json`;
`affected_payload` is what `graphify affected --json` prints) with the shipped
defaults: depth 2, confidence ≥ 0.2, at most 10 co-change items.

### 8.1 Before/after on the built code (`scripts/run_all_built.sh`)

Same 6 repos, cut commits and 2,070 queries as above. First build (section printed after the graph list), files in `results/built_v1/`; the current build is in §9.3 and `results/built/`.

| row | django | flask | requests | hono | jsoup | caddy | ALL R@5 | ALL R@10 | ALL R@20 | ALL hit@10 |
|---|---|---|---|---|---|---|---|---|---|---|
| **before**: v8 `affected` (graph items) | 0.114 / 0.250 | 0.058 / 0.161 | 0.365 / 0.681 | 0.318 / 0.414 | 0.117 / 0.337 | 0.103 / 0.197 | 0.137 | **0.179** | 0.221 | **0.340** |
| after, printed order (graph lines, then the section) | 0.268 / 0.499 | 0.271 / 0.452 | 0.395 / 0.723 | 0.663 / 0.844 | 0.410 / 0.801 | 0.235 / 0.359 | 0.285 | 0.374 | 0.454 | 0.613 |
| **after, co-change items first** (merge by the `source` tag) | 0.326 / 0.574 | 0.415 / 0.677 | 0.519 / 0.830 | 0.698 / 0.888 | 0.514 / 0.902 | 0.422 / 0.626 | 0.399 | **0.483** | 0.510 | **0.749** |
| after, first k graph lines + the whole section | 0.331 / 0.578 | 0.422 / 0.677 | 0.536 / 0.830 | 0.710 / 0.892 | 0.538 / 0.906 | 0.426 / 0.628 | 0.469 | 0.494 | 0.519 | 0.752 |

(Per-repo cells are recall@10 / hit@10.) The last row shows on average 8.4 files at k = 10,
because v8 returns nothing for many seeds.

Paired hit@10 vs before: co-change first 866 vs 7 (p ≈ 2e-246); first 10 graph
lines + section 866 vs 0; printed order 616 vs 0. The "before" row reproduces the
study's v8 row (0.179 vs 0.180; the 0.001 is 7 seeds the study resolved with a
fallback and the CLI does not). Compared with the study's unthresholded
co-change-first (0.521), the 0.2 floor and the 10-item cap cost about 0.04 recall@10
on this answer key.

### 8.2 A non-circular answer key: failing tests (`scripts/run_mutation.sh`)

click (`ac0e297`), flask (`49943b5`), httpx (`b5addb6`). 40 functions sampled per
repo (seed 2026) from the package source, skipping one-line defs, stubs, nested
helpers and `@overload`/`@abstractmethod`. One at a time, `raise RuntimeError("mut")`
is inserted as the first line of the body and the repo's full test suite runs
(its own pytest config; proxy variables removed for httpx; tests that fail on
clean code are ignored). Truth = the test files with new failures. Seed = the
mutated file. Co-change is mined with the built miner from `C^` (strictly before
the tested commit). `results/mutation/`.

| repo | killed mutants (of 40) | failing test files per mutant | v8 R@10 | v8 + co-change, co-change first R@10 | first 10 graph lines + section R | v8 R@20 | co-change first R@20 | v8 hit@10 | co-change first hit@10 | first 10 + section hit |
|---|---|---|---|---|---|---|---|---|---|---|
| click | 35 | 7.9 | 0.223 | 0.281 | 0.294 | 0.359 | 0.396 | 0.543 | 0.743 | 0.743 |
| flask | 33 | 5.8 | 0.262 | 0.214 | 0.306 | 0.297 | 0.309 | 0.485 | 0.485 | 0.576 |
| httpx | 39 | 7.3 | 0.027 | 0.189 | 0.209 | 0.209 | 0.253 | 0.128 | 0.538 | 0.615 |
| **pooled** | **107** | | **0.164** | **0.227** | 0.267 | 0.285 | 0.317 | **0.374** | **0.589** | 0.645 |

- Paired hit@10, co-change first vs v8: 29 vs 6, p = 0.0001. First 10 graph lines +
  section vs v8 top 10: 29 vs 0, p ≈ 4e-9 (that view shows more lines: 11.8 / 14.3 / 15.6 files on average for click / flask / httpx, against 10).
- The printed order equals v8 at k = 10 and 20 here: v8 returns 16–68 files, so the
  section starts after line 20.
- **What this says about the bias worry.** The gain is real but much smaller than on
  the commit key (+0.06 recall@10 instead of +0.30), it comes from click and httpx,
  and on flask co-change does not help (recall@10 drops with co-change first; a
  plain naming rule, "test file named after the module", beats everything there at 0.328).
- **Why.** For "what breaks", the graph already *reaches* most failing tests (recall
  over v8's whole list: click 0.96, httpx 0.76, flask 0.34); it ranks them badly.
  Co-change finds almost no new failing files (0.000 / 0.018 / 0.066 recall found only
  by the section); it works as a better ordering. For "what else gets edited" (the
  commit key) it finds files the graph never reaches (docs, configs).
- Small sample: 107 mutants, 3 Python repos, one commit each.

### 8.3 Ranking only (not built)

Same v8 result SET (reverse edges only, depth 2), only the order changes: by graph
distance, then by the number of linking edges from the candidate file into the
files one step closer to the seed, then path. `scripts/ranking_only.py`,
`scripts/mutation_ranking.py`.

| answer key | v8 order R@10 | sorted R@10 | v8 order hit@10 | sorted hit@10 |
|---|---|---|---|---|
| commits, 2,070 queries (repo mean) | 0.180 | 0.221 | 0.341 | 0.395 |
| failing tests, 107 mutants (pooled) | 0.164 | 0.168 | 0.374 | 0.421 |

Per repo on the commit key, sorting helps most in caddy (0.107 → 0.170) and django
(0.114 → 0.151), and does nothing in requests. Sorting alone is a modest, cheap gain
(+0.04 recall@10, +0.05 hit@10), well below co-change (+0.30 on commits, +0.06 on
failing tests). Worth a second small PR only if it stays this cheap; on the
failing-tests key it does not fix v8's ordering problem. Variants (distinct linking
nodes; edges into the seed only) are in `results/ranking_only.md`.

### 8.4 Cost on Django (HEAD `d9d05f1`, 4-core VM, `graphify update .`)

| | v8 | branch |
|---|---|---|
| cold full build | 128.0 s | 126.3 s |
| warm, nothing changed (3 runs) | 2.92 / 2.97 / 2.81 s | 2.77 / 2.80 / 3.04 s |
| warm, cochange.json deleted so it must re-mine (3 runs) | — | 3.43 / 3.47 / 3.09 s |
| `mine_cochange` alone (5 runs) | — | 0.31 s min, 0.32 s median |

The branch's cochange.json for Django: 2,922 commits used, 36 bulk commits skipped,
897 files, 315 KB (38 KB gzipped). Byte-identical across PYTHONHASHSEED 0/1/4242, and
the written file equals a fresh mine. The graph itself is identical to v8's
(55,328 nodes, 131,856 edges). When HEAD has not moved the step costs one
`git rev-parse` plus reading the JSON.

### 8.5 Tests and checks

- New tests `tests/test_affected_cochange.py`: 22 pass on the branch; on v8 source
  21 fail and 1 passes (the regression guard "graph results are unchanged", which
  should pass on both). `results/feature_checks/new_tests_on_*.txt`.
- Full suite, `PYTHONPATH="$PWD" uv run --frozen pytest tests -q -p no:cacheprovider`,
  same environment (`uv sync --all-extras --frozen`): v8 10,198 passed, 21 skipped,
  1 xfailed, 0 failed; branch 10,223 passed, 21 skipped, 1 xfailed, 0 failed (+22 new
  tests, +3 from `test_architecture_doc.py`, which imports every symbol named in the
  ARCHITECTURE.md table). A first v8 run in a worktree synced without
  `--all-extras` showed 7 failures in `test_ext_tagged_id_clash.py`; they come from
  that environment, not the code.
- `ruff check .` clean; pyright on changed files: no new errors (the files' existing
  errors are unchanged; the new module and test file have 0).

### 8.6 Repro

`repro/make_repo.sh` builds a 7-commit repo where `app/pricing.py` changes with a
YAML rate table it reads by name, its docs page and the changelog. `repro/run_repro.sh`
prints `graphify affected app/pricing.py` from v8 and from the branch;
`repro/output.txt` is the result.

## 9. Second round: section first, corpus filter, and a ranking PR

### 9.1 What changed in `claude/affected-cochange`

- **Layout.** The text report now prints the co-change section (at most 10
  lines) BEFORE the code links, under the same label, followed by a
  `Code links:` label and the full, unchanged graph list. JSON lists the same
  items in the same order (co-change first), each tagged `source: graph |
  cochange`; no second "ranked" field, so text and JSON can never disagree and
  a consumer that only wants code links filters on the tag. Without
  cochange.json or with `--no-cochange` the text is byte-identical to v8.
- **Corpus filter.** A partner must be tracked at HEAD AND pass
  `corpus_filter`: `detect.ignored_predicate` (the scan's own "would `graphify
  update` exclude this path?": .graphifyignore/.gitignore chain including
  nested files, persisted `--exclude` patterns read from the build config,
  noise dirs, skipped names) plus `detect._is_sensitive`, plus the miner's
  lockfile/generated/vendored rules. Tracked docs, configs and tests stay.
  cochange.json records the corpus settings and a hash of the root
  .graphifyignore/.gitignore, so changing them re-mines at the same HEAD.
  On Django the filter removed one file
  (`admin/templates/admin/auth/user/change_password.html`, which graphify's
  sensitive-name rule also skips in the scan).

### 9.2 Why "section first" (`scripts/layout_choice.py`)

Flat top-10 orders scored on both answer keys with the built feature:

| layout (flat top 10) | commits R@10 / hit@10 | mutants R@10: click / flask / httpx | mutants R@10 / hit@10 (repo mean) |
|---|---|---|---|
| graph only (v8) | 0.179 / 0.340 | 0.223 / 0.262 / 0.027 | 0.171 / 0.385 |
| section capped at 3, then graph | 0.434 / 0.707 | 0.271 / 0.288 / 0.087 | 0.215 / 0.485 |
| section capped at 5, then graph | 0.454 / 0.721 | 0.277 / 0.282 / 0.080 | 0.213 / 0.486 |
| **section (≤ 10), then graph — shipped** | **0.482 / 0.748** | 0.281 / **0.214** / 0.189 | 0.228 / **0.589** |
| interleave graph / co-change | 0.473 / 0.734 | 0.277 / 0.265 / 0.173 | **0.238** / 0.510 |
| graph, then section (first build) | 0.373 / 0.612 | 0.223 / 0.262 / 0.027 | 0.171 / 0.385 |

The shipped layout is best on the commit key and on mutant hit@10. Interleaving
is a near-tie on recall (0.238 vs 0.228 on mutants) and spares flask, but it
would mix history lines into the code-link list, which breaks the "separate,
labelled section" requirement. Capping the section at 3–5 helps flask a little
and costs httpx most of its gain. I did not tune further: these are the test
sets. **Cost: flask's failing-tests recall@10 drops from 0.262 to 0.214** because up
to 10 history lines push its graph hits past line 10.

### 9.3 Re-measured, built code, new layout

Commit key (`scripts/run_all_built.sh`, 2,070 queries), recall@10 / hit@10:

| repo | queries | v8 | built (section, then code links) |
|---|---|---|---|
| django | 760 | 0.114 / 0.250 | 0.322 / 0.566 |
| flask | 31 | 0.058 / 0.161 | 0.415 / 0.677 |
| requests | 47 | 0.365 / 0.681 | 0.519 / 0.830 |
| hono | 473 | 0.318 / 0.414 | 0.698 / 0.888 |
| jsoup | 297 | 0.117 / 0.337 | 0.514 / 0.902 |
| caddy | 462 | 0.103 / 0.197 | 0.422 / 0.626 |
| **repo mean** | 2,070 | **0.179 / 0.340** | **0.482 / 0.748** |

Paired hit@10: 860 vs 7, p ≈ 2e-244. Django moved from 0.326 to 0.322 vs the first
build because the corpus filter now drops a few files.

Failing-tests key (`scripts/mutation_rescore.py cochange_v2`, 107 killed mutants;
truth unchanged, predictions recomputed with the built code):

| repo | mutants | v8 R@10 / R@20 / hit@10 | built R@10 / R@20 / hit@10 |
|---|---|---|---|
| click | 35 | 0.223 / 0.359 / 0.543 | 0.281 / 0.396 / 0.743 |
| **flask** | 33 | 0.262 / 0.297 / 0.485 | **0.214** / 0.309 / 0.485 |
| httpx | 39 | 0.027 / 0.209 / 0.128 | 0.189 / 0.253 / 0.538 |
| **pooled** | 107 | **0.164 / 0.285 / 0.374** | **0.227 / 0.317 / 0.589** |

Paired hit@10: 29 vs 6, p = 0.0001. Flask is worse on recall@10 and equal on hit@10.

### 9.4 Ranking PR (`claude/affected-ranking`, independent of the co-change PR)

`affected_nodes` now returns its hits sorted by (depth, −edges from the hit's
file into the files one step closer to the seed, path, line, id). Same set,
depths and relations. v8 has no `affected` JSON or MCP tool, so only the CLI
text changes. Measured with `scripts/bench_order.py` (same 2,070 queries, run
under v8 and under the branch) and `scripts/mutation_rescore.py ranking`:

| repo | queries | v8 R@10 / hit@10 | ranked R@10 / hit@10 | same set |
|---|---|---|---|---|
| django | 760 | 0.114 / 0.250 | 0.151 / 0.303 | 760/760 |
| flask | 31 | 0.058 / 0.161 | 0.145 / 0.258 | 31/31 |
| requests | 47 | 0.365 / 0.681 | 0.369 / 0.681 | 47/47 |
| hono | 473 | 0.318 / 0.414 | 0.337 / 0.436 | 473/473 |
| jsoup | 297 | 0.117 / 0.337 | 0.156 / 0.407 | 297/297 |
| caddy | 462 | 0.103 / 0.197 | 0.165 / 0.284 | 462/462 |
| **repo mean** | 2,070 | **0.179 / 0.340** | **0.221 / 0.395** | |

Paired hit@10 122 vs 8, p ≈ 3e-27.

| mutants | v8 R@10 / R@20 / hit@10 | ranked R@10 / R@20 / hit@10 |
|---|---|---|
| click (35) | 0.223 / 0.359 / 0.543 | 0.223 / 0.368 / 0.571 |
| flask (33) | 0.262 / 0.297 / 0.485 | 0.288 / 0.322 / 0.515 |
| httpx (39) | 0.027 / 0.209 / 0.128 | 0.022 / 0.174 / 0.205 |
| **pooled (107)** | **0.164 / 0.285 / 0.374** | **0.170 / 0.283 / 0.421** |

Paired hit@10 8 vs 3, p = 0.23 (not significant); httpx recall@20 drops. The set is
identical for 107/107.

### 9.5 Checks and cost (second round)

- New tests: co-change 25 pass on the branch, 24 fail on v8 source (the one that
  passes is the "graph results unchanged" guard); ranking 6 pass, 5 fail on v8
  (the one that passes is the "set and depths unchanged" guard).
  `results/feature_checks_v2/`.
- Full suite, `PYTHONPATH="$PWD" uv run --frozen pytest tests -q -p no:cacheprovider`,
  every tree synced with `uv sync --all-extras --frozen`: clean v8 10,198 passed;
  co-change branch 10,226 passed; ranking branch 10,204 passed; each with 21 skipped,
  1 xfailed and **0 failed**, so no file needed a lone re-run.
- `ruff check .` clean on both branches; pyright on changed files: no new errors.
- Django `graphify update .` (warm): nothing changed 2.8 s on both v8 and the
  branch; when HEAD moved (cochange.json re-mined with the corpus filter) about
  4.0 s, so the filter made re-mining cost about 1.2 s instead of 0.5 s
  (filter set-up 0.25 s, the rest per-path ignore checks). cochange.json 317 KB.

## Files

- `scripts/prepare.sh` — pick T, make a worktree, build the v8 graph at T.
- `scripts/evaluate.py` — mine co-change, replay test commits, write per-query predictions.
- `scripts/report.py` — all tables and statistics → `results/tables.md`, `results/summary.json`.
- `scripts/examples.py` — candidate examples → `results/example_candidates.txt`.
- `scripts/run_all.sh` — the whole study in one command.
- `results/<repo>.queries.jsonl.gz` — raw: one line per query with truth, kinds, and the
  top-20 list of every predictor.
- `results/<repo>.run.json` — cut, counts, cost, seed resolution.
- `results/<repo>.meta.json`, `results/<repo>.graph_build.log` — graph build at T.
- `scripts/run_all_built.sh`, `scripts/bench_built.py`, `scripts/bench_built_report.py`,
  `scripts/bench_built_tests.py` → `results/built/` — before/after on the built feature.
- `scripts/run_mutation.sh`, `scripts/mutation.py`, `scripts/mutation_report.py`,
  `scripts/mutation_ranking.py` → `results/mutation/` — failing-tests answer key.
- `scripts/ranking_only.py` → `results/ranking_only.{md,json}` — sort-only experiment.
- `results/feature_checks/` — test, suite, lint/type and Django timing evidence.
- `repro/` — the tiny before/after repros (`run_repro.sh` for co-change,
  `run_repro_ranking.sh` for the ranking PR) and their outputs.
- `scripts/layout_choice.py` → `results/tables_layout_choice.md`; `scripts/mutation_rescore.py`
  → `results/mutation/tables_{cochange_v2,ranking}.md`; `scripts/bench_order.py`,
  `scripts/bench_order_compare.py` → `results/tables_order_v8_vs_ranked.md`;
  `results/built_v1/` keeps the first build's numbers.
