#!/usr/bin/env bash
# usage: prep_pr.sh N WT_ROOT   -> worktree WT_ROOT/pr-N = PR head + benchmark commits (PR #4342)
# A conflict only in help text / docs (__main__.py, docs/) is resolved by keeping
# the PR's side. Prints "clean", "help-conflict-resolved" or "conflict" (cherry-pick
# aborted; bench_driver.py then imports this PR's serve.py instead).
set -u
n=$1; root=$2
git fetch -q upstream pull/$n/head:pr-$n 2>/dev/null || git branch -f pr-$n refs/prs/$n
wt=$root/pr-$n
[ -d "$wt" ] || git worktree add -q --detach "$wt" pr-$n
cd "$wt"
git reset -q --hard pr-$n
status=clean
for c in 5a8e560a 0b1f76a7; do
  if ! git cherry-pick $c >/dev/null 2>&1; then
    bad=$(git diff --name-only --diff-filter=U | grep -v -E '^(graphify/__main__.py|docs/)')
    if [ -n "$bad" ]; then git cherry-pick --abort >/dev/null 2>&1; git reset -q --hard pr-$n; echo conflict; exit 0; fi
    for f in $(git diff --name-only --diff-filter=U); do git checkout --ours -- "$f"; git add "$f"; done
    GIT_EDITOR=true git cherry-pick --continue >/dev/null 2>&1 || { git cherry-pick --abort; git reset -q --hard pr-$n; echo conflict; exit 0; }
    status=help-conflict-resolved
  fi
done
echo $status
