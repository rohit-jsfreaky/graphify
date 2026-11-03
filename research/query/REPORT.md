# Why `query` gives poor answers, what the open PRs do, and what would win

Measured 2026-11-03 on `upstream/v8` @ `8e6a6d21` (0.9.101), with the PR #4342 benchmark cherry-picked.

## Answer key

- **Source:** SWE-bench Lite (`princeton-nlp/SWE-bench_Lite`, test split).
- **Questions and answers:** the question is the issue title. The right answer is the set of non-test files the gold patch changes.
- **Repos:** the 9 repos from the earlier study, 177 issues:

  | Repo | Issues |
  |---|---|
  | django | 114 |
  | pytest | 17 |
  | sphinx | 16 |
  | astropy | 6 |
  | requests | 6 |
  | pylint | 6 |
  | xarray | 5 |
  | seaborn | 4 |
  | flask | 3 |

- **Graphs:** each repo is built once with `graphify update .` (code only, no LLM). The base commit is whichever issue's base commit has the most issues' gold files present. That commit covered **every** issue in all 9 repos (`questions/commits.json`).
- **Score:** where the first gold file appears among the distinct files of the `NODE` lines that `query_graph` shows. The MCP defaults apply: BFS, depth 3, 2000-token budget. Tokens are `len(answer)//3`, the same rule the budget uses.

## Results

| Variant | Top-1 | Top-3 | Top-5 | Anywhere | Median tokens |
|---|---|---|---|---|---|
| **upstream/v8 `query_graph`** | 26% | 34% | 42% | 59% | 2,194 |
| BM25 over whole files ¹ | 31% | 55% | 63% | 100% | 42,558 ¹ |
| PR #3417 (ANSWER block, camelCase, test demotion, relevance sort) | 28% | 44% | 51% | 71% | 2,549 ² |
| PR #2403 (exclude test paths from seeds) | 28% | 43% | 51% | 62% | 2,161 |
| PR #4481 (NL question leads with best file) | 27% | 35% | 44% | 60% | 2,194 |
| PR #4504 (docstrings searchable) | 26% | 35% | 44% | 60% | 2,191 |
| PR #4504, graphs rebuilt with its extractor | 25% | 35% | 43% | 61% | 2,194 |
| PR #4601 (file-type weights) | 26% | 34% | 42% | 59% | 2,194 |
| PR #4592 (drop isolating context filters) | 26% | 34% | 42% | 63% | 2,203 |
| PR #3636, graphs rebuilt (body attribute tier) | 25% | 34% | 39% | 59% | 2,177 |
| PR #3284 (same-hop relevance sort) | 25% | 34% | 38% | 52% | 2,175 |
| PR #3866 (phrase bonus, community coherence) | 17% | 25% | 32% | 45% | 2,187 |
| **Prototype A: body-word BM25, source over tests, file-first answer** | **44%** | **62%** | **71%** | 75% | **1,381** |
| Prototype A, body stored as unique-term sets (graph.json form) | 42% | 64% | 70% | 74% | 1,369 |
| Prototype B: body-word BM25 seeds + 1-hop, ordered by score | 40% | 62% | 69% | 72% | 1,463 |
| Prototype B without the test/doc demotion | 24% | 46% | 54% | 60% | 1,198 |
| Prototype B without the body words (label + path only) | 35% | 52% | 58% | 63% | 1,242 |
| v8 with test/doc nodes removed from seeds | 28% | 40% | 45% | 59% | 2,162 |
| v8 with output ordered by v8 term score | 26% | 34% | 42% | 64% | 1,361 |

¹ The BM25 baseline returns only file names. The token figure is what an agent pays to read the 5 files it ranks first. The 5 paths alone are about 40 tokens.

² For #3417, 150 of 177 answers exceed 2,000 tokens and 50 exceed 2,600. For v8, 148 exceed 2,000 and 1 exceeds 2,600. For prototype A, 39 exceed 2,000 and none exceed 2,600.

The full table is in `results/table.md`. It covers all 31 measured PR heads, each next to its own merge-base. The per-question rows are in `results/<variant>/<repo>.json`.

**Split by repo (top-5):**

| Variant | Django (114) | Other 8 repos (63) |
|---|---|---|
| v8 | 38% | 49% |
| BM25 over files | 62% | 65% |
| Prototype A | 76% | 60% |

