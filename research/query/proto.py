"""Prototype query rankers on top of upstream/v8 graphify.serve, scored with the
same harness scoring (PR #4342's _score_answer) and the same 2000-token budget.

usage: PYTHONPATH=<v8 checkout> python proto.py VARIANT GRAPHS_DIR REPOS_DIR OUT_DIR

Variants (one change at a time, then combined):
  v8_noseedtests  v8 scorer + v8 render, but test/doc nodes are dropped from the
                  seeds unless the question mentions tests/docs
  v8_relrender    v8 seeds; output ordered by v8 term score (then hop, degree)
                  instead of hop then degree
  bm25n_seeds     node BM25 over label + path only (no body), source over tests;
                  v8 BFS/render
  bm25b_seeds     node BM25 over label + path + BODY words (identifiers,
                  docstring and comment words in the node's own source lines),
                  source over tests; v8 BFS depth 3 + v8 render
  bm25b_rel       bm25b seeds + 1-hop expansion, output ordered by BM25 score
  bm25b_rel_tests same as bm25b_rel but WITHOUT the test/doc demotion
  bm25n_rel       label+path BM25 + relevance render (isolates the body index)
  <any>_set       body words stored as a unique-term set (no term counts), i.e.
                  what a `body_terms` attribute in graph.json would carry
  bm25b_filefirst body BM25 pooled per file (best node + 0.3*rest), top files'
                  best nodes first, then their 1-hop neighbours by score

"Body words" = what an extractor can index at build time for each node: the
tokens (identifier parts, docstring/comment words) of the lines from the node's
start line up to the next node's start line in the same file (max 150 lines).
"""
import json, math, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import graphify.serve as s
from graphify.security import sanitize_label
from bench_driver import _score_answer
from bm25_files import tokens

TEST_WORDS = {"test", "tests", "testing", "pytest", "unittest", "testcase", "fixture", "fixtures"}
DOC_WORDS = {"doc", "docs", "documentation", "readme", "rst"}


def is_test(p):
    parts = p.lower().split("/")
    return any(d in ("tests", "test", "testing") for d in parts[:-1]) or parts[-1].startswith("test_") \
        or parts[-1].endswith("_test.py") or parts[-1] == "conftest.py"


def is_doc(p, d):
    return d.get("file_type") in ("document", "paper") or p.lower().endswith((".rst", ".md", ".txt"))


def demote_factor(G, nid, qwords):
    d = G.nodes[nid]; p = d.get("source_file") or ""
    if is_test(p) and not (qwords & TEST_WORDS):
        return 0.3
    if is_doc(p, d) and not (qwords & DOC_WORDS):
        return 0.3
    return 1.0


def _line(loc):
    m = re.match(r"L(\d+)", str(loc or ""))
    return int(m.group(1)) if m else None


UNIQUE_BODY = False  # variant *_set: body stored as a set of unique terms (what graph.json would hold)


def node_docs(G, repo_dir, body=True):
    by_file = defaultdict(list)
    for nid, d in G.nodes(data=True):
        by_file[d.get("source_file") or ""].append(nid)
    docs = {}
    for f, nids in by_file.items():
        lines = None
        if body and f:
            p = Path(repo_dir) / f
            if p.is_file():
                lines = p.read_text(errors="replace").splitlines()
        starts = sorted({_line(G.nodes[n].get("source_location")) for n in nids} - {None})
        for nid in nids:
            d = G.nodes[nid]
            doc = tokens(d.get("label") or "") * 2 + tokens(f)
            st = _line(d.get("source_location"))
            if lines is not None and st is not None and d.get("file_type") != "rationale":
                nxt = next((x for x in starts if x > st), len(lines) + 1)
                body = tokens("\n".join(lines[st - 1:min(nxt - 1, st + 149)]))
                doc += sorted(set(body)) if UNIQUE_BODY else body
            docs[nid] = doc
    return docs


class NodeBM25:
    def __init__(self, docs, k1=1.2, b=0.75):
        self.ids = list(docs)
        self.post = defaultdict(list)
        self.len = {}
        for nid, d in docs.items():
            self.len[nid] = len(d)
            for t, c in Counter(d).items():
                self.post[t].append((nid, c))
        self.avg = sum(self.len.values()) / max(1, len(self.len))
        N = len(self.ids)
        self.idf = {t: math.log(1 + (N - len(p) + 0.5) / (len(p) + 0.5)) for t, p in self.post.items()}
        self.k1, self.b = k1, b

    def score(self, q):
        out = defaultdict(float)
        for t in set(q):
            for nid, f in self.post.get(t, ()):
                out[nid] += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[nid] / self.avg))
        return out


