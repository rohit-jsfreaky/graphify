## Dataset

| repo | HEAD | cut T (date) | test commits after T | in 2-20 files | used (>=1 query) | queries (seed files) | true files / query | share of changed files new since T | seeds in graph |
|---|---|---|---|---|---|---|---|---|---|
| django | d9d05f104 | 3e0190a45 (2026-05-08) | 537 | 327 | 244 | 760 | 4.8 | 10.5% | 100% |
| flask | 49943b5a9 | 2ac89889f (2026-04-09) | 26 | 15 | 14 | 31 | 4.3 | 0.0% | 100% |
| requests | 3c7baaa05 | 6ec76b4a3 (2026-04-27) | 54 | 26 | 14 | 47 | 7.9 | 11.1% | 100% |
| hono | eb754bd5e | f10dee89c (2026-05-06) | 302 | 202 | 185 | 473 | 2.6 | 3.4% | 99% |
| jsoup | d90d57521 | 477740fc0 (2026-05-04) | 169 | 91 | 79 | 297 | 5.2 | 3.8% | 100% |
| caddy | b3d67c861 | fb324331f (2026-05-07) | 286 | 245 | 165 | 462 | 3.4 | 18.1% | 100% |

### ALL (repo mean) — 2070 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.188 | 0.267 | 0.362 | 0.140 | 0.123 | 0.092 | 0.421 | 0.494 | 0.561 |
| v8 affected, depth 1 | 0.127 | 0.155 | 0.170 | 0.097 | 0.060 | 0.032 | 0.271 | 0.314 | 0.341 |
| v8 affected, depth 2 (default) | 0.138 | 0.180 | 0.221 | 0.107 | 0.079 | 0.050 | 0.281 | 0.341 | 0.385 |
| v8 affected, depth 3 | 0.138 | 0.184 | 0.238 | 0.107 | 0.083 | 0.056 | 0.282 | 0.345 | 0.396 |
| Co-change, support>=2, 3y | 0.398 | 0.485 | 0.519 | 0.213 | 0.136 | 0.077 | 0.662 | 0.736 | 0.745 |
| Co-change, support>=3, 3y | 0.343 | 0.387 | 0.401 | 0.167 | 0.098 | 0.054 | 0.569 | 0.610 | 0.613 |
| Co-change, support>=2, 3y, decay | 0.398 | 0.485 | 0.524 | 0.214 | 0.136 | 0.077 | 0.670 | 0.737 | 0.751 |
| Union: v8 d2 first, co-change fills | 0.293 | 0.403 | 0.502 | 0.181 | 0.135 | 0.089 | 0.518 | 0.636 | 0.724 |
| Union: co-change first, v8 d2 fills | 0.414 | 0.521 | 0.570 | 0.245 | 0.168 | 0.100 | 0.697 | 0.783 | 0.797 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.364 | 0.468 | 0.539 | 0.212 | 0.150 | 0.094 | 0.623 | 0.725 | 0.763 |
| Fusion: reciprocal rank (RRF) | 0.386 | 0.499 | 0.573 | 0.223 | 0.160 | 0.098 | 0.653 | 0.752 | 0.801 |
| Fusion with v8 depth 1 | 0.372 | 0.484 | 0.527 | 0.213 | 0.148 | 0.087 | 0.634 | 0.749 | 0.772 |
| Extra: graph both directions, depth 1 | 0.300 | 0.368 | 0.398 | 0.171 | 0.123 | 0.071 | 0.566 | 0.647 | 0.672 |
| Extra: graph both directions, depth 2 | 0.308 | 0.432 | 0.522 | 0.183 | 0.148 | 0.106 | 0.583 | 0.712 | 0.768 |
| Extra: fusion, both-directions graph + co-change | 0.399 | 0.508 | 0.605 | 0.233 | 0.170 | 0.117 | 0.695 | 0.800 | 0.840 |

