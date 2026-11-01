# C# call graph: graphify (upstream/v8) vs the Roslyn compiler

Measure-only. No graphify source was changed. Graphify under test: `upstream/v8` @ `32e5efe`.

## What was measured

* **Projects** (shallow clones, 2026-11-01): Dapper `eb47546`, AutoMapper `df65f2e`, Newtonsoft.Json `52fa3ae`.
  The answer key covers each main library project (`Dapper/Dapper`, `src/AutoMapper`, `Src/Newtonsoft.Json`).
  Graphify was run on the whole repo.
* **Answer key** (`tools/RoslynCallKey`). Each library was built with `dotnet build -f net8.0`. An injected MSBuild target
  (`tools/dump-csc-args.targets`) saved the exact `csc` arguments, so the tool rebuilds the same `CSharpCompilation`
  (same sources, defines, references and LangVersion) with Roslyn 5.0.0 and runs the build's source generators.
  All 3 compile with **0 errors**. Every `InvocationExpression` / `ObjectCreationExpression` / target-typed `new()`
  inside a method, constructor, destructor, operator, accessor or local function is resolved with
  `SemanticModel.GetSymbolInfo`. Only targets declared in the library's own non-`obj/` sources are kept. Skipped:
  calls outside members (such as field initializers), `nameof`/`dynamic`, delegate invokes, and calls to local
  functions.
* **KIND** (first rule that matches wins): `ctor` (`new`) > `generic` (explicit type arguments) > `extension`
  (reduced-form extension call) > `interface` (target declared on an interface) > `static` (`Type.M()`) >
  `same` / `inherited` (bare, `this.` or `base.`; target declared in the caller's type or in a base type) >
  `typed` (receiver is a local, parameter, field or property) > `other`.
* **Matching** (`compare.py`). A node matches by `(source_file, line)`, where the line can be the declaration
  line, the line after attributes, or the identifier line, and the node's short name must match. A link counts as
  found if graphify has a `calls`/`references`/`uses`/`instantiates` edge from caller to target. For `ctor`, the
  target may be the constructor or the type's node (graphify has no constructor nodes). For a local function, the
  enclosing method's node also counts as the caller. The main numbers use lenient overload matching (any node with
  the same name in the target file), so overload merging (#1533) is not counted against graphify. Strict numbers
  are in `results/summary.md`. Links are unique (caller declaration, target declaration) pairs.

## Results

See `results/summary.md` (tables), `results/causes.txt` (why each miss happened) and `results/ab_preprocessor.md`.

| kind | compiler links | graphify found | recall % |
|---|---:|---:|---:|
| same | 2819 | 2497 | 88.6 |
| inherited | 422 | 302 | 71.6 |
| static | 948 | 807 | 85.1 |
| typed | 986 | 680 | 69.0 |
| extension | 871 | 1 | **0.1** |
| interface | 188 | 104 | 55.3 |
| generic | 321 | 263 | 81.9 |
| ctor | 710 | 478 | 67.3 |
| other | 84 | 71 | 84.5 |
| **total** | **7349** | **5203** | **70.8** |

Per project: Dapper 573/706 (81.2%), AutoMapper 652/1178 (55.3%), Newtonsoft.Json 3978/5465 (72.8%).

## The 3 biggest gaps (all reproduced in `repros/`, see `repros/results.txt`)

1. **Extension-method calls are never resolved.** 870 missed links (41% of all misses), 0.1% recall.
   `x.Ext()` is a member call, so the engine defers it (`_csharp_defer` in `walk_calls`,
   `graphify/extractors/engine.py`). `_resolve_csharp_member_calls` (`graphify/extract.py`) then looks the name up
   only on the receiver's type and its bases (`_method_on_type_or_bases`). When that fails it hits
   `continue  # receiver typed, but the type has no such method — skip`. An untypable receiver, such as the 244
   `"...".FormatWith()` calls in Newtonsoft.Json, is skipped even earlier. Nothing ever checks static methods whose
   first parameter is `this T`.
2. **Calls inside members that aren't `method_declaration` have no correct caller.** 417 missed links. In
   `extract.py`, `_CSHARP_CONFIG.function_types = {"method_declaration"}`. In `_extract_generic`
   (`graphify/extractors/engine.py`), constructor bodies are walked with the class node as the caller (#4246).
   The C# `property_declaration` branch never queues accessor bodies, and operators, conversion operators and
   indexers aren't handled at all. Constructor calls end up on the class node, and calls in getters, setters and
   operators are dropped.
3. **`#if` / `#else` / `#endif` derail tree-sitter.** About 360 missed links plus orphaned nodes. `extract_csharp`
   (`extract.py`) parses the raw text with no preprocessor step. In larger files, tree-sitter-c-sharp's error
   recovery around directives can close the enclosing class early, so every later member becomes a class-less
   node. Those members lose their `Type.` label, field/receiver typing and same-class resolution. 40 library files
   contain a tree-sitter ERROR. A/B test on the same answer key, comparing the raw library with a copy where
   directives and inactive branches are blanked and line numbers are kept: recall goes from 70.8% to **75.7%**
   (+359 links). Newtonsoft.Json goes from 72.8% to 79.1%, `typed` 69.0% to 85.0%, `inherited` 71.6% to 89.1%.

## Wrong links (graphify `calls` edges with both ends in library source that the compiler does not have)

288 of 5263 in-scope `calls` edges. Of those, 107 have a wrong target: 72 bind a BCL call to a same-named own method,
and 35 pick the wrong own method. 148 have the right target but the wrong caller node (constructor body attributed
to the class, merged overload, or `#if`-orphaned method). 33 come from `#if` branches the net8.0 build doesn't
compile. Details are in `results/summary.md` and `results/<project>/wrong_calls.jsonl`.

## Commands run

```bash
git remote add upstream https://github.com/Graphify-Labs/graphify.git && git fetch upstream v8 && git checkout -b claude/csharp-measure upstream/v8
uv sync --all-extras --frozen                      # uv 0.11.32 was preinstalled, so `pip install uv` was not run
bash dotnet-install.sh --channel 8.0 --install-dir /root/.dotnet    # SDK 8.0.427
bash dotnet-install.sh --channel 10.0 --install-dir /root/.dotnet   # SDK 10.0.403: all 3 repos pin a 10.0 SDK in global.json
git clone --depth 1 https://github.com/{JamesNK/Newtonsoft.Json,DapperLib/Dapper,AutoMapper/AutoMapper}.git
research/csharp/run_all.sh     # = run_key.sh + `uv run --frozen --project <graphify> graphify update .` per repo + compare/analyze/summarize + A/B
research/csharp/repros/run_repros.sh
```

Build notes: `NBGV_GitEngine=Disabled` was required because Nerdbank.GitVersioning (Dapper) fails on a shallow
clone. `--no-incremental` is needed so CoreCompile runs and its arguments get dumped. No project failed to produce
an answer key.
