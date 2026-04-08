"""
tala_graph.py — Queries tala/vibhag/beat/bol nodes from graph.
"""

from typing import Dict, List, Optional, NamedTuple
from .graph_seed_data import TALA_STRUCTURES, BOL_PROPERTIES


class TalaStructure(NamedTuple):
    name: str
    beats: int
    vibhag: List[int]
    vibhag_gravity: List[float]
    sam: int
    khali: int
    theka: List[str]
    rasa_affinity: Dict[str, float]


class BolProperties(NamedTuple):
    name: str
    weight: float
    hand: str
    resonance: str
    rasa: List[str]


def get_tala(tala_name: str) -> TalaStructure:
    """Return full tala structure from graph."""
    t = TALA_STRUCTURES.get(tala_name, TALA_STRUCTURES["Adi"])
    return TalaStructure(
        name=tala_name,
        beats=t["beats"],
        vibhag=t["vibhag"],
        vibhag_gravity=t["vibhag_gravity"],
        sam=t["sam"],
        khali=t["khali"],
        theka=t["theka"],
        rasa_affinity=t.get("rasa_affinity", {}),
    )


def get_theka(tala_name: str, rasa: str = "") -> List[str]:
    """Return theka bol sequence, optionally weighted by rasa affinity."""
    t = TALA_STRUCTURES.get(tala_name, TALA_STRUCTURES["Adi"])
    return list(t["theka"])


def get_bol_properties(bol: str) -> BolProperties:
    """Return properties of a bol stroke."""
    p = BOL_PROPERTIES.get(bol, {"weight": 0.3, "hand": "right_open",
                                  "resonance": "dry", "rasa": ["shanta"]})
    return BolProperties(name=bol, weight=p["weight"], hand=p["hand"],
                         resonance=p["resonance"], rasa=p["rasa"])


def get_rasa_tala_affinity(rasa: str) -> List[str]:
    """Return talas ranked by rasa fit (best first)."""
    scored = []
    for name, t in TALA_STRUCTURES.items():
        aff = t.get("rasa_affinity", {}).get(rasa, 0.3)
        scored.append((name, aff))
    scored.sort(key=lambda x: -x[1])
    return [name for name, _ in scored]


def beat_to_vibhag(beat: int, tala: TalaStructure) -> int:
    """Return which vibhag a beat belongs to."""
    pos = beat % tala.beats
    acc = 0
    for i, v in enumerate(tala.vibhag):
        acc += v
        if pos < acc:
            return i
    return len(tala.vibhag) - 1
