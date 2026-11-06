### click @ ac0e297ec: 40 functions mutated, 35 broke at least one test file (0 broke the whole suite, 5 broke nothing); 43 test files; co-change from 490 commits before the commit (mined in 0.04 s); failing test files per mutant: 7.9

| predictor | recall@10 | recall@20 | hit@10 | mean list length |
|---|---|---|---|---|
| v8 `affected` (graph items) | 0.223 | 0.359 | 0.543 | 68.0 |
| v8 + co-change, printed order (graph, then section) | 0.223 | 0.359 | 0.543 | 68.6 |
| v8 + co-change, co-change first | 0.281 | 0.396 | 0.743 | 68.6 |
| first 10 graph files + whole co-change section (what a reader sees) | 0.294 | 0.294 | 0.743 | 11.8 |
| co-change section only (conf >= 0.2, top 10) | 0.239 | 0.239 | 0.629 | 3.7 |
| co-change, no confidence floor (top 50) | 0.326 | 0.431 | 0.771 | 19.6 |
| floor: test files whose name contains the module name | 0.099 | 0.099 | 0.286 | 0.4 |

### flask @ 49943b5a9: 40 functions mutated, 33 broke at least one test file (0 broke the whole suite, 7 broke nothing); 22 test files; co-change from 213 commits before the commit (mined in 0.04 s); failing test files per mutant: 5.8

| predictor | recall@10 | recall@20 | hit@10 | mean list length |
|---|---|---|---|---|
| v8 `affected` (graph items) | 0.262 | 0.297 | 0.485 | 15.8 |
| v8 + co-change, printed order (graph, then section) | 0.262 | 0.297 | 0.485 | 20.2 |
| v8 + co-change, co-change first | 0.214 | 0.309 | 0.485 | 20.2 |
| first 10 graph files + whole co-change section (what a reader sees) | 0.306 | 0.306 | 0.576 | 14.3 |
| co-change section only (conf >= 0.2, top 10) | 0.119 | 0.119 | 0.303 | 6.9 |
| co-change, no confidence floor (top 50) | 0.119 | 0.173 | 0.303 | 16.8 |
| floor: test files whose name contains the module name | 0.328 | 0.328 | 0.606 | 0.8 |

### httpx @ b5addb64f: 40 functions mutated, 39 broke at least one test file (0 broke the whole suite, 1 broke nothing); 31 test files; co-change from 279 commits before the commit (mined in 0.03 s); failing test files per mutant: 7.3

| predictor | recall@10 | recall@20 | hit@10 | mean list length |
|---|---|---|---|---|
| v8 `affected` (graph items) | 0.027 | 0.209 | 0.128 | 46.1 |
| v8 + co-change, printed order (graph, then section) | 0.027 | 0.247 | 0.128 | 49.0 |
| v8 + co-change, co-change first | 0.189 | 0.253 | 0.538 | 49.0 |
| first 10 graph files + whole co-change section (what a reader sees) | 0.209 | 0.209 | 0.615 | 15.6 |
| co-change section only (conf >= 0.2, top 10) | 0.189 | 0.189 | 0.538 | 9.1 |
| co-change, no confidence floor (top 50) | 0.189 | 0.273 | 0.538 | 27.8 |
| floor: test files whose name contains the module name | 0.138 | 0.138 | 0.436 | 0.6 |

### All repos pooled (107 killed mutants)

| predictor | recall@10 | recall@20 | hit@10 |
|---|---|---|---|
| v8 `affected` (graph items) | 0.164 | 0.285 | 0.374 |
| v8 + co-change, printed order (graph, then section) | 0.164 | 0.299 | 0.374 |
| v8 + co-change, co-change first | 0.227 | 0.317 | 0.589 |
| first 10 graph files + whole co-change section (what a reader sees) | 0.267 | 0.267 | 0.645 |
| co-change section only (conf >= 0.2, top 10) | 0.184 | 0.184 | 0.495 |
| co-change, no confidence floor (top 50) | 0.212 | 0.294 | 0.542 |
| floor: test files whose name contains the module name | 0.184 | 0.184 | 0.439 |

McNemar on hit@10, co-change first vs v8: only co-change-first hits 29, only v8 hits 6, p = 0.00012
McNemar, first 10 graph files + section vs v8 top 10: only the section view hits 29, only v8 hits 0, p = 3.7e-09

The printed order (graph, then section) equals v8 at k = 10 and 20 whenever the graph list is longer than k, which it usually is here.