### ALL (pooled) — 2070 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.200 | 0.269 | 0.339 | 0.103 | 0.080 | 0.052 | 0.382 | 0.467 | 0.540 |
| v8 affected, depth 1 | 0.120 | 0.146 | 0.171 | 0.058 | 0.037 | 0.022 | 0.228 | 0.278 | 0.320 |
| v8 affected, depth 2 (default) | 0.131 | 0.164 | 0.199 | 0.064 | 0.045 | 0.029 | 0.240 | 0.298 | 0.347 |
| v8 affected, depth 3 | 0.131 | 0.167 | 0.206 | 0.065 | 0.046 | 0.031 | 0.242 | 0.302 | 0.356 |
| Co-change, support>=2, 3y | 0.427 | 0.478 | 0.511 | 0.197 | 0.116 | 0.066 | 0.667 | 0.705 | 0.717 |
| Co-change, support>=3, 3y | 0.367 | 0.398 | 0.411 | 0.164 | 0.093 | 0.050 | 0.582 | 0.606 | 0.611 |
| Co-change, support>=2, 3y, decay | 0.428 | 0.475 | 0.513 | 0.196 | 0.115 | 0.066 | 0.670 | 0.705 | 0.719 |
| Union: v8 d2 first, co-change fills | 0.304 | 0.394 | 0.462 | 0.142 | 0.099 | 0.062 | 0.501 | 0.611 | 0.680 |
| Union: co-change first, v8 d2 fills | 0.439 | 0.499 | 0.544 | 0.208 | 0.126 | 0.074 | 0.696 | 0.744 | 0.767 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.377 | 0.452 | 0.500 | 0.177 | 0.113 | 0.067 | 0.621 | 0.695 | 0.727 |
| Fusion: reciprocal rank (RRF) | 0.406 | 0.485 | 0.541 | 0.188 | 0.122 | 0.073 | 0.658 | 0.729 | 0.765 |
| Fusion with v8 depth 1 | 0.389 | 0.464 | 0.503 | 0.182 | 0.115 | 0.067 | 0.636 | 0.704 | 0.731 |
| Extra: graph both directions, depth 1 | 0.328 | 0.373 | 0.406 | 0.144 | 0.089 | 0.051 | 0.578 | 0.642 | 0.680 |
| Extra: graph both directions, depth 2 | 0.336 | 0.403 | 0.475 | 0.150 | 0.101 | 0.067 | 0.587 | 0.675 | 0.748 |
| Extra: fusion, both-directions graph + co-change | 0.422 | 0.491 | 0.557 | 0.194 | 0.125 | 0.080 | 0.703 | 0.776 | 0.825 |

### django — 760 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.062 | 0.097 | 0.110 | 0.058 | 0.050 | 0.028 | 0.211 | 0.262 | 0.278 |
| v8 affected, depth 1 | 0.086 | 0.109 | 0.148 | 0.045 | 0.029 | 0.019 | 0.196 | 0.242 | 0.292 |
| v8 affected, depth 2 (default) | 0.087 | 0.114 | 0.155 | 0.047 | 0.031 | 0.021 | 0.200 | 0.250 | 0.303 |
| v8 affected, depth 3 | 0.087 | 0.114 | 0.156 | 0.047 | 0.031 | 0.021 | 0.200 | 0.250 | 0.304 |
| Co-change, support>=2, 3y | 0.298 | 0.327 | 0.345 | 0.142 | 0.080 | 0.044 | 0.503 | 0.532 | 0.543 |
| Co-change, support>=3, 3y | 0.251 | 0.272 | 0.282 | 0.115 | 0.063 | 0.034 | 0.433 | 0.455 | 0.462 |
| Co-change, support>=2, 3y, decay | 0.295 | 0.322 | 0.345 | 0.138 | 0.078 | 0.044 | 0.500 | 0.525 | 0.542 |
| Union: v8 d2 first, co-change fills | 0.230 | 0.288 | 0.349 | 0.113 | 0.074 | 0.046 | 0.436 | 0.520 | 0.593 |
| Union: co-change first, v8 d2 fills | 0.322 | 0.361 | 0.394 | 0.159 | 0.092 | 0.052 | 0.566 | 0.612 | 0.639 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.287 | 0.333 | 0.369 | 0.136 | 0.084 | 0.048 | 0.525 | 0.584 | 0.621 |
| Fusion: reciprocal rank (RRF) | 0.306 | 0.355 | 0.387 | 0.147 | 0.090 | 0.050 | 0.557 | 0.601 | 0.637 |
| Fusion with v8 depth 1 | 0.296 | 0.343 | 0.370 | 0.140 | 0.085 | 0.048 | 0.542 | 0.591 | 0.617 |
| Extra: graph both directions, depth 1 | 0.245 | 0.276 | 0.311 | 0.119 | 0.071 | 0.041 | 0.492 | 0.550 | 0.599 |
| Extra: graph both directions, depth 2 | 0.246 | 0.286 | 0.342 | 0.121 | 0.079 | 0.052 | 0.496 | 0.586 | 0.670 |
| Extra: fusion, both-directions graph + co-change | 0.314 | 0.354 | 0.410 | 0.153 | 0.095 | 0.060 | 0.597 | 0.667 | 0.738 |

