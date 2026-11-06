"""Wall time of each part of the first and later queries (wrappers around serve functions)."""
import json, sys, time, functools
from collections import defaultdict
import graphify.serve as s
acc = defaultdict(float)
def wrap(name):
    f = getattr(s, name)
    @functools.wraps(f)
    def g(*a, **k):
        t = time.perf_counter(); r = f(*a, **k); acc[name] += time.perf_counter() - t; return r
    setattr(s, name, g)
names = ["_get_trigram_index", "_get_body_index", "_body_doc_stats", "_body_rank_files", "_score_query", "_fused_file_scores",
         "_render_query", "_query_name_refusal", "_traversal_view"]
for n in names:
    if hasattr(s, n): wrap(n)
t = time.perf_counter(); G = s._load_graph(sys.argv[1]); print(f"load {time.perf_counter()-t:.2f}s")
qs = [json.loads(l)["question"] for l in open(sys.argv[2])]
for i, q in enumerate(qs[:6]):
    acc.clear(); t = time.perf_counter(); s._query_graph_text(G, q, mode="bfs", depth=2, token_budget=2000)
    print(f"q{i} total {time.perf_counter()-t:.2f}s  " + "  ".join(f"{k}={v:.2f}" for k, v in acc.items() if v > 0.005))
