"""Full answer text of _query_graph_text for every question, depth 2 (CLI default) and 3
(MCP/benchmark default), budget 2000, each against the graph of its own commit.
usage: PYTHONPATH=SRC python dump_answers.py GRAPHS_DIR OUT.jsonl [tune|heldout|all]
Rows: {id, depth, sha256, files} where files = the NODE-line files in order."""
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, "/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad/rq")
import graphify.serve as s
from bench_driver import _answer_files
here = Path("/tmp/claude-0/-home-user-graphify/c0347ad2-359e-5c9d-840e-d5dd426d374c/scratchpad/rq")
graphs, out, only = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "all")
groups = {}
for f in sorted((here / "questions").glob("*.jsonl")):
    for l in f.read_text().splitlines():
        groups.setdefault(f"{graphs}/{f.stem}.json", []).append((f.stem, json.loads(l)))
for f in sorted((here / "questions_ext").glob("*.jsonl")):
    for l in f.read_text().splitlines():
        q = json.loads(l); groups.setdefault(f"{graphs}/{f.stem}@{q['commit'][:12]}.json", []).append((f.stem, q))
rows = []
for gpath, qs in groups.items():
    if only == "tune" and qs[0][0] != "django": continue
    if only == "heldout" and qs[0][0] == "django": continue
    G = s._load_graph(gpath)
    for repo, q in qs:
        for depth in (2, 3):
            text = s._query_graph_text(G, q["question"], mode="bfs", depth=depth, token_budget=2000)
            rows.append({"id": q["id"], "depth": depth, "sha256": hashlib.sha256(text.encode()).hexdigest(),
                         "files": _answer_files(text)})
Path(out).write_text("".join(json.dumps(r) + "\n" for r in rows))
print(len(rows), "answers", file=sys.stderr)