### flask — 31 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.139 | 0.155 | 0.187 | 0.077 | 0.055 | 0.037 | 0.323 | 0.355 | 0.387 |
| v8 affected, depth 1 | 0.019 | 0.052 | 0.052 | 0.013 | 0.010 | 0.005 | 0.065 | 0.097 | 0.097 |
| v8 affected, depth 2 (default) | 0.019 | 0.058 | 0.126 | 0.013 | 0.016 | 0.021 | 0.065 | 0.161 | 0.226 |
| v8 affected, depth 3 | 0.019 | 0.058 | 0.126 | 0.013 | 0.016 | 0.021 | 0.065 | 0.161 | 0.226 |
| Co-change, support>=2, 3y | 0.289 | 0.415 | 0.450 | 0.148 | 0.110 | 0.071 | 0.516 | 0.677 | 0.677 |
| Co-change, support>=3, 3y | 0.289 | 0.415 | 0.432 | 0.148 | 0.110 | 0.063 | 0.516 | 0.677 | 0.677 |
| Co-change, support>=2, 3y, decay | 0.280 | 0.428 | 0.479 | 0.148 | 0.119 | 0.071 | 0.548 | 0.677 | 0.710 |
| Union: v8 d2 first, co-change fills | 0.161 | 0.274 | 0.412 | 0.071 | 0.061 | 0.056 | 0.290 | 0.452 | 0.613 |
| Union: co-change first, v8 d2 fills | 0.289 | 0.415 | 0.450 | 0.148 | 0.110 | 0.071 | 0.516 | 0.677 | 0.677 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.194 | 0.342 | 0.464 | 0.077 | 0.074 | 0.061 | 0.323 | 0.548 | 0.645 |
| Fusion: reciprocal rank (RRF) | 0.197 | 0.348 | 0.477 | 0.084 | 0.081 | 0.065 | 0.355 | 0.548 | 0.710 |
| Fusion with v8 depth 1 | 0.194 | 0.393 | 0.444 | 0.077 | 0.090 | 0.068 | 0.323 | 0.645 | 0.677 |
| Extra: graph both directions, depth 1 | 0.119 | 0.142 | 0.142 | 0.045 | 0.032 | 0.016 | 0.226 | 0.323 | 0.323 |
| Extra: graph both directions, depth 2 | 0.126 | 0.271 | 0.361 | 0.058 | 0.065 | 0.050 | 0.290 | 0.516 | 0.548 |
| Extra: fusion, both-directions graph + co-change | 0.119 | 0.323 | 0.474 | 0.071 | 0.071 | 0.056 | 0.290 | 0.581 | 0.645 |

### requests — 47 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.138 | 0.309 | 0.556 | 0.345 | 0.368 | 0.315 | 0.574 | 0.596 | 0.638 |
| v8 affected, depth 1 | 0.281 | 0.307 | 0.309 | 0.353 | 0.206 | 0.104 | 0.660 | 0.681 | 0.681 |
| v8 affected, depth 2 (default) | 0.291 | 0.365 | 0.411 | 0.383 | 0.281 | 0.166 | 0.660 | 0.681 | 0.681 |
| v8 affected, depth 3 | 0.291 | 0.379 | 0.478 | 0.383 | 0.298 | 0.196 | 0.660 | 0.681 | 0.702 |
| Co-change, support>=2, 3y | 0.286 | 0.470 | 0.470 | 0.243 | 0.181 | 0.090 | 0.596 | 0.745 | 0.745 |
| Co-change, support>=3, 3y | 0.195 | 0.195 | 0.195 | 0.089 | 0.045 | 0.022 | 0.362 | 0.362 | 0.362 |
| Co-change, support>=2, 3y, decay | 0.289 | 0.470 | 0.470 | 0.251 | 0.181 | 0.090 | 0.596 | 0.745 | 0.745 |
| Union: v8 d2 first, co-change fills | 0.338 | 0.497 | 0.677 | 0.404 | 0.326 | 0.207 | 0.723 | 0.809 | 0.915 |
| Union: co-change first, v8 d2 fills | 0.346 | 0.623 | 0.677 | 0.413 | 0.353 | 0.207 | 0.723 | 0.915 | 0.915 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.426 | 0.582 | 0.677 | 0.430 | 0.334 | 0.207 | 0.809 | 0.894 | 0.915 |
| Fusion: reciprocal rank (RRF) | 0.435 | 0.623 | 0.677 | 0.443 | 0.353 | 0.207 | 0.809 | 0.915 | 0.915 |
| Fusion with v8 depth 1 | 0.416 | 0.574 | 0.594 | 0.400 | 0.296 | 0.155 | 0.809 | 0.915 | 0.915 |
| Extra: graph both directions, depth 1 | 0.352 | 0.563 | 0.608 | 0.396 | 0.351 | 0.202 | 0.787 | 0.915 | 0.915 |
| Extra: graph both directions, depth 2 | 0.362 | 0.699 | 0.847 | 0.430 | 0.430 | 0.316 | 0.787 | 1.000 | 1.000 |
| Extra: fusion, both-directions graph + co-change | 0.541 | 0.703 | 0.853 | 0.515 | 0.432 | 0.317 | 0.957 | 1.000 | 1.000 |