**Head-to-head:** prototype A finds 27 questions that BM25 misses, and BM25 finds 14 that A misses. A two-sided sign test gives p ≈ 0.06. A clearly beats BM25 on Django. On the 63 non-Django questions it is about 5 points behind (60% vs 65%), at 1/30th of the reading cost. Its main gains are over v8 (+29 points) and over the best PR (+20 points).

## Every query PR

**Method.** Each PR head was fetched with `git fetch upstream pull/N/head:pr-N`. The benchmark commits from #4342 were cherry-picked onto it. When the only conflict was the help text in `__main__.py` or `docs/`, I kept the PR's side. When `benchmark.py` or `cli.py` conflicted, `bench_driver.py` imports that PR's own `graphify.serve` and runs the identical `_score_answer`. On v8, the driver reproduces the harness exactly: 42% top-5 and 2,194 median tokens.

Every PR was also run on its own **merge-base**. The "Δ vs base" column separates the PR's effect from how old its branch is. PRs branched in July sit on code that scored about 21% top-5.

**Feedback.** Maintainer and reviewer feedback was read from the PR pages and is collected in `pr_feedback.md`. The only maintainer is **safishamsi**. He has left no comment on any of the October ranking PRs (#3417, #2403, #4481, #4504, #4601, #3636, #4592, #3284). They are all "awaiting requested review".

| PR | What it does | Top-5 (Δ vs its base) | What it lacks | Maintainer and reviewer feedback |
|---|---|---|---|---|
| #3417 (open) | Adds an ANSWER block. Splits camelCase/snake identifiers. Demotes test, fixture and vendor paths. Sorts by relevance first. Adds `rel=` per node and source snippets. | 51% (+24 q) | Still matches names and paths only, not bodies. Answers grow (median 2.5k tokens, 50 over 2.6k). | No maintainer comment. The bot says the relevance weight is never applied to the final score, and that snippets can read files outside the graph root. |
| #2403 (open) | Excludes `tests/` paths from the default seeds, with an override flag. | 51% (+17 q) | Doesn't handle docs or rationale seeds. No body words. BFS and degree ordering unchanged. | No maintainer comment. The bot says safe to merge. |
| #4481 (open) | A question of 3+ words leads with the best node of the best-scoring file. Tests lead only when asked for. | 44% (+3 q) | Still uses the names-only scorer. Only the first seed changes. | No maintainer comment. The author asks for a title. |
| #4504 (draft) | Stores the full docstring text (up to 600 chars) and attaches it to the documented symbol for the rationale tier. | 44% / 43% rebuilt (+3 / +2 q) | The right idea, but too weak. Docstrings go into a 0.75-weight substring tier that exact name matches (1000×) still bury. No identifiers or comments from bodies. No test demotion. | No maintainer comment. |
| #4601 (open) | Weights scores by file type: document ×0.7, image ×0.4. | 42% (+0) | Tests are "code", so the biggest polluter is untouched. | No maintainer comment. The bot says it can demote exact doc matches. |
| #4592 (open) | Drops inferred context filters that isolate the seeds. | 42% (+0), anywhere 59→63% | Not a ranking change. | No maintainer comment. |
| #4470 (open) | `--compact` output (opt-in). | 42% (+0, flag off) | Format only. | A contributor review says tests pass. |
| #3636 (open) | Adds a `body` attribute tier at 0.35. The markdown extractor fills it from frontmatter. | 39% rebuilt (+2 q) | Only markdown frontmatter, never code bodies. The tier is too weak to seed. | Contributor sortakool shaped the design. No maintainer comment. |
| #3284 (open) | Orders same-hop nodes by query score, then degree. | 38% (+2 q), anywhere drops | Output order only. Seeds are still names-only, and many are tests. | rek (#3417) disagreed on the sort key and said it is "the maintainer's call". |
| #3285 (open) | Surfaces "bridge" nodes reached from 2+ seeds. | 37% (−1 q), +350 tokens | Adds tokens without improving seeds. | None. |
| #3866 (open) | Phrase bonus, majority-community seed preference, and shortest-path evidence rendered first. | 32% (−18 q) | The community filter drops correct seeds. **This is the worst regression measured.** | **Maintainer blockers (Oct 6 and 12):** the parity test was muted, the top seed is dropped, the heuristics should be split, and "a before/after retrieval benchmark is needed for ranking changes". The author's reply shows only speed numbers. |
| #2294 (open, stale) | Rationale tier. | 41% (+0) | Superseded. | Landed as #3288. |
| #2975 (open) | Rationale prefix ×0.01. | 37% (+0) | — | None. |
| #2113 (open) | Caps per-term seed recovery at `max_k`. | 37% (−7 q), tokens 1.1k | Fewer seeds lose recall. | None. |
| #2376 (open) | Reserves 50% of the budget for EDGE lines. | 41% (+0) | Output only. | None. |
| #1658 (open) | Per-term seed guarantee, joined bonus, relevance ordering, `explain` ambiguity. | 36% (+15 q vs its July base) | Mostly already in v8, where it scores lower than v8's 42%. | None. The per-term part landed via #1596. |
| #3837 (open) | "Correctness-aware retrieval": query index, ontology traversal, evidence packets. | 37% (−1 q) | 4.7k-line change with no ranking gain. | No maintainer comment. |
| #1782 (open) | RRF of lexical, structural and optional semantic signals for output order. | 39% (+31 q vs July base) | Gains are relative to old July code. Below v8 today. | None. |
| #3856 (open) | LLM-API two-stage semantic seeding. Falls back to `_pick_seeds`. | 38% (+0; no API key, so it fell back) | Needs a paid API. | The bot found a hardcoded API key in `.env.example`. |
| #1856 (closed by author, no reason) | Scope directives, cross-community quota, budget-derived BFS bound. | 44% (+39 q vs July base) | Largest gain over its own base, and still ends at v8's level. Its BFS bound is worth revisiting. | None. |
| #2516 (closed, replaced by #2617) | Skips covered-term seeds and relaxes starving filters. | 42% (+1 q) | — | Closed by the author in favour of #2617. |
| #1596, #1597, #1724, #1832, #1918, #2338, #2473, #2662, #3288, #3373 (closed, already landed in v8 by cherry-pick) | Per-term seed guarantee, stopwords, coverage², label dedup, one-pass scoring, induced edges, `_` splitting, rationale tier, undirected MCP traversal, banner fix. | Their effect is already inside v8's 42% (each ±0 to ±7 q vs its base) | — | Landed by safishamsi. He rejected #1832's multiplicity penalty ("silently reweights path/explain endpoint selection"). |
| #166, #347, #424, #879, #308 (April-era branches) | Hybrid embeddings, community-pruned query, sentence-transformer query, exact-label bonus, relevance sort. | **Not measured** | These branch from April code that has no `_query_graph_text`; query_graph lives inline in the MCP closure. #166 and #424 need embedding models, and #347 needs LLM community summaries. Measuring them would score April's ranker, not the idea. | #879: maintainer said "core fix definitely wanted" but it is "built against a stale baseline" and must layer on v8's tiers. The others have no maintainer comment. |
| Opt-in only: #4478 `--learned`, #1783 `--seed-file`, #2958 Japanese, #4760 / #1663 / #1664 defaults, #1665 `--recency` | — | Not measured | Defaults are unchanged, so the score equals the base. #4478 needs past-answer history. | — |

**What the maintainer wants** (from his reviews on #879, #3866, #1832, #2473):

- Layer on top of the existing tiers rather than replacing them.
- Keep the per-term seed guarantee and its tests.
- Show a before/after retrieval benchmark.
- Avoid side effects on `path`/`explain` endpoint resolution.
- Keep PRs small and split.

## Why the gold file is missed: the 3 biggest causes

On v8, 103 of 177 questions miss top-5. Script: `gap_analysis.py` + `gap_flags.py`. Rows: `results/gap_v8_misses.json`.

Basic facts:

- query_graph picks a median of **7 start nodes**. 568 of 1,309 seeds (43%) are test nodes, 86 are docstring (rationale) nodes, and 2 are doc nodes.
- BFS at depth 3 then visits a median of about **2,000 nodes**.
- The 2,000-token answer shows them in order: seeds first, then by hop, then by **degree**. Hubs win, and query relevance plays no part after the seeds.

Each miss is assigned one cause, the first that applies:

| Cause | Misses |
|---|---|
| **C. Names-only scoring.** The term scorer, which uses only names and paths, doesn't have the gold file in its top 5 files. BM25 over the file text does. | **40** |
| **E. Vocabulary gap.** Neither the term scorer nor full-text BM25 has it in the top 5. Only semantics could help. | 36 |
| **B. Tests and docs crowd it out.** The scorer would have the gold file in its top 5 once test and doc nodes are removed. | 13 |
| **D. Shown 6th or later by BFS luck.** | 9 |
| **A. The scorer had it in the top 5, but traversal and degree ordering dropped it.** | 5 |

**1. Names-only scoring (40 misses; 49 counted non-exclusively).**

The scorer matches labels and paths. An exact name match outweighs a substring match about 1,000-fold, and words inside the function body are never seen.

- *"Set default FILE_UPLOAD_PERMISSION to 0o644."* Gold: `django/conf/global_settings.py`. The seeds were `Permission`, `default()`, `File`, `set()` and `uploadedfile.py`, all exact name hits on common words. The setting lives in the file's body, and the scorer ranks the gold file 22nd.
- *"Incorrect removal of order_by clause created as multiline RawSQL."* Gold: `django/db/models/sql/compiler.py`. The seeds were `RawSQL`, `Order`, `.multiline()` and two test or admin nodes. The scorer ranks the gold file 36th, and the answer shows it 30th.

**2. Tests and docs as start nodes (55 of 103 misses have at least half test/doc seeds; 13 are the primary cause).**

Test classes repeat the issue's words in their names (`UsernameValidatorsTests`, `TestCombinations`), so they win exact-name tiers.

- *"UsernameValidator allows trailing newline in usernames."* Gold: `django/contrib/auth/validators.py`. All 5 seeds are tests or test models (`UsernameValidatorsTests`, `return_usernames()` …). Without tests, the scorer ranks the gold file 9th → in the top 5.
- *"sqlmigrate wraps it's outpout in BEGIN/COMMIT even if the database doesn't support…"* Gold: `django/core/management/commands/sqlmigrate.py`. The seeds include `.test_sqlmigrate_for_non_transactional_databases()`, `TransactionalTests` and two test docstrings.

**3. BFS spreading and degree ordering under the budget (92 of 103 misses: BFS reached a gold-file node, but the answer shows it 6th or later, or cuts it).**

From about 7 seeds at depth 3, the 2k-token answer can hold about 40 of roughly 2,000 visited nodes. They are ordered by hop and degree, never by relevance.

- *"Merging 3 or more media objects can throw unnecessary MediaOrderConflictWarnings."* The scorer had the gold file `django/forms/widgets.py` 3rd, but the seeds were `Media` (admin), `Thrower()`, `more_operations.py` and jQuery. The answer shows admin widgets, context processors and jquery.js, and never reaches the gold file.
- *"Rewrite fails when first expression of file is a number and mistaken as docstring."* The scorer ranks `src/_pytest/assertion/rewrite.py` 4th, but the answer shows it 8th behind `testing/test_assertrewrite.py` and hubs.

Re-ordering alone does not fix this. The "v8 ordered by v8 score" variant stays at 42% (#3284, #2376 and #3285 likewise sit at 37–41%), because the scores being re-ordered are the names-only ones. **Fixing cause 1 is what makes ordering useful.**

## The prototypes

`proto.py` builds on v8's graph, traversal view and NODE format, with the same budget cut.

1. **Body index (cause 1, which no PR covers).**
   - Each node gets the words of its own source lines: identifier parts (camelCase and snake_case split), docstring words and comment words. The span runs from its start line to the next node's start, at most 150 lines.
   - Nodes are scored with BM25 over the label (×2), the path tokens and those body words.
   - In graphify this means storing a `body_terms` set per node at extract time. The *_set* rows above show a plain unique-term set loses only 1 point. That adds about 20% to graph.json: Django grows 48 → 57 MB, Sphinx 10.4 → 13.1 MB.
2. **Source over tests and docs (cause 2).** Test-path and doc nodes get ×0.3 unless the question says test, fixture, doc and similar words. #2403 and #3417 do part of this, but only on top of names-only scores.
3. **File-first answer (cause 3).**
   - Files are ranked by their best node's score plus 0.3 × their next 5 nodes.
   - The best node of each of the top 5 files leads the answer.
   - Their 1-hop neighbours follow, ordered by BM25 score, capped at 30 nodes.

**Ablation (top-5):**

| Variant | Top-5 |
|---|---|
| Label + path BM25 + demotion | 58% |
| + body words | 69% (+11) |
| + file-first | 71% |
| Body BM25 without the demotion | 54% (demotion is worth +15) |

Keeping v8's depth-3 BFS render with body-BM25 seeds still gives 68%. Seeding matters more than rendering; the relevance render mainly cuts tokens (2.2k → 1.4k).

## Recommendation

**Change seeding to BM25 over node text that includes body words, with tests and docs demoted unless the question asks for them. Then lead the answer with the best node of each top-ranked file.** This is prototype A.

- **Numbers:** top-1 **44%**, top-3 **62%**, top-5 **71%**, median **1,381 tokens**.
- **Versus v8:** 26% / 34% / 42% at 2,194 tokens.
- **Versus BM25 over whole files:** 31% / 55% / 63% at about 42k tokens to read the files.
- **Versus the best PR (#3417 and #2403):** 51% top-5.
- **Storage-friendly form** (unique body terms in graph.json): 42% / 64% / 70% at 1,369 tokens.

It is the only variant that beats BM25 on top-1, top-3 and top-5 while giving a smaller answer than today. It is no larger than v8's answer and about 1/30th of BM25's reading cost.

Caveats:

- The advantage over BM25 comes from Django (76% vs 62%). On the other 63 questions it is slightly behind (60% vs 65%), and the paired test is borderline (27 wins vs 14 losses, p ≈ 0.06).
- About 36 misses (20%) are vocabulary gaps no lexical method fixes.
- Weights such as ×0.3, ×2 label and the 0.3 file pooling were set once and **not tuned** on these questions.

To fit the maintainer's stated bar, it would land as small PRs, each with a before/after run of this benchmark:

1. Extractor: emit `body_terms` per node.
2. A BM25 body tier layered **on top of** the existing tiers for seeding, keeping the per-term guarantee and leaving `path`/`explain` resolution untouched.
3. Test and doc demotion (could build on #2403).
4. File-first ordering of the answer.

## Commands (all from the repo root unless noted)

```bash
git remote add upstream https://github.com/Graphify-Labs/graphify.git && git fetch upstream v8
git checkout -b claude/query-study upstream/v8
git cherry-pick 5a8e560a 0b1f76a7   # PR #4342 harness; __main__.py help-text conflict resolved by hand
pip install uv && uv sync --all-extras --frozen
```

```bash
# answer key (S = scratch dir; repos cloned with --filter=blob:none into $S/repos)
curl -L -o $S/dl/lite.parquet https://huggingface.co/datasets/princeton-nlp/SWE-bench_Lite/resolve/main/data/test-00000-of-00001.parquet
python3 -I research/query/make_questions.py $S/dl/lite.parquet $S/repos research/query/questions
# per repo: git checkout <commit from questions/commits.json>, then
(cd $S/repos/<repo> && uv run --frozen --project /home/user/graphify graphify update .)
```

```bash
# baselines
research/query/run_bench.sh v8 /home/user/graphify $S/graphs     # = graphify benchmark <graph> --questions <file> --json, per repo
python3 -I research/query/bm25_files.py $S/graphs $S/repos research/query/results/bm25_files
```

```bash
# PRs
research/query/prep_pr.sh <N> $S/wt         # git fetch upstream pull/N/head:pr-N, worktree, cherry-pick harness
research/query/run_pr.sh <N> $S/wt $S/graphs
research/query/prep_base.sh <N> $S/wt       # PR merge-base control, run the same way
research/query/rebuild_with_pr.sh 4504 $S/wt $S/repos $S/graphs-4504   # extractor PRs (4504, 3636)
```

```bash
# gaps, prototypes, table
PYTHONPATH=. uv run --frozen python research/query/gap_analysis.py $S/graphs $S/repos research/query/results/gap_v8.json
python3 -I research/query/gap_flags.py
research/query/run_proto.sh <variant> $S/graphs $S/repos
uv run --frozen python research/query/table.py
```

## What failed or was not done

- **Initial checkout:** the first parallel `git checkout` of django and seaborn hung and left `index.lock`. I killed it and redid it with `checkout -f`.
- **`graphify update` warnings:** syntax-error warnings on a few non-Python files (django gis `.js`, astropy `.c/.h`, pylint test fixtures). The builds completed.
- **Conflicting PRs:** 15 PR heads conflicted in `benchmark.py`/`cli.py` and were run with `bench_driver.py`, which is verified identical to the harness on v8. 9 more conflicted only in help text, and I kept the PR side.
- **April-base PRs:** #166, #347, #424, #879 and #308 were not measured (see above). Their shared merge-base also fails the harness, because that old code requires the graph to sit under the CWD's `graphify-out/`.
- **#3856** ran without an API key and fell back to the keyword seeds.
- **API access:** the GitHub API and MCP are not available for `Graphify-Labs/graphify` in this session. PR feedback was read from the public PR web pages, and some role badges and bot texts were not visible (`pr_feedback.md`).
- **#3417 over-budget count:** the over-budget figure here (15/177) counts query_graph's own "complete answer over budget" notice. The earlier "146/177" figure matches "answers over 2,000 tokens" (150/177 here).
- `uv.lock` is unchanged. Nothing was pushed anywhere except `claude/query-study`.
