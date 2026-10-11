"""Per question, why query_graph (upstream/v8) misses the gold file.

usage: python gap_analysis.py GRAPHS_DIR REPOS_DIR OUT.json
Primary cause, first that applies:
  ok            gold file in first 5 files shown
  late          gold file shown, but 6th or later
  budget_cut    BFS visited a gold-file node but the 2000-token budget cut it
  seeds_lost    a gold-file node scores > 0 on the term scorer but was not a seed
                and BFS (depth 3) from the chosen seeds never reached it
  names_only    gold-file nodes score 0 (question words not in names/attrs) but the
                words ARE in the gold file's source text (identifiers, docstrings,
                comments) -- a body index would see them
  vocab_gap     even the gold file's source text shares < 2 question terms
Seed facts recorded for every question: how many seeds are tests / docs / rationale.
"""
import json, re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import graphify.serve as s
from bench_driver import _score_answer
from bm25_files import tokens

def is_test(p):
    parts = p.lower().split("/")
    return any(d in ("tests", "test", "testing") for d in parts[:-1]) or parts[-1].startswith("test_") \
        or parts[-1].endswith("_test.py") or parts[-1] == "conftest.py"

def is_doc(p, data):
    return (data.get("file_type") in ("document", "paper")) or p.lower().endswith((".rst", ".md", ".txt"))

def kind(G, nid):
    d = G.nodes[nid]; p = d.get("source_file") or ""
    if is_test(p): return "test"
    if is_doc(p, d): return "doc"
    if d.get("file_type") == "rationale": return "rationale"
    return "code"

def main(graphs, repos, out):
    rows = []
    for q in sorted(Path(__file__).parent.glob("questions/*.jsonl")):
        repo = q.stem
        G = s._load_graph(str(Path(graphs) / f"{repo}.json"))
        TV = s._traversal_view(G)
        for line in q.read_text().splitlines():
            item = json.loads(line); question = item["question"]; gold = set(item["files"])
            text = s._query_graph_text(G, question, mode="bfs", depth=3, token_budget=2000)
            sc = _score_answer(question, item["files"], text)
            terms = s._query_terms(question)
            qs = s._score_query(G, terms, collect_per_term_seeds=True)
            seeds = s._pick_seeds(qs.ranked, G=G, best_seed_by_term=qs.best_seed_by_term, term_order=qs.term_order)
            visited, _ = s._bfs(TV, seeds, 3) if seeds else (set(), [])
            gold_nodes = [n for n, d in G.nodes(data=True) if (d.get("source_file") or "") in gold]
            rank_of = {nid: i for i, (_, nid) in enumerate(qs.ranked)}
            gold_score_ranks = sorted(rank_of[n] for n in gold_nodes if n in rank_of)
            qt = set(tokens(question))
            src_terms = set()
            for f in gold:
                p = Path(repos) / repo / f
                if p.is_file():
                    src_terms |= qt & set(tokens(p.read_text(errors="replace")))
            files_order, files_order_nt = [], []
            for _, nid in qs.ranked:
                f = G.nodes[nid].get("source_file") or ""
                if f and f not in files_order:
                    files_order.append(f)
                    if not is_test(f) and not is_doc(f, G.nodes[nid]):
                        files_order_nt.append(f)
                if len(files_order) > 400: break
            frank = next((i for i, f in enumerate(files_order) if f in gold), None)
            frank_nt = next((i for i, f in enumerate(files_order_nt) if f in gold), None)
            r = sc["rank"]
            if r is not None and r < 5: cause = "ok"
            elif r is not None: cause = "late"
            elif any(n in visited for n in gold_nodes): cause = "budget_cut"
            elif gold_score_ranks: cause = "seeds_lost"
            elif len(src_terms) >= 2: cause = "names_only"
            else: cause = "vocab_gap"
            kinds = Counter(kind(G, n) for n in seeds)
            rows.append({"repo": repo, "id": item.get("id"), "question": question, "files": item["files"], "rank": r,
                         "cause": cause, "seeds": [G.nodes[n].get("label") for n in seeds],
                         "seed_files": [G.nodes[n].get("source_file") for n in seeds],
                         "seed_kinds": dict(kinds), "gold_nodes": len(gold_nodes),
                         "best_gold_score_rank": gold_score_ranks[0] if gold_score_ranks else None,
                         "visited": len(visited), "gold_terms_in_source": sorted(src_terms),
                         "tokens": sc["tokens"], "scorer_file_rank": frank, "scorer_file_rank_no_tests": frank_nt})
        print(repo, file=sys.stderr)
    Path(out).write_text(json.dumps(rows, indent=1))
    c = Counter(r["cause"] for r in rows); print(dict(c))
    allk = Counter(); [allk.update(r["seed_kinds"]) for r in rows]
    print("seed kinds:", dict(allk), "questions with >=1 test/doc seed:",
          sum(1 for r in rows if r["seed_kinds"].get("test") or r["seed_kinds"].get("doc")))
    miss = [r for r in rows if r["cause"] != "ok"]
    allm = Counter(); [allm.update(r["seed_kinds"]) for r in miss]
    print("seed kinds on misses:", dict(allm), "misses with no code seed:", sum(1 for r in miss if not r["seed_kinds"].get("code")))
if __name__ == "__main__":
    main(*sys.argv[1:4])