### hono — 473 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.500 | 0.572 | 0.651 | 0.173 | 0.110 | 0.063 | 0.681 | 0.725 | 0.808 |
| v8 affected, depth 1 | 0.263 | 0.289 | 0.308 | 0.082 | 0.046 | 0.025 | 0.355 | 0.387 | 0.408 |
| v8 affected, depth 2 (default) | 0.284 | 0.318 | 0.344 | 0.091 | 0.052 | 0.030 | 0.376 | 0.414 | 0.436 |
| v8 affected, depth 3 | 0.287 | 0.320 | 0.347 | 0.092 | 0.052 | 0.031 | 0.378 | 0.416 | 0.438 |
| Co-change, support>=2, 3y | 0.662 | 0.716 | 0.755 | 0.207 | 0.121 | 0.067 | 0.865 | 0.901 | 0.918 |
| Co-change, support>=3, 3y | 0.597 | 0.628 | 0.637 | 0.181 | 0.100 | 0.052 | 0.789 | 0.812 | 0.816 |
| Co-change, support>=2, 3y, decay | 0.689 | 0.733 | 0.760 | 0.217 | 0.123 | 0.067 | 0.890 | 0.918 | 0.922 |
| Union: v8 d2 first, co-change fills | 0.614 | 0.684 | 0.740 | 0.192 | 0.114 | 0.066 | 0.799 | 0.858 | 0.892 |
| Union: co-change first, v8 d2 fills | 0.663 | 0.722 | 0.765 | 0.208 | 0.122 | 0.069 | 0.867 | 0.905 | 0.922 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.659 | 0.716 | 0.756 | 0.205 | 0.121 | 0.068 | 0.856 | 0.896 | 0.909 |
| Fusion: reciprocal rank (RRF) | 0.666 | 0.717 | 0.760 | 0.205 | 0.121 | 0.068 | 0.865 | 0.901 | 0.915 |
| Fusion with v8 depth 1 | 0.659 | 0.722 | 0.757 | 0.205 | 0.121 | 0.067 | 0.858 | 0.903 | 0.915 |
| Extra: graph both directions, depth 1 | 0.551 | 0.614 | 0.639 | 0.170 | 0.097 | 0.052 | 0.757 | 0.814 | 0.846 |
| Extra: graph both directions, depth 2 | 0.577 | 0.677 | 0.776 | 0.183 | 0.116 | 0.073 | 0.780 | 0.860 | 0.939 |
| Extra: fusion, both-directions graph + co-change | 0.661 | 0.743 | 0.803 | 0.210 | 0.129 | 0.076 | 0.863 | 0.932 | 0.956 |

### jsoup — 297 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.090 | 0.143 | 0.192 | 0.110 | 0.086 | 0.060 | 0.421 | 0.542 | 0.589 |
| v8 affected, depth 1 | 0.053 | 0.076 | 0.082 | 0.062 | 0.046 | 0.025 | 0.239 | 0.290 | 0.303 |
| v8 affected, depth 2 (default) | 0.068 | 0.117 | 0.158 | 0.077 | 0.068 | 0.045 | 0.259 | 0.337 | 0.387 |
| v8 affected, depth 3 | 0.068 | 0.126 | 0.184 | 0.077 | 0.073 | 0.052 | 0.259 | 0.347 | 0.414 |
| Co-change, support>=2, 3y | 0.443 | 0.528 | 0.618 | 0.378 | 0.231 | 0.141 | 0.882 | 0.902 | 0.909 |
| Co-change, support>=3, 3y | 0.406 | 0.460 | 0.505 | 0.347 | 0.204 | 0.115 | 0.838 | 0.848 | 0.852 |
| Co-change, support>=2, 3y, decay | 0.446 | 0.510 | 0.610 | 0.378 | 0.225 | 0.140 | 0.889 | 0.899 | 0.906 |
| Union: v8 d2 first, co-change fills | 0.306 | 0.427 | 0.537 | 0.263 | 0.191 | 0.125 | 0.684 | 0.805 | 0.859 |
| Union: co-change first, v8 d2 fills | 0.449 | 0.536 | 0.632 | 0.382 | 0.235 | 0.145 | 0.889 | 0.909 | 0.916 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.370 | 0.488 | 0.582 | 0.323 | 0.216 | 0.136 | 0.811 | 0.896 | 0.906 |
| Fusion: reciprocal rank (RRF) | 0.385 | 0.509 | 0.630 | 0.331 | 0.226 | 0.145 | 0.811 | 0.892 | 0.912 |
| Fusion with v8 depth 1 | 0.397 | 0.514 | 0.607 | 0.347 | 0.227 | 0.141 | 0.835 | 0.892 | 0.909 |
| Extra: graph both directions, depth 1 | 0.203 | 0.254 | 0.303 | 0.178 | 0.115 | 0.072 | 0.626 | 0.721 | 0.754 |
| Extra: graph both directions, depth 2 | 0.210 | 0.289 | 0.408 | 0.185 | 0.132 | 0.102 | 0.633 | 0.744 | 0.842 |
| Extra: fusion, both-directions graph + co-change | 0.336 | 0.453 | 0.581 | 0.289 | 0.200 | 0.138 | 0.835 | 0.936 | 0.963 |

### caddy — 462 queries

