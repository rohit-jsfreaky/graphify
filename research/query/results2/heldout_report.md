
### tune (Django): 114 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 27% (31) | 34% (39) | 38% (43) | 51% | 2,192 |
| bm25files | 31% (35) | 54% (61) | 62% (71) | 100% | 41,355 |
| proto_before | 51% (58) | 67% (76) | 76% (87) | 79% | 1,733 |
| proto_tuned | 55% (63) | 75% (85) | 81% (92) | 83% | 1,766 |
| proto_tuned_set | 54% (62) | 70% (80) | 80% (91) | 82% | 1,680 |
| pr1 | 28% (32) | 40% (46) | 48% (55) | 54% | 2,189 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned vs bm25files | 24 | 3 | 4.92e-05 |
| proto_tuned vs v8 | 51 | 2 | 3.18e-13 |
| proto_before vs bm25files | 21 | 5 | 0.00249 |
| proto_before vs v8 | 46 | 2 | 8.36e-12 |
| proto_tuned_set vs bm25files | 23 | 3 | 8.8e-05 |
| proto_tuned vs proto_before | 6 | 1 | 0.125 |
| pr1 vs v8 | 12 | 0 | 0.000488 |

### held-out Lite (63): 63 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 24% (15) | 33% (21) | 49% (31) | 75% | 2,196 |
| bm25files | 30% (19) | 57% (36) | 65% (41) | 100% | 44,277 |
| proto_before | 37% (23) | 52% (33) | 62% (39) | 67% | 1,146 |
| proto_tuned | 38% (24) | 57% (36) | 65% (41) | 71% | 1,311 |
| proto_tuned_set | 38% (24) | 57% (36) | 67% (42) | 73% | 1,129 |
| pr1 | 29% (18) | 43% (27) | 56% (35) | 62% | 2,197 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned vs bm25files | 6 | 6 | 1 |
| proto_tuned vs v8 | 15 | 5 | 0.0414 |
| proto_before vs bm25files | 6 | 8 | 0.791 |
| proto_before vs v8 | 13 | 5 | 0.0963 |
| proto_tuned_set vs bm25files | 6 | 5 | 1 |
| proto_tuned vs proto_before | 5 | 3 | 0.727 |
| pr1 vs v8 | 7 | 3 | 0.344 |

### held-out Verified (116): 116 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 28% (32) | 50% (58) | 59% (69) | 78% | 2,193 |
| bm25files | 29% (34) | 55% (64) | 68% (79) | 100% | 49,060 |
| proto_before | 41% (48) | 66% (76) | 73% (85) | 75% | 1,468 |
| proto_tuned | 47% (54) | 71% (82) | 77% (89) | 79% | 1,489 |
| proto_tuned_set | 47% (55) | 68% (79) | 79% (92) | 81% | 1,275 |
| pr1 | 32% (37) | 59% (68) | 65% (75) | 72% | 2,202 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned vs bm25files | 15 | 5 | 0.0414 |
| proto_tuned vs v8 | 25 | 5 | 0.000325 |
| proto_before vs bm25files | 18 | 12 | 0.362 |
| proto_before vs v8 | 24 | 8 | 0.007 |
| proto_tuned_set vs bm25files | 20 | 7 | 0.0192 |
| proto_tuned vs proto_before | 9 | 5 | 0.424 |
| pr1 vs v8 | 7 | 1 | 0.0703 |

### held-out all non-Django: 179 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 26% (47) | 44% (79) | 56% (100) | 77% | 2,195 |
| bm25files | 30% (53) | 56% (100) | 67% (120) | 100% | 46,541 |
| proto_before | 40% (71) | 61% (109) | 69% (124) | 72% | 1,351 |
| proto_tuned | 44% (78) | 66% (118) | 73% (130) | 77% | 1,395 |
| proto_tuned_set | 44% (79) | 64% (115) | 75% (134) | 78% | 1,248 |
| pr1 | 31% (55) | 53% (95) | 61% (110) | 68% | 2,201 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned vs bm25files | 21 | 11 | 0.11 |
| proto_tuned vs v8 | 40 | 10 | 2.39e-05 |
| proto_before vs bm25files | 24 | 20 | 0.652 |
| proto_before vs v8 | 37 | 13 | 0.000936 |
| proto_tuned_set vs bm25files | 26 | 12 | 0.0336 |
| proto_tuned vs proto_before | 14 | 8 | 0.286 |
| pr1 vs v8 | 14 | 4 | 0.0309 |

