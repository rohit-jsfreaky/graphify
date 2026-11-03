
### tune (Django): 114 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| pr1 | 28% (32) | 40% (46) | 48% (55) | 54% | 2,189 |
| proto_tuned_set | 54% (62) | 70% (80) | 80% (91) | 82% | 1,680 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned_set vs pr1 | 39 | 3 | 5.63e-09 |

### held-out Lite (63): 63 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| pr1 | 29% (18) | 43% (27) | 56% (35) | 62% | 2,197 |
| proto_tuned_set | 38% (24) | 57% (36) | 67% (42) | 73% | 1,129 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned_set vs pr1 | 12 | 5 | 0.143 |

### held-out Verified (116): 116 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| pr1 | 32% (37) | 59% (68) | 65% (75) | 72% | 2,202 |
| proto_tuned_set | 47% (55) | 68% (79) | 79% (92) | 81% | 1,275 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned_set vs pr1 | 21 | 4 | 0.000911 |

### held-out all non-Django: 179 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| pr1 | 31% (55) | 53% (95) | 61% (110) | 68% | 2,201 |
| proto_tuned_set | 44% (79) | 64% (115) | 75% (134) | 78% | 1,248 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned_set vs pr1 | 33 | 9 | 0.000272 |

Per repo (held-out all non-Django), top-5 hits:

| repo | n | pr1 | proto_tuned_set |
|---|---|---|---|
| astropy | 24 | 75% (18) | 92% (22) |
| flask | 4 | 100% (4) | 100% (4) |
| pylint | 15 | 33% (5) | 60% (9) |
| pytest | 34 | 53% (18) | 62% (21) |
| requests | 13 | 69% (9) | 62% (8) |
| seaborn | 6 | 67% (4) | 83% (5) |
| sphinx | 57 | 60% (34) | 77% (44) |
| xarray | 26 | 69% (18) | 81% (21) |

Per repo (held-out all non-Django), McNemar on top-5 (A only / B only, p):

| repo | proto_tuned_set vs pr1 |
|---|---|
| astropy | 4/0, p=0.12 |
| flask | 0/0, p=1 |
| pylint | 4/0, p=0.12 |
| pytest | 7/4, p=0.55 |
| requests | 1/2, p=1 |
| seaborn | 2/1, p=1 |
| sphinx | 11/1, p=0.0063 |
| xarray | 4/1, p=0.38 |

### all questions: 293 questions

| system | top-1 | top-3 | top-5 | anywhere | median tokens |
|---|---|---|---|---|---|
| pr1 | 30% (87) | 48% (141) | 56% (165) | 62% | 2,197 |
| proto_tuned_set | 48% (141) | 67% (195) | 77% (225) | 80% | 1,360 |

| pair (top-5) | A only | B only | McNemar p |
|---|---|---|---|
| proto_tuned_set vs pr1 | 72 | 12 | 1.39e-11 |

Per repo (all questions), top-5 hits:

| repo | n | pr1 | proto_tuned_set |
|---|---|---|---|
| astropy | 24 | 75% (18) | 92% (22) |
| django | 114 | 48% (55) | 80% (91) |
| flask | 4 | 100% (4) | 100% (4) |
| pylint | 15 | 33% (5) | 60% (9) |
| pytest | 34 | 53% (18) | 62% (21) |
| requests | 13 | 69% (9) | 62% (8) |
| seaborn | 6 | 67% (4) | 83% (5) |
| sphinx | 57 | 60% (34) | 77% (44) |
| xarray | 26 | 69% (18) | 81% (21) |

Per repo (all questions), McNemar on top-5 (A only / B only, p):

| repo | proto_tuned_set vs pr1 |
|---|---|
| astropy | 4/0, p=0.12 |
| django | 39/3, p=5.6e-09 |
| flask | 0/0, p=1 |
| pylint | 4/0, p=0.12 |
| pytest | 7/4, p=0.55 |
| requests | 1/2, p=1 |
| seaborn | 2/1, p=1 |
| sphinx | 11/1, p=0.0063 |
| xarray | 4/1, p=0.38 |
