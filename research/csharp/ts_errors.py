"""List .cs files whose tree-sitter-c-sharp parse (the parser graphify uses) contains ERROR/MISSING nodes.
usage: uv run --frozen python research/csharp/ts_errors.py <dir> [<dir>...]"""
import sys, pathlib, json
import tree_sitter_c_sharp as tscs
from tree_sitter import Language, Parser
parser = Parser(Language(tscs.language()))
def first_err(n):
    if n.type == "ERROR" or n.is_missing:
        return n
    for c in n.children:
        if c.has_error:
            e = first_err(c)
            if e: return e
    return n if n.has_error else None
for d in sys.argv[1:]:
    root = pathlib.Path(d)
    for p in sorted(root.rglob("*.cs")):
        if "/obj/" in str(p) or "/bin/" in str(p): continue
        t = parser.parse(p.read_bytes())
        if t.root_node.has_error:
            e = first_err(t.root_node)
            print(json.dumps({"file": str(p.relative_to(root.parent if len(sys.argv)>2 else root)), "first_error_line": e.start_point[0]+1, "err_type": e.type,
                              "text": p.read_text(errors="replace").splitlines()[e.start_point[0]][:120]}))
