# Query study, round 2: is the win real outside Django?

Date: 2026-11-03. Code: `upstream/v8` @ `8e6a6d21`. Every number below comes from a
committed file in `research/query/`.

## How the test was made fair

**The split.** Django questions (114) are for tuning. Every non-Django question is
held out (`split.json`). I wrote that file and committed it first, before any change
(commit `b7d088da3`).

**More questions.** SWE-bench Lite has no more issues for the 8 non-Django repos; all
63 were already used. So I added SWE-bench Verified:
- 116 new issues for those repos (`questions_ext/`).
- Each has its own base commit, so I built **116 more graphs**, one per commit, with
  `graphify update .` and no failures (`results2/builds_ext.tsv`).
- Now there are **179 held-out questions**.
- The 116 Verified ones I never looked at before the final run.

**Tuning.** All tuning ran on Django only. The evaluator skips every non-Django
question in tuning mode. The weights were frozen in `tuned_params.json` and committed
before the held-out run. Then the held-out run happened **once**
(`results2/final-*.jsonl`).

**Same scorer.** The new evaluator (`evalset.py`) uses the same scoring as the
`graphify benchmark --questions` command. It reproduces last round's numbers exactly
(v8 74/177, BM25 112/177, prototype 125/177 in `results2/chk_*.jsonl`).

## 1. Held-out result (179 non-Django questions)

"top-5" = a file the gold patch changed is in the first 5 files shown. The p-value is
an exact McNemar test on the top-5 hits (`results2/heldout_report.md`).

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 `query_graph` | 26% | 44% | 56% | 77% | 2,195 |
| BM25 over whole files | 30% | 56% | 67% | 100% | 46,541 (to read the 5 files) |
| prototype, before tuning | 40% | 61% | 69% | 72% | 1,351 |
| **prototype, after tuning** | 44% | 66% | **73%** | 77% | 1,395 |
| prototype, after tuning, body words stored as a set | 44% | 64% | 75% | 78% | 1,248 |
| PR 1 (no body words) | 31% | 53% | 61% | 68% | 2,201 |

**Paired, top-5, held-out:**

| Pair | Prototype only | Other only | p |
|---|---|---|---|
| tuned prototype vs BM25-files | 21 | 11 | **0.11** |
| tuned prototype vs v8 | 40 | 10 | **2e-5** |
| prototype before tuning vs BM25-files | 24 | 20 | 0.65 |
| prototype before tuning vs v8 | 37 | 13 | 0.0009 |
| set-stored prototype vs BM25-files | 26 | 12 | 0.034 |
| tuned vs before tuning | 14 | 8 | 0.29 |

**By held-out part (top-5):**

| Part | v8 | BM25-files | Before tuning | After tuning | After vs BM25 (p) |
|---|---|---|---|---|---|
| Lite, 63 (seen in round 1) | 49% | 65% | 62% | 65% | 6 / 6, p = 1 |
| Verified, 116 (never seen) | 59% | 68% | 73% | 77% | 15 / 5, p = 0.04 |

**Per repo, held-out, top-5:**

| repo | n | v8 | BM25-files | before | after | after vs BM25 (only/only, p) | after vs v8 (only/only, p) |
|---|---|---|---|---|---|---|---|
| astropy | 24 | 75% | 71% | 92% | 88% | 4/0, 0.12 | 4/1, 0.38 |
| flask | 4 | 75% | 75% | 100% | 100% | 1/0, 1 | 1/0, 1 |
| pylint | 15 | 20% | 60% | 67% | 67% | 3/2, 1 | 7/0, 0.016 |
| pytest | 34 | 50% | 56% | 47% | 59% | 2/1, 1 | 6/3, 0.51 |
| requests | 13 | 62% | 77% | 69% | 62% | 1/3, 0.62 | 2/2, 1 |
| seaborn | 6 | 83% | 33% | 67% | 83% | 3/0, 0.25 | 1/1, 1 |
| sphinx | 57 | 53% | 70% | 72% | 74% | 5/3, 0.73 | 14/2, 0.004 |
| xarray | 26 | 62% | 77% | 69% | 77% | 2/2, 1 | 5/1, 0.22 |