Per repo (held-out all non-Django), top-5 hits:

| repo | n | v8 | bm25files | proto_before | proto_tuned | proto_tuned_set | pr1 |
|---|---|---|---|---|---|---|---|
| astropy | 24 | 75% (18) | 71% (17) | 92% (22) | 88% (21) | 92% (22) | 75% (18) |
| flask | 4 | 75% (3) | 75% (3) | 100% (4) | 100% (4) | 100% (4) | 100% (4) |
| pylint | 15 | 20% (3) | 60% (9) | 67% (10) | 67% (10) | 60% (9) | 33% (5) |
| pytest | 34 | 50% (17) | 56% (19) | 47% (16) | 59% (20) | 62% (21) | 53% (18) |
| requests | 13 | 62% (8) | 77% (10) | 69% (9) | 62% (8) | 62% (8) | 69% (9) |
| seaborn | 6 | 83% (5) | 33% (2) | 67% (4) | 83% (5) | 83% (5) | 67% (4) |
| sphinx | 57 | 53% (30) | 70% (40) | 72% (41) | 74% (42) | 77% (44) | 60% (34) |
| xarray | 26 | 62% (16) | 77% (20) | 69% (18) | 77% (20) | 81% (21) | 69% (18) |

Per repo (held-out all non-Django), McNemar on top-5 (A only / B only, p):

| repo | proto_tuned vs bm25files | proto_tuned vs v8 | proto_before vs bm25files | proto_before vs v8 | proto_tuned_set vs bm25files | proto_tuned vs proto_before | pr1 vs v8 |
|---|---|---|---|---|---|---|---|
| astropy | 4/0, p=0.12 | 4/1, p=0.38 | 5/0, p=0.062 | 4/0, p=0.12 | 5/0, p=0.062 | 0/1, p=1 | 0/0, p=1 |
| flask | 1/0, p=1 | 1/0, p=1 | 1/0, p=1 | 1/0, p=1 | 1/0, p=1 | 0/0, p=1 | 1/0, p=1 |
| pylint | 3/2, p=1 | 7/0, p=0.016 | 3/2, p=1 | 8/1, p=0.039 | 3/3, p=1 | 2/2, p=1 | 2/0, p=0.5 |
| pytest | 2/1, p=1 | 6/3, p=0.51 | 2/5, p=0.45 | 4/5, p=1 | 3/1, p=0.62 | 5/1, p=0.22 | 3/2, p=1 |
| requests | 1/3, p=0.62 | 2/2, p=1 | 1/2, p=1 | 2/1, p=1 | 1/3, p=0.62 | 0/1, p=1 | 1/0, p=1 |
| seaborn | 3/0, p=0.25 | 1/1, p=1 | 2/0, p=0.5 | 1/2, p=1 | 3/0, p=0.25 | 1/0, p=1 | 0/1, p=1 |
| sphinx | 5/3, p=0.73 | 14/2, p=0.0042 | 7/6, p=1 | 12/1, p=0.0034 | 7/3, p=0.34 | 3/2, p=1 | 5/1, p=0.22 |
| xarray | 2/2, p=1 | 5/1, p=0.22 | 3/5, p=0.73 | 5/3, p=0.73 | 3/2, p=1 | 3/1, p=0.62 | 2/0, p=0.5 |

### all questions: 293 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 27% (78) | 40% (118) | 49% (143) | 67% | 2,193 |
| bm25files | 30% (88) | 55% (161) | 65% (191) | 100% | 44,991 |
| proto_before | 44% (129) | 63% (185) | 72% (211) | 75% | 1,426 |
| proto_tuned | 48% (141) | 69% (203) | 76% (222) | 79% | 1,521 |
| proto_tuned_set | 48% (141) | 67% (195) | 77% (225) | 80% | 1,360 |
| pr1 | 30% (87) | 48% (141) | 56% (165) | 62% | 2,197 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned vs bm25files | 45 | 14 | 6.53e-05 |
| proto_tuned vs v8 | 91 | 12 | 3.46e-16 |
| proto_before vs bm25files | 45 | 25 | 0.0225 |
| proto_before vs v8 | 83 | 15 | 1.4e-12 |
| proto_tuned_set vs bm25files | 49 | 15 | 2.44e-05 |
| proto_tuned vs proto_before | 20 | 9 | 0.0614 |
| pr1 vs v8 | 26 | 4 | 5.95e-05 |

