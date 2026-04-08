"""
lineage_engine.py — Calculate accessible lineages from natal chart.

Reads datasets/game/lineages.csv.
Scores each lineage against natal placements.
Pattern follows ui_vastu_engine.py.
"""

import csv
import io
import os
from typing import Dict, List

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_LINEAGES_CSV = os.path.join(_ROOT, "datasets", "game", "lineages.csv")

_cache = None


def _load():
    global _cache
    if _cache is not None:
        return _cache
    try:
        with open(_LINEAGES_CSV, encoding="utf-8") as f:
            _cache = list(csv.DictReader(io.StringIO(f.read().lstrip())))
    except Exception:
        _cache = []
    return _cache


def _natal_elements(natal):
    """Count elements across all placements."""
    counts = {"fire": 0, "water": 0, "earth": 0, "air": 0, "ether": 0}
    planets = natal.get("planets", {})
    for p, data in planets.items():
        if isinstance(data, dict):
            # Map nakshatra to element via the natal data
            elem = ""
            # Use sign-based element mapping
            sign = data.get("sign", "").lower()
            _SIGN_ELEM = {"aries": "fire", "taurus": "earth", "gemini": "air",
                          "cancer": "water", "leo": "fire", "virgo": "earth",
                          "libra": "air", "scorpio": "water", "sagittarius": "fire",
                          "capricorn": "earth", "aquarius": "air", "pisces": "water"}
            elem = _SIGN_ELEM.get(sign, "")
            if elem:
                counts[elem] = counts.get(elem, 0) + 1
    return counts


def _graha_strong(natal, graha_name):
    """Check if a graha is strong in natal chart."""
    planets = natal.get("planets", {})
    g = graha_name.lower()
    _GRAHA_MAP = {"surya": "sun", "chandra": "moon", "mangala": "mars",
                  "budha": "mercury", "guru": "jupiter", "shukra": "venus",
                  "shani": "saturn", "rahu": "rahu", "ketu": "ketu"}
    key = _GRAHA_MAP.get(g, g)
    data = planets.get(key, {})
    if not data:
        return False
    # Strong = exalted, or in own sign, or lagna lord
    if data.get("exalted"):
        return True
    lagna = natal.get("lagna", {})
    if lagna.get("lord", "").lower() == key:
        return True
    return True  # present = somewhat strong for scoring


def _nak_match(natal, nak_triggers):
    """Check if any natal placement is in trigger nakshatras."""
    triggers = [n.strip().lower().replace(" ", "_") for n in nak_triggers.split(";")]
    planets = natal.get("planets", {})
    for p, data in planets.items():
        if isinstance(data, dict):
            pnak = data.get("nakshatra", "").lower().replace(" ", "_")
            for t in triggers:
                if t and (t in pnak or pnak in t):
                    return True
    # Check lagna
    lagna_nak = natal.get("lagna", {}).get("nakshatra", "").lower().replace(" ", "_")
    for t in triggers:
        if t and (t in lagna_nak or lagna_nak in t):
            return True
    return False


def calculate_accessible_lineages(natal: dict) -> list:
    """Score all lineages against natal chart. Returns ranked list."""
    try:
        lineages = _load()
        if not lineages:
            return []

        elements = _natal_elements(natal)
        results = []

        for lin in lineages:
            score = 0.0
            reasons = []

            # Graha primary strength
            graha = lin.get("graha_primary", "")
            if graha and _graha_strong(natal, graha):
                score += 0.3
                reasons.append(f"{graha} strong")

            # Nakshatra trigger match
            nak_trigger = lin.get("nakshatra_trigger", "")
            if nak_trigger and _nak_match(natal, nak_trigger):
                score += 0.35
                reasons.append("nakshatra match")

            # Element dominance
            elem = lin.get("element_dominant", "").lower()
            if elem and elements.get(elem, 0) >= 2:
                score += 0.2
                reasons.append(f"{elem} dominant")
            elif elem and elements.get(elem, 0) >= 1:
                score += 0.1

            # Special conditions from natal_requirements
            reqs = lin.get("natal_requirements", "")
            if "saturn_exalted" in reqs and natal.get("special", {}).get("saturn_exalted"):
                score += 0.15
                reasons.append("Saturn exalted")
            if "ketu_mula" in reqs:
                planets = natal.get("planets", {})
                ketu = planets.get("ketu", {})
                if "mula" in ketu.get("nakshatra", "").lower():
                    score += 0.15
                    reasons.append("Ketu in Mula")
            if "moon_punarvasu" in reqs:
                planets = natal.get("planets", {})
                moon = planets.get("moon", {})
                if "punarvasu" in moon.get("nakshatra", "").lower():
                    score += 0.2
                    reasons.append("Moon in Punarvasu")

            # Baseline for all lineages
            score += 0.1

            results.append({
                "lineage_id": lin.get("lineage_id", ""),
                "name": lin.get("name_iast", ""),
                "name_english": lin.get("name_english", ""),
                "type": lin.get("lineage_type", ""),
                "score": round(min(1.0, score), 3),
                "reasons": reasons,
                "quality": lin.get("quality", ""),
                "district": lin.get("district_affinity", ""),
                "attestation": lin.get("attestation", "SYNTHESIS"),
            })

        results.sort(key=lambda x: -x["score"])
        return results

    except Exception:
        return []
