"""Print graphify's call-ish edges for a repro dir: python3 -I show_edges.py <dir>"""
import json, sys
g = json.load(open(sys.argv[1] + "/graphify-out/graph.json"))
lab = {n["id"]: f'{n["label"]} [{n.get("source_file")}:{n.get("source_location")}]' for n in g["nodes"]}
for l in sorted(g["links"], key=lambda l: (l.get("source_file") or "", int((l.get("source_location") or "L0")[1:] or 0))):
    if l["relation"] in ("calls", "references", "uses", "instantiates"):
        print(f'  {l["relation"]:10} {lab.get(l["source"], l["source"])}  ->  {lab.get(l["target"], l["target"])}   (site {l.get("source_location")}, ctx={l.get("context")})')