| predictor | R@5 | R@10 | R@20 | P@5 | P@10 | P@20 | hit@5 | hit@10 | hit@20 |
|---|---|---|---|---|---|---|---|---|---|
| Floor: same directory | 0.202 | 0.328 | 0.479 | 0.076 | 0.067 | 0.050 | 0.318 | 0.487 | 0.665 |
| v8 affected, depth 1 | 0.064 | 0.095 | 0.122 | 0.024 | 0.022 | 0.016 | 0.110 | 0.188 | 0.264 |
| v8 affected, depth 2 (default) | 0.076 | 0.107 | 0.135 | 0.027 | 0.023 | 0.017 | 0.123 | 0.201 | 0.277 |
| v8 affected, depth 3 | 0.076 | 0.110 | 0.138 | 0.028 | 0.025 | 0.018 | 0.128 | 0.214 | 0.292 |
| Co-change, support>=2, 3y | 0.412 | 0.456 | 0.472 | 0.159 | 0.091 | 0.050 | 0.613 | 0.660 | 0.675 |
| Co-change, support>=3, 3y | 0.320 | 0.350 | 0.354 | 0.120 | 0.068 | 0.035 | 0.476 | 0.506 | 0.511 |
| Co-change, support>=2, 3y, decay | 0.390 | 0.445 | 0.479 | 0.151 | 0.089 | 0.050 | 0.597 | 0.656 | 0.682 |
| Union: v8 d2 first, co-change fills | 0.111 | 0.248 | 0.295 | 0.040 | 0.045 | 0.032 | 0.177 | 0.374 | 0.472 |
| Union: co-change first, v8 d2 fills | 0.417 | 0.467 | 0.501 | 0.162 | 0.095 | 0.055 | 0.621 | 0.677 | 0.712 |
| Fusion: 0.5 conf + 0.5/depth (HEADLINE) | 0.250 | 0.349 | 0.383 | 0.103 | 0.069 | 0.041 | 0.416 | 0.532 | 0.584 |
| Fusion: reciprocal rank (RRF) | 0.330 | 0.441 | 0.504 | 0.127 | 0.088 | 0.053 | 0.519 | 0.652 | 0.716 |
| Fusion with v8 depth 1 | 0.268 | 0.361 | 0.388 | 0.107 | 0.071 | 0.042 | 0.437 | 0.548 | 0.600 |
| Extra: graph both directions, depth 1 | 0.330 | 0.360 | 0.388 | 0.118 | 0.069 | 0.041 | 0.509 | 0.558 | 0.597 |
| Extra: graph both directions, depth 2 | 0.331 | 0.369 | 0.399 | 0.119 | 0.070 | 0.042 | 0.509 | 0.567 | 0.610 |
| Extra: fusion, both-directions graph + co-change | 0.421 | 0.470 | 0.506 | 0.161 | 0.095 | 0.055 | 0.630 | 0.682 | 0.740 |

## v8 `affected` depth 2 without a cut-off (all files it returns)

| repo | mean files returned | recall over all returned files | share of queries returning nothing |
|---|---|---|---|
| django | 72.3 | 0.227 | 44% |
| flask | 10.7 | 0.206 | 45% |
| requests | 10.5 | 0.411 | 15% |
| hono | 11.9 | 0.373 | 48% |
| jsoup | 17.0 | 0.248 | 44% |
| caddy | 47.6 | 0.265 | 3% |

## Paired tests on hit@10 (McNemar, exact) and commit-level sign test on recall@10

