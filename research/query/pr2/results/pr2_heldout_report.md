
### tune (Django): 114 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 28% (32) | 40% (46) | 48% (55) | 54% | 2,190 |
| bm25files | 31% (35) | 54% (61) | 62% (71) | 100% | 41,355 |
| pr2 | 47% (54) | 67% (76) | 75% (85) | 76% | 2,217 |
| strict_tier_only | 30% (34) | 46% (53) | 53% (60) | 59% | 2,188 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr2 vs v8 | 31 | 1 | 1.54e-08 |
| pr2 vs bm25files | 20 | 6 | 0.00936 |
| strict_tier_only vs v8 | 7 | 2 | 0.18 |
| pr2 vs strict_tier_only | 25 | 0 | 5.96e-08 |

### held-out Lite (63): 63 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 29% (18) | 43% (27) | 56% (35) | 62% | 2,197 |
| bm25files | 30% (19) | 57% (36) | 65% (41) | 100% | 44,277 |
| pr2 | 37% (23) | 63% (40) | 71% (45) | 78% | 2,240 |
| strict_tier_only | 27% (17) | 48% (30) | 60% (38) | 70% | 2,203 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr2 vs v8 | 12 | 2 | 0.0129 |
| pr2 vs bm25files | 7 | 3 | 0.344 |
| strict_tier_only vs v8 | 4 | 1 | 0.375 |
| pr2 vs strict_tier_only | 8 | 1 | 0.0391 |

### held-out Verified (116): 116 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 32% (37) | 59% (68) | 65% (75) | 72% | 2,202 |
| bm25files | 29% (34) | 55% (64) | 68% (79) | 100% | 49,060 |
| pr2 | 49% (57) | 74% (86) | 78% (90) | 84% | 2,237 |
| strict_tier_only | 35% (41) | 60% (70) | 69% (80) | 74% | 2,200 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr2 vs v8 | 17 | 2 | 0.000729 |
| pr2 vs bm25files | 19 | 8 | 0.0522 |
| strict_tier_only vs v8 | 7 | 2 | 0.18 |
| pr2 vs strict_tier_only | 12 | 2 | 0.0129 |

### held-out all non-Django: 179 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 31% (55) | 53% (95) | 61% (110) | 69% | 2,202 |
| bm25files | 30% (53) | 56% (100) | 67% (120) | 100% | 46,541 |
| pr2 | 45% (80) | 70% (126) | 75% (135) | 82% | 2,237 |
| strict_tier_only | 32% (58) | 56% (100) | 66% (118) | 73% | 2,200 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr2 vs v8 | 29 | 4 | 1.09e-05 |
| pr2 vs bm25files | 26 | 11 | 0.0201 |
| strict_tier_only vs v8 | 11 | 3 | 0.0574 |
| pr2 vs strict_tier_only | 20 | 3 | 0.000488 |

Per repo (held-out all non-Django), top-5 hits:

| repo | n | v8 | bm25files | pr2 | strict_tier_only |
|---|---|---|---|---|---|
| astropy | 24 | 75% (18) | 71% (17) | 92% (22) | 75% (18) |
| flask | 4 | 100% (4) | 75% (3) | 100% (4) | 100% (4) |
| pylint | 15 | 33% (5) | 60% (9) | 53% (8) | 40% (6) |
| pytest | 34 | 53% (18) | 56% (19) | 74% (25) | 59% (20) |
| requests | 13 | 69% (9) | 77% (10) | 92% (12) | 77% (10) |
| seaborn | 6 | 67% (4) | 33% (2) | 50% (3) | 50% (3) |
| sphinx | 57 | 60% (34) | 70% (40) | 72% (41) | 67% (38) |
| xarray | 26 | 69% (18) | 77% (20) | 77% (20) | 73% (19) |

Per repo (held-out all non-Django), McNemar on top-5 (A only / B only, p):

