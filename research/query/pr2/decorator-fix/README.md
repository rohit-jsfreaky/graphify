# Decorator fix (642cff05): before vs after

The bot review on PR #5052 found that decorator lines (`@app.route("/x")`) were
counted in the parent's `body_terms` (the file or class) instead of the decorated
def. Commit `642cff05` (fork branch `feat/query-body-words`) fixes that. It sits
on upstream v8 0.9.103 + `e6940a30` (squash of PR 2's three commits).

## How the numbers were made

1. **Fix graphs.** All 125 graphs for the 293 questions were rebuilt with `642cff05`
   (`scripts/build_set_wipe.sh`).
   - One graph per Lite repo commit and per Verified base commit.
   - `graphify-out/` was deleted before every build, cache included, because the AST
     cache schema is the same before and after the fix.
   - Build log: `builds_fix_642cff05.tsv`. All 125 built, none failed.
2. **Fix benchmark.** `graphify benchmark <graph> --questions <file> --json`
   (PR #4342 cherry-picked into a scratch worktree) was run on all 293 questions
   with `scripts/bench_cli.py`. Output: `final4-fix.jsonl`.
3. **Comparison.** `comparison.md` (`scripts/cmp_fix.py`) compares `final4-fix.jsonl`
   with the frozen PR 2 results, `../results/final2-pr2.jsonl` (`24d81d2d` on v8
   0.9.102). It has top-1/3/5/anywhere per split and every question whose rank
   changed.
4. **Attribution.** The frozen results are on an older upstream base, so a
   difference could come from the fix or from the 37 upstream commits in between.
   To separate them, the 7 graphs behind the changed questions were also built with
   `e6940a30` (same new base, no fix; `scripts/build_one.sh`) and benchmarked
   (`final4-squash-subset.jsonl`, 141 questions answered by those 7 graphs).
   - On those 7 graphs, the squash and fix graphs have the same node ids, the same
     links and the same node data except `body_terms`.
   - `decorator_attribution.md` shows that the decorator fix alone causes all 8 rank
     changes: frozen vs squash moves no rank on those 141 questions; squash vs fix
     moves exactly these 8.
   - The upstream changes only changed answer sizes (tokens).
