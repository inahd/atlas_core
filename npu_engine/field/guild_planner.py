"""
guild_planner.py — Permaculture guild generator from real data.

Reads:
  guild_relations.csv    — 216 relations across 27 anchors
  nakshatra_plants.csv   — anchor plants + timing
  pfaf_lookup.py         — PFAF SQLite (if available)
  herb_spine_108.csv     — Ayurvedic profiles

Returns complete guild plan with hex layout, canopy, roots, timing.

Pattern follows ui_vastu_engine.py:
    canonical data → internal helpers → validation → public API
"""

import csv
import io
import logging
import math
import os
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_GUILD_CSV = os.path.join(_ROOT, "datasets", "plants", "guild_relations.csv")
_PLANTS_CSV = os.path.join(_ROOT, "datasets", "plants", "nakshatra_plants.csv")
_HERBS_CSV = os.path.join(_ROOT, "datasets", "ayurveda", "herb_spine_108.csv")

_guild_cache = None
_plants_cache = None
_herbs_cache = None


# ══════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════

def _load_csv(path):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read().lstrip()
        return list(csv.DictReader(io.StringIO(text)))
    except Exception:
        return []


def _guild_relations():
    global _guild_cache
    if _guild_cache is None:
        rows = _load_csv(_GUILD_CSV)
        _guild_cache = {}
        for r in rows:
            anchor = r.get("anchor_plant", "").strip()
            if anchor:
                _guild_cache.setdefault(anchor, []).append(r)
    return _guild_cache


def _nak_plants():
    global _plants_cache
    if _plants_cache is None:
        _plants_cache = _load_csv(_PLANTS_CSV)
    return _plants_cache


def _herbs():
    global _herbs_cache
    if _herbs_cache is None:
        _herbs_cache = _load_csv(_HERBS_CSV)
    return _herbs_cache


def _pfaf(latin_name):
    """Try PFAF lookup. Returns None if unavailable."""
    try:
        from datasets.plants.pfaf_lookup import get_pfaf_plant
        return get_pfaf_plant(latin_name)
    except Exception:
        return None


def _find_nak_plant(nak_name):
    """Find plant row for a nakshatra."""
    nak_n = nak_name.lower().replace(" ", "").replace("_", "")
    for a, b in [("ā","a"),("ī","i"),("ū","u"),("ṛ","r"),("ṣ","sh"),("ś","sh")]:
        nak_n = nak_n.replace(a, b)
    for p in _nak_plants():
        pn = p.get("nakshatra", "").lower().replace(" ", "")
        if pn and (pn in nak_n or nak_n in pn):
            return p
    return {}


def _find_herb(plant_name):
    """Find Ayurvedic data for a plant."""
    name_l = plant_name.lower()
    for h in _herbs():
        if name_l in h.get("name_common", "").lower() or name_l in h.get("name_iast", "").lower():
            return h
    return {}


# ══════════════════════════════════════════════════════════
# CANONICAL MAPPINGS
# ══════════════════════════════════════════════════════════

_FUNCTION_LAYER = {
    "nitrogen_fixer": "understory",
    "dynamic_accumulator": "shrub",
    "pest_repellent": "herb",
    "pollinator_attractor": "herb",
    "ground_cover": "ground",
    "climber": "vine",
    "root_crop": "root",
}

_VASTU_HEX = {
    "NW": (-2, -1), "N": (0, -2), "NE": (2, -1),
    "E": (2, 0), "SE": (1, 2), "S": (0, 2),
    "SW": (-1, 2), "W": (-2, 0),
}

_FUNCTION_ICON = {
    "nitrogen_fixer": "\u2191",        # ↑
    "dynamic_accumulator": "\u2295",   # ⊕
    "pest_repellent": "\u25C9",        # ◉
    "pollinator_attractor": "\u2740",  # ✿
    "ground_cover": "\u2261",          # ≡
    "climber": "\u2197",               # ↗
    "root_crop": "\u2193",             # ↓
}

_PLOT_SIZES = {
    "small":  {"grid": 7,  "scale": 1.0},
    "medium": {"grid": 11, "scale": 2.0},
    "large":  {"grid": 17, "scale": 3.0},
}

# Height → canopy radius in hexes
def _canopy_hexes(height_m):
    if height_m < 2:
        return 1
    elif height_m < 5:
        return 2
    elif height_m < 10:
        return 3
    return 4

# Height estimates from nakshatra_plants.csv (no PFAF)
_HEIGHT_ESTIMATES = {
    "tree": 10.0, "large tree": 15.0, "shrub": 2.5,
    "herb": 0.6, "vine": 3.0, "grass": 0.3,
    "default": 3.0,
}


