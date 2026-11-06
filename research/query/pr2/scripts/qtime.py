"""Query latency on the Django PR 2 graph: first query (includes building indexes) and
the median of the 114 Django questions after it. usage: PYTHONPATH=SRC python qtime.py GRAPH QUESTIONS"""
import json, sys, time, statistics
import graphify.serve as s
G = s._load_graph(sys.argv[1])
qs = [json.loads(l)["question"] for l in open(sys.argv[2])]
t = time.perf_counter(); s._query_graph_text(G, qs[0], mode="bfs", depth=3, token_budget=2000); first = time.perf_counter() - t
times = []
for q in qs:
    t = time.perf_counter(); s._query_graph_text(G, q, mode="bfs", depth=3, token_budget=2000); times.append(time.perf_counter() - t)
print(f"first query {first:.2f}s, then median {statistics.median(times)*1000:.0f} ms, max {max(times)*1000:.0f} ms")
