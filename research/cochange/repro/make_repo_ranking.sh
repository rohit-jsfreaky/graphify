#!/usr/bin/env bash
# Tiny repo for the ranking PR: aaa.py barely uses core.py (one import),
# zzz.py calls into it everywhere, and helper.py depends on zzz.py.
# Usage: make_repo_ranking.sh <empty-dir>
set -euo pipefail
D=$1; mkdir -p "$D"; cd "$D"
cat > core.py <<'PY'
def load():
    return {}

def save(data):
    return data
PY
cat > aaa.py <<'PY'
import core

VERSION = 1
PY
cat > zzz.py <<'PY'
from core import load, save

def sync():
    return save(load())

def reset():
    save({})
    return load()
PY
cat > helper.py <<'PY'
from zzz import sync

def run():
    return sync()
PY
