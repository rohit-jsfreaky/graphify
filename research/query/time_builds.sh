#!/usr/bin/env bash
# Part B: wall time of a plain `graphify update .` (upstream/v8, cold: no graphify-out
# cache) at each Lite repo's commit. usage: time_builds.sh REPOS_DIR OUT.tsv
here=$(cd "$(dirname "$0")" && pwd); repos=$1; out=$2
echo -e "repo\tbuild_s\tgraph_bytes" > "$out"
for repo in django pytest sphinx astropy requests pylint xarray seaborn flask; do
  c=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]['commit'])" "$here/questions/commits.json" "$repo")
  cd "$repos/$repo"; rm -f .git/index.lock; git checkout -q -f "$c" </dev/null
  mv graphify-out /tmp/go-$repo
  s=$(date +%s.%N); uv run -q --frozen --project /home/user/graphify graphify update . </dev/null >/dev/null 2>&1; e=$(date +%s.%N)
  echo -e "$repo\t$(echo "$e - $s" | bc | xargs printf %.1f)\t$(stat -c %s graphify-out/graph.json)" >> "$out"
  rm -rf graphify-out; mv /tmp/go-$repo graphify-out
done