def render(G, ordered, budget=2000, header=""):
    """Same NODE/EDGE line format and the same 3-chars/token cut as v8's renderer."""
    TV = s._traversal_view(G)
    lines = []
    for nid in ordered:
        d = G.nodes[nid]
        lines.append(f"NODE {sanitize_label(d.get('label', nid))} [src={sanitize_label(str(d.get('source_file', '')))} "
                     f"loc={sanitize_label(str(d.get('source_location', '')))} "
                     f"community={sanitize_label(str(d.get('community_name') or d.get('community', '')))}]")
    chosen = set(ordered)
    for u in ordered:
        for v in TV.neighbors(u):
            if v in chosen and str(u) < str(v):
                for e in s.edge_datas(TV, u, v):
                    src, tgt = e.get("_src", u), e.get("_tgt", v)
                    lines.append(f"EDGE {sanitize_label(G.nodes[src].get('label', src))} --{e.get('relation', '')} "
                                 f"[{e.get('confidence', '')}]--> {sanitize_label(G.nodes[tgt].get('label', tgt))}")
    out = "\n".join(lines)
    cb = budget * 3
    if len(out) > cb:
        cut = out[:cb].rfind("\n")
        out = out[:cut] + "\n... (truncated)"
    return header + out


def relevance_answer(G, scores, seeds, hops=1, budget=2000):
    TV = s._traversal_view(G)
    dist = {n: 0 for n in seeds}
    frontier = list(seeds)
    for h in range(1, hops + 1):
        nxt = []
        for n in frontier:
            for nb in TV.neighbors(n):
                if nb not in dist:
                    dist[nb] = h; nxt.append(nb)
        frontier = nxt
    rest = sorted(set(dist) - set(seeds), key=lambda n: (-scores.get(n, 0.0), dist[n], -G.degree(n), str(n)))
    # cap the node list so edges among them still fit under the budget
    ordered = list(seeds) + rest[:max(0, 30 - len(seeds))]
    return render(G, ordered, budget, header=f"Start: {[G.nodes[n].get('label') for n in seeds]}\n\n")


def pick(scores, G, k=5, per_file=2):
    seeds, per = [], Counter()
    for nid, sc in sorted(scores.items(), key=lambda kv: (-kv[1], str(kv[0]))):
        f = G.nodes[nid].get("source_file") or ""
        if per[f] >= per_file:
            continue
        seeds.append(nid); per[f] += 1
        if len(seeds) >= k:
            break
    return seeds


def answer(variant, G, question, index):
    qwords = set(tokens(question))
    if variant in ("v8_noseedtests", "v8_relrender"):
        terms = s._query_terms(question)
        qs = s._score_query(G, terms, collect_per_term_seeds=True)
        seeds = s._pick_seeds(qs.ranked, G=G, best_seed_by_term=qs.best_seed_by_term, term_order=qs.term_order)
        if variant == "v8_noseedtests":
            kept = [n for n in seeds if demote_factor(G, n, qwords) == 1.0]
            if not kept:  # fall back to the best non-test/doc scored nodes
                kept = [n for _, n in qs.ranked if demote_factor(G, n, qwords) == 1.0][:3]
            seeds = kept or seeds
            return s._render_query(G, question, seeds, mode="bfs", depth=3, token_budget=2000,
                                   context_filters=None, graph_path=None)
        scores = {n: sc for sc, n in qs.ranked}
        return relevance_answer(G, scores, seeds, hops=3)
    sc = index.score(tokens(question))
    variant = variant.removesuffix("_set")
    demote = not variant.endswith("_tests")
    if demote:
        sc = {n: v * demote_factor(G, n, qwords) for n, v in sc.items()}
    if variant == "bm25b_filefirst":
        per_file = defaultdict(list)
        for n, v in sc.items():
            per_file[G.nodes[n].get("source_file") or ""].append((v, n))
        frank = sorted(per_file, key=lambda f: -(max(per_file[f])[0] + 0.3 * sum(v for v, _ in sorted(per_file[f])[:-1][-5:])))
        seeds = [max(per_file[f])[1] for f in frank[:5]]
        return relevance_answer(G, sc, seeds, hops=1)
    seeds = pick(sc, G)
    if not seeds:
        return s._QUERY_NO_MATCH
    if variant in ("bm25n_seeds", "bm25b_seeds"):
        return s._render_query(G, question, seeds, mode="bfs", depth=3, token_budget=2000,
                               context_filters=None, graph_path=None)
    return relevance_answer(G, sc, seeds, hops=1)


def main(variant, graphs, repos, out):
    Path(out).mkdir(parents=True, exist_ok=True)
    for q in sorted((Path(__file__).parent / "questions").glob("*.jsonl")):
        repo = q.stem
        G = s._load_graph(str(Path(graphs) / f"{repo}.json"))
        index = None
        global UNIQUE_BODY
        UNIQUE_BODY = variant.endswith("_set")
        if variant.startswith("bm25"):
            index = NodeBM25(node_docs(G, Path(repos) / repo, body=variant.startswith("bm25b")))
        per = []
        for line in q.read_text().splitlines():
            item = json.loads(line)
            per.append(_score_answer(item["question"], item["files"], answer(variant, G, item["question"], index)))
        (Path(out) / f"{repo}.json").write_text(json.dumps({"per_question": per}))


if __name__ == "__main__":
    main(*sys.argv[1:5])