| comparison | scope | queries both hit | only A hit | only B hit | McNemar p | commits A better | B better | tie | sign p |
|---|---|---|---|---|---|---|---|---|---|
| A=comb_fusion vs B=v8_d2 | ALL | 614 | 825 | 2 | 7.7e-244 | 521 | 1 | 179 | 7.6e-155 |
| A=comb_fusion vs B=v8_d2 | django | 190 | 254 | 0 | 6.9e-77 | 160 | 0 | 84 | 1.4e-48 |
| A=comb_fusion vs B=v8_d2 | flask | 5 | 12 | 0 | 0.00049 | 7 | 0 | 7 | 0.016 |
| A=comb_fusion vs B=v8_d2 | requests | 32 | 10 | 0 | 0.002 | 11 | 0 | 3 | 0.00098 |
| A=comb_fusion vs B=v8_d2 | hono | 196 | 228 | 0 | 4.6e-69 | 173 | 0 | 12 | 1.7e-52 |
| A=comb_fusion vs B=v8_d2 | jsoup | 99 | 167 | 1 | 9e-49 | 75 | 0 | 4 | 5.3e-23 |
| A=comb_fusion vs B=v8_d2 | caddy | 92 | 154 | 1 | 6.8e-45 | 95 | 1 | 69 | 2.4e-27 |
| A=comb_union_graph_first vs B=v8_d2 | ALL | 616 | 649 | 0 | 8.6e-196 | 465 | 0 | 236 | 2.1e-140 |
| A=comb_union_graph_first vs B=v8_d2 | django | 190 | 205 | 0 | 3.9e-62 | 154 | 0 | 90 | 8.8e-47 |
| A=comb_union_graph_first vs B=v8_d2 | flask | 5 | 9 | 0 | 0.0039 | 7 | 0 | 7 | 0.016 |
| A=comb_union_graph_first vs B=v8_d2 | requests | 32 | 6 | 0 | 0.031 | 7 | 0 | 7 | 0.016 |
| A=comb_union_graph_first vs B=v8_d2 | hono | 196 | 210 | 0 | 1.2e-63 | 169 | 0 | 16 | 2.7e-51 |
| A=comb_union_graph_first vs B=v8_d2 | jsoup | 100 | 139 | 0 | 2.9e-42 | 74 | 0 | 5 | 1.1e-22 |
| A=comb_union_graph_first vs B=v8_d2 | caddy | 93 | 80 | 0 | 1.7e-24 | 54 | 0 | 111 | 1.1e-16 |
| A=comb_union_cc_first vs B=v8_d2 | ALL | 594 | 946 | 22 | 2.8e-247 | 545 | 14 | 142 | 3.1e-141 |
| A=comb_union_cc_first vs B=v8_d2 | django | 184 | 281 | 6 | 6.1e-75 | 161 | 2 | 81 | 2.3e-45 |
| A=comb_union_cc_first vs B=v8_d2 | flask | 5 | 16 | 0 | 3.1e-05 | 10 | 0 | 4 | 0.002 |
| A=comb_union_cc_first vs B=v8_d2 | requests | 32 | 11 | 0 | 0.00098 | 13 | 0 | 1 | 0.00024 |
| A=comb_union_cc_first vs B=v8_d2 | hono | 192 | 236 | 4 | 1.6e-64 | 172 | 3 | 10 | 3.7e-47 |
| A=comb_union_cc_first vs B=v8_d2 | jsoup | 100 | 170 | 0 | 1.3e-51 | 75 | 0 | 4 | 5.3e-23 |
| A=comb_union_cc_first vs B=v8_d2 | caddy | 81 | 232 | 12 | 5.3e-54 | 114 | 9 | 42 | 2.7e-24 |
| A=comb_rrf vs B=v8_d2 | ALL | 608 | 901 | 8 | 5.2e-255 | 544 | 5 | 152 | 4.5e-154 |
| A=comb_rrf vs B=v8_d2 | django | 187 | 270 | 3 | 4.5e-76 | 162 | 1 | 81 | 2.8e-47 |
| A=comb_rrf vs B=v8_d2 | flask | 5 | 12 | 0 | 0.00049 | 7 | 0 | 7 | 0.016 |
| A=comb_rrf vs B=v8_d2 | requests | 32 | 11 | 0 | 0.00098 | 13 | 0 | 1 | 0.00024 |
| A=comb_rrf vs B=v8_d2 | hono | 196 | 230 | 0 | 1.2e-69 | 171 | 1 | 13 | 5.8e-50 |
| A=comb_rrf vs B=v8_d2 | jsoup | 99 | 166 | 1 | 1.8e-48 | 75 | 0 | 4 | 5.3e-23 |
| A=comb_rrf vs B=v8_d2 | caddy | 89 | 212 | 4 | 1.7e-57 | 116 | 3 | 46 | 8.5e-31 |
| A=cc_s2_3y vs B=v8_d2 | ALL | 513 | 946 | 103 | 2.9e-171 | 528 | 53 | 120 | 1.8e-99 |
| A=cc_s2_3y vs B=v8_d2 | django | 123 | 281 | 67 | 2.7e-32 | 147 | 32 | 65 | 8.2e-19 |
| A=cc_s2_3y vs B=v8_d2 | flask | 5 | 16 | 0 | 3.1e-05 | 10 | 0 | 4 | 0.002 |
| A=cc_s2_3y vs B=v8_d2 | requests | 24 | 11 | 8 | 0.65 | 10 | 4 | 0 | 0.18 |
| A=cc_s2_3y vs B=v8_d2 | hono | 190 | 236 | 6 | 7.6e-62 | 172 | 4 | 9 | 8.3e-46 |
| A=cc_s2_3y vs B=v8_d2 | jsoup | 98 | 170 | 2 | 5e-48 | 75 | 1 | 3 | 2e-21 |
| A=cc_s2_3y vs B=v8_d2 | caddy | 73 | 232 | 20 | 6.1e-47 | 114 | 12 | 39 | 5.1e-22 |
| A=comb_fusion vs B=cc_s2_3y | ALL | 1334 | 105 | 125 | 0.21 | 102 | 156 | 443 | 0.00093 |
| A=comb_fusion vs B=cc_s2_3y | django | 376 | 68 | 28 | 5.5e-05 | 57 | 40 | 147 | 0.1 |
| A=comb_fusion vs B=cc_s2_3y | flask | 17 | 0 | 4 | 0.12 | 0 | 4 | 10 | 0.12 |
| A=comb_fusion vs B=cc_s2_3y | requests | 34 | 8 | 1 | 0.039 | 4 | 1 | 9 | 0.38 |
| A=comb_fusion vs B=cc_s2_3y | hono | 418 | 6 | 8 | 0.79 | 17 | 15 | 153 | 0.86 |
| A=comb_fusion vs B=cc_s2_3y | jsoup | 264 | 2 | 4 | 0.69 | 10 | 33 | 36 | 0.00061 |
| A=comb_fusion vs B=cc_s2_3y | caddy | 225 | 21 | 80 | 2.7e-09 | 14 | 63 | 88 | 1.4e-08 |
| A=comb_union_cc_first vs B=cc_s2_3y | ALL | 1459 | 81 | 0 | 8.3e-25 | 87 | 0 | 614 | 1.3e-26 |
| A=comb_union_cc_first vs B=cc_s2_3y | django | 404 | 61 | 0 | 8.7e-19 | 58 | 0 | 186 | 6.9e-18 |
| A=comb_union_cc_first vs B=cc_s2_3y | flask | 21 | 0 | 0 | 1 | 0 | 0 | 14 | 1 |
| A=comb_union_cc_first vs B=cc_s2_3y | requests | 35 | 8 | 0 | 0.0078 | 4 | 0 | 10 | 0.12 |
| A=comb_union_cc_first vs B=cc_s2_3y | hono | 426 | 2 | 0 | 0.5 | 7 | 0 | 178 | 0.016 |
| A=comb_union_cc_first vs B=cc_s2_3y | jsoup | 268 | 2 | 0 | 0.5 | 6 | 0 | 73 | 0.031 |
| A=comb_union_cc_first vs B=cc_s2_3y | caddy | 305 | 8 | 0 | 0.0078 | 12 | 0 | 153 | 0.00049 |
| A=comb_fusion_undirected_d2 vs B=undirected_d2 | ALL | 1383 | 223 | 15 | 1.1e-48 | 224 | 16 | 461 | 4.2e-48 |
| A=comb_fusion_undirected_d2 vs B=undirected_d2 | django | 442 | 65 | 3 | 3.6e-16 | 63 | 3 | 178 | 1.3e-15 |
| A=comb_fusion_undirected_d2 vs B=undirected_d2 | flask | 16 | 2 | 0 | 0.5 | 2 | 1 | 11 | 1 |
| A=comb_fusion_undirected_d2 vs B=undirected_d2 | requests | 47 | 0 | 0 | 1 | 1 | 1 | 12 | 1 |
| A=comb_fusion_undirected_d2 vs B=undirected_d2 | hono | 404 | 37 | 3 | 1.9e-08 | 42 | 5 | 138 | 2.5e-08 |
| A=comb_fusion_undirected_d2 vs B=undirected_d2 | jsoup | 220 | 58 | 1 | 2.1e-16 | 65 | 0 | 14 | 5.4e-20 |
| A=comb_fusion_undirected_d2 vs B=undirected_d2 | caddy | 254 | 61 | 8 | 3.2e-11 | 51 | 6 | 108 | 5.7e-10 |

