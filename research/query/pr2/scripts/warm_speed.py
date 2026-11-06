"""Warm: one process, graph loaded once, one untimed query first (indexes built), then the
median time of _query_graph_text over the questions with the CLI defaults (BFS, depth 2,
budget 2000). usage: PYTHONPATH=SRC python warm_speed.py LABEL GRAPH QUESTIONS.jsonl"""
import json, statistics, sys, time
import graphify.serve as s
lab, graph, qf = sys.argv[1:4]
G = s._load_graph(graph)
qs = [json.loads(l)["question"] for l in open(qf)]
s._query_graph_text(G, qs[0], mode="bfs", depth=2, token_budget=2000)
times = []
for q in qs:
    t = time.perf_counter(); s._query_graph_text(G, q, mode="bfs", depth=2, token_budget=2000); times.append(time.perf_counter() - t)
print(f"{lab} warm: median {statistics.median(times)*1000:.0f} ms over {len(times)} questions")
