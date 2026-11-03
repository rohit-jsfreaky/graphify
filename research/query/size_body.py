"""Part B: graph.json size and extra build time when body words are stored per node.

usage: PYTHONPATH=<v8> python size_body.py GRAPHS_DIR REPOS_DIR OUT.tsv
For each Lite repo graph (the commit in questions/commits.json): time the body-word
pass (read every source file at that commit, cut each node's lines, tokenize, shrink
to the storage form) and write the graph with a `body_terms` string per node, in the
same compact JSON form graphify writes. Reports bytes per form; build seconds of the
plain graph come from build_times.tsv (time_builds.sh).
"""
import json, sys, time
from pathlib import Path
here = Path(__file__).parent; sys.path.insert(0, str(here))
import graphify.serve as s
import proto
from evalset import GitReader

MODES = ["full", "set", "nostop", "lean"]

def main(graphs, repos, out):
    commits = json.loads((here / "questions/commits.json").read_text())
    rows = ["repo\tmode\tplain_bytes\tbytes\tgrowth_pct\tbody_pass_s"]
    for repo, info in commits.items():
        gpath = Path(graphs) / f"{repo}.json"
        raw = json.loads(gpath.read_text())
        plain = len(json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode())
        G = s._load_graph(str(gpath))
        read = GitReader(Path(repos) / repo, info["commit"])
        t0 = time.time(); bodies = proto.body_terms(G, read); t_tok = time.time() - t0
        read.close()
        for mode in MODES:
            t1 = time.time(); shr = proto.shrink_body(G, bodies, mode); t_mode = time.time() - t1
            for n in raw["nodes"]:
                b = shr.get(n["id"])
                if b:
                    n["body_terms"] = " ".join(b)
                else:
                    n.pop("body_terms", None)
            size = len(json.dumps(raw, ensure_ascii=False, separators=(",", ":")).encode())
            rows.append(f"{repo}\t{mode}\t{plain}\t{size}\t{100 * (size - plain) / plain:.1f}\t{t_tok + t_mode:.1f}")
            print(rows[-1], flush=True)
    Path(out).write_text("\n".join(rows) + "\n")

if __name__ == "__main__":
    main(*sys.argv[1:4])
