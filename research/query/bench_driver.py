"""Fallback when PR #4342 does not cherry-pick onto a PR head (benchmark.py/cli.py
conflict). Run with PYTHONPATH=<PR worktree>: imports THAT PR's graphify.serve and
asks its query_graph each question with the MCP defaults (BFS, depth 3, budget
2000); scoring is PR #4342's own _score_answer, copied verbatim below.

usage: PYTHONPATH=WT python bench_driver.py GRAPH.json QUESTIONS.jsonl > out.json
Writes the same JSON shape as `graphify benchmark --questions --json`.
"""
import json, re, sys

_ANSWER_NODE_RE = re.compile(r"^NODE .*? \[src=(.*?) loc=", re.M)

def _norm_path(path):
    path = path.replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return path

def _answer_files(text):
    files = []
    for m in _ANSWER_NODE_RE.finditer(text):
        p = _norm_path(m.group(1))
        if p and p not in files:
            files.append(p)
    return files

def _score_answer(question, expected, text):
    shown = _answer_files(text)
    wanted = set(expected)
    return {"question": question, "files": expected,
            "rank": next((i for i, f in enumerate(shown) if f in wanted), None),
            "tokens": len(text) // 3, "over_budget": "[i] Complete answer over budget" in text,
            "files_shown": len(shown), "top_files": shown[:5]}

def answer_fn():
    import graphify.serve as s
    if hasattr(s, "_query_graph_text"):
        return lambda G, q: s._query_graph_text(G, q, mode="bfs", depth=3, token_budget=2000)
    raise SystemExit("this PR has no _query_graph_text (April-era MCP closure); not measured")

if __name__ == "__main__":
    import graphify.serve as s
    G = s._load_graph(sys.argv[1])
    ask = answer_fn()
    per = []
    for line in open(sys.argv[2]):
        item = json.loads(line)
        per.append(_score_answer(item["question"], [_norm_path(f) for f in item["files"]], ask(G, item["question"])))
    print(json.dumps({"nodes": G.number_of_nodes(), "per_question": per}))
