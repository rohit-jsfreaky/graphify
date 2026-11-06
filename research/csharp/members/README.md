# C# constructors, properties and operators: extended Roslyn key and branch measurements

Measure-only. This adds to `research/csharp` (branch `claude/csharp-measure`) without changing what it
measured: the 7349-link call key is rebuilt byte-for-byte identical (checked with `sort | cmp` on all three
projects). Projects and commits are the same: Dapper `eb47546`, AutoMapper `df65f2e`, Newtonsoft.Json `52fa3ae`.

## What is new

* `tools/RoslynCallKey/Program.cs` takes an optional `--members <out.jsonl>` (last two arguments). It writes a
  SECOND key with the links the call key does not cover, using the same callers (`FindCaller`) and the same
  record shape:
  * `ctor_init`: `: base(...)` / `: this(...)` constructor initializers;
  * `property_get` / `property_set` / `indexer_get` / `indexer_set`: `IPropertyReferenceOperation`, set for an
    assignment target, get + set for `+=`, `++` and `??=`, flagged `auto_property` when every accessor has no
    body;
  * `operator`: a user-defined unary/binary/compound/increment operator (`OperatorMethod`);
  * `conversion`: a user-defined conversion (`IConversionOperation.OperatorMethod`).
  Implicitly declared (synthesized) members are skipped, as are uses inside `nameof`.
* `results/keys_members/<project>.members.jsonl.gz`: that key.
* `members/compare_members.py`: scores a graphify run against it with `compare.py`'s own matching
  (`load_graph`, `match_decl`), unique (caller decl, target decl, kind) pairs.
* `members/measure.sh <variant> <graphify checkout>`: copies each project fresh (no `.git`, no `graphify-out`),
  runs `python -m graphify update .` from that checkout, then `compare.py` and `summarize.py`.
* `members/table.py`, `members/wrongdiff.py` (classifies `calls` edges that are extra in one variant and not
  the other), `members/idcheck.py` (every baseline node id must survive in the branch).

Paths in the scripts are the ones used in the session (`/home/user/cs`, `/home/user/runs`,
`/home/user/mres`); adjust them for another machine.

## Commands

```bash
dotnet RoslynCallKey.dll _rsp/<p>.net8.0.rsp <projectDir> <repoRoot> _key2/<p>.jsonl --members _key2/<p>.members.jsonl
members/measure.sh v8 <checkout of upstream/v8>
members/measure.sh ctor <checkout of claude/csharp-ctor>
members/measure.sh members <checkout of claude/csharp-members>
python3 members/compare_members.py <p> /home/user/runs/<variant>/<p> /home/user/cs/_key2/<p>.members.jsonl /home/user/mres/<variant>/<p>/members.json
python3 members/table.py v8 ctor members
python3 members/wrongdiff.py v8 ctor
python3 members/idcheck.py v8 ctor
```

## Results

See `results.md`.