Per repo (all questions), top-5 hits:

| repo | n | v8 | bm25files | proto_before | proto_tuned | proto_tuned_set | pr1 |
|---|---|---|---|---|---|---|---|
| astropy | 24 | 75% (18) | 71% (17) | 92% (22) | 88% (21) | 92% (22) | 75% (18) |
| django | 114 | 38% (43) | 62% (71) | 76% (87) | 81% (92) | 80% (91) | 48% (55) |
| flask | 4 | 75% (3) | 75% (3) | 100% (4) | 100% (4) | 100% (4) | 100% (4) |
| pylint | 15 | 20% (3) | 60% (9) | 67% (10) | 67% (10) | 60% (9) | 33% (5) |
| pytest | 34 | 50% (17) | 56% (19) | 47% (16) | 59% (20) | 62% (21) | 53% (18) |
| requests | 13 | 62% (8) | 77% (10) | 69% (9) | 62% (8) | 62% (8) | 69% (9) |
| seaborn | 6 | 83% (5) | 33% (2) | 67% (4) | 83% (5) | 83% (5) | 67% (4) |
| sphinx | 57 | 53% (30) | 70% (40) | 72% (41) | 74% (42) | 77% (44) | 60% (34) |
| xarray | 26 | 62% (16) | 77% (20) | 69% (18) | 77% (20) | 81% (21) | 69% (18) |

Per repo (all questions), McNemar on top-5 (A only / B only, p):

| repo | proto_tuned vs bm25files | proto_tuned vs v8 | proto_before vs bm25files | proto_before vs v8 | proto_tuned_set vs bm25files | proto_tuned vs proto_before | pr1 vs v8 |
|---|---|---|---|---|---|---|---|
| astropy | 4/0, p=0.12 | 4/1, p=0.38 | 5/0, p=0.062 | 4/0, p=0.12 | 5/0, p=0.062 | 0/1, p=1 | 0/0, p=1 |
| django | 24/3, p=4.9e-05 | 51/2, p=3.2e-13 | 21/5, p=0.0025 | 46/2, p=8.4e-12 | 23/3, p=8.8e-05 | 6/1, p=0.12 | 12/0, p=0.00049 |
| flask | 1/0, p=1 | 1/0, p=1 | 1/0, p=1 | 1/0, p=1 | 1/0, p=1 | 0/0, p=1 | 1/0, p=1 |
| pylint | 3/2, p=1 | 7/0, p=0.016 | 3/2, p=1 | 8/1, p=0.039 | 3/3, p=1 | 2/2, p=1 | 2/0, p=0.5 |
| pytest | 2/1, p=1 | 6/3, p=0.51 | 2/5, p=0.45 | 4/5, p=1 | 3/1, p=0.62 | 5/1, p=0.22 | 3/2, p=1 |
| requests | 1/3, p=0.62 | 2/2, p=1 | 1/2, p=1 | 2/1, p=1 | 1/3, p=0.62 | 0/1, p=1 | 1/0, p=1 |
| seaborn | 3/0, p=0.25 | 1/1, p=1 | 2/0, p=0.5 | 1/2, p=1 | 3/0, p=0.25 | 1/0, p=1 | 0/1, p=1 |
| sphinx | 5/3, p=0.73 | 14/2, p=0.0042 | 7/6, p=1 | 12/1, p=0.0034 | 7/3, p=0.34 | 3/2, p=1 | 5/1, p=0.22 |
| xarray | 2/2, p=1 | 5/1, p=0.22 | 3/5, p=0.73 | 5/3, p=0.73 | 3/2, p=1 | 3/1, p=0.62 | 2/0, p=0.5 |
