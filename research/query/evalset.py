"""Evaluate one system on every question, each against the graph of its own commit.

usage: PYTHONPATH=<graphify src> python evalset.py LABEL SYSTEM GRAPHS_DIR GRAPHS_EXT_DIR REPOS_DIR [PARAMS_JSON]
SYSTEM: query_graph (whatever graphify is on PYTHONPATH: v8, or the PR-1 branch),
        bm25files, or proto:<variant> (proto.py, PARAMS_JSON overrides proto.PARAMS).
Question sets: questions/ (Lite, one graph per repo, commit from commits.json) and
questions_ext/ (Verified, one graph per base commit). Source text is read with
`git cat-file` at the question's commit, so no checkout is needed.
Writes results2/LABEL.jsonl: one row per question {id, repo, set, rank, tokens, top_files}.
"""
import json, subprocess, sys, time
from collections import defaultdict
from pathlib import Path
here = Path(__file__).parent
sys.path.insert(0, str(here))
import graphify.serve as s
from bench_driver import _score_answer
import bm25_files as B


class GitReader:
    def __init__(self, repo_dir, commit):
        self.commit = commit
        self.p = subprocess.Popen(["git", "-C", str(repo_dir), "cat-file", "--batch"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.cache = {}

    def __call__(self, path):
        if path in self.cache:
            return self.cache[path]
        self.p.stdin.write(f"{self.commit}:{path}\n".encode()); self.p.stdin.flush()
        head = self.p.stdout.readline().split()
        if len(head) < 3 or head[1] != b"blob":
            self.cache[path] = None; return None
        data = self.p.stdout.read(int(head[2])); self.p.stdout.read(1)
        txt = data.decode("utf-8", "replace") if b"\0" not in data[:8000] else None
        self.cache[path] = txt
        return txt

    def close(self):
        self.p.stdin.close(); self.p.wait()


def groups(graphs, graphs_ext):
    commits = json.loads((here / "questions/commits.json").read_text())
    g = defaultdict(list)
    for f in sorted((here / "questions").glob("*.jsonl")):
        c = commits[f.stem]["commit"]
        for l in f.read_text().splitlines():
            g[(f.stem, c, str(Path(graphs) / f"{f.stem}.json"), "lite")].append(json.loads(l))
    for f in sorted((here / "questions_ext").glob("*.jsonl")):
        for l in f.read_text().splitlines():
            q = json.loads(l)
            g[(f.stem, q["commit"], str(Path(graphs_ext) / f"{f.stem}@{q['commit'][:12]}.json"), "verified")].append(q)
    return g


def main(label, system, graphs, graphs_ext, repos, params=None, only=None):
    import proto
    if params:
        proto.PARAMS.update(json.loads(params))
    out = []
    t0 = time.time()
    for (repo, commit, gpath, qset), qs in groups(graphs, graphs_ext).items():
        if only == "tune" and repo != "django":
            continue  # tuning runs never touch held-out questions
        if not Path(gpath).exists():
            print(f"MISSING GRAPH {gpath}", file=sys.stderr); continue
        G = s._load_graph(gpath)
        read = GitReader(Path(repos) / repo, commit)
        if system == "query_graph":
            ask = lambda q: s._query_graph_text(G, q, mode="bfs", depth=3, token_budget=2000)
        elif system == "bm25files":
            files = sorted({d.get("source_file") for _, d in G.nodes(data=True) if d.get("source_file")})
            texts = {f: read(f) for f in files}
            files = [f for f in files if texts[f] is not None]
            bm = B.BM25([B.tokens(f + " " + texts[f]) for f in files])
            def ask(q, files=files, bm=bm, texts=texts):
                sc = bm.scores(B.tokens(q))
                order = sorted((i for i in range(len(files)) if sc[i] > 0), key=lambda i: -sc[i])
                # a file list in NODE-line form so the shared scorer reads it; tokens = reading the 5 files
                text = "\n".join(f"NODE f [src={files[i]} loc=L1 community=]" for i in order)
                return text, sum(len(texts[files[i]]) for i in order[:5]) // 3
        elif system.startswith("proto:"):
            variant = system.split(":", 1)[1]
            index = None
            if variant.startswith("bm25"):
                proto.UNIQUE_BODY = variant.endswith("_set")
                docs = proto.node_docs(G, read, body=variant.startswith("bm25b"))
                index = proto.Index(G, docs) if variant.removesuffix("_set") == "bm25b_ff2" else proto.NodeBM25(docs)
            ask = lambda q, v=variant, index=index: proto.answer(v, G, q, index)
        else:
            raise SystemExit(f"unknown system {system}")
        for q in qs:
            res = ask(q["question"])
            text, tok = res if isinstance(res, tuple) else (res, None)
            r = _score_answer(q["question"], q["files"], text)
            out.append({"id": q["id"], "repo": repo, "set": qset, "rank": r["rank"],
                        "tokens": r["tokens"] if tok is None else tok, "top_files": r["top_files"]})
        read.close()
    (here / "results2").mkdir(exist_ok=True)
    (here / "results2" / f"{label}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in out))
    print(f"{label}: {len(out)} questions, {time.time() - t0:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main(*sys.argv[1:])
