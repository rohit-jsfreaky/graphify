### Dapper

| kind | compiler links | graphify found | recall % | found via `calls` edge | found only via other relation |
|---|---:|---:|---:|---:|---:|
| same | 262 | 230 | 87.8 | 230 | 0 |
| inherited | 2 | 0 | 0.0 | 0 | 0 |
| static | 33 | 22 | 66.7 | 22 | 0 |
| typed | 44 | 30 | 68.2 | 30 | 0 |
| extension | 24 | 0 | 0.0 | 0 | 0 |
| interface | 16 | 8 | 50.0 | 8 | 0 |
| generic | 185 | 176 | 95.1 | 176 | 0 |
| ctor | 116 | 83 | 71.6 | 83 | 0 |
| other | 24 | 24 | 100.0 | 24 | 0 |
| **total** | **706** | **573** | **81.2** | 573 | 0 |

### AutoMapper

| kind | compiler links | graphify found | recall % | found via `calls` edge | found only via other relation |
|---|---:|---:|---:|---:|---:|
| same | 314 | 289 | 92.0 | 289 | 0 |
| inherited | 30 | 23 | 76.7 | 23 | 0 |
| static | 36 | 31 | 86.1 | 31 | 0 |
| typed | 185 | 116 | 62.7 | 116 | 0 |
| extension | 269 | 1 | 0.4 | 1 | 0 |
| interface | 81 | 52 | 64.2 | 52 | 0 |
| generic | 19 | 11 | 57.9 | 11 | 0 |
| ctor | 196 | 88 | 44.9 | 69 | 19 |
| other | 48 | 41 | 85.4 | 41 | 0 |
| **total** | **1178** | **652** | **55.3** | 633 | 19 |

### Newtonsoft.Json

| kind | compiler links | graphify found | recall % | found via `calls` edge | found only via other relation |
|---|---:|---:|---:|---:|---:|
| same | 2243 | 1978 | 88.2 | 1978 | 0 |
| inherited | 390 | 279 | 71.5 | 279 | 0 |
| static | 879 | 754 | 85.8 | 754 | 0 |
| typed | 757 | 534 | 70.5 | 534 | 0 |
| extension | 578 | 0 | 0.0 | 0 | 0 |
| interface | 91 | 44 | 48.4 | 44 | 0 |
| generic | 117 | 76 | 65.0 | 76 | 0 |
| ctor | 398 | 307 | 77.1 | 281 | 26 |
| other | 12 | 6 | 50.0 | 6 | 0 |
| **total** | **5465** | **3978** | **72.8** | 3952 | 26 |

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

### Strict vs lenient (overload) matching

| project | links | found (exact overload node) | found (any same-name node in target file) |
|---|---:|---:|---:|
| Dapper | 706 | 546 | 573 |
| AutoMapper | 1178 | 597 | 652 |
| Newtonsoft.Json | 5465 | 3501 | 3978 |

### graphify `calls` edges the compiler does not have (both ends in the library source)

| verdict | Dapper | AutoMapper | Newtonsoft.Json | total | by compiler KIND of the call at that line |
|---|---:|---:|---:|---:|---|
| wrong target: compiler binds to a BCL/package method, graphify to a same-named own method | 0 | 56 | 16 | 72 | other 51, inherited 10, typed 8, generic 3 |
| wrong target: compiler binds to a different own method | 0 | 12 | 23 | 35 | typed 17, inherited 12, same 6 |
| right target, wrong caller node (class node for ctor bodies, merged overload/explicit impl, #if-orphaned method) | 20 | 24 | 104 | 148 | static 67, same 42, typed 16, inherited 9, ctor 8, generic 4, interface 1, other 1 |
| call sits in an #if branch the net8.0 build does not compile | 0 | 4 | 29 | 33 | ? 33 |
| no call with that name on that line | 0 | 0 | 0 | 0 |  |
| **all extra `calls` edges** | 20 | 96 | 172 | 288 | |
| in-scope graphify `calls` edges | 574 | 685 | 4004 | 5263 | |
