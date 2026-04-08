"""
city_engine.py — Vastu city generator. S6 neutral portal.

Projects a vastu mandala onto a hex settlement.
Each district maps to an app/domain.
Active district from current ashtakala/field state.
Interaction logging → adaptive layout (districts grow/shrink with use).

Pattern follows ui_vastu_engine.py.
"""

import json
import logging
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import csv

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_ZONES_CSV = os.path.join(_ROOT, "datasets", "cosmology", "vastu_zones.csv")
_CITY_DIR = os.path.join(_ROOT, "instance", "city")
_INTERACTIONS_LOG = os.path.join(_CITY_DIR, "interactions.jsonl")
_SCORES_FILE = os.path.join(_CITY_DIR, "district_scores.json")

# ══════════════════════════════════════════════════════════
# CANONICAL DISTRICT MAP
# ══════════════════════════════════════════════════════════

_DISTRICTS = {
    "NE": {"deity": "Ishana", "terrain": "sacred", "color": "#1a0d28",
            "app_url": "/reading/bandhu", "buildings": ["temple", "study_hall", "meditation_pavilion"],
            "symbol": "\u2726"},
    "N":  {"deity": "Kubera", "terrain": "treasury", "color": "#0d1828",
            "app_url": "/kala", "buildings": ["granary", "calendar_tower", "water_tank"],
            "symbol": "\u25C8"},
    "NW": {"deity": "Vayu", "terrain": "wind", "color": "#0d2818",
            "app_url": "/bandhu", "buildings": ["music_pavilion", "herb_spiral", "gateway"],
            "symbol": "\u266A"},
    "E":  {"deity": "Indra", "terrain": "village", "color": "#280d0d",
            "app_url": "/vidya", "buildings": ["market_gate", "guest_house", "workshop"],
            "symbol": "\u2B21"},
    "SE": {"deity": "Agni", "terrain": "forge", "color": "#281808",
            "app_url": "/kala", "buildings": ["forge", "kitchen", "drying_room"],
            "symbol": "\u25B2"},
    "S":  {"deity": "Yama", "terrain": "boundary", "color": "#1a1408",
            "app_url": "/trajectory", "buildings": ["storage", "compost", "root_cellar"],
            "symbol": "\u25CE"},
    "SW": {"deity": "Nirriti", "terrain": "forest", "color": "#0d2010",
            "app_url": "/bhumi/guild", "buildings": ["food_forest", "guild_garden", "seed_bank"],
            "symbol": "\u2767"},
    "W":  {"deity": "Varuna", "terrain": "river", "color": "#0d2020",
            "app_url": "/journal", "buildings": ["bathing_ghat", "pond", "water_garden"],
            "symbol": "\u25CE"},
    "C":  {"deity": "Brahma", "terrain": "void", "color": "#0a0d14",
            "app_url": "/reading/bandhu", "buildings": [],
            "symbol": "\u00B7"},
}

_SIZES = {
    "hamlet":  {"w": 7,  "h": 7,  "scale": 3.0},
    "village": {"w": 17, "h": 13, "scale": 5.0},
    "town":    {"w": 33, "h": 25, "scale": 10.0},
}


def _hex_direction(q, r):
    """Map hex (q,r) to vastu direction from center."""
    if q == 0 and r == 0:
        return "C"
    angle = math.atan2(r, q) * 180 / math.pi
    # Normalize to 0-360
    if angle < 0:
        angle += 360
    # Map angle to 8 directions (flat-top hex orientation)
    if angle < 22.5 or angle >= 337.5:
        return "E"
    elif angle < 67.5:
        return "SE"
    elif angle < 112.5:
        return "S"
    elif angle < 157.5:
        return "SW"
    elif angle < 202.5:
        return "W"
    elif angle < 247.5:
        return "NW"
    elif angle < 292.5:
        return "N"
    else:
        return "NE"


# ══════════════════════════════════════════════════════════
# INTERACTION LOGGING + ADAPTIVE SCORING
# ══════════════════════════════════════════════════════════

