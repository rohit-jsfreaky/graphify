"""Count the causes behind query_graph's misses (rank None or >= 5) on upstream/v8.
Non-exclusive flags, from results/gap_v8.json + results/bm25_files:
  test_doc_seeds    half or more of the start nodes are test/doc nodes
  names_only        the term scorer (names/paths only) does not put the gold file in its top 5
                    files, but BM25 over the files' full text does -> the words are in the body
  spread_or_budget  the scorer DID have the gold file in its top 5 files, or BFS reached a
                    gold-file node, yet the rendered answer shows it 6th+ or not at all ->
                    traversal/order/budget lost it (output is ordered by hop then degree)
  vocab_gap         neither the term scorer nor full-text BM25 has it in the top 5
"""
import json
from collections import Counter
from pathlib import Path
here = Path(__file__).parent
rows = json.load(open(here / "results/gap_v8.json"))
bm = {}
for f in (here / "results/bm25_files").glob("*.json"):
    if f.name == "summary.json": continue
    for p in json.load(open(f))["per_question"]:
        bm[p["question"], tuple(p["files"])] = p["rank"]
c = Counter(); ex = {}
miss = [r for r in rows if r["cause"] != "ok"]
for r in miss:
    n = sum(r["seed_kinds"].values()) or 1
    b = bm.get((r["question"], tuple(r["files"])))
    fr = r["scorer_file_rank"]
    flags = []
    if (r["seed_kinds"].get("test", 0) + r["seed_kinds"].get("doc", 0)) * 2 >= n: flags.append("test_doc_seeds")
    if (fr is None or fr >= 5) and b is not None and b < 5: flags.append("names_only")
    if (fr is not None and fr < 5) or r["cause"] in ("late", "budget_cut"): flags.append("spread_or_budget")
    if (fr is None or fr >= 5) and (b is None or b >= 5): flags.append("vocab_gap")
    r["flags"] = flags
    for fl in flags:
        c[fl] += 1; ex.setdefault(fl, []).append(r)
print(f"misses: {len(miss)} of {len(rows)}")
for k, v in c.most_common():
    print(f"  {k}: {v}")
print("  scorer had gold in top-5 files but answer missed it:", sum(1 for r in miss if r['scorer_file_rank'] is not None and r['scorer_file_rank'] < 5))
print("  test/doc demoted scorer would have gold in top-5 files:", sum(1 for r in miss if r['scorer_file_rank_no_tests'] is not None and r['scorer_file_rank_no_tests'] < 5))
json.dump(miss, open(here / "results/gap_v8_misses.json", "w"), indent=1)

# Exclusive primary cause, first that applies:
def primary(r):
    b = bm.get((r["question"], tuple(r["files"])))
    fr, frn = r["scorer_file_rank"], r["scorer_file_rank_no_tests"]
    if fr is not None and fr < 5: return "A_scorer_had_it_render_lost_it"
    if frn is not None and frn < 5: return "B_tests_docs_crowd_it_out"
    if b is not None and b < 5: return "C_names_only_words_are_in_body"
    if r["cause"] in ("late", "budget_cut") and r["rank"] is not None: return "D_shown_late_by_bfs_luck"
    return "E_vocab_gap_nobody_finds_it"
pc = Counter()
for r in miss:
    r["primary"] = primary(r); pc[r["primary"]] += 1
print("primary cause (exclusive):")
for k in sorted(pc): print(f"  {k}: {pc[k]}")
json.dump(miss, open(here / "results/gap_v8_misses.json", "w"), indent=1)
