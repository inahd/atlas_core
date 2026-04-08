"""
s5_kernel.py — S5 Svadhisthana · Water · Ecology kernel.

Computes the living plant wheel from field state.
Three concentric rings, three authority levels.

Ring 1 (inner, shastra): 27 nakshatra canonical plants
Ring 2 (middle, sadhu):  dosha-nakshatra herb recommendations
Ring 3 (outer, guru):    relational inference from 704 herb db

Output: S5State consumed by shell canvas and om_engines.
Writes: /tmp/s5_state.json every field cycle.
"""

import csv, json, math, time
from pathlib import Path
from typing import Dict, List, NamedTuple

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "datasets"

STABILITY  = "working"
AUTHORITY  = "guru"
LAYER      = "S5"


class PlantNode(NamedTuple):
    id:          str
    name:        str
    sanskrit:    str
    nakshatra:   str
    nak_index:   int
    ring:        int
    authority:   str
    element:     str
    dosha:       str
    body_part:   str
    deity:       str
    use:         str
    active:      bool
    angle_deg:   float
    radius:      float


class S5State(NamedTuple):
    nakshatra:        str
    active_nak_idx:   int
    canonical_plant:  str
    ring1:            List[PlantNode]
    ring2:            List[PlantNode]
    ring3:            List[PlantNode]
    day_type:         str
    element:          str
    dosha_today:      str
    harvest_quality:  str
    active_herbs:     List[str]
    timestamp:        float


NAKSHATRA_ORDER = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira",
    "Ardra","Punarvasu","Pushya","Ashlesha","Magha",
    "Purva Phalguni","Uttara Phalguni","Hasta","Chitra",
    "Swati","Vishakha","Anuradha","Jyeshtha","Mula",
    "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha",
    "Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

def _nak_index(name: str) -> int:
    name_clean = name.lower().strip()
    for i, n in enumerate(NAKSHATRA_ORDER):
        if n.lower() in name_clean or name_clean in n.lower():
            return i
    return 0

def _angle(nak_idx: int, offset: float = 0) -> float:
    return (nak_idx / 27) * 360 + offset


def _load_nakshatra_plants() -> List[PlantNode]:
    """Ring 1 — 27 canonical nakshatra plants (shastra)."""
    nodes = []
    path = DATA / "plants" / "nakshatra_plants.csv"
    if not path.exists():
        return nodes
    for row in csv.DictReader(open(path, encoding="utf-8")):
        nak = row.get("nakshatra", "").strip()
        idx = _nak_index(nak)
        nodes.append(PlantNode(
            id        = f"plant:{row.get('plant','').lower().replace(' ','_')}",
            name      = row.get("plant", "").strip(),
            sanskrit  = row.get("sanskrit_name", "").strip(),
            nakshatra = nak,
            nak_index = idx,
            ring      = 1,
            authority = "shastra",
            element   = row.get("element", "ether").lower(),
            dosha     = row.get("dosha", "").strip(),
            body_part = row.get("body_part", "").strip(),
            deity     = row.get("deity", "").strip(),
            use       = row.get("ayurvedic_use", "").strip(),
            active    = False,
            angle_deg = _angle(idx),
            radius    = 0.35,
        ))
    return nodes


def _load_dosha_herbs(current_dosha: str) -> List[PlantNode]:
    """Ring 2 — dosha-nakshatra herb recommendations (sadhu)."""
    nodes = []
    path = DATA / "ayurveda" / "dosha_nakshatra_matrix.csv"
    if not path.exists():
        return nodes
    for row in csv.DictReader(open(path, encoding="utf-8")):
        nak = row.get("nakshatra", "").strip()
        herb = row.get("herb_recommendation", "").strip()
        if not herb:
            continue
        idx = _nak_index(nak)
        dosha = row.get("primary_dosha", "").strip()
        nodes.append(PlantNode(
            id        = f"herb:{herb.lower().replace(' ','_').replace('/','_')}",
            name      = herb,
            sanskrit  = "",
            nakshatra = nak,
            nak_index = idx,
            ring      = 2,
            authority = "sadhu",
            element   = "",
            dosha     = dosha,
            body_part = "",
            deity     = "",
            use       = f"balances {dosha}",
            active    = dosha.lower() in current_dosha.lower(),
            angle_deg = _angle(idx, offset=3),
            radius    = 0.60,
        ))
    return nodes


