#!/usr/bin/env bash
# Cold build time + graph.json size per Lite repo commit, for each graphify SRC given.
# usage: time_cold.sh OUT.tsv LABEL=SRC [LABEL=SRC ...]   (no cache: graphify-out removed first)
here=$(cd "$(dirname "$0")" && pwd); out=$1; shift
echo -e "repo\tversion\tbuild_s\tgraph_bytes\tnodes_with_body_terms" > "$out"
for repo in django pytest sphinx astropy requests pylint xarray seaborn flask; do
  c=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]['commit'])" "$here/questions/commits.json" "$repo")
  cd "$S_REPOS/$repo"; rm -f .git/index.lock; git checkout -q -f "$c" </dev/null
  for pair in "$@"; do lab=${pair%%=*}; src=${pair#*=}
    rm -rf graphify-out
    s=$(date +%s.%N); PYTHONPATH="$src" uv run -q --frozen --project /home/user/graphify python -m graphify update . </dev/null >/dev/null 2>&1; e=$(date +%s.%N)
    nb=$(python3 -c "import json; print(sum(1 for n in json.load(open('graphify-out/graph.json'))['nodes'] if n.get('body_terms')))")
    echo -e "$repo\t$lab\t$(echo "$e - $s" | bc | xargs printf %.1f)\t$(stat -c %s graphify-out/graph.json)\t$nb" >> "$out"
  done
done
