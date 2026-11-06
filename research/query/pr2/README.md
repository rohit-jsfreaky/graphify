# PR 2 (body words): measurements

Branch `claude/query-pr2`, three commits on upstream `v8` (0.9.102):

1. `ba701e7c` feat(query): find code by the words in its body
2. `24d81d2d` docs: state the measured graph.json growth from body words
3. `388af93e` perf(query): keep the body ranking cheap in a new process

Names used below:
- **v8** = upstream/v8 0.9.102 (`59b5ab11`).
- **before** = PR 2 at `24d81d2d`.
- **after** = PR 2 at `388af93e`.

Every number below is in a file under `results/`. The scripts are in `scripts/`. They use absolute paths of the scratch folder where the repos and graphs lived; change those to rerun.

## Questions and graphs

There are 293 questions: the 177 SWE-bench Lite and 116 SWE-bench Verified questions in `../questions/` and `../questions_ext/`. 114 Django questions are for tuning; the 179 others are held out (`../split.json`).

Graphs are built with `scripts/build_set.sh`, which runs `python -m graphify update .`:
- One graph per base commit.
- A fresh `graphify-out/` each time; only the AST cache is kept.

Build times per commit (built 3 at a time, so not clean timings) are in `results/builds_pr2_all_commits.tsv`.

v8 answers were measured on the PR 2 graphs, because v8 ignores `body_terms`. Check: on all 114 Django questions, v8 on its own graph and v8 on the PR 2 graph give the same rank, tokens and top files (`results/eq-v8-on-v8graph.jsonl` vs `results/tuning/p2-v8.jsonl`).

## Answer quality: `results/pr2_heldout_report.md`

All four systems were run on all 293 questions with the real CLI, `graphify benchmark <graph> --questions <file> --json` (PR #4342 cherry-picked into a separate worktree), via `scripts/bench_cli.py`:
- `final2-v8.jsonl`
- `final2-pr2.jsonl` (before)
- `final2-strict.jsonl` (body tier only: no body seeds, no fusion)
- `final2-bm25files.jsonl` (BM25 over whole files, `../evalset.py`)

The report has top-1/3/5, anywhere, median tokens, per repo, and exact McNemar tests on top-5, from `../heldout_report.py`.

Tuning was on Django only (`scripts/tune2.sh`, `results/tuning/`). The chosen settings are in `results/tuning/pr2_frozen_params.json`, frozen at commit `ba701e7c` before the one held-out run.

## Size and build time: `results/pr2_build_size.tsv`

- Script: `scripts/time_cold.sh`.
- Commits: the Lite commit of each repo.
- Method: `graphify-out/` deleted first (no cache), v8 then PR 2 for each repo, one after another on a quiet machine.
- Reported: wall time of `python -m graphify update .`, graph.json bytes, and the number of nodes that have `body_terms`.

## Query speed: `results/speed/`

**Cold** (`cold.txt`, `scripts/cold_interleaved.sh`):
- Each call is a new process: `python -m graphify query "<question>" --graph <django graph.json>`, with the CLI defaults (BFS, depth 2, budget 2000).
- Questions: the first 10 Django questions, run twice, so 20 calls per version.
- The versions alternate call by call (v8, before, after, v8, ...), so slow moments on the machine hit all three.
- Each version uses its own graph: v8 its v8 graph, before/after the PR 2 graph.
- Reported: the median wall time of the 20 calls.

**Warm** (`warm.txt`, `scripts/warm_speed.py`):
- One process loads the Django graph and runs one query untimed.
- It then times `_query_graph_text` (same CLI defaults) for each of the 114 Django questions.
- Reported: the median; two runs per version.

**First-query parts** (`first_query_parts.txt`, `scripts/parts.py`):
- Wall time of the main steps of the first query in a new process, from wrappers around the `serve.py` functions.
- Some steps are nested: `_query_name_refusal` includes `_get_trigram_index`; `_render_query` includes `_traversal_view`; `_body_rank_files` includes `_body_doc_stats`.

| Django | v8 | before | after |
|---|---|---|---|
| cold CLI query, median of 20 | 3.63 s | 5.74 s | 3.86 s |
| warm query, median of 114 (run 1 / run 2) | 249 / 231 ms | 489 / 439 ms | 282 / 264 ms |

## Answers did not change: `results/identity/summary.txt`

`scripts/dump_answers.py` writes, for every question at depth 2 (CLI default) and depth 3 (MCP default), the SHA-256 of the full answer text and the list of NODE-line files in order. `scripts/identity_summary.py` compares the dumps.

- **Fixed hash seed (`PYTHONHASHSEED=0`), before vs after:** 586 answers, 0 text differences, 0 differences in files or their order.
- **Random hash seed, before vs after:** 9 answer texts differ, 0 differences in files or order. The differences are only the order of some EDGE lines. `scripts/show_diff.py` prints one answer, so two versions can be diffed, for example `sphinx-doc__sphinx-7757` at depth 3.
- **v8 vs v8 itself, random hash seed, two runs:** 21 answer texts differ, 0 file differences. So EDGE order already depends on Python's per-process hash seed in upstream v8; this change does not cause it.
- **`graphify benchmark --questions` on all 293 questions,** before (`final2-pr2.jsonl`) vs after (`final3-pr2fast.jsonl`): rank, tokens and top files are identical for every question.

## Checks on the final commit

**Full suite:** `PYTHONPATH="$PWD" uv run --frozen pytest tests -q`.

| Branch | Passed | Failed |
|---|---|---|
| PR 2 | 10,001 | 0 |
| v8 | 9,991 | 0 |

Source: `results/suite_pr2.txt`, `results/suite_v8.txt`. The watch tests in `tests/test_language_override_lifecycle.py` are known flaky: they fail now and then on both branches.

**Ruff:** `uv run --frozen ruff check .` is clean.

**Pyright** on `graphify/serve.py` and `tests/test_query_body_terms.py`: 67 errors before and after, with the same messages. None are new.
