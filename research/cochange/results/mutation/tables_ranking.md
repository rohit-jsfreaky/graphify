## ranking: 107 killed mutants, failing test files as truth

| repo | mutants | view | R@10 | R@20 | hit@10 | section + first 10 graph files: R / hit / files shown |
|---|---|---|---|---|---|---|
| click | 35 | before | 0.223 | 0.359 | 0.543 |  |
| click | 35 | after | 0.223 | 0.368 | 0.571 |  |
| click | 35 | graph_only_now | 0.223 | 0.368 | 0.571 |  |
| flask | 33 | before | 0.262 | 0.297 | 0.485 |  |
| flask | 33 | after | 0.288 | 0.322 | 0.515 |  |
| flask | 33 | graph_only_now | 0.288 | 0.322 | 0.515 |  |
| httpx | 39 | before | 0.027 | 0.209 | 0.128 |  |
| httpx | 39 | after | 0.022 | 0.174 | 0.205 |  |
| httpx | 39 | graph_only_now | 0.022 | 0.174 | 0.205 |  |
| pooled | 107 | before | 0.164 | 0.285 | 0.374 |  |
| pooled | 107 | after | 0.170 | 0.283 | 0.421 |  |
| pooled | 107 | graph_only_now | 0.170 | 0.283 | 0.421 |  |

McNemar hit@10, after vs before: only after 8, only before 3, p = 0.23

McNemar hit@10, graph_only_now vs before: only graph_only_now 8, only before 3, p = 0.23

Graph result SET identical to the recorded v8 set for 107 of 107 mutants.
