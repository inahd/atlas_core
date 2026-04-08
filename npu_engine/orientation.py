"""
orientation.py — Philosophical orientation computation.

Maps natal chart + field interactions → position on the 2-axis system:
  oneness_axis: -1 (pure oneness/advaita) → 0 (acintya center) → +1 (pure difference/dvaita)
  path_axis:    -1 (left-hand/tantric) → 0 (both/center) → +1 (right-hand/vedic)

Sources: Supabase phil_positions, natal chart, entity interactions.
"""

import math
from typing import Any, Dict, List, Optional

# Philosophical positions (from Supabase phil_positions, cached here for offline)
POSITIONS = [
    {"id": "sunyata",           "name": "Śūnyatā",                "o": -1.0, "p":  0.0, "tradition": "bauddha"},
    {"id": "advaita",           "name": "Advaita",                "o": -0.9, "p":  0.7, "tradition": "smarta"},
    {"id": "trika",             "name": "Trika / Pratyabhijñā",   "o": -0.5, "p": -0.4, "tradition": "kashmir_shaivism"},
    {"id": "vishishtadvaita",   "name": "Viśiṣṭādvaita",         "o": -0.4, "p":  0.6, "tradition": "srivaishnava"},
    {"id": "srividya",          "name": "Śrī Vidyā",             "o": -0.3, "p": -0.6, "tradition": "srividya"},
    {"id": "acintya_bhedabheda","name": "Acintya-bhedābheda",     "o":  0.0, "p":  0.0, "tradition": "gaudiya"},
    {"id": "anekantavada",      "name": "Anekāntavāda",           "o":  0.0, "p":  0.5, "tradition": "jaina"},
    {"id": "dvaita",            "name": "Dvaita",                 "o":  0.8, "p":  0.8, "tradition": "madhva"},
]

# Element → oneness signal (ether/water lean toward unity, fire/earth toward difference)
ELEMENT_ONENESS = {
    "ether": -0.3, "water": -0.2, "air": -0.1, "fire": 0.15, "earth": 0.2,
}

# Guna → oneness signal (sattva → unity, tamas → difference)
GUNA_ONENESS = {
    "sattva": -0.2, "rajas": 0.0, "tamas": 0.15,
}

# Category → path signal
CATEGORY_PATH = {
    "deity": 0.2,     # form worship → right-hand tendency
    "devi": -0.2,     # shakti → left-hand tendency
    "ritual": 0.3,    # ritual → right-hand
    "mantra": -0.1,   # mantra → slight left
    "tantra": -0.4,   # tantra → left-hand
    "plant": -0.1,    # nature → slight left
    "yantra": -0.2,   # yantra → left
    "concept": 0.0,   # neutral
    "tattva": -0.1,   # philosophy → slight left
    "nakshatra": 0.0, # neutral
    "graha": 0.1,     # jyotish → slight right
}


def compute_natal_orientation(natal: dict) -> Dict[str, float]:
    """Compute baseline orientation from natal chart.

    Rohiṇī (moon) = earth/water → slight oneness
    Vṛṣabha (lagna) = earth → slight difference
    Budha daśā = mercury → neutral
    """
    if not natal:
        return {"oneness": 0.0, "path": 0.0}

    signals = []
    # Lagna nakshatra
    lagna_nak = natal.get("lagna_nak", "")
    if "Rohiṇī" in lagna_nak or "rohini" in lagna_nak.lower():
        signals.append((-0.15, 0.1))  # earth-water, slight devotional
    elif "Puṣya" in lagna_nak or "pushya" in lagna_nak.lower():
        signals.append((-0.1, 0.2))  # nurturing, right-hand
    # Moon sign
    moon = natal.get("moon", {})
    moon_nak = moon.get("nak", "")
    if "Punarvasu" in moon_nak:
        signals.append((-0.1, 0.0))  # renewal, center
    # Saturn exalted → structure, right-hand
    saturn = natal.get("saturn", {})
    if saturn.get("exalted"):
        signals.append((0.1, 0.2))
    # Rahu in Ārdrā → Rudra, left-hand tendency
    rahu = natal.get("rahu", {})
    if "Ārdrā" in rahu.get("nak", "") or "ardra" in rahu.get("nak", "").lower():
        signals.append((-0.1, -0.2))
    # Ketu in Mūla → liberation, oneness
    ketu = natal.get("ketu", {})
    if "Mūla" in ketu.get("nak", "") or "mula" in ketu.get("nak", "").lower():
        signals.append((-0.2, -0.1))

    if not signals:
        return {"oneness": 0.0, "path": 0.0}

    avg_o = sum(s[0] for s in signals) / len(signals)
    avg_p = sum(s[1] for s in signals) / len(signals)
    return {"oneness": round(max(-1, min(1, avg_o)), 3),
            "path": round(max(-1, min(1, avg_p)), 3)}