def _load_inferred_herbs(current_nak: str, current_element: str) -> List[PlantNode]:
    """Ring 3 — relational inference from amidha_herbs (guru)."""
    nodes = []
    path = DATA / "ayurveda" / "amidha_herbs.csv"
    if not path.exists():
        return nodes

    _ELEM_DOSHA = {
        "fire": "pitta", "water": "kapha",
        "earth": "kapha", "air": "vata", "ether": "vata"
    }
    target_dosha = _ELEM_DOSHA.get(current_element.lower(), "")

    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    matched = [r for r in rows
               if target_dosha in r.get("pacify", "").lower()][:27]

    nak_idx = _nak_index(current_nak)
    for i, row in enumerate(matched):
        spread = (i - len(matched) // 2) * (180 / max(len(matched), 1))
        angle = _angle(nak_idx) + spread

        nodes.append(PlantNode(
            id        = f"herb_inferred:{row.get('name','').lower().replace(' ','_')}",
            name      = row.get("name", "").strip(),
            sanskrit  = "",
            nakshatra = current_nak,
            nak_index = nak_idx,
            ring      = 3,
            authority = "guru",
            element   = current_element,
            dosha     = row.get("pacify", "").strip(),
            body_part = "",
            deity     = "",
            use       = f"pacifies {row.get('pacify', '')}",
            active    = True,
            angle_deg = angle % 360,
            radius    = 0.82,
        ))
    return nodes


def _day_type(nakshatra: str) -> tuple:
    path = DATA / "plants" / "nakshatra_agriculture.csv"
    if not path.exists():
        return ("?", "?", "?")
    for row in csv.DictReader(open(path, encoding="utf-8")):
        if _nak_index(row.get("nakshatra", "")) == _nak_index(nakshatra):
            return (
                row.get("quality", "?").strip(),
                row.get("activity", "?").strip(),
                row.get("crops", "?").strip(),
            )
    return ("?", "?", "?")


_ELEM_DAY = {
    "fire": "fruit", "earth": "root",
    "air": "flower", "water": "leaf", "ether": "rest",
}


def derive_s5_state(field_state: dict) -> S5State:
    """Compute S5 plant wheel from field state."""
    p5        = field_state.get("panchanga", {})
    nakshatra = p5.get("nakshatra", "Hasta")
    element   = p5.get("element", "earth").lower()
    tidx      = int(p5.get("tidx", 0))

    _ELEM_DOSHA = {
        "fire": "pitta", "water": "kapha",
        "earth": "kapha", "air": "vata", "ether": "vata"
    }
    dosha_today = _ELEM_DOSHA.get(element, "tridosha")

    ring1 = _load_nakshatra_plants()
    ring2 = _load_dosha_herbs(dosha_today)
    ring3 = _load_inferred_herbs(nakshatra, element)

    nak_idx = _nak_index(nakshatra)
    ring1 = [p._replace(active=(p.nak_index == nak_idx)) for p in ring1]

    today_plant = next(
        (p.name for p in ring1 if p.nak_index == nak_idx), "?")

    quality, activity, crops = _day_type(nakshatra)
    day_type = _ELEM_DAY.get(element, "rest")

    active_herbs = (
        [p.name for p in ring1 if p.active] +
        [p.name for p in ring2 if p.active]
    )

    return S5State(
        nakshatra       = nakshatra,
        active_nak_idx  = nak_idx,
        canonical_plant = today_plant,
        ring1           = ring1,
        ring2           = ring2,
        ring3           = ring3,
        day_type        = day_type,
        element         = element,
        dosha_today     = dosha_today,
        harvest_quality = quality,
        active_herbs    = active_herbs,
        timestamp       = time.time(),
    )


def write_s5_state(field_state: dict):
    """Compute and write S5 state to /tmp/s5_state.json."""
    state = derive_s5_state(field_state)

    def node_dict(p):
        return {
            "id": p.id, "name": p.name, "sanskrit": p.sanskrit,
            "nakshatra": p.nakshatra, "nak_index": p.nak_index,
            "ring": p.ring, "authority": p.authority,
            "element": p.element, "dosha": p.dosha,
            "body_part": p.body_part, "deity": p.deity,
            "use": p.use, "active": p.active,
            "angle_deg": round(p.angle_deg, 2),
            "radius": p.radius,
        }

    out = {
        "nakshatra":       state.nakshatra,
        "active_nak_idx":  state.active_nak_idx,
        "canonical_plant": state.canonical_plant,
        "day_type":        state.day_type,
        "element":         state.element,
        "dosha_today":     state.dosha_today,
        "harvest_quality": state.harvest_quality,
        "active_herbs":    state.active_herbs,
        "ring1":           [node_dict(p) for p in state.ring1],
        "ring2":           [node_dict(p) for p in state.ring2],
        "ring3":           [node_dict(p) for p in state.ring3],
        "timestamp":       state.timestamp,
        "layer":           "S5",
        "stability":       STABILITY,
        "authority":       AUTHORITY,
    }
    Path("/tmp/s5_state.json").write_text(json.dumps(out, ensure_ascii=False))
    return out


if __name__ == "__main__":
    import urllib.request
    try:
        bs = json.loads(urllib.request.urlopen(
            "http://localhost:5000/field", timeout=3).read())
    except Exception:
        bs = {"panchanga": {"nakshatra": "Hasta", "element": "earth",
                            "guna": "sattva", "tidx": 14}}

    state = write_s5_state(bs)
    print(f"S5 State — {state['nakshatra']} / {state['element']}")
    print(f"  canonical plant: {state['canonical_plant']}")
    print(f"  day type: {state['day_type']}")
    print(f"  dosha: {state['dosha_today']}")
    print(f"  active herbs: {state['active_herbs'][:5]}")
    print(f"  ring1: {len(state['ring1'])} plants")
    print(f"  ring2: {len(state['ring2'])} herbs")
    print(f"  ring3: {len(state['ring3'])} inferred")
    print(f"  written to /tmp/s5_state.json")
