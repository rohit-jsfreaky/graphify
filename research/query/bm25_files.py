"""BM25 over whole files: the plain-search baseline.

usage: python bm25_files.py GRAPHS_DIR REPOS_DIR OUT_DIR
Corpus per repo = every file the graph has a node for (the same files graphify
saw). Tokens: words split on non-alphanumerics, camelCase and snake_case, lower-
cased, with the whole identifier kept too. Writes OUT_DIR/<repo>.json in the
same shape as `graphify benchmark --questions --json` so aggregate.py pools it.
`tokens` = estimated tokens (chars/3) of the 5 top files' full text, i.e. what
an agent would read to use the answer; `tokens_paths` = the 5 paths alone.
"""
import json, math, re, sys
from collections import Counter
from pathlib import Path

WORD = re.compile(r"[A-Za-z0-9_]+")
CAMEL = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")
STOP = set("a an the of to in on for and or is are be with by from as at it this that not no when if into "
           "does do doesn should can cannot can't use using used via its it's than then".split())

def tokens(text):
    out = []
    for w in WORD.findall(text):
        lw = w.lower()
        parts = [p.lower() for s in w.split("_") for p in CAMEL.findall(s)]
        if lw not in STOP:
            out.append(lw)
        if len(parts) > 1:
            out.extend(p for p in parts if p not in STOP)
    return out

class BM25:
    def __init__(self, docs, k1=1.2, b=0.75):
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = sum(self.len) / max(1, len(docs))
        df = Counter(t for c in self.tf for t in c)
        N = len(docs)
        self.idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
        self.k1, self.b = k1, b

    def scores(self, q):
        qt = set(q)
        out = []
        for i, c in enumerate(self.tf):
            s = 0.0
            for t in qt:
                f = c.get(t)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            out.append(s)
        return out

def graph_files(graph_json):
    g = json.loads(Path(graph_json).read_text())
    return sorted({n["source_file"] for n in g["nodes"] if n.get("source_file")})

def main(graphs, repos, out):
    here = Path(__file__).parent
    Path(out).mkdir(parents=True, exist_ok=True)
    for q in sorted((here / "questions").glob("*.jsonl")):
        repo = q.stem
        files = [f for f in graph_files(Path(graphs) / f"{repo}.json") if (Path(repos) / repo / f).is_file()]
        texts = [(Path(repos) / repo / f).read_text(errors="replace") for f in files]
        bm = BM25([tokens(f + " " + t) for f, t in zip(files, texts)])
        per = []
        for line in q.read_text().splitlines():
            item = json.loads(line)
            sc = bm.scores(tokens(item["question"]))
            order = sorted((i for i in range(len(files)) if sc[i] > 0), key=lambda i: -sc[i])
            shown = [files[i] for i in order]
            want = set(item["files"])
            per.append({"question": item["question"], "files": item["files"],
                        "rank": next((k for k, f in enumerate(shown) if f in want), None),
                        "tokens": sum(len(texts[i]) for i in order[:5]) // 3,
                        "tokens_paths": len("\n".join(shown[:5])) // 3,
                        "top_files": shown[:5], "over_budget": False})
        (Path(out) / f"{repo}.json").write_text(json.dumps({"per_question": per}, indent=1))
        print(repo, len(files), "files")

if __name__ == "__main__":
    main(*sys.argv[1:4])
