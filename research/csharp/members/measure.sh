#!/usr/bin/env bash
# usage: measure.sh <variant> <graphify checkout>
# Copies each library repo fresh (no .git, no graphify-out), runs graphify from <checkout>, compares to the Roslyn key.
set -euo pipefail
V=$1; GFY=$(cd "$2" && pwd); CS=/home/user/cs; H=/home/user/measure/research/csharp; OUT=/home/user/mres/$V
PY=/home/user/graphify/.venv/bin/python
mkdir -p "$OUT"
(cd / && PYTHONPATH="$GFY" $PY -c "import graphify,sys; print('graphify from', graphify.__file__)") | tee "$OUT/which.txt"
grep -q "$GFY/graphify/__init__.py" "$OUT/which.txt"
for p in Dapper AutoMapper Newtonsoft.Json; do
  W=/home/user/runs/$V/$p; rm -rf "$W"; mkdir -p "$W"
  (cd "$CS/$p" && tar --exclude=.git --exclude=graphify-out -cf - .) | tar -xf - -C "$W"
  (cd "$W" && PYTHONPATH="$GFY" $PY -m graphify update . > "$OUT/gfy_$p.log" 2>&1)
  python3 -I "$H/compare.py" "$p" "$W" "$CS/_key/$p.jsonl" --out "$OUT/$p" > "$OUT/compare_$p.txt"
done
python3 -I "$H/summarize.py" "$OUT" Dapper AutoMapper Newtonsoft.Json > "$OUT/summary.md"
echo done "$V"
