## cochange_v2: 107 killed mutants, failing test files as truth

| repo | mutants | view | R@10 | R@20 | hit@10 | section + first 10 graph files: R / hit / files shown |
|---|---|---|---|---|---|---|
| click | 35 | before | 0.223 | 0.359 | 0.543 |  |
| click | 35 | after | 0.281 | 0.396 | 0.743 | 0.294 / 0.743 / 11.8 |
| click | 35 | graph_only_now | 0.223 | 0.359 | 0.543 |  |
| flask | 33 | before | 0.262 | 0.297 | 0.485 |  |
| flask | 33 | after | 0.214 | 0.309 | 0.485 | 0.306 / 0.576 / 14.3 |
| flask | 33 | graph_only_now | 0.262 | 0.297 | 0.485 |  |
| httpx | 39 | before | 0.027 | 0.209 | 0.128 |  |
| httpx | 39 | after | 0.189 | 0.253 | 0.538 | 0.209 / 0.615 / 15.6 |
| httpx | 39 | graph_only_now | 0.027 | 0.209 | 0.128 |  |
| pooled | 107 | before | 0.164 | 0.285 | 0.374 |  |
| pooled | 107 | after | 0.227 | 0.317 | 0.589 | 0.267 / 0.645 / 14.0 |
| pooled | 107 | graph_only_now | 0.164 | 0.285 | 0.374 |  |

McNemar hit@10, after vs before: only after 29, only before 6, p = 0.00012

McNemar hit@10, graph_only_now vs before: only graph_only_now 0, only before 0, p = 1

Graph result SET identical to the recorded v8 set for 107 of 107 mutants.
