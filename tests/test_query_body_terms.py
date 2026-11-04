"""Body words: Python nodes store the words of their own source lines
(`body_terms`), and `query` uses them.

A question often shares no word with the name of the code that answers it
("Set default FILE_UPLOAD_PERMISSION to 0o644" is answered by a settings module,
not by a `Permission` class), so name-only scoring cannot find it. Extraction now
stores, per file/class/function node, the unique words of its own lines; `query`
adds a body tier below the name tiers and a body ranking that adds start nodes
after the name seeds and is fused into the answer's file order. `path`,
`explain` and `_score_nodes` ignore body words.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import networkx as nx

from graphify.extract import extract_python
from graphify.serve import (
    _QUERY_DEMOTE_WEIGHT,
    _query_graph_text,
    _query_path_weight,
    _query_terms,
    _score_nodes,
    _score_query,
)


def _extract(tmp_path: Path, code: str) -> dict[str, dict]:
    path = tmp_path / "mod.py"
    path.write_text(textwrap.dedent(code), encoding="utf-8")
    result = extract_python(path)
    return {n["label"]: n for n in result["nodes"] if n.get("file_type") != "rationale"}


def test_function_class_and_module_nodes_store_their_own_body_words(tmp_path):
    nodes = _extract(tmp_path, '''
        """Module docstring about uploads."""
        FILE_UPLOAD_PERMISSIONS = 0o644

        class Storage:
            """Keeps files."""
            chunk_size = 64

            def save(self, name):
                # the quarantine folder holds partial uploads
                raise ValueError("cannot overwrite existing upload")
        ''')
    module = nodes["mod.py"]["body_terms"].split()
    assert {"file", "upload", "permissions", "module", "docstring", "uploads"} <= set(module)
    assert "quarantine" not in module  # the method's words stay with the method
    cls = set(nodes["Storage"]["body_terms"].split())
    assert {"storage", "keeps", "files", "chunk", "size"} <= cls
    assert "overwrite" not in cls
    method = set(nodes[".save()"]["body_terms"].split())
    assert {"quarantine", "folder", "partial", "uploads", "cannot", "overwrite", "existing", "valueerror", "value", "error"} <= method
    assert method == set(sorted(method))  # stored once each


def test_short_long_and_credential_words_are_not_stored(tmp_path):
    secret = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
    nodes = _extract(tmp_path, f'''
        def connect():
            token = "{secret}"
            ab = "x" * 50
            return token, ab, "{'y' * 45}"
        ''')
    words = nodes["connect()"]["body_terms"].split()
    assert all(3 <= len(w) <= 40 for w in words)
    assert not any("a1b2c3" in w for w in words)  # redacted before splitting


def _graph() -> nx.Graph:
    G = nx.Graph()
    # The answer: its name shares no word with the question.
    G.add_node("cfg", label="base_config.py", source_file="proj/conf/base_config.py", source_location="L1",
               body_terms="default file permissions upload")
    # Decoys that match question words by name only.
    G.add_node("perm", label="Permission", source_file="proj/auth/models.py", source_location="L10")
    G.add_node("fil", label="File", source_file="proj/files/base.py", source_location="L5")
    G.add_node("vend", label="vendored()", source_file="proj/static/jquery-3.5.1.js", source_location="L1",
               body_terms="default file permissions upload")
    G.add_edge("perm", "fil", relation="calls")
    return G


def test_query_finds_a_node_by_its_body_words():
    text = _query_graph_text(_graph(), "Set default FILE_UPLOAD_PERMISSIONS", depth=1)
    start = text.split("Start: ")[1].split("|")[0]
    assert "base_config.py" in start
    files = [line.split("[src=")[1].split(" ")[0] for line in text.splitlines() if line.startswith("NODE ")]
    assert files.index("proj/conf/base_config.py") < files.index("proj/static/jquery-3.5.1.js")


def test_without_body_words_the_answer_is_name_only():
    G = _graph()
    for n in G.nodes:
        G.nodes[n].pop("body_terms", None)
    text = _query_graph_text(G, "Set default FILE_UPLOAD_PERMISSIONS", depth=1)
    assert "base_config.py" not in text.split("Start: ")[1].split("|")[0]


def test_per_term_a_name_match_outranks_a_body_match():
    G = nx.Graph()
    G.add_node("name", label="Permission", source_file="pkg/a.py", source_location="L1")
    G.add_node("body", label="check()", source_file="pkg/b.py", source_location="L1", body_terms="permission")
    terms = _query_terms("permission")
    ranked = _score_query(G, terms, collect_per_term_seeds=True, body=True).ranked
    assert [nid for _, nid in ranked] == ["name", "body"]


def test_name_seeds_and_the_per_term_guarantee_come_first():
    text = _query_graph_text(_graph(), "Permission File upload", depth=1)
    start = text.split("Start: ")[1].split("|")[0]
    assert start.index("Permission") < start.index("base_config.py")
    assert start.index("File") < start.index("base_config.py")


def test_path_and_explain_scoring_ignore_body_words():
    G = _graph()
    terms = _query_terms("default upload permissions")
    with_body = _score_nodes(G, terms)
    for n in G.nodes:
        G.nodes[n].pop("body_terms", None)
    assert _score_nodes(G, terms) == with_body
    assert "cfg" not in [nid for _, nid in with_body]


def test_vendored_and_minified_files_are_weighted_down():
    weight = _query_path_weight(_query_terms("encode request body"))
    for path in ("requests/packages/urllib3/response.py", "sphinx/themes/basic/static/jquery-3.5.1.js",
                 "app/static/app.min.js", "lib/vendor/six.py", "ui/node_modules/x/index.js",
                 "pkg/_vendor/packaging/version.py", "src/third_party/zlib.c"):
        assert weight({"source_file": path}) == _QUERY_DEMOTE_WEIGHT, path
    for path in ("packages/core/src/index.ts", "requests/models.py", "pkg/static/theme.js"):
        assert weight({"source_file": path}) == 1.0, path
