#!/usr/bin/env bash
# For each repro: Roslyn answer key (compiler edges) vs graphify edges.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
export PATH=/root/.dotnet:$PATH DOTNET_ROOT=/root/.dotnet DOTNET_NOLOGO=1
K="$HERE/../tools/RoslynCallKey/bin/Release/net8.0/RoslynCallKey.dll"
REF=$(ls -d /root/.dotnet/packs/Microsoft.NETCore.App.Ref/8.*/ref/net8.0 | tail -1)
for d in 1-extension 2-non-method-callers 3-preprocessor; do
  rsp="$HERE/$d/.csc.rsp"
  { echo "/target:library"; echo "/out:repro.dll"; echo "/nullable:enable"; echo "/langversion:latest"; echo "/nostdlib+"
    for r in "$REF"/*.dll; do echo "/reference:$r"; done
    (cd "$HERE/$d" && ls *.cs); } > "$rsp"
  echo "=== $d"
  echo "--- compiler (Roslyn) call edges:"
  dotnet "$K" "$rsp" "$HERE/$d" "$HERE/$d" "$HERE/$d/.key.jsonl" 2>&1 | grep -E 'compile\]|compile-error' || true
  python3 -I -c "
import json,sys
for l in open('$HERE/$d/.key.jsonl'):
    r=json.loads(l); t=r['target'] or {'type':r['target_type_name'],'name':'(implicit ctor)','file':'','line':0}
    print(f\"  {r['caller']['type']}.{r['caller']['name']} ({r['caller']['decl_kind']}, {r['caller']['file']}:L{r['caller']['line']})  ->  {t['type']}.{t['name']} ({t['file']}:L{t['line']})   site L{r['call_line']} kind={r['kind']}\")"
  rm -f "$rsp" "$HERE/$d/.key.jsonl" "$HERE/$d/.key.sites.jsonl"
  echo "--- graphify (upstream/v8) edges:"
  (cd "$HERE/$d" && rm -rf graphify-out && uv run --frozen --project "$HERE/../../.." graphify update . >/dev/null 2>&1)
  python3 -I "$HERE/show_edges.py" "$HERE/$d"
done
