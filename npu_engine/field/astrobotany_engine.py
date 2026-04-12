"""
astrobotany_engine.py

Domain: S5 — Ecology & Embodiment
Purpose: Derives biodynamic planting guidance from field state using the
         astrobotanical class system (C1=fruit/seed, C2=leaf, C3=flower,
         C4=root, C5=rest/nervine).

Atlas Relations:
  nakshatra → element → astrobotanical_class (via biodynamic_vedic_mapping)
  tithi → moon phase → planting quality modifier
  field_state.panchanga → day_type, recommended_herbs, avoid_activities
"""

import csv
import os
from typing import Any, Dict, List, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_DATA = os.path.join(_ROOT, "datasets", "astrobotany")

# ── Caches ────────────────────────────────────────────────

_classes: Optional[Dict[str, dict]] = None
_herbs: Optional[List[dict]] = None
_biodynamic: Optional[List[dict]] = None
_lunar: Optional[List[dict]] = None


def _load_csv(path: str) -> List[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_classes() -> Dict[str, dict]:
    global _classes
    if _classes is None:
        rows = _load_csv(os.path.join(_DATA, "astrobotanical_classes.csv"))
        _classes = {}
        for r in rows:
            _classes[r["class_id"]] = r
            # Also index by day type for reverse lookup
            day_type = r.get("biodynamic_day_type", "").strip()
            if day_type:
                _classes[day_type] = r
    return _classes


def _load_herbs() -> List[dict]:
    global _herbs
    if _herbs is None:
        _herbs = _load_csv(os.path.join(_DATA, "herbs_by_class.csv"))
    return _herbs


def _load_biodynamic() -> List[dict]:
    global _biodynamic
    if _biodynamic is None:
        _biodynamic = _load_csv(os.path.join(_DATA, "biodynamic_vedic_mapping.csv"))
    return _biodynamic


def _load_lunar() -> List[dict]:
    global _lunar
    if _lunar is None:
        _lunar = _load_csv(os.path.join(_DATA, "lunar_plant_biology.csv"))
    return _lunar


# ── Element → day type mapping ────────────────────────────

_ELEMENT_TO_DAY_TYPE = {
    "fire":  "Fruit/Seed",
    "earth": "Root",
    "air":   "Flower",
    "water": "Leaf",
    "ether": "All (peak on lunations)",
}

_DAY_TYPE_SHORT = {
    "Fruit/Seed": "fruit",
    "Root":       "root",
    "Flower":     "flower",
    "Leaf":       "leaf",
    "All (peak on lunations)": "rest",
}

_DAY_TYPE_TO_CLASS = {
    "Fruit/Seed": "C1",
    "Root":       "C4",
    "Flower":     "C3",
    "Leaf":       "C2",
    "All (peak on lunations)": "C5",
}


# ── Nakshatra → element lookup from biodynamic mapping ────

def _nakshatra_to_element(nakshatra: str) -> str:
    """Look up element for a nakshatra via biodynamic_vedic_mapping.csv."""
    nak_clean = nakshatra.lower().strip()
    for row in _load_biodynamic():
        equivalents = row.get("nakshatra_equivalents_sidereal_major", "")
        for nak in equivalents.split(";"):
            nak_part = nak.strip().lower()
            # Remove annotations like "(cusp)", "(major)", "(half/cusp)"
            nak_name = nak_part.split("(")[0].strip()
            if nak_name and (nak_name in nak_clean or nak_clean in nak_name):
                elem = row.get("element", "").split("/")[0].strip().lower()
                return elem
    return ""


def _herbs_for_class(class_id: str) -> List[str]:
    """Return herb names matching a class ID."""
    return [
        r["herb_name"]
        for r in _load_herbs()
        if r.get("class_id") == class_id
    ]


def _biodynamic_activities(element: str) -> str:
    """Return best activities for element from biodynamic mapping."""
    elem_lower = element.lower().strip()
    for row in _load_biodynamic():
        row_elem = row.get("element", "").split("/")[0].strip().lower()
        if row_elem == elem_lower:
            return row.get("best_activities_biodynamic", "")
    return ""


def _relevant_lunar_note(paksha: str, tidx: int) -> str:
    """Pick a relevant lunar biology note based on phase."""
    lunar_rows = _load_lunar()
    if not lunar_rows:
        return ""
    # Near new/full moon → pick the lunation-specific claims
    is_new = tidx == 0 or tidx == 29
    is_full = tidx == 14 or tidx == 15
    if is_new or is_full:
        for r in lunar_rows:
            claim = r.get("claim", "")
            if "new" in claim.lower() or "full" in claim.lower():
                return claim
    # Default: return the stem tides claim (most robust evidence)
    return lunar_rows[0].get("claim", "")


def _planting_quality(paksha: str, tidx: int, day_type_short: str) -> float:
    """
    Score planting quality 0.0–1.0.

    Waxing (Śukla) favors above-ground parts (fruit, leaf, flower).
    Waning (Kṛṣṇa) favors below-ground (root) and rest/nervine.
    """
    is_waxing = paksha == "Śukla"
    didx = tidx % 15  # 0-14 within paksha

    # Base quality from phase position (peaks mid-paksha)
    phase_curve = 1.0 - abs(didx - 7) / 7.0  # 0.0 at edges, 1.0 at mid
    base = 0.4 + 0.4 * phase_curve  # range 0.4–0.8

    # Boost/penalty based on day type vs phase
    above_ground = day_type_short in ("fruit", "flower", "leaf")
    below_ground = day_type_short in ("root",)

    if above_ground and is_waxing:
        base += 0.15
    elif above_ground and not is_waxing:
        base -= 0.10
    elif below_ground and not is_waxing:
        base += 0.15
    elif below_ground and is_waxing:
        base -= 0.10

    # Full moon / new moon are transition points — slightly lower
    if tidx in (0, 14, 15, 29):
        base -= 0.05

    return round(max(0.0, min(1.0, base)), 2)


# ── Public API ────────────────────────────────────────────


def derive_astrobotany(field_state: dict) -> dict:
    """
    Given current field_state, return astrobotanical planting guidance.

    Reads from panchanga: nakshatra, element, tidx, paksha.
    Returns day_type, class, recommended herbs, planting quality.
    """
    panchanga = field_state.get("panchanga", {})

    nakshatra = panchanga.get("nakshatra", "")
    element_raw = panchanga.get("element", "")
    tidx = panchanga.get("tidx", 0)
    paksha = panchanga.get("paksha", "Śukla")

    # Step 1: Determine element — prefer biodynamic mapping, fallback to panchanga
    element = _nakshatra_to_element(nakshatra) or element_raw or "ether"

    # Step 2: Map element → biodynamic day type
    day_type_full = _ELEMENT_TO_DAY_TYPE.get(element, "All (peak on lunations)")
    day_type_short = _DAY_TYPE_SHORT.get(day_type_full, "rest")
    class_id = _DAY_TYPE_TO_CLASS.get(day_type_full, "C5")

    # Step 3: Load class details
    classes = _load_classes()
    class_record = classes.get(class_id, {})

    # Step 4: Get herbs for this class
    herbs = _herbs_for_class(class_id)

    # Step 5: Nakshatra-specific plant (from extended nakshatra data)
    nak_plant = ""
    plants_data = field_state.get("plants", [])
    if plants_data:
        nak_lower = nakshatra.lower().strip()
        for p in plants_data:
            p_nak = (p.get("nakshatra", "") or "").lower().strip()
            if p_nak and (p_nak in nak_lower or nak_lower in p_nak):
                nak_plant = p.get("plant", p.get("tree", ""))
                break

    # Step 6: Planting quality
    quality = _planting_quality(paksha, tidx, day_type_short)

    # Step 7: Lunar biology note
    lunar_note = _relevant_lunar_note(paksha, tidx)

    # Step 8: Best activities
    activities = _biodynamic_activities(element)

    return {
        "day_type":          day_type_short,
        "day_class":         class_id,
        "class_name":        class_record.get("class_name", ""),
        "element":           element,
        "planting_quality":  quality,
        "paksha":            paksha,
        "recommended_herbs": herbs,
        "nakshatra":         nakshatra,
        "nakshatra_plant":   nak_plant,
        "best_activities":   activities,
        "lunar_note":        lunar_note,
        "dosha_heuristic":   class_record.get("dosha_correspondence", ""),
        "harvest_timing":    class_record.get("harvest_timing", ""),
        "source":            "astrobotany_engine",
    }
