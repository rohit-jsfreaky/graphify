# Results: upstream/v8 (0.9.103, 16218bf) vs claude/csharp-ctor vs claude/csharp-members

Found = compare.py's lenient match (found + found_other_overload). Member-key rows come from `members/compare_members.py`. "wrong calls edges" is compare.py's count of `calls` edges with both ends in library source that are not a key pair; initializer edges are not in the 7349 key, so they appear there even when correct (see below).

#### Dapper

| kind | links | v8 | ctor | members |
|---|---:|---:|---:|---:|
| same | 262 | 233 | 241 | 239 |
| inherited | 2 | 0 | 0 | 0 |
| static | 33 | 22 | 22 | 23 |
| typed | 44 | 30 | 30 | 30 |
| extension | 24 | 0 | 0 | 0 |
| interface | 16 | 8 | 9 | 8 |
| generic | 185 | 177 | 177 | 179 |
| ctor | 116 | 83 | 86 | 83 |
| other | 24 | 24 | 24 | 24 |
| **total (7349 key)** | **706** | **577** | **589** | **586** |
| _of which caller is ctor_ | 9 | 0 | 9 | 0 |
| _of which caller is accessor_get_ | 5 | 0 | 0 | 5 |
| _of which caller is accessor_set_ | 4 | 0 | 0 | 4 |
| _of which caller is conversion_ | 1 | 0 | 0 | 0 |
| member key: ctor_init | 7 | 0 | 3 | 0 |
| member key: property_get | 208 | 0 | 0 | 0 |
| member key: property_set | 78 | 0 | 0 | 0 |
| member key: indexer_get | 1 | 0 | 0 | 0 |
| wrong `calls` edges | | 19 | 22 | 22 |

#### AutoMapper

| kind | links | v8 | ctor | members |
|---|---:|---:|---:|---:|
| same | 314 | 289 | 292 | 298 |
| inherited | 30 | 23 | 24 | 23 |
| static | 36 | 31 | 31 | 34 |
| typed | 185 | 116 | 127 | 118 |
| extension | 269 | 1 | 1 | 1 |
| interface | 81 | 52 | 53 | 52 |
| generic | 19 | 11 | 11 | 11 |
| ctor | 196 | 88 | 92 | 88 |
| other | 48 | 41 | 42 | 41 |
| **total (7349 key)** | **1178** | **652** | **673** | **666** |
| _of which caller is ctor_ | 34 | 0 | 13 | 0 |
| _of which caller is accessor_get_ | 45 | 0 | 0 | 14 |
| member key: ctor_init | 31 | 0 | 24 | 0 |
| member key: property_get | 1005 | 0 | 0 | 0 |
| member key: property_set | 154 | 0 | 0 | 0 |
| member key: indexer_get | 3 | 0 | 0 | 0 |
| wrong `calls` edges | | 96 | 109 | 96 |

#### Newtonsoft.Json

| kind | links | v8 | ctor | members |
|---|---:|---:|---:|---:|
| same | 2243 | 2064 | 2075 | 2200 |
| inherited | 390 | 353 | 357 | 354 |
| static | 879 | 777 | 844 | 803 |
| typed | 757 | 692 | 693 | 692 |
| extension | 578 | 0 | 0 | 0 |
| interface | 91 | 44 | 44 | 44 |
| generic | 117 | 76 | 77 | 79 |
| ctor | 398 | 303 | 319 | 354 |
| other | 12 | 6 | 7 | 6 |
| **total (7349 key)** | **5465** | **4315** | **4416** | **4532** |
| _of which caller is ctor_ | 108 | 0 | 97 | 0 |
| _of which caller is accessor_get_ | 63 | 0 | 0 | 49 |
| _of which caller is accessor_set_ | 27 | 0 | 0 | 20 |
| _of which caller is conversion_ | 185 | 0 | 0 | 148 |
| member key: ctor_init | 92 | 0 | 53 | 0 |
| member key: property_get | 1612 | 0 | 0 | 0 |
| member key: property_set | 431 | 0 | 0 | 0 |
| member key: indexer_get | 19 | 0 | 0 | 0 |
| member key: indexer_set | 4 | 0 | 0 | 0 |
| member key: conversion | 60 | 0 | 0 | 0 |
| wrong `calls` edges | | 149 | 135 | 152 |

#### All three

| kind | links | v8 | ctor | members |
|---|---:|---:|---:|---:|
| same | 2819 | 2586 | 2608 | 2737 |
| inherited | 422 | 376 | 381 | 377 |
| static | 948 | 830 | 897 | 860 |
| typed | 986 | 838 | 850 | 840 |
| extension | 871 | 1 | 1 | 1 |
| interface | 188 | 104 | 106 | 104 |
| generic | 321 | 264 | 265 | 269 |
| ctor | 710 | 474 | 497 | 525 |
| other | 84 | 71 | 73 | 71 |
| **total (7349 key)** | **7349** | **5544** | **5678** | **5784** |
| _of which caller is ctor_ | 151 | 0 | 119 | 0 |
| _of which caller is accessor_get_ | 113 | 0 | 0 | 68 |
| _of which caller is accessor_set_ | 31 | 0 | 0 | 24 |
| _of which caller is conversion_ | 186 | 0 | 0 | 148 |
| member key: ctor_init | 130 | 0 | 80 | 0 |
| member key: property_get | 2825 | 0 | 0 | 0 |
| member key: property_set | 663 | 0 | 0 | 0 |
| member key: indexer_get | 23 | 0 | 0 | 0 |
| member key: indexer_set | 4 | 0 | 0 | 0 |
| member key: conversion | 60 | 0 | 0 | 0 |
| wrong `calls` edges | | 264 | 266 | 270 |

