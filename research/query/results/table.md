| variant | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| upstream/v8 query_graph | 26% | 34% | 42% | 59% | 2,194 |
| BM25 over whole files (tokens = reading the 5 files) | 31% | 55% | 63% | 100% | 42,558 |

PRs (each on its own head, same v8-built graphs; base = its merge-base with v8):

| PR | how run | top-1 | top-3 | top-5 | anywhere | median tokens | base top-5 | Δ top-5 vs base |
|---|---|---|---|---|---|---|---|---|
| #3417 | cherry-pick | 28% | 44% | 51% | 71% | 2,549 | 38% | +24 q |
| #2403 | cherry-pick (help text kept) | 28% | 43% | 51% | 62% | 2,161 | 41% | +17 q |
| #4481 | cherry-pick | 27% | 35% | 44% | 60% | 2,194 | 42% | +3 q |
| #1856 | driver | 24% | 36% | 44% | 53% | 2,105 | 21% | +39 q |
| #4504 | cherry-pick | 26% | 35% | 44% | 60% | 2,191 | 42% | +3 q |
| #4504-rebuilt | cherry-pick, graphs rebuilt with PR | 25% | 35% | 43% | 61% | 2,194 | 42% | +2 q |
| #2516 | cherry-pick (help text kept) | 26% | 35% | 42% | 56% | 2,177 | 41% | +1 q |
| #4601 | cherry-pick | 26% | 34% | 42% | 59% | 2,194 | 42% | +0 q |
| #4470 | cherry-pick | 26% | 34% | 42% | 59% | 2,194 | 42% | +0 q |
| #4592 | cherry-pick (help text kept) | 26% | 34% | 42% | 63% | 2,203 | 42% | +0 q |
| #2294 | cherry-pick (help text kept) | 26% | 34% | 41% | 54% | 2,167 | 41% | +0 q |
| #2338 | cherry-pick (help text kept) | 26% | 34% | 41% | 54% | 2,167 | 41% | +0 q |
| #2376 | cherry-pick (help text kept) | 26% | 34% | 41% | 52% | 2,178 | 41% | +0 q |
| #2662 | cherry-pick (help text kept) | 26% | 35% | 41% | 54% | 2,177 | 41% | +0 q |
| #3636-rebuilt | cherry-pick, graphs rebuilt with PR | 25% | 34% | 39% | 59% | 2,177 | 38% | +2 q |
| #1782 | driver | 26% | 34% | 39% | 57% | 2,090 | 21% | +31 q |
| #3284 | cherry-pick | 25% | 34% | 38% | 52% | 2,175 | 37% | +2 q |
| #3636 | cherry-pick | 25% | 34% | 38% | 59% | 2,175 | 38% | +0 q |
| #3373 | cherry-pick | 25% | 34% | 38% | 59% | 2,175 | 37% | +1 q |
| #3856 | cherry-pick | 25% | 34% | 38% | 59% | 2,175 | 38% | +0 q |
| #3288 | cherry-pick | 25% | 34% | 37% | 53% | 2,178 | 37% | +0 q |
| #3837 | driver | 23% | 32% | 37% | 48% | 2,158 | 38% | -1 q |
| #2975 | cherry-pick (help text kept) | 27% | 34% | 37% | 53% | 2,168 | 37% | +0 q |
| #2113 | driver | 25% | 34% | 37% | 39% | 1,125 | 41% | -7 q |
| #2473 | cherry-pick (help text kept) | 25% | 34% | 37% | 52% | 2,168 | 41% | -7 q |
| #3285 | cherry-pick | 25% | 34% | 37% | 54% | 2,529 | 37% | -1 q |
| #1658 | driver | 26% | 31% | 36% | 57% | 2,097 | 27% | +15 q |
| #3866 | cherry-pick | 17% | 25% | 32% | 45% | 2,187 | 42% | -18 q |
| #1597 | driver | 8% | 22% | 27% | 33% | 505 | 27% | +0 q |
| #1724 | driver | 4% | 14% | 21% | 52% | 2,088 | 21% | +1 q |
| #1832 | driver | 3% | 14% | 21% | 54% | 2,095 | 20% | +1 q |
| #1918 | driver | 5% | 15% | 21% | 53% | 2,089 | 21% | -1 q |
| #1596 | driver | 3% | 11% | 18% | 52% | 2,097 | 27% | -16 q |

Prototypes (on top of upstream/v8, same graphs, same scoring):

| variant | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| bm25b_filefirst | 44% | 62% | 71% | 75% | 1,381 |
| bm25b_filefirst_set | 42% | 64% | 70% | 74% | 1,369 |
| bm25b_rel | 40% | 62% | 69% | 72% | 1,463 |
| bm25b_seeds | 40% | 62% | 68% | 79% | 2,190 |
| bm25b_rel_set | 40% | 60% | 67% | 69% | 1,149 |
| bm25n_rel | 35% | 52% | 58% | 63% | 1,242 |
| bm25n_seeds | 35% | 52% | 56% | 70% | 2,209 |
| bm25b_rel_tests | 24% | 46% | 54% | 60% | 1,198 |
| v8_noseedtests | 28% | 40% | 45% | 59% | 2,162 |
| v8_relrender | 26% | 34% | 42% | 64% | 1,361 |

Django (114) vs the other 8 repos (63), top-5:

| variant | django | others |
|---|---|---|
| v8 | 38% | 49% |
| bm25_files | 62% | 65% |
| pr-3417 | 51% | 52% |
| pr-2403 | 52% | 49% |
| proto-bm25b_filefirst | 76% | 60% |
| proto-bm25b_filefirst_set | 77% | 57% |
| proto-bm25b_rel | 75% | 60% |

Paired, top-5: bm25b_filefirst wins 27 questions BM25-files misses, loses 14 (sign test on 41 discordant pairs).
