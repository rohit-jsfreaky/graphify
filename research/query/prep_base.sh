#!/usr/bin/env bash
# usage: prep_base.sh N WT_ROOT -> prints "base-<sha12>" : a worktree WT_ROOT/pr-base-<sha12> at the
# PR's merge-base with upstream/v8 (the code the PR was written against), with the
# benchmark cherry-picked when it applies (run_pr.sh falls back to bench_driver.py otherwise).
n=$1; root=$2
mb=$(git merge-base upstream/v8 pr-$n); id=base-${mb:0:12}; wt=$root/pr-$id
if [ ! -d "$wt" ]; then
  git worktree add -q --detach "$wt" $mb
  (cd "$wt"; for c in 5a8e560a 0b1f76a7; do
     if ! git cherry-pick $c >/dev/null 2>&1; then
       bad=$(git diff --name-only --diff-filter=U | grep -v -E '^(graphify/__main__.py|docs/)')
       if [ -n "$bad" ]; then git cherry-pick --abort; git reset -q --hard $mb; break; fi
       for f in $(git diff --name-only --diff-filter=U); do git checkout --ours -- "$f"; git add "$f"; done
       GIT_EDITOR=true git cherry-pick --continue >/dev/null 2>&1
     fi; done) >/dev/null 2>&1
fi
echo $id