## Extra `calls` edges, ctor vs v8 (`members/wrongdiff.py v8 ctor`)

```
  [AutoMapper] same wrong edge, caller moved from the type to its constructor: MapperConfiguration.MapperConfiguration() L67 -> MemberConfiguration.Seal() L41 | wrong_own_target | 'Seal()' | compiler: Seal()
  [AutoMapper] NEW: QueryExpressions.QueryExpressions() L379 -> ExpressionBuilder.Lambda() L199 | external_target | 'Lambda(projection, parameter)' | compiler: System.Linq.Expressions.Expression.Lambda(System.Linq.Expressions.Expression, params System.Linq.Expressions.ParameterExpression[]?)
  [AutoMapper] NEW: SubQueryPath.SubQueryPath() L295 -> ExpressionBuilder.Default() L39 | external_target | 'Default(letExpression.Body.Type)' | compiler: System.Linq.Expressions.Expression.Default(System.Type)
  [Newtonsoft.Json] ctor edge mirroring an existing extra edge to the type: DefaultContractResolver.CreateMemberValueProvider() L1436 -> ExpressionValueProvider.ExpressionValueProvider() L55 | no_call_with_that_name_at_line | None | compiler: None
  [Newtonsoft.Json] ctor edge mirroring an existing extra edge to the type: DictionaryWrapper.GetEnumerator() L421 -> DictionaryEnumerator.DictionaryEnumerator() L510 | right_target_other_caller | 'new DictionaryEnumerator<TKey, TValue>(_readOnlyDictionary.GetEnumerator())' | compiler: Newtonsoft.Json.Utilities.DictionaryWrapper<TKey, TValue>.DictionaryEnumerator<TEnumeratorKey, TEnumeratorValue>.DictionaryEnumerator(System.Collections.Generic.IEnumerator<System.Collections.Generic.KeyValuePair<TEnumeratorKey, TEnumeratorValue>>)
  [Newtonsoft.Json] NEW: JArray.JArray() L95 -> JArray.Add() L372 | wrong_own_target | 'Add(content)' | compiler: Newtonsoft.Json.Linq.JContainer.Add(object?)
  [Newtonsoft.Json] NEW: JObject.JObject() L118 -> JObject.Add() L646 | wrong_own_target | 'Add(content)' | compiler: Newtonsoft.Json.Linq.JContainer.Add(object?)
  [Newtonsoft.Json] same wrong edge, caller moved from the type to its constructor: JsonArrayContract.JsonArrayContract() L124 -> ReflectionUtils.IsNullableType() L281 | no_call_with_that_name_at_line | None | compiler: None
  [Newtonsoft.Json] same wrong edge, caller moved from the type to its constructor: JsonDictionaryContract.JsonDictionaryContract() L116 -> ReflectionUtils.IsNullableType() L281 | no_call_with_that_name_at_line | None | compiler: None
  [Newtonsoft.Json] same wrong edge, caller moved from the type to its constructor: ReflectionUtils.ReflectionUtils() L88 -> CollectionUtils.ArrayEmpty() L375 | no_call_with_that_name_at_line | None | compiler: None
77 removed: gone
73 correct: confirmed by Roslyn member key (ctor initializer)
4 same wrong edge, caller moved from the type to its constructor
4 NEW
4 removed: moved to the constructor node
2 ctor edge mirroring an existing extra edge to the type
```

## Extra `calls` edges, members vs v8 (`members/wrongdiff.py v8 members`)

```
  [Dapper] NEW: LegacyParameter L31 -> CompiledRegex.LegacyParameterGen() L19 | external_target | 'LegacyParameterGen()' | compiler: Dapper.CompiledRegex.LegacyParameterGen()
  [Dapper] NEW: LiteralTokens L32 -> CompiledRegex.LiteralTokensGen() L22 | external_target | 'LiteralTokensGen()' | compiler: Dapper.CompiledRegex.LiteralTokensGen()
  [Dapper] NEW: PseudoPositional L33 -> CompiledRegex.PseudoPositionalGen() L25 | external_target | 'PseudoPositionalGen()' | compiler: Dapper.CompiledRegex.PseudoPositionalGen()
  [Dapper] NEW: WhitespaceOrReserved L34 -> CompiledRegex.WhitespaceOrReservedGen() L28 | external_target | 'WhitespaceOrReservedGen()' | compiler: Dapper.CompiledRegex.WhitespaceOrReservedGen()
  [Newtonsoft.Json] NEW: First L380 -> JToken.GetType() L545 | external_target | 'GetType()' | compiler: object.GetType()
  [Newtonsoft.Json] NEW: Last L386 -> JToken.GetType() L545 | external_target | 'GetType()' | compiler: object.GetType()
  [Newtonsoft.Json] NEW: this[] L356 -> JToken.GetType() L545 | external_target | 'GetType()' | compiler: object.GetType()
7 NEW
1 removed: gone
```

## Node ids

```
Dapper: v8 nodes 3649, branch 3809, lost 0, new 160 {'constructor': 160}, same id but label/file/line changed 0
AutoMapper: v8 nodes 14008, branch 14615, lost 0, new 607 {'constructor': 607}, same id but label/file/line changed 0
Newtonsoft.Json: v8 nodes 13655, branch 14311, lost 0, new 656 {'constructor': 656}, same id but label/file/line changed 0
Dapper: v8 nodes 3649, branch 3667, lost 0, new 18 {'indexer': 17, 'operator': 1}, same id but label/file/line changed 0
AutoMapper: v8 nodes 14008, branch 14022, lost 0, new 14 {'operator': 9, 'indexer': 5}, same id but label/file/line changed 0
Newtonsoft.Json: v8 nodes 13655, branch 13774, lost 0, new 119 {'operator': 87, 'indexer': 32}, same id but label/file/line changed 0
```