def compute_entity_signal(entity_id: str, element: str = "", guna: str = "",
                          category: str = "") -> Dict[str, float]:
    """Compute orientation signal from a single entity interaction."""
    if not category and "_" in entity_id:
        category = entity_id.split("_")[0]

    o = ELEMENT_ONENESS.get(element.lower(), 0) + GUNA_ONENESS.get(guna.lower(), 0)
    p = CATEGORY_PATH.get(category.lower(), 0)

    return {"oneness_signal": round(max(-1, min(1, o)), 3),
            "path_signal": round(max(-1, min(1, p)), 3)}


def nearest_position(oneness: float, path: float) -> dict:
    """Find the nearest philosophical position to a point on the 2-axis system."""
    best = None
    best_dist = float("inf")
    for pos in POSITIONS:
        d = math.sqrt((oneness - pos["o"])**2 + (path - pos["p"])**2)
        if d < best_dist:
            best_dist = d
            best = pos
    return {
        "position": best["id"] if best else "acintya_bhedabheda",
        "position_name": best["name"] if best else "Acintya-bhedābheda",
        "center_distance": round(best_dist, 3),
        "tradition": best["tradition"] if best else "gaudiya",
    }


def traditions_near(oneness: float, path: float, radius: float = 0.5) -> List[str]:
    """Find traditions that cluster near a position."""
    near = []
    for pos in POSITIONS:
        d = math.sqrt((oneness - pos["o"])**2 + (path - pos["p"])**2)
        if d <= radius:
            near.append(pos["tradition"])
    return near


def orientation_note(oneness: float, path: float) -> str:
    """Generate a human-readable orientation note."""
    parts = []
    if abs(oneness) < 0.15 and abs(path) < 0.15:
        parts.append("Near the acintya center — simultaneous oneness and difference")
    else:
        if oneness < -0.3:
            parts.append("Strong oneness orientation — unity pervades")
        elif oneness < -0.1:
            parts.append("Slight oneness tendency — unity as ground")
        elif oneness > 0.3:
            parts.append("Strong difference orientation — distinctions are real")
        elif oneness > 0.1:
            parts.append("Slight difference tendency — forms matter")

        if path < -0.3:
            parts.append("Left-hand path emphasis — śakti, tantra, direct experience")
        elif path < -0.1:
            parts.append("Slight left tendency — receptive, intuitive")
        elif path > 0.3:
            parts.append("Right-hand path emphasis — ritual, scripture, lineage")
        elif path > 0.1:
            parts.append("Slight right tendency — structured, traditional")

    return " · ".join(parts) if parts else "Centered — open to all paths"


def compute_orientation(natal: dict, interaction_history: Optional[List[dict]] = None) -> dict:
    """Full orientation computation from natal + interactions."""
    baseline = compute_natal_orientation(natal)
    o = baseline["oneness"]
    p = baseline["path"]

    # Apply interaction history if available
    if interaction_history:
        i_o = sum(h.get("oneness_signal", 0) for h in interaction_history) / len(interaction_history)
        i_p = sum(h.get("path_signal", 0) for h in interaction_history) / len(interaction_history)
        # Blend: 60% natal, 40% interactions
        o = 0.6 * o + 0.4 * i_o
        p = 0.6 * p + 0.4 * i_p

    o = round(max(-1, min(1, o)), 3)
    p = round(max(-1, min(1, p)), 3)

    pos = nearest_position(o, p)
    near = traditions_near(o, p)

    return {
        "oneness_axis": o,
        "path_axis": p,
        "center_distance": pos["center_distance"],
        "position": pos["position"],
        "position_name": pos["position_name"],
        "note": orientation_note(o, p),
        "traditions_near": near,
    }
