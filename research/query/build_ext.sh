#!/usr/bin/env bash
# usage: build_ext.sh REPOS_DIR OUT_DIR [REPO ...]   (REPO filter lets several repos build in parallel)
# One graph per distinct base commit of questions_ext/<repo>.jsonl, built with
# upstream/v8 graphify (`graphify update .`, code only). Writes OUT_DIR/<repo>@<sha12>.json
# and appends "repo commit seconds bytes" to OUT_DIR/builds.tsv. Leaves each repo
# checked out back at its original commit with its original graphify-out/graph.json.
set -u
here=$(cd "$(dirname "$0")" && pwd); repos=$1; out=$2; shift 2; mkdir -p "$out"
for q in "$here"/questions_ext/*.jsonl; do
  repo=$(basename "$q" .jsonl)
  [ $# -gt 0 ] && [[ " $* " != *" $repo "* ]] && continue
  cd "$repos/$repo" || continue
  rm -f .git/index.lock
  orig=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]['commit'])" "$here/questions/commits.json" "$repo")
  cp "$out/../graphs/$repo.json" /tmp/orig-$repo.json
  for c in $(python3 -c "import json,sys; print('\n'.join(dict.fromkeys(json.loads(l)['commit'] for l in open(sys.argv[1]))))" "$q"); do
    f="$out/$repo@${c:0:12}.json"; [ -f "$f" ] && continue
    git checkout -q -f "$c" </dev/null || { echo "CHECKOUT FAILED $repo $c" >&2; continue; }
    s=$(date +%s.%N)
    uv run -q --frozen --project /home/user/graphify graphify update . </dev/null >/dev/null 2>&1 || echo "BUILD FAILED $repo $c" >&2
    e=$(date +%s.%N)
    cp graphify-out/graph.json "$f" && printf "%s\t%s\t%.1f\t%s\n" "$repo" "$c" "$(echo "$e - $s" | bc)" "$(stat -c %s "$f")" >> "$out/builds.tsv"
  done
  git checkout -q -f "$orig" </dev/null; cp /tmp/orig-$repo.json graphify-out/graph.json
done
echo ALLDONE
