#!/usr/bin/env bash
# usage: run_eval.sh LABEL SYSTEM [PARAMS_JSON] [GRAPHIFY_SRC] [tune]   (5th arg "tune" = Django only)   (GRAPHIFY_SRC defaults to upstream/v8 checkout)
S=/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad
here=$(cd "$(dirname "$0")" && pwd)
src=${4:-/home/user/graphify}
cd /tmp && PYTHONPATH="$src" uv run -q --frozen --project /home/user/graphify python "$here/evalset.py" "$1" "$2" \
  "$S/graphs" "$S/graphs_ext" "$S/repos" "${3:-{\}}" ${5:+"$5"} </dev/null