**What this means:**
- Outside Django, the prototype clearly beats v8: 73% vs 56%, p = 2e-5.
- It is **not proven better than BM25-files**: 73% vs 67%, p = 0.11. It is ahead
  on 5 repos and behind on requests.
- On the fresh Verified questions it is ahead of BM25: 77% vs 68%, p = 0.04. On
  the 63 Lite questions it only ties.
- Its answers are about 1/30 of the reading cost of BM25 (1.4k vs 46.5k tokens).
- The tuning itself is a small, unproven gain: +6 questions, p = 0.29.

## 2. Why it lost outside Django, and what I changed

Before tuning, I looked at the 63 Lite non-Django questions. BM25 won 9 and the
prototype won 6. One line per loss is in `heldout_loss_causes.md`.

| Cause (before tuning) | Count |
|---|---|
| File ranking misses what whole-file scoring sees. Either the gold file is big with its words spread over many functions, or summing 5 nodes per file favours big files with many weak matches (sphinx `c.py`, `cpp.py`). | 7 |
| "pytest" and "fixture" count as test words, so test demotion is switched off in the pytest repo | 2 |
| Non-source nodes (no source file, `.yml`, doc examples) were not demoted | 1 |
| Small gold file, generic words | 1 |

**What I changed (variant `bm25b_ff2`, tuned on Django only):**

1. **A whole-file score.** The file's own BM25 score over all its nodes' words is
   added to the file ranking with weight 1. Node pooling went from 0.3 to 0.1.
   - Django top-5: 87 → 92.
   - I searched a grid of weight 0–2 × pooling 0–0.3. The 0.5–2 × 0–0.1 area is
     flat at 90–92 (`results2/tune-s1-*`).
2. **Strict test words.** Only "test", "tests", "testing", "testcase" and "unittest"
   switch the demotion off. Neutral on Django.
3. **Non-source demotion.** Nodes with no source file, config/data files and
   doc/example folders are demoted. Neutral on Django.
4. **The demotion factor stays 0.3.** 0.1–0.5 all give 92 on Django.

**After tuning, post-hoc.** Written after the one held-out run; nothing was changed
after it. BM25 still wins 11 held-out questions. The main cause, in 5 of them, is
**vendored or minified third-party code** in the top 5: `jquery-3.5.1.js`,
`underscore-1.13.1.js`, `requests/packages/urllib3`. The next fix would be to demote
vendored paths. I did not do it: that would be tuning on held-out data.

## 3. Size of storing body words

**Measured:**
- Each Lite repo's commit, compact JSON as graphify writes it (`results2/body_sizes.tsv`).
- The plain build time of a cold `graphify update .` (`results2/build_times.tsv`).
- The body pass is the extra time to read the files and make the word lists.

| repo | build s | graph.json MB | full (counts) | **set (chosen)** | set − stop words | set − stop − name words | body pass s |
|---|---|---|---|---|---|---|---|
| django | 100.3 | 48.3 | 65.6 (+36%) | **55.5 (+15%)** | 54.8 (+14%) | 53.3 (+11%) | 3.6 |
| pytest | 7.4 | 4.4 | 5.7 (+28%) | **5.2 (+18%)** | 5.1 (+15%) | 4.9 (+11%) | 0.3 |
| sphinx | 19.9 | 10.4 | 20.4 (+97%) | **12.8 (+23%)** | 12.5 (+21%) | 12.3 (+18%) | 1.9 |
| astropy | 60.5 | 31.2 | 43.7 (+40%) | **35.8 (+15%)** | 35.3 (+13%) | 34.5 (+11%) | 2.5 |
| requests | 3.1 | 1.2 | 1.5 (+28%) | **1.4 (+16%)** | 1.4 (+15%) | 1.4 (+13%) | 0.1 |
| pylint | 19.0 | 11.4 | 13.1 (+15%) | **12.5 (+10%)** | 12.3 (+8%) | 12.1 (+6%) | 0.4 |
| xarray | 10.0 | 6.3 | 7.8 (+25%) | **7.1 (+14%)** | 7.0 (+12%) | 6.9 (+10%) | 0.3 |
| seaborn | 6.5 | 3.3 | 4.4 (+33%) | **3.9 (+18%)** | 3.8 (+16%) | 3.7 (+13%) | 0.3 |
| flask | 3.2 | 1.6 | 1.9 (+23%) | **1.8 (+15%)** | 1.8 (+13%) | 1.7 (+10%) | 0.1 |

