
### tune (Django): 114 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 27% (31) | 34% (39) | 38% (43) | 51% | 2,192 |
| pr1 | 28% (32) | 40% (46) | 48% (55) | 54% | 2,189 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr1 vs v8 | 12 | 0 | 0.000488 |

### held-out Lite (63): 63 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 24% (15) | 33% (21) | 49% (31) | 75% | 2,196 |
| pr1 | 29% (18) | 43% (27) | 56% (35) | 62% | 2,197 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr1 vs v8 | 7 | 3 | 0.344 |

### held-out Verified (116): 116 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 28% (32) | 50% (58) | 59% (69) | 78% | 2,193 |
| pr1 | 32% (37) | 59% (68) | 65% (75) | 72% | 2,202 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr1 vs v8 | 7 | 1 | 0.0703 |

### held-out all non-Django: 179 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 26% (47) | 44% (79) | 56% (100) | 77% | 2,195 |
| pr1 | 31% (55) | 53% (95) | 61% (110) | 68% | 2,201 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr1 vs v8 | 14 | 4 | 0.0309 |

Per repo (held-out all non-Django), top-5 hits:

| repo | n | v8 | pr1 |
|---|---|---|---|
| astropy | 24 | 75% (18) | 75% (18) |
| flask | 4 | 75% (3) | 100% (4) |
| pylint | 15 | 20% (3) | 33% (5) |
| pytest | 34 | 50% (17) | 53% (18) |
| requests | 13 | 62% (8) | 69% (9) |
| seaborn | 6 | 83% (5) | 67% (4) |
| sphinx | 57 | 53% (30) | 60% (34) |
| xarray | 26 | 62% (16) | 69% (18) |

### all questions: 293 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 27% (78) | 40% (118) | 49% (143) | 67% | 2,193 |
| pr1 | 30% (87) | 48% (141) | 56% (165) | 62% | 2,197 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr1 vs v8 | 26 | 4 | 5.95e-05 |

Per repo (all questions), top-5 hits:

| repo | n | v8 | pr1 |
|---|---|---|---|
| astropy | 24 | 75% (18) | 75% (18) |
| django | 114 | 38% (43) | 48% (55) |
| flask | 4 | 75% (3) | 100% (4) |
| pylint | 15 | 20% (3) | 33% (5) |
| pytest | 34 | 50% (17) | 53% (18) |
| requests | 13 | 62% (8) | 69% (9) |
| seaborn | 6 | 83% (5) | 67% (4) |
| sphinx | 57 | 53% (30) | 60% (34) |
| xarray | 26 | 62% (16) | 69% (18) |