def _estimate_height(plant_name, nak_row=None):
    """Estimate height from available data."""
    # Try PFAF
    pfaf = _pfaf(plant_name)
    if pfaf and pfaf.get("height"):
        try:
            return float(pfaf["height"])
        except (ValueError, TypeError):
            pass
    # Estimate from type
    if nak_row:
        use = nak_row.get("use", "").lower()
        for key, h in _HEIGHT_ESTIMATES.items():
            if key in use:
                return h
    return _HEIGHT_ESTIMATES["default"]


def _moon_phase_for_type(guild_function):
    """Lunar timing from function type."""
    if guild_function in ("root_crop",):
        return "waning", "root plants → waning/new moon"
    elif guild_function in ("pollinator_attractor",):
        return "full_moon", "flower plants → full moon"
    elif guild_function in ("ground_cover", "nitrogen_fixer"):
        return "waxing", "leaf/growth plants → waxing moon"
    return "waxing", "general planting → waxing moon"


# ══════════════════════════════════════════════════════════
# VALIDATION
# ══════════════════════════════════════════════════════════

def _validate(plan):
    defaults = {
        "anchor": {}, "companions": [], "conflict": {},
        "guild_profile": {"total_height_range": [0, 0], "layers_present": [],
                          "dosha_balance": {"vata": 0, "pitta": 0, "kapha": 0},
                          "medicinal_rating": 0, "edibility_rating": 0,
                          "soil_improvement": [], "succession_stage": "building"},
        "hex_layout": {"grid_size": 11, "cells": [], "scale_m_per_hex": 2.0},
        "planting_calendar": [],
        "attestation": "SYNTHESIS",
        "pfaf_credit": "Plants for a Future database (pfaf.org)",
    }
    for k, v in defaults.items():
        if k not in plan or plan[k] is None:
            plan[k] = v
        elif isinstance(v, dict) and isinstance(plan[k], dict):
            for dk, dv in v.items():
                if dk not in plan[k]:
                    plan[k][dk] = dv
    return plan


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def plan_guild(anchor_plant: str, field_state: dict,
               plot_size: str = "medium",
               dosha_target: str = None) -> dict:
    """Generate complete permaculture guild from real data.

    Args:
        anchor_plant: name of the anchor tree (e.g. "Arjuna")
        field_state: from kernel field_state()
        plot_size: 'small'|'medium'|'large'
        dosha_target: 'vata'|'pitta'|'kapha' or None

    Returns validated guild plan. Never raises.
    """
    try:
        p5 = field_state.get("panchanga", {})
        nak = p5.get("nakshatra", "")
        tidx = int(p5.get("tidx", 0))
        element = p5.get("element", "earth").lower()

        # Find anchor in nakshatra_plants
        nak_row = _find_nak_plant(nak)
        if not anchor_plant and nak_row:
            anchor_plant = nak_row.get("plant", "")

        # Get guild relations
        relations = _guild_relations().get(anchor_plant, [])
        if not relations:
            # Try fuzzy match
            for key in _guild_relations():
                if anchor_plant.lower() in key.lower() or key.lower() in anchor_plant.lower():
                    relations = _guild_relations()[key]
                    anchor_plant = key
                    break

        herb_data = _find_herb(anchor_plant)
        anchor_height = _estimate_height(anchor_plant, nak_row)
        pfaf_data = _pfaf(anchor_plant)

        # Build anchor
        anchor = {
            "name": anchor_plant,
            "latin": pfaf_data.get("latin_name", "") if pfaf_data else "",
            "height_m": anchor_height,
            "spread_m": round(anchor_height * 0.6, 1),
            "root_depth": "deep" if anchor_height > 5 else "medium",
            "canopy_radius_hex": _canopy_hexes(anchor_height),
            "dosha_effect": herb_data.get("dosha_effect", ""),
            "element": element,
            "nakshatra": nak,
            "pfaf_edibility": int(pfaf_data.get("edibility_rating", 0)) if pfaf_data else 0,
            "pfaf_medicinal": int(pfaf_data.get("medicinal_rating", 0)) if pfaf_data else 0,
            "plant_timing": {
                "best_nakshatra": nak_row.get("nakshatra", nak) if nak_row else nak,
                "best_phase": "waxing",
                "best_vara": nak_row.get("deity", "").lower() if nak_row else "",
                "current_score": 0.5,
            },
        }

        # Build companions
        companions = []
        conflict = {}
        plot = _PLOT_SIZES.get(plot_size, _PLOT_SIZES["medium"])

        for rel in relations:
            rtype = rel.get("relationship_type", "")
            comp_name = rel.get("companion_plant", "")
            func = rel.get("guild_function", "")
            vastu = rel.get("vastu_zone", "")

            if rtype == "conflict":
                conflict = {
                    "name": comp_name,
                    "reason": rel.get("notes", func),
                    "hex_position": {"q": 4, "r": 4},
                    "min_distance_m": anchor_height * 1.5,
                }
                continue

            comp_height = _estimate_height(comp_name)
            comp_pfaf = _pfaf(comp_name)
            moon_phase, moon_reason = _moon_phase_for_type(func)
            hex_pos = _VASTU_HEX.get(vastu, (1, 0))

            companions.append({
                "name": comp_name,
                "latin": comp_pfaf.get("latin_name", "") if comp_pfaf else "",
                "guild_function": func,
                "function_icon": _FUNCTION_ICON.get(func, ""),
                "vastu_zone": vastu,
                "hex_position": {"q": hex_pos[0], "r": hex_pos[1]},
                "height_m": comp_height,
                "spread_m": round(comp_height * 0.5, 1),
                "root_depth": "shallow" if func in ("ground_cover", "pest_repellent") else "medium",
                "canopy_overlap": comp_height > anchor_height * 0.3,
                "dosha_effect": "",
                "ayurvedic_synergy": rel.get("ayurvedic_synergy", ""),
                "layer": _FUNCTION_LAYER.get(func, "shrub"),
                "plant_timing": {
                    "best_nakshatra": rel.get("planting_nakshatra", ""),
                    "best_phase": rel.get("planting_phase", moon_phase),
                    "best_vara": rel.get("planting_vara", ""),
                },
            })

        # Dosha filtering
        if dosha_target:
            # Prefer companions whose ayurvedic_synergy mentions the target dosha
            companions.sort(key=lambda c: (
                1 if dosha_target.lower() in c.get("ayurvedic_synergy", "").lower() else 0
            ), reverse=True)

        # Guild profile
        all_heights = [anchor_height] + [c["height_m"] for c in companions]
        layers = sorted(set(c["layer"] for c in companions))
        if anchor_height > 5:
            layers = ["canopy"] + layers

        dosha_balance = {"vata": 0, "pitta": 0, "kapha": 0}
        anchor_dosha = anchor.get("dosha_effect", "").lower()
        for d in ("vata", "pitta", "kapha"):
            if d in anchor_dosha:
                dosha_balance[d] += 1
        dosha_balance["pitta"] = max(1, dosha_balance["pitta"])  # plants generally have some pitta effect

        soil_funcs = [c["guild_function"] for c in companions
                      if c["guild_function"] in ("nitrogen_fixer", "dynamic_accumulator", "ground_cover")]

        profile = {
            "total_height_range": [round(min(all_heights), 1), round(max(all_heights), 1)],
            "layers_present": layers,
            "dosha_balance": dosha_balance,
            "medicinal_rating": anchor["pfaf_medicinal"],
            "edibility_rating": anchor["pfaf_edibility"],
            "soil_improvement": soil_funcs,
            "succession_stage": "building" if anchor_height < 5 else "climax",
        }

        # Hex layout
        grid_size = plot["grid"]
        scale = plot["scale"]
        cells = [{"q": 0, "r": 0, "plant": anchor_plant, "layer": "canopy",
                  "canopy_circle": {"radius_hex": anchor["canopy_radius_hex"]},
                  "color": "#d4a84b", "highlight": True}]
        for c in companions:
            hp = c["hex_position"]
            cells.append({
                "q": hp["q"], "r": hp["r"],
                "plant": c["name"], "layer": c["layer"],
                "function": c["guild_function"],
                "function_icon": c["function_icon"],
                "color": {"nitrogen_fixer": "#5cb87a", "dynamic_accumulator": "#4878c8",
                           "pest_repellent": "#cc6644", "pollinator_attractor": "#ffaadd",
                           "ground_cover": "#6a8a5a", "climber": "#8a6a4a",
                           "root_crop": "#a09070"}.get(c["guild_function"], "#808080"),
                "highlight": False,
            })

        # Planting calendar (next 14 days)
        calendar = []
        for plant_info in [anchor] + companions:
            timing = plant_info.get("plant_timing", {})
            if isinstance(plant_info, dict) and "name" in plant_info:
                name = plant_info["name"]
            else:
                name = anchor_plant
            calendar.append({
                "plant": name,
                "best_window": f"{timing.get('best_nakshatra', '')} nakshatra, {timing.get('best_phase', '')} moon",
                "vara": timing.get("best_vara", ""),
                "phase": timing.get("best_phase", "waxing"),
            })

        plan = {
            "anchor": anchor,
            "companions": companions,
            "conflict": conflict,
            "guild_profile": profile,
            "hex_layout": {
                "grid_size": grid_size,
                "cells": cells,
                "scale_m_per_hex": scale,
            },
            "planting_calendar": calendar,
            "attestation": "SYNTHESIS",
            "pfaf_credit": "Plants for a Future database (pfaf.org)",
        }

        log.info("guild: anchor=%s companions=%d", anchor_plant, len(companions))
        return _validate(plan)

    except Exception as e:
        log.warning("plan_guild failed: %s", e)
        return _validate({"attestation": "SYNTHESIS"})