**Score of each form (Django top-5, of 114):**

| Form | Top-5 |
|---|---|
| full counts | 92 |
| set | 91 |
| set − stop words | 89 |
| set − stop words − name words | 89 |
| keep only the 60 / 40 / 20 / 10 rarest words per node | 88 / 88 / 85 / 84 |

**My choice: the unique-word set.**
- It is the smallest form within 1 point of full counts on Django (−0.9 point).
- On held-out it scores 75% top-5, which is as good as full counts (73%).
- The smaller forms save only 2–5 more points of size, but lose 2.6+ points of score.
- Cost: +10% to +23% graph.json and 0.1–3.6 s build time (about 3–10% of the build).
- Sphinx grows the most because it ships minified JavaScript. Skipping vendored files
  would cut that, but I did not measure it.

## 4. PR 1 (prepared, not opened)

**Branch:** `claude/query-pr1`, one commit on `upstream/v8`.

**Diff:** `graphify/serve.py` +83 / −10, plus a new `tests/test_query_source_first.py`
(+125, 9 tests). The full description is in `PR1.md`.

**What it does:**
- Tests, docs, config files and nodes with no source file are weighted ×0.3, but
  only inside `query`, and not when the question names tests or docs.
- The per-term seed guarantee is kept.
- The answer is file-first.
- `path`, `explain`, traversal and the budget are unchanged.

**All 293 questions:**

| | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 27% | 40% | 49% | 67% | 2,193 |
| PR 1 | 30% | 48% | 56% | 62% | 2,197 |

**Paired, top-5:**
- All 293 questions: 26 vs 4 (PR 1 only vs v8 only), p = 6e-5.
- Held-out 179 alone: 14 vs 4, p = 0.03.

**Cost:** "anywhere" drops from 67% to 62%. The same `graphify benchmark --questions`
command on the Lite set gives identical numbers for this branch.

**Tests:**
- The full suite fails 5 tests and errors on 6, all in two watch/rebuild files.
- Run alone 3 times, those two files pass 3/3 on PR 1.
- On plain v8 the same files fail once in 3 runs. So they are flaky on v8 too.

**Overlap with open upstream PRs:**
- **Same idea:** #2403 (exclude tests from seeds), #3417 (test demotion + relevance
  order), #4601 (file-type weights), #4481 (lead with best file), and the
  relevance-order PRs #3284, #1782, #1658.
- **New textual conflicts in `serve.py`** with 6 open PRs that merge cleanly with v8
  today: #3284, #3636, #3866, #4478, #4576, #4601.
- 90 other PRs touching the same functions already conflict with v8 inside `serve.py`.

## 5. My honest call on PR 2 (body words)

**Yes, send it, but describe it honestly.**

**Why yes:**
- **Body words are where the gain is.**
  - With body words (set form), held-out top-5 is 75%. PR 1 without them is 61%.
  - Held-out pairs: 33 vs 9, p = 0.0003.
  - Against v8 the gain is large and proven on held-out data: 73% vs 56%, p = 2e-5.
- **The answer is smaller than today:** about 1.3k tokens instead of 2.2k.
- **The cost is known:** about +15% graph.json (10–23%) and a few seconds of build time.

**What not to claim:**
- **Do not claim it beats plain BM25 over files.** On all 179 held-out questions it
  is ahead but not proven (p = 0.11). It only ties on the 63 Lite questions.
- **Keep the BM25 comparison fair.** BM25 needs about 46k tokens of file reading to
  use its answer.

**Before sending:**
- **Build PR 2 to fit the maintainer's rules** from `pr_feedback.md`.
  - The prototype is a separate BM25 ranker. PR 2 should add the body words as a
    stored `body_terms` set per node, plus a body tier layered on the existing
    tiers, keeping the per-term guarantee.
  - Then measure it again here: the layered version is not the prototype, so its
    numbers are not yet known.
- **Fix vendored and minified files first.** They are the top held-out loss cause and
  most of Sphinx's size growth. Tune that on Django, then test on new questions
  (for example SWE-bench full) that nobody has looked at.
