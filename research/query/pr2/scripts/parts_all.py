import json, sys, time, functools
from collections import defaultdict
import graphify.serve as s
acc = defaultdict(float)
def wrap(name):
    f = getattr(s, name)
    def g(*a, **k):
        t = time.perf_counter(); r = f(*a, **k); acc[name] += time.perf_counter() - t; return r
    setattr(s, name, g)
for n in ["_score_query", "_body_rank_files", "_fused_file_scores", "_render_query", "_query_name_refusal", "_pick_seeds", "_bfs", "_subgraph_to_text", "_filter_graph_by_context"]:
    if hasattr(s, n): wrap(n)
G = s._load_graph(sys.argv[1]); qs = [json.loads(l)["question"] for l in open(sys.argv[2])]
s._query_graph_text(G, qs[0], mode="bfs", depth=2, token_budget=2000); acc.clear()
t = time.perf_counter()
for q in qs: s._query_graph_text(G, q, mode="bfs", depth=2, token_budget=2000)
tot = time.perf_counter() - t
print(f"total {tot/len(qs)*1000:.0f} ms/q  " + "  ".join(f"{k}={v/len(qs)*1000:.0f}" for k, v in sorted(acc.items())))
