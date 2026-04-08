"""
orientation_engine.py — Sura/asura orientation from field + natal.

Reads datasets/game/sura_asura_map.csv.
Pattern follows ui_vastu_engine.py.
"""

import csv
import io
import os
from typing import Dict

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_MAP_CSV = os.path.join(_ROOT, "datasets", "game", "sura_asura_map.csv")

_cache = None


def _load():
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(_MAP_CSV, encoding="utf-8") as f:
            _cache = {r["entity_id"]: r for r in csv.DictReader(io.StringIO(f.read().lstrip()))}
    except Exception:
        _cache = {}
    return _cache


def derive_sura_asura(field_state: dict, natal: dict = None) -> dict:
    """Today's sura/asura orientation + accessible districts. Never raises."""
    try:
        sa_map = _load()
        p5 = field_state.get("panchanga", {})
        hora_lord = field_state.get("hora", {}).get("hora_lord", "Sun").lower()

        # Map hora lord to entity_id
        _GRAHA_KEY = {"sun": "surya", "moon": "chandra", "mars": "mangala",
                      "mercury": "budha", "jupiter": "guru", "venus": "shukra",
                      "saturn": "shani"}
        hora_entity = _GRAHA_KEY.get(hora_lord, hora_lord)
        hora_data = sa_map.get(hora_entity, {})

        orientation = hora_data.get("orientation", "neutral")
        quality = hora_data.get("quality", "")

        # Count sura vs asura strength from natal planets visible today
        sura_strength = 0
        asura_strength = 0
        for eid, data in sa_map.items():
            o = data.get("orientation", "")
            if o == "sura":
                sura_strength += 1
            elif o == "asura":
                asura_strength += 1

        # Field element tips balance
        element = p5.get("element", "ether").lower()
        if element in ("fire", "air"):
            sura_strength += 1
        elif element in ("water", "earth"):
            asura_strength += 1

        # Districts more accessible
        sura_districts = [d.get("direction", "") for d in sa_map.values() if d.get("orientation") == "sura"]
        asura_districts = [d.get("direction", "") for d in sa_map.values() if d.get("orientation") == "asura"]

        return {
            "orientation": orientation,
            "hora_graha": hora_entity,
            "quality": quality,
            "sura_strength": sura_strength,
            "asura_strength": asura_strength,
            "balance": "sura" if sura_strength > asura_strength else "asura" if asura_strength > sura_strength else "balanced",
            "sura_districts": sura_districts,
            "asura_districts": asura_districts,
        }
    except Exception:
        return {"orientation": "neutral", "balance": "balanced",
                "sura_districts": [], "asura_districts": []}