Commit-cluster bootstrap (2000 resamples), repo-mean recall@10 difference:

- comb_fusion − v8_d2: +0.288 (95% CI +0.253 … +0.348)
- comb_union_graph_first − v8_d2: +0.223 (95% CI +0.196 … +0.263)
- comb_union_cc_first − v8_d2: +0.341 (95% CI +0.303 … +0.402)
- comb_rrf − v8_d2: +0.319 (95% CI +0.282 … +0.381)
- cc_s2_3y − v8_d2: +0.306 (95% CI +0.261 … +0.382)
- comb_fusion − cc_s2_3y: -0.017 (95% CI -0.047 … +0.001)
- comb_union_cc_first − cc_s2_3y: +0.035 (95% CI +0.014 … +0.045)
- comb_fusion_undirected_d2 − undirected_d2: +0.076 (95% CI +0.057 … +0.105)

## Recall@10 by kind of true file (pooled over all queries)

| predictor | source code (n=3696) | test (n=3461) | config/build (n=273) | docs (n=881) | migrations/templates/other (n=228) |
|---|---|---|---|---|---|
| floor_same_dir | 0.248 | 0.195 | 0.099 | 0.024 | 0.061 |
| v8_d2 | 0.117 | 0.136 | 0.015 | 0.017 | 0.031 |
| undirected_d2 | 0.351 | 0.209 | 0.099 | 0.008 | 0.123 |
| cc_s2_3y | 0.323 | 0.231 | 0.187 | 0.370 | 0.158 |
| comb_fusion | 0.323 | 0.245 | 0.128 | 0.269 | 0.145 |
| comb_union_graph_first | 0.300 | 0.195 | 0.128 | 0.232 | 0.136 |
| comb_union_cc_first | 0.356 | 0.256 | 0.190 | 0.370 | 0.171 |
| comb_rrf | 0.354 | 0.251 | 0.147 | 0.304 | 0.158 |
| comb_fusion_undirected_d2 | 0.411 | 0.248 | 0.121 | 0.166 | 0.149 |

Share of true files that have any node in the v8 graph, by kind:

| source code | test | config/build | docs | migrations/templates/other |
|---|---|---|---|---|
| 100% | 98% | 87% | 37% | 42% |

Recall@10 by kind of true file, per repo (v8_d2 → comb_fusion):

| repo | source code | test | config/build | docs | migrations/templates/other |
|---|---|---|---|---|---|
| django | 0.051 → 0.215 (n=1072) | 0.096 → 0.172 (n=1786) | 0.098 → 0.415 (n=41) | 0.000 → 0.092 (n=568) | 0.031 → 0.150 (n=193) |
| flask | 0.097 → 0.323 (n=31) | 0.057 → 0.229 (n=35) | 0.000 → 0.021 (n=47) | 0.000 → 0.190 (n=21) | — |
| requests | 0.360 → 0.423 (n=317) | 0.857 → 0.905 (n=21) | 0.000 → 0.000 (n=29) | 0.000 → 1.000 (n=4) | — |
| hono | 0.093 → 0.467 (n=621) | 0.375 → 0.522 (n=504) | 0.000 → 0.179 (n=95) | 0.000 → 0.000 (n=9) | 0.000 → 0.000 (n=6) |
| jsoup | 0.199 → 0.461 (n=683) | 0.084 → 0.248 (n=597) | — | 0.056 → 0.663 (n=267) | 0.000 → 0.250 (n=8) |
| caddy | 0.070 → 0.220 (n=972) | 0.075 → 0.199 (n=518) | 0.000 → 0.000 (n=61) | 0.000 → 0.000 (n=12) | 0.048 → 0.095 (n=21) |

