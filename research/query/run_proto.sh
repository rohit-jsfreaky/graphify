#!/usr/bin/env bash
# usage: run_proto.sh VARIANT GRAPHS_DIR REPOS_DIR   (prototype on top of upstream/v8 = /home/user/graphify)
here=$(cd "$(dirname "$0")" && pwd)
(cd /tmp && PYTHONPATH=/home/user/graphify uv run -q --frozen --project /home/user/graphify python "$here/proto.py" "$1" "$2" "$3" "$here/results/proto-$1" </dev/null) \
  && uv run -q --frozen --project /home/user/graphify python "$here/aggregate.py" "$here/results/proto-$1"
