#!/usr/bin/env bash
# Full measurement pipeline (what produced results/). Run from anywhere; graphify checkout = ../.. (upstream/v8).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; GFY="$(cd "$HERE/../.." && pwd)"
CS="${CS_ROOT:-/home/user/cs}"; export CS_ROOT="$CS"
mkdir -p "$CS"
# 1. projects (shallow)
for r in JamesNK/Newtonsoft.Json DapperLib/Dapper AutoMapper/AutoMapper; do
  [ -d "$CS/${r#*/}" ] || git clone -q --depth 1 "https://github.com/$r.git" "$CS/${r#*/}"
done
# 2. answer keys (dotnet build net8.0 -> exact csc args -> Roslyn)
"$HERE/run_key.sh"
# 3. graphify on each full repo
for p in Dapper AutoMapper Newtonsoft.Json; do
  (cd "$CS/$p" && uv run --frozen --project "$GFY" graphify update . > "$CS/_gfy_$p.log" 2>&1)
done
# 4. tree-sitter parse errors in the library sources (the parser graphify uses)
(cd "$GFY" && for d in Newtonsoft.Json/Src/Newtonsoft.Json AutoMapper/src/AutoMapper Dapper/Dapper; do
  uv run --frozen python "$HERE/ts_errors.py" "$CS/$d" 2>/dev/null | python3 -I -c "
import sys,json
pre='$d'.split('/',1)[1]
for l in sys.stdin:
    r=json.loads(l); r['file']=pre+'/'+r['file']; print(json.dumps(r))"; done) > "$HERE/results/tree_sitter_errors.jsonl"
# 5. A/B for the preprocessor: library-only copy, raw vs #if-blanked (line numbers preserved)
export PATH=/root/.dotnet:$PATH DOTNET_ROOT=/root/.dotnet
K="$HERE/tools/RoslynCallKey/bin/Release/net8.0/RoslynCallKey.dll"
for spec in Dapper:Dapper AutoMapper:src/AutoMapper Newtonsoft.Json:Src/Newtonsoft.Json; do
  n=${spec%%:*}; d=${spec#*:}
  rm -rf "$CS/lib/$n" "$CS/pp/$n"; mkdir -p "$CS/lib/$n" "$CS/pp/$n"
  (cd "$CS/$n" && find "$d" -name '*.cs' -not -path '*/obj/*' -not -path '*/bin/*' | while read -r f; do
     mkdir -p "$CS/lib/$n/$(dirname "$f")"; cp "$f" "$CS/lib/$n/$f"; done)
  dotnet "$K" "$CS/_rsp/$n.net8.0.rsp" "$CS/$n/$d" "$CS/$n" /dev/null --write-preprocessed "$CS/pp/$n"
  for v in lib pp; do (cd "$CS/$v/$n" && uv run --frozen --project "$GFY" graphify update . > "$CS/_gfy_${v}_$n.log" 2>&1); done
done
# 6. compare + summaries
for p in Dapper AutoMapper Newtonsoft.Json; do
  python3 -I "$HERE/compare.py" "$p" "$CS/$p" "$CS/_key/$p.jsonl" --out "$HERE/results/$p" --pp-root "$CS/pp/$p"
  for v in lib pp; do python3 -I "$HERE/compare.py" "$p" "$CS/$v/$p" "$CS/_key/$p.jsonl" --out "$HERE/results/ab_$v/$p" >/dev/null; done
done
python3 -I "$HERE/summarize.py" "$HERE/results" Dapper AutoMapper Newtonsoft.Json > "$HERE/results/summary.md"
python3 -I "$HERE/analyze.py" "$HERE/results" "$HERE/results/tree_sitter_errors.jsonl" Dapper AutoMapper Newtonsoft.Json > "$HERE/results/causes.txt"
"$HERE/repros/run_repros.sh" > "$HERE/repros/results.txt" 2>&1
