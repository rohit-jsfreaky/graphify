## Ranking only: same v8 result set, different order (depth 2)

| repo | queries | order | R@5 | R@10 | R@20 | hit@10 | P@10 |
|---|---|---|---|---|---|---|---|
| django | 760 | bfs | 0.087 | 0.114 | 0.155 | 0.250 | 0.031 |
| django | 760 | dist_edges | 0.137 | 0.151 | 0.173 | 0.303 | 0.040 |
| django | 760 | dist_nodes | 0.133 | 0.151 | 0.173 | 0.301 | 0.039 |
| django | 760 | edges_only | 0.136 | 0.150 | 0.168 | 0.304 | 0.039 |
| flask | 31 | bfs | 0.019 | 0.058 | 0.126 | 0.161 | 0.016 |
| flask | 31 | dist_edges | 0.052 | 0.145 | 0.174 | 0.258 | 0.032 |
| flask | 31 | dist_nodes | 0.052 | 0.145 | 0.190 | 0.258 | 0.032 |
| flask | 31 | edges_only | 0.052 | 0.058 | 0.090 | 0.129 | 0.016 |
| requests | 47 | bfs | 0.291 | 0.365 | 0.411 | 0.681 | 0.281 |
| requests | 47 | dist_edges | 0.282 | 0.369 | 0.411 | 0.681 | 0.287 |
| requests | 47 | dist_nodes | 0.284 | 0.369 | 0.411 | 0.681 | 0.287 |
| requests | 47 | edges_only | 0.281 | 0.370 | 0.411 | 0.681 | 0.287 |
| hono | 473 | bfs | 0.284 | 0.318 | 0.344 | 0.414 | 0.052 |
| hono | 473 | dist_edges | 0.299 | 0.337 | 0.359 | 0.436 | 0.056 |
| hono | 473 | dist_nodes | 0.269 | 0.318 | 0.348 | 0.416 | 0.052 |
| hono | 473 | edges_only | 0.296 | 0.335 | 0.352 | 0.436 | 0.055 |
| jsoup | 297 | bfs | 0.068 | 0.117 | 0.158 | 0.337 | 0.068 |
| jsoup | 297 | dist_edges | 0.105 | 0.155 | 0.189 | 0.407 | 0.088 |
| jsoup | 297 | dist_nodes | 0.106 | 0.155 | 0.189 | 0.407 | 0.088 |
| jsoup | 297 | edges_only | 0.122 | 0.156 | 0.183 | 0.418 | 0.082 |
| caddy | 462 | bfs | 0.076 | 0.107 | 0.135 | 0.201 | 0.023 |
| caddy | 462 | dist_edges | 0.151 | 0.170 | 0.195 | 0.288 | 0.038 |
| caddy | 462 | dist_nodes | 0.148 | 0.170 | 0.195 | 0.288 | 0.038 |
| caddy | 462 | edges_only | 0.164 | 0.184 | 0.209 | 0.307 | 0.040 |
| ALL (repo mean) | 2070 | bfs | 0.138 | 0.180 | 0.221 | 0.341 | 0.079 |
| ALL (repo mean) | 2070 | dist_edges | 0.171 | 0.221 | 0.250 | 0.395 | 0.090 |
| ALL (repo mean) | 2070 | dist_nodes | 0.165 | 0.218 | 0.251 | 0.392 | 0.089 |
| ALL (repo mean) | 2070 | edges_only | 0.175 | 0.209 | 0.236 | 0.379 | 0.087 |

Sanity check: queries whose recomputed v8 top-20 differs from the study's stored v8 top-20: 0

