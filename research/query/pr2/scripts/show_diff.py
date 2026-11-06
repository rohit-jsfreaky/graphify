import json, sys
sys.path.insert(0, "/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad/rq")
import graphify.serve as s
from pathlib import Path
qid, depth, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
here = Path("/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad/rq"); G_DIR = "/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad/graphs_pr2"
commits = json.loads((here / "questions/commits.json").read_text())
for f in list((here / "questions").glob("*.jsonl")) + list((here / "questions_ext").glob("*.jsonl")):
    for l in f.read_text().splitlines():
        q = json.loads(l)
        if q["id"] == qid:
            g = f"{G_DIR}/{f.stem}.json" if "commit" not in q else f"{G_DIR}/{f.stem}@{q['commit'][:12]}.json"
            G = s._load_graph(g)
            Path(out).write_text(s._query_graph_text(G, q["question"], mode="bfs", depth=depth, token_budget=2000))