## By kind of seed file (pooled R@10 / hit@10)

| seed kind | queries | v8_d2 R@10 | undirected_d2 R@10 | cc_s2_3y R@10 | comb_fusion R@10 | comb_union_cc_first R@10 | v8_d2 hit@10 | comb_fusion hit@10 | comb_union_cc_first hit@10 |
|---|---|---|---|---|---|---|---|---|---|
| source code | 1033 | 0.293 | 0.409 | 0.495 | 0.463 | 0.525 | 0.505 | 0.730 | 0.791 |
| test | 980 | 0.025 | 0.399 | 0.468 | 0.444 | 0.478 | 0.073 | 0.664 | 0.702 |
| config/build | 21 | 0.310 | 0.447 | 0.419 | 0.443 | 0.443 | 0.476 | 0.667 | 0.667 |
| docs | 10 | 0.000 | 0.106 | 0.100 | 0.100 | 0.100 | 0.000 | 0.100 | 0.100 |
| migrations/templates/other | 26 | 0.234 | 0.400 | 0.394 | 0.453 | 0.466 | 0.462 | 0.731 | 0.769 |

## Cold start: history window before T (R@10 / hit@10, repo mean)

| repo | cc 3 months | cc 1 year | cc 3 years | fusion 3 months | fusion 1 year | fusion 3 years | v8_d2 | seeds with any rule (3m / 1y / 3y) |
|---|---|---|---|---|---|---|---|---|
| django | 0.065 / 0.11 | 0.220 / 0.37 | 0.327 / 0.53 | 0.158 / 0.32 | 0.257 / 0.47 | 0.333 / 0.58 | 0.114 / 0.25 | 18% / 52% / 71% |
| flask | 0.160 / 0.29 | 0.173 / 0.32 | 0.415 / 0.68 | 0.215 / 0.42 | 0.221 / 0.42 | 0.342 / 0.55 | 0.058 / 0.16 | 42% / 52% / 84% |
| requests | 0.149 / 0.34 | 0.149 / 0.34 | 0.470 / 0.74 | 0.478 / 0.81 | 0.478 / 0.81 | 0.582 / 0.89 | 0.365 / 0.68 | 51% / 51% / 79% |
| hono | 0.200 / 0.23 | 0.461 / 0.60 | 0.716 / 0.90 | 0.430 / 0.55 | 0.578 / 0.75 | 0.716 / 0.90 | 0.318 / 0.41 | 29% / 68% / 96% |
| jsoup | 0.035 / 0.11 | 0.298 / 0.60 | 0.528 / 0.90 | 0.151 / 0.40 | 0.344 / 0.68 | 0.488 / 0.90 | 0.117 / 0.34 | 14% / 63% / 93% |
| caddy | 0.144 / 0.19 | 0.234 / 0.34 | 0.456 / 0.66 | 0.211 / 0.33 | 0.264 / 0.39 | 0.349 / 0.53 | 0.107 / 0.20 | 39% / 51% / 87% |
| ALL | 0.125 / 0.21 | 0.256 / 0.43 | 0.485 / 0.74 | 0.274 / 0.47 | 0.357 / 0.59 | 0.468 / 0.73 | 0.180 / 0.34 | 26% / 57% / 84% |

## Cost of mining (3-year window) and of the stored rules

| repo | commits mined | bulk skipped (>30 files) | git log seconds | counting seconds | total seconds | files with history | pairs support>=2 | stored JSON bytes | gzip bytes | graph build seconds (v8, for scale) | graph nodes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| django | 2834 | 29 | 0.2 | 0.1 | 0.3 | 1685 | 3182 | 304,943 | 33,890 | 74.7 | 54,035 |
| flask | 294 | 1 | 0.02 | 0.01 | 0.03 | 115 | 596 | 37,078 | 3,708 | 3.0 | 2,346 |
| requests | 210 | 0 | 0.01 | 0.0 | 0.01 | 87 | 131 | 11,263 | 1,438 | 1.3 | 1,434 |
| hono | 1573 | 5 | 0.1 | 0.03 | 0.13 | 449 | 1367 | 102,519 | 9,890 | 5.2 | 3,332 |
| jsoup | 607 | 3 | 0.03 | 0.01 | 0.04 | 197 | 717 | 78,714 | 5,741 | 3.7 | 5,093 |
| caddy | 896 | 4 | 0.05 | 0.02 | 0.07 | 460 | 689 | 80,877 | 7,950 | 2.5 | 4,698 |

Seed resolution for v8 `affected` (how the seed file was mapped to a node):

- django: {'resolve_seed': 403}
- flask: {'resolve_seed': 22}
- requests: {'resolve_seed': 19}
- hono: {'all_nodes_of_file': 1, 'not_in_graph': 5, 'resolve_seed': 162}
- jsoup: {'resolve_seed': 79}
- caddy: {'all_nodes_of_file': 1, 'resolve_seed': 148}

