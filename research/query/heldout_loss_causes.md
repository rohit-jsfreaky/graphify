# Why the prototype loses to BM25-files outside Django (Lite, 63 questions)

Prototype = `proto:bm25b_filefirst` with the first-study weights (`results2/chk_ff.jsonl`).
BM25-files = `results2/chk_bm25.jsonl`. A loss = BM25-files has a gold file in its top 5
and the prototype does not. Facts per question come from `loss_details.py` (rank of the
gold file under the prototype's file ranking with and without demotion, and with the
best node only instead of pooling).

On these 63 questions BM25-files wins 9, the prototype wins 6.

| Question | Cause (one line) |
|---|---|
| pytest-5221 "Display fixture scope with `pytest --fixtures`" | "pytest"/"fixture" count as test words, so demotion is switched off and two test files take top-5 places; gold is a big file (132 nodes) whose words are spread over many functions. |
| pytest-6116 "pytest --collect-only needs a one char shortcut command" | "pytest" in the question switches demotion off; testing/test_session.py and testing/test_config.py take top-5 places. |
| pytest-7168 "INTERNALERROR when exception in __repr__" | Gold is a small file (13 nodes); generic words (exception, repr) match nodes in many files, and whole-file term counts favour the small file that repeats "repr". |
| pytest-7373 "Incorrect caching of skipif/xfail string condition evaluation" | Pooling favours big files: best-node rank is 2 but pooled rank is 8; also a node with no source file, a doc example and azure-pipelines.yml take top-5 places (non-source files not demoted). |
| requests-2317 "method = builtin_str(method) problem" | Big gold file, words in function bodies: best-node rank 8, pooled 11; whole-file scoring is enough in an 83-file repo. |
| sphinx-7975 "Two sections called Symbols in index" | Pooling favours big files: domains/c.py and cpp.py (hundreds of nodes with "symbol"/"index") beat the 11-node gold file. |
| sphinx-8627 "autodoc isn't able to resolve struct.Struct type annotations" | Pooling favours big files: c.py and cpp.py again; gold ends 6th, just outside the top 5. |
| sphinx-8801 "The annotation only member in superclass is treated as undocumented" | Pooling favours big files (best-node rank 7, pooled 10); the words are spread in the gold file's bodies, which whole-file BM25 sees at once. |
| xarray-4493 "DataSet.update causes chunked dask DataArray to evaluate eagerly" | Gold is a huge file (172 nodes) whose words are spread across functions; prototype has it 6th, whole-file BM25 2nd. |

## Counted (a question can have two causes)

| Cause | Count |
|---|---|
| File ranking misses what whole-file scoring sees: big gold file with words spread over many functions, or pooling over 5 nodes favouring big files with many weak matches | 7 (5221, 7373, 2317, 7975, 8627, 8801, 4493) |
| Project-name test words ("pytest", "fixture") switch the test demotion off | 2 (5221, 6116) |
| Non-source files (no source file, .yml, doc examples) not demoted | 1 (7373) |
| Small gold file, generic words, whole-file term counts decide | 1 (7168) |

## What this says to change (to be tuned on Django only)

1. Add a whole-file signal to the file ranking: the file's own BM25 score over the
   body words of all its nodes, mixed with the best node's score (weight tuned on Django).
   Re-tune or drop the 5-node pooling.
2. Only "test", "tests", "testing", "testcase", "unittest" switch the demotion off;
   "pytest" and "fixture(s)" are feature words in a test-runner repo.
3. Demote non-source nodes too: no source file, config/data files (.yml, .yaml, .toml,
   .cfg, .ini, .json, .txt) and doc/example folders.
