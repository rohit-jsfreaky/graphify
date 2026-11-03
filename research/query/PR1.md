# query: rank source above tests and docs, and answer file-first

Branch: `claude/query-pr1` (one commit on `upstream/v8` @ `8e6a6d21`).
Diff: `graphify/serve.py` +83 / −10, `tests/test_query_source_first.py` +125 (new).
No new stored data. `graph.json` does not change.

## Why

`query` scores node names only. A test named after a bug repeats the question's
words in its own name (`UsernameValidatorsTests`, `test_sqlmigrate_for_non_transactional_databases`),
so it wins the exact-name tier. On 177 SWE-bench Lite questions, 43% of the start
nodes were tests. Then the answer lists nodes by hop and degree, so hub files
fill the 2,000-token budget.

## What changes (query only)

1. **Source above tests and docs.** `_score_query` takes an optional `path_weight`.
   - Only `_query_graph_text` passes it. Test files, doc files, config files and
     nodes without a source file count ×0.3.
   - If the question says "test", "tests", "testing", "testcase" or "unittest", tests
     keep full weight. "doc", "docs", "documentation" or "readme" do the same for docs.
   - Tests are found by the existing `graphify.paths._is_test_path`, plus a
     `testing/` folder and `conftest.py`.
   - The weight scales both the combined score and the per-term singleton score.
     So **the per-term seed guarantee still holds**: every matched term still gets
     a seed, but a source node is preferred for it.
2. **File-first answer.** `_subgraph_to_text` takes optional `scores`.
   - When `query` passes them, the seeds and then the other nodes are listed file
     by file, best-scoring file first.
   - Nodes the question did not match keep the old order (hop, then degree) after
     them.

**Not changed:**
- `path`, `explain` and every other `_score_nodes` / `_subgraph_to_text` caller.
  The new arguments default to `None`, and the old code path runs unchanged.
- Traversal and depth.
- The token budget.
- The seed truncation guarantee: seeds are still the first lines.

## Result

Measured with `graphify benchmark --questions` (PR #4342) under the MCP defaults:
BFS, depth 3, 2,000-token budget.

- **Questions:** 293 SWE-bench Lite and Verified questions from 9 Python repos.
  Each question is asked against the graph of its own base commit.
- **Score:** "top-5" means a file the fix changed is among the first 5 files the
  answer shows.
- **Source files:** `research/query/results2/final-v8.jsonl` and `final-pr1.jsonl`,
  summarised in `results2/pr1_report.md`.
- **Cross-check:** the CLI benchmark on the Lite set gives the same numbers for this
  branch (`results/pr1-harness/`).

| | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| before (v8) | 27% (78) | 40% (118) | 49% (143) | 67% | 2,193 |
| after (this PR) | 30% (87) | 48% (141) | **56% (165)** | 62% | 2,197 |

Top-5, paired:
- This PR finds 26 questions that v8 misses.
- v8 finds 4 that this PR misses.
- Exact McNemar p = 6e-5.

**Per split (top-5):**

| Split | v8 | This PR | PR-only / v8-only | p |
|---|---|---|---|---|
| Django (114) | 38% | 48% | 12 / 0 | 5e-4 |
| Other 8 repos, Lite (63) | 49% | 56% | 7 / 3 | 0.34 |
| Other 8 repos, Verified (116) | 59% | 65% | 7 / 1 | 0.07 |

The weight 0.3 and the file-first rule were chosen on the Django questions only.

**Per repo (top-5):**

| Repo | n | v8 | This PR |
|---|---|---|---|
| astropy | 24 | 75% | 75% |
| django | 114 | 38% | 48% |
| flask | 4 | 75% | 100% |
| pylint | 15 | 20% | 33% |
| pytest | 34 | 50% | 53% |
| requests | 13 | 62% | 69% |
| seaborn | 6 | 83% | 67% |
| sphinx | 57 | 53% | 60% |
| xarray | 26 | 62% | 69% |

**Cost:**
- "Anywhere" drops from 67% to 62%. 30 questions had the gold file somewhere in v8's
  answer but not in this PR's; in 28 of those 30, v8 had shown it only 6th or later
  (6th to 32nd file). 17 questions go the other way.
- Answer size is unchanged.

**Variants tried on Django (114) before choosing:**

| Variant | Top-5 |
|---|---|
| v8 | 43 |
| Weight only | 51 |
| + order the non-seed nodes file-first | 51 |
| **+ also order the seed block file-first (this PR)** | **55** |
| + lead with the best node of the top 1 / 3 / 5 files | 54 / 52 / 48 |

## Tests

`tests/test_query_source_first.py` has 9 tests, one per behaviour:

1. A source node outranks its same-named test.
2. The `query` answer leads with source.
3. A question that names tests keeps tests at full weight.
4. Docs, config and source-less nodes are weighted down, and a question naming
   docs keeps docs at full weight.
5. pytest's `testing/` folder and `conftest.py` count as tests.
6. `path`/`explain` scoring (`_score_nodes`) is unchanged.
7. The per-term seed guarantee still seeds a term that only a test matches.
8. The answer is file-first, and the old order is kept without scores.
9. The seed block is file-first.

**Full suite on this branch:** 9,551 passed, 5 failed, 6 errors. All 11 are in
`tests/test_language_override_lifecycle.py` and `tests/test_graph_invariance.py`
(watch and rebuild timing).

| Branch | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| This branch | 35/35 | 35/35 | 35/35 |
| Plain `upstream/v8` | 35/35 | 35/35 | 1 failed |

These are the two files above run alone, three times on each branch. They are
flaky on v8 too, not caused by this change.

## Overlap with open upstream PRs

152 open PRs touch `graphify/serve.py`. 99 of them touch a function this PR changes:
`_score_query`, `_query_graph_text`, `_render_query` or `_subgraph_to_text`.
90 of those 99 already conflict with v8 inside `serve.py`; most are stale April–July
branches. Data: `results2/pr1_overlap/`.

**Same idea (would need a decision on which one lands):**
- **#2403** excludes `tests/` paths from the default seeds. Same goal as change 1;
  this PR weights instead of excluding, and also covers docs.
- **#3417** demotes test, fixture and vendor paths, and sorts the answer by relevance.
  It overlaps both changes.
- **#4601** weights seed scores by file type (docs ×0.7, images ×0.4). Same
  mechanism as change 1; tests are "code" there, so it does not demote tests.
- **#4481** leads the answer with the best node of the best-scoring file. Same aim
  as change 2. It merges with this PR without a textual conflict, but the two
  orderings would interact.
- **#3284** (same-hop relevance order), **#1782** and **#1658** (relevance order of
  the output) also overlap change 2.

**New textual conflicts in `serve.py`:** this PR conflicts with 6 open PRs that merge
cleanly with v8 today. All would need a small rebase:

| PR | Topic |
|---|---|
| #3284 | relevance order |
| #3636 | body attribute tier |
| #3866 | phrase bonus |
| #4478 | `--learned` seeds |
| #4576 | render rationale |
| #4601 | file-type weights |

**Merge clean with both v8 and this PR:** #4592, #4682, #4481.
