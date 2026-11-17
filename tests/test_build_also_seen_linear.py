"""`_fold_also_seen` dedupes evidence by hashable key, not by a list scan.

Each fold checked every new entry with ``ev not in kept``, a scan of the list
it was building, so one fold cost O(k^2) dict comparisons in the k entries an
edge carries and an edge folded k times O(k^3): on golang/go the build spent
over 20 minutes there. The output must not change: same entries, same order.
"""
from __future__ import annotations

import copy
import json
import random

from graphify.build import _evidence, _evidence_sort_key, _fold_also_seen, edge_evidence


def _old_fold_also_seen(winner: dict, loser: dict) -> None:
    """The list-scan implementation, verbatim, as the reference."""
    own = _evidence(winner)
    kept: list[dict] = []
    for raw in (*edge_evidence(winner)[1:], loser, *edge_evidence(loser)[1:]):
        ev = _evidence(raw)
        if ev and not ev.items() <= own.items() and ev not in kept:
            kept.append(ev)
    if kept:
        winner["also_seen"] = sorted(kept, key=_evidence_sort_key)
    else:
        winner.pop("also_seen", None)


_VALUES = {
    "confidence": ["EXTRACTED", "INFERRED", "AMBIGUOUS", "", None, "weird", 3],
    "confidence_score": [0.5, 1, 1.0, 0.0, -0.0, "0.7", "x", float("nan"),
                         float("inf"), None, True, 2],
    "source_file": ["a.py", "b.py", "", None, 7, 7.0, False, ["list"]],
    "source_location": ["L1", "L2", 1, 1.0, None, float("nan"), "L1"],
}


def _random_evidence(rng: random.Random) -> dict:
    return {k: rng.choice(v) for k, v in _VALUES.items() if rng.random() < 0.8}


def _random_edge(rng: random.Random) -> dict:
    edge = _random_evidence(rng)
    roll = rng.random()
    if roll < 0.7:
        also: list = [_random_evidence(rng) for _ in range(rng.randint(0, 12))]
        if rng.random() < 0.1:
            also.append("not a dict")
        edge["also_seen"] = also
    elif roll < 0.8:
        edge["also_seen"] = "not a list"
    return edge


def test_output_matches_the_list_scan_on_random_edges() -> None:
    rng = random.Random(4881)
    for _ in range(3000):
        winner, loser = _random_edge(rng), _random_edge(rng)
        old_w, old_l = copy.deepcopy(winner), copy.deepcopy(loser)
        new_w, new_l = copy.deepcopy(winner), copy.deepcopy(loser)
        _old_fold_also_seen(old_w, old_l)
        _fold_also_seen(new_w, new_l)
        # repr, not ==: NaN never equals itself, but must sit in the same slot.
        assert json.dumps(new_w, default=repr) == json.dumps(old_w, default=repr)
        assert new_l == old_l or json.dumps(new_l, default=repr) == json.dumps(old_l, default=repr)


def test_repeated_folds_match_the_list_scan() -> None:
    rng = random.Random(5)
    old_w, new_w = {"confidence": "EXTRACTED"}, {"confidence": "EXTRACTED"}
    for _ in range(400):
        loser = _random_edge(rng)
        _old_fold_also_seen(old_w, copy.deepcopy(loser))
        _fold_also_seen(new_w, copy.deepcopy(loser))
        assert json.dumps(new_w, default=repr) == json.dumps(old_w, default=repr)


class _CountingStr(str):
    compares = 0

    def __eq__(self, other):  # noqa: D105
        type(self).compares += 1
        return str.__eq__(self, other)

    __hash__ = str.__hash__


def test_one_fold_compares_linearly_many_evidence_entries() -> None:
    k = 600
    loser = {
        "confidence": "INFERRED",
        "also_seen": [{"confidence": "INFERRED", "source_file": _CountingStr(f"f{i}.go")}
                      for i in range(k)],
    }
    winner = {"confidence": "EXTRACTED", "source_file": "w.go"}
    _CountingStr.compares = 0
    _fold_also_seen(winner, loser)
    assert len(winner["also_seen"]) == k + 1
    # A list scan compares each new entry with every kept one: ~k*k/2 (180k).
    assert _CountingStr.compares <= 10 * k, _CountingStr.compares
