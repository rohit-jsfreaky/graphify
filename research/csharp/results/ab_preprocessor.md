## A/B: library-only copy, raw vs #if-blanked (same answer key)
### lib
### All three projects

| kind | compiler links | graphify found | recall % | found via `calls` edge | found only via other relation |
|---|---:|---:|---:|---:|---:|
| same | 2819 | 2497 | 88.6 | 2497 | 0 |
| inherited | 422 | 302 | 71.6 | 302 | 0 |
| static | 948 | 807 | 85.1 | 807 | 0 |
| typed | 986 | 680 | 69.0 | 680 | 0 |
| extension | 871 | 1 | 0.1 | 1 | 0 |
| interface | 188 | 104 | 55.3 | 104 | 0 |
| generic | 321 | 263 | 81.9 | 263 | 0 |
| ctor | 710 | 478 | 67.3 | 433 | 45 |
| other | 84 | 71 | 84.5 | 71 | 0 |
| **total** | **7349** | **5203** | **70.8** | 5158 | 45 |
### pp
### All three projects

| kind | compiler links | graphify found | recall % | found via `calls` edge | found only via other relation |
|---|---:|---:|---:|---:|---:|
| same | 2819 | 2598 | 92.2 | 2598 | 0 |
| inherited | 422 | 376 | 89.1 | 376 | 0 |
| static | 948 | 834 | 88.0 | 834 | 0 |
| typed | 986 | 838 | 85.0 | 838 | 0 |
| extension | 871 | 1 | 0.1 | 1 | 0 |
| interface | 188 | 104 | 55.3 | 104 | 0 |
| generic | 321 | 265 | 82.6 | 265 | 0 |
| ctor | 710 | 475 | 66.9 | 430 | 45 |
| other | 84 | 71 | 84.5 | 71 | 0 |
| **total** | **7349** | **5562** | **75.7** | 5517 | 45 |