def log_interaction(gate: str, app: str, duration_s: float = 0,
                    entities: list = None, sections: list = None) -> dict:
    """Append interaction to JSONL log. Recompute scores. Never raises."""
    try:
        os.makedirs(_CITY_DIR, exist_ok=True)
        entry = {
            "gate": gate,
            "app": app,
            "duration_s": duration_s,
            "entities": entities or [],
            "sections": sections or [],
            "timestamp": datetime.now().isoformat(),
        }
        with open(_INTERACTIONS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log.info("city interaction: gate=%s app=%s dur=%.0fs", gate, app, duration_s)
        return _recompute_scores()
    except Exception as e:
        log.warning("city log failed: %s", e)
        return {}


def _recompute_scores() -> dict:
    """Recompute district engagement scores from interaction log."""
    scores = {d: 0.0 for d in _DISTRICTS}
    total = 0
    try:
        if not os.path.exists(_INTERACTIONS_LOG):
            return scores
        with open(_INTERACTIONS_LOG, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    gate = entry.get("gate", "")
                    dur = float(entry.get("duration_s", 0))
                    if gate in scores:
                        scores[gate] += max(1.0, dur / 60.0)  # minutes, min 1
                        total += 1
                except (json.JSONDecodeError, ValueError):
                    continue
        # Normalize to 0-1
        if total > 0:
            max_score = max(scores.values()) or 1.0
            scores = {k: round(v / max_score, 3) for k, v in scores.items()}
        # Save
        os.makedirs(_CITY_DIR, exist_ok=True)
        with open(_SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except Exception:
        pass
    return scores


def get_district_scores() -> dict:
    """Read cached district scores. Returns empty dict on error."""
    try:
        if os.path.exists(_SCORES_FILE):
            with open(_SCORES_FILE, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {d: 0.0 for d in _DISTRICTS}


def get_gate_inscription(direction: str, field_state: dict) -> dict:
    """Generate gate inscription for a district. Uses composition_engine."""
    dd = _DISTRICTS.get(direction, {})
    if not dd:
        return {"inscription": "", "district": direction, "app": "", "what_awaits": ""}

    # Field context
    p5 = field_state.get("panchanga", {})
    nak = p5.get("nakshatra", "")
    element = p5.get("element", "")

    # Try composition engine for inscription
    inscription = ""
    try:
        from .composition_engine import compose_response
        comp = compose_response(
            f"entering {dd['deity']} gate, {dd['terrain']} district",
            field_state, use_llm=False)
        pada = comp.get("pada", {})
        inscription = pada.get("opening_line", "")
    except Exception:
        pass

    if not inscription:
        inscription = f"Enter the realm of {dd['deity']}"

    # What awaits from district context
    what_awaits = f"{dd['terrain']} · {dd.get('buildings', ['unknown'])[0].replace('_', ' ')}"

    return {
        "inscription": inscription,
        "district": direction,
        "deity": dd.get("deity", ""),
        "app": dd.get("app_url", ""),
        "what_awaits": what_awaits,
    }


def city_report(field_state: dict) -> dict:
    """Weekly city engagement report. Uses reading_engine for interpretation."""
    scores = get_district_scores()
    high = [k for k, v in scores.items() if v > 0.6]
    low = [k for k, v in scores.items() if v < 0.2 and k != "C"]
    never = [k for k, v in scores.items() if v == 0.0 and k != "C"]

    # Get reading for guidance
    guidance = ""
    try:
        from .reading_engine import derive_reading
        r = derive_reading("bandhu", field_state, intention="city practice focus")
        guidance = r.get("interpretation", {}).get("guidance", "")
    except Exception:
        pass

    return {
        "scores": scores,
        "grew": high,
        "shrunk": low,
        "unvisited": never,
        "guidance": guidance,
        "period": "weekly",
    }


def _validate(city):
    defaults = {
        "grid_size": {"width": 17, "height": 13},
        "scale_m_per_hex": 5.0,
        "hexes": [],
        "active_district": "",
        "brahmasthana": {"q": 0, "r": 0, "radius": 1},
        "paths": [],
        "field_moment": "",
        "attestation": "SYNTHESIS",
    }
    for k, v in defaults.items():
        if k not in city or city[k] is None:
            city[k] = v
    return city


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def derive_vastu_city(field_state: dict, city_size: str = "village") -> dict:
    """Generate vastu city hex layout from field state. Never raises."""
    try:
        p5 = field_state.get("panchanga", {})
        element = p5.get("element", "ether").lower()
        nak = p5.get("nakshatra", "")

        # Active district from ashtakala
        try:
            from .goloka_engine import derive_goloka_state
            goloka = derive_goloka_state(field_state)
            active_forest = goloka.get("active_forest", {}).get("name", "")
            # Map forest → direction (rough)
            _FOREST_DIR = {"Madhuvana": "NW", "Vrindavana": "C", "Kamyavana": "S",
                           "Bhadravana": "N", "Talavana": "N", "Bahulavana": "E"}
            active_district = _FOREST_DIR.get(active_forest, "C")
        except Exception:
            active_district = "C"

        sz = _SIZES.get(city_size, _SIZES["village"])
        half_w = sz["w"] // 2
        half_h = sz["h"] // 2

        # Adaptive layout: district scores affect boundary
        scores = get_district_scores()

        hexes = []
        for q in range(-half_w, half_w + 1):
            for r in range(-half_h, half_h + 1):
                if abs(q + r) > max(half_w, half_h):
                    continue
                dist = math.sqrt(q * q + r * r)
                direction = _hex_direction(q, r)
                dd = _DISTRICTS.get(direction, _DISTRICTS["C"])

                # Adaptive: high-score districts extend, low-score shrink
                district_score = scores.get(direction, 0.0)
                max_dist = half_w * (0.7 + district_score * 0.3)
                if direction != "C" and dist > max_dist:
                    continue  # district boundary shrunk

                # Terrain decay for unvisited districts
                terrain = dd["terrain"]
                if district_score == 0.0 and dist > half_w * 0.4 and direction != "C":
                    terrain = "overgrown"

                # Building type from distance
                if dist < 2:
                    btype = dd["buildings"][0] if dd["buildings"] else "open"
                elif dist < half_w * 0.5:
                    btype = dd["buildings"][1] if len(dd["buildings"]) > 1 else "residence"
                else:
                    btype = dd["buildings"][-1] if dd["buildings"] else "field"

                hexes.append({
                    "q": q, "r": r,
                    "district": direction,
                    "direction_name": dd["deity"],
                    "terrain": terrain,
                    "building_type": btype if terrain != "overgrown" else "overgrown",
                    "app_url": dd["app_url"],
                    "active": direction == active_district,
                    "element": element if direction == active_district else "",
                    "color": dd["color"],
                    "symbol": dd["symbol"] if terrain != "overgrown" else "\u2042",
                    "distance_from_center": round(dist, 1),
                    "engagement": round(district_score, 2),
                })

        # Main roads
        paths = [
            {"from_q": -half_w, "from_r": 0, "to_q": half_w, "to_r": 0, "path_type": "road"},
            {"from_q": 0, "from_r": -half_h, "to_q": 0, "to_r": half_h, "path_type": "road"},
        ]

        field_moment = f"{nak} \u00b7 {element} \u00b7 {active_district} district active"

        city = {
            "grid_size": {"width": sz["w"], "height": sz["h"]},
            "scale_m_per_hex": sz["scale"],
            "hexes": hexes,
            "active_district": active_district,
            "brahmasthana": {"q": 0, "r": 0, "radius": 1},
            "paths": paths,
            "field_moment": field_moment,
            "attestation": "SYNTHESIS",
        }
        return _validate(city)

    except Exception:
        return _validate({"attestation": "SYNTHESIS"})
