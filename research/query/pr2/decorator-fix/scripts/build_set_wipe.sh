#!/usr/bin/env bash
# usage: build_set.sh SRC OUT_DIR REPO [REPO...]
# Build one graph per (repo, commit) for the Lite commit (questions/commits.json) and every
# Verified base commit (questions_ext/), with the graphify package in SRC (`python -m graphify
# update .`). OUT_DIR/<repo>.json = Lite commit, OUT_DIR/<repo>@<sha12>.json = Verified commits.
# Appends "repo commit seconds bytes" to OUT_DIR/builds.tsv. Leaves each repo at its Lite commit.
set -u
here=$(cd "$(dirname "$0")" && pwd); src=$1; out=$2; shift 2; mkdir -p "$out"
for repo in "$@"; do
  cd "$S_REPOS/$repo" || continue
  lite=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]['commit'])" "$here/questions/commits.json" "$repo")
  ext=""; [ -z "${LITE_ONLY:-}" ] && [ -f "$here/questions_ext/$repo.jsonl" ] && ext=$(python3 -c "import json,sys; print('\n'.join(dict.fromkeys(json.loads(l)['commit'] for l in open(sys.argv[1]))))" "$here/questions_ext/$repo.jsonl")
  for c in $lite $ext; do
    if [ "$c" = "$lite" ]; then f="$out/$repo.json"; else f="$out/$repo@${c:0:12}.json"; fi
    [ -f "$f" ] && continue
    rm -f .git/index.lock; git checkout -q -f "$c" </dev/null || { echo "CHECKOUT FAILED $repo $c" >&2; continue; }
    # fresh build: keep only the AST cache (namespaced by version + schema), so
    # nothing from an earlier graph.json/manifest is merged in
    rm -rf graphify-out  # fully fresh: the AST cache schema did not change between the compared commits
    s=$(date +%s.%N)
    PYTHONPATH="$src" uv run -q --frozen --project /home/user/graphify python -m graphify update . </dev/null >/dev/null 2>&1 || echo "BUILD FAILED $repo $c" >&2
    e=$(date +%s.%N)
    cp graphify-out/graph.json "$f" && printf "%s\t%s\t%.1f\t%s\n" "$repo" "$c" "$(echo "$e - $s" | bc)" "$(stat -c %s "$f")" >> "$out/builds.tsv"
  done
  git checkout -q -f "$lite" </dev/null
done
echo ALLDONE