| repo | pr2 vs v8 | pr2 vs bm25files | strict_tier_only vs v8 | pr2 vs strict_tier_only |
|---|---|---|---|---|
| astropy | 4/0, p=0.12 | 5/0, p=0.062 | 0/0, p=1 | 4/0, p=0.12 |
| flask | 0/0, p=1 | 1/0, p=1 | 0/0, p=1 | 0/0, p=1 |
| pylint | 4/1, p=0.38 | 2/3, p=1 | 2/1, p=1 | 2/0, p=0.5 |
| pytest | 7/0, p=0.016 | 6/0, p=0.031 | 2/0, p=0.5 | 5/0, p=0.062 |
| requests | 3/0, p=0.25 | 2/0, p=0.5 | 1/0, p=1 | 2/0, p=0.5 |
| seaborn | 0/1, p=1 | 2/1, p=1 | 0/1, p=1 | 0/0, p=1 |
| sphinx | 8/1, p=0.039 | 7/6, p=1 | 4/0, p=0.12 | 5/2, p=0.45 |
| xarray | 3/1, p=0.62 | 1/1, p=1 | 2/1, p=1 | 2/1, p=1 |

### all questions: 293 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| v8 | 30% (87) | 48% (141) | 56% (165) | 63% | 2,196 |
| bm25files | 30% (88) | 55% (161) | 65% (191) | 100% | 44,991 |
| pr2 | 46% (134) | 69% (202) | 75% (220) | 80% | 2,230 |
| strict_tier_only | 31% (92) | 52% (153) | 61% (178) | 67% | 2,196 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| pr2 vs v8 | 60 | 5 | 4.87e-13 |
| pr2 vs bm25files | 46 | 17 | 0.000337 |
| strict_tier_only vs v8 | 18 | 5 | 0.0106 |
| pr2 vs strict_tier_only | 45 | 3 | 1.31e-10 |

Per repo (all questions), top-5 hits:

| repo | n | v8 | bm25files | pr2 | strict_tier_only |
|---|---|---|---|---|---|
| astropy | 24 | 75% (18) | 71% (17) | 92% (22) | 75% (18) |
| django | 114 | 48% (55) | 62% (71) | 75% (85) | 53% (60) |
| flask | 4 | 100% (4) | 75% (3) | 100% (4) | 100% (4) |
| pylint | 15 | 33% (5) | 60% (9) | 53% (8) | 40% (6) |
| pytest | 34 | 53% (18) | 56% (19) | 74% (25) | 59% (20) |
| requests | 13 | 69% (9) | 77% (10) | 92% (12) | 77% (10) |
| seaborn | 6 | 67% (4) | 33% (2) | 50% (3) | 50% (3) |
| sphinx | 57 | 60% (34) | 70% (40) | 72% (41) | 67% (38) |
| xarray | 26 | 69% (18) | 77% (20) | 77% (20) | 73% (19) |

Per repo (all questions), McNemar on top-5 (A only / B only, p):

| repo | pr2 vs v8 | pr2 vs bm25files | strict_tier_only vs v8 | pr2 vs strict_tier_only |
|---|---|---|---|---|
| astropy | 4/0, p=0.12 | 5/0, p=0.062 | 0/0, p=1 | 4/0, p=0.12 |
| django | 31/1, p=1.5e-08 | 20/6, p=0.0094 | 7/2, p=0.18 | 25/0, p=6e-08 |
| flask | 0/0, p=1 | 1/0, p=1 | 0/0, p=1 | 0/0, p=1 |
| pylint | 4/1, p=0.38 | 2/3, p=1 | 2/1, p=1 | 2/0, p=0.5 |
| pytest | 7/0, p=0.016 | 6/0, p=0.031 | 2/0, p=0.5 | 5/0, p=0.062 |
| requests | 3/0, p=0.25 | 2/0, p=0.5 | 1/0, p=1 | 2/0, p=0.5 |
| seaborn | 0/1, p=1 | 2/1, p=1 | 0/1, p=1 | 0/0, p=1 |
| sphinx | 8/1, p=0.039 | 7/6, p=1 | 4/0, p=0.12 | 5/2, p=0.45 |
| xarray | 3/1, p=0.62 | 1/1, p=1 | 2/1, p=1 | 2/1, p=1 |
